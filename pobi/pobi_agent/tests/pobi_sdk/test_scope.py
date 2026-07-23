"""Tests for the authorization scope gate (pobi_agent.scope)."""
from __future__ import annotations

import yaml

import pytest

from pobi_agent.scope import (
    DEFAULT_SCOPE,
    ScopePolicy,
    ScopeViolation,
    check_scope,
)


def test_disabled_is_noop():
    p = ScopePolicy({"enabled": False, "root_domains": ["example.com"]})
    assert p.is_allowed("https://evil.com") == (True, "scope gate disabled")
    assert p.check("https://evil.com") is True


def test_root_domain_allows_subdomains():
    p = ScopePolicy({"enabled": True, "root_domains": ["example.com"]})
    assert p.is_allowed("https://example.com") == (True, "in scope")
    assert p.is_allowed("https://api.example.com/path") == (True, "in scope")
    assert p.is_allowed("https://evil.com") == (False, "no matching in-scope target")


def test_domain_exact_only():
    p = ScopePolicy({"enabled": True, "domains": ["app.example.com"]})
    assert p.is_allowed("https://app.example.com") == (True, "in scope")
    assert p.is_allowed("https://sub.app.example.com") == (False, "no matching in-scope target")
    assert p.is_allowed("https://example.com") == (False, "no matching in-scope target")


def test_ips_and_cidr():
    p = ScopePolicy({"enabled": True, "ips": ["10.0.0.5", "192.168.1.0/24"]})
    assert p.is_allowed("http://10.0.0.5") == (True, "in scope")
    assert p.is_allowed("http://192.168.1.42") == (True, "in scope")
    assert p.is_allowed("http://10.0.1.5") == (False, "no matching in-scope target")


def test_out_of_scope_exclusion_wins():
    p = ScopePolicy(
        {
            "enabled": True,
            "root_domains": ["example.com"],
            "out_of_scope": ["secret.example.com", "127.0.0.1"],
        }
    )
    assert p.is_allowed("https://secret.example.com") == (
        False,
        "explicitly excluded (secret.example.com)",
    )
    assert p.is_allowed("https://127.0.0.1") == (False, "explicitly excluded (127.0.0.1)")
    assert p.is_allowed("https://api.example.com") == (True, "in scope")


def test_enabled_with_no_in_scope_fails_closed():
    p = ScopePolicy({"enabled": True, "root_domains": [], "domains": [], "ips": []})
    assert p.is_allowed("https://example.com") == (False, "no matching in-scope target")


def test_check_raises_on_violation():
    p = ScopePolicy({"enabled": True, "root_domains": ["example.com"]})
    with pytest.raises(ScopeViolation):
        p.check("https://evil.com")
    assert p.check("https://api.example.com") is True


def test_port_and_scheme_normalized():
    p = ScopePolicy({"enabled": True, "domains": ["example.com"]})
    assert p.is_allowed("http://example.com:8080/foo") == (True, "in scope")


def test_check_scope_reads_file(tmp_path):
    cfg_path = tmp_path / "scope.yaml"
    cfg_path.write_text(
        yaml.safe_dump({"enabled": True, "root_domains": ["example.com"]}),
        encoding="utf-8",
    )
    assert check_scope("https://api.example.com", path=str(cfg_path)) is True
    with pytest.raises(ScopeViolation):
        check_scope("https://evil.com", path=str(cfg_path))


def test_defaults_sane():
    assert DEFAULT_SCOPE["enabled"] is False
    assert isinstance(DEFAULT_SCOPE["root_domains"], list)
