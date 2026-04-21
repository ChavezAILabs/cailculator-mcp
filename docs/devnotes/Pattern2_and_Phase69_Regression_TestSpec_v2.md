# Test Specification: Pattern 2 Structural Audit + Phase 69 ZDTP Regression

**Target:** CAILculator v2.0 production (post-deployment verification)
**Authored:** April 20, 2026
**Context:** Gemini CLI identified Pattern 2 as "Universal Bilateral Anchor" during v2.0 staging — the Canonical Six pattern that holds identically across both Cayley-Dickson and Clifford algebra representations. This specification tests the hypothesis that Pattern 2's cross-framework stability derives from a specific conjugate-symmetry property, and separately verifies that v2.0's verified core reproduces the Phase 69 ZDTP ceiling result from v1.x within double-precision tolerance.

---

## 1. Scope and Rationale

This test suite has two objectives, structured as a single integrated run because both depend on the same v2.0 oracle layer:

**Part A — Pattern 2 structural audit (§3):** Determine *why* Pattern 2 is the cross-framework anchor. Three candidate explanations must be distinguished:
1. Conjugate symmetry purity (Pattern 2 is the only pattern whose P, Q pair is preserved cleanly under sedenion conjugation)
2. Alternative-law restriction (Pattern 2 satisfies alternative laws $(PP)Q = P(PQ)$ that other patterns fail)
3. Clifford pure-grade form (Pattern 2 has a single-grade Clifford bivector representation while others require mixed-grade)

**Part B — Phase 69 ZDTP regression (§4):** Re-run the April 13, 2026 Phase 69 ZDTP computation that established the Riemann zero ZDTP ceiling at 0.9577023861134006 using the v2.0 oracle layer. Verify that v2.0's verified engine reproduces this result to $10^{-15}$ precision — the canonical late-phase RHI benchmark carries forward cleanly into the overhauled architecture.

**Why integrated:** Pattern 2 is hypothesized to be the pattern most responsible for the Riemann-zero bilateral annihilation universality established across all 50 zeros and 6 gateways in Phase 42. If Part A confirms Pattern 2's privileged status and Part B confirms the v2.0 engine reproduces the Phase 69 result, we have two independent angles converging on the same structural claim: Pattern 2 is the anchor of both the cross-framework correspondence *and* the RHI spectral correspondence.

---

## 2. Preconditions

Before running this suite, confirm:

- CAILculator v2.0 installed from PyPI (`pip install cailculator_mcp`)
- Oracle tools visible in Claude Desktop tool permissions: `chavez_transform`, `detect_patterns`, `verify_bilateral_oracle`, `map_e8_orbit`, `list_domain_profiles`, `zdtp_transmit`, `illustrate`
- `verify_bilateral_oracle` precision threshold confirmed at $10^{-15}$
- RHI domain profile loaded (`list_domain_profiles` returns "rhi" as available)
- Canonical Six indexing convention confirmed: Pattern 2 corresponds to $P_2 = e_3 + e_{12}$, $Q_2 = e_5 + e_{10}$ per the gateway audit table in `CAILculatorV2_Final_Handoff.md` §11.4

If indexing differs in production (profile label drift is a known risk), pause the suite and resolve the canonical mapping first — the entire audit is meaningless against a mis-identified Pattern 2.

---

## 3. Part A — Pattern 2 Structural Audit

### Test A.1 — Conjugation purity across all six patterns

**Purpose:** Test the conjugate-symmetry-purity hypothesis. Sedenion conjugation flips sign on non-real components: $\overline{e_0} = e_0$, $\overline{e_k} = -e_k$ for $k \geq 1$. For each Canonical Six pair, compute $\overline{P_i}$ and $\overline{Q_i}$ and classify the relationship to the original pair.

