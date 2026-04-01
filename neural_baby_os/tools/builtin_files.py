from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List

from neural_baby_os.tools.base import Tool, ToolExecutionResult


def _resolve_safe_path(root: Path, rel_path: str) -> Path:
    """
    Resolve a user-supplied relative path under a fixed root.
    Prevents escaping via .. segments.
    """
    target = (root / rel_path).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise ValueError("Access outside allowed root is not permitted")
    return target


def make_list_dir_tool(root: Path) -> Tool:
    def run(args: Dict[str, Any]) -> ToolExecutionResult:
        start = perf_counter()
        rel = str(args.get("path", "."))
        max_entries = int(args.get("max_entries", 100))
        try:
            target = _resolve_safe_path(root, rel)
            if not target.exists() or not target.is_dir():
                raise FileNotFoundError(f"Directory not found: {rel}")
            entries: List[str] = []
            for name in os.listdir(target):
                entries.append(name)
                if len(entries) >= max_entries:
                    break
            stdout = "\n".join(entries)
            return ToolExecutionResult(
                ok=True,
                stdout=stdout,
                stderr="",
                duration_s=perf_counter() - start,
                meta={"count": len(entries), "path": str(rel)},
            )
        except Exception as exc:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=str(exc),
                duration_s=perf_counter() - start,
                meta={"path": str(rel)},
            )

    return Tool(
        name="files.list_dir",
        description="List entries in a directory under the configured root.",
        schema={"path": "relative directory path", "max_entries": "int, optional"},
        run=run,
    )


def make_read_file_tool(root: Path, max_bytes: int = 64_000) -> Tool:
    def run(args: Dict[str, Any]) -> ToolExecutionResult:
        start = perf_counter()
        rel = str(args.get("path", ""))
        if not rel:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Missing 'path' argument",
                duration_s=0.0,
                meta={},
            )
        try:
            target = _resolve_safe_path(root, rel)
            if not target.exists() or not target.is_file():
                raise FileNotFoundError(f"File not found: {rel}")
            data = target.read_bytes()[:max_bytes]
            try:
                text = data.decode("utf-8", errors="replace")
            except Exception:
                text = ""
            return ToolExecutionResult(
                ok=True,
                stdout=text,
                stderr="",
                duration_s=perf_counter() - start,
                meta={"path": str(rel), "size": len(data)},
            )
        except Exception as exc:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=str(exc),
                duration_s=perf_counter() - start,
                meta={"path": str(rel)},
            )

    return Tool(
        name="files.read_text",
        description="Read a small UTF-8 text file under the configured root.",
        schema={"path": "relative file path"},
        run=run,
    )


def make_write_file_tool(root: Path, max_bytes: int = 64_000) -> Tool:
    def run(args: Dict[str, Any]) -> ToolExecutionResult:
        start = perf_counter()
        rel = str(args.get("path", ""))
        content = str(args.get("content", ""))
        if not rel:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Missing 'path' argument",
                duration_s=0.0,
                meta={},
            )
        if len(content.encode("utf-8")) > max_bytes:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Content too large for safe write",
                duration_s=0.0,
                meta={"max_bytes": max_bytes},
            )
        try:
            target = _resolve_safe_path(root, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return ToolExecutionResult(
                ok=True,
                stdout=f"Wrote {len(content)} characters to {rel}",
                stderr="",
                duration_s=perf_counter() - start,
                meta={"path": str(rel), "chars": len(content)},
            )
        except Exception as exc:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=str(exc),
                duration_s=perf_counter() - start,
                meta={"path": str(rel)},
            )

    return Tool(
        name="files.write_text",
        description="Write a small UTF-8 text file under the configured root.",
        schema={"path": "relative file path", "content": "string"},
        run=run,
    )

