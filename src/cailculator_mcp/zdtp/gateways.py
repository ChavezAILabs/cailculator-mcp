"""
ZDTP Gateways - CAILculator v2.0 Staging
Structural Pathway Definitions grounded in Verified Core
"""

from typing import Dict, Any, Tuple
import numpy as np

# v2.0 Core Import
from ..core.canonical_six import get_canonical_six, get_pattern_metadata

def get_gateway_pair(pattern_id: int, dimension: int = 32) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns the verified (P, Q) pair from the core.
    """
    six = get_canonical_six(dimension)
    if pattern_id not in six:
        raise ValueError(f"Invalid pattern_id: {pattern_id}")
    return six[pattern_id]

def get_structural_info(pattern_id: int) -> Dict[str, Any]:
    """Returns structural information about the gateway."""
    meta = get_pattern_metadata(pattern_id)
    return {
        "id": pattern_id,
        "structural_id": f"P{pattern_id}_Q{pattern_id}",
        "formula": meta["formula"],
        "verification": meta["verification_source"]
    }

def list_gateways() -> Dict[int, Dict[str, Any]]:
    """Lists available structural pathways."""
    return {i: get_structural_info(i) for i in range(1, 7)}
