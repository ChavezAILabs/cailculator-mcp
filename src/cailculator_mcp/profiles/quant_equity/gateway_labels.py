"""
Quant Equity Gateway Labels
Domain Projection Layer for CAILculator v2.0

Translates v2.0 structural pathways into financial risk/opportunity labels.
"""

# Quant-specific labels for the structural gateways 1-6
GATEWAY_LABELS = {
    1: "Primary Volatility Anchor",
    2: "Multi-Asset Resonance Path",
    3: "Bifurcation Trigger (A)",
    4: "Mean-Reversion Discontinuity",
    5: "Bifurcation Trigger (B)",
    6: "Structural Regime Shift Path"
}

def get_label(pattern_id: int) -> str:
    return GATEWAY_LABELS.get(pattern_id, f"Risk Pathway {pattern_id}")
