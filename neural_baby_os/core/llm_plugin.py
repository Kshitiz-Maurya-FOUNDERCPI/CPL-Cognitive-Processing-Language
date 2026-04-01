from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMRequest:
    kind: str
    payload: Dict[str, Any]


@dataclass
class LLMResponse:
    text: str
    meta: Dict[str, Any]


class LLMPlugin:
    """
    Optional LLM plugin interface.

    This is an abstraction only; wiring to a concrete model or API is left
    to the user so the core remains math-first and local by default.
    """

    def explain_state(self, snapshot: Dict[str, Any]) -> Optional[LLMResponse]:
        """
        Given a compact snapshot of internal state, return a human-readable explanation.
        Default implementation is a stub.
        """
        return None

    def suggest_self_repair(self, error_log: str) -> Optional[LLMResponse]:
        """
        Given a text description of an error or crash, return suggested fixes.
        Default implementation is a stub.
        """
        return None

