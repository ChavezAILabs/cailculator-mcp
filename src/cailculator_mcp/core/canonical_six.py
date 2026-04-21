"""
Canonical Six - Lean-Proved Bilateral Zero Divisor Patterns
Universal Ground Truth for CAILculator v2.0

These patterns are formally verified in BilateralCollapse.lean (Lean 4).
They satisfy P × Q = 0 AND Q × P = 0 to machine precision (10^-15).
"""

import numpy as np
from typing import Dict, Tuple

# Canonical Six bilateral pairs: ((P_idx_a, P_idx_b, P_sign), (Q_idx_c, Q_idx_d, Q_sign))
# P = e_a + sign_P * e_b,  Q = e_c + sign_Q * e_d
# Verified in BilateralCollapse.lean (April 2026)
_CANONICAL_SIX_DEFINITIONS = {
    1: ((1, 14, 1), (3, 12, 1)),   # P=(e_1+e_14), Q=(e_3+e_12)
    2: ((3, 12, 1), (5, 10, 1)),   # P=(e_3+e_12), Q=(e_5+e_10)
    3: ((4, 11, 1), (6,  9, 1)),   # P=(e_4+e_11), Q=(e_6+e_9)
    4: ((1, 14, -1), (3, 12, -1)), # P=(e_1-e_14), Q=(e_3-e_12)
    5: ((1, 14, -1), (5, 10, 1)),  # P=(e_1-e_14), Q=(e_5+e_10)
    6: ((2, 13, -1), (6,  9, 1)),  # P=(e_2-e_13), Q=(e_6+e_9)
}

def get_canonical_six(dimension: int = 32) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
    """
    Returns the verified 6 (P,Q) pairs as high-precision numpy arrays.
    
    Args:
        dimension: The algebra dimension (default 32 for pathions).
        
    Returns:
        Dictionary mapping pattern_id (1-6) to (P, Q) array tuples.
    """
    if dimension < 16:
        raise ValueError(f"Bilateral zero divisors require at least 16D (Sedenions), got {dimension}D")
        
    six_pairs = {}
    for pid, defs in _CANONICAL_SIX_DEFINITIONS.items():
        (pa, pb, ps), (qc, qd, qs) = defs
        
        p_arr = np.zeros(dimension, dtype=np.float64)
        p_arr[pa] = 1.0
        p_arr[pb] = float(ps)
        
        q_arr = np.zeros(dimension, dtype=np.float64)
        q_arr[qc] = 1.0
        q_arr[qd] = float(qs)
        
        six_pairs[pid] = (p_arr, q_arr)
        
    return six_pairs

def get_pattern_metadata(pattern_id: int) -> Dict:
    """Returns metadata for a specific pattern ID."""
    if pattern_id not in _CANONICAL_SIX_DEFINITIONS:
        raise ValueError(f"Invalid pattern_id: {pattern_id}. Must be 1-6.")
        
    (pa, pb, ps), (qc, qd, qs) = _CANONICAL_SIX_DEFINITIONS[pattern_id]
    
    ps_str = "+" if ps == 1 else "-"
    qs_str = "+" if qs == 1 else "-"
    
    return {
        "pattern_id": pattern_id,
        "formula": f"(e_{pa} {ps_str} e_{pb}) × (e_{qc} {qs_str} e_{qd}) = 0",
        "P_expression": f"e_{pa} {ps_str} e_{pb}",
        "Q_expression": f"e_{qc} {qs_str} e_{qd}",
        "P_vector_indices": [pa, pb],
        "Q_vector_indices": [qc, qd],
        "is_bilateral": True,
        "verification_source": "BilateralCollapse.lean"
    }
