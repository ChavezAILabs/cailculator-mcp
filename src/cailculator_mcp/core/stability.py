"""
Stability Constants - Lean-Proved Bounds
Universal Ground Truth for CAILculator v2.0

Verified in ChavezTransform_genuine.lean (April 2026).
Bound: |C[f]| <= M * ||f||_1
where M = 2*(||P||^2 + ||Q||^2) / (alpha * exp(1))
"""

import numpy as np
import math

def get_stability_constant(P: np.ndarray, Q: np.ndarray, alpha: float) -> float:
    """
    Computes the formally verified stability constant M.
    
    Verified in ChavezTransform_genuine.lean (Theorem 2).
    Axiom footprint: [propext, Classical.choice, Quot.sound]
    
    Args:
        P: First sedenion/pathion of zero divisor pair (array)
        Q: Second sedenion/pathion of zero divisor pair (array)
        alpha: Gaussian decay parameter (alpha > 0)
        
    Returns:
        High-precision stability constant M
    """
    if alpha <= 0:
        raise ValueError(f"alpha must be positive, got {alpha}")
        
    p_norm_sq = np.sum(P**2)
    q_norm_sq = np.sum(Q**2)
    
    # M = 2*(||P||^2 + ||Q||^2) / (alpha * e)
    M = 2.0 * (p_norm_sq + q_norm_sq) / (alpha * math.e)
    
    return float(M)

def verify_bound(transform_value: float, f_l1_norm: float, M: float) -> bool:
    """
    Checks if a transform value satisfies the stability bound.
    
    Returns:
        True if |C[f]| <= M * ||f||_1 (within machine precision)
    """
    bound = M * f_l1_norm
    # Use small epsilon for machine precision safety, though Lean proof is exact.
    return abs(transform_value) <= (bound + 1e-15)
