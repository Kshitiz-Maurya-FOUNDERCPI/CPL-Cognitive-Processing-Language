import time
from typing import List

from neural_baby_os.core.engine import NeuralBabyAgent
from neural_baby_os.sensory.system_sensors import SystemSensors
from neural_baby_os.self_maint.self_repair import run_with_supervisor


def life_loop(tick_seconds: float = 1.0) -> None:
    """
    Foreground life loop using real system sensors as input.
    """
    sensors = SystemSensors()
    agent = NeuralBabyAgent(input_dim=5, output_dim=2)

    print("Neural Baby Agentic OS – life loop with system sensors")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            snap = sensors.snapshot()
            raw_vec = snap.as_vector()
            # Resource pressure proxy: average of cpu and mem usage.
            resource_pressure = (snap.cpu_load + snap.mem_used) / 2.0
            status = agent.step(raw_vec, resource_pressure=resource_pressure)

            line_parts: List[str] = [
                f"step={status['step']}",
                f"time={snap.time_of_day:.2f}",
                f"bat={snap.battery_level:.2f}",
                f"cpu={snap.cpu_load:.2f}",
                f"mood={status['mood']}",
                f"val={status['valence']}",
                f"sal={status.get('salience', 0.0):.2f}",
            ]
            print(" | ".join(line_parts))

            # Simple resource-aware throttling: slow down more when pressure is high.
            sleep_factor = 1.0 + resource_pressure
            time.sleep(tick_seconds * sleep_factor)
    except KeyboardInterrupt:
        print("\nShutting down Neural Baby loop.")


if __name__ == "__main__":
    run_with_supervisor(lambda: life_loop())

