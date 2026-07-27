#!/bin/bash
#
# Pobi — install & environment setup script
# ---------------------------------------------------------------------------
# After a plain `git clone`, this script:
#   1. Ensures `uv` is installed (installs it if missing)
#   2. Creates an isolated virtualenv and installs the project via `uv sync`
#      (web dependencies are included by default, so `pobi-web-console` works)
#   3. Checks runtime prerequisites and helps configure them:
#        - Docker (required for sandboxed scans; pulls the sandbox image)
#        - Playwright Chromium (used by the browser-automation tool)
#   4. Symlinks the console scripts onto your PATH
#   5. Optionally launches the Web Console
#
# Simplest path (no script needed):
#   uv sync && pobi-web-console        # then open http://localhost:8000
#
# Examples:
#   ./install.sh                         # full setup into ~/.cache/pobi/venv
#   ./install.sh --install-dir /opt/pobi
#   ./install.sh --no-browser            # skip the (large) Playwright download
#   ./install.sh --skip-docker           # skip Docker checks / image pull
#   ./install.sh --launch                # install, then launch the Web Console
#   ./install.sh --help
# ---------------------------------------------------------------------------
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info(){ printf '%s%s%s\n' "$GREEN" "$*" "$NC"; }
warn(){ printf '%s%s%s\n' "$YELLOW" "$*" "$NC"; }
err(){ printf '%s%s%s\n' "$RED" "$*" "$NC" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- Version (single source of truth: ./VERSION) ----
if [ -f "$SCRIPT_DIR/VERSION" ]; then
  VERSION="$(tr -d '[:space:]' < "$SCRIPT_DIR/VERSION")"
else
  VERSION="0.2.0"
fi

# ---- Defaults ----
INSTALL_DIR="${INSTALL_DIR:-$HOME/.cache/pobi/venv}"
BIN_DIR="$HOME/.local/bin"
PACKAGE_DIR="$SCRIPT_DIR/pobi"
LAUNCH=false
PYTHON_BIN=""
INSTALL_BROWSER=true
SKIP_DOCKER=false

# ---- Argument parsing ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)      VERSION="$2"; shift 2;;
    --install-dir)  INSTALL_DIR="$2"; shift 2;;
    --bin-dir)      BIN_DIR="$2"; shift 2;;
    --package-dir)  PACKAGE_DIR="$2"; shift 2;;
    --no-browser)   INSTALL_BROWSER=false; shift;;
    --skip-docker)  SKIP_DOCKER=true; shift;;
    --launch)       LAUNCH=true; shift;;
    --python)       PYTHON_BIN="$2"; shift 2;;
    -h|--help)
      sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
      echo
      echo "Usage: ./install.sh [OPTIONS]"
      echo "  --version VER       Version label (informational, default: $VERSION)"
      echo "  --install-dir DIR   Virtualenv location (default: $INSTALL_DIR)"
      echo "  --bin-dir DIR       Where to symlink console scripts (default: $BIN_DIR)"
      echo "  --package-dir DIR   Path to the pobi package (default: $PACKAGE_DIR)"
      echo "  --no-browser        Skip the Playwright Chromium download"
      echo "  --skip-docker       Skip Docker checks / image pull"
      echo "  --launch            Launch the Web Console after installing"
      echo "  --python PATH       Python interpreter to use (default: uv/python3)"
      echo "  -h, --help          Show this help"
      exit 0;;
    *) err "Unknown option: $1"; exit 1;;
  esac
done

info "==> Pobi installer (version $VERSION)"

# ---- 0. Ensure uv is available ----
if ! command -v uv >/dev/null 2>&1; then
  warn "uv not found — installing it now (requires curl + internet) ..."
  if command -v curl >/dev/null 2>&1; then
    if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
      err "uv auto-install failed. Install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
      exit 1
    fi
    # Put the uv we just installed on PATH for the rest of this script.
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  else
    err "curl is required to auto-install uv. Install uv manually and re-run."
    exit 1
  fi
  if ! command -v uv >/dev/null 2>&1; then
    err "uv installation failed. Install it manually and re-run."
    exit 1
  fi
fi
info "==> Using uv: $(uv --version)"

# ---- 1. Ensure git submodules (best-effort; skipped when none) ----
if [ -f "$SCRIPT_DIR/.gitmodules" ] && command -v git >/dev/null 2>&1; then
  info "==> Initializing git submodules ..."
  git -C "$SCRIPT_DIR" submodule update --init --recursive || \
    warn "Submodule init partially failed; core sandbox should still be present."
