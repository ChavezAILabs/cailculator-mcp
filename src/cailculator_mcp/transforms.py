"""
Chavez Transform - CAILculator v2.0 Staging
High-Precision Universal Numerical Engine

Refactored to use the v2.0 Core and Profile System.
Maintains 10^-15 machine precision standard.
"""

import numpy as np
from scipy import integrate
from typing import Callable, Tuple, List, Optional, Dict, Any
import sys
import os

# v2.0 Core Imports
from .core.chavez_transform import ChavezTransform as CoreChavezTransform
from .core.canonical_six import get_canonical_six, get_pattern_metadata
from .core.stability import get_stability_constant

class ChavezTransform:
    """
    Wrapper for v2.0 Chavez Transform Core.
    Orchestrates high-precision numerical operations.
    """

    def __init__(self, dimension: int = 32, alpha: float = 1.0):
        self.core = CoreChavezTransform(dimension=dimension, alpha=alpha)
        self.dimension = dimension
        self.alpha = alpha

    def transform_1d(self, f: Callable, P: Any, Q: Any, d: int,
                     domain: Tuple[float, float] = (-5.0, 5.0)) -> float:
        """Computes 1D transform with core validation."""
        P_arr = _to_array(P, self.dimension)
        Q_arr = _to_array(Q, self.dimension)
        result = self.core.transform_1d(f, P_arr, Q_arr, d, domain)
        return result["value"]

    def transform_nd(self, f: Callable, P: Any, Q: Any, d: int,
                     domain_ranges: List[Tuple[float, float]],
                     num_samples: int = 10000) -> float:
        """Computes n-D transform with core validation."""
        P_arr = _to_array(P, self.dimension)
        Q_arr = _to_array(Q, self.dimension)
        result = self.core.transform_nd(f, P_arr, Q_arr, d, domain_ranges, num_samples)
        return result["value"]

    def canonical_six_analysis(self, f: Callable, d: int,
                              domain: Tuple[float, float] = (-5.0, 5.0)) -> dict:
        """Full analysis across all 6 verified patterns."""
        six_pairs = get_canonical_six(self.dimension)
        results = {}
        for pid, (P_arr, Q_arr) in six_pairs.items():
            val = self.transform_1d(f, P_arr, Q_arr, d, domain)
            results[f'locus_{pid}'] = val

        values = [results[f'locus_{i}'] for i in range(1, 7)]
        results['dominant_locus'] = max(range(1, 7), key=lambda i: abs(results[f'locus_{i}']))
        results['mean_response'] = np.mean(values)
        results['std_response'] = np.std(values)
        results['dimension'] = self.dimension
        return results

def create_canonical_six_pattern(pattern_id: int, dimension: int = 32) -> Tuple[np.ndarray, np.ndarray]:
    """Retrieves verified pattern from core."""
    six = get_canonical_six(dimension)
    if pattern_id not in six:
        raise ValueError(f"Invalid pattern_id: {pattern_id}")
    return six[pattern_id]

def _to_array(val: Any, dimension: int) -> np.ndarray:
    """Helper to ensure input is a numpy array of correct dimension."""
    if hasattr(val, 'coeffs'):
        return np.array(val.coeffs)
    arr = np.array(val)
    if arr.ndim == 0:
        res = np.zeros(dimension)
        res[0] = float(arr)
        return res
    return arr

def stability_constant(P: Any, Q: Any, alpha: float) -> float:
    """Proved constant M from core."""
    P_arr = np.array(P.coeffs) if hasattr(P, 'coeffs') else np.array(P)
    Q_arr = np.array(Q.coeffs) if hasattr(Q, 'coeffs') else np.array(Q)
    return get_stability_constant(P_arr, Q_arr, alpha)
