# Pobi CLI

> [!WARNING]
> **Active Development**: This project is undergoing active development. Current features are functional but the interface and workflows are being improved based on new architecture and features.

**Autonomous pentesting agent using feedback-driven iteration**
Achieves ~78% on XBOW benchmarks with fully local execution and model-agnostic architecture.

📄 [Read Technical Deep Dive](https://xoxruns.medium.com/feedback-driven-iteration-and-fully-local-webapp-pentesting-ai-agent-achieving-78-on-xbow-199ef719bf01) | 📊 [Benchmark Results](https://github.com/xoxruns/deadend-cli/tree/main/benchmarks-results/xbow)

---

## What is Pobi CLI?

Pobi CLI is an autonomous web application penetration testing agent that uses feedback-driven iteration to adapt exploitation strategies. When standard tools fail, it generates custom Python payloads, observes responses, and iteratively refines its approach until breakthrough.

**Key features:**

- Fully local execution (no cloud dependencies, zero data exfiltration)
- Model-agnostic design (works with any deployable LLM)
- Custom sandboxed tools (Playwright, Docker, WebAssembly)
- ADaPT-based architecture with supervisor-subagent hierarchy
- Confidence-based decision making (fail <20%, expand 20-60%, refine 60-80%, validate >80%)

**Benchmark results:** 78% on XBOW validation suite (76/98 challenges), including blind SQL injection exploits where other agents achieved 0%.

[Read the architecture breakdown in our technical article →](https://xoxruns.medium.com/feedback-driven-iteration-and-fully-local-webapp-pentesting-ai-agent-achieving-78-on-xbow-199ef719bf01)

---

## Core Analysis Capabilities

The framework focuses on **intelligent security analysis** through:

- **🔍 Taint Analysis**: Automated tracking of data flow from sources to sinks
- **🎯 Source/Sink Detection**: Intelligent identification of entry points and vulnerable functions
- **🔗 Contextual Tool Integration**: Smart connection to specialized tools for testing complex logic patterns
- **🧠 AI-Driven Reasoning**: Context-aware analysis that mimics expert security thinking

---

## 🔧 Custom Pentesting Tools

- **Webapp-Specific Tooling**: Custom tools designed specifically for web application penetration testing
- **Authentication Handling**: Built-in support for session management, cookies, and auth flows
- **Fine-Grained Testing**: Precise control over individual requests and parameters
- **Payload Generation**: AI-powered payload creation tailored to target context
- **Automated Payload Testing**: Generate, inject, and validate payloads in a single workflow

---

## Quick Start

### Prerequisites

- Docker (required)
- Python 3.11+
- uv >= 0.5.30
- Playwright: `playwright install`

### Installation

```bash
# Install via pipx (recommended)
pipx install pobi

# Or build from source
git clone https://github.com/xoxruns/deadend-cli.git
cd pobi
uv sync && uv build
```

### First Run

```bash
# Initialize configuration
pobi init
```

---

## Commands

### `pobi init`

Initialize configuration and set up pgvector database

### `pobi eval-agent`

Run evaluation against challenge datasets

- `--eval-metadata-file`: Challenge dataset file
- `--provider`: AI model provider to use
- `--model-name`: AI model to use

### `pobi version`

Display current version

---

## Architecture Summary

The agent uses a two-phase approach (reconnaissance → exploitation) with a supervisor-subagent hierarchy:

**Supervisor**: Maintains high-level goals, delegates to specialized subagents
**Subagents**: Focused toolsets (Requester for HTTP, Shell for commands, Python for payloads)
**Policy**: Confidence scores (0-1.0) determine whether to fail, expand, refine, or validate

**Key innovation:** When standard tools fail, the agent generates custom exploitation scripts and iterates based on observed feedback—solving challenges like blind SQL injection where static toolchains achieve 0%.

[Read full architecture details →](https://xoxruns.medium.com/feedback-driven-iteration-and-fully-local-webapp-pentesting-ai-agent-achieving-78-on-xbow-199ef719bf01)

---

## Validation Configuration

The agent uses a composable validation system to determine when the root goal of an assessment has been achieved. Configuration is driven by a YAML file at `~/.cache/pobi/validation.yaml`.

### How It Works

After every supervisor execution, a **validation gate** runs a chain of strategies in order. The first strategy that returns `stop: true` triggers a report and exits the loop. If no strategy stops, the ADaPT policy (expand/refine/fail) continues as normal.

**Available strategies:**

| Strategy | Cost | What it does |
|----------|------|-------------|
| `flag` | Zero (regex) | Scans proofs, summaries, and context for a token matching a configurable regex pattern |
| `judge` | 1 LLM call | Agent that evaluates the full execution trace against the root goal. Self-throttles when no new evidence has appeared |

### Configuration File

Create `~/.cache/pobi/validation.yaml`. A reference file with all options is at `pobi_agent/src/pobi_agent/config/validation.default.yaml`.

### Examples

**CTF with `FLAG{}` tokens** (default if no file exists):

```yaml
validation_format: "FLAG{}"
validation_type: "flag"
strategies:
  - name: flag
    pattern: "FLAG\\{[^}]+\\}"
  - name: judge
```

The `flag` strategy runs first (free regex check). If no match, the `judge` LLM evaluates whether the goal is done.

**HackTheBox:**

```yaml
validation_format: "HTB{}"
validation_type: "flag"
strategies:
  - name: flag
    pattern: "HTB\\{[^}]+\\}"
  - name: judge
    validation_format: "HTB{}"
```

**picoCTF:**

```yaml
validation_format: "picoCTF{}"
validation_type: "flag"
strategies:
  - name: flag
    pattern: "picoCTF\\{[^}]+\\}"
  - name: judge
    validation_format: "picoCTF{}"
```

**Recon / security assessment** (no flag to find):

```yaml
validation_type: "security assessment"
strategies:
  - name: judge
```

No `flag` strategy — the LLM judge evaluates whether the recon goal (e.g., "map the attack surface") is satisfied based on accumulated evidence.

**Flag-only (fastest, no LLM judge):**

```yaml
validation_format: "FLAG{}"
strategies:
  - name: flag
```

Only regex matching, no LLM call at all. Cheapest option for CTFs where the flag format is known.

### Configuration Reference

**Top-level fields:**

| Field | Type | Description |
|-------|------|-------------|
| `validation_format` | `string \| null` | Token format shown in agent prompts (e.g., `"FLAG{}"`, `"HTB{}"`). Set to `null` for assessments without tokens |
| `validation_type` | `string \| null` | Type label for the judge prompt (e.g., `"flag"`, `"security assessment"`) |
| `strategies` | `list` | Ordered list of strategy configurations |

**Per-strategy fields:**

| Field | Strategy | Description |
|-------|----------|-------------|
| `name` | all | Strategy name: `"flag"` or `"judge"` |
| `pattern` | `flag` | Regex pattern (default: `FLAG\{[^}]+\}`) |
| `validation_type` | `judge` | Override top-level `validation_type` for this strategy |
| `validation_format` | `judge` | Override top-level `validation_format` for this strategy |

### Programmatic Override

Pass a custom config path when constructing the agent:

```python
agent = DeadEndAgent(
    session_id=session_id,
    model=model,
    available_agents=agents,
    validation_config_path="/path/to/custom/validation.yaml",
)
```

---

## Benchmark Results

Evaluated on XBOW's 104-challenge validation suite (black-box mode, January 2026):

| Agent              | Success Rate | Infrastructure  | Blind SQLi |
| ------------------ | ------------ | --------------- | ---------- |
| XBOW (proprietary) | 85%          | Proprietary     | ?          |
| Cyber-AutoAgent    | 81%          | AWS Bedrock     | 0%         |
| **Pobi CLI**    | **78%**      | **Fully local** | **33%**    |
| MAPTA              | 76.9%        | External APIs   | 0%         |

**Models tested:** Claude Sonnet 4.5 (~78%), Kimi K2 Thinking (~69%)

Strong performance: XSS (91%), Business Logic (86%), SQL injection (83%), IDOR (80%)
Perfect scores: GraphQL, SSRF, NoSQL injection, HTTP method tampering (100%)

## Technology Stack

- **LiteLLM**: Multi-provider model abstraction (OpenAI, Anthropic, Ollama)
- **Instructor**: Structured LLM outputs
- **pgvector**: Vector database for context
- **Pyodide/WebAssembly**: Python sandbox
- **Playwright**: HTTP request generation
- **Docker**: Shell command isolation

---

## Configuration

Configuration is managed via `~/.pobi/config.json`. Run `pobi init` to set up your Docker prerequisites, then configure providers from the chat UI.

---

## Current Status & Roadmap

### Stable (v0.0.15)

✅ New architecture
✅ XBOW benchmark evaluation (78%)
✅ Custom sandboxed tools
✅ Multi-model support with liteLLM
✅ Two-phase execution (recon + exploitation)

### In Progress (v0.1.0)

🚧 **CLI Redesign** with enhanced workflows:

- Plan mode (review strategies before execution)
- Preset configuration workflows (API testing, web apps, auth bypass)
- Workflow automation (save/replay attack chains)

🚧 Context optimization (reduce redundant tool calls)
🚧 Secrets management improvements

### Future roadmap

The current architecture proves competitive autonomous pentesting (78%) is achievable without cloud dependencies. The plan below moves Pobi from a **CTF-competitive web agent** to a **general-purpose autonomous pentesting platform**. Milestones are ordered by **blocking-value first** — safety and honesty gaps before new capability.

For the full narrative version, see the [top-level README roadmap](../README.md#future-roadmap). Summary here:

#### v0.3 — Harden what's already claimed (Q3 2026)

- **Authorization scope gate** *(blocking)*. `scope: { domains, cidrs, out_of_scope, max_qps }` in config, enforced inside `AgentExecutor` and every network tool. Out-of-scope request → hard abort. Without this, "autonomous" is a liability, not a feature.
- **Plan mode (`/plan`)** finished. Render `Planner.TaskNode` tree before execution; human approves / prunes / edits; approved plans persist as JSON for replay.
- **Context compression**. Dedup repeated tool outputs in `ContextEngine`; summarize long HTTP bodies before re-injection; raw blobs stay in RAG. Target: same XBOW score at ≥30% fewer tokens.
- **Report v2**. Split `reporter.py` into technical writeup + executive summary + SARIF/JSON. Every finding carries repro, evidence blob IDs, CVSS.
- **Core-loop tests**. Assert-level unit tests for `ADaPTAgent` threshold branches, `ValidationGate` chaining, scope-gate rejection.

#### v0.4 — Beyond web-only (Q4 2026)

- **Recon toolbelt** (Docker-wrapped): `nmap`, `httpx`, `naabu`, `ffuf`/`gobuster`, `nuclei`, `subfinder`/`amass`, `whatweb`. Each is a `Tool` with a strict output schema so recon planning uses real evidence, not guesses.
- **Vulnerability intelligence RAG**. Ingest `nuclei-templates`, `exploit-db`, CVE feeds into the existing `pgvector`. Fingerprint → template/exploit retrieval → planner suggestion. Nightly refresh.
- **Persistent shell sessions**. Replace one-shot `shell.py` with pty-backed sessions keyed by `session_id`. Enables post-exploitation.
- **WAF / rate-limit adaptation**. Adaptive backoff on 429/403, proxy-pool hook, payload mutator (encoding, case, delimiters).
- **Session credential vault**. Sqlite store for collected cookies/tokens/hashes/keys, scoped to `session_id`.

#### v0.5 — Post-exploitation and multi-target (Q1 2027)

- **Post-exploitation agent**. Automated Linux/Windows enum (LinPEAS/WinPEAS/PowerUp-style), credential harvest, kernel-version → exploit lookup via vuln RAG. Emits structured findings, not shell dumps.
- **Pivot primitives**. SSH/SOCKS pivot manager, reachability graph (`host_a --creds_from--> host_b`) as first-class state.
- **Multi-target orchestration**. Refactor `DeadEndAgent` from single-target to a target graph; artifacts from A auto-enter B's context.
- **Cross-session knowledge base**. Persistent `assets` / `findings` / `credentials` / `attack_paths` tables. Warm-start against known domains.

#### v0.6 — Open models and adversarial robustness (Q2 2027)

- **Open-weight parity**. Fine-tune Qwen/Llama on distilled XBOW success traces (from `benchmarks-results/xbow/`) with efficiency-based reward shaping. Target ≥75% XBOW. Trace dataset + eval harness published.
- **Adversarial training**. WAF/rate-limit/honeypot corpus; agent variants scored on evasion **and** safety together; findings feed the mutator.
- **Hybrid white-box**. `code_indexer` + tree-sitter AST → taint analysis → prioritized input to `PlannerExploitAgent`.

#### v0.7 — Productionization (H2 2027)

- **Execution trace UI** in `web_console` (uses existing `event_bus`): timeline, per-node cost, single-step replay from any checkpoint.
- **Multi-user backend**: authn/authz, per-user scope isolation, task queue, artifact storage.
- **Compliance mapping**: findings auto-tagged against OWASP ASVS / PCI-DSS / MITRE ATT&CK; reporter emits a coverage matrix.
- **Cost governance**: per-run token/$ budget with hard stop, surfaced in Plan mode.

#### Explicit non-goals

To keep scope honest: no physical/social engineering/phishing, no DoS/stress/mass targeting (the scope gate is designed to prevent this), no evasion tooling for unauthorized use, no hosted SaaS before v0.7 — local-first is a feature.

**North star:** point Pobi at an in-scope asset, walk away, come back to a report a human pentester would sign.

---

## Contributing

Contributions welcome in:

- Context optimization algorithms
- Vulnerability test cases
- Open-weight model fine-tuning
- Adversarial testing scenarios

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on how to contribute.

---

## Citation

```bibtex
@software{pobi_2026,
  author = {Yassine Bargach},
  title = {Pobi CLI: Feedback-Driven Autonomous Pentesting},
  year = {2026},
  url = {https://github.com/xoxruns/deadend-cli}
}
```

---

## Disclaimer

**For authorized security testing only.** Unauthorized testing is illegal. Users are responsible for compliance with all applicable laws and obtaining proper authorization.

---

## Links

📄 [Architecture Deep Dive](https://xoxruns.medium.com/feedback-driven-iteration-and-fully-local-webapp-pentesting-ai-agent-achieving-78-on-xbow-199ef719bf01)
📊 [Benchmark Results](https://github.com/xoxruns/deadend-cli/tree/main/benchmarks-results/xbow)
🐛 [Report Issues](https://github.com/xoxruns/deadend-cli/issues)
⭐ [Star this repo](https://github.com/xoxruns/deadend-cli)
