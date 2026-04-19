"""
RHI Gateway Labels
Domain Projection Layer for CAILculator v2.0

Maps RHI semantic concepts to universal Canonical Six patterns.
Verified anchors in BilateralCollapse.lean.
"""

from typing import Dict

# RHI semantic labels for the Canonical Six
# Anchored via (P,Q) pairs verified in Lean
GATEWAY_LABELS = {
    1: "Master Gateway",
    2: "Multi-Modal Gateway",
    3: "Discontinuous Gateway",
    4: "Conjugate Pair Gateway",
    5: "Linear Gateway",
    6: "Transformation Gateway"
}

def get_label(pattern_id: int) -> str:
    """Returns the RHI semantic label for a given core pattern ID."""
    return GATEWAY_LABELS.get(pattern_id, f"Pattern {pattern_id}")

def get_pattern_id_from_label(label: str) -> int:
    """Reverse lookup: returns pattern ID for a given RHI label."""
    for pid, lbl in GATEWAY_LABELS.items():
        if lbl.lower() == label.lower():
            return pid
    raise ValueError(f"Unknown RHI label: {label}")
