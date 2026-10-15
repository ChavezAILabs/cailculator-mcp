"""
Golden suite. Run everything with:

    pytest tests/golden -q

Each case runs in-process and against a spawned server started from a temp
directory. See tests/golden/README.md for the case format and change policy.
"""

import json
import os
from collections import defaultdict

import numpy as np
import pytest

from conftest import CASES, CASES_BY_ID, OUTCOMES
from runner import (check_case, run_inprocess, strip_volatile, structural_findings)


def _judge(case, result, mode):
    problems = check_case(case, result)
    known = case.get("known_failure")
    key = (case["id"], mode)
    if known:
        if problems:
            OUTCOMES[key] = "XFAIL"
            pytest.xfail(f"known failure: {known['reason']}")
        OUTCOMES[key] = "XPASS"
        pytest.fail(f"case is marked known_failure but now passes — review it and remove the "
                    f"marker per the change policy ({known['reason']})")
    OUTCOMES[key] = "FAIL" if problems else "PASS"
    assert not problems, "\n".join(problems)


def _cleanup(result):
    path = result.get("static_path")
    if path and os.path.exists(path):
        os.remove(path)


@pytest.mark.parametrize("case_id", [c["id"] for c in CASES])
def test_case_inprocess(case_id, results):
    case = CASES_BY_ID[case_id]
    result = results.inprocess(case_id)
    try:
        if case.get("expect_static_file"):
            assert os.path.isfile(result.get("static_path", "")), "static_path file was not written"
        _judge(case, result, "inprocess")
    finally:
        if case.get("expect_static_file"):
            _cleanup(result)


@pytest.mark.parametrize("case_id", [c["id"] for c in CASES])
def test_case_mcp(case_id, results):
    case = CASES_BY_ID[case_id]
    result = results.mcp(case_id)
    try:
        if case.get("expect_static_file"):
            assert os.path.isfile(result.get("static_path", "")), \
                "static_path file was not written when the server ran from a temp cwd"
        _judge(case, result, "mcp")
    finally:
        if case.get("expect_static_file"):
            _cleanup(result)


@pytest.mark.parametrize("case_id", [c["id"] for c in CASES if not c.get("expect_static_file")])
def test_mcp_matches_inprocess(case_id, results):
    """The spawned server and the in-process handler must give identical output."""
    a = strip_volatile(results.inprocess(case_id))
    b = strip_volatile(results.mcp(case_id))
    assert a == b, f"in-process and MCP outputs differ for {case_id}"


def _agreement_groups():
    groups = defaultdict(list)
    for c in CASES:
        if c.get("agreement_group"):
            groups[c["agreement_group"]].append(c["id"])
    return sorted(groups.items())


@pytest.mark.parametrize("group,case_ids", _agreement_groups())
def test_tools_agree(group, case_ids, results):
    """Cases in one agreement group ask the same question of different tools."""
    verdicts = {cid: results.inprocess(cid).get("is_bilateral_zero_divisor") for cid in case_ids}
    assert len(set(verdicts.values())) == 1, f"tools disagree in {group}: {verdicts}"


def test_chavez_reversal_symmetry(results):
    """The 1D Chavez kernel is invariant under reversing the input (CHANGELOG audit 2026-08-21)."""
    fwd = results.inprocess("chavez_structured_fibonacci")["transform_value"]
    rev = results.inprocess("chavez_reversed_fibonacci")["transform_value"]
    assert abs(fwd - rev) <= 1e-9 * max(1.0, abs(fwd))


def test_every_profile_has_tier_and_gate_status():
    listing = run_inprocess("list_domain_profiles", {})
    for p in listing["profiles"]:
        if p["name"] == "custom_request":
            continue
        assert p.get("tier") in ("Template", "Experimental", "Official"), p["name"]
        assert "gate_status" in p and "gates_failed" in p, p["name"]


# --- Journalism properties (Job 3B) ---

POLITICS_CASE = "journalism_politics_analyze"


def test_journalism_determinism(results):
    """Same input twice: identical output and identical input_hash."""
    first = results.inprocess(POLITICS_CASE)
    case = CASES_BY_ID[POLITICS_CASE]
    second = run_inprocess(case["tool"], case["resolved_args"])
    assert first["provenance"]["input_hash"] == second["provenance"]["input_hash"]
    assert strip_volatile(first) == strip_volatile(second)


def test_journalism_stability(results):
    """A 1e-9 relative perturbation must not flip any verdict or finding."""
    case = CASES_BY_ID[POLITICS_CASE]
    base = results.inprocess(POLITICS_CASE)
    data = np.array(case["resolved_args"]["data"], dtype=float)
    noise = np.random.default_rng(99).normal(0.0, 1e-9, size=data.shape)
    perturbed = run_inprocess(case["tool"], {**case["resolved_args"], "data": list(data * (1 + noise))})
    for key in ("classification", "stability_level"):
        assert perturbed["regime"][key] == base["regime"][key]
    assert structural_findings(perturbed) == structural_findings(base)
    assert abs(perturbed["regime"]["convergence_score"] - base["regime"]["convergence_score"]) < 1e-6
