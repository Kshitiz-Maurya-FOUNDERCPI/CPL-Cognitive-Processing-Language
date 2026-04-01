from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None


@dataclass
class SystemSnapshot:
    time_of_day: float
    battery_level: float
    cpu_load: float
    mem_used: float
    file_count: int

    def as_vector(self) -> np.ndarray:
        return np.array(
            [
                self.time_of_day,
                self.battery_level,
                self.cpu_load,
                self.mem_used,
                float(self.file_count),
            ],
            dtype=float,
        )


class SystemSensors:
    """
    Cross-platform snapshots of basic system state.

    This is intentionally lightweight so it works on Windows and Termux.
    """

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir else Path.home()

    def read_time(self) -> float:
        now = datetime.now()
        return (now.hour * 3600 + now.minute * 60 + now.second) / 86400.0

    def read_battery(self) -> float:
        if psutil is None or not hasattr(psutil, "sensors_battery"):
            return 0.0
        try:
            info = psutil.sensors_battery()
        except Exception:
            return 0.0
        if info is None or info.percent is None:
            return 0.0
        return float(info.percent) / 100.0

    def read_cpu_mem(self) -> Dict[str, float]:
        if psutil is None:
            return {"cpu": 0.0, "mem": 0.0}
        try:
            cpu = float(psutil.cpu_percent(interval=0.0)) / 100.0
            mem = float(psutil.virtual_memory().percent) / 100.0
        except Exception:
            cpu, mem = 0.0, 0.0
        return {"cpu": cpu, "mem": mem}

    def sample_files(self, max_entries: int = 256) -> int:
        count = 0
        try:
            for _root, _dirs, files in os.walk(self.root_dir):
                count += len(files)
                if count >= max_entries:
                    break
        except Exception:
            return 0
        return min(count, max_entries)

    def snapshot(self) -> SystemSnapshot:
        t = self.read_time()
        b = self.read_battery()
        usage = self.read_cpu_mem()
        file_count = self.sample_files()
        return SystemSnapshot(
            time_of_day=t,
            battery_level=b,
            cpu_load=usage["cpu"],
            mem_used=usage["mem"],
            file_count=file_count,
        )

