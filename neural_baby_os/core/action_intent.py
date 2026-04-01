from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ActionIntent:
    """
    Optional external action requested by the user/UI.

    - kind='tool': run a single tool with args
    - kind='skill': run a named skill
    """

    kind: str  # 'tool' or 'skill'
    name: str
    args: Dict[str, Any] = field(default_factory=dict)
    created_from: str = "ui"
    # If true, the runner should allow running without repeated confirmation.
    bypass_confirm: bool = False
    # Optional human message for logging.
    user_note: Optional[str] = None

