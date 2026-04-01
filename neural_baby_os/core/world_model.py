from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class WorldModelState:
    """
    Lightweight latent state for the world model.
    For now this is just a vector the same size as the sensory input.
    """

    latent: np.ndarray


class SimpleWorldModel:
    """
    Very small predictive model:
    - maintains an exponential moving average of sensory inputs as a latent
    - predicts next sensory vector as that latent
    - exposes surprise = prediction error (L2) and a simple information gain proxy
    This is intentionally cheap so it can run on many devices.
    """

    def __init__(self, dim: int, ema_decay: float = 0.9) -> None:
        self.dim = dim
        self.ema_decay = ema_decay
        self.state: Optional[WorldModelState] = None

    def init_state(self, first_obs: np.ndarray) -> None:
        x = np.asarray(first_obs, dtype=float)
        self.state = WorldModelState(latent=x.copy())

    def predict(self) -> np.ndarray:
        if self.state is None:
            return np.zeros(self.dim, dtype=float)
        return self.state.latent

    def update(self, obs: np.ndarray) -> dict:
        """
        Update latent given new observation and return prediction / surprise stats.
        """
        x = np.asarray(obs, dtype=float)
        if self.state is None:
            self.init_state(x)
            pred = self.state.latent
        else:
            pred = self.predict()

        error_vec = x - pred
        error = float(np.linalg.norm(error_vec))

        # Information value proxy: how much the latent actually moved.
        if self.state is None:
            info_gain = 0.0
        else:
            old_latent = self.state.latent
            new_latent = self.ema_decay * old_latent + (1.0 - self.ema_decay) * x
            info_gain = float(np.linalg.norm(new_latent - old_latent))
            self.state.latent = new_latent

        return {
            "prediction": pred,
            "error": error,
            "info_gain": info_gain,
        }

