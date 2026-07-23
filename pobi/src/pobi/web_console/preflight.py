# Copyright (C) 2025 Yassine Bargach
# Licensed under the GNU Affero General Public License v3
# See LICENSE file for full license information.

"""Preflight self-check for the Pobi Web Console.

Every check is pure and side-effect-free until the operator explicitly
calls one of the ``pull_*`` / ``install_*`` helpers. This is what powers
the Dashboard "Environment preflight" card and the LLM "Test connection"
button.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


KALI_IMAGE = "xoxruns/sandboxed_kali"
VALIDATION_YAML = Path.home() / ".cache" / "pobi" / "validation.yaml"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _ok(check_id: str, label: str, detail: str, actions: list | None = None) -> dict:
    return {"id": check_id, "label": label, "status": "ok", "detail": detail, "actions": actions or []}


def _warn(check_id: str, label: str, detail: str, impact: str, actions: list | None = None) -> dict:
    return {
        "id": check_id, "label": label, "status": "warn",
        "detail": detail, "impact": impact, "actions": actions or [],
    }


def _err(check_id: str, label: str, detail: str, impact: str, actions: list | None = None) -> dict:
    return {
        "id": check_id, "label": label, "status": "error",
        "detail": detail, "impact": impact, "actions": actions or [],
    }


def _repo_root() -> Path:
    """Walk up from this file to find the git repo root (a dir holding .gitmodules/.git)."""
    cur = Path(__file__).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / ".gitmodules").exists() or (parent / ".git").exists():
            return parent
    # Fallback: two levels up from web_console -> pobi package -> repo root.
    return Path(__file__).resolve().parents[3]


def _dir_nonempty(p: Path) -> bool:
    try:
        return p.exists() and p.is_dir() and any(True for _ in p.iterdir())
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_python() -> dict:
    v = sys.version_info
    detail = f"{v.major}.{v.minor}.{v.micro} ({platform.machine()})"
    if (v.major, v.minor) < (3, 10):
        return _err(
            "python", "Python", detail,
            impact="Pobi requires Python 3.10+.",
            actions=[{"kind": "link", "href": "https://docs.python.org/3/", "label": "Install Python 3.11+"}],
        )
    return _ok("python", "Python", detail)


def _check_playwright() -> dict:
    if importlib.util.find_spec("playwright") is None:
        return _warn(
            "playwright", "Playwright", "package not installed",
            impact="HTTP recon (requester / webapp_analyzer / authenticator) will not work.",
            actions=[
                {"kind": "api", "method": "POST", "path": "/api/preflight/install-playwright",
                 "label": "Install Playwright + chromium"},
            ],
        )
    # Chromium bundled binary check — cheap heuristic via env / cache dir.
    cache = os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or str(Path.home() / "Library/Caches/ms-playwright")
    has_chromium = False
    try:
        p = Path(cache)
        if p.exists():
            has_chromium = any(d.name.startswith("chromium") for d in p.iterdir())
    except OSError:
        has_chromium = False
    if not has_chromium:
        # Try Linux/Windows default too.
        for alt in (Path.home() / ".cache/ms-playwright",
                    Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"):
            try:
                if alt.exists() and any(d.name.startswith("chromium") for d in alt.iterdir()):
                    has_chromium = True
                    break
            except OSError:
                continue
    if not has_chromium:
        return _warn(
            "playwright", "Playwright", "package installed, chromium browser missing",
            impact="Recon agents will fail on first HTTP call.",
            actions=[
                {"kind": "api", "method": "POST", "path": "/api/preflight/install-playwright",
                 "label": "Install chromium"},
            ],
        )
    return _ok("playwright", "Playwright", "chromium installed")


def _check_docker() -> dict:
    try:
        import docker
    except ImportError:
        return _warn(
            "docker", "Docker daemon", "docker-py not installed",
            impact="Shell agent (nmap/sqlmap/curl in Kali) unavailable.",
        )
    try:
        client = docker.from_env()
        client.ping()
        info = client.version()
        return _ok("docker", "Docker daemon", f"connected ({info.get('Version', 'unknown')})")
    except Exception as exc:  # docker.errors.DockerException, ConnectionError, etc.
        return _warn(
            "docker", "Docker daemon", f"not reachable: {type(exc).__name__}",
            impact="Shell agent (nmap/sqlmap/curl in Kali) unavailable. HTTP-layer scans still work.",
            actions=[
                {"kind": "link", "href": "https://docs.docker.com/get-docker/",
                 "label": "Install Docker"},
            ],
        )


def _check_kali_image() -> dict:
    try:
        import docker
        client = docker.from_env()
        client.ping()
    except Exception:
        return _warn(
            "kali_image", "Kali sandbox image", "docker unavailable",
            impact="Cannot check or pull the sandbox image without Docker.",
        )
    try:
        client.images.get(KALI_IMAGE)
        return _ok("kali_image", "Kali sandbox image", f"{KALI_IMAGE} present")
    except Exception:
        return _warn(
            "kali_image", "Kali sandbox image", f"{KALI_IMAGE} not pulled",
            impact="Shell agent will fail on sandbox creation.",
            actions=[
                {"kind": "api", "method": "POST", "path": "/api/preflight/pull-kali",
                 "label": "Pull Kali image (~500MB)"},
            ],
        )


def _check_llm() -> dict:
    """LLM is the only preflight item that blocks scanning entirely."""
    try:
        from pobi_agent import config_setup
        from pobi_agent.config.settings import EmbeddingSpec, ModelSpec
    except Exception as exc:
        return _err(
            "llm", "LLM provider", f"cannot read config: {type(exc).__name__}",
            impact="Scanning requires an LLM.",
            actions=[{"kind": "route", "hash": "#settings", "label": "Configure LLM"}],
        )
    try:
        config = config_setup()
        providers = getattr(config, "model_providers", []) or []
        # EmbeddingSpec subclasses ModelSpec — use type() not isinstance().
        llm_specs = [p for p in providers if type(p) is ModelSpec]
    except Exception as exc:
        return _err(
            "llm", "LLM provider", f"config error: {type(exc).__name__}: {exc}"[:200],
            impact="Scanning requires an LLM.",
            actions=[{"kind": "route", "hash": "#settings", "label": "Configure LLM"}],
        )
    if not llm_specs:
        return _err(
            "llm", "LLM provider", "no provider configured",
            impact="Scanning requires an LLM.",
            actions=[{"kind": "route", "hash": "#settings", "label": "Configure LLM"}],
        )
    first = llm_specs[0]
    detail = f"{first.provider} / {first.model_name}"
    return _ok(
        "llm", "LLM provider", detail,
        actions=[
            {"kind": "route", "hash": "#settings", "label": "Manage LLM"},
        ],
    )


def _check_validation() -> dict:
    if VALIDATION_YAML.exists():
        return _ok("validation", "Validation config", str(VALIDATION_YAML))
    return _warn(
        "validation", "Validation config",
        "no ~/.cache/pobi/validation.yaml",
        impact="Defaults to FLAG{} regex — for non-CTF targets create judge-only config.",
        actions=[{"kind": "route", "hash": "#settings", "label": "Open Settings"}],
    )


# ---------------------------------------------------------------------------
# Git submodules / Python sandbox (uv workspace member)
# ---------------------------------------------------------------------------

def _submodule_paths(root: Path) -> list[tuple[str | None, Path]]:
    """Parse .gitmodules into [(submodule_name, absolute_path), ...]."""
    gm = root / ".gitmodules"
    if not gm.exists():
        return []
    out: list[tuple[str | None, Path]] = []
    name: str | None = None
    try:
        for line in gm.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("[submodule"):
                m = re.search(r'"([^"]+)"', s)
                name = m.group(1) if m else None
            elif s.startswith("path") and "=" in s:
                out.append((name, root / s.split("=", 1)[1].strip()))
    except OSError:
        return []
    return out


def _check_python_sandbox() -> dict:
    """The simple-python-interpreter-sandbox submodule is where the agent runs
    untrusted Python. It is also a uv workspace member — if it is missing,
    `uv run` itself fails to start, so this is effectively required."""
    root = _repo_root()
    cand = [
        (n, p) for n, p in _submodule_paths(root)
        if "simple-python-interpreter-sandbox" in (n or "") or "simple-python-interpreter-sandbox" in str(p)
    ]
    target = cand[0][1] if cand else (root / "simple-python-interpreter-sandbox")
    rel = target.relative_to(root) if target.is_relative_to(root) else target
    if _dir_nonempty(target):
        return _ok("python_sandbox_submodule", "Python sandbox (submodule)", f"{rel} present and populated")
    cmd = f"cd {root} && git submodule update --init --recursive"
    return _err(
        "python_sandbox_submodule", "Python sandbox (submodule)",
        f"{rel} not found or empty. The agent executes untrusted Python here; "
        "it is a uv workspace member, so `uv run` fails without it. Fix: " + cmd,
        impact="Scans that execute Python payloads cannot run until the sandbox submodule is initialized.",
        actions=[{"kind": "route", "hash": "#settings", "label": "Open Settings"}],
    )


def _check_submodules() -> dict:
    """Verify every declared git submodule is checked out and non-empty."""
    root = _repo_root()
    subs = _submodule_paths(root)
    if not subs:
        gm = root / ".gitmodules"
        if not gm.exists():
            return _ok("submodules", "Git submodules", "no submodules declared in this repository")
        return _ok("submodules", "Git submodules", "no submodule paths declared")
    rel_paths = [str(p.relative_to(root) if p.is_relative_to(root) else p) for _, p in subs]
    missing = [str(p.relative_to(root) if p.is_relative_to(root) else p) for _, p in subs if not _dir_nonempty(p)]
    if not missing:
        return _ok("submodules", "Git submodules", f"all {len(rel_paths)} submodules initialized")
    critical = [p for p in missing if "simple-python-interpreter-sandbox" in p]
    cmd = f"cd {root} && git submodule update --init --recursive"
    status = "error" if critical else "warn"
    label = "Git submodules"
    detail = ("Missing required submodule(s): " if critical else "Some submodules not initialized: ") \
             + ", ".join(missing) + f". Fix: {cmd}"
    impact = ("uv will fail to start without the sandbox submodule." if critical
              else "Optional submodules (e.g. benchmarks) are missing; core scanning is unaffected.")
    return {
        "id": "submodules", "label": label, "status": status,
        "detail": detail, "impact": impact,
        "actions": [{"kind": "route", "hash": "#settings", "label": "Open Settings"}],
    }


def environment_checks() -> list[dict]:
    """Lightweight environment-only checks (submodules / python sandbox) for the
    component-health view. The daemon's ComponentManager does not cover these."""
    return [_check_python_sandbox(), _check_submodules()]


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def run_preflight() -> dict:
    checks = [
        _check_python(),
        _check_python_sandbox(),
        _check_submodules(),
        _check_playwright(),
        _check_docker(),
        _check_kali_image(),
        _check_llm(),
        _check_validation(),
    ]
    def _status(cid: str) -> str:
        for c in checks:
            if c["id"] == cid:
                return c["status"]
        return "error"

    return {
        "checks": checks,
        "can_scan": all(c["status"] != "error" for c in checks),
        "capabilities": {
            "http_layer": _status("playwright") == "ok",
            "shell_tools": _status("docker") == "ok" and _status("kali_image") == "ok",
            "wasm_python": True,
        },
    }


