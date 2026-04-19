"""
Integration Tests for CAILculator v2.0 Engine
Includes AIEX-506 stability regression guard.
"""

import numpy as np
import math
import pytest
import sys
import os

# Ensure we can import from the staging package
sys.path.append(os.path.join(os.getcwd(), 'src'))

from cailculator_v2.core.chavez_transform import ChavezTransform
from cailculator_v2.core.canonical_six import get_canonical_six
from cailculator_v2.core.stability import get_stability_constant

# Test 5 — AIEX-506 regression guard (critical)
def test_stability_bound_holds_across_alpha_regime():
    """
    Regression guard for AIEX-506. 
    v1.4.7 violated this at α=1.0 and α=5.0.
    v2.0 must hold the bound: |C[f]| <= M * ||f||1
    """
    P, Q = get_canonical_six(16)[1]

    def gaussian(x):
        # x is a numpy array (1D for this test)
        return np.exp(-x[0]**2)

    # L1 norm of exp(-x^2) over (-inf, inf) is sqrt(pi)
    # Our integration domain is finite (-5, 5), but sqrt(pi) is a safe upper bound
    L1_norm_gaussian = math.sqrt(math.pi) 

    # Test across the regime where v1.4.7 failed
    for alpha in [0.1, 1.0, 5.0]:
        ct = ChavezTransform(dimension=16, alpha=alpha)
        
        # Compute transform in 1D
        result = ct.transform_1d(gaussian, P, Q, d=1, domain=(-5.0, 5.0))
        
        transform_magnitude = abs(result["value"])
        M = get_stability_constant(P, Q, alpha)
        bound = M * L1_norm_gaussian
        
        print(f"\nAlpha={alpha}:")
        print(f"  Transform Magnitude: {transform_magnitude:.6e}")
        print(f"  Stability Bound (M*L1): {bound:.6e}")
        print(f"  Ratio: {transform_magnitude/bound:.2%}")
        
        # The key assertion
        assert transform_magnitude <= (bound + 1e-12), (
            f"AIEX-506 violation at alpha={alpha}: "
            f"transform={transform_magnitude:.6e}, bound={bound:.6e}"
        )
        
        # Verify internal core flag also agrees
        assert result["stability_bound"]["satisfied"]

if __name__ == "__main__":
    # If run directly, execute the test
    test_stability_bound_holds_across_alpha_regime()
