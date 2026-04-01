import numpy as np


class PlasticNeuralNetwork:
    """
    Hebbian plastic neural layer from the notebook.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        learning_rate: float = 0.01,
        weight_limit: float = 2.0,
    ):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.lr = learning_rate
        self.weight_limit = weight_limit
        self.weights = np.random.randn(output_dim, input_dim) * 0.1
        self.last_input = np.zeros(input_dim, dtype=float)
        self.last_output = np.zeros(output_dim, dtype=float)

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.last_input = np.asarray(x, dtype=float)
        self.last_output = np.tanh(self.weights @ self.last_input)
        return self.last_output

    def hebbian_update(self) -> None:
        delta_w = self.lr * np.outer(self.last_output, self.last_input)
        self.weights += delta_w
        self.normalize_weights()

    def normalize_weights(self) -> None:
        self.weights = np.clip(self.weights, -self.weight_limit, self.weight_limit)

    def get_synaptic_weights(self) -> np.ndarray:
        return np.copy(self.weights)


class CuriosityModule:
    """
    Intrinsic motivation via novelty, ported from the notebook CuriosityModule.
    """

    def __init__(self, memory_size: int = 50, reward_scale: float = 0.5) -> None:
        self.memory_size = memory_size
        self.reward_scale = reward_scale
        self.sensory_history: list[np.ndarray] = []

    def calculate_novelty(self, current_input: np.ndarray) -> float:
        x = np.asarray(current_input, dtype=float)
        if not self.sensory_history:
            self.sensory_history.append(x)
            return 1.0

        distances = [float(np.linalg.norm(x - h)) for h in self.sensory_history]
        min_distance = min(distances) if distances else 0.0

        self.sensory_history.append(x)
        if len(self.sensory_history) > self.memory_size:
            self.sensory_history.pop(0)

        return min_distance

    def generate_intrinsic_reward(self, current_input: np.ndarray) -> float:
        novelty_score = self.calculate_novelty(current_input)
        intrinsic_reward = novelty_score * self.reward_scale
        return float(min(intrinsic_reward, 1.0))


def prediction_based_curiosity(
    error: float, info_gain: float, alpha: float = 1.0, beta: float = 0.5
) -> float:
    """
    Simple intrinsic reward from world-model prediction error and information gain.
    Reward = alpha * error + beta * info_gain, clipped to [0, 1].
    """
    reward = alpha * float(error) + beta * float(info_gain)
    return float(max(0.0, min(1.0, reward)))


