"""Runtime configuration for the Pobi Web Console."""
from __future__ import annotations

import os
from pathlib import Path

# Path to the repository root (the directory that contains `pobi/`).
# This file lives at <repo>/pobi/src/pobi/web_console/settings.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEADEND_CLI_DIR = _REPO_ROOT / "pobi"


class Settings:
    def __init__(self) -> None:
        self.repo_root: Path = _REPO_ROOT
        self.pobi_dir: Path = _DEADEND_CLI_DIR

        self.host: str = os.getenv("DEADEND_WEB_HOST", "0.0.0.0")
        self.port: int = int(os.getenv("DEADEND_WEB_PORT", "8000"))

        # Where to persist the audit log and other web-console state.
        self.data_dir: Path = Path(os.getenv("DEADEND_WEB_DATA", str(_REPO_ROOT / "web_console_data")))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Force simulation mode (no daemon). Useful for demos without docker/LLM.
        self.force_simulation: bool = os.getenv("DEADEND_WEB_SIMULATE", "").lower() in ("1", "true", "yes")

        # Explicit daemon command. If unset we auto-detect a working invocation.
        self.daemon_cmd: list[str] | None = None
        raw = os.getenv("DEADEND_DAEMON_CMD")
        if raw:
            self.daemon_cmd = raw.split()

        self.request_timeout: float = float(os.getenv("DEADEND_RPC_TIMEOUT", "120"))
        self.connect_timeout: float = float(os.getenv("DEADEND_RPC_CONNECT_TIMEOUT", "90"))


settings = Settings()
