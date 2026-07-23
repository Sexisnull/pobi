# Copyright (C) 2025 Yassine Bargach
# Licensed under the GNU Affero General Public License v3
# See LICENSE file for full license information.

"""Live-target scan entrypoint.

Runs the Pobi agent against a running URL and writes reports to a workspace.
No EvalMetadata, no scoring — this is the general-purpose "scan a target"
path used by `pobi run` and the Web Console.
"""

import asyncio
import os
from pathlib import Path
from uuid import uuid4

from rich import print as console_printer

from pobi_agent import (
    Config,
    DeadEndAgent,
    ModelRegistry,
    init_rag_session_manager,
    sandbox_setup,
)
from pobi_agent.agents import AgentOutput
from pobi_agent.config.settings import ModelSpec
from pobi_agent.tools.browser_automation import cleanup_playwright_sessions
from pobi_agent.utils.network import deterministic_session_id


# Same taxonomy as web console (jsonrpc_server.py:864). Kept in sync manually
# until we lift it into a shared constant.
AVAILABLE_AGENTS = {
    "requester": (
        "Agent specialized in quick targeted HTTP testing. Capable of handling "
        "authentication (session and token) and exploring APIs and websites. "
        "Best default for simple requests, auth checks, individual endpoints, "
        "and lightweight payload validation. Should NOT be used for automation "
        "tasks such as fuzzing, repetitive loops, or repeated exploit attempts; "
        "use python_interpreter for those tasks instead."
    ),
    "python_interpreter": (
        "Agent specialized in generating code and running it safely in a sandbox. "
        "Best for fuzzing, repeated exploit attempts, sending many requests, "
        "parameter testing, and stateful security testing operations."
    ),
    "shell": (
        "Agent providing access to a bash shell for CLI tooling. "
        "Use for curl when exact request control is required and for external "
        "security tools such as ffuf, gobuster, sqlmap, or nmap."
    ),
    "memory": "Agent specialized in reading and writing the persistent memory workspace under the agent cache.",
    "router_agent": "Router agent that selects the appropriate specialized agent.",
    "webapp_analyzer": (
        "Front-end webapp analyzer. This agent is specialized in looking into the web application "
        "to be able to extract information about the logic details of the application. "
        "We can look for forms, API endpoints, website logic and forms"
    ),
    "authenticator": (
        "Single-purpose agent that performs the target's real authentication workflow "
        "(form login, SPA/JWT, same-tab OAuth, popup OAuth) through a real browser "
        "and persists a reusable AuthContext profile. Other agents can then opt into "
        "authenticated execution by passing auth_profile=\"<profile>\" to "
        "browser_run_steps and pw_send_payload."
    ),
}


def _resolve_model_selection(
    config: Config,
    provider: str | None,
    model_name: str | None,
) -> tuple[str, str | None]:
    """Resolve which provider/model to use.

    Priority: explicit CLI args > env vars (POBI_DEFAULT_PROVIDER/MODEL) >
    first non-embedder spec in ~/.pobi/config.json.
    """
    prov = provider or os.environ.get("POBI_DEFAULT_PROVIDER")
    mdl = model_name or os.environ.get("POBI_DEFAULT_MODEL")
    if prov is None:
        for spec in getattr(config, "model_providers", []):
            # EmbeddingSpec subclasses ModelSpec, so use type() not isinstance().
            if type(spec) is ModelSpec:
                prov = spec.provider
                mdl = mdl or spec.model_name
                break
    if prov is None:
        raise RuntimeError(
            "No LLM provider configured. Run `pobi init`, or set "
            "POBI_DEFAULT_PROVIDER (and optionally POBI_DEFAULT_MODEL) in .env."
        )
    return prov, mdl


def _shutdown_telemetry() -> None:
    """Flush OTLP exporter before the event loop closes.

    Copied from eval.py to keep run/eval independent.
    """
    try:
        from opentelemetry import trace
    except Exception:
        return
    try:
        provider = trace.get_tracer_provider()
    except Exception:
        return
    try:
        if hasattr(provider, "force_flush"):
            try:
                provider.force_flush(timeout_millis=5000)
            except TypeError:
                provider.force_flush()
    except Exception as exc:
        console_printer(f"[yellow]Telemetry force_flush failed: {exc}[/yellow]")
    try:
        if hasattr(provider, "shutdown"):
            provider.shutdown()
    except Exception as exc:
        console_printer(f"[yellow]Telemetry shutdown failed: {exc}[/yellow]")