**Procedure:**
```python
def test_conjugation_purity_all_patterns():
    canonical = get_canonical_six()
    conjugation_classes = {}
    for i, (P, Q) in canonical.items():
        P_conj = sedenion_conjugate(P)  # e_0 unchanged, e_1..e_15 negated
        Q_conj = sedenion_conjugate(Q)
        # Classify: does conjugation preserve pair (up to sign) or produce a different pair?
        matches_self = np.allclose(P_conj, -P, atol=1e-15) and np.allclose(Q_conj, -Q, atol=1e-15)
        matches_other_pattern = _find_matching_pattern(P_conj, Q_conj, canonical, i)
        conjugation_classes[i] = {
            "pure_self_conjugate": matches_self,
            "maps_to_other_pattern": matches_other_pattern,
            "P_conj": P_conj.tolist(),
            "Q_conj": Q_conj.tolist()
        }
    return conjugation_classes
```

**Expected result under hypothesis:** Pattern 2 (and possibly a small subset) returns `pure_self_conjugate = True`. The remaining patterns return either `maps_to_other_pattern` with a specific target, or produce a vector outside the Canonical Six.

**Null result interpretation:** If all six patterns conjugate identically (all pure-self or all map-to-other in the same way), conjugation is not what distinguishes Pattern 2 and the anchor mechanism is elsewhere.

### Test A.2 — Alternative law check on all six patterns

**Purpose:** Test the alternative-law hypothesis. Sedenion algebra is non-alternative globally, but specific sub-structures can satisfy alternative laws $(xx)y = x(xy)$ and $y(xx) = (yx)x$ on restricted inputs.

**Procedure:**
```python
def test_alternative_laws_all_patterns():
    canonical = get_canonical_six()
    alternative_results = {}
    for i, (P, Q) in canonical.items():
        # Left alternative: (PP)Q =? P(PQ)
        left_alt_lhs = sedenion_multiply(sedenion_multiply(P, P), Q)
        left_alt_rhs = sedenion_multiply(P, sedenion_multiply(P, Q))
        left_alt_holds = np.allclose(left_alt_lhs, left_alt_rhs, atol=1e-15)

        # Right alternative: Q(PP) =? (QP)P
        right_alt_lhs = sedenion_multiply(Q, sedenion_multiply(P, P))
        right_alt_rhs = sedenion_multiply(sedenion_multiply(Q, P), P)
        right_alt_holds = np.allclose(right_alt_lhs, right_alt_rhs, atol=1e-15)

        alternative_results[i] = {
            "left_alternative": left_alt_holds,
            "right_alternative": right_alt_holds,
            "left_defect_norm": np.linalg.norm(left_alt_lhs - left_alt_rhs),
            "right_defect_norm": np.linalg.norm(right_alt_lhs - right_alt_rhs)
        }
    return alternative_results
```

**Expected result under hypothesis:** Pattern 2 shows `left_alternative = True, right_alternative = True`. Other patterns show at least one failure with non-zero defect norms.

**Null result interpretation:** If all six satisfy alternative laws (unexpected given sedenion non-alternativity, but possible for restricted input pairs), alternativity is a universal property of the Canonical Six, not a Pattern 2 distinguisher. If none satisfy alternative laws, alternativity is ruled out as the anchor mechanism.

### Test A.3 — Clifford representation grade purity

**Purpose:** Test the Clifford pure-grade hypothesis. Prior work established that all 48 bilateral pairs produce pure grade-2 bivectors in Cl(7,0). If Pattern 2 is the cross-framework anchor, it may have a distinguished Clifford representation — e.g., a pure bivector in a lower-dimensional Clifford algebra Cl(4,0) or Cl(5,0), while other patterns require Cl(7,0) or mixed-grade elements.

**Procedure:**
```python
def test_clifford_grade_purity():
    canonical = get_canonical_six()
    clifford_results = {}
    for i, (P, Q) in canonical.items():
        # Map sedenion (P, Q) to Clifford representation
        P_clifford = map_sedenion_to_clifford(P)  # returns multivector in Cl(n,0)
        Q_clifford = map_sedenion_to_clifford(Q)
        # Determine minimum Clifford dimension needed
        min_dim_P = minimum_clifford_dimension(P_clifford)
        min_dim_Q = minimum_clifford_dimension(Q_clifford)
        # Determine grade structure
        grades_P = active_grades(P_clifford)  # which k-vector components are non-zero
        grades_Q = active_grades(Q_clifford)
        pure_grade = (len(grades_P) == 1) and (len(grades_Q) == 1)
        clifford_results[i] = {
            "min_dimension_P": min_dim_P,
            "min_dimension_Q": min_dim_Q,
            "grades_P": grades_P,
            "grades_Q": grades_Q,
            "pure_grade": pure_grade
        }
    return clifford_results
```

