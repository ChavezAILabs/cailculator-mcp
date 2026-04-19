# Test Specification: `stability_constant(P, Q, alpha)` Oracle Tool

**Target:** `core/stability.py` in CAILculator v2.0
**Lean anchor:** `chavez_transform_stability` in `ChavezTransform_genuine.lean`
**KSJ reference:** AIEX-484 (April 17, 2026) — callable CAILculator API function
**Handoff reference:** `CAILculatorV2_Final_Handoff.md` §11.1 item 2, §11.3

---

## 1. Scope

This document specifies the acceptance test suite for the `stability_constant` oracle tool introduced in the CAILculator v2.0 architecture plan. The tool implements the Lean-proved stability bound:

$$\text{stability\_constant}(P, Q, \alpha) = \frac{2 \cdot (\|P\|^2 + \|Q\|^2)}{\alpha \cdot e}$$

For the Canonical Six specifically, $\|P\|^2 = \|Q\|^2 = 2$ (E8 first shell), so the formula reduces to $8/(\alpha \cdot e)$.

This is the function that grounds the AIEX-506 regression guard — the v1.4.7 stability violation (bound held at α=0.1 but violated at α=1.0 by 47.3% and at α=5.0). The test suite must make that failure mode structurally impossible in v2.0.

---

## 2. Test Suite

