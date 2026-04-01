from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, Optional, Tuple

from neural_baby_os.tools.base import Tool, ToolExecutionResult
from neural_baby_os.tools.builtin_commands import make_command_tool
from neural_baby_os.tools.builtin_files import (
    make_list_dir_tool,
    make_read_file_tool,
    make_write_file_tool,
)
from neural_baby_os.tools.builtin_web import WebRateState, make_web_fetch_tool
from neural_baby_os.tools.learner import rank_tools
from neural_baby_os.tools.registry import ToolMeta, ToolPolicy, ToolRegistry
from neural_baby_os.tools.skills import Skill, Skill as _Skill


ConfirmFn = Callable[[str, Dict[str, Any], str], bool]
EpisodeCallback = Callable[[Dict[str, Any]], None]


def _now_step_meta(tool_meta: ToolMeta, current_step: int) -> bool:
    return current_step < tool_meta.cooldown_until_step


class ToolManager:
    def __init__(
        self,
        data_dir: Path,
        file_root: Path,
        tool_registry: Optional[ToolRegistry] = None,
        episode_callback: Optional[EpisodeCallback] = None,
    ) -> None:
        self.data_dir = data_dir
        self.file_root = file_root
        self.episode_callback = episode_callback

        self.logs_dir = self.data_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.registry = tool_registry or ToolRegistry(data_dir=self.data_dir)

        # Instantiate built-in tools.
        self.tool_impls: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        # Default policy:
        # - read/list: auto
        # - write/cmd/web: ask
        defaults: Dict[str, ToolPolicy] = {
            "files.list_dir": ToolPolicy(auto_execute=True, ask_each_time=False),
            "files.read_text": ToolPolicy(auto_execute=True, ask_each_time=False),
            "files.write_text": ToolPolicy(auto_execute=False, ask_each_time=True),
            "cmd.run": ToolPolicy(auto_execute=False, ask_each_time=True),
            "web.fetch": ToolPolicy(auto_execute=False, ask_each_time=True),
        }

        # Create tool implementations.
        self.tool_impls["files.list_dir"] = make_list_dir_tool(self.file_root)
        self.tool_impls["files.read_text"] = make_read_file_tool(self.file_root)
        self.tool_impls["files.write_text"] = make_write_file_tool(self.file_root)
        self.tool_impls["cmd.run"] = make_command_tool(self.file_root)

        web_rate = WebRateState(last_fetch_ts=0.0, min_interval_s=3.0)
        self.tool_impls["web.fetch"] = make_web_fetch_tool(rate_state=web_rate)

        # Ensure registry entries exist for all built-ins and have defaults.
        for name in self.tool_impls.keys():
            meta = self.registry.ensure_tool(name)
            if name in defaults:
                meta.policy = defaults[name]

        self.registry.save()

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        for name, meta in sorted(self.registry.tools.items()):
            out[name] = {
                "enabled": meta.enabled,
                "cooldown_until_step": meta.cooldown_until_step,
                "success_count": meta.success_count,
                "failure_count": meta.failure_count,
                "policy": {
                    "auto_execute": meta.policy.auto_execute,
                    "ask_each_time": meta.policy.ask_each_time,
                },
            }
        return out

    def set_tool_enabled(self, name: str, enabled: bool) -> None:
        meta = self.registry.ensure_tool(name)
        meta.enabled = enabled
        self.registry.save()

    def set_tool_policy(self, name: str, auto_execute: bool, ask_each_time: bool) -> None:
        meta = self.registry.ensure_tool(name)
        meta.policy = ToolPolicy(auto_execute=auto_execute, ask_each_time=ask_each_time)
        self.registry.save()

    def ranked_tools(self, candidate: Optional[list[str]] = None) -> list[tuple[str, float]]:
        tools = candidate or list(self.tool_impls.keys())
        return rank_tools(self.registry, tools)

    def _log_tool_event(self, payload: Dict[str, Any]) -> None:
        path = self.logs_dir / "tool_history.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        *,
        current_step: int,
        confirm_fn: Optional[ConfirmFn] = None,
        bypass_confirm: bool = False,
    ) -> ToolExecutionResult:
        if tool_name not in self.tool_impls:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Unknown tool: {tool_name}",
                duration_s=0.0,
                meta={},
            )

        meta = self.registry.tools.get(tool_name)
        if meta is None or not meta.enabled:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Tool disabled: {tool_name}",
                duration_s=0.0,
                meta={"tool": tool_name},
            )

        # Cooldown
        if current_step < meta.cooldown_until_step:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Tool in cooldown until step {meta.cooldown_until_step}",
                duration_s=0.0,
                meta={"tool": tool_name, "cooldown_until_step": meta.cooldown_until_step},
            )

        # Policy check
        policy = meta.policy
        need_confirm = (not bypass_confirm) and policy.ask_each_time and confirm_fn is not None
        if not bypass_confirm and policy.ask_each_time and confirm_fn is None:
            # Can't ask, fail safely.
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Confirmation required for tool '{tool_name}' but no confirm_fn provided.",
                duration_s=0.0,
                meta={"tool": tool_name},
            )

        if (not bypass_confirm) and policy.ask_each_time:
            assert confirm_fn is not None
            ok = confirm_fn(tool_name, args, "confirm_tool")
            if not ok:
                # Count as "failure" to reflect reduced utility?
                self.registry.record_failure(tool_name, current_step=current_step, cooldown_steps=3)
                self.registry.save()
                return ToolExecutionResult(
                    ok=False,
                    stdout="",
                    stderr="Tool execution cancelled by user",
                    duration_s=0.0,
                    meta={"tool": tool_name, "cancelled": True},
                )

        start = perf_counter()
        try:
            result = self.tool_impls[tool_name].run(args)
            # normalize duration_s
            result.duration_s = perf_counter() - start
        except Exception as exc:
            result = ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=str(exc),
                duration_s=perf_counter() - start,
                meta={"tool": tool_name, "exception": True},
            )

        # Update stats + cooldown
        if result.ok:
            self.registry.record_success(tool_name)
            self.registry.save()
        else:
            self.registry.record_failure(tool_name, current_step=current_step, cooldown_steps=10)

            # Self-repair / downgrade if it fails too many times.
            meta_after = self.registry.tools.get(tool_name)
            if meta_after and meta_after.failure_count >= 3:
                meta_after.enabled = False
                # Keep it disabled for longer.
                meta_after.cooldown_until_step = max(
                    meta_after.cooldown_until_step, current_step + 50
                )
                self.registry.save()

                diag_payload = {
                    "step": current_step,
                    "tool": tool_name,
                    "action": "disabled_due_to_repeated_failures",
                    "failure_count": meta_after.failure_count,
                    "suggestion": "User can re-enable via: tools enable <tool_name> in the terminal UI.",
                }
                path = self.logs_dir / "tool_diagnostics.jsonl"
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(diag_payload, ensure_ascii=False) + "\n")

            self.registry.save()

        # Log
        log_payload = {
            "step": current_step,
            "tool": tool_name,
            "args": args,
            "ok": result.ok,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:2000],
            "duration_s": result.duration_s,
        }
        self._log_tool_event(log_payload)

        # Optional episode callback for learning.
        if self.episode_callback is not None:
            valence_delta = 0.2 if result.ok else -0.3
            self.episode_callback(
                {
                    "kind": "tool_episode",
                    "tool": tool_name,
                    "ok": result.ok,
                    "valence_delta": valence_delta,
                    "result": {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "duration_s": result.duration_s,
                    },
                    "step": current_step,
                }
            )

        return result

    def execute_skill(
        self,
        skill: Skill,
        *,
        current_step: int,
        confirm_fn: Optional[ConfirmFn] = None,
        bypass_confirm: bool = False,
    ) -> ToolExecutionResult:
        """
        Executes a skill as a sequence of tool calls.
        Returns ok only if all steps ok.
        """
        overall_stdout = []
        overall_stderr = []
        all_ok = True
        start = perf_counter()
        last_result: Optional[ToolExecutionResult] = None

        for st in skill.steps:
            r = self.execute_tool(
                st.tool,
                st.args,
                current_step=current_step,
                confirm_fn=confirm_fn,
                bypass_confirm=bypass_confirm,
            )
            last_result = r
            if r.ok:
                overall_stdout.append(f"[{st.tool}] {r.stdout[:500]}")
            else:
                all_ok = False
                overall_stderr.append(f"[{st.tool}] {r.stderr[:500]}")
        duration = perf_counter() - start
        if last_result is None:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Skill had no steps",
                duration_s=duration,
                meta={"skill": skill.name},
            )
        return ToolExecutionResult(
            ok=all_ok,
            stdout="\n".join(overall_stdout)[:20_000],
            stderr="\n".join(overall_stderr)[:20_000],
            duration_s=duration,
            meta={"skill": skill.name},
        )