**Expected result under hypothesis:** Pattern 2 shows smaller `min_dimension` and purer grade structure than the other five patterns.

**Note:** This test requires a sedenion-to-Clifford mapping function that may not exist in v2.0's oracle layer yet. If unavailable, document this as a deferred test and flag it as a feature request for v2.1. Do not substitute an ad-hoc mapping — that would reintroduce exactly the kind of heuristic drift v2.0 was built to eliminate.

### Test A.4 — Cross-framework identity check

**Purpose:** The defining claim of Pattern 2 as Universal Bilateral Anchor is that it "holds identically across both Cayley-Dickson and Clifford algebras." Verify this claim directly.

**Procedure:**
```python
def test_cross_framework_identity():
    canonical = get_canonical_six()
    framework_results = {}
    for i, (P, Q) in canonical.items():
        # Cayley-Dickson framework
        cd_product = sedenion_multiply(P, Q)
        cd_is_zero = np.allclose(cd_product, np.zeros(16), atol=1e-15)

        # Clifford framework (if mapping available)
        if clifford_mapping_available():
            P_cl = map_sedenion_to_clifford(P)
            Q_cl = map_sedenion_to_clifford(Q)
            cl_product = clifford_multiply(P_cl, Q_cl)
            cl_is_zero = is_clifford_zero(cl_product, atol=1e-15)
        else:
            cl_is_zero = None

        framework_results[i] = {
            "cayley_dickson_PQ_zero": cd_is_zero,
            "clifford_PQ_zero": cl_is_zero,
            "both_frameworks_zero": cd_is_zero and cl_is_zero
        }
    return framework_results
```

**Expected result:** All six patterns satisfy `cayley_dickson_PQ_zero = True` (established theorem). The question is whether all six, or only Pattern 2, satisfy `clifford_PQ_zero = True`. If only Pattern 2 does, the Universal Bilateral Anchor claim is verified as written. If all six do, the "anchor" status of Pattern 2 must rest on a different property (likely A.1 or A.3 above).

---

## 4. Part B — Phase 69 ZDTP Regression

### Test B.1 — Reproduce Phase 69 ZDTP ceiling

**Purpose:** Phase 69 (April 13, 2026) established two canonical values via CAILculator v1.x ZDTP:
- Sophie Germain prime ZDTP convergence: **0.9866936838248778**
- Riemann zero ZDTP ceiling: **0.9577023861134006**
- Difference: a Sophie Germain prime outperforms the Riemann zero ceiling by ~0.0290.

Re-run this computation using v2.0's `zdtp_transmit` oracle tool. If v2.0 reproduces these values within $10^{-15}$, the overhauled engine preserves the RHI benchmark. If values drift, the drift must be characterized before any Phase 69 result is cited under v2.0.

**Procedure:**
```python
def test_phase_69_zdtp_regression():
    # Load Phase 69 source data from the archive (see §7 for file manifest)
    phase_69_archive = load_phase_69_inputs()  # see note below

    v2_results = {}

    # Test B.1.a — SG prime convergence
    sg_prime = phase_69_archive["sophie_germain_prime_input"]
    sg_zdtp = zdtp_transmit(
        input_data=sg_prime,
        profile="rhi",
        bilateral_grounding=True  # v2.0 default
    )
    v2_results["sg_prime_convergence"] = sg_zdtp.convergence_score

    # Test B.1.b — Riemann zero ceiling
    riemann_zeros = phase_69_archive["riemann_zero_set"]  # the 100-zero set used in Phase 69
    riemann_zdtp = zdtp_transmit(
        input_data=riemann_zeros,
        profile="rhi",
        bilateral_grounding=True
    )
    v2_results["riemann_ceiling"] = max(z.convergence_score for z in riemann_zdtp.results)

    # Test B.1.c — Verification assertions
    V1_SG_CONVERGENCE = 0.9866936838248778
    V1_RIEMANN_CEILING = 0.9577023861134006
    TOLERANCE = 1e-15

    assert abs(v2_results["sg_prime_convergence"] - V1_SG_CONVERGENCE) < TOLERANCE, (
        f"SG prime convergence drift: v1={V1_SG_CONVERGENCE}, v2={v2_results['sg_prime_convergence']}, "
        f"Δ={v2_results['sg_prime_convergence'] - V1_SG_CONVERGENCE}"
    )
    assert abs(v2_results["riemann_ceiling"] - V1_RIEMANN_CEILING) < TOLERANCE, (
        f"Riemann ceiling drift: v1={V1_RIEMANN_CEILING}, v2={v2_results['riemann_ceiling']}, "
        f"Δ={v2_results['riemann_ceiling'] - V1_RIEMANN_CEILING}"
    )

    return v2_results
```

