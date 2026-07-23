#!/bin/bash
#
# Pobi CLI — install & launch script
# ---------------------------------------------------------------------------
# Builds the Pobi CLI Python package into an isolated virtual environment
# and links the console scripts onto your PATH. By default it also installs
# the optional [web] extra so the Web Console (pobi-web-console) works.
#
# Examples:
#   ./install.sh                         # install into ~/.cache/pobi/venv
#   ./install.sh --install-dir /opt/pobi
#   ./install.sh --no-web                # skip the Web Console extra
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
WEB_EXTRA=true
LAUNCH=false
PYTHON_BIN=""

# ---- Argument parsing ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)      VERSION="$2"; shift 2;;
    --install-dir)  INSTALL_DIR="$2"; shift 2;;
    --bin-dir)      BIN_DIR="$2"; shift 2;;
    --package-dir)  PACKAGE_DIR="$2"; shift 2;;
    --no-web)       WEB_EXTRA=false; shift;;
    --launch)       LAUNCH=true; shift;;
    --python)       PYTHON_BIN="$2"; shift 2;;
    -h|--help)
      sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
      echo
      echo "Usage: ./install.sh [OPTIONS]"
      echo "  --version VER       Version label (informational, default: $VERSION)"
      echo "  --install-dir DIR   Virtualenv location (default: $INSTALL_DIR)"
      echo "  --bin-dir DIR       Where to symlink console scripts (default: $BIN_DIR)"
      echo "  --package-dir DIR   Path to the pobi package (default: $PACKAGE_DIR)"
      echo "  --no-web            Skip the optional [web] extra (Web Console)"
      echo "  --launch            Launch the Web Console after installing"
      echo "  --python PATH       Python interpreter to use (default: uv/python3)"
      echo "  -h, --help          Show this help"
      exit 0;;
    *) err "Unknown option: $1"; exit 1;;
  esac
done

info "==> Pobi CLI installer (version $VERSION)"

# ---- Ensure git submodules are initialized (sandbox, benchmarks, ...) ----
# Git does not clone submodule contents by default, so do it here to make
# `./install.sh` self-sufficient after a plain `git clone` (no extra command
# required by the user). Skipped gracefully when not in a git checkout.
if [ -f "$SCRIPT_DIR/.gitmodules" ] && command -v git >/dev/null 2>&1; then
  info "==> Initializing git submodules ..."
  # Non-fatal: some submodules (e.g. benchmarks) may point at an upstream
  # commit that is no longer reachable; the core sandbox is what matters.
  if ! git -C "$SCRIPT_DIR" submodule update --init --recursive; then
    warn "Submodule init partially failed (an upstream commit may be unreachable); core sandbox should still be present."
  fi
fi

if [ ! -f "$PACKAGE_DIR/pyproject.toml" ]; then
  err "Cannot find the pobi package at: $PACKAGE_DIR"
  err "Pass --package-dir to point at the directory containing pyproject.toml."
  exit 1
fi

# ---- Resolve a Python interpreter ----
if [ -z "$PYTHON_BIN" ]; then
  if command -v uv >/dev/null 2>&1; then
    PYTHON_BIN="$(uv python find 2>/dev/null || true)"
  fi
  if [ -z "$PYTHON_BIN" ]; then
    PYTHON_BIN="$(command -v python3 || true)"
  fi
fi
[ -z "$PYTHON_BIN" ] && { err "No Python 3 interpreter found. Install Python 3.11+ and retry."; exit 1; }
info "==> Using Python: $("$PYTHON_BIN" --version 2>&1)"

# ---- Create / reuse virtualenv ----
if [ ! -x "$INSTALL_DIR/bin/python" ]; then
  info "==> Creating virtual environment at $INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"
  if command -v uv >/dev/null 2>&1; then
    uv venv --python "$PYTHON_BIN" "$INSTALL_DIR" >/dev/null
  else
    "$PYTHON_BIN" -m venv "$INSTALL_DIR"
  fi
fi
VENV_PY="$INSTALL_DIR/bin/python"
VENV_BIN="$INSTALL_DIR/bin"

# ---- Install the package ----
SPEC="."
if [ "$WEB_EXTRA" = true ]; then
  SPEC=".[web]"
  info "==> Installing pobi with the [web] extra ..."
else
  info "==> Installing pobi (core only) ..."
fi

if command -v uv >/dev/null 2>&1; then
  (cd "$PACKAGE_DIR" && uv pip install --python "$VENV_PY" "$SPEC")
else
  "$VENV_PY" -m pip install --quiet --upgrade pip
  (cd "$PACKAGE_DIR" && "$VENV_PY" -m pip install "$SPEC")
fi

# ---- Symlink console scripts onto PATH ----
info "==> Linking console scripts into $BIN_DIR"
mkdir -p "$BIN_DIR"
for cmd in pobi pobi-web-console pobi-jsonrpc-server pobi-frontend pobi-sandbox; do
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

info "==> Done. Version: $VERSION"
echo
echo "  Try it:"
echo "    pobi --target http://localhost:3000 --prompt \"find SQL injection\""
if [ "$WEB_EXTRA" = true ]; then
echo "    pobi-web-console      # then open http://localhost:8000"
fi

# ---- Optional launch ----
if [ "$LAUNCH" = true ]; then
  if [ -x "$BIN_DIR/pobi-web-console" ]; then
    info "==> Launching Web Console ..."
    exec "$BIN_DIR/pobi-web-console"
  else
    err "pobi-web-console not found; install completed but launch aborted."
    exit 1
  fi
fi
