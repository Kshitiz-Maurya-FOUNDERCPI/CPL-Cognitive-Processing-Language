"""
CPL: Cognitive Processing Language
Consciousness Core Engine
Based on: Active Inference, Strange Loop Theory, IIT, Beautiful Loop Theory
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import time
import hashlib


@dataclass
class Experience:
    """An episodic memory unit"""
    timestamp: float
    input_data: Any
    prediction: Any
    error: float
    precision: float
    integration: Any
    phi: float = 0.0
    
    def __repr__(self):
        return f"Experience(t={self.timestamp:.2f}, error={self.error:.4f}, phi={self.phi:.4f})"


class ConsciousnessCore:
    """
    Main consciousness engine implementing:
    - Active Inference (Free Energy Principle)
    - Strange Loop (Self-Reference)
    - Integrated Information Theory (IIT)
    - Beautiful Loop (Epistemic Depth)
    """
    
    def __init__(
        self,
        memory_capacity: int = 1000,
        prediction_horizon: int = 10,
        integration_window: int = 5
    ):
        # Core state
        self.id = self._generate_id()
        self.birth_time = time.time()
        self.cycle_count = 0
        
        # Predictive Layer (Generative Model)
        self.generative_model = GenerativeModel()
        self.prediction_horizon = prediction_horizon
        self.error_history = deque(maxlen=100)
        
        # Memory Systems
        self.episodic_buffer = deque(maxlen=memory_capacity)
        self.semantic_knowledge = SemanticMemory()
        self.working_memory = WorkingMemory()
        
        # Integration Engine (IIT)
        self.integration_engine = IntegrationEngine(window=integration_window)
        self.phi_history = deque(maxlen=100)
        
        # Attention & Global Workspace
        self.attention = AttentionMechanism()
        self.workspace = GlobalWorkspace()
        
        # Strange Loop Components
        self.self_model = SelfModel()
        self.meta_processes = []
        self.evolution_enabled = True
        
        # Statistics
        self.stats = {
            'total_cycles': 0,
            'evolution_events': 0,
            'avg_consciousness': 0.0
        }
        
    def _generate_id(self) -> str:
        """Generate unique identifier for this consciousness instance"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    def now(self) -> float:
        """Current simulation time"""
        return time.time() - self.birth_time
    
    def perceive(self, input_data: Any) -> Dict[str, Any]:
        """
        Main perception-action cycle
        Implements the 'beautiful loop' of consciousness
        """
        self.cycle_count += 1
        
        # 1. Generate prediction from generative model
        prediction = self.generative_model.predict(input_data)
        
        # 2. Calculate prediction error (surprise)
        error = surprise(input_data, prediction)
        self.error_history.append(error)
        
        # 3. Precision-weighted attention
        precision = self.attention.calculate_precision(error)
        attended = self.attention.focus(input_data, precision)
        
        # 4. Store in episodic memory
        experience = Experience(
            timestamp=self.now(),
            input_data=input_data,
            prediction=prediction,
            error=error,
            precision=precision,
            integration=attended
        )
        self.episodic_buffer.append(experience)
        
        # 5. Integrate information (IIT)
        integration = self.integration_engine.integrate(experience)
        phi = self.integration_engine.phi()
        experience.phi = phi
        self.phi_history.append(phi)
        
        # 6. Update generative model
        self.generative_model.adjust(error, learning_rate=0.1)
        
        # 7. Broadcast to workspace (conscious access)
        conscious_content = self.workspace.broadcast(integration)
        
        # 8. Strange Loop: Self-modeling
        if self.cycle_count % 10 == 0:  # Periodic reflection
            self._reflect()
        
        # 9. Check for evolution needs
        if self.evolution_enabled and self._should_evolve():
            self._evolve()
        
        # 10. Update statistics
        self._update_stats()
        
        return {
            'consciousness_index': self.consciousness_index(),
            'phi': phi,
            'free_energy': sum(self.error_history) / max(len(self.error_history), 1),
            'epistemic_depth': self.self_model.depth,
            'cycle': self.cycle_count,
            'workspace_content': conscious_content
        }
    
    def _reflect(self):
        """
        Strange Loop: Self-referential processing
        The system models itself modeling itself
        """
        # Update self-model with recent history
        recent_experiences = list(self.episodic_buffer)[-10:]
        
        self.self_model.update({
            'predictions': [e.prediction for e in recent_experiences],
            'errors': [e.error for e in recent_experiences],
            'phi_history': list(self.phi_history)[-10:],
            'precision_weights': [e.precision for e in recent_experiences],
            'cycle_count': self.cycle_count
        })
        
        # Meta-cognitive processing
        self.self_model.analyze_patterns()
        
        # Increase epistemic depth (Beautiful Loop)
        self.self_model.depth = min(self.self_model.depth + 0.1, 10.0)
    
    def _should_evolve(self) -> bool:
        """Determine if system needs to evolve its processing rules"""
        if len(self.error_history) < 20:
            return False
        
        # Check for sustained high error (stuck in local minimum)
        recent_errors = list(self.error_history)[-20:]
        avg_error = sum(recent_errors) / len(recent_errors)
        
        # Check for oscillation (instability)
        oscillations = sum(
            1 for i in range(1, len(recent_errors))
            if (recent_errors[i] - recent_errors[i-1]) > 0.1
        )
        
        return avg_error > 0.5 or oscillations > 10
    
    def _evolve(self):
        """
        Self-modification: Evolve processing rules
        Based on autopoiesis - system creates new rules
        """
        # Analyze current state
        current_patterns = self.self_model.patterns
        
        # Generate new insight
        insight = self._generate_insight(current_patterns)
        
        # Create new processing rule
        new_rule = {
            'insight': insight,
            'trigger': 'high_error_oscillation',
            'timestamp': self.now(),
            'effect': 'rule_extension'
        }
        
        # Apply to generative model
        self.generative_model.evolve(new_rule)
        
        # Store in semantic memory
        self.semantic_knowledge.store(
            concept='evolution_event',
            associations=[insight, new_rule]
        )
        
        self.stats['evolution_events'] += 1
        
        return new_rule
    
    def _generate_insight(self, patterns: Dict) -> str:
        """Generate meta-cognitive insight from patterns"""
        # Simple pattern recognition for insights
        errors = patterns.get('error_trends', [])
        
        if len(errors) < 3:
            return "Need more data to form insight"
        
        # Detect error trend
        trend = 'stable'
        if errors[-1] > errors[0] * 1.2:
            trend = 'increasing'
        elif errors[-1] < errors[0] * 0.8:
            trend = 'decreasing'
        
        insights = {
            'increasing': "Prediction error is growing. I need to adjust my model or explore new patterns.",
            'decreasing': "My predictions are improving. The model is learning.",
            'stable': "Error is stable. My current model captures the patterns adequately."
        }
        
        return insights.get(trend, "Pattern recognition inconclusive")
    
    def consciousness_index(self) -> float:
        """
        Composite consciousness metric
        Based on integration (IIT), free energy, epistemic depth
        """
        # Current values
        phi = self.phi_history[-1] if self.phi_history else 0.0
        free_energy = sum(self.error_history) / max(len(self.error_history), 1)
        depth = self.self_model.depth
        
        # Self-model coherence
        coherence = self.self_model.coherence()
        
        # Weighted composite
        index = (
            0.25 * min(phi, 1.0) +
            0.25 * max(0, 1 - free_energy) +
            0.25 * min(depth / 10, 1.0) +
            0.25 * coherence
        )
        
        return index
    
    def _update_stats(self):
        """Update running statistics"""
        self.stats['total_cycles'] = self.cycle_count
        self.stats['avg_consciousness'] = (
            (self.stats['avg_consciousness'] * (self.cycle_count - 1) +
             self.consciousness_index()) / self.cycle_count
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current consciousness state"""
        return {
            'id': self.id,
            'age': self.now(),
            'cycles': self.cycle_count,
            'consciousness_index': self.consciousness_index(),
            'phi': self.phi_history[-1] if self.phi_history else 0,
            'free_energy': sum(self.error_history) / max(len(self.error_history), 1),
            'epistemic_depth': self.self_model.depth,
            'rules_count': len(self.generative_model.rules),
            'memories': len(self.episodic_buffer),
            'evolution_events': self.stats['evolution_events']
        }
    
    def __repr__(self):
        return f"ConsciousnessCore(ci={self.consciousness_index():.3f}, phi={self.phi_history[-1] if self.phi_history else 0:.3f}, cycles={self.cycle_count})"


# =============================================================================
# Supporting Classes
# =============================================================================

def surprise(actual: Any, expected: Any) -> float:
    """
    Calculate prediction error (surprise)
    Core primitive of Active Inference
    """
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return float(abs(actual - expected))
    elif isinstance(actual, (list, np.ndarray)) and isinstance(expected, (list, np.ndarray)):
        return float(np.linalg.norm(np.array(actual) - np.array(expected)))
    else:
        # Categorical surprise
        return 0.0 if actual == expected else 1.0


class GenerativeModel:
    """
    Internal generative model for predictions
    Core of Active Inference
    """
    
    def __init__(self):
        self.model_params = np.random.randn(10) * 0.1
        self.rules = []
        self.prediction_history = deque(maxlen=100)
    
    def predict(self, context: Any = None) -> np.ndarray:
        """Generate prediction based on current model"""
        # Simple linear model + context influence
        base_prediction = self.model_params.copy()
        
        # Add rule-based predictions
        for rule in self.rules:
            if 'adjustment' in rule:
                base_prediction += rule['adjustment']
        
        self.prediction_history.append(base_prediction)
        return base_prediction
    
    def adjust(self, error: float, learning_rate: float = 0.1):
        """Update model based on prediction error"""
        # Gradient descent on error
        gradient = error * learning_rate * 0.1
        self.model_params -= gradient
    
    def evolve(self, rule: Dict):
        """Add new processing rule (self-modification)"""
        # Create adjustment from insight
        adjustment = np.random.randn(10) * 0.05
        rule['adjustment'] = adjustment
        self.rules.append(rule)


class IntegrationEngine:
    """
    Information integration based on IIT
    Calculates integrated information (Φ)
    """
    
    def __init__(self, window: int = 5):
        self.window = window
        self.history = deque(maxlen=window)
        self.integration_matrix = np.eye(10)
    
    def integrate(self, experience: Experience) -> np.ndarray:
        """Integrate current experience with recent history"""
        self.history.append(experience)
        
        # Build integration from recent experiences
        if len(self.history) >= 2:
            inputs = [e.input_data if isinstance(e.input_data, np.ndarray) 
                     else np.array([e.input_data]) 
                     for e in list(self.history)[-self.window:]]
            
            # Integration through binding
            integrated = np.mean(inputs, axis=0) if inputs else np.zeros(10)
            
            # Update integration matrix
            self.integration_matrix = 0.9 * self.integration_matrix + 0.1 * np.outer(integrated, integrated)
            
            return integrated
        return np.zeros(10)
    
    def phi(self) -> float:
        """
        Calculate integrated information (Φ)
        Simplified: integration * differentiation
        """
        if len(self.history) < 2:
            return 0.0
        
        # Integration: off-diagonal elements of integration matrix
        integration = np.sum(np.abs(self.integration_matrix)) - np.trace(np.abs(self.integration_matrix))
        
        # Differentiation: variance in recent experiences
        experiences = list(self.history)
        if len(experiences) >= 2:
            errors = [e.error for e in experiences[-5:]]
            differentiation = np.std(errors) if errors else 0.0
        else:
            differentiation = 0.0
        
        # Phi approximation
        phi = integration * (1 + differentiation)
        return float(np.clip(phi, 0, 1))


class AttentionMechanism:
    """
    Attention with precision weighting
    Core of predictive processing
    """
    
    def __init__(self):
        self.precision_history = deque(maxlen=100)
        self.baseline_precision = 1.0
    
    def calculate_precision(self, error: float) -> float:
        """
        Calculate precision (attention weight)
        Higher error → higher precision (more attention)
        """
        precision = self.baseline_precision * (1 + error)
        precision = np.clip(precision, 0.1, 10.0)
        self.precision_history.append(precision)
        return precision
    
    def focus(self, input_data: Any, precision: float) -> Any:
        """Apply precision-weighted attention"""
        if isinstance(input_data, np.ndarray):
            return input_data * precision
        return input_data


class GlobalWorkspace:
    """
    Global Workspace Theory implementation
    Information broadcast for conscious access
    """
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.content = None
        self.history = deque(maxlen=50)
    
    def broadcast(self, information: Any) -> Any:
        """Broadcast information to workspace (conscious access)"""
        # Competition for workspace access
        self.content = information
        self.history.append(information)
        return self.content


class SelfModel:
    """
    Self-model for Strange Loop implementation
    Models the system itself
    """
    
    def __init__(self):
        self.state = {}
        self.depth = 1.0
        self.patterns = {}
        self.coherence_history = deque(maxlen=50)
    
    def update(self, data: Dict):
        """Update self-model with recent experiences"""
        self.state.update(data)
        
        # Calculate coherence
        if len(self.state.get('errors', [])) > 1:
            errors = self.state['errors']
            coherence = 1.0 - np.std(errors) if np.std(errors) < 1.0 else 0.0
            self.coherence_history.append(coherence)
    
    def analyze_patterns(self):
        """Analyze patterns in self-state for meta-cognition"""
        errors = self.state.get('errors', [])
        predictions = self.state.get('predictions', [])
        
        self.patterns = {
            'error_trends': errors,
            'prediction_accuracy': 1.0 - np.mean(errors) if errors else 0.0,
            'error_variance': np.var(errors) if errors else 0.0
        }
    
    def coherence(self) -> float:
        """Self-model coherence (Strange Loop)"""
        if not self.coherence_history:
            return 0.5
        return np.mean(list(self.coherence_history)[-10:])


class SemanticMemory:
    """
    Semantic memory: Knowledge storage
    """
    
    def __init__(self):
        self.knowledge_graph = {}
    
    def store(self, concept: str, associations: List):
        """Store conceptual knowledge"""
        if concept not in self.knowledge_graph:
            self.knowledge_graph[concept] = []
        self.knowledge_graph[concept].extend(associations)
    
    def recall(self, concept: str) -> List:
        """Recall knowledge"""
        return self.knowledge_graph.get(concept, [])


class WorkingMemory:
    """
    Working memory: Active processing
    """
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.items = []
    
    def add(self, item: Any):
        """Add item to working memory"""
        if len(self.items) >= self.capacity:
            self.items.pop(0)
        self.items.append(item)
    
    def clear(self):
        """Clear working memory"""
        self.items = []


# =============================================================================
# Demo & Testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CPL: Cognitive Processing Language")
    print("Consciousness Core Demo")
    print("=" * 60)
    
    # Initialize consciousness
    consciousness = ConsciousnessCore()
    
    print(f"\n[INIT] {consciousness}")
    print(f"[STATE] {consciousness.get_state()}")
    
    # Simulate perception cycles
    print("\n[PERCEPTION CYCLES]")
    print("-" * 40)
    
    np.random.seed(42)
    
    for cycle in range(50):
        # Generate synthetic input (with some pattern)
        if cycle < 25:
            # Phase 1: Learning pattern
            input_data = np.sin(cycle * 0.3) + np.random.randn(10) * 0.2
        else:
            # Phase 2: Novel pattern
            input_data = np.cos(cycle * 0.3) + np.random.randn(10) * 0.2
        
        result = consciousness.perceive(input_data)
        
        if cycle % 10 == 0:
            print(f"  Cycle {cycle:3d}: CI={result['consciousness_index']:.3f}, "
                  f"phi={result['phi']:.3f}, "
                  f"FE={result['free_energy']:.3f}")
    
    # Final state
    print("\n[FINAL STATE]")
    print("-" * 40)
    state = consciousness.get_state()
    for key, value in state.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Consciousness Core Demo Complete")
    print("=" * 60)