**Note on Phase 69 inputs:** Five Phase 69 CAILculator JSON files were generated with raw output values for open science record. These are the authoritative inputs — see §7 "Phase 69 Source Files" for the full manifest with paths, roles, and which file feeds which sub-test.

**Interpretation of results:**

- **Exact match ($10^{-15}$):** v2.0 reproduces v1.x at machine precision. The Phase 69 result carries forward cleanly and can be cited under v2.0 without qualification.
- **Small drift ($10^{-15}$ to $10^{-8}$):** likely due to the Option A embedding change ($e_1$–$e_{15}$ instead of $e_0$). Document the drift, identify its structural source, and determine whether v2.0 or v1.x is closer to the Lean-proved ground truth. One is correct; the other is an artifact.
- **Large drift ($>10^{-8}$):** indicates ZDTP 2.0's bilateral-grounding (§ README "ZDTP 2.0") changes the protocol output meaningfully. Not necessarily wrong — the new protocol is more formally grounded — but all prior Phase 69 citations need re-verification, and the Phase 69 headline value (0.9577023861134006) must be updated or contextualized.

### Test B.2 — Pattern 2 contribution to ZDTP convergence

**Purpose:** If Part A confirms Pattern 2 is structurally privileged, verify that Pattern 2 contributes disproportionately to the ZDTP convergence score in Phase 69 re-runs. This connects Part A (structural) to Part B (spectral) at the level of actual RHI computation.

**Procedure:**
```python
def test_pattern_2_zdtp_contribution():
    phase_69_archive = load_phase_69_inputs()
    riemann_zeros = phase_69_archive["riemann_zero_set"]

    # Transmit through each gateway individually (per-pattern convergence)
    per_pattern_convergence = {}
    for pattern_id in range(1, 7):
        gateway_result = zdtp_transmit(
            input_data=riemann_zeros,
            profile="rhi",
            restrict_to_pattern=pattern_id  # new v2.0 capability
        )
        per_pattern_convergence[pattern_id] = gateway_result.mean_convergence

    # Expected under Pattern 2 anchor hypothesis: Pattern 2 shows highest mean convergence
    # or lowest variance, or some distinguishable statistical signature
    return per_pattern_convergence
```

**Expected result under hypothesis:** Pattern 2 shows a distinguishing statistical property — either highest mean convergence, lowest variance, or tightest correlation with γ. If no single pattern distinguishes itself, Pattern 2's anchor status does not translate to measurable RHI-level convergence differences, which would be an important null result worth capturing.

---

## 5. Integrated Pass / Fail Criteria

The full suite (A.1–A.4 + B.1–B.2) yields one of four outcomes:

| Outcome | Part A | Part B | Interpretation |
|---|---|---|---|
| **Full validation** | One hypothesis (A.1, A.2, or A.3) confirmed; A.4 confirms cross-framework identity holds only for Pattern 2 | B.1 exact match; B.2 shows Pattern 2 distinguishes itself | Pattern 2 as Universal Bilateral Anchor is both structurally and spectrally verified. SYN-page-worthy. |
| **Structural only** | Part A confirms one mechanism | B.1 matches but B.2 shows no Pattern 2 distinction | Pattern 2 is algebraically special but that specialness doesn't propagate to RHI-level convergence. Still a real finding; more limited in scope. |
| **Spectral only** | Part A inconclusive (all patterns indistinguishable) | B.2 shows Pattern 2 distinguishes itself | Pattern 2 is empirically privileged but the mechanism is hidden. Follow-up investigation needed. |
| **Null result** | Part A all patterns identical | B.2 no pattern distinguishes | "Universal Bilateral Anchor" claim in README needs qualification. Audit how the naming was arrived at. |

