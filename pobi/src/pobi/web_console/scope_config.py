"""Scope configuration persistence for the POBI Web Console.

Mirrors :mod:`validation_config`: the operator edits the authorization scope in
the UI, we persist it to ``~/.cache/pobi/scope.yaml``. The autonomous agent
reads the very same file and enforces it at its network egress.

Defaults come from :data:`pobi_agent.scope.DEFAULT_SCOPE` so the console and the
agent never drift.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, Dict

from pobi_agent.scope import DEFAULT_PATH, DEFAULT_SCOPE

LIST_KEYS = ("root_domains", "domains", "ips", "out_of_scope")


def load_scope(path: str | None = None) -> Dict[str, Any]:
    """Return the current scope policy merged onto the defaults."""
    from pobi_agent.scope import load_scope_dict

    return load_scope_dict(path)


def _clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = value.replace(",", "\n").split("\n")
    else:
        items = list(value)
    return [str(x).strip() for x in items if str(x).strip()]


def save_scope(cfg: Dict[str, Any], path: str | None = None) -> Dict[str, Any]:
    """Validate, normalize and persist the scope policy. Returns the saved dict."""
    p = Path(path) if path else DEFAULT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)

    data: Dict[str, Any] = {k: DEFAULT_SCOPE[k] for k in DEFAULT_SCOPE}
    cfg = cfg or {}

    for key in LIST_KEYS:
        data[key] = _clean_list(cfg.get(key, DEFAULT_SCOPE[key]))

    try:
        data["max_qps"] = int(cfg.get("max_qps", DEFAULT_SCOPE["max_qps"])) or DEFAULT_SCOPE["max_qps"]
    except (TypeError, ValueError):
        data["max_qps"] = DEFAULT_SCOPE["max_qps"]

    try:
        data["max_bytes"] = int(cfg.get("max_bytes", DEFAULT_SCOPE["max_bytes"])) or DEFAULT_SCOPE["max_bytes"]
    except (TypeError, ValueError):
        data["max_bytes"] = DEFAULT_SCOPE["max_bytes"]

    data["enabled"] = bool(cfg.get("enabled", DEFAULT_SCOPE["enabled"]))

    p.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    data["path"] = str(p)
    return data
