"""Launcher for the Pobi Web Console.

Run it with the console script (after install)::

    pobi-web-console

or directly (repo root on PYTHONPATH)::

    python -m pobi.web_console.run
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

# Make the `src` layout importable even when running without an install,
# so `pobi.web_console` resolves regardless of cwd.
_SRC_DIR = str(Path(__file__).resolve().parents[2])  # .../pobi/src
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


def _ensure_deps() -> None:
    """Best-effort install of the optional web dependencies if missing."""
    needed = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn[standard]",
        "sse_starlette": "sse-starlette",
    }
    missing = [pkg for mod, pkg in needed.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"[web-console] installing missing deps: {', '.join(missing)}")
        if shutil.which("uv"):
            subprocess.check_call(["uv", "pip", "install", "--python", sys.executable, *missing])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *missing])


def main() -> None:
    _ensure_deps()
    import os  # noqa: E402
    import threading  # noqa: E402
    import webbrowser  # noqa: E402
    from pobi.web_console.settings import settings  # noqa: E402
    import uvicorn  # noqa: E402
    from pobi.web_console.api import app  # noqa: E402

    host_for_url = "localhost" if settings.host in ("0.0.0.0", "") else settings.host
    url = f"http://{host_for_url}:{settings.port}"
    print(f"[web-console] starting on {url}")
    print(f"[web-console] data dir: {settings.data_dir}")

    if os.environ.get("POBI_NO_BROWSER") != "1":
        # Give uvicorn ~1.5s to bind before opening the tab.
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