All four outcomes are valuable — the null result especially, because it corrects potential overclaim in the v2.0 README.

---

## 6. Non-Triviality Guards

Per the v2.0 non-triviality discipline (established during v2.0 rebuild — any test that returns bit-identical outputs across what should be distinct inputs is either vacuous or is hitting a known scalar-input collapse regime):

- **Pattern 2 audit** must return distinguishable outputs across the six patterns or explicitly confirm they are algebraically identical. A result showing "all six patterns pass identically" without an explicit identity proof is a vacuous pass.
- **Phase 69 regression** must return non-zero, non-trivial convergence values. If v2.0 returns 0.0, 1.0, or NaN for either SG prime or Riemann ceiling, the computation is broken, not a pass.
- **Pattern 2 contribution** must show per-pattern variation. If all six patterns return bit-identical convergence scores, the test is probing in a regime where the real-to-sedenion embedding (K_Z_realToSed) collapses the signal — adjust inputs (non-scalar, asymmetric, aligned with the Option A embedding) until genuine differentiation appears.

**Advance warning from Phase 69 data itself.** The Phase 69 source files document this collapse directly: `RH_Phase69_zdtp_ceiling_invariance.json` and `RH_Phase69_block_replication_16D.json` both record `pattern_variance = 0.0` — all six Canonical Six patterns return bit-identical transform values on 1D real-valued Riemann-zero and SG-prime input at 16D. The `block_replication_16D.json` interpretation field cross-references Phase 7 (March 8, 2026) and states explicitly: *"Pattern differentiation requires multi-channel or complex-valued input."* Therefore B.2 (per-pattern ZDTP contribution) and Test A.4 on scalar inputs are expected to hit the scalar-input collapse regime as-specified. The test operator must feed B.2 a multi-channel or complex-valued construction (e.g., the sigma-variation commutator surrogate from `RH_Phase69_sigma_variation.json`, or the FLT-structured 16D vector from `RH_Phase69_sophie_germain_tribute.json` §flt_canonical_six_pattern1) rather than the raw 1D zero/prime list, or else record a vacuous pass and flag the input regime as out-of-scope for pattern differentiation.

---

## 7. Phase 69 Source Files

The five Phase 69 CAILculator JSON output files are the authoritative inputs for Part B. They are all present in the RHI results directory:

