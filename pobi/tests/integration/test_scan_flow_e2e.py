# Copyright (C) 2025 Yassine Bargach
# Licensed under the GNU Affero General Public License v3
# See LICENSE file for full license information.

"""End-to-end scan-flow tests, mirroring exactly what the web console (app.js)
does when launching a scan:

    POST /api/agents            -> instantiate_agent   (create agent + sandbox)
    POST /api/agents/{id}/embed -> embed_target        (crawl + embed RAG)
    POST /api/scans             -> run_agent_recursive (start the pentest)

Two seams are covered (per the agreed TDD plan):

  * Seam A - HTTP Web API layer (TestWebScanFlow*): drives the real FastAPI
    endpoints the browser hits, so HTTP-layer flow bugs (e.g. the previous
    "agent_id required" 400, missing embed step, errors not surfaced) are caught.
  * Seam B - RPC layer (TestRpcScanFlow*): drives the daemon JSON-RPC directly,
    exercising the real orchestration code (lazy init of config / model_registry
    / docker / sandbox, crawl+embed, recursive run).

Run modes
---------
  * Simulation tests (no external infra) run the full web sequence against the
    in-process simulator and validate ordering (embed MUST complete before the
    scan starts). These run anywhere, fast.
  * Real-daemon tests are marked ``docker`` + ``slow`` and require a running
    Docker + a configured LLM. They are skipped automatically when Docker is
    unavailable, so the suite stays green locally; run them in your infra env
    with ``pytest -m docker`` to observe the real-penetration-test flow.
"""
import asyncio
import json
import os
import shutil
import subprocess
import pytest

from fastapi.testclient import TestClient

from pobi.web_console.api import app, bridge, simulator


# --------------------------------------------------------------------------- #
# Infra helpers
# --------------------------------------------------------------------------- #
def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        proc = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=8
        )
        return proc.returncode == 0
    except Exception:
        return False


DOCKER_SKIP = pytest.mark.skipif(
    not _docker_available() or os.environ.get("PEN_TEST_E2E") != "1",
    reason="Real-daemon scan-flow tests need Docker + LLM and PEN_TEST_E2E=1",
)


