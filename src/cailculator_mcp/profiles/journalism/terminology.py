"""
Journalism Terminology
Domain Projection Layer for CAILculator v2.0

Profile 3.0.0: output keys and values are passed through unchanged at every
terminology level. The earlier newsroom renames ("Tipping Point", "Systemic
Breakdown Warning", "Sourcing Confidence", ...) asserted conclusions no test
supports and were removed; see CHANGELOG. A reporter reads the same measured
quantities a technical user does.
"""

from typing import Dict, Any

def translate_term(term: str, level: str = "standard") -> str:
    return term

def translate_output(result_dict: Dict[str, Any], level: str = "standard") -> Dict[str, Any]:
    return result_dict