Tests are ordered from most critical (must pass for the oracle tool to be trusted) to most valuable (catches the specific failure modes v1.4.7 exhibited). All tests assume double precision (tolerance $10^{-15}$ per Gemini's high-precision standard).

### Test 1 — Exact formula verification

The function must return exactly $2 \cdot (\|P\|^2 + \|Q\|^2) / (\alpha \cdot e)$ to double precision. This is the foundational test; anything else is a bug.

```python
def test_stability_constant_exact_formula():
    import math
    P = np.array([1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    Q = np.array([0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    alpha = 1.0
    expected = 2.0 * (5.0 + 9.0) / (alpha * math.e)  # = 28/e
    assert abs(stability_constant(P, Q, alpha) - expected) < 1e-15
```

### Test 2 — Canonical Six reduction to 8/(α·e)

Per AIEX-484, for any Canonical Six pair the formula collapses to $8/(\alpha \cdot e)$ because $\|P\|^2 = \|Q\|^2 = 2$ (E8 first shell). This verifies both the formula *and* that the canonical pairs loaded from the Lean source of truth have the expected E8 norms. Catches formula bugs and canonical-pair mis-loading simultaneously.

```python
def test_canonical_six_stability_reduces_to_8_over_alpha_e():
    import math
    canonical = get_canonical_six()  # from core/canonical_six.py
    alpha = 1.0
    expected = 8.0 / (alpha * math.e)
    for i, (P, Q) in canonical.items():
        result = stability_constant(P, Q, alpha)
        assert abs(result - expected) < 1e-15, (
            f"Pattern {i}: got {result}, expected {expected}. "
            f"‖P‖²={np.dot(P,P)}, ‖Q‖²={np.dot(Q,Q)} "
            f"(both should be 2 on E8 first shell)"
        )
```

### Test 3 — Non-triviality

Per v2.0 handoff §11.3: every oracle tool must prove it can return meaningfully distinct values. Guards against the vacuous-Lean-integration failure mode (AIEX-441, AIEX-482 — `ChavezTransform_Specification_aristotle.lean` passed `#print axioms` but had `CD4_mul = 0`, rendering all theorems vacuously true).

```python
def test_stability_constant_non_triviality():
    P_small = np.zeros(16); P_small[0] = 1.0
    P_large = np.zeros(16); P_large[0] = 10.0
    Q = np.zeros(16); Q[1] = 1.0
    alpha = 1.0

    s_small = stability_constant(P_small, Q, alpha)
    s_large = stability_constant(P_large, Q, alpha)
    assert s_large > s_small, "Stability constant must scale with ‖P‖²"
    assert s_large / s_small == pytest.approx((100 + 1) / (1 + 1))
```

### Test 4 — Alpha scaling

The function is $\propto 1/\alpha$. Doubling α must halve the constant. This catches off-by-one or squaring bugs in alpha handling — the AIEX-506 class of drift where the Python formula decoupled from the proof.

```python
def test_stability_constant_alpha_scaling():
    P, Q = get_canonical_six()[1]
    s_alpha1 = stability_constant(P, Q, 1.0)
    s_alpha2 = stability_constant(P, Q, 2.0)
    s_alpha10 = stability_constant(P, Q, 10.0)

    assert s_alpha2 == pytest.approx(s_alpha1 / 2.0, rel=1e-14)
    assert s_alpha10 == pytest.approx(s_alpha1 / 10.0, rel=1e-14)
```

### Test 5 — AIEX-506 regression guard (critical)

This is the test the v1.4.7 bug would have failed. The Python `chavez_transform` output must never exceed $\text{stability\_constant}(P, Q, \alpha) \cdot \|f\|_1$ on a baseline Gaussian at $\alpha \in \{0.1, 1.0, 5.0\}$. v1.4.7 held the bound at α=0.1 but violated it at α=1.0 by 47.3% and at α=5.0.

This is the test that must appear explicitly in §11.3 of the architecture plan — the original handoff named the bug class but did not specify the assertion-level test.

```python
def test_stability_bound_holds_across_alpha_regime():
    """Regression guard for AIEX-506. v1.4.7 violated this at α=1.0 and α=5.0."""
    import math
    P, Q = get_canonical_six()[1]

    def gaussian(x):
        return np.exp(-x**2)

    L1_norm_gaussian = math.sqrt(math.pi)  # ∫exp(-x²)dx = √π

    for alpha in [0.1, 1.0, 5.0]:
        bound = stability_constant(P, Q, alpha) * L1_norm_gaussian
        transform_magnitude = abs(chavez_transform(gaussian, P, Q, alpha, d=1))
        assert transform_magnitude <= bound, (
            f"AIEX-506 regression at α={alpha}: "
            f"transform={transform_magnitude}, bound={bound}, "
            f"violation={100*(transform_magnitude/bound - 1):.1f}%"
        )
```

### Test 6 — Unconditional validity (AIEX-479)

Convergence and stability hold for *any* P and Q, not just zero divisor pairs. The bilateral zero divisor condition P·Q=0 is not a hypothesis of the theorem. This test verifies the implementation doesn't silently assume P·Q=0.

```python
def test_stability_holds_without_zero_divisor_condition():
    import math
    # Random P, Q with P·Q ≠ 0
    np.random.seed(42)
    P = np.random.randn(16)
    Q = np.random.randn(16)
    alpha = 1.0

    s = stability_constant(P, Q, alpha)
    assert s > 0
    assert math.isfinite(s)

    def f(x): return np.exp(-x**2)
    bound = s * math.sqrt(math.pi)
    assert abs(chavez_transform(f, P, Q, alpha, d=1)) <= bound
```

### Test 7 — Input validation

α must be positive. P and Q must be length 16 (sedenion dimension). Rejects malformed input at the boundary, per the AIEX-507 lesson about transport-layer validation.

```python
def test_stability_constant_input_validation():
    P = np.zeros(16); P[0] = 1.0
    Q = np.zeros(16); Q[1] = 1.0

    with pytest.raises(ValueError, match="alpha must be positive"):
        stability_constant(P, Q, 0.0)
    with pytest.raises(ValueError, match="alpha must be positive"):
        stability_constant(P, Q, -1.0)
    with pytest.raises(ValueError, match="16"):
        stability_constant(np.zeros(15), Q, 1.0)
    with pytest.raises(ValueError, match="16"):
        stability_constant(P, np.zeros(17), 1.0)
```

---

## 3. What the suite guarantees

If all seven tests pass, the following invariants hold:

| Test | Guarantee |
|---|---|
| 1 | Formula matches the Lean theorem to double precision |
| 2 | Canonical Six are correctly loaded from the verified source, and their E8 norms hold |
| 3 | Oracle is non-trivial, not vacuous |
| 4 | Alpha handling is correct |
| 5 | The v1.4.7 stability violation cannot reoccur |
| 6 | The theorem's actual hypothesis structure is preserved |
| 7 | Transport-layer malformed input is rejected at the boundary |

---

## 4. Recommended addition at integration time

A property-based fuzz test using Hypothesis, generating random $(P, Q, \alpha)$ triples over a reasonable range and asserting the formula returns exactly $2 \cdot (\|P\|^2 + \|Q\|^2) / (\alpha \cdot e)$ with the transform bound holding.

Hypothesis is particularly good at finding edge cases (very small α, very large norms, NaN/Inf handling) that hand-written tests miss. Worth adding once the tool ships but not required for the initial acceptance suite.

---

## 5. Request for Gemini CLI

Please incorporate **Test 5** (AIEX-506 regression guard) into §11.3 of the CAILculator v2.0 architecture plan as the explicit assertion-level specification for the AIEX-506 bug-class prevention test. The original handoff §11.3 named the bug class but did not specify the test code; this closes that ambiguity.

The remaining tests (1, 2, 3, 4, 6, 7) should be added to the acceptance test appendix for `core/stability.py` as part of the Phase 1 Core Foundation deliverable.

---

*End of test specification.*
