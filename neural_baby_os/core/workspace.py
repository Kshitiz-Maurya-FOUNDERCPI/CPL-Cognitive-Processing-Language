from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkspaceItem:
    kind: str
    data: Dict[str, Any]
    salience: float


@dataclass
class Workspace:
    """
    Small global workspace / focus pool.
    """

    max_items: int = 5
    items: List[WorkspaceItem] = field(default_factory=list)
    focus: Optional[WorkspaceItem] = None

    def update(self, candidates: List[WorkspaceItem]) -> None:
        """
        Merge new candidates, keep top-k by salience, and set focus.
        """
        self.items.extend(candidates)
        self.items.sort(key=lambda it: it.salience, reverse=True)
        self.items = self.items[: self.max_items]
        self.focus = self.items[0] if self.items else None


def compute_salience(
    prediction_error: float,
    info_gain: float,
    valence_abs: float,
    resource_pressure: float,
) -> float:
    """
    Simple salience function combining:
    - surprise (prediction_error)
    - learning opportunity (info_gain)
    - emotional intensity (|valence|)
    - resource pressure (e.g., high CPU/battery stress)
    """
    s = (
        1.0 * float(prediction_error)
        + 0.5 * float(info_gain)
        + 0.7 * float(valence_abs)
        + 0.3 * float(resource_pressure)
    )
    return max(0.0, min(5.0, s))