# ---------------------------------------------------------------------------
# Actions — mutating helpers called by /api/preflight/* endpoints
# ---------------------------------------------------------------------------

def pull_kali_image() -> dict:
    """Pull the sandbox image. Blocks until done; returns summary."""
    try:
        import docker
    except ImportError as exc:
        return {"ok": False, "error_type": "missing_dep", "detail": str(exc)}
    try:
        client = docker.from_env()
    except Exception as exc:
        return {"ok": False, "error_type": "docker_unreachable", "detail": str(exc)[:400]}

    start = time.monotonic()
    try:
        client.images.pull(KALI_IMAGE)
        return {
            "ok": True,
            "detail": f"pulled {KALI_IMAGE}",
            "elapsed_seconds": round(time.monotonic() - start, 1),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:400],
            "elapsed_seconds": round(time.monotonic() - start, 1),
        }


def install_playwright_chromium() -> dict:
    """Best-effort install of playwright + chromium.

    First installs the Python package if missing, then runs
    ``playwright install chromium``. Blocking; can take a minute.
    """
    if importlib.util.find_spec("playwright") is None:
        pip_cmd = [sys.executable, "-m", "pip", "install", "playwright"]
        try:
            subprocess.run(pip_cmd, check=True, capture_output=True, timeout=180)
        except subprocess.CalledProcessError as exc:
            return {"ok": False, "error_type": "pip_failed",
                    "detail": (exc.stderr or b"").decode(errors="ignore")[:400]}
        except Exception as exc:
            return {"ok": False, "error_type": type(exc).__name__, "detail": str(exc)[:400]}

    pw_cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    try:
        proc = subprocess.run(pw_cmd, capture_output=True, timeout=600)
        if proc.returncode != 0:
            return {"ok": False, "error_type": "playwright_install_failed",
                    "detail": (proc.stderr or b"").decode(errors="ignore")[:400]}
        return {"ok": True, "detail": "chromium installed"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error_type": "timeout", "detail": "playwright install > 10min"}
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__, "detail": str(exc)[:400]}


