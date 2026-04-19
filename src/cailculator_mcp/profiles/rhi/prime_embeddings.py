"""
RHI Prime Embeddings
Domain Projection Layer for CAILculator v2.0

Verified in RHForcingArgument.lean (Phase 61/63).
Maps spectral parameter t to 16D sedenion vectors via prime logarithms.
"""

import numpy as np

def get_two_prime_surrogate(t: float) -> np.ndarray:
    """
    Computes the Two-Prime Surrogate sedenion vector F_base(t).
    
    Formula (RHForcingArgument.lean):
    F_base(t) = cos(t·log 2)·(e₀+e₁₅) + sin(t·log 2)·(e₃+e₁₂) + sin(t·log 3)·(e₆+e₉)
    
    Args:
        t: Spectral parameter (often Im(s))
        
    Returns:
        16D sedenion coefficients as numpy array
    """
    f_base = np.zeros(16, dtype=np.float64)
    
    log2 = np.log(2.0)
    log3 = np.log(3.0)
    
    # cos(t * log 2) * (e0 + e15)
    cos_val = np.cos(t * log2)
    f_base[0] = cos_val
    f_base[15] = cos_val
    
    # sin(t * log 2) * (e3 + e12)
    sin2_val = np.sin(t * log2)
    f_base[3] = sin2_val
    f_base[12] = sin2_val
    
    # sin(t * log 3) * (e6 + e9)
    sin3_val = np.sin(t * log3)
    f_base[6] = sin3_val
    f_base[9] = sin3_val
    
    return f_base

def get_u_antisym() -> np.ndarray:
    """
    Returns the mirror-antisymmetric tension axis u_antisym.
    
    Formula (RHForcingArgument.lean):
    u = (1/√2)(e₄ − e₅ − e₁₁ + e₁₀)
    """
    u = np.zeros(16, dtype=np.float64)
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    
    u[4] = inv_sqrt2
    u[5] = -inv_sqrt2
    u[11] = -inv_sqrt2
    u[10] = inv_sqrt2
    
    return u

def get_parametric_lift(t: float, sigma: float) -> np.ndarray:
    """
    Computes the full parametric lift F(t, σ).
    
    Formula: F(t, σ) = F_base(t) + (σ - 0.5) * u_antisym
    """
    f_base = get_two_prime_surrogate(t)
    u = get_u_antisym()
    
    return f_base + (sigma - 0.5) * u
