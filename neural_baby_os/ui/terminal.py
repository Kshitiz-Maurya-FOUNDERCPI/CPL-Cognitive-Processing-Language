from __future__ import annotations

import shlex
import threading
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from neural_baby_os.core.action_intent import ActionIntent
from neural_baby_os.core.engine import NeuralBabyAgent
from neural_baby_os.self_maint.self_repair import run_with_supervisor
from neural_baby_os.sensory.system_sensors import SystemSensors
from neural_baby_os.tools.manager import ToolManager
from neural_baby_os.tools.skills import Skill, Skill as _Skill, SkillsStore, ToolCallStep


def _input_thread(stop_flag: dict, commands: Queue[str]) -> None:
    while not stop_flag["stop"]:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if line:
            commands.put(line)
        if line.lower() in {"quit", "exit"}:
            stop_flag["stop"] = True


def _coerce_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith(("'", '"')) and raw.endswith(("'", '"')):
        return raw[1:-1]
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except Exception:
        return raw


def parse_kv_args(arg_tokens: List[str]) -> Dict[str, Any]:
    args: Dict[str, Any] = {}
    for tok in arg_tokens:
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        args[k.strip()] = _coerce_value(v)
    return args


class AgentToolRunner:
    def __init__(self, *, tick_seconds: float = 1.0) -> None:
        self.tick_seconds = tick_seconds
        self.sensors = SystemSensors()
        self.agent = NeuralBabyAgent(input_dim=5, output_dim=2)

        data_dir = Path(__file__).resolve().parent.parent / "data"
        # Safe file operations root:
        # default to agent data dir so the agent stays contained.
        file_root = data_dir
        self.tool_manager = ToolManager(
            data_dir=data_dir,
            file_root=file_root,
            episode_callback=None,
        )
        self.skills_store = SkillsStore(data_dir=data_dir)

        self.intent_queue: Queue[ActionIntent] = Queue()
        self.last_context_vec: Optional[np.ndarray] = None
        self.stop_flag = False

    def enqueue_intent(self, intent: ActionIntent) -> None:
        self.intent_queue.put(intent)

    def _execute_tool_intent(self, intent: ActionIntent) -> None:
        assert intent.kind == "tool"
        ctx = (
            self.last_context_vec
            if self.last_context_vec is not None
            else np.zeros(self.agent.input_dim, dtype=float)
        )
        res = self.tool_manager.execute_tool(
            intent.name,
            intent.args,
            current_step=self.agent.step_count,
            confirm_fn=None,
            bypass_confirm=intent.bypass_confirm,
        )
        val_delta = 0.2 if res.ok else -0.3
        self.agent.record_action_episode(
            sensory_context=ctx,
            action={"kind": "tool", "tool": intent.name, "args": intent.args, "ok": res.ok},
            valence_delta=val_delta,
        )

    def _execute_skill_intent(self, intent: ActionIntent) -> None:
        assert intent.kind == "skill"
        skill = self.skills_store.get(intent.name)
        if skill is None:
            return
        ctx = (
            self.last_context_vec
            if self.last_context_vec is not None
            else np.zeros(self.agent.input_dim, dtype=float)
        )
        for step in skill.steps:
            # Execute each tool so we can record tool-by-tool episodes.
            res = self.tool_manager.execute_tool(
                step.tool,
                step.args,
                current_step=self.agent.step_count,
                confirm_fn=None,
                bypass_confirm=intent.bypass_confirm,
            )
            val_delta = 0.2 if res.ok else -0.3
            self.agent.record_action_episode(
                sensory_context=ctx,
                action={
                    "kind": "tool",
                    "tool": step.tool,
                    "args": step.args,
                    "ok": res.ok,
                },
                valence_delta=val_delta,
            )
            if not res.ok:
                break

    def run_forever(self) -> None:
        while not self.stop_flag:
            snap = self.sensors.snapshot()
            raw_vec = snap.as_vector()
            resource_pressure = (snap.cpu_load + snap.mem_used) / 2.0
            self.last_context_vec = raw_vec

            # Tick the brain.
            self.agent.step(raw_vec, resource_pressure=resource_pressure)

            # Drain pending intents quickly.
            while True:
                try:
                    intent = self.intent_queue.get_nowait()
                except Empty:
                    break

                if intent.kind == "tool":
                    self._execute_tool_intent(intent)
                elif intent.kind == "skill":
                    self._execute_skill_intent(intent)

            # Simple sleep; run.py already has more elaborate throttling.
            import time

            time.sleep(self.tick_seconds)

    def shutdown(self) -> None:
        self.stop_flag = True


