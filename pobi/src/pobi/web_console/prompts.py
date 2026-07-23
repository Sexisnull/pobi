"""List / read / write agent instruction prompt templates from the pobi_prompts package.

These are the ``<name>.instructions.jinja2`` files that drive each agent's system
prompt. Edits are persisted next to the package (editable installs) or into an
override directory under the web console data dir when the package is read-only.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .settings import settings

_PKG = "pobi_prompts"
_SUFFIX = ".instructions.jinja2"


def _frontmatter(text: str) -> dict:
    try:
        import frontmatter

        meta, _ = frontmatter.parse(text)
        return dict(meta) if isinstance(meta, dict) else {}
    except Exception:
        return {}


def _package_root() -> Optional[Path]:
    try:
        from importlib import resources

        root = resources.files(_PKG)
        path = Path(str(root))
        if path.exists():
            return path
    except Exception:
        pass
    return None


def _override_path(name: str) -> Path:
    d = settings.data_dir / "prompts"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{name}{_SUFFIX}"


def _candidates() -> list[Path]:
    out: list[Path] = []
    ov = settings.data_dir / "prompts"
    if ov.exists():
        out.extend(ov.glob(f"*{_SUFFIX}"))
    root = _package_root()
    if root is not None:
        out.extend(root.glob(f"*{_SUFFIX}"))
    return out


def list_agent_prompts() -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []
    for f in sorted(_candidates(), key=lambda p: p.name):
        name = f.name[: -len(_SUFFIX)]
        if name in seen:
            continue
        seen.add(name)
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _frontmatter(text)
        results.append(
            {
                "name": name,
                "description": meta.get("description", ""),
                "role": meta.get("role", ""),
                "path": str(f),
                "writable": os.access(f, os.W_OK),
                "bytes": f.stat().st_size if f.exists() else 0,
            }
        )
    return results


def get_agent_prompt(name: str) -> dict:
    ov = _override_path(name)
    root = _package_root()
    if ov.exists():
        src = ov
    elif root is not None and (root / f"{name}{_SUFFIX}").exists():
        src = root / f"{name}{_SUFFIX}"
    elif root is not None:
        src = root / f"{name}{_SUFFIX}"
    else:
        src = ov
    if not src.exists():
        raise FileNotFoundError(f"prompt template not found: {name}{_SUFFIX}")
    try:
        content = src.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot read {src}: {exc}") from exc
    return {
        "name": name,
        "content": content,
        "path": str(src),
        "override": src == ov,
    }


def save_agent_prompt(name: str, content: str) -> dict:
    root = _package_root()
    target: Optional[Path] = None
    if root is not None:
        pkg_file = root / f"{name}{_SUFFIX}"
        try:
            if os.access(pkg_file, os.W_OK):
                target = pkg_file
        except Exception:
            target = None
    if target is None:
        target = _override_path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    stored = "override" if target.parent.name == "prompts" else "package"
    return {"ok": True, "name": name, "path": str(target), "stored": stored}
