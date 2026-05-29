"""
RHI Gateway Labels
Domain Projection Layer for CAILculator v2.0

Maps RHI gateway identifiers to universal Canonical Six pattern IDs.
Verified anchors in BilateralCollapse.lean.
"""

from typing import Dict

# Gateway identifiers for the Canonical Six (pattern ID → gateway name)
GATEWAY_LABELS = {
    1: "S1",
    2: "S2",
    3: "S3A",
    4: "S3B",
    5: "S4",
    6: "S5"
}

def get_label(pattern_id: int) -> str:
    """Returns the gateway identifier for a given core pattern ID."""
    return GATEWAY_LABELS.get(pattern_id, f"Pattern {pattern_id}")

def get_pattern_id_from_label(label: str) -> int:
    """Reverse lookup: returns pattern ID for a given gateway identifier."""
    for pid, lbl in GATEWAY_LABELS.items():
        if lbl.lower() == label.lower():
            return pid
    raise ValueError(f"Unknown gateway identifier: {label}")
