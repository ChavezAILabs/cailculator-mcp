"""
Acceptance Tests for stability_constant Oracle Tool
Target: core/stability.py
Verified in ChavezTransform_genuine.lean (Theorem 2)
"""

import numpy as np
import math
import pytest
import sys
import os

# Ensure we can import from the staging package
sys.path.append(os.path.join(os.getcwd(), 'src'))

from cailculator_v2.core.stability import get_stability_constant, verify_bound
from cailculator_v2.core.canonical_six import get_canonical_six

# Test 1 — Exact formula verification
def test_stability_constant_exact_formula():
    """Foundational test: Function must return exactly 2*(||P||² + ||Q||²) / (alpha * e)"""
    P = np.array([1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    Q = np.array([0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    alpha = 1.0
    # ||P||^2 = 1^2 + 2^2 = 5
    # ||Q||^2 = 3^2 = 9
    expected = 2.0 * (5.0 + 9.0) / (alpha * math.e)  # = 28/e
    result = get_stability_constant(P, Q, alpha)
    assert abs(result - expected) < 1e-15

# Test 2 — Canonical Six reduction to 8/(alpha*e)
def test_canonical_six_stability_reduces_to_8_over_alpha_e():
    """Verified: Canonical Six pairs live on E8 first shell (norm^2 = 2)"""
    canonical = get_canonical_six(dimension=16)
    alpha = 1.0
    expected = 8.0 / (alpha * math.e) # 2*(2+2)/(alpha*e)
    
    for i, (P, Q) in canonical.items():
        result = get_stability_constant(P, Q, alpha)
        p_norm_sq = np.dot(P, P)
        q_norm_sq = np.dot(Q, Q)
        
        assert abs(p_norm_sq - 2.0) < 1e-15, f"Pattern {i}: P norm_sq expected 2, got {p_norm_sq}"
        assert abs(q_norm_sq - 2.0) < 1e-15, f"Pattern {i}: Q norm_sq expected 2, got {q_norm_sq}"
        assert abs(result - expected) < 1e-15, f"Pattern {i}: got {result}, expected {expected}"

# Test 3 — Non-triviality
def test_stability_constant_non_triviality():
    """Guards against vacuous-Lean-integration (constant must scale with norm^2)"""
    P_small = np.zeros(16); P_small[0] = 1.0
    P_large = np.zeros(16); P_large[0] = 10.0
    Q = np.zeros(16); Q[1] = 1.0
    alpha = 1.0

    s_small = get_stability_constant(P_small, Q, alpha)
    s_large = get_stability_constant(P_large, Q, alpha)
    
    assert s_large > s_small, "Stability constant must scale with ||P||^2"
    # Ratio: (100 + 1) / (1 + 1) = 101/2 = 50.5
    assert s_large / s_small == pytest.approx(50.5, rel=1e-14)

# Test 4 — Alpha scaling
def test_stability_constant_alpha_scaling():
    """Stability constant must be inversely proportional to alpha"""
    P, Q = get_canonical_six(16)[1]
    s_alpha1 = get_stability_constant(P, Q, 1.0)
    s_alpha2 = get_stability_constant(P, Q, 2.0)
    s_alpha10 = get_stability_constant(P, Q, 10.0)

    assert s_alpha2 == pytest.approx(s_alpha1 / 2.0, rel=1e-14)
    assert s_alpha10 == pytest.approx(s_alpha1 / 10.0, rel=1e-14)

# Test 6 — Unconditional validity (AIEX-479)
def test_stability_holds_without_zero_divisor_condition():
    """Stability holds for ANY P and Q, not just zero divisors"""
    np.random.seed(42)
    P = np.random.randn(16)
    Q = np.random.randn(16)
    alpha = 1.0

    s = get_stability_constant(P, Q, alpha)
    assert s > 0
    assert math.isfinite(s)
    
    # verify_bound should work even for random noise
    # |val| <= M * ||f||1
    assert verify_bound(10.0, 100.0, s) # 10 <= s * 100 (s is large for random norms)

# Test 7 — Input validation
def test_stability_constant_input_validation():
    """Rejects malformed input at the boundary (AIEX-507)"""
    P = np.zeros(16); P[0] = 1.0
    Q = np.zeros(16); Q[1] = 1.0

    with pytest.raises(ValueError, match="alpha must be positive"):
        get_stability_constant(P, Q, 0.0)
    with pytest.raises(ValueError, match="alpha must be positive"):
        get_stability_constant(P, Q, -1.0)
    
    # Dimension validation can be added here if we enforce strict 16/32/etc lengths in get_stability_constant
    # Currently it takes any numpy array. Let's add dimension validation if required.
