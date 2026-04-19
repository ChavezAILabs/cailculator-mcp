"""
Journalism Terminology Translation
Domain Projection Layer for CAILculator v2.0

Translates mathematical concepts into "Newsroom English" for investigative reporters.
Leverages 30+ years of reporting experience.
"""

from typing import Dict, Any

# Core terminology mappings - Journalism Domain
JOURNALISM_GLOSSARY = {
    "bilateral_zeros": {
        "technical": "Bilateral zero divisor structural detection",
        "standard": "Tipping Point",
        "simple": "Systemic Breakdown Warning",
        "description": "A sudden mathematical cancellation that precedes a major structural breakdown, like a consensus shift, budget collapse, or policy failure."
    },
    "conjugation_symmetry": {
        "technical": "Conjugation symmetry (E8-related mirror invariance)",
        "standard": "Pattern Consistency",
        "simple": "Narrative Alignment",
        "description": "How strongly the current data aligns with historical averages or established institutional patterns."
    },
    "transform_convergence": {
        "technical": "Chavez Transform L² convergence",
        "standard": "Sourcing Confidence",
        "simple": "Data Reliability",
        "description": "A measure of how robust the mathematical signal is against noise, missing data, or 'dirty' public records."
    },
    "dimensional_persistence": {
        "technical": "Cross-dimensional pattern stability",
        "standard": "Cross-Jurisdictional Stability",
        "simple": "Widespread Pattern",
        "description": "Indicates if a pattern found in city data remains identical when tested against state or federal levels."
    }
}

FIELD_MAPPINGS = {
    "standard": {
        "bilateral_zeros": "tipping_point",
        "conjugation_symmetry": "pattern_consistency",
        "transform_convergence": "sourcing_confidence",
        "dimensional_persistence": "cross_jurisdictional_stability"
    },
    "simple": {
        "bilateral_zeros": "breakdown_risk",
        "conjugation_symmetry": "narrative_match",
        "transform_convergence": "data_reliability",
        "dimensional_persistence": "universal_pattern"
    }
}

def translate_term(term: str, level: str = "standard") -> str:
    """Translate a single technical term to newsroom level."""
    if level == "technical":
        return term
    term_lower = term.lower().replace(" ", "_")
    if term_lower in JOURNALISM_GLOSSARY:
        return JOURNALISM_GLOSSARY[term_lower].get(level, term)
    return term

def translate_output(result_dict: Dict[str, Any], level: str = "standard") -> Dict[str, Any]:
    """Translate investigative report to reporter-friendly language."""
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
