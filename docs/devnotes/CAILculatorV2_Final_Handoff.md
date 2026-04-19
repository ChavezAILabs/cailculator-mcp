# CAILculator v2.0 — Final Architecture Handoff

**From:** Gemini CLI (Planning Mode)
**To:** Implementation Team
**Date:** April 19, 2026
**Status:** v2.0 Final Architecture Plan (Pre-Implementation)

---

## Executive Summary & Core Diagnosis

The CAILculator v2.0 engine overhaul addresses a cluster of v1.4.7 bugs caused by the Python surface drifting from the Lean-verified mathematical core. The guiding principle for v2.0 is: **Verified math survives broken tooling when data flows from the verified core. Data flowing from ad-hoc Python does not.**

### High-Precision Standard
v2.0 maintains a strict double-precision standard ($10^{-15}$) for all algebraic operations, including sedenion multiplication and kernel evaluations. The Lean "Oracle" provides the structural ground truth, while the Python engine executes these verified definitions with maximum hardware precision.

### The AIEX-505 "Dispatch Collapse" Revelation
Recent analysis from Claude Code revealed that the "dispatch collapse" (where all 6 Canonical Six patterns return bit-identical outputs on 1D scalar inputs) is **not a bug, but a verified mathematical theorem**. 

The Lean proof `K_Z_realToSed` establishes that when a scalar $x$ is embedded as $x \cdot e_0$, the kernel $K_Z$ evaluates exactly to $2x^2(\|P\|^2 + \|Q\|^2)$. Since $\|P\|^2 + \|Q\|^2 = 4$ for all Canonical Six patterns, $K_Z \equiv 8x^2$ identically across all six patterns.

**Prerequisite Fix (Option A):** To genuinely differentiate patterns, we must correct the sedenion embedding for multi-dimensional input. Instead of embedding scalars into the $e_0$ channel, $x$ must be embedded into the non-real components ($e_1$–$e_{15}$). This is the mathematically richer path and a strict prerequisite for v2.0 expansion.

---

## 11.1 Architectural Plan

v2.0 adopts **Option 3 (Lean as Oracle Layer)**, transitioning the Python engine to a fast numerical approximation layer governed strictly by Lean-proved theorems.

### Module-Level Dependency Graph
```
cailculator/
├── core/                           # Universal, Lean-anchored Ground Truth
│   ├── chavez_transform.py         # n-D embedding (Option A), uses stability_constant
│   ├── bilateral_collapse.py       # P·Q = 0 checks
│   ├── canonical_six.py            # Lean-proved Canonical Six (P,Q) pairs
│   ├── extended_structures.py      # 24-family generation, G2 invariance, E8 mapping
│   └── stability.py                # 2(||P||² + ||Q||²)/(α·e) bound checks
└── profiles/                       # Domain Projection Layer
    ├── rhi/                        # Riemann Hypothesis Investigation Profile
    │   ├── manifest.json
    │   ├── terminology.py
    │   ├── prime_embeddings.py
    │   └── gateway_labels.py       # Master, Transformation, etc. -> Canonical Six
    └── quant_equity/               # Quantitative Finance Profile
        ├── manifest.json
        ├── terminology.py
        ├── indicators.py
        ├── interpretation.py
        └── coefficient_mapping.py  # OHLCV -> Sedenion components
```

### Oracle Tool Interfaces
1. `verify_bilateral_collapse(P: Array, Q: Array) -> bool`: Runs exact `P·Q = 0` algebraic check.
2. `get_stability_constant(P: Array, Q: Array, alpha: float) -> float`: Returns `2(||P||² + ||Q||²)/(α·e)`.
3. `kernel_distance(x: Array) -> float`: Returns `0.5 * ||[u_antisym, x]||`.
4. `get_canonical_six() -> Dict[int, Tuple[Array, Array]]`: Returns the verified 6 (P,Q) pairs.
5. `map_to_weyl_orbit(v: Array) -> Dict`: Projects vector onto E8 Weyl orbits.
6. `detect_24_family(v: Array) -> List[Dict]`: Identifies membership in the complete 24 bilateral zero-divisor families.

