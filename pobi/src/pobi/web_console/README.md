# Pobi Web Console

A browser-based control plane for the **Pobi** autonomous penetration-testing
agent. It is the "Web Console" component described in the architecture diagram:
it talks JSON-RPC 2.0 over stdio to the Python `pobi-jsonrpc-server` daemon,
exposes a small REST + SSE API, and renders a live operations UI (dashboard,
scan wizard, monitor, results, settings, audit).

```
Browser ──HTTP/SSE──▶ Web Console (FastAPI) ──JSON-RPC(stdio)──▶ pobi-jsonrpc-server (daemon)
                                                       │
                                                       └─ subscribe_events ─▶ SSE fan-out to all clients
```

## Features

- **Dashboard** – component health, mode, live client count, recent activity.
- **New Scan** – preset workflows (Quick Recon, Full Web Pentest, API-Only,
  Auth & Access Control), target/scope, agent strategy, LLM model, guardrails
  (max depth, min confidence, approval gate).
- **Monitor** – live event feed, agent-confidence bar, task tree, operator
  approval inbox, interrupt.
- **Results** – validated findings table + execution log.
- **Settings** – component health + re-init, validation config, LLM provider,
  approval mode.
- **Audit** – an accountable trail of every privileged action (scan launched,
  approval granted/denied, config changed, scan interrupted).

## Modes

The console can run in two modes:

| Mode        | When                                                          | Use case |
|-------------|---------------------------------------------------------------|----------|
| `daemon`    | The `pobi-jsonrpc-server` can be spawned in this env      | Real autonomous scans against your target (needs Docker + an LLM key configured for the daemon). |
| `simulation`| Daemon unavailable (no Docker/LLM, or `DEADEND_WEB_SIMULATE=1`) | Demos, CI, and verifying the UI without the heavy stack. Emits the same event schema. |

Mode is detected automatically at startup; the top bar shows the active mode.

## Run it

The web console now lives inside the main `pobi` package (as
`pobi.web_console`), so it ships with the project — no separate folder.

```bash
# 1. install the project with the optional web extra (or let run.py auto-install)
pip install -e ".[web]"        # editable, from the repo root
# or, for a regular install:
pip install ".[web]"

# 2. launch the console
pobi-web-console

# alternatives (no install needed, repo root on PYTHONPATH):
python -m pobi.web_console.run
```

Then open <http://localhost:8000>. On first run the launcher auto-installs
`fastapi` / `uvicorn` / `sse-starlette` if they are missing.

### Environment variables

| Variable                 | Default   | Purpose |
|--------------------------|-----------|---------|
| `DEADEND_WEB_HOST`       | `0.0.0.0` | Bind host |
| `DEADEND_WEB_PORT`       | `8000`    | Bind port |
| `DEADEND_WEB_DATA`       | `<repo>/web_console_data` | Where `audit.db` / `daemon.log` live |
| `DEADEND_WEB_SIMULATE`   | `""`      | Set `1`/`true` to force simulation mode |
| `DEADEND_DAEMON_CMD`     | auto      | Override the daemon spawn command (space-separated) |
| `DEADEND_RPC_CONNECT_TIMEOUT` | `90` | Seconds to wait for the daemon to become responsive |

## Running a real scan

1. Make sure the daemon's prerequisites are met in your environment
   (Docker daemon running, an OpenAI-compatible `LLM_*` config, Playwright, etc.).
2. Open **Settings → Re-init components** (or rely on the daemon's own init).
3. Go to **New Scan**, enter your target (e.g. `http://127.0.0.1:8005`), pick a
   preset, and **Launch**.
4. Watch **Monitor** for the live event feed, confidence and approval requests;
   review **Results** when the session completes.

## API summary

| Method | Path | Notes |
|--------|------|-------|
| GET  | `/api/status`            | mode, connection, approval mode |
| GET  | `/api/health`            | component health |
| POST | `/api/init`              | (re)initialize components |
| GET/POST | `/api/validation`     | validation config |
| GET/POST | `/api/llm`           | LLM provider/model |
| GET/POST | `/api/approval-mode` | approval gate |
| GET  | `/api/presets`          | preset workflows |
| POST | `/api/agents`           | instantiate an agent (returns `agent_id`) |
| GET  | `/api/agents/{id}/tasks`| task snapshot |
| POST | `/api/agents/{id}/embed`| embed target (streaming) |
| POST | `/api/scans`            | start `run_agent_recursive` (returns `session_id`) |
| GET  | `/api/sessions/{id}`    | session snapshot (findings, tasks, confidence) |
| POST | `/api/scans/{id}/interrupt` | interrupt a scan |
| POST | `/api/approve`          | approve/deny an intrusive action |
| GET/POST | `/api/audit`         | audit trail |
| GET  | `/api/events`           | SSE stream of agent events |

## Layout

```
pobi/src/pobi/web_console/
  run.py                 # launcher (auto-installs deps, runs uvicorn) + `pobi-web-console` entry point
  settings.py            # paths & env config
  daemon_bridge.py       # JSON-RPC stdio client + event fan-out
  simulator.py           # fallback scan engine (simulation mode)
  audit.py               # sqlite audit trail
  presets.py             # preset scan workflows
  api.py                 # FastAPI app (REST + SSE)
  static/                # frontend (index.html, css, js)
```
