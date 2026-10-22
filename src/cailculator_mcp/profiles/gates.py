"""
Profile tier gates.

A profile's manifest states the tier it is *aiming for* (``tier``). The tier it
actually loads at is decided here, from the gate record ``GATES.json`` written
by ``scripts/check_profile_gates.py``:

    Template     -> Template (gates do not apply)
    Official     -> Official only if a gate record exists, every gate passed,
                    and the record matches the current profile version;
                    otherwise Experimental
    Experimental -> Experimental

Nothing else can make a profile Official.
"""

import json
import os
from typing import Any, Dict, Optional

TIERS = ("Template", "Experimental", "Official")
GATE_IDS = ("G1", "G2", "G3", "G4", "G5")
GATES_FILENAME = "GATES.json"


def load_gate_record(profile_dir: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(profile_dir, GATES_FILENAME)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"unreadable": True}


def resolve_tier(manifest: Dict[str, Any], record: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    requested = manifest.get("tier")
    status: Dict[str, Any] = {
        "requested_tier": requested,
        "gate_status": "no_record",
        "gates_passed": [],
        "gates_failed": [],
    }

    if record and not record.get("unreadable"):
        gates = record.get("gates", {})
        status["gates_passed"] = [g for g in GATE_IDS if gates.get(g, {}).get("passed") is True]
        status["gates_failed"] = [g for g in GATE_IDS if gates.get(g, {}).get("passed") is not True]
        status["gate_record"] = {
            "profile_version": record.get("profile_version"),
            "false_positive_rate": record.get("false_positive_rate"),
            "null_series": record.get("null_series"),
            "golden_suite": record.get("golden_suite"),
            "commit": record.get("commit"),
            "checked_at": record.get("checked_at"),
        }
        if record.get("profile_version") != manifest.get("version"):
            status["gate_status"] = "stale"
        elif status["gates_failed"]:
            status["gate_status"] = "failed"
        else:
            status["gate_status"] = "passed"
    elif record:
        status["gate_status"] = "unreadable"

    if requested == "Template":
        status["tier"] = "Template"
        status["gate_status"] = "not_applicable"
    elif requested == "Official" and status["gate_status"] == "passed":
        status["tier"] = "Official"
    else:
        status["tier"] = "Experimental"

    reasons = {
        "no_record": "No gate record; run scripts/check_profile_gates.py.",
        "stale": "Gate record is for a different profile version; re-run the gate check.",
        "failed": "Failed gate(s): " + ", ".join(status["gates_failed"]) + ".",
        "unreadable": "Gate record could not be read.",
    }
    if status["tier"] == "Experimental" and requested == "Official":
        status["tier_reason"] = reasons.get(status["gate_status"], "")
    elif requested not in TIERS:
        status["tier_reason"] = f"Manifest tier {requested!r} is not one of {list(TIERS)}."
    return status
