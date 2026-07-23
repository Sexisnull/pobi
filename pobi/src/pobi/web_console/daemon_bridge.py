"""Bridge between the Web Console and the Pobi JSON-RPC daemon.

The daemon (`pobi-jsonrpc-server`) speaks JSON-RPC 2.0 over newline-delimited
JSON on stdin/stdout. This module:

  * spawns the daemon as a subprocess (auto-detecting a working invocation),
  * implements a small async JSON-RPC client over that pipe,
  * keeps a single long-lived `subscribe_events` subscription and re-broadcasts
    every agent event to the web console's SSE clients,
  * transparently falls back to an in-process simulator when the daemon cannot
    be reached (so the console is always runnable / demoable).
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
from typing import Any, Awaitable, Callable, Optional

from .settings import settings

EventCallback = Callable[[dict], Awaitable[None]]
RPCError = type("RPCError", (Exception,), {})


class DaemonBridge:
    def __init__(self) -> None:
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.mode: str = "offline"  # "daemon" | "simulation"
        self.connected: bool = False
        self.daemon_error: Optional[str] = None

        self._pending: dict[int, dict] = {}
        self._req_id = 0
        self._reader_task: Optional[asyncio.Task] = None
        self._write_lock = asyncio.Lock()

        self._event_subscribers: set[asyncio.Queue] = set()
        self.simulator = None  # set by the API layer
        self._scan_tasks: dict[str, asyncio.Task] = {}

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def _resolve_daemon_cmd(self) -> Optional[list[str]]:
        if settings.daemon_cmd:
            return settings.daemon_cmd
        cli_dir = settings.pobi_dir
        venv_py = cli_dir / ".venv" / "bin" / "python"
        if venv_py.exists():
            return [str(venv_py), "-m", "pobi.jsonrpc_server"]
        if shutil.which("uv") and cli_dir.exists():
            return ["uv", "run", "pobi-jsonrpc-server"]
        if shutil.which("python"):
            return ["python", "-m", "pobi.jsonrpc_server"]
        if shutil.which("python3"):
            return ["python3", "-m", "pobi.jsonrpc_server"]
        return None

    async def connect(self) -> str:
        if settings.force_simulation:
            self.mode = "simulation"
            self.connected = True
            return self.mode

        cmd = self._resolve_daemon_cmd()
        if not cmd:
            self.mode = "simulation"
            self.connected = True
            self.daemon_error = "No daemon invocation found; using simulation."
            return self.mode

        cwd = str(settings.pobi_dir) if cmd[0] in ("uv",) else str(settings.repo_root)
        try:
            env = dict(os.environ)
            env.setdefault("PYTHONUNBUFFERED", "1")
            # Redirect the daemon's stderr to a log file (NOT a pipe) so a chatty
            # daemon cannot fill the pipe buffer and deadlock itself.
            self._daemon_err = open(str(settings.data_dir / "daemon.log"), "ab", buffering=0)
            self.proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=self._daemon_err,
                cwd=cwd,
                env=env,
            )
        except Exception as exc:  # pragma: no cover - environment dependent
            self.mode = "simulation"
            self.connected = True
            self.daemon_error = f"Failed to spawn daemon ({exc}); using simulation."
            return self.mode

        self._reader_task = asyncio.create_task(self._reader_loop())
        # Probe readiness with a lightweight call that does not touch heavy components.
        try:
            await asyncio.wait_for(self.call("get_approval_mode"), timeout=settings.connect_timeout)
            self.mode = "daemon"
            self.connected = True
            await self.subscribe_events()
        except Exception as exc:
            self.mode = "simulation"
            self.connected = True
            self.daemon_error = f"Daemon reachable but unresponsive ({exc}); using simulation."
            await self._terminate_daemon()
        return self.mode

    async def _terminate_daemon(self) -> None:
        if self.proc and self.proc.returncode is None:
            try:
                self.proc.terminate()
                await asyncio.wait_for(self.proc.wait(), timeout=5)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        self.proc = None

    async def shutdown(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
        for t in self._scan_tasks.values():
            t.cancel()
        await self._terminate_daemon()
        if getattr(self, "_daemon_err", None):
            try:
                self._daemon_err.close()
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    # JSON-RPC client
    # ------------------------------------------------------------------ #
    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _write(self, msg: dict) -> None:
        if not self.proc or not self.proc.stdin:
            raise RPCError("Daemon not connected")
        async with self._write_lock:
            self.proc.stdin.write((json.dumps(msg) + "\n").encode())
            await self.proc.stdin.drain()

    async def call(self, method: str, params: Optional[dict] = None, timeout: Optional[float] = None):
        """One-shot JSON-RPC call. Returns the `result` payload."""
        if self.mode == "simulation":
            return await self._sim_call(method, params or {})
        rid = self._next_id()
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[rid] = {"future": fut, "streaming": False, "results": []}
        await self._write({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
        try:
            return await asyncio.wait_for(fut, timeout or settings.request_timeout)
        except asyncio.TimeoutError:
            self._pending.pop(rid, None)
            raise RPCError(f"Timeout calling {method}")

    async def call_stream(self, method: str, params: Optional[dict], on_chunk: Callable[[dict], None]):
        """Streaming JSON-RPC call. Each result chunk is delivered to `on_chunk`.
        Returns when the stream ends. Errors are raised."""
        if self.mode == "simulation":
            await self._sim_stream(method, params or {}, on_chunk)
            return
        rid = self._next_id()
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[rid] = {"future": fut, "streaming": True, "results": [], "on_chunk": on_chunk}
        await self._write({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
        return await asyncio.wait_for(fut, timeout=max(settings.request_timeout, 3600))

    async def subscribe_events(self) -> None:
        """Open the long-lived event subscription and re-broadcast to clients."""
        if self.mode == "simulation":
            return
        rid = self._next_id()
        self._pending[rid] = {
            "streaming": True,
            "results": [],
            "on_chunk": lambda chunk: self._broadcast_event(chunk.get("event", chunk)),
        }

        async def _kick():
            try:
                await self._write({"jsonrpc": "2.0", "id": rid, "method": "subscribe_events", "params": {}})
            except Exception:
                pass

        asyncio.create_task(_kick())

    async def _reader_loop(self) -> None:
        assert self.proc and self.proc.stdout
        try:
            while True:
                line = await self.proc.stdout.readline()
                if not line:
                    break
                line = line.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "method" in msg and "id" not in msg:
                    # server -> client notification (not used today)
                    continue
                rid = msg.get("id")
                if rid is None or rid not in self._pending:
                    continue
                entry = self._pending[rid]
                if "error" in msg:
                    err = msg["error"]
                    if entry.get("future") and not entry["future"].done():
                        entry["future"].set_exception(RPCError(str(err)))
                    self._pending.pop(rid, None)
                    continue
                result = msg.get("result")
                # Streaming termination sentinel.
                if isinstance(result, dict) and result.get("_end"):
                    if entry.get("future") and not entry["future"].done():
                        entry["future"].set_result(entry["results"])
                    self._pending.pop(rid, None)
                    continue
                if "on_chunk" in entry and callable(entry["on_chunk"]):
                    try:
                        entry["on_chunk"](result)
                    except Exception:
                        pass
                if entry.get("streaming"):
                    entry["results"].append(result)
                elif entry.get("future") and not entry["future"].done():
                    entry["future"].set_result(result)
                    self._pending.pop(rid, None)
        except asyncio.CancelledError:
            pass
        finally:
            self.connected = False

    # ------------------------------------------------------------------ #
    # Scan orchestration (used by the API layer)
    # ------------------------------------------------------------------ #
    async def start_scan(self, params: dict) -> str:
        """Launch run_agent_recursive as a background task; events stream via SSE."""
        session_id = params.get("session_id") or f"session-{os.urandom(4).hex()}"
        params = {**params, "session_id": session_id}
        if self.mode == "simulation":
            task = asyncio.create_task(self._sim_run_scan(params))
        else:
            task = asyncio.create_task(self.call_stream("run_agent_recursive", params, lambda c: None))
        self._scan_tasks[session_id] = task
        return session_id

    async def embed_target(self, params: dict) -> None:
        if self.mode == "simulation":
            asyncio.create_task(self._sim_embed(params))
        else:
            asyncio.create_task(self.call_stream("embed_target", params, lambda c: None))

    # ------------------------------------------------------------------ #
    # Event fan-out to SSE clients
    # ------------------------------------------------------------------ #
    def add_subscriber(self, queue: asyncio.Queue) -> None:
        self._event_subscribers.add(queue)

    def remove_subscriber(self, queue: asyncio.Queue) -> None:
        self._event_subscribers.discard(queue)

    def _broadcast_event(self, event: dict) -> None:
        for q in list(self._event_subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass

    @property
    def subscriber_count(self) -> int:
        return len(self._event_subscribers)

    # ------------------------------------------------------------------ #
    # Simulation backend (delegated to Simulator)
    # ------------------------------------------------------------------ #
    async def _sim_call(self, method: str, params: dict):
        if self.simulator is None:
            raise RPCError("Simulator not configured")
        return await self.simulator.handle(method, params)

    async def _sim_stream(self, method: str, params: dict, on_chunk):
        if self.simulator is None:
            raise RPCError("Simulator not configured")
        await self.simulator.stream(method, params, on_chunk)

    async def _sim_run_scan(self, params: dict) -> None:
        if self.simulator is None:
            return
        await self.simulator.run_scan(params, self._broadcast_event)

    async def _sim_embed(self, params: dict) -> None:
        if self.simulator is None:
            return
        await self.simulator.run_embed(params, self._broadcast_event)
