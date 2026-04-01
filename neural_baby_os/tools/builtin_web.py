from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict
from urllib.parse import urlparse
from time import perf_counter

from neural_baby_os.tools.base import Tool, ToolExecutionResult


@dataclass
class WebRateState:
    last_fetch_ts: float = 0.0
    min_interval_s: float = 3.0


def make_web_fetch_tool(rate_state: WebRateState, timeout_s: float = 12.0) -> Tool:
    def run(args: Dict[str, Any]) -> ToolExecutionResult:
        start = perf_counter()

        url = str(args.get("url", "")).strip()
        max_bytes = int(args.get("max_bytes", 25_000))
        if not url:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Missing 'url' argument",
                duration_s=0.0,
                meta={},
            )

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Only http/https URLs are allowed",
                duration_s=0.0,
                meta={"url": url},
            )
        host = parsed.hostname or ""
        if host in {"localhost", "127.0.0.1", "::1"}:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr="Localhost fetch is not allowed",
                duration_s=0.0,
                meta={"url": url},
            )

        now = time.time()
        elapsed = now - rate_state.last_fetch_ts
        if elapsed < rate_state.min_interval_s:
            wait_s = rate_state.min_interval_s - elapsed
            # Keep it responsive: fail fast if called too quickly.
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Rate limited: wait {wait_s:.2f}s before fetching again",
                duration_s=perf_counter() - start,
                meta={"url": url, "rate_wait_s": wait_s},
            )

        try:
            with urllib.request.urlopen(url, timeout=timeout_s) as resp:
                raw = resp.read(max_bytes)
            rate_state.last_fetch_ts = time.time()
            text = raw.decode("utf-8", errors="replace")
            # Basic cleanup: avoid huge blobs.
            text = text[:20_000]
            return ToolExecutionResult(
                ok=True,
                stdout=text,
                stderr="",
                duration_s=perf_counter() - start,
                meta={"url": url, "bytes": len(raw)},
            )
        except urllib.error.HTTPError as e:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"HTTPError: {e.code}",
                duration_s=perf_counter() - start,
                meta={"url": url},
            )
        except urllib.error.URLError as e:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"URLError: {e.reason}",
                duration_s=perf_counter() - start,
                meta={"url": url},
            )
        except socket.timeout:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=f"Web fetch timed out after {timeout_s}s",
                duration_s=perf_counter() - start,
                meta={"url": url},
            )
        except Exception as exc:
            return ToolExecutionResult(
                ok=False,
                stdout="",
                stderr=str(exc),
                duration_s=perf_counter() - start,
                meta={"url": url},
            )

    return Tool(
        name="web.fetch",
        description="Fetch a web page (http/https) and return extracted text (best-effort).",
        schema={"url": "string", "max_bytes": "int, optional"},
        run=run,
    )

