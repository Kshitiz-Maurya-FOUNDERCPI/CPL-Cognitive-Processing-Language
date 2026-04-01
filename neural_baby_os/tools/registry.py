from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ToolPolicy:
    auto_execute: bool = True
    ask_each_time: bool = False


@dataclass
class ToolMeta:
    enabled: bool = True
    cooldown_until_step: int = 0
    success_count: int = 0
    failure_count: int = 0
    policy: ToolPolicy = field(default_factory=ToolPolicy)


class ToolRegistry:
    """
    Persistent registry for tools and their policies.
    Stored as JSON under data/tool_registry.json.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = self.data_dir / "tool_registry.json"
        self.tools: Dict[str, ToolMeta] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.tools = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self.tools = {}
            return
        out: Dict[str, ToolMeta] = {}
        for name, meta in raw.get("tools", {}).items():
            policy_raw = meta.get("policy", {})
            policy = ToolPolicy(
                auto_execute=bool(policy_raw.get("auto_execute", True)),
                ask_each_time=bool(policy_raw.get("ask_each_time", False)),
            )
            out[name] = ToolMeta(
                enabled=bool(meta.get("enabled", True)),
                cooldown_until_step=int(meta.get("cooldown_until_step", 0)),
                success_count=int(meta.get("success_count", 0)),
                failure_count=int(meta.get("failure_count", 0)),
                policy=policy,
            )
        self.tools = out

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "tools": {
                name: {
                    "enabled": meta.enabled,
                    "cooldown_until_step": meta.cooldown_until_step,
                    "success_count": meta.success_count,
                    "failure_count": meta.failure_count,
                    "policy": asdict(meta.policy),
                }
                for name, meta in self.tools.items()
            }
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def ensure_tool(self, name: str) -> ToolMeta:
        if name not in self.tools:
            self.tools[name] = ToolMeta()
        return self.tools[name]

    def record_success(self, name: str) -> None:
        meta = self.ensure_tool(name)
        meta.success_count += 1

    def record_failure(self, name: str, current_step: int, cooldown_steps: int = 10) -> None:
        meta = self.ensure_tool(name)
        meta.failure_count += 1
        meta.cooldown_until_step = max(meta.cooldown_until_step, current_step + cooldown_steps)

