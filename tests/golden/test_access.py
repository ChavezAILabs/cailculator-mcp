"""
Access gating (Phase 1): which domain profiles each plan may use.

In-process only (the plan is injected; the spawned server always runs as the dev
``developer`` plan). Fast: denied calls and default-filling never reach the math.
"""

import ast
import asyncio
from pathlib import Path

import pytest

from runner import SRC_DIR  # noqa: F401  (puts src/ on sys.path)
from cailculator_mcp import plans
from cailculator_mcp.tools import call_tool

REPO = Path(__file__).resolve().parents[2]
SOLD_PLANS = [p for p in plans.PLAN_PROFILES if p != "developer"]
ALL_PROFILES = ["general_data", "journalism", "quant_equity", "developer_v1"]


def _call(tool, args, plan):
    return asyncio.run(call_tool(tool, args, plan=plan))


def test_plan_table_matches_auth_server():
    """The welcome email quotes auth_server's table; the package enforces this one."""
    tree = ast.parse((REPO / "auth_server" / "main.py").read_text(encoding="utf-8"))
    server_table = next(
        ast.literal_eval(node.value) for node in tree.body
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "PLAN_PROFILES" for t in node.targets))
    assert {k: sorted(v) for k, v in server_table.items()} == \
        {k: sorted(plans.PLAN_PROFILES[k]) for k in SOLD_PLANS}


def test_every_plan_profile_exists():
    profiles_dir = REPO / "src" / "cailculator_mcp" / "profiles"
    for plan, included in plans.PLAN_PROFILES.items():
        for p in included:
            assert (profiles_dir / p / "manifest.json").exists(), (plan, p)
        assert plans.default_profile(plan) in included, plan


@pytest.mark.parametrize("plan", SOLD_PLANS)
@pytest.mark.parametrize("profile", ALL_PROFILES)
@pytest.mark.parametrize("tool", sorted(plans.PROFILE_TOOLS))
def test_allowed_or_denied(tool, profile, plan):
    args = {"input_16d": [0.0] * 16, "gateway": "S1", "profile": profile}
    if profile in plans.PLAN_PROFILES[plan]:
        assert plans.apply_plan(tool, args, plan) is args
        return
    with pytest.raises(PermissionError):
        plans.apply_plan(tool, args, plan)
    # End to end: a denial is an ordinary error response that carries provenance.
    result = _call(tool, args, plan)
    assert result["success"] is False
    assert f"The {profile} profile is not included in the {plan} plan" in result["error"]
    assert plans.UPGRADE_URL in result["error"]
    assert result["provenance"]["plan"] == plan
    assert result["provenance"]["profile"] is None


@pytest.mark.parametrize("plan", SOLD_PLANS)
@pytest.mark.parametrize("tool", sorted(plans.PROFILE_TOOLS))
def test_omitted_profile_gets_plan_default(tool, plan):
    out = plans.apply_plan(tool, {"input_16d": [0.0] * 16}, plan)
    assert out["profile"] == plans.default_profile(plan)


def test_defaults():
    assert plans.default_profile("journalist") == "journalism"
    assert plans.default_profile("quant_elite") == "quant_equity"
    assert plans.default_profile("individual") == "general_data"
    assert plans.default_profile("academic") == "general_data"


def test_no_plan_means_no_gating():
    args = {"input_16d": [0.0] * 16}
    assert plans.apply_plan("zdtp_transmit", args, None) is args


def test_unknown_plan_falls_back_to_lowest():
    result = _call("zdtp_transmit", {"input_16d": [0.0] * 16, "profile": "quant_equity"},
                   "quant_enterprise_legacy")
    assert result["success"] is False
    assert result["provenance"]["plan"] == plans.FALLBACK_PLAN


@pytest.mark.parametrize("plan", SOLD_PLANS)
def test_list_domain_profiles_marks_plan(plan):
    result = _call("list_domain_profiles", {}, plan)
    assert result["plan"] == plan
    assert result["default_profile"] == plans.default_profile(plan)
    marked = {p["name"]: p["included_in_plan"] for p in result["profiles"]
              if p["name"] != "custom_request"}
    assert marked == {p: p in plans.PLAN_PROFILES[plan] for p in ALL_PROFILES}
    assert result["provenance"]["plan"] == plan


def test_dev_key_rejected_outside_source_checkout(monkeypatch):
    from cailculator_mcp import auth
    monkeypatch.setattr(auth.settings, "enable_dev_mode", True)
    monkeypatch.setattr(auth, "is_source_checkout", lambda: False)
    ok, error, plan = asyncio.run(auth.validate_api_key("dev_anything"))
    assert (ok, plan) == (False, None) and "installed package" in error
    monkeypatch.setattr(auth, "is_source_checkout", lambda: True)
    assert asyncio.run(auth.validate_api_key("dev_anything")) == (True, "", "developer")


def test_offline_fallback_grants_only_lowest_plan(monkeypatch):
    import httpx
    from cailculator_mcp import auth

    class Down:
        def __init__(self, *a, **k): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def post(self, *a, **k): raise httpx.ConnectError("down")

    monkeypatch.setattr(auth.httpx, "AsyncClient", Down)
    monkeypatch.setattr(auth.settings, "enable_offline_fallback", True)
    assert asyncio.run(auth.validate_api_key("cail_live_x")) == (True, "", plans.FALLBACK_PLAN)
    monkeypatch.setattr(auth.settings, "enable_offline_fallback", False)
    ok, _, plan = asyncio.run(auth.validate_api_key("cail_live_x"))
    assert (ok, plan) == (False, None)