fi

if [ ! -f "$PACKAGE_DIR/pyproject.toml" ]; then
  err "Cannot find the pobi package at: $PACKAGE_DIR"
  err "Pass --package-dir to point at the directory containing pyproject.toml."
  exit 1
fi

# ---- 2. Resolve a Python interpreter & create the venv ----
if [ -z "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(uv python find 2>/dev/null || true)"
  [ -z "$PYTHON_BIN" ] && PYTHON_BIN="$(command -v python3 || true)"
fi
[ -z "$PYTHON_BIN" ] && { err "No Python 3 interpreter found. Install Python 3.11+ and retry."; exit 1; }
info "==> Using Python: $("$PYTHON_BIN" --version 2>&1)"

if [ ! -x "$INSTALL_DIR/bin/python" ]; then
  info "==> Creating virtual environment at $INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"
  uv venv --python "$PYTHON_BIN" "$INSTALL_DIR" >/dev/null
fi
VENV_PY="$INSTALL_DIR/bin/python"
VENV_BIN="$INSTALL_DIR/bin"

# ---- 3. Install the project (workspace-aware uv sync) ----
# Web deps are part of the default dependencies, so plain `uv sync` is enough.
info "==> Installing pobi (workspace) via uv sync ..."
(cd "$SCRIPT_DIR" && UV_PROJECT_ENVIRONMENT="$INSTALL_DIR" uv sync)

# ---- 4. Symlink console scripts onto PATH ----
info "==> Linking console scripts into $BIN_DIR"
mkdir -p "$BIN_DIR"
for cmd in pobi pobi-web-console pobi-jsonrpc-server pobi-web pobi_eval; do
  if [ -x "$VENV_BIN/$cmd" ]; then
    ln -sf "$VENV_BIN/$cmd" "$BIN_DIR/$cmd"
    info "    linked $cmd"
  fi
done
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  warn "==> $BIN_DIR is not on your PATH. Add it with:"
  if [ "$(uname)" = "Darwin" ]; then
    echo "    echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.zshrc"
  else
    echo "    echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.bashrc"
  fi
fi

# ---- 5. Runtime environment checks (best-effort, non-fatal) ----
if [ "$SKIP_DOCKER" = false ]; then
  info "==> Checking Docker (required for sandboxed scans) ..."
  if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
      info "    Docker: OK (daemon running)"
      info "    Pre-pulling sandbox image xoxruns/sandboxed_kali ..."
      if docker pull xoxruns/sandboxed_kali >/dev/null 2>&1; then
        info "    image pulled"
      else
        warn "    could not pull image (will retry automatically on first scan)"
      fi
    else
      warn "    Docker CLI found but the daemon is NOT running."
      warn "    Start Docker Desktop, or 'sudo systemctl start docker', before running a scan."
    fi
  else
    warn "    Docker not found. Install it to enable sandboxed scans:"
    if [ "$(uname)" = "Darwin" ]; then
      echo "      brew install --cask docker      # then launch Docker Desktop"
    elif [ "$(uname)" = "Linux" ]; then
      echo "      sudo apt-get update && sudo apt-get install -y docker.io"
      echo "      sudo usermod -aG docker \$USER   # then re-login"
    else
      echo "      Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    fi
  fi
fi

if [ "$INSTALL_BROWSER" = true ]; then
  info "==> Installing Playwright Chromium (used by the browser tool) ..."
  if [ -x "$VENV_BIN/playwright" ]; then
    if "$VENV_BIN/playwright" install chromium >/dev/null 2>&1; then
      info "    chromium installed"
    else
      warn "    Playwright Chromium install skipped/failed (browser tool may need it later)"
    fi
  else
    warn "    playwright not found in venv; skipping browser install"
  fi
fi

info "==> Done. Version: $VERSION"
echo
echo "  Launch the Web Console:"
echo "    pobi-web-console          # then open http://localhost:8000"
echo "  Or run a headless scan:"
echo "    pobi --target http://localhost:3000 --prompt \"find SQL injection\""

# ---- 6. Optional launch ----
if [ "$LAUNCH" = true ]; then
  if [ -x "$BIN_DIR/pobi-web-console" ]; then
    info "==> Launching Web Console ..."
    exec "$BIN_DIR/pobi-web-console"
  else
    err "pobi-web-console not found; install completed but launch aborted."
    exit 1
  fi
fi
