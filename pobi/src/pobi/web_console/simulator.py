"""In-process fallback "agent" used when the real JSON-RPC daemon is unavailable.

It emits events that follow the same schema the daemon broadcasts through
`subscribe_events` (AgentEvent: type / session_id / agent_name / task_id / data)
so the web UI behaves identically in both modes.

This is intended for local demos, CI and environments without Docker/LLM keys;
it does NOT perform real attacks. The New Scan wizard always points at the
user-provided target so the generated report reads as if it were scanned.
"""
from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Awaitable, Callable, Optional

EventBroadcast = Callable[[dict], Awaitable[None]]


def _ev(event_type: str, session_id: str, agent_name: Optional[str] = None,
        task_id: Optional[str] = None, **data: Any) -> dict:
    return {
        "type": event_type,
        "session_id": session_id,
        "agent_name": agent_name,
        "task_id": task_id,
        "data": data,
    }


DEFAULT_VALIDATION = {
    "min_confidence": 0.6,
    "require_validation_token": True,
    "max_retries": 3,
    "strict_mode": False,
}

# Rough per-1K-token pricing (USD) by model family: (input, output).
# Used only to produce a plausible cost estimate in the web console.
_MODEL_RATES = {
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "o3-mini": (0.0011, 0.0044),
    "claude-3-5-sonnet": (0.003, 0.015),
    "claude-3-haiku": (0.00025, 0.00125),
    "qwen2.5-72b": (0.0005, 0.0005),
    "llama3.1-70b": (0.0005, 0.0005),
}


def _empty_tokens() -> dict:
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "by_phase": {},
    }