def _rpc_client_class():
    """Minimal JSON-RPC stdio client mirroring tests/integration/test_rpc_server.py."""

    class RPCClient:
        def __init__(self, process):
            self.process = process
            self._rid = 0

        async def call(self, method, params=None, timeout=600.0):
            self._rid += 1
            rid = self._rid
            await self._write({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
            return await self._read(rid, timeout)

        async def _write(self, msg):
            if self.process.stdin:
                self.process.stdin.write((json.dumps(msg) + "\n").encode())
                await self.process.stdin.drain()

        async def _read(self, rid, timeout):
            while True:
                line = await asyncio.wait_for(self.process.stdout.readline(), timeout)
                if not line:
                    raise EOFError("server closed stdout")
                try:
                    msg = json.loads(line.decode())
                except json.JSONDecodeError:
                    continue
                if msg.get("id") != rid:
                    continue
                if "error" in msg:
                    raise RuntimeError(f"RPC error: {msg['error']}")
                return msg.get("result")

    return RPCClient


# --------------------------------------------------------------------------- #
# Seam A - HTTP Web API layer (simulation, runnable everywhere)
# --------------------------------------------------------------------------- #
@pytest.fixture
def sim_client():
    """FastAPI TestClient wired to the in-process simulator (no Docker/LLM).

    We pin the bridge to simulation mode directly (instead of via the
    ``settings.force_simulation`` flag) because in some environments the
    ``settings`` module resolves to a second instance, so the flag would not
    be seen by ``daemon_bridge`` and the bridge would spawn a real daemon.
    """
    original_connect = type(bridge).connect

    async def _noop_connect(self):
        self.mode = "simulation"
        self.connected = True
        return "simulation"

    type(bridge).connect = _noop_connect
    simulator.agents.clear()
    simulator.sessions.clear()
    simulator.agent_session.clear()
    bridge.simulator = simulator
    bridge.mode = "simulation"
    bridge.connected = True
    try:
        with TestClient(app) as client:
            yield client
    finally:
        type(bridge).connect = original_connect
        bridge.mode = "init"
        bridge.connected = False


def test_web_scan_flow_mirrors_app_js_sequence(sim_client):
    """The web page does instantiate -> embed -> run; each step must succeed
    in order and surface a proper HTTP contract (no 500 / silent failure)."""
    target = "http://127.0.0.1:8005"

    # 1) instantiate agent
    r = sim_client.post(
        "/api/agents",
        json={"target": target, "provider": "openai", "model_name": "gpt-4o"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "agent_id" in body, body
    agent_id = body["agent_id"]

    # 2) embed target (crawl + embed RAG)
    r = sim_client.post(
        f"/api/agents/{agent_id}/embed",
        json={"target": target, "session_id": "sess-embed"},
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"accepted": True}

    # 3) start the scan
    r = sim_client.post(
        "/api/scans",
        json={"agent_id": agent_id, "target": target, "prompt": "scan"},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("session_id")


def test_embed_target_awaits_full_completion():
    """RED->GREEN regression for the flow bug where ``embed_target`` was
    fire-and-forget: ``/api/agents/{id}/embed`` returned before the
    crawl+embed finished, so the scan could start against an un-embedded
    target (the original deadend-cli awaits ``embedTarget``).

    We drive ``bridge.embed_target`` directly (single event loop, loop-safe)
    and assert that the WHOLE embed -- up to the ``embed_done`` event -- has
    completed by the time the coroutine returns. With the bug (fire-and-forget)
    the coroutine returns before the task even starts, so the event queue is
    still empty -> test fails (RED). After the fix it awaits -> GREEN.
    """
    import asyncio

    bridge.simulator = simulator
    bridge.mode = "simulation"
    bridge.connected = True
    simulator.agents.clear()
    simulator.sessions.clear()
    simulator.agent_session.clear()
    aid = "agent-x"
    simulator.agents[aid] = {"target": "http://127.0.0.1:8005"}
    sid = "sess-embed"

    def _phase(ev: dict):
        # Events nest extra fields under ``data`` (see simulator._ev).
        return ev.get("phase") or (ev.get("data") or {}).get("phase")

    async def _run():
        q: asyncio.Queue = asyncio.Queue()
        bridge._event_subscribers.add(q)
        await bridge.embed_target(
            {"agent_id": aid, "target": "http://127.0.0.1:8005", "session_id": sid}
        )
        # At this exact point the embedding must already be DONE. If
        # embed_target is fire-and-forget the event loop has not run the task
        # yet -> empty queue.
        assert not q.empty(), (
            "embed_target returned before embedding completed (fire-and-forget bug)"
        )
        saw_done = False
        while not q.empty():
            ev = q.get_nowait()
            if _phase(ev) == "embed_done":
                saw_done = True
                break
        assert saw_done, "embed completed but embed_done event missing"
        bridge._event_subscribers.discard(q)

    # pytest may already own an event loop in this thread; drive the coroutine
    # on a fresh, dedicated loop to avoid "loop already running" conflicts.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def test_web_scan_flow_rejects_missing_agent_id(sim_client):
    """The web page always supplies agent_id; a missing one must be a clean 400
    (the bug we fixed earlier), never a 500."""
    r = sim_client.post("/api/scans", json={"target": "http://x", "prompt": "scan"})
    assert r.status_code == 400
    assert "agent_id required" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# Seam A - HTTP Web API layer (REAL daemon, docker + slow)
# --------------------------------------------------------------------------- #
@DOCKER_SKIP
@pytest.mark.docker
@pytest.mark.slow
@pytest.mark.integration
class TestWebScanFlowRealDaemon:
    """Full web sequence against a real daemon (Docker + configured LLM).

    These never run automatically. In an environment with Docker, a configured
    LLM and a real target, opt in with::

        PEN_TEST_E2E=1 pytest -m docker tests/integration/test_scan_flow_e2e.py
    """

    @pytest.mark.asyncio
    async def test_full_flow(self):
        import httpx

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Give the bridge time to spawn + probe the real daemon.
            for _ in range(100):
                if bridge.mode == "daemon":
                    break
                await asyncio.sleep(0.05)
            if bridge.mode != "daemon":
                pytest.skip(f"daemon not reachable: {bridge.daemon_error}")

            target = "http://127.0.0.1:8005"  # replace with a real target in your env

            r = await client.post(
                "/api/agents",
                json={"target": target, "provider": "openai", "model_name": "gpt-4o"},
            )
            assert r.status_code == 200, r.text
            agent_id = r.json()["agent_id"]
            assert agent_id

            r = await client.post(f"/api/agents/{agent_id}/embed", json={"target": target})
            assert r.status_code == 200, r.text

            r = await client.post(
                "/api/scans",
                json={"agent_id": agent_id, "target": target, "prompt": "scan"},
            )
            assert r.status_code == 200, r.text
            session_id = r.json()["session_id"]
            assert session_id

            # Observe the running flow until it terminates (or times out).
            import time
            deadline = time.time() + 1800
            final = None
            while time.time() < deadline:
                snap = (await client.get(f"/api/sessions/{session_id}")).json()
                final = snap
                if snap.get("status") in ("completed", "aborted", "failed"):
                    break
                await asyncio.sleep(5)
            assert final is not None
            assert final.get("status") in ("completed", "aborted", "failed"), final


# --------------------------------------------------------------------------- #
# Seam B - RPC layer (REAL daemon, docker + slow)
# --------------------------------------------------------------------------- #
@DOCKER_SKIP
@pytest.mark.docker
@pytest.mark.slow
@pytest.mark.integration
class TestRpcScanFlow:
    """Drive instantiate_agent -> embed_target directly on the daemon JSON-RPC,
    exercising the real orchestration path (lazy init of config / model_registry
    / docker / sandbox, then crawl+embed). The recursive run is long-running, so
    it is observed manually via the web UI; here we assert the setup steps that
    are the ones most prone to the "not initialized" class of flow bugs.
    """

    @pytest.fixture
    async def rpc_process(self, tmp_path):
        import pathlib
        pobi_dir = pathlib.Path(__file__).parent.parent.parent
        log_file = str(tmp_path / "rpc_server.log")
        proc = await asyncio.create_subprocess_exec(
            "uv", "run", "python", "-m", "pobi.jsonrpc_server",
            "--log-file", log_file,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(pobi_dir),
        )
        yield proc
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5)
            except Exception:
                proc.kill()

    @pytest.fixture
    async def rpc(self, rpc_process):
        RPCClient = _rpc_client_class()
        yield RPCClient(rpc_process)

    @pytest.mark.asyncio
    async def test_instantiate_and_embed(self, rpc):
        target = "http://127.0.0.1:8005"  # replace with a real target in your env

        res = await rpc.call("instantiate_agent", {
            "target": target, "provider": "openai", "model_name": "gpt-4o",
        })
        assert res.get("status") in ("ok", None) or "agent_id" in res, res
        agent_id = res.get("agent_id")
        assert agent_id, res

        res = await rpc.call("embed_target", {"agent_id": agent_id, "target": target})
        assert res.get("status") != "failed", res
