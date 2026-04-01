"""
CPL: API Key Management System
"""

import os
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    import requests
except:
    import subprocess
    subprocess.run(['pip', 'install', 'requests'], check=True)
    import requests


class KeySource(Enum):
    ENVIRONMENT = "environment"
    FILE = "file"
    MANUAL = "manual"


@dataclass
class APIKey:
    key: str
    source: str
    provider: str
    created_at: float = field(default_factory=time.time)
    last_used: float = 0.0
    use_count: int = 0
    rate_limit: int = 100
    is_valid: bool = True
    error_count: int = 0

    def mark_used(self):
        self.last_used = time.time()
        self.use_count += 1

    def mark_error(self, error: str):
        self.error_count += 1
        if self.error_count > 10:
            self.is_valid = False

    def reset_errors(self):
        self.error_count = 0


class KeyManager:
    def __init__(self):
        self.providers: Dict[str, List[APIKey]] = {}
        self.stats = {"keys_loaded": 0, "keys_valid": 0}

    def get_key(self, provider: str) -> Optional[APIKey]:
        keys = self.providers.get(provider, [])
        valid = [k for k in keys if k.is_valid and k.error_count < 5]
        if not valid:
            return None
        valid.sort(key=lambda k: k.last_used)
        return valid[0]

    def mark_key_error(self, provider: str, error: str):
        keys = self.providers.get(provider, [])
        if keys:
            keys[0].mark_error(error)

    def mark_key_success(self, provider: str):
        keys = self.providers.get(provider, [])
        if keys:
            keys[0].mark_used()
            keys[0].reset_errors()

    def get_all_providers(self) -> List[str]:
        return list(self.providers.keys())

    def add_key(self, provider: str, key: str, source: str = "manual"):
        api_key = APIKey(key=key, source=source, provider=provider)
        if provider not in self.providers:
            self.providers[provider] = []
        self.providers[provider].append(api_key)
        self.stats["keys_loaded"] += 1
        self.stats["keys_valid"] += 1
        return True


class MultiSourceLLMClient:
    ENDPOINTS = {
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
            "supports_system": True
        },
        "cerebras": {
            "url": "https://api.cerebras.ai/v1/chat/completions",
            "models": ["llama3.1-8b", "qwen-3-235b-a22b-instruct-2507"],
            "supports_system": True
        },
        "mistral": {
            "url": "https://api.mistral.ai/v1/chat/completions",
            "models": ["mistral-large-latest", "mistral-small-latest"],
            "supports_system": True
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "models": ["gemini-2.0-flash", "gemini-2.0-flash-lite"],
            "supports_system": True
        },
    }

    def __init__(self, key_manager: Optional[KeyManager] = None,
                 preferred_providers: Optional[List[str]] = None, timeout: int = 30):
        self.key_manager = key_manager or KeyManager()
        self.preferred_providers = preferred_providers or ["cerebras", "groq", "mistral", "gemini"]
        self.timeout = timeout
        self.rate_limit_cooldown = {}
        self.provider_chain = self._build_provider_chain()
        self.stats = {"total_requests": 0, "successful": 0, "failed": 0}

    def _build_provider_chain(self) -> List[str]:
        chain = []
        for provider in self.preferred_providers:
            if provider in self.key_manager.providers:
                chain.append(provider)
        return chain

    def query(self, prompt: str, system_prompt: Optional[str] = None,
              max_tokens: int = 200, temperature: float = 0.7, model: Optional[str] = None) -> Dict:
        self.stats["total_requests"] += 1

        for provider in self.provider_chain:
            if provider in self.rate_limit_cooldown:
                if time.time() < self.rate_limit_cooldown[provider]:
                    continue

            key = self.key_manager.get_key(provider)
            if not key:
                continue

            endpoint = self.ENDPOINTS.get(provider)
            if not endpoint:
                continue

            try:
                headers = {"Authorization": f"Bearer {key.key}"}
                messages = []
                if system_prompt and endpoint["supports_system"]:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                model_name = model or endpoint["models"][0]

                response = requests.post(
                    endpoint["url"],
                    headers=headers,
                    json={"model": model_name, "messages": messages,
                         "max_tokens": max_tokens, "temperature": temperature},
                    timeout=self.timeout
                )

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 30))
                    self.rate_limit_cooldown[provider] = time.time() + retry_after
                    print(f"[RATE LIMIT] {provider} rate limited")
                    continue

                if response.status_code != 200:
                    self.key_manager.mark_key_error(provider, f"HTTP {response.status_code}")
                    continue

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                self.key_manager.mark_key_success(provider)
                self.stats["successful"] += 1

                return {"success": True, "content": content, "provider": provider,
                       "model": model_name, "tokens": len(content.split())}

            except Exception as e:
                self.stats["failed"] += 1
                continue

        return {"success": False, "content": "", "provider": None, "error": "All providers failed"}