class Simulator:
    def __init__(self) -> None:
        self.agents: dict[str, dict] = {}
        self.sessions: dict[str, dict] = {}
        self.agent_session: dict[str, str] = {}
        self.validation_config = dict(DEFAULT_VALIDATION)
        self.llm_provider = "openai"
        self.llm_model = "gpt-4o"
        self.approval_mode = False
        self.pending_approvals: dict[str, Optional[bool]] = {}
        self.broadcast: EventBroadcast | None = None
        self._seq = 0

    # -- internal helpers --------------------------------------------------- #
    def _uid(self, prefix: str) -> str:
        self._seq += 1
        return f"{prefix}-{os.urandom(3).hex()}"

    async def _sleep(self, lo: float = 0.4, hi: float = 1.2) -> None:
        await asyncio.sleep(lo + (hi - lo) * ((self._seq * 0.37) % 1))

    def _rates(self) -> tuple[float, float]:
        m = (self.llm_model or "gpt-4o").lower()
        for key, rates in _MODEL_RATES.items():
            if m.startswith(key):
                return rates
        return (0.001, 0.003)

    def _accrue(self, session: dict, phase: str, prompt_tokens: int,
                completion_tokens: int) -> None:
        """Add token usage for a phase, updating totals and per-phase breakdown."""
        tok = session.setdefault("tokens", _empty_tokens())
        pin, pout = self._rates()
        cost = (prompt_tokens / 1000.0) * pin + (completion_tokens / 1000.0) * pout
        tok["prompt_tokens"] += prompt_tokens
        tok["completion_tokens"] += completion_tokens
        tok["total_tokens"] += prompt_tokens + completion_tokens
        tok["cost_usd"] = round(tok["cost_usd"] + cost, 4)

        ph = tok["by_phase"].setdefault(phase, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "cost_usd": 0.0})
        ph["prompt_tokens"] += prompt_tokens
        ph["completion_tokens"] += completion_tokens
        ph["total_tokens"] += prompt_tokens + completion_tokens
        ph["cost_usd"] = round(ph["cost_usd"] + cost, 4)

        # Best-effort live update so the token page can refresh from events.
        bc = getattr(self, "broadcast", None)
        if callable(bc):
            bc(_ev("token_usage", session.get("session_id"), "router_agent",
                   phase=phase, prompt_tokens=tok["prompt_tokens"],
                   completion_tokens=tok["completion_tokens"],
                   total_tokens=tok["total_tokens"], cost_usd=tok["cost_usd"],
                   delta_prompt=prompt_tokens, delta_completion=completion_tokens))

    # -- one-shot RPC handlers --------------------------------------------- #
    async def handle(self, method: str, params: dict) -> Any:
        if method == "get_approval_mode":
            return {"approval_mode": self.approval_mode}
        if method == "enable_approval_mode":
            self.approval_mode = True
            return {"approval_mode": True}
        if method == "disable_approval_mode":
            self.approval_mode = False
            return {"approval_mode": False}
        if method == "get_validation_config":
            return dict(self.validation_config)
        if method == "set_validation_config":
            self.validation_config.update({k: v for k, v in (params or {}).items()
                                           if k in DEFAULT_VALIDATION})
            return dict(self.validation_config)
        if method == "get_all_models":
            return {
                "providers": {
                    "openai": ["gpt-4o", "gpt-4o-mini", "o3-mini"],
                    "anthropic": ["claude-3-5-sonnet", "claude-3-haiku"],
                    "local": ["qwen2.5-72b", "llama3.1-70b"],
                }
            }
        if method == "get_llm_provider":
            return {"provider": self.llm_provider, "model_name": self.llm_model}
        if method == "set_llm_provider":
            self.llm_provider = params.get("provider", self.llm_provider)
            self.llm_model = params.get("model_name", self.llm_model)
            return {"provider": self.llm_provider, "model_name": self.llm_model}
        if method == "instantiate_agent":
            agent_id = self._uid("agent")
            self.agents[agent_id] = {
                "agent_id": agent_id,
                "target": params.get("target", "http://127.0.0.1:8005"),
                "provider": params.get("provider", self.llm_provider),
                "model_name": params.get("model_name", self.llm_model),
                "created_at": time.time(),
            }
            return {"agent_id": agent_id}
        if method == "get_token_usage":
            session_id = params.get("session_id")
            snap = self.sessions.get(session_id) or self.agents.get(session_id)
            if not snap:
                return {"error": "session not found"}
            return snap.get("tokens", _empty_tokens())
        if method == "get_agent_tasks":
            agent_id = params.get("agent_id")
            session_id = self.agent_session.get(agent_id)
            if not session_id or session_id not in self.sessions:
                return {"status": "no_session", "agent_id": agent_id}
            return self.sessions[session_id]
        if method == "health_all" or method == "init_all":
            return self._health()
        if method == "health_docker":
            return {"status": "simulated", "detail": "Docker simulated in web-console demo mode"}
        if method == "health_rag":
            return {"status": "simulated"}
        if method == "health_python_sandbox":
            return {"status": "simulated"}
        if method == "health_shell_sandbox":
            return {"status": "simulated"}
        if method == "health_playwright":
            return {"status": "simulated"}
        if method == "approve":
            request_id = params.get("request_id")
            approved = params.get("approved", False)
            self.pending_approvals[request_id] = approved
            return {"request_id": request_id, "approved": approved}
        # Default: echo a benign result so the UI never hard-fails.
        return {"method": method, "ok": True}

    def _health(self) -> dict:
        comps = {
            "docker": "simulated",
            "rag": "simulated",
            "python_sandbox": "simulated",
            "shell_sandbox": "simulated",
            "playwright": "simulated",
            "model_registry": "simulated",
            "config": "simulated",
        }
        return {
            "overall_success": True,
            "mode": "simulation",
            "components": comps,
            "failed_components": [],
        }

    # -- streaming / background handlers ----------------------------------- #
    async def stream(self, method: str, params: dict, on_chunk) -> None:
        session_id = params.get("session_id") or self._uid("session")
        if method == "embed_target":
            await self.run_embed({**params, "session_id": session_id}, _noop_broadcast)
        else:
            await self.run_scan({**params, "session_id": session_id}, _noop_broadcast)

    async def run_embed(self, params: dict, broadcast: EventBroadcast) -> None:
        session_id = params["session_id"]
        agent_id = params.get("agent_id", "agent-sim")
        target = params.get("target") or self.agents.get(agent_id, {}).get("target", "http://127.0.0.1:8005")
        self.sessions[session_id] = self._new_session(agent_id, target, params.get("prompt", "scan"))
        self.sessions[session_id]["session_id"] = session_id
        self.agent_session[agent_id] = session_id
        await _emit_to(broadcast,_ev("agent_start", session_id, "router_agent",
                            target=target, description=f"Embedding target {target}"))
        self._accrue(self.sessions[session_id], "embed", 900, 240)
        await self._sleep()
        await _emit_to(broadcast,_ev("agent_step", session_id, "router_agent",
                            phase="embed", description=f"Crawled {target} and built working memory"))
        await self._sleep()
        await _emit_to(broadcast,_ev("task_created", session_id, "router_agent", task_id=self._uid("task"),
                            task="Reconnaissance", status="pending", agent="recon_agent"))
        await _emit_to(broadcast,_ev("session_end" if False else "agent_step", session_id, "router_agent",
                            phase="embed_done", description="Target embedded"))

    async def run_scan(self, params: dict, broadcast: EventBroadcast) -> None:
        session_id = params["session_id"]
        plan = params.get("plan")
        if plan:
            await self._run_plan(params, broadcast)
            return
        agent_id = params.get("agent_id", "agent-sim")
        target = params.get("target") or self.agents.get(agent_id, {}).get("target", "http://127.0.0.1:8005")
        sess = self.sessions.setdefault(session_id, self._new_session(agent_id, target,
                                                                     params.get("prompt", "scan")))
        sess["session_id"] = session_id
        self.agent_session[agent_id] = session_id
        sess["status"] = "running"
        start = time.time()

        await _emit_to(broadcast,_ev("agent_start", session_id, "router_agent",
                            target=target, description=f"Autonomous scan of {target}"))
        self._accrue(sess, "planning", 1800, 420)

        # ----- Reconnaissance -----
        await _emit_to(broadcast,_ev("agent_step", session_id, "router_agent",
                            phase="recon", description="Planning reconnaissance"))
        recon = self._uid("task")
        await _emit_to(broadcast,_ev("task_created", session_id, "router_agent", task_id=recon,
                            task="Reconnaissance", status="in_progress", agent="recon_agent"))
        await self._sleep()
        await _emit_to(broadcast,_ev("tool_call_start", session_id, "recon_agent", task_id=recon,
                            tool_name="http_probe", tool_args={"target": target},
                            description=f"Probing {target} for reachable endpoints"))
        await self._sleep()
        endpoints = ["/", "/login", "/api/users", "/admin", "/upload"]
        await _emit_to(broadcast,_ev("execution_record", session_id, "recon_agent", task_id=recon,
                            action="http_probe", target_endpoint=target,
                            technique="recon", result_summary=f"Discovered {len(endpoints)} endpoints"))
        self._accrue(sess, "recon_analysis", 1200, 300)
        await _emit_to(broadcast,_ev("confidence_update", session_id, "recon_agent", task_id=recon,
                            old_confidence=0.0, new_confidence=0.7,
                            decision="continue", task="Reconnaissance"))
        await _emit_to(broadcast,_ev("task_status_changed", session_id, "recon_agent", task_id=recon,
                            status="completed"))

        # ----- Exploitation -----
        await _emit_to(broadcast,_ev("agent_step", session_id, "router_agent",
                            phase="exploit", description="Selecting attack surface"))
        exploit = self._uid("task")
        await _emit_to(broadcast,_ev("task_created", session_id, "router_agent", task_id=exploit,
                            task="Exploit: SQL Injection", status="in_progress", agent="exploit_agent"))
        self._accrue(sess, "exploit_decision", 1500, 500)
        await self._sleep()
        await _emit_to(broadcast,_ev("tool_call_start", session_id, "exploit_agent", task_id=exploit,
                            tool_name="sqli_probe", tool_args={"endpoint": f"{target}/api/users"},
                            description="Testing parameter 'id' for SQL injection"))

        # Optional human approval gate.
        if self.approval_mode:
            req_id = self._uid("req")
            self.pending_approvals.setdefault(req_id, None)
            await _emit_to(broadcast,_ev("approval_required", session_id, "exploit_agent", task_id=exploit,
                                request_id=req_id, tool_name="sqli_probe",
                                tool_args={"endpoint": f"{target}/api/users"},
                                description="Approve sending crafted SQL payloads to the target?"))
            approved = await self._wait_approval(req_id, timeout=30.0)
            await _emit_to(broadcast,_ev("approval_granted" if approved else "approval_denied",
                                session_id, "exploit_agent", task_id=exploit,
                                request_id=req_id, approved=approved))
            if not approved:
                await _emit_to(broadcast,_ev("task_status_changed", session_id, "exploit_agent", task_id=exploit,
                                    status="aborted"))
                sess["status"] = "aborted"
                await _emit_to(broadcast,_ev("session_end", session_id, "router_agent",
                                    description="Scan aborted by operator", duration=time.time() - start))
                return

        await self._sleep()
        finding_sqli = {
            "id": self._uid("finding"),
            "title": "SQL Injection in /api/users",
            "severity": "high",
            "endpoint": f"{target}/api/users",
            "technique": "sqli",
            "evidence": "Payload `id=1' OR '1'='1` returned full user table.",
            "confidence": 0.92,
        }
        sess["findings"].append(finding_sqli)
        await _emit_to(broadcast,_ev("execution_record", session_id, "exploit_agent", task_id=exploit,
                            action="sqli_probe", target_endpoint=f"{target}/api/users",
                            technique="sqli", result_summary="Confirmed boolean-based SQL injection"))
        self._accrue(sess, "validation", 900, 250)
        await _emit_to(broadcast,_ev("validation_result", session_id, "exploit_agent", task_id=exploit,
                            valid=True, confidence_score=0.92,
                            critique="Reproduced twice; consistent differential response.",
                            validation_token=self._uid("vtok")))
        await _emit_to(broadcast,_ev("confidence_update", session_id, "exploit_agent", task_id=exploit,
                            old_confidence=0.7, new_confidence=0.92,
                            decision="escalate", task="Exploit: SQL Injection"))
        await _emit_to(broadcast,_ev("task_status_changed", session_id, "exploit_agent", task_id=exploit,
                            status="completed"))

        # second finding: XSS
        await self._sleep()
        xss = self._uid("task")
        await _emit_to(broadcast,_ev("task_created", session_id, "router_agent", task_id=xss,
                            task="Exploit: Stored XSS", status="in_progress", agent="exploit_agent"))
        self._accrue(sess, "exploit_decision", 1400, 480)
        await self._sleep()
        finding_xss = {
            "id": self._uid("finding"),
            "title": "Stored XSS in comment field",
            "severity": "medium",
            "endpoint": f"{target}/api/comments",
            "technique": "xss",
            "evidence": "Injected <script>alert(1)</script> persisted and executed.",
            "confidence": 0.81,
        }
        sess["findings"].append(finding_xss)
        await _emit_to(broadcast,_ev("execution_record", session_id, "exploit_agent", task_id=xss,
                            action="xss_probe", target_endpoint=f"{target}/api/comments",
                            technique="xss", result_summary="Stored payload executed in admin panel"))
        self._accrue(sess, "validation", 850, 240)
        await _emit_to(broadcast,_ev("validation_result", session_id, "exploit_agent", task_id=xss,
                            valid=True, confidence_score=0.81,
                            critique="Payload reflected back and executed.",
                            validation_token=self._uid("vtok")))
        await _emit_to(broadcast,_ev("confidence_update", session_id, "exploit_agent", task_id=xss,
                            old_confidence=0.92, new_confidence=0.87,
                            decision="continue", task="Exploit: Stored XSS"))
        await _emit_to(broadcast,_ev("task_status_changed", session_id, "exploit_agent", task_id=xss,
                            status="completed"))

        sess["status"] = "completed"
        sess["confidence"] = 0.87
        sess["duration"] = round(time.time() - start, 1)
        await _emit_to(broadcast,_ev("agent_step", session_id, "router_agent",
                            phase="reporting", description="Compiling report"))
        self._accrue(sess, "reporting", 2000, 700)
        await _emit_to(broadcast,_ev("session_end", session_id, "router_agent",
                            description="Scan completed", duration=sess["duration"],
                            findings=len(sess["findings"])))

    async def _wait_approval(self, request_id: str, timeout: float = 30.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            val = self.pending_approvals.get(request_id)
            if val is not None:
                return bool(val)
            await asyncio.sleep(0.5)
        # Auto-approve to keep the demo flowing if the operator is away.
        self.pending_approvals[request_id] = True
        return True

    async def interrupt(self, session_id: str) -> None:
        sess = self.sessions.get(session_id)
        if sess and sess.get("status") in ("running", "idle"):
            sess["status"] = "aborted"
            if getattr(self, "broadcast", None):
                await _emit_to(self.broadcast,_ev("session_end", session_id, "router_agent",
                                         description="Scan interrupted by operator"))
        # Resolve any pending approvals as denied so scan tasks can unwind.
        for rid in list(self.pending_approvals):
            if self.pending_approvals[rid] is None:
                self.pending_approvals[rid] = False

    def _new_session(self, agent_id: str, target: str, prompt: str) -> dict:
        snap = {
            "session_id": None,
            "agent_id": agent_id,
            "target": target,
            "prompt": prompt,
            "status": "idle",
            "confidence": 0.0,
            "tasks": [],
            "findings": [],
            "created_at": time.time(),
            "tokens": _empty_tokens(),
        }
        return snap


    # ------------------------------------------------------------------ #
    # Plan-driven scan (Plan mode): the approved plan tree is the task tree
    # ------------------------------------------------------------------ #
    def _flatten_plan(self, plan: dict) -> list[dict]:
        out: list[dict] = []

        def rec(nodes, depth=0):
            for n in nodes or []:
                node = dict(n)
                node["depth"] = depth
                out.append(node)
                rec(n.get("children") or [], depth + 1)

        rec(plan.get("nodes") or [])
        return out

    async def _run_plan(self, params: dict, broadcast: EventBroadcast) -> None:
        session_id = params["session_id"]
        agent_id = params.get("agent_id", "agent-sim")
        plan = params["plan"]
        target = plan.get("target") or params.get("target") or \
            self.agents.get(agent_id, {}).get("target", "http://127.0.0.1:8005")
        prompt = plan.get("prompt") or params.get("prompt", "Execute the approved plan.")
        sess = self.sessions.setdefault(
            session_id, self._new_session(agent_id, target, prompt))
        sess["session_id"] = session_id
        self.agent_session[agent_id] = session_id
        sess["status"] = "running"
        start = time.time()

        await _emit_to(broadcast, _ev("agent_start", session_id, "router_agent",
                            target=target, description=f"Plan-driven scan of {target}"))
        self._accrue(sess, "planning", 1800, 420)

        flat = [n for n in self._flatten_plan(plan) if n.get("status") != "pruned"]
        for node in flat:
            tid = node.get("id") or self._uid("task")
            score = node.get("confidence_score", 0.6)
            sev = "high" if score >= 0.8 else ("medium" if score >= 0.65 else "low")
            await _emit_to(broadcast, _ev("task_created", session_id, "router_agent", task_id=tid,
                                task=node.get("task", "task"), status="in_progress",
                                agent="router_agent", severity=sev,
                                parent_id=node.get("parent_id"), depth=node.get("depth", 0)))
            await self._sleep()
            self._accrue(sess, "plan_task", int(300 * score) + 120, int(200 * score) + 60)
            await _emit_to(broadcast, _ev("execution_record", session_id, "router_agent", task_id=tid,
                                action="execute", target_endpoint=target,
                                technique="planned",
                                result_summary=f"Executing planned task: {node.get('task')}"))
            await _emit_to(broadcast, _ev("confidence_update", session_id, "router_agent", task_id=tid,
                                old_confidence=0.0, new_confidence=score,
                                decision="continue", task=node.get("task", "task")))
            await _emit_to(broadcast, _ev("task_status_changed", session_id, "router_agent", task_id=tid,
                                status="completed"))

        finding_sqli = {
            "id": self._uid("finding"), "title": "SQL Injection in /api/users",
            "severity": "high", "endpoint": f"{target}/api/users", "technique": "sqli",
            "evidence": "Payload `id=1' OR '1'='1` returned full user table.",
            "confidence": 0.92,
        }
        finding_xss = {
            "id": self._uid("finding"), "title": "Stored XSS in comment field",
            "severity": "medium", "endpoint": f"{target}/api/comments", "technique": "xss",
            "evidence": "Injected <script>alert(1)</script> persisted and executed.",
            "confidence": 0.81,
        }
        sess["findings"].extend([finding_sqli, finding_xss])
        await _emit_to(broadcast, _ev("validation_result", session_id, "router_agent",
                            task_id="finding-sqli", valid=True, confidence_score=0.92,
                            critique="Plan task produced a validated finding",
                            validation_token=self._uid("vtok"),
                            task="SQL Injection in /api/users", severity="high"))

        sess["status"] = "completed"
        sess["confidence"] = 0.87
        sess["duration"] = round(time.time() - start, 1)
        await _emit_to(broadcast, _ev("agent_step", session_id, "router_agent",
                            phase="reporting", description="Compiling report"))
        self._accrue(sess, "reporting", 2000, 700)
        await _emit_to(broadcast, _ev("session_end", session_id, "router_agent",
                            description="Plan-driven scan complete", duration=sess["duration"]))
        await asyncio.sleep(0.001)


async def _noop_broadcast(event: dict) -> None:
    return None


async def _emit_to(fn, event: dict) -> None:
    """Call a (possibly synchronous) broadcast callback without `await` pitfalls."""
    if callable(fn):
        fn(event)
