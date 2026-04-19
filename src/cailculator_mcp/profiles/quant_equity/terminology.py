"""
Quant Equity Terminology Translation
Domain Projection Layer for CAILculator v2.0

Maps mathematical concepts to financial/trading language.
Supports three levels: technical, standard, simple.
"""

from typing import Dict, Any

# Core terminology mappings - Finance Domain
# Evidence references (AIEX-###) represent the documented link between math and finance.
FINANCIAL_GLOSSARY = {
    "conjugation_symmetry": {
        "technical": "Conjugation symmetry detection (eigenvalue stability in hypercomplex space)",
        "standard": "Mean reversion strength indicator",
        "simple": "How strongly price returns to average",
        "evidence": "AIEX-231 (Mirror symmetry in prime spectra)"
    },
    "bilateral_zeros": {
        "technical": "Bilateral zero divisor detection in sedenion/pathion algebras",
        "standard": "Volatility regime shift signals",
        "simple": "Major market mood changes",
        "evidence": "AIEX-501 (Zero divisors as structural bifurcation points)"
    },
    "dimensional_persistence": {
        "technical": "Cross-dimensional pattern stability (16D→32D→64D Cayley-Dickson)",
        "standard": "Pattern stability across timeframes",
        "simple": "Patterns that work on multiple chart timeframes (daily, weekly, monthly)"
    },
    "transform_convergence": {
        "technical": "Chavez Transform L² convergence with alpha-parametrized damping",
        "standard": "Analysis confidence score",
        "simple": "How sure we are about the results"
    },
    "chavez_transform": {
        "technical": "Zero-divisor weighted integral transform in pathion space",
        "standard": "Pattern-weighted data analysis",
        "simple": "Smart way to find hidden patterns in data"
    },
    "zero_divisor": {
        "technical": "Non-zero elements P, Q where P×Q = 0 in non-associative algebra",
        "standard": "Structural weakness point in data",
        "simple": "Special relationship where things cancel out"
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
        "conjugation_symmetry": "mean_reversion",
        "bilateral_zeros": "regime_shifts",
        "dimensional_persistence": "timeframe_stability",
        "transform_convergence": "confidence_score",
        "chavez_transform": "pattern_analysis",
        "zero_divisor": "structural_weakness",
    },
    "simple": {
        "conjugation_symmetry": "return_to_average",
        "bilateral_zeros": "mood_changes",
        "dimensional_persistence": "pattern_consistency",
        "transform_convergence": "certainty",
        "chavez_transform": "pattern_finder",
        "zero_divisor": "cancellation_point",
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
