"""
Journalism Gateway Labels
Domain Projection Layer for CAILculator v2.0

Translates v2.0 structural pathways into investigative reporting labels.
"""

# Journalism-specific labels for the structural gateways 1-6
GATEWAY_LABELS = {
    1: "Data Integrity Gateway",
    2: "Consensus Tipping Point",
    3: "Budgetary Anomaly Pathway",
    4: "Source Reliability Check",
    5: "Policy Shift Indicator",
    6: "Public Health Sentinel"
}

def get_label(pattern_id: int) -> str:
    return GATEWAY_LABELS.get(pattern_id, f"Investigative Path {pattern_id}")
