"""
Journalism Gateway Labels
Domain Projection Layer for CAILculator v2.0

Profile 3.0.0: gateways are identified by their Canonical Six names only.
The earlier interpretive labels ("Consensus Tipping Point", "Policy Shift
Indicator", ...) were not backed by any test and were removed; see CHANGELOG.
"""

GATEWAY_LABELS = {
    1: "S1",
    2: "S2",
    3: "S3A",
    4: "S3B",
    5: "S4",
    6: "S5"
}

def get_label(pattern_id: int) -> str:
    return GATEWAY_LABELS.get(pattern_id, f"Pattern {pattern_id}")