async def run_scan(
    config: Config,
    target: str,
    prompt: str,
    provider: str | None,
    model_name: str | None,
    with_indexing: bool = False,
    max_depth: int = 3,
) -> Path:
    """Scan ``target`` with ``prompt`` and write reports under a run workspace.

    Returns the workspace path so the caller (CLI or web) can point the user at it.
    """
    model_registry = ModelRegistry(config=config)
    if not model_registry.has_any_model():
        raise RuntimeError(
            "No LM model configured. Run `pobi init` to set up an LLM provider."
        )

    resolved_provider, resolved_model = _resolve_model_selection(
        config=config, provider=provider, model_name=model_name
    )
    console_printer(
        f"[green]Using provider=[bold]{resolved_provider}[/bold] "
        f"model=[bold]{resolved_model or '(default for provider)'}[/bold][/green]"
    )
    model = model_registry.get_model(provider=resolved_provider, model_name=resolved_model)

    rag_manager = init_rag_session_manager(storage_root=config.agents_storage_root)
    local_agent_id = config.get_local_agent_id()
    embedding_session_id = deterministic_session_id(target)
    rag_db = await rag_manager.get_connector(
        agent_id=local_agent_id,
        embedding_session_id=embedding_session_id,
        target=target,
    )

    # Empty asset dir — black-box, no source to mount.
    assets_dir = Path.home() / ".cache" / "pobi" / "run-assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    sandbox = None
    sandbox_id = None
    try:
        sandbox_manager = sandbox_setup()
    except (RuntimeError, OSError) as exc:
        console_printer(f"[red]Sandbox manager could not be started: {exc}[/red]")
        raise SystemExit(1) from exc

    session_id = uuid4()
    workspace = Path.cwd() / f"pobi-run-{session_id.hex[:8]}"
    workspace.mkdir(parents=True, exist_ok=True)
    console_printer(f"[green]Workspace: {workspace}[/green]")

    try:
        sandbox_id = sandbox_manager.create_sandbox(
            image="xoxruns/sandboxed_kali",
            volume_path=str(assets_dir),
        )
        sandbox = sandbox_manager.get_sandbox(sandbox_id=sandbox_id)
        embedder_client = model_registry.get_embedder_model()

        pobi_agent = DeadEndAgent(
            session_id=session_id,
            embedding_session_id=embedding_session_id,
            model=model,
            available_agents=AVAILABLE_AGENTS,
            max_depth=max_depth,
            workspace_root=str(workspace),
            agents_storage_root=config.agents_storage_root,
            local_agent_id=local_agent_id,
        )
        pobi_agent.target = target

        if with_indexing:
            console_printer("[cyan]Crawling and indexing target...[/cyan]")
            pobi_agent.init_webtarget_indexer(target)
            await pobi_agent.crawl_target()
            code_chunks, embed_diff = await pobi_agent.embed_target(
                embedder_client=embedder_client
            )
            if embed_diff:
                stale = embed_diff.get("changed_files", []) + embed_diff.get("removed_files", [])
                if stale:
                    await rag_db.delete_code_chunks_for_files(files=stale)
            await rag_db.batch_insert_code_chunks(code_chunks_data=code_chunks)

        pobi_agent.prepare_dependencies(
            embedder_client=embedder_client,
            rag_connector=rag_db,
            sandbox=sandbox,
            target=target,
        )

        console_printer("[cyan]Phase 1/2: threat modeling & recon...[/cyan]")
        _, threat_model_data, validation_token = await pobi_agent.threat_model(task=prompt)

        if pobi_agent.goal_achieved:
            console_printer(
                f"[green]Validation stopped after recon (token={validation_token}).[/green]"
            )
        else:
            threat_output = getattr(threat_model_data, "output", threat_model_data)
            summary = (
                threat_output.detailed_summary
                if isinstance(threat_output, AgentOutput)
                else str(threat_output)
            )
            console_printer("[cyan]Phase 2/2: exploitation...[/cyan]")
            await pobi_agent.run_exploitation(threat_model=summary, task=prompt)

        reports_dir = workspace / "reports"
        console_printer(f"\n[bold green]Done.[/bold green] Reports under: {reports_dir}")
        if reports_dir.exists():
            for report in sorted(reports_dir.iterdir()):
                console_printer(f"  - {report}")
        return workspace

    finally:
        try:
            await cleanup_playwright_sessions()
        except Exception as exc:
            console_printer(f"[yellow]Playwright cleanup failed: {exc}[/yellow]")
        try:
            await rag_manager.close_all()
        except Exception as exc:
            console_printer(f"[yellow]RAG cleanup failed: {exc}[/yellow]")
        try:
            if sandbox is not None:
                sandbox.cleanup()
            elif sandbox_id is not None:
                managed = sandbox_manager.get_sandbox(sandbox_id=sandbox_id)
                if managed is not None:
                    managed.cleanup()
        except Exception as exc:
            console_printer(f"[yellow]Sandbox cleanup failed: {exc}[/yellow]")
        try:
            _shutdown_telemetry()
            await asyncio.sleep(0.1)
        except Exception as exc:
            console_printer(f"[yellow]Telemetry cleanup failed: {exc}[/yellow]")