def simple_terminal_ui() -> None:
    stop_flag = {"stop": False}
    commands: Queue[str] = Queue()
    record_mode = {"active": False, "steps": []}  # type: ignore[var-annotated]
    # steps: list[ToolCallStep]
    runner: Optional[AgentToolRunner] = None

    def runner_main() -> None:
        nonlocal runner
        runner = AgentToolRunner(tick_seconds=1.0)
        runner.run_forever()

    # Supervisor will restart runner on crash.
    runner_thread = threading.Thread(
        target=lambda: run_with_supervisor(runner_main, max_restarts=3),
        daemon=True,
    )
    runner_thread.start()

    input_t = threading.Thread(
        target=_input_thread, args=(stop_flag, commands), daemon=True
    )
    input_t.start()

    print("Neural Baby Agentic OS – Skill/Tools Terminal UI")
    print("Commands: tools list, tools enable/disable/policy, tools run <tool> key=val...,")
    print("skills: skill list, skill run <name>, skill record start|stop <name>|cancel, status, quit\n")

    try:
        while not stop_flag["stop"]:
            try:
                cmd = commands.get(timeout=0.1)
            except Empty:
                continue

            if runner is None:
                continue

            lower = cmd.lower().strip()
            if lower in {"quit", "exit"}:
                stop_flag["stop"] = True
                break

            if lower == "status":
                st = runner.agent.get_status()
                print(f"step={st['step']} mood={st['mood']} val={st['valence']} salience? episodes={st.get('episodes',0)}")
                continue

            parts = shlex.split(cmd)
            if not parts:
                continue

            if parts[0] == "tools":
                if len(parts) == 2 and parts[1] == "list":
                    reg = runner.tool_manager.list_tools()
                    for name, meta in reg.items():
                        pol = meta["policy"]
                        print(
                            f"{name}: enabled={meta['enabled']} succ={meta['success_count']} fail={meta['failure_count']} policy={{auto={pol['auto_execute']}, ask={pol['ask_each_time']}}}"
                        )
                    continue

                if len(parts) == 2 and parts[1] == "recommend":
                    ranked = runner.tool_manager.ranked_tools()
                    print("Recommended tools (best expected success first):")
                    for name, score in ranked:
                        print(f"- {name}: expected_success={score:.3f}")
                    continue

                if len(parts) >= 3 and parts[1] in {"enable", "disable"}:
                    name = parts[2]
                    runner.tool_manager.set_tool_enabled(name, parts[1] == "enable")
                    print(f"{parts[1]}d {name}")
                    continue

                if len(parts) >= 4 and parts[1] == "policy":
                    name = parts[2]
                    pol = parts[3].lower()
                    if pol == "auto":
                        runner.tool_manager.set_tool_policy(name, auto_execute=True, ask_each_time=False)
                    elif pol == "ask":
                        runner.tool_manager.set_tool_policy(name, auto_execute=False, ask_each_time=True)
                    else:
                        print("policy must be auto or ask")
                        continue
                    print(f"policy for {name} set to {pol}")
                    continue

                if len(parts) >= 4 and parts[1] == "run":
                    tool_name = parts[2]
                    arg_tokens = parts[3:]
                    args = parse_kv_args(arg_tokens)
                    # Record step if recording.
                    if record_mode["active"]:
                        record_mode["steps"].append(ToolCallStep(tool=tool_name, args=args))
                    intent = ActionIntent(kind="tool", name=tool_name, args=args, bypass_confirm=True)
                    runner.enqueue_intent(intent)
                    print(f"Enqueued tool: {tool_name}")
                    continue

                print("tools usage: tools list | tools enable <name> | tools disable <name> | tools policy <name> auto|ask | tools run <tool> k=v ...")
                continue

            if parts[0] == "skill":
                if len(parts) == 2 and parts[1] == "list":
                    for name in runner.skills_store.list_names():
                        skill = runner.skills_store.get(name)
                        steps_len = len(skill.steps) if skill else 0
                        print(f"{name} (steps={steps_len})")
                    continue

                if len(parts) >= 3 and parts[1] == "run":
                    name = parts[2]
                    intent = ActionIntent(kind="skill", name=name, args={}, bypass_confirm=True)
                    runner.enqueue_intent(intent)
                    print(f"Enqueued skill: {name}")
                    continue

                if len(parts) >= 2 and parts[1] == "record":
                    if len(parts) >= 3 and parts[2] == "start":
                        record_mode["active"] = True
                        record_mode["steps"] = []
                        print("Skill recording started.")
                        continue
                    if len(parts) >= 3 and parts[2] == "cancel":
                        record_mode["active"] = False
                        record_mode["steps"] = []
                        print("Skill recording cancelled.")
                        continue
                    if len(parts) >= 4 and parts[2] == "stop":
                        name = parts[3]
                        steps = record_mode["steps"]
                        skill = Skill(name=name, description="", steps=steps)
                        runner.skills_store.upsert(skill)
                        record_mode["active"] = False
                        record_mode["steps"] = []
                        print(f"Saved skill '{name}' with {len(steps)} steps.")
                        continue
                    print("skill record usage: skill record start | skill record stop <name> | skill record cancel")
                    continue

                print("skill usage: skill list | skill run <name> | skill record ...")
                continue

            print("Unknown command.")
    except KeyboardInterrupt:
        stop_flag["stop"] = True

    if runner is not None:
        runner.shutdown()
    print("Exiting Terminal UI.")


if __name__ == "__main__":
    simple_terminal_ui()

