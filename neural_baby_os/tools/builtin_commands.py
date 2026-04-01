from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional

from neural_baby_os.tools.base import Tool, ToolExecutionResult


def _resolve_safe_path(root: Path, rel_path: str) -> Path:
    target = (root / rel_path).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise ValueError("Access outside allowed root is not permitted")
    return target


def make_command_tool(root: Path, timeout_default_s: float = 15.0) -> Tool:
    """
    Command tool with basic safety:
    - runs with subprocess timeout
    - optional working directory restricted under root
    - supports a configurable allowlist of command names via args['allowlist'] (optional)
    """

    def run(args: Dict[str, Any]) -> ToolExecutionResult:
        start = perf_counter()
        cmd_text = str(args.get("command", "")).strip()
        if not cmd_text:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Missing 'command' argument",
                duration_s=0.0,
                meta={},
            )

        timeout_s = float(args.get("timeout_s", timeout_default_s))
        cwd_rel = str(args.get("cwd", "."))
        cwd: Optional[str] = None
        try:
            cwd_target = _resolve_safe_path(root, cwd_rel)
            if cwd_target.exists() and cwd_target.is_dir():
                cwd = str(cwd_target)
        except Exception:
            cwd = None

        # Optional allowlist for the command name the user provided.
        allowlist = args.get("allowlist")
        tokens: List[str] = shlex.split(cmd_text, posix=os.name != "nt")
        if not tokens:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Could not parse command",
                duration_s=0.0,
                meta={},
            )

        user_first = tokens[0].lower()

        # Windows shell built-ins like `echo` and `dir` are not standalone executables.
        # If the user uses them, route through `cmd /c`.
        if os.name == "nt" and user_first in {"echo", "dir"}:
            tokens = ["cmd", "/c"] + tokens

        if allowlist:
            allowed = {str(x).lower() for x in allowlist}
            if user_first not in allowed:
                return ToolExecutionResult(
                    ok=False,
                    stdout="",
                    stderr=f"Command '{user_first}' not allowed by allowlist",
                    duration_s=0.0,
                    meta={"command": cmd_text, "first": user_first},
                )

        try:
            proc = subprocess.run(
                tokens,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_s,
                text=True,
                shell=False,
            )
            ok = proc.returncode == 0
            # Keep logs short
            stdout = (proc.stdout or "")[:20_000]
            stderr = (proc.stderr or "")[:20_000]
            return ToolExecutionResult(
                ok=ok,
                stdout=stdout,
                stderr=stderr,
                duration_s=perf_counter() - start,
                meta={
                    "command": cmd_text,
                    "returncode": proc.returncode,
                    "cwd": cwd_rel,
                },
            )
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Command timed out after {timeout_s}s",
                duration_s=perf_counter() - start,
                meta={"command": cmd_text, "timeout_s": timeout_s},
            )
        except Exception as exc:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=str(exc),
                duration_s=perf_counter() - start,
                meta={"command": cmd_text},
            )

    return Tool(
        name="cmd.run",
        description="Run a command with subprocess timeout and restricted working directory.",
        schema={"command": "string", "cwd": "relative path under root", "timeout_s": "float"},
        run=run,
    )

