"""FastAPI application for the Pobi Web Console.

Exposes a small REST surface plus an SSE stream over the daemon's
`subscribe_events` feed. All privileged actions are recorded in the audit log.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from . import audit as audit_mod
from .daemon_bridge import DaemonBridge
from .preflight import environment_checks, run_preflight
from .presets import get_presets, get_preset
from .prompts import get_agent_prompt, list_agent_prompts, save_agent_prompt
from .settings import settings
from .simulator import Simulator
from .validation_config import load_validation, save_validation
from .scope_config import load_scope, save_scope, DEFAULT_PATH
from .plan_config import (
    list_plans, get_plan, save_plan, delete_plan, approve_plan, generate_draft,
)

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Pobi Web Console", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bridge = DaemonBridge()
simulator = Simulator()
audit_store = audit_mod.audit_store

# session_id -> agent_id mapping (so the UI can resolve task trees)
session_index: dict[str, str] = {}

# Persisted session snapshots (history that survives restarts). Completed and
# aborted simulation sessions are synced here by a background loop; in daemon
# mode the daemon remains the source of truth but its sessions are merged too.
HISTORY_FILE = settings.data_dir / "sessions.json"
_sessions_store: dict[str, dict] = {}


def _load_sessions() -> None:
    global _sessions_store
    try:
        if HISTORY_FILE.exists():
            _sessions_store = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        _sessions_store = {}


def _save_sessions() -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(_sessions_store, ensure_ascii=False, indent=2),
                                encoding="utf-8")
    except Exception:
        pass


def _all_sessions() -> dict[str, dict]:
    out: dict[str, dict] = dict(_sessions_store)
    for sid, snap in simulator.sessions.items():
        out[sid] = dict(snap)
    return out


def _get_session(sid: str) -> Optional[dict]:
    if sid in simulator.sessions:
        return dict(simulator.sessions[sid])
    return _sessions_store.get(sid)


async def _session_sync_loop() -> None:
    while True:
        try:
            for sid, snap in simulator.sessions.items():
                if snap.get("status") in ("completed", "aborted"):
                    _sessions_store.setdefault(sid, dict(snap))
            _save_sessions()
        except Exception:
            pass
        await asyncio.sleep(5)


def _operator(request: Request) -> str:
    return request.headers.get("x-operator", "web-operator")


# --------------------------------------------------------------------------- #
# Lifecycle
# --------------------------------------------------------------------------- #
@app.on_event("startup")
async def _startup() -> None:
    simulator.broadcast = bridge._broadcast_event
    bridge.simulator = simulator
    _load_sessions()
    asyncio.create_task(_session_sync_loop())

    async def _boot() -> None:
        mode = await bridge.connect()
        await audit_store.add(
            actor="system",
            action="console_start",
            decision=mode,
            detail=f"Web console started in {mode} mode",
        )

    # Connect to the daemon in the background so the HTTP server is ready
    # immediately; `mode` flips to "daemon" once the link is established.
    asyncio.create_task(_boot())


@app.on_event("shutdown")
async def _shutdown() -> None:
    await bridge.shutdown()


# --------------------------------------------------------------------------- #
# Status / health
# --------------------------------------------------------------------------- #
@app.get("/api/status")
async def status():
    return {
        "mode": bridge.mode,
        "connected": bridge.connected,
        "daemon_error": bridge.daemon_error,
        "subscribers": bridge.subscriber_count,
        "approval_mode": simulator.approval_mode if bridge.mode == "simulation"
        else (await _safe_call("get_approval_mode")).get("approval_mode"),
    }


async def _safe_call(method: str, params: Optional[dict] = None) -> Any:
    try:
        return await bridge.call(method, params)
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}


# Map the preflight/health status vocabulary ("ok"/"warn"/"error"/...) onto the
# canonical dashboard vocabulary ("healthy"/"warn"/"error"). Daemon components are
# normalised inline below; environment_checks() reuses preflight's "ok"/"warn"/
# "error" vocabulary and must be normalised here too, otherwise "ok" components
# render as errors and drag overall_success to False.
_HEALTH_STATUS_MAP = {
    "ok": "healthy", "pass": "healthy", "passed": "healthy", "healthy": "healthy",
    "warn": "warn", "warning": "warn",
    "error": "error", "fail": "error", "failed": "error",
}


def _health_status(raw):
    return _HEALTH_STATUS_MAP.get(str(raw).lower() if raw is not None else "", "error")


@app.get("/api/health")
async def health():
    """Component-health view.

    - daemon mode: delegate to the daemon's ComponentManager.health_all (real
      component readiness: python sandbox, shell sandbox, RAG, embedder, ...),
      then MERGE the git-submodule / python-sandbox env checks that the daemon
      does not cover.
    - simulation mode: no daemon is running, so derive health from the same
      preflight env checks that power the Dashboard self-check. This yields
      REAL component status (docker, kali image, LLM, submodule, sandbox, ...)
      instead of the previous empty placeholder.
    """
    if bridge.mode == "daemon":
        result = None
        try:
            result = await bridge.call("health_all")
        except Exception as exc:  # pragma: no cover - daemon down
            logger.warning("health_all unavailable, falling back to preflight: %s", exc)
            result = {"error": str(exc)}
        if isinstance(result, dict) and result.get("error"):
            pf = await asyncio.to_thread(run_preflight)
            return {
                "mode": "daemon",
                "components": pf["checks"],
                "overall_success": pf["can_scan"],
                "checked_at": datetime.now().isoformat(),
                "note": "health_all unavailable; showing preflight env checks",
            }
        comps = [
            {
                "id": (c.get("component") or c.get("id") or "unknown"),
                "label": (c.get("component") or c.get("id") or "unknown").replace("_", " ").title(),
                "status": "healthy" if c.get("healthy") else ("error" if c.get("status") == "error" else "warn"),
                "detail": c.get("message", "") or "",
                "actions": [],
            }
            for c in (result.get("components") or [])
        ]
        try:
            for ec in environment_checks():
                ec = dict(ec)
                ec["status"] = _health_status(ec.get("status"))
                comps.append(ec)
        except Exception as exc:  # pragma: no cover
            logger.warning("environment_checks failed: %s", exc)
        return {
            "mode": "daemon",
            "components": comps,
            "overall_success": all(c["status"] == "healthy" for c in comps),
            "checked_at": datetime.now().isoformat(),
        }
    pf = await asyncio.to_thread(run_preflight)
    return {
        "mode": "simulation",
        "components": pf["checks"],
        "overall_success": pf["can_scan"],
        "checked_at": datetime.now().isoformat(),
    }


# --------------------------------------------------------------------------- #
# Preflight — environment self-check and one-click installers
# --------------------------------------------------------------------------- #
@app.get("/api/preflight")
async def preflight():
    return await asyncio.to_thread(run_preflight)


@app.post("/api/preflight/pull-kali")
async def preflight_pull_kali(request: Request):
    from .preflight import pull_kali_image
    result = await asyncio.to_thread(pull_kali_image)
    await audit_store.add(actor=_operator(request), action="pull_kali",
                          decision="ok" if result.get("ok") else "failed",
                          detail=result.get("detail", ""))
    return result


@app.post("/api/preflight/install-playwright")
async def preflight_install_playwright(request: Request):
    from .preflight import install_playwright_chromium
    result = await asyncio.to_thread(install_playwright_chromium)
    await audit_store.add(actor=_operator(request), action="install_playwright",
                          decision="ok" if result.get("ok") else "failed",
                          detail=result.get("detail", ""))
    return result


@app.post("/api/llm/test")
async def test_llm(request: Request, payload: dict):
    provider = payload.get("provider")
    model_name = payload.get("model_name")
    # Embedding models can't answer a chat completion, so route them to the
    # embedding connectivity probe (which also reports the vector dimension).
    if payload.get("type_model") == "embeddings":
        from .preflight import test_embedding_connectivity
        result = await asyncio.to_thread(
            test_embedding_connectivity,
            provider=provider,
            model_name=model_name,
            api_key=payload.get("api_key"),
            base_url=payload.get("base_url"),
        )
    else:
        from .preflight import test_llm_connectivity
        result = await asyncio.to_thread(
            test_llm_connectivity,
            provider=provider,
            model_name=model_name,
            api_key=payload.get("api_key"),
            base_url=payload.get("base_url"),
        )
    # Redact key from audit log — never write it.
    await audit_store.add(
        actor=_operator(request), action="test_llm",
        decision="ok" if result.get("ok") else "failed",
        detail=f"provider={provider} model={model_name} type={payload.get('type_model', 'llm')} "
               f"result={result.get('error_type', 'ok')}",
    )
    return result


@app.post("/api/init")
async def init_all(request: Request):
    result = await _safe_call("init_all")
    await audit_store.add(actor=_operator(request), action="init_components", detail="Initialized all components")
    return result


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
@app.get("/api/models")
async def models():
    return await _safe_call("get_all_models")


@app.get("/api/validation")
async def get_validation():
    return await _safe_call("get_validation_config")


@app.post("/api/validation")
async def set_validation(request: Request, payload: dict):
    result = await _safe_call("set_validation_config", payload)
    await audit_store.add(actor=_operator(request), action="set_validation_config",
                          detail=json.dumps(payload, ensure_ascii=False))
    return result


@app.get("/api/llm")
async def get_llm():
    return await _safe_call("get_llm_provider")


@app.get("/api/llm/list")
async def list_llm():
    """All configured providers (api_key redacted) for the settings page.

    Returns: {current: str, providers: [{provider, model_name, base_url, has_key}, ...]}
    """
    return await _safe_call("list_llm_providers")


@app.post("/api/llm")
async def set_llm(request: Request, payload: dict):
    # Always route through `add_model` — the daemon reuses the previously-saved
    # api_key / base_url when the caller omits them, so a "just switch active
    # provider" click still works. Errors are propagated so the UI can show them
    # instead of silently pretending the save succeeded.
    provider = payload.get("provider")
    model_name = payload.get("model_name")
    if not provider or not model_name:
        raise HTTPException(status_code=400, detail="provider and model_name are required")
    try:
        result = await bridge.call("add_model", {
            "provider": provider,
            "model_name": model_name,
            "api_key": payload.get("api_key"),
            "base_url": payload.get("base_url"),
            "type_model": payload.get("type_model"),
            "vec_dim": payload.get("vec_dim"),
        })
    except Exception as exc:
        # Audit the failure too — operators want to see why saves fail.
        await audit_store.add(actor=_operator(request), action="set_llm_provider",
                              decision="failed", detail=f"provider={provider} model={model_name} err={exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    # Redact secrets from audit trail.
    audit_detail = json.dumps(
        {k: v for k, v in payload.items() if k not in ("api_key",)},
        ensure_ascii=False,
    )
    await audit_store.add(actor=_operator(request), action="set_llm_provider",
                          detail=audit_detail)
    return result


@app.delete("/api/llm")
async def delete_llm(request: Request, provider: str, model_name: str):
    """Remove a configured model provider from config.json."""
    if not provider or not model_name:
        raise HTTPException(status_code=400, detail="provider and model_name are required")
    try:
        result = await bridge.call("delete_model", {
            "provider": provider,
            "model_name": model_name,
        })
    except Exception as exc:
        await audit_store.add(actor=_operator(request), action="delete_llm_provider",
                              decision="failed", detail=f"provider={provider} model={model_name} err={exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    await audit_store.add(actor=_operator(request), action="delete_llm_provider",
                          detail=f"provider={provider} model={model_name}")
    return result


@app.get("/api/approval-mode")
async def get_approval():
    if bridge.mode == "simulation":
        return {"approval_mode": simulator.approval_mode}
    return await _safe_call("get_approval_mode")


@app.post("/api/approval-mode")
async def set_approval(request: Request, payload: dict):
    enabled = bool(payload.get("enabled", False))
    method = "enable_approval_mode" if enabled else "disable_approval_mode"
    if bridge.mode == "simulation":
        simulator.approval_mode = enabled
        result = {"approval_mode": enabled}
    else:
        result = await _safe_call(method)
    await audit_store.add(actor=_operator(request), action="set_approval_mode",
                          decision="enabled" if enabled else "disabled")
    return result


# --------------------------------------------------------------------------- #
# Presets & agents
# --------------------------------------------------------------------------- #
@app.get("/api/presets")
async def presets():
    return get_presets()


@app.get("/api/agents/available")
async def available_agents():
    """Agent roster for the New Scan strategy picker.

    Mirrors the roster the daemon uses when instantiating an agent (shell is
    dropped when Docker/Kali are unavailable).
    """
    return await _safe_call("get_available_agents")


@app.post("/api/agents")
async def create_agent(request: Request, payload: dict):
    result = await _safe_call("instantiate_agent", payload)
    target = payload.get("target")
    await audit_store.add(actor=_operator(request), action="instantiate_agent",
                          target=target, detail=json.dumps(payload, ensure_ascii=False))
    return result


@app.get("/api/agents/{agent_id}/tasks")
async def agent_tasks(agent_id: str):
    return await _safe_call("get_agent_tasks", {"agent_id": agent_id})


# --------------------------------------------------------------------------- #
# Agent prompt templates (view / edit)
# --------------------------------------------------------------------------- #
@app.get("/api/agents/templates")
async def list_agent_templates():
    return {"agents": list_agent_prompts()}


@app.get("/api/agents/templates/{name}")
async def get_agent_template(name: str):
    try:
        return get_agent_prompt(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"agent prompt '{name}' not found")


@app.put("/api/agents/templates/{name}")
async def put_agent_template(name: str, request: Request, payload: dict):
    content = payload.get("content", "")
    res = save_agent_prompt(name, content)
    await audit_store.add(
        actor=_operator(request),
        action="edit_agent_prompt",
        target=name,
        detail=res.get("path"),
    )
    return res


# --------------------------------------------------------------------------- #
# Validation strategy config (sync to backend YAML)
# --------------------------------------------------------------------------- #
@app.get("/api/validation-config")
async def get_validation_config_api():
    return load_validation()


@app.post("/api/validation-config")
async def post_validation_config_api(request: Request, payload: dict):
    res = save_validation(payload)
    await audit_store.add(
        actor=_operator(request),
        action="edit_validation_config",
        detail=res.get("path"),
    )
    return res


# --------------------------------------------------------------------------- #
# Authorization scope config (sync to backend YAML, enforced by the agent)
# --------------------------------------------------------------------------- #
@app.get("/api/scope-config")
async def get_scope_config_api():
    return load_scope()


@app.post("/api/scope-config")
async def post_scope_config_api(request: Request, payload: dict):
    res = save_scope(payload)
    await audit_store.add(
        actor=_operator(request),
        action="edit_scope_config",
        detail=str(DEFAULT_PATH),
    )
    return res


@app.post("/api/scope-config/test")
async def test_scope_config_api(request: Request, payload: dict):
    from pobi_agent.scope import ScopePolicy

    target = payload.get("target", "")
    allowed, reason = ScopePolicy(payload).is_allowed(target)
    return {"target": target, "allowed": bool(allowed), "reason": reason}


# --------------------------------------------------------------------------- #
# Engagement plans (Plan mode)
# --------------------------------------------------------------------------- #
@app.get("/api/plans")
async def list_plans_api():
    return list_plans()


@app.post("/api/plans")
async def save_plan_api(request: Request, payload: dict):
    res = save_plan(payload)
    await audit_store.add(
        actor=_operator(request),
        action="edit_plan",
        target=res.get("plan_id"),
        detail=res.get("name"),
    )
    return res


@app.get("/api/plans/{plan_id}")
async def get_plan_api(plan_id: str):
    plan = get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"plan '{plan_id}' not found")
    return plan


@app.delete("/api/plans/{plan_id}")
async def delete_plan_api(request: Request, plan_id: str):
    res = delete_plan(plan_id)
    await audit_store.add(actor=_operator(request), action="delete_plan", target=plan_id)
    return res


@app.post("/api/plans/generate")
async def generate_plan_api(request: Request, payload: dict):
    target = payload.get("target", "")
    prompt = payload.get("prompt", "")
    return generate_draft(target, prompt)


@app.post("/api/plans/{plan_id}/approve")
async def approve_plan_api(request: Request, plan_id: str):
    res = approve_plan(plan_id)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=404, detail=res["error"])
    await audit_store.add(actor=_operator(request), action="approve_plan", target=plan_id)
    return res


# --------------------------------------------------------------------------- #
# Scans
# --------------------------------------------------------------------------- #
@app.post("/api/agents/{agent_id}/embed")
async def embed(request: Request, agent_id: str, payload: dict):
    params = {"agent_id": agent_id, **payload}
    # Await embedding so the scan never starts against an un-embedded target.
    # (The original deadend-cli awaits embedTarget before running the scan.)
    await bridge.embed_target(params)
    await audit_store.add(actor=_operator(request), action="embed_target",
                          target=payload.get("target"), detail=agent_id)
    return {"accepted": True}


@app.post("/api/scans")
async def start_scan(request: Request, payload: dict):
    agent_id = payload.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id required")
    session_id = payload.get("session_id") or f"session-{os.urandom(4).hex()}"
    session_index[session_id] = agent_id
    params = {
        "agent_id": agent_id,
        "session_id": session_id,
        "prompt": payload.get("prompt", "Run a full autonomous penetration test."),
        "max_depth": payload.get("max_depth", 5),
        "validation_config": payload.get("validation_config"),
        "target": payload.get("target"),
    }
    plan_id = payload.get("plan_id")
    if plan_id:
        plan = get_plan(plan_id)
        if plan is None:
            raise HTTPException(status_code=400, detail=f"plan '{plan_id}' not found")
        params["plan_id"] = plan_id
        params["plan"] = plan
    sid = await bridge.start_scan(params)
    await audit_store.add(actor=_operator(request), action="start_scan",
                          target=payload.get("target"),
                          decision="launched",
                          detail=f"agent={agent_id} session={sid}",
                          request_id=sid)
    return {"session_id": sid, "agent_id": agent_id}


@app.get("/api/sessions")
async def list_sessions():
    if bridge.mode == "daemon":
        res = await _safe_call("list_sessions", {})
        if isinstance(res, dict) and "sessions" in res:
            return res["sessions"]
    sessions = _all_sessions()
    out = []
    for sid, snap in sessions.items():
        snap = dict(snap)
        snap["session_id"] = snap.get("session_id") or sid
        tok = snap.get("tokens") or {}
        out.append({
            "session_id": snap["session_id"],
            "agent_id": snap.get("agent_id"),
            "target": snap.get("target"),
            "status": snap.get("status"),
            "prompt": snap.get("prompt"),
            "confidence": snap.get("confidence"),
            "findings": len(snap.get("findings") or []),
            "duration": snap.get("duration"),
            "created_at": snap.get("created_at"),
            "total_tokens": tok.get("total_tokens", 0),
            "cost_usd": tok.get("cost_usd", 0.0),
        })
    out.sort(key=lambda x: (x.get("created_at") or 0), reverse=True)
    return out


@app.get("/api/sessions/{session_id}")
async def session_info(session_id: str):
    agent_id = session_index.get(session_id)
    if bridge.mode == "simulation":
        if session_id in simulator.sessions:
            snap = dict(simulator.sessions[session_id])
            snap["session_id"] = session_id
            return snap
        if session_id in _sessions_store:
            return _sessions_store[session_id]
    else:
        res = await _safe_call("get_session", {"session_id": session_id})
        if isinstance(res, dict) and "error" not in res and res:
            return res
    return {"session_id": session_id, "agent_id": agent_id, "status": "unknown"}


@app.get("/api/sessions/{session_id}/tokens")
async def session_tokens(session_id: str):
    snap = _get_session(session_id)
    if snap is None:
        if bridge.mode == "daemon":
            res = await _safe_call("get_token_usage", {"session_id": session_id})
            if isinstance(res, dict) and "error" not in res and res:
                return res
        raise HTTPException(status_code=404, detail="session not found")
    return snap.get("tokens") or {"prompt_tokens": 0, "completion_tokens": 0,
                                  "total_tokens": 0, "cost_usd": 0.0, "by_phase": {}}


@app.get("/api/tokens")
async def token_aggregate():
    sessions = _all_sessions()
    total_prompt = total_completion = total_tokens = 0
    total_cost = 0.0
    by_phase: dict[str, dict] = {}
    per_session = []
    for snap in sessions.values():
        tok = snap.get("tokens") or {}
        p = tok.get("prompt_tokens", 0)
        c = tok.get("completion_tokens", 0)
        tt = tok.get("total_tokens", p + c)
        cost = tok.get("cost_usd", 0.0)
        total_prompt += p
        total_completion += c
        total_tokens += tt
        total_cost += cost
        for ph, pd in (tok.get("by_phase") or {}).items():
            agg = by_phase.setdefault(ph, {"prompt_tokens": 0, "completion_tokens": 0,
                                           "total_tokens": 0, "cost_usd": 0.0})
            agg["prompt_tokens"] += pd.get("prompt_tokens", 0)
            agg["completion_tokens"] += pd.get("completion_tokens", 0)
            agg["total_tokens"] += pd.get("total_tokens", 0)
            agg["cost_usd"] = round(agg["cost_usd"] + pd.get("cost_usd", 0.0), 4)
        per_session.append({
            "session_id": snap.get("session_id"),
            "target": snap.get("target"),
            "total_tokens": tt,
            "cost_usd": cost,
        })
    per_session.sort(key=lambda x: x["total_tokens"], reverse=True)
    return {
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 4),
        "by_phase": by_phase,
        "per_session": per_session,
    }


def _build_report(snap: dict) -> dict:
    findings = snap.get("findings") or []
    tok = snap.get("tokens") or {}
    return {
        "session_id": snap.get("session_id"),
        "agent_id": snap.get("agent_id"),
        "target": snap.get("target"),
        "status": snap.get("status"),
        "prompt": snap.get("prompt"),
        "confidence": snap.get("confidence"),
        "duration": snap.get("duration"),
        "created_at": snap.get("created_at"),
        "findings": findings,
        "tokens": tok,
        "generated_at": time.time(),
    }


def _build_markdown_report(snap: dict) -> str:
    r = _build_report(snap)
    lines = []
    lines.append("# Pobi Security Assessment Report")
    lines.append("")
    lines.append(f"- **Target:** {r['target']}")
    lines.append(f"- **Session:** `{r['session_id']}`")
    lines.append(f"- **Status:** {r['status']}")
    lines.append(f"- **Confidence:** {r['confidence']}")
    lines.append(f"- **Duration:** {r['duration']}s")
    lines.append(f"- **Prompt:** {r['prompt']}")
    tok = r["tokens"]
    lines.append(f"- **Tokens used:** {tok.get('total_tokens', 0)} (est. ${tok.get('cost_usd', 0):.2f})")
    lines.append("")
    lines.append("## Findings")
    if not r["findings"]:
        lines.append("_No validated findings._")
    else:
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        for f in sorted(r["findings"], key=lambda x: sev_order.get((x.get("severity") or "low").lower(), 9)):
            lines.append(f"### [{f.get('severity', '').upper()}] {f.get('title')}")
            lines.append(f"- **Endpoint:** {f.get('endpoint')}")
            lines.append(f"- **Confidence:** {f.get('confidence')}")
            lines.append(f"- **Evidence:** {f.get('evidence')}")
            lines.append("")
    lines.append("## Token usage by phase")
    for ph, pd in (tok.get("by_phase") or {}).items():
        lines.append(f"- {ph}: {pd.get('total_tokens', 0)} tokens (${pd.get('cost_usd', 0):.2f})")
    lines.append("")
    lines.append(f"_Generated at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r['generated_at']))}_")
    return "\n".join(lines)


@app.get("/api/sessions/{session_id}/report")
async def report_json(session_id: str):
    snap = _get_session(session_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="session not found")
    return _build_report(snap)


@app.get("/api/sessions/{session_id}/report/download")
async def report_download(session_id: str, format: str = "markdown"):
    snap = _get_session(session_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="session not found")
    sid = snap.get("session_id") or session_id
    if format == "json":
        content = json.dumps(_build_report(snap), ensure_ascii=False, indent=2)
        media = "application/json"
        ext = "json"
    else:
        content = _build_markdown_report(snap)
        media = "text/markdown"
        ext = "md"
    headers = {"Content-Disposition": f'attachment; filename="pobi-report-{sid}.{ext}"'}
    return Response(content=content, media_type=media, headers=headers)


@app.post("/api/scans/{session_id}/interrupt")
async def interrupt(request: Request, session_id: str, payload: dict | None = None):
    reason = (payload or {}).get("reason", "interrupted by operator")
    if bridge.mode == "simulation":
        await simulator.interrupt(session_id)
        result = {"interrupted": True}
    else:
        result = await _safe_call("interrupt", {"session_id": session_id, "reason": reason})
    await audit_store.add(actor=_operator(request), action="interrupt_scan",
                          target=session_id, detail=reason)
    return result


@app.post("/api/approve")
async def approve(request: Request, payload: dict):
    request_id = payload.get("request_id")
    approved = bool(payload.get("approved", False))
    if bridge.mode == "simulation":
        simulator.pending_approvals[request_id] = approved
        result = {"request_id": request_id, "approved": approved}
    else:
        result = await _safe_call("approve", {"request_id": request_id, "approved": approved})
    await audit_store.add(actor=_operator(request), action="approval_decision",
                          decision="granted" if approved else "denied",
                          request_id=request_id)
    return result


# --------------------------------------------------------------------------- #
# Audit
# --------------------------------------------------------------------------- #
@app.get("/api/audit")
async def list_audit(limit: int = 100, offset: int = 0, action: Optional[str] = None):
    return await audit_store.list(limit=limit, offset=offset, action=action)


@app.post("/api/audit")
async def add_audit(request: Request, payload: dict):
    return await audit_store.add(
        actor=payload.get("actor", _operator(request)),
        action=payload.get("action", "manual"),
        target=payload.get("target"),
        decision=payload.get("decision"),
        detail=payload.get("detail"),
        request_id=payload.get("request_id"),
    )


# --------------------------------------------------------------------------- #
# Event stream (SSE)
# --------------------------------------------------------------------------- #
@app.get("/api/events")
async def events(request: Request):
    queue: asyncio.Queue = asyncio.Queue(maxsize=500)

    async def gen():
        bridge.add_subscriber(queue)
        try:
            yield {"event": "ready", "data": json.dumps({
                "mode": bridge.mode,
                "connected": bridge.connected,
                "subscribers": bridge.subscriber_count,
            })}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
                    continue
                yield {"event": "message", "data": json.dumps(event, ensure_ascii=False)}
        finally:
            bridge.remove_subscriber(queue)

    return EventSourceResponse(gen())


# --------------------------------------------------------------------------- #
# Static frontend
# --------------------------------------------------------------------------- #
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})
