import numpy as np


class SensoryInterface:
    """
    Minimal port of the notebook SensoryInterface.
    Handles raw numeric input and normalization.
    """

    def __init__(self, input_dim: int, normalization_range=(0.0, 1.0)) -> None:
        self.input_dim = input_dim
        self.min_val, self.max_val = normalization_range

    def normalize(self, raw_data: np.ndarray) -> np.ndarray:
        data_min = float(np.min(raw_data))
        data_max = float(np.max(raw_data))
        if data_max == data_min:
            return np.zeros_like(raw_data)
        return (raw_data - data_min) / (data_max - data_min) * (
            self.max_val - self.min_val
        ) + self.min_val

    def process_stimuli(self, raw_input) -> np.ndarray:
        raw_array = np.array(raw_input, dtype=float)
        if raw_array.size != self.input_dim:
            raise ValueError(
                f"Input size {raw_array.size} does not match expected dimension {self.input_dim}"
            )
        return self.normalize(raw_array)

