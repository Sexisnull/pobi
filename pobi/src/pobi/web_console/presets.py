"""Preset scan workflows for the New Scan wizard.

Presets map directly to a `run_agent_recursive` invocation: they pre-fill the
agent strategy, depth and validation configuration so an operator can launch a
recognised engagement type in one click.
"""

PRESETS = [
    {
        "id": "quick_recon",
        "name": "Quick Recon",
        "description": "Lightweight, read-only reconnaissance of the target surface. "
                       "No intrusive payloads.",
        "agent_type": "router_agent",
        "prompt": "Perform read-only reconnaissance: enumerate endpoints, technologies "
                  "and obvious misconfigurations. Do not send intrusive payloads.",
        "max_depth": 2,
        "icon": "radar",
        "color": "#38bdf8",
    },
    {
        "id": "full_web_pentest",
        "name": "Full Web Pentest",
        "description": "End-to-end autonomous web penetration test: recon, injection, "
                       "auth bypass and business-logic abuse. Requires approval mode for "
                       "destructive steps.",
        "agent_type": "router_agent",
        "prompt": "Run a full web application penetration test. Cover reconnaissance, "
                  "SQL/NoSQL injection, XSS, authentication flaws and access control. "
                  "Escalate only on validated findings.",
        "max_depth": 5,
        "icon": "crosshair",
        "color": "#f472b6",
    },
    {
        "id": "api_only",
        "name": "API-Only Audit",
        "description": "Focus on REST/GraphQL APIs: parameter tampering, IDOR, BOLA and "
                       "rate-limit weaknesses.",
        "agent_type": "router_agent",
        "prompt": "Focus exclusively on the API surface. Test for broken object level "
                  "authorization, parameter tampering, injection in query/path bodies and "
                  "weak rate limiting.",
        "max_depth": 4,
        "icon": "brackets",
        "color": "#a78bfa",
    },
    {
        "id": "auth_bypass",
        "name": "Auth & Access Control",
        "description": "Target authentication and authorization: login bypass, JWT flaws, "
                       "privilege escalation.",
        "agent_type": "router_agent",
        "prompt": "Focus on authentication and authorization. Attempt login bypass, JWT "
                  "weaknesses, session fixation and vertical/horizontal privilege escalation.",
        "max_depth": 4,
        "icon": "shield",
        "color": "#34d399",
    },
]


def get_presets() -> list[dict]:
    return PRESETS


def get_preset(preset_id: str) -> dict | None:
    for p in PRESETS:
        if p["id"] == preset_id:
            return p
    return None
