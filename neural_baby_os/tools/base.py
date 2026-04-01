from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional


@dataclass
class ToolExecutionResult:
    ok: bool
    stdout: str
    stderr: str
    duration_s: float
    meta: Dict[str, Any]


ToolFunc = Callable[[Dict[str, Any]], ToolExecutionResult]


@dataclass
class Tool:
    name: str
    description: str
    schema: Dict[str, Any]
    run: ToolFunc

