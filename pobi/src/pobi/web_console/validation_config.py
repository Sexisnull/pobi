"""Read / write the YAML-driven validation strategy config.

The pobi agent loads ``~/.cache/pobi/validation.yaml`` at scan time, so writing
this file from the web console effectively "syncs" the strategy config to the
backend. Works in both daemon and simulation modes.
"""
from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_PATH = Path.home() / ".cache" / "pobi" / "validation.yaml"

DEFAULT_CONFIG = {
    "strategies": [
        {"name": "flag"},
        {"name": "judge"},
    ],
    "validation_format": None,
    "validation_type": None,
}


def load_validation(path=None) -> dict:
    p = Path(path) if path else DEFAULT_PATH
    base = {k: v for k, v in DEFAULT_CONFIG.items()}
    if p.exists():
        try:
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            if isinstance(raw, dict):
                for k in ("strategies", "validation_format", "validation_type"):
                    if k in raw:
                        base[k] = raw[k]
        except Exception:
            pass
    if not isinstance(base.get("strategies"), list) or not base["strategies"]:
        base["strategies"] = list(DEFAULT_CONFIG["strategies"])
    return base


def save_validation(cfg: dict, path=None) -> dict:
    p = Path(path) if path else DEFAULT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    clean = {
        "strategies": cfg.get("strategies", DEFAULT_CONFIG["strategies"]),
        "validation_format": cfg.get("validation_format"),
        "validation_type": cfg.get("validation_type"),
    }
    p.write_text(
        yaml.safe_dump(clean, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return {"ok": True, "path": str(p)}
