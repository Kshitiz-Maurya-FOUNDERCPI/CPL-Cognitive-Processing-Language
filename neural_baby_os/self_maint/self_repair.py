from __future__ import annotations

import traceback
from pathlib import Path
from typing import Callable


def run_with_supervisor(loop_fn: Callable[[], None], max_restarts: int = 3) -> None:
    """
    Wrap a life loop with simple crash logging and limited restarts.
    """
    log_dir = Path(__file__).resolve().parent.parent / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    restarts = 0
    while True:
        try:
            loop_fn()
            break
        except KeyboardInterrupt:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            restarts += 1
            log_path = log_dir / f"crash_{restarts}.log"
            with log_path.open("w", encoding="utf-8") as fh:
                fh.write("Neural Baby Agentic OS crash report\n")
                fh.write(f"Restart #{restarts}\n\n")
                fh.write("Exception:\n")
                fh.write(f"{exc!r}\n\n")
                fh.write("Traceback:\n")
                fh.write("".join(traceback.format_exc()))

            if restarts >= max_restarts:
                print(f"Fatal: exceeded max restarts ({max_restarts}). See {log_path}")
                break
            print(f"Crash detected, restarting (attempt {restarts}/{max_restarts})")