### Interface Contract (`core/` ↔ `profiles/`)
- `core/` accepts ONLY raw arrays (Sedenion/Pathion components) and universal parameters ($\alpha, d$).
- `core/` NEVER accepts semantic strings (e.g., "S1", "bull_market").
- `profiles/` are strictly responsible for mapping domain data (e.g., OHLCV) to mathematical vectors and translating core algebraic outputs back to semantic interpretations.

---

## 11.2 Migration Plan

### Phase 0: Handoff Documentation
1. Save this final architecture handoff document to `C:\Users\chave\PROJECTS\cailculator-mcp\docs\devnotes\CAILculatorV2_Final_Handoff.md`.

### Phase 1: Core Foundation & Embedding Fix
1. Implement `core/canonical_six.py` and `core/stability.py` using Lean-verified constants.
2. **Fix `zero_divisor_kernel`:** Modify the embedding logic so multi-dimensional inputs map to non-real sedenion components ($e_1$-$e_{15}$) instead of $e_0$ to enable actual pattern differentiation.

### Phase 2: Profile System Bootstrapping
1. Scaffold the `profiles/` directory structure.
2. Port existing RHI logic into `profiles/rhi/`.
3. Port `quant_indicators.py` and `terminology.py` into `profiles/quant_equity/`.

### Phase 3: Oracle-Gated Replacement (Module-by-Module)
1. **`transforms.py`**: Rip out heuristic Canonical Six definitions. Route all pair generation through `get_canonical_six()`. Enforce `get_stability_constant()` as a hard clipping bound on outputs.
2. **`patterns.py`**: Deprecate heuristic symmetry scoring. Replace with `detect_24_family()` and `map_to_weyl_orbit()`.
3. **`regime_detection.py`**: Refactor to use the `quant_equity` profile for mappings and interpretation, calling the updated `transforms.py` for structural numerics.

### Deprecation Timeline
- v1.4.7 tools remain available but emit deprecation warnings.
- Data formats (e.g., 16D array inputs) remain compatible, but semantic `pattern_id` arguments will be internally mapped via the active profile.

---

## 11.3 Acceptance Test Specifications

### v1.4.7 Bug Class Prevention
1. **AIEX-505 (Dispatch Collapse):** Test that $n$-D input embedded into non-real components ($e_1$-$e_{15}$) produces distinct transform values across the 6 Canonical patterns. Test that 1D scalar input ($e_0$) produces identical values (verifying `K_Z_realToSed`).
2. **AIEX-506 (Stability Bound):** Fuzz `chavez_transform` with random bounded functions and various $\alpha > 0$. Assert that the output NEVER exceeds `get_stability_constant() * L1_norm(f)`.
   ```python
   def test_stability_bound_holds_across_alpha_regime():
       """Regression guard for AIEX-506. v1.4.7 violated this at α=1.0 and α=5.0."""
       import math
       P, Q = get_canonical_six()[1]
       def gaussian(x): return np.exp(-x**2)
       L1_norm_gaussian = math.sqrt(math.pi)  # ∫exp(-x²)dx = √π
       for alpha in [0.1, 1.0, 5.0]:
           bound = get_stability_constant(P, Q, alpha) * L1_norm_gaussian
           # Transform magnitude must be <= bound
           res = chavez_transform({"data": [1.0]*10, "alpha": alpha}) # Simplified for spec
           assert abs(res["transform_value"]) <= bound
   ```
3. **AIEX-507 (Transport Inflation):** Submit 256-length float arrays to the core boundary. Verify exact length enforcement and rejection of malformed payloads before computation.
4. **AIEX-510 (Timeout/Throughput):** Ensure fast-mode downsampling in profiles executes strictly under 5 seconds.

