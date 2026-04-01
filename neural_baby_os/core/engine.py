import numpy as np

from neural_baby_os.core.emotions import EmotionalStateSystem
from neural_baby_os.core.llm_plugin import LLMPlugin
from neural_baby_os.core.sensory import SensoryInterface
from neural_baby_os.core.world_model import SimpleWorldModel
from neural_baby_os.core.workspace import Workspace, WorkspaceItem, compute_salience
from neural_baby_os.learning.hebbian import (
    PlasticNeuralNetwork,
    prediction_based_curiosity,
)
from neural_baby_os.learning.memory import MemoryFramework
from neural_baby_os.learning.episodic_memory import Episode, HierarchicalEpisodicMemory


class NeuralBabyAgent:
    """
    Thin façade over the core 'neural baby' components.

    The agent exposes a simple step() API that:
    - accepts a numeric sensory vector
    - updates internal neural/emotional/memory state
    - returns a compact action/status dict suitable for a terminal UI
    """

    def __init__(
        self,
        input_dim: int = 4,
        output_dim: int = 2,
        llm_plugin: LLMPlugin | None = None,
    ) -> None:
        self.input_dim = input_dim
        self.sensory = SensoryInterface(input_dim=input_dim)
        self.emotional = EmotionalStateSystem(decay_rate=0.03)
        self.brain = PlasticNeuralNetwork(input_dim=input_dim, output_dim=output_dim)
        self.memory = MemoryFramework(stm_capacity=20, ltm_capacity=200)
        self.world_model = SimpleWorldModel(dim=input_dim)
        self.workspace = Workspace(max_items=5)
        self.episodic = HierarchicalEpisodicMemory(max_episodes=256, max_summaries=32)
        self.llm_plugin = llm_plugin

        self.step_count = 0

    def step(self, raw_input, resource_pressure: float = 0.0) -> dict:
        """
        One life-tick of the agent.

        raw_input: array-like numeric sensory vector of length input_dim.
        """
        self.step_count += 1

        x = self.sensory.process_stimuli(raw_input)

        # Predictive world model update
        wm_stats = self.world_model.update(x)
        intrinsic_reward = prediction_based_curiosity(
            error=wm_stats["error"], info_gain=wm_stats["info_gain"]
        )
        valence = self.emotional.update_valence(intrinsic_reward)
        val_abs = abs(valence)

        # Salience and workspace update
        sal = compute_salience(
            prediction_error=wm_stats["error"],
            info_gain=wm_stats["info_gain"],
            valence_abs=val_abs,
            resource_pressure=resource_pressure,
        )
        ws_item = WorkspaceItem(
            kind="sensory_tick",
            data={
                "sensory": x,
                "wm_error": wm_stats["error"],
                "wm_info": wm_stats["info_gain"],
            },
            salience=sal,
        )
        self.workspace.update([ws_item])

        y = self.brain.forward(x)
        # Simple selective plasticity: only update strongly when salience is high.
        if sal > 0.5:
            self.brain.hebbian_update()

        self.memory.store_stm(x, valence)
        if self.step_count % 10 == 0:
            self.memory.consolidate_to_ltm(significance_threshold=0.5)

        # Episodic write (compressed later)
        episode = Episode(sensory=x, valence=valence, action=None, meta={})
        self.episodic.write(episode)

        status = self.get_status()
        status["last_output"] = y.tolist()
        status["prediction_error"] = wm_stats["error"]
        status["info_gain"] = wm_stats["info_gain"]
        status["intrinsic_reward"] = intrinsic_reward
        status["salience"] = sal
        status["workspace_has_focus"] = self.workspace.focus is not None
        # If an LLM plugin is present, we could attach a brief explanation lazily.
        if self.llm_plugin is not None:
            # Keep this cheap: caller can decide when to actually call the LLM.
            status["llm_available"] = True
        return status

    def record_action_episode(
        self,
        sensory_context,
        action: dict,
        valence_delta: float,
    ) -> None:
        """
        Apply an external action outcome into the agent's internal state.

        This is the hook used by the Skill/Tools layer so tool execution
        can influence emotion and episodic memory.
        """
        self.emotional.update_valence(valence_delta)
        current_valence = float(self.emotional.valence)
        x = np.asarray(sensory_context, dtype=float)
        self.episodic.write(Episode(sensory=x, valence=current_valence, action=action, meta={}))

    def get_status(self) -> dict:
        emo = self.emotional.get_current_state()
        weights = self.brain.get_synaptic_weights()
        weights_sample = weights[0][: min(3, weights.shape[1])]

        return {
            "step": self.step_count,
            "valence": emo["valence"],
            "mood": emo["label"],
            "stm_size": len(self.memory.stm),
            "ltm_size": len(self.memory.ltm),
             "episodes": len(self.episodic.episodes),
             "episode_summaries": len(self.episodic.summaries),
            "weights_sample": weights_sample.tolist(),
        }