def test_llm_connectivity(
    provider: str | None,
    model_name: str | None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict:
    """Send a minimal completion request to verify the LLM is reachable.

    ``api_key`` / ``base_url`` are optional overrides — if omitted, the
    saved config values apply (via ``config_setup()``).
    """
    if not provider or not model_name:
        return {"ok": False, "error_type": "missing_input",
                "detail": "provider and model_name required"}

    # Fall back to saved credentials when the caller left them blank.
    if not api_key or not base_url:
        try:
            from pobi_agent import config_setup
            from pobi_agent.config.settings import ModelSpec
            cfg = config_setup()
            for spec in getattr(cfg, "model_providers", []) or []:
                if type(spec) is ModelSpec and spec.provider == provider and spec.model_name == model_name:
                    api_key = api_key or spec.api_key
                    base_url = base_url or spec.base_url
                    break
        except Exception:
            pass

    try:
        import litellm
    except ImportError as exc:
        return {"ok": False, "error_type": "missing_dep", "detail": f"litellm: {exc}"}

    start = time.monotonic()
    try:
        resp = litellm.completion(
            model=f"{provider}/{model_name}",
            messages=[{"role": "user", "content": "ping"}],
            api_key=api_key,
            api_base=base_url,
            max_tokens=5,
            timeout=15,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        try:
            content = resp.choices[0].message.content or ""
        except Exception:
            content = ""
        return {"ok": True, "detail": f"got {len(content)} char reply",
                "latency_ms": latency_ms}
    except Exception as exc:
        # Classify — litellm has typed exceptions but we take a defensive approach
        # so users with older/newer versions get a useful message either way.
        name = type(exc).__name__.lower()
        if "auth" in name or "permission" in name:
            error_type = "auth"
        elif "rate" in name:
            error_type = "rate_limit"
        elif "connection" in name or "timeout" in name or "apiconnection" in name:
            error_type = "network"
        elif "notfound" in name or "badrequest" in name:
            error_type = "bad_request"
        else:
            error_type = "other"
        return {
            "ok": False,
            "error_type": error_type,
            "detail": f"{type(exc).__name__}: {exc}"[:400],
            "latency_ms": int((time.monotonic() - start) * 1000),
        }


# Small smoke test — run: python -m pobi.web_console.preflight
if __name__ == "__main__":
    import json
    print(json.dumps(run_preflight(), indent=2, ensure_ascii=False))
