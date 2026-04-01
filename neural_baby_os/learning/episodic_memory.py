from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Episode:
    sensory: np.ndarray
    valence: float
    action: Optional[Dict[str, Any]] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EpisodeSummary:
    sensory_centroid: np.ndarray
    avg_valence: float
    count: int


class HierarchicalEpisodicMemory:
    """
    Two-level episodic memory:
    - raw episodes (recent, fine-grained)
    - summaries (compressed clusters)
    """

    def __init__(self, max_episodes: int = 256, max_summaries: int = 32) -> None:
        self.max_episodes = max_episodes
        self.max_summaries = max_summaries
        self.episodes: List[Episode] = []
        self.summaries: List[EpisodeSummary] = []

    def write(self, episode: Episode) -> None:
        self.episodes.append(episode)
        if len(self.episodes) > self.max_episodes:
            self._compress_once()

    def _compress_once(self) -> None:
        """
        Merge a small batch of lowest-salience episodes into a summary.
        For now, we just take the oldest few.
        """
        if not self.episodes:
            return
        batch_size = min(8, len(self.episodes))
        batch = self.episodes[:batch_size]
        self.episodes = self.episodes[batch_size:]

        data = np.stack([e.sensory for e in batch], axis=0)
        vals = np.array([e.valence for e in batch], dtype=float)

        centroid = data.mean(axis=0)
        avg_valence = float(vals.mean())
        summary = EpisodeSummary(
            sensory_centroid=centroid, avg_valence=avg_valence, count=batch_size
        )
        self.summaries.append(summary)
        if len(self.summaries) > self.max_summaries:
            self.summaries.pop(0)

    def read_closest(self, query_vec: np.ndarray) -> Optional[Tuple[float, EpisodeSummary]]:
        """
        Retrieve the summary closest to the query sensory vector.
        Returns (distance, summary) or None.
        """
        if not self.summaries:
            return None
        q = np.asarray(query_vec, dtype=float)
        best: Optional[EpisodeSummary] = None
        best_dist = float("inf")
        for s in self.summaries:
            d = float(np.linalg.norm(q - s.sensory_centroid))
            if d < best_dist:
                best_dist = d
                best = s
        if best is None:
            return None
        return best_dist, best