### Non-Triviality Test Template
To prevent vacuous Lean theorem integration, every oracle tool must pass a non-triviality test:
```python
def test_oracle_non_triviality():
    # Prove the oracle can return False/Zero
    assert not verify_bilateral_collapse(random_array, random_array)
    # Prove the oracle can return True/Non-Zero
    P, Q = get_canonical_six()[1]
    assert verify_bilateral_collapse(P, Q)
```

### CWD-Hardness Test
```python
def test_cwd_independence():
    # Spawn MCP server in C:\WINDOWS\System32
    # Issue tool call to 'illustrate'
    # Assert file is written to correct repo assets/ path, not System32
```

---

## 11.4 Gateway Audit Table

| Profile Label | Original v1.x Label | Canonical (P,Q) Pair | Lean Theorem Anchor | Status / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **S1** | Master Gateway | P1: $(e_1+e_{14})$, Q1: $(e_3+e_{12})$ | `BilateralCollapse.lean` | Verified |
| **S2** | Multi-Modal Gateway | P2: $(e_3+e_{12})$, Q2: $(e_5+e_{10})$ | `BilateralCollapse.lean` | Verified |
| **S3A** | Discontinuous Gateway | P3: $(e_4+e_{11})$, Q3: $(e_6+e_9)$ | `BilateralCollapse.lean` | Verified |
| **S3B** | Conjugate Pair Gateway | P4: $(e_1-e_{14})$, Q4: $(e_3-e_{12})$ | `BilateralCollapse.lean` | Verified |
| **S4** | Linear Gateway | P5: $(e_1-e_{14})$, Q5: $(e_5+e_{10})$ | `BilateralCollapse.lean` (Empirical S3B=S4 equivalence: AIEX-229) | Verified (Flag empirical link) |
| **S5** | Transformation Gateway | P6: $(e_2-e_{13})$, Q6: $(e_6+e_9)$ | `BilateralCollapse.lean` | Verified |

*Note: S3A and S5 share the Q vector $(e_6+e_9)$. This shared-Q dual structure is fully Lean-proved.*

---

## 11.5 RHI Profile Specification

**Path:** `profiles/rhi/`

**Manifest:**
```yaml
{
  "name": "rhi",
  "version": "2.0.0",
  "scope": "Riemann Hypothesis Investigation & Spectral Profiling",
  "used_theorems": ["BilateralCollapse", "ChavezTransform_genuine", "MirrorSymmetry"],
  "empirical_dependencies": [
    {"claim": "S3B=S4 Equivalence", "reference": "AIEX-229"},
    {"claim": "Log-periodic convergence", "reference": "AIEX-231"}
  ]
}
```
**Mappings:**
- **Coefficient Mapping:** Maps prime logarithms ($\log p$) to 16D root vectors.
- **Gateway Labels:** Translates semantic labels (Master, Transformation, Diagonal-A/B) strictly to Canonical 1-6 indices.

---

## 11.6 Quant_Equity Profile Specification

**Path:** `profiles/quant_equity/`

**Manifest:**
```yaml
{
  "name": "quant_equity",
  "version": "2.0.0",
  "scope": "Financial Market Regime Detection",
  "used_theorems": ["ChavezTransform_genuine"],
  "empirical_dependencies": [
    {"claim": "Zero divisors predict volatility clustering", "reference": "v1.x heuristics"}
  ]
}
```
**Mappings:**
- **Coefficient Mapping:** Maps OHLCV (Open, High, Low, Close, Volume) + Volatility to specific sedenion component channels ($e_1$-$e_6$).
- **Interpretation Logic:** Refactors existing `quant_indicators.py` rules (RSI, MACD). Translates "Low Conjugation Symmetry" to "Trending/Volatile Regime". Translates "High Zero Divisor Count" to "High Bifurcation Risk". All translations must include documented evidence references.
