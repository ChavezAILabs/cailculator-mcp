"""
Bilateral Collapse Oracle
Universal Ground Truth for CAILculator v2.0

Verified in BilateralCollapse.lean (Lean 4).
Tests the P × Q = 0 AND Q × P = 0 identity at 10^-15 precision.
"""

import numpy as np
from ..hypercomplex import create_hypercomplex

def verify_bilateral_collapse(P_arr: np.ndarray, Q_arr: np.ndarray, precision: float = 1e-15, framework: str = "cayley-dickson", clifford_strategy: str = "direct") -> dict:
    """
    Oracular check for the bilateral zero divisor property.
    
    Verified Theorem (BilateralCollapse.lean):
    (P, Q) is a bilateral zero divisor iff P × Q = 0 and Q × P = 0.
    
    Args:
        P_arr: First hypercomplex element as array
        Q_arr: Second hypercomplex element as array
        precision: Required zero-approximation (default 10^-15)
        framework: 'cayley-dickson' or 'clifford'
        clifford_strategy: Mapping strategy for 16D 'clifford' framework ('direct' or 'bivector_pure')
        
    Returns:
        Result dictionary with status and norms
    """
    dim = len(P_arr)
    if len(Q_arr) != dim:
        raise ValueError(f"Dimension mismatch: P is {dim}D, Q is {len(Q_arr)}D")
        
    if framework == "clifford" and dim == 16:
        from .clifford_element import map_sedenion_to_clifford
        P = map_sedenion_to_clifford(P_arr, strategy=clifford_strategy)
        Q = map_sedenion_to_clifford(Q_arr, strategy=clifford_strategy)
    else:
        P = create_hypercomplex(dim, P_arr.tolist(), framework=framework)
        Q = create_hypercomplex(dim, Q_arr.tolist(), framework=framework)
    
    # Check products in both directions (Bilateral property)
    PQ = P * Q
    QP = Q * P
    
    norm_PQ = abs(PQ)
    norm_QP = abs(QP)
    
    is_zero_PQ = norm_PQ < precision
    is_zero_QP = norm_QP < precision
    
    return {
        "is_bilateral_zero_divisor": bool(is_zero_PQ and is_zero_QP),
        "PQ_norm": float(norm_PQ),
        "QP_norm": float(norm_QP),
        "is_zero_PQ": bool(is_zero_PQ),
        "is_zero_QP": bool(is_zero_QP),
        "dimension": dim,
        "precision": precision
    }
