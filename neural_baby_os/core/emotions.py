class EmotionalStateSystem:
    """
    Manages internal valence (comfort/discomfort) on [-1.0, 1.0].
    Ported from the notebook EmotionalStateSystem.
    """

    def __init__(self, decay_rate: float = 0.05, baseline: float = 0.0) -> None:
        self.valence = baseline
        self.decay_rate = decay_rate
        self.baseline = baseline

    def update_valence(self, stimulus_value: float) -> float:
        self.valence += float(stimulus_value)
        self.valence = max(-1.0, min(1.0, self.valence))
        return self.valence

    def apply_decay(self) -> float:
        if self.valence > self.baseline:
            self.valence = max(self.baseline, self.valence - self.decay_rate)
        elif self.valence < self.baseline:
            self.valence = min(self.baseline, self.valence + self.decay_rate)
        return self.valence

    def get_current_state(self) -> dict:
        label = "Neutral"
        if self.valence > 0.2:
            label = "Comfortable"
        elif self.valence < -0.2:
            label = "Uncomfortable"
        return {"valence": round(self.valence, 3), "label": label}