**Base path:** `C:\dev\projects\Experiments_January_2026\Primes_2026\CAIL-rh-investigation\results\`

| # | File | Role in this suite |
|---|---|---|
| 1 | `RH_Phase69_sophie_germain_tribute.json` | **Primary B.1 input.** Contains `runs.sg_primes_zdtp_full_cascade.convergence.score = 0.9866936838248778` (SG prime ZDTP convergence target) and `headline_comparison.riemann_zero_zdtp_ceiling = 0.9577023861134006` (Riemann ceiling target). The `runs.sg_primes_zdtp_full_cascade.input_16d` field is the exact 16D SG-prime input vector to re-run through `zdtp_transmit`. |
| 2 | `RH_Phase69_zdtp_ceiling_invariance.json` | **Pattern-invariance ground truth for A.1/A.2/A.4 cross-check.** Records that all 6 Canonical Six patterns return identical `transform_value = 7.589096137228364` at alpha=0.9577 on the first 6 Riemann zeros (`pattern_variance = 0.0`). Use to verify the v2.0 oracle reproduces Block Replication on the same input. |
| 3 | `RH_Phase69_block_replication_16D.json` | **Expanded Block Replication reference for B.1.** First 20 Riemann zeros at alpha=1.0, all 6 patterns identical at `transform_value = 55.262546653260316`. Use as the secondary regression target alongside file 1. Also documents the scalar-input collapse regime (`pattern_variance = 0.0`) that §6 flags. |
| 4 | `RH_Phase69_sigma_variation.json` | **Non-scalar input source for B.2.** The 5 commutator-surrogate vectors at sigma ∈ {0.5, 0.52, 0.6, 0.8, 1.0} are the antisymmetric 16D inputs that break the 1D scalar collapse and allow genuine per-pattern differentiation. Feed these into B.2 in place of the raw Riemann-zero list. |
| 5 | `RH_Phase69_bilateral_zero_phase_transition.json` | **Phase-transition corroboration for A.1/A.4.** Records `detect_patterns` behavior at the critical line (sigma=0.5) vs off-critical (sigma=0.6): 0 bilateral-zero pairs at critical, 24 off-critical. Use to verify the Clifford-framework side of A.4 is reading the same phase transition. |

**Access requirement for Gemini CLI:** All five paths must be readable. If any file is missing, mark B.1 as not runnable and halt — do not reconstruct inputs from narrative text.

**Canonical regression constants (extracted from file 1 above):**

```
V1_SG_CONVERGENCE   = 0.9866936838248778   # runs.sg_primes_zdtp_full_cascade.convergence.score
V1_RIEMANN_CEILING  = 0.9577023861134006   # headline_comparison.riemann_zero_zdtp_ceiling
V1_DELTA            = 0.028993282324377198 # headline_comparison.delta
TOLERANCE           = 1e-15
```

**Canonical regression input vectors (also from file 1 and file 3):**

```python
SG_PRIMES_16D     = [2, 3, 5, 11, 23, 29, 41, 53, 83, 89, 113, 131, 173, 179, 191, 233]
RIEMANN_ZEROS_6   = [14.134725, 21.02204, 25.010858, 30.424876, 32.935062, 37.586178]
RIEMANN_ZEROS_20  = [14.134725, 21.02204, 25.010858, 30.424876, 32.935062, 37.586178,
                     40.918719, 43.327073, 48.005151, 49.773832, 52.970321, 56.446248,
                     59.347044, 60.831779, 65.112544, 67.079811, 69.546402, 72.067158,
                     75.704691, 77.14484]
```

---

## 8. Output Artifacts

On completion, produce:

1. **JSON result archive** — full output of A.1, A.2, A.3, A.4, B.1, B.2 with all numerical values preserved. File this alongside the Phase 69 archive for open science traceability.
2. **Outcome classification** — which of the four §5 outcomes obtained.
3. **Drift report (if any)** from B.1 — structural source, magnitude, which version reflects Lean-proved ground truth.
4. **KSJ extraction input** — a session_text block summarizing findings, ready for `extract_insights` with suggested tags and connections.

---

## 9. Planning Notes for Gemini CLI

- Tests A.3 (Clifford grade purity) and A.4 (cross-framework identity) require a sedenion-to-Clifford mapping that may not exist in v2.0's public oracle layer. If not present, mark these tests as deferred v2.1 features rather than silently skipping.
- Test B.2 requires a `restrict_to_pattern` parameter on `zdtp_transmit` that may need to be added to the oracle tool. If the parameter doesn't exist, this test should be flagged as requiring a v2.0.1 patch rather than stubbed out.
- Phase 69 inputs must be loaded from the authoritative JSON archive listed in §7, not reconstructed from narrative text. All five files listed in §7 must be verified present on disk before running B.1.
- The expected precision is $10^{-15}$ per the v2.0 standard. Any looser tolerance must be justified in the test output.

---

## 10. References

- **CAILculatorV2_Final_Handoff.md §11.4** — Gateway audit table with canonical (P,Q) pair assignments
- **README.md (v2.0)** — Pattern 2 as "Universal Bilateral Anchor" claim
- **Phase 7 (March 8, 2026)** — Block Replication Theorem: all 6 patterns identical on 1D real input; pattern differentiation requires multi-channel or complex-valued input
- **Phase 42 (March 28–29, 2026)** — Universal bilateral annihilation across all 50 Riemann zeros and 6 gateways ("The First Ascent" close)
- **Phase 69 (April 13, 2026)** — Headline comparison: SG prime ZDTP convergence 0.9866936838248778 vs Riemann zero ZDTP ceiling 0.9577023861134006; delta 0.0290 in favor of SG primes (Sophie Germain 250th birthday tribute). See §7 for the five source JSON files.

---

*End of test specification. Hand to Gemini CLI for execution against CAILculator v2.0 production.*

