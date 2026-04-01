from collections import deque
from typing import Any, Dict, List

import numpy as np


class MemoryFramework:
    """
    Dual-buffer memory system (STM + LTM) from the notebook.
    """

    def __init__(self, stm_capacity: int = 10, ltm_capacity: int = 100) -> None:
        self.stm: deque[Dict[str, Any]] = deque(maxlen=stm_capacity)
        self.ltm: List[Dict[str, Any]] = []
        self.ltm_capacity = ltm_capacity

    def store_stm(self, sensory_data, valence: float) -> None:
        snapshot = {"data": np.asarray(sensory_data), "valence": float(valence)}
        self.stm.append(snapshot)

    def consolidate_to_ltm(self, significance_threshold: float = 0.7) -> None:
        for memory in list(self.stm):
            if abs(memory["valence"]) >= significance_threshold:
                if memory not in self.ltm:
                    if len(self.ltm) >= self.ltm_capacity:
                        self.ltm.pop(0)
                    self.ltm.append(memory)

    def retrieve_relevant_memory(self, current_input, similarity_threshold: float = 0.1):
        x = np.asarray(current_input)
        best_match = None
        min_dist = float("inf")

        for memory in self.ltm:
            dist = float(np.linalg.norm(x - memory["data"]))
            if dist < min_dist:
                min_dist = dist
                best_match = memory

        if best_match is not None and min_dist < similarity_threshold:
            return best_match
        return None

