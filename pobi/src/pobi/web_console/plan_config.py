"""Persistence + generation for operator-authored engagement plans (Plan mode).

A plan is a tree of task nodes (mirroring the agent's ``Planner.TaskNode``). The
operator can review, prune, edit and approve the tree *before* execution; the
approved plan is what the executor runs. Plans are persisted as JSON under
``<data_dir>/plans`` so they can be reused across engagements.

Node schema::

    {
        "id": "node-...",
        "task": "Reconnaissance",
        "status": "pending",      # pending | approved | pruned
        "confidence_score": 0.6,
        "depth": 0,
        "parent_id": null,
        "children": [ ... ]
    }

Plan schema::

    {
        "plan_id": "plan-...",
        "name": "...",
        "target": "http://...",
        "prompt": "...",
        "created_at": 1234567890.0,
        "updated_at": 1234567890.0,
        "approved": false,
        "nodes": [ ... ]          # list of root nodes
    }
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from .settings import settings

PLANS_DIR = settings.data_dir / "plans"


def _uid(prefix: str) -> str:
    return f"{prefix}-{os.urandom(3).hex()}"


def _ensure_dir() -> None:
    PLANS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Tree helpers
# --------------------------------------------------------------------------- #
def walk(nodes, parent_id: Optional[str] = None, depth: int = 0) -> list[dict]:
    """Flatten a node tree, (re)assigning depth / parent_id / defaults."""
    out: list[dict] = []
    for n in nodes or []:
        node = {
            "id": n.get("id") or _uid("node"),
            "task": n.get("task", "task"),
            "status": n.get("status", "pending"),
            "confidence_score": float(n.get("confidence_score", 0.6)),
            "depth": depth,
            "parent_id": parent_id,
            "children": [],
        }
        out.append(node)
        node["children"] = walk(n.get("children") or [], node["id"], depth + 1)
        # compact: walk already embedded children into node["children"]
    return out


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #
_DEFAULT_TEMPLATE = [
    ("Reconnaissance", 0.70, [
        ("Passive recon (OSINT / DNS)", 0.60, []),
        ("Active recon (probe endpoints)", 0.70, []),
    ]),
    ("Enumeration", 0.70, [
        ("Port & service enumeration", 0.65, []),
        ("Web path / directory brute", 0.70, []),
        ("Tech stack fingerprinting", 0.60, []),
    ]),
    ("Exploitation", 0.80, [
        ("SQL injection", 0.85, []),
        ("Cross-site scripting (XSS)", 0.75, []),
        ("Authentication bypass", 0.70, []),
        ("Insecure deserialization", 0.60, []),
    ]),
    ("Post-exploitation", 0.70, [
        ("Privilege escalation", 0.60, []),
        ("Lateral movement", 0.50, []),
    ]),
    ("Reporting", 0.90, []),
]


def _build_node(task: str, confidence: float, children) -> dict:
    return {
        "id": _uid("node"),
        "task": task,
        "status": "pending",
        "confidence_score": confidence,
        "depth": 0,
        "parent_id": None,
        "children": [_build_node(c, conf, sub) for (c, conf, sub) in children],
    }


def generate_draft(target: str, prompt: str) -> dict:
    """Build a sensible default pentest plan tree for a target / prompt."""
    nodes = [_build_node(task, conf, children) for (task, conf, children) in _DEFAULT_TEMPLATE]
    return {
        "plan_id": _uid("plan"),
        "name": f"Plan for {target or 'target'}",
        "target": target or "",
        "prompt": prompt or "Run a full autonomous penetration test.",
        "created_at": time.time(),
        "updated_at": time.time(),
        "approved": False,
        "nodes": nodes,
    }


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #
def _path(plan_id: str) -> Path:
    safe = "".join(c for c in (plan_id or "") if c.isalnum() or c in "-_")
    return PLANS_DIR / f"{safe}.json"


def list_plans() -> list[dict]:
    _ensure_dir()
    out: list[dict] = []
    for f in sorted(PLANS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        nodes = data.get("nodes") or []
        out.append({
            "plan_id": data.get("plan_id"),
            "name": data.get("name"),
            "target": data.get("target"),
            "approved": bool(data.get("approved", False)),
            "root_count": len(nodes),
            "updated_at": data.get("updated_at"),
        })
    out.sort(key=lambda x: (x.get("updated_at") or 0), reverse=True)
    return out


def get_plan(plan_id: str) -> Optional[dict]:
    p = _path(plan_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_plan(payload: dict) -> dict:
    _ensure_dir()
    plan_id = payload.get("plan_id") or _uid("plan")
    existing = get_plan(plan_id) or {}
    nodes = walk(payload.get("nodes") or existing.get("nodes") or [])
    now = time.time()
    plan = {
        "plan_id": plan_id,
        "name": payload.get("name") or existing.get("name") or "Untitled plan",
        "target": payload.get("target", existing.get("target", "")),
        "prompt": payload.get("prompt", existing.get("prompt", "")),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "approved": bool(payload.get("approved", existing.get("approved", False))),
        "nodes": nodes,
    }
    _path(plan_id).write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan


def delete_plan(plan_id: str) -> dict:
    p = _path(plan_id)
    if p.exists():
        p.unlink()
        return {"deleted": True, "plan_id": plan_id}
    return {"deleted": False, "plan_id": plan_id}


def _mark_approved(nodes) -> None:
    for n in nodes or []:
        if n.get("status") != "pruned":
            n["status"] = "approved"
        _mark_approved(n.get("children") or [])


def approve_plan(plan_id: str) -> dict:
    plan = get_plan(plan_id)
    if plan is None:
        return {"error": "plan not found"}
    plan["approved"] = True
    plan["updated_at"] = time.time()
    # Approving also marks every non-pruned node as approved.
    _mark_approved(plan["nodes"])
    _path(plan_id).write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan
