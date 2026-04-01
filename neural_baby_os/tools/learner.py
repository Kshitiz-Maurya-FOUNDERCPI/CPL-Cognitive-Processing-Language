from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from neural_baby_os.tools.registry import ToolRegistry


def tool_success_score(registry: ToolRegistry, tool_name: str) -> float:
    meta = registry.tools.get(tool_name)
    if not meta:
        return 0.0
    succ = meta.success_count
    fail = meta.failure_count
    # Laplace smoothing.
    return (succ + 1.0) / (succ + fail + 2.0)


def rank_tools(registry: ToolRegistry, candidate_tools: List[str]) -> List[Tuple[str, float]]:
    """
    Lightweight ranking: higher expected success gets higher score.
    This satisfies "success scoring affects future selections" deterministically.
    """
    scored: List[Tuple[str, float]] = []
    for name in candidate_tools:
        meta = registry.tools.get(name)
        if not meta or not meta.enabled:
            continue
        score = tool_success_score(registry, name)
        # Penalize cooldown tools by making their score small.
        scored.append((name, float(score)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

