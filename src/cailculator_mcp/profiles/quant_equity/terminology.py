"""
Quant Equity Terminology Translation
Domain Projection Layer for CAILculator v2.0

Maps mathematical concepts to financial/trading language.
Supports three levels: technical, standard, simple.
"""

from typing import Dict, Any

# Core terminology mappings - Finance Domain
# Profile 3.0.0: algebraic quantities are no longer translated into market language.
# Removed: bilateral_zeros ("Volatility regime shift signals"), zero_divisor ("Structural
# weakness point"), conjugation_symmetry ("Mean reversion strength", cited AIEX-231 on
# prime spectra), dimensional_persistence ("Patterns that work on multiple chart
# timeframes") and transform_convergence ("Analysis confidence score"). No test supports
# any of these readings; see CHANGELOG. Standard technical-indicator terms remain.
# chavez_transform is described as what it computes (2.2.0 decision 1); its key is no
# longer renamed to pattern_analysis / pattern_finder.
FINANCIAL_GLOSSARY = {
    "chavez_transform": {
        "technical": "1D Chavez Transform; closed form: fixed center-weighted sum of the series",
        "standard": "Center-weighted sum of the series (experimental)",
        "simple": "A weighted total of the data, with the middle counting most"
    },
    "bullish": {
        "technical": "Positive momentum with directional bias > 0",
        "standard": "Upward price trend expected",
        "simple": "Price likely going up"
    },
    "bearish": {
        "technical": "Negative momentum with directional bias < 0",
        "standard": "Downward price trend expected",
        "simple": "Price likely going down"
    },
    "overbought": {
        "technical": "RSI > 70 or price > +2σ Bollinger Band",
        "standard": "Price extended above normal range",
        "simple": "Price too high, might drop soon"
    },
    "oversold": {
        "technical": "RSI < 30 or price < -2σ Bollinger Band",
        "standard": "Price extended below normal range",
        "simple": "Price too low, might bounce up"
    },
    "volatility": {
        "technical": "Standard deviation of log returns: σ = √(Var(log(Pₜ/Pₜ₋₁)))",
        "standard": "Price movement variability",
        "simple": "How jumpy the price is"
    }
}

FIELD_MAPPINGS = {
    "technical": {},
    "standard": {
    },
    "simple": {
    }
}

def translate_term(term: str, level: str = "standard") -> str:
    """Translate a single technical term to specified level."""
    if level == "technical":
        return term
    term_lower = term.lower().replace(" ", "_")
    if term_lower in FINANCIAL_GLOSSARY:
        return FINANCIAL_GLOSSARY[term_lower].get(level, term)
    return term

def translate_output(result_dict: Dict[str, Any], level: str = "standard") -> Dict[str, Any]:
    """Translate entire tool output to specified terminology level."""
    if level == "technical":
        return result_dict
    translated = {}
    field_map = FIELD_MAPPINGS.get(level, {})
    for key, value in result_dict.items():
        new_key = field_map.get(key, key)
        if isinstance(value, dict):
            translated[new_key] = translate_output(value, level)
        elif isinstance(value, str):
            translated[new_key] = translate_term(value, level)
        else:
            translated[new_key] = value
    return translated

def add_terminology_context(result_dict: Dict[str, Any], level: str = "standard") -> Dict[str, Any]:
    """Add explanatory context based on terminology level."""
    result = result_dict.copy()
    if level == "simple":
        result["_explanation"] = "Simplified view for non-experts."
    elif level == "standard":
        result["_explanation"] = "Professional technical analysis terminology."
    else:
        result["_explanation"] = "Full mathematical and hypercomplex notation."
    return result
