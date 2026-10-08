"""
Subscription plan -> domain profile access (access gating, Phase 1).

The auth server's /validate response names the caller's plan (``tier``). The
server passes it to ``tools.call_tool``, which applies these rules to every call
that takes a ``profile``. This runs on the customer's machine, so it states the
rules and stops ordinary use; it is not tamper-proof (Phase 2 moves enforcement
to the auth server).

PLAN_PROFILES must match PLAN_PROFILES in auth_server/main.py, which the welcome
email quotes (checked by tests/golden/test_access.py).
"""

import contextvars
from typing import Any, Dict, Optional

_BASE = ["general_data", "developer_v1"]
_QUANT = ["quant_equity", *_BASE]
_ALL = ["general_data", "journalism", "quant_equity", "developer_v1"]

PLAN_PROFILES: Dict[str, list] = {
    "individual": list(_BASE),
    "journalist": ["journalism", *_BASE],
    "academic": list(_BASE),
    "quant_explorer": list(_QUANT),
    "quant_professional": list(_QUANT),
    "quant_elite": list(_QUANT),
    "commercial": list(_ALL),
    "enterprise": list(_ALL),
    # Not sold: dev keys in a source checkout (see auth.py).
    "developer": list(_ALL),
}

DEFAULT_PROFILE: Dict[str, str] = {
    "journalist": "journalism",
    "quant_explorer": "quant_equity",
    "quant_professional": "quant_equity",
    "quant_elite": "quant_equity",
}

# Plan granted when the auth server cannot be reached and offline fallback is on,
# or when it names a plan this package does not know: the lowest paid plan.
FALLBACK_PLAN = "individual"

UPGRADE_URL = "https://cailculator-mcp-production.up.railway.app/"

# Tools whose arguments take a ``profile``.
PROFILE_TOOLS = {"zdtp_transmit", "analyze_dataset"}

_current_plan: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "cailculator_plan", default=None
)


def normalize_plan(plan: Optional[str]) -> str:
    return plan if plan in PLAN_PROFILES else FALLBACK_PLAN


def default_profile(plan: str) -> str:
    return DEFAULT_PROFILE.get(plan, "general_data")


def current_plan() -> Optional[str]:
    """The plan of the call in progress, or None outside a gated call."""
    return _current_plan.get()


class using_plan:
    """Context manager that sets the plan for one tool call (None = ungated)."""

    def __init__(self, plan: Optional[str]):
        self.plan = plan

    def __enter__(self) -> Optional[str]:
        self._token = _current_plan.set(self.plan)
        return self.plan

    def __exit__(self, *exc) -> None:
        _current_plan.reset(self._token)


def apply_plan(tool: str, arguments: Dict[str, Any], plan: Optional[str]) -> Dict[str, Any]:
    """Fill in the plan's default profile and reject profiles the plan does not include.

    Returns the arguments to run with. Raises PermissionError for a denied profile.
    With ``plan=None`` (in-process use, tests) the arguments pass through unchanged.
    """
    if plan is None or tool not in PROFILE_TOOLS:
        return arguments
    included = PLAN_PROFILES[plan]
    profile = arguments.get("profile")
    if profile is None:
        return {**arguments, "profile": default_profile(plan)}
    if profile not in included:
        raise PermissionError(
            f"The {profile} profile is not included in the {plan} plan. "
            f"Included: {', '.join(included)}. Upgrade: {UPGRADE_URL}"
        )
    return arguments
