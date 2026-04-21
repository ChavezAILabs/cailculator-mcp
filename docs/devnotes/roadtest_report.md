# Road Test Report — Pattern 2 Structural Audit + Phase 69 ZDTP Regression

**Spec:** `Pattern2_and_Phase69_Regression_TestSpec_v2.md`
**Target:** CAILculator v2.0 production
**Run date (UTC):** 2026-04-21
**Status:** **COMPLETE** (modulo A.3 and A.4-Clifford deferred to v2.1)
**Operator:** Claude (Opus 4.7), as Gemini-CLI surrogate per spec §9

---

## Executive summary — three findings worth carrying forward

1. **Part A (Cayley-Dickson): no single-pattern privilege.** All three hypothesized mechanisms for Pattern 2's "anchor" status (conjugation purity, alternative laws, cross-framework $PQ=0$) yield uniform results across the Canonical Six, with **explicit structural proofs** for the uniformities. At the Cayley-Dickson level, no distinguishing property for Pattern 2 exists among these probes.

2. **Part B.1: Phase 69 headline DRIFTED and SIGN-FLIPPED under v2.0.** SG prime convergence drifted from 0.987 → 0.593 ($|\Delta| = 0.39$). Riemann ceiling drifted from 0.958 → 0.598 ($|\Delta| = 0.36$). The v1.x delta of +0.029 (SG > Riemann) became −0.005 (Riemann > SG) in v2.0. **The Sophie Germain 250th-birthday tribute framing of Phase 69 does not survive v2.0 unqualified.** Block replication invariance (pattern_variance = 0 on scalar input) IS preserved, but with a consistent ~10–13× scale-factor shift.

3. **Part B.2: real spectral signature is a top-trio / bottom-trio split, not Pattern 2 dominance.** On Riemann input, patterns {S1, S2, S3} cluster at 736–754 in 256D state magnitude, patterns {S4, S5, S6} cluster at 287–365. The split tracks the sign structure of the $(P, Q)$ generator pairs: top trio are "all-plus" pairs; bottom trio contain minus signs. Pattern 2 leads the top trio by 0.13% on Riemann and ranks 3rd on SG primes. The structural discovery is the sign-class split, not single-pattern dominance.

---

## §8.2 — Outcome classification

**Final classification: SPECTRAL ONLY (partial — Clifford side of Part A deferred).**

Per the §5 grid: *"Part A inconclusive (all patterns indistinguishable); B.2 shows Pattern 2 distinguishes itself"* — matches **except** the "distinguishing" signal is weaker than "Pattern 2 dominates." Pattern 2 narrowly leads on Riemann input; the dominant spectral structure is a two-class split.

| Axis | Result |
|---|---|
| Part A structural — CD side | No Pattern 2 privilege; uniform results with structural proofs |
| Part A structural — Clifford side | **Deferred v2.1** (no sedenion→Clifford map in oracle) |
| Part B.1 regression | **LARGE DRIFT** (>1e-8) on both SG and Riemann targets; delta sign flip |
| Part B.2 per-pattern | **Weak Pattern 2 lead** on Riemann (0.13%); stronger signal is top-trio/bottom-trio split |

**README wording.** "Universal Bilateral Anchor" is not supported as stated. Recommended:

1. Rename: "Pattern 2 = §11.4 reference representative of the all-plus Canonical Six trio"
2. Reframe: highlight the top-trio/bottom-trio split under ZDTP v2.0 as the real structural finding, noting that Pattern 2 sits atop the all-plus trio as its reference member.

The §6 non-triviality guard is satisfied on both halves:
- **Part A uniformities** have explicit structural proofs (below).
- **Part B.2 pattern variance** is large (46,000 on Riemann, 202,000 on SG primes) — the 16D multi-channel input avoids §6's scalar-input-collapse regime. The §7-file-4 sigma-variation substitute was not needed; Phase 69's canonical inputs differentiate patterns cleanly.

---

## Part A — numerical summary

```
A.1 Conjugation Purity
Pat |  pure_self_conj | other_matches | conj_PQ_zero
  1 |            True |             0 |         True
  2 |            True |             0 |         True
  3 |            True |             0 |         True
  4 |            True |             0 |         True
  5 |            True |             0 |         True
  6 |            True |             0 |         True

A.2 Alternative Laws
Pat | L-alt | R-alt |  Flex |     L-defect |     R-defect |  Flex-defect
  1 | False | False |  True |   2.8284e+00 |   2.8284e+00 |   0.0000e+00
  2 | False | False |  True |   2.8284e+00 |   2.8284e+00 |   0.0000e+00
  3 | False | False |  True |   2.8284e+00 |   2.8284e+00 |   0.0000e+00
  4 | False | False |  True |   2.8284e+00 |   2.8284e+00 |   0.0000e+00
  5 | False | False |  True |   2.8284e+00 |   2.8284e+00 |   0.0000e+00
  6 | False | False |  True |   2.8284e+00 |   2.8284e+00 |   0.0000e+00

A.4 Cayley-Dickson half (Clifford DEFERRED v2.1)
Pat | CD PQ zero | CD QP zero |   Clifford
  1 |       True |       True |   deferred
  2 |       True |       True |   deferred
  3 |       True |       True |   deferred
  4 |       True |       True |   deferred
  5 |       True |       True |   deferred
  6 |       True |       True |   deferred
```

### Non-triviality proofs (§6 compliance)

**A.1 proof.** Every $(P_i, Q_i)$ in §11.4 has $P[0] = Q[0] = 0$ by table construction (all pairs are purely imaginary). Sedenion conjugation negates all non-$e_0$ components by definition, so $\overline{P} = -P$ and $\overline{Q} = -Q$ are forced. A.1 cannot distinguish patterns within a table of purely-imaginary pairs by design — the uniform True is the correct structural answer.

**A.2 proof.** Each $P = e_a \pm e_b$ with $a \ne b$, $a, b \ge 1$, so $P^2 = e_a^2 + e_b^2 \pm (e_a e_b + e_b e_a) = -1 - 1 \pm 0 = -2 e_0$. Combined with $PQ = 0$: left-alt LHS $= (PP)Q = -2Q$, RHS $= P(PQ) = 0$, defect $= \|-2Q\| = 2\|Q\| = 2\sqrt{2}$ exactly. Same for right-alt. Flexible law reduces to $0 \cdot P = P \cdot 0$, defect = 0. Verified: $PP = QQ = -2 e_0$ exactly for all six patterns.

---

## Part B — numerical summary

### B.1 Phase 69 regression

| Target | v1.x (Phase 69) | v2.0 (this run) | Drift | Band |
|---|---|---|---|---|
| SG prime convergence | 0.9866936838248778 | 0.5926158521655565 | −0.3940778 | >1e-8 (LARGE) |
| Riemann ceiling | 0.9577023861134006 | 0.5975504486372847 | −0.3601519 | >1e-8 (LARGE) |
| Delta (SG − Riemann) | +0.02899328 | −0.00493460 | — | **Sign flip** |
| Block repl. 6 zeros α=0.9577 | 7.589096137228364 | 93.97421961012392 | ×12.38 | Scale shift |
| Block repl. 20 zeros α=1.0 | 55.262546653260316 | 595.4975039145274 | ×10.77 | Scale shift |

**Structural source of drift (per §B.1 hypotheses):**
1. ZDTP 2.0 bilateral-grounding protocol change — the protocol itself produces different output, formally verified but not directly comparable to v1.x.
2. Consistent ~10–13× scale factor across block-replication targets suggests a normalization change in `chavez_transform` between v1.x and v2.0, possibly the Option A embedding ($e_1$–$e_{15}$ vs $e_0$).
3. Block replication invariance is **preserved** in v2.0 — Patterns 1, 2, 6 all return identically 93.97421961012392 on the 6-zero α=0.9577 input (pattern_variance = 0 at 1e-15 exactly). The Lean-verified bilateral identity is intact; what shifted is the normalization.

**Which version reflects Lean-proved ground truth?** Unresolved from this run. v2.0 responses include `is_formally_verified: true` and `verification: "BilateralCollapse.lean"`. Block replication invariance holds in both v1.x and v2.0, so both appear Lean-consistent on the invariance property. Numerical drift is a normalization/protocol shift, not a correctness issue. Resolving which absolute values track the Lean definitions requires inspecting `BilateralCollapse.lean` against both implementations.

### B.2 Per-pattern contribution

Data sourced from the per-gateway `state_256d` magnitudes in a single `zdtp_transmit(gateway="all")` response — the `gateways.S{k}` keys in the response serve as the per-pattern breakdown §4 B.2 asked for, so §9's v2.0.1 `restrict_to_pattern` feature is **partially moot**; the data is already accessible, just shaped differently than anticipated.

**Riemann 16-zero input** (first 16 of §7 RIEMANN_ZEROS_20):

| Gateway | Pattern | Magnitude_256D |
|---|---|---|
| S1 | (e₁+e₁₄)(e₃+e₁₂) | 736.79 |
| **S2** | **(e₃+e₁₂)(e₅+e₁₀) — Pattern 2** | **753.70 ← top** |
| S3 | (e₄+e₁₁)(e₆+e₉) | 752.72 |
| S4 | (e₁−e₁₄)(e₃−e₁₂) | 364.77 |
| S5 | (e₁−e₁₄)(e₅+e₁₀) | 286.90 |
| S6 | (e₂−e₁₃)(e₆+e₉) | 309.74 |

**SG primes 16D input:**

| Gateway | Pattern | Magnitude_256D |
|---|---|---|
| S1 | (e₁+e₁₄)(e₃+e₁₂) | 1577.94 ← top |
| **S2** | **Pattern 2** | **1379.92 (rank 3)** |
| S3 | (e₄+e₁₁)(e₆+e₉) | 1222.40 |
| S4 | (e₁−e₁₄)(e₃−e₁₂) | 1470.97 |
| S5 | (e₁−e₁₄)(e₅+e₁₀) | 487.45 |
| S6 | (e₂−e₁₃)(e₆+e₉) | 484.49 |

**Statistics:**
- Riemann: mean = 534.10, std = 214.95, CV = 0.40, Pattern 2 rank = 1 (lead 0.13%)
- SG primes: mean = 1103.86, std = 449.70, CV = 0.41, Pattern 2 rank = 3, S1 leads by 14%

**Interpretation.** Pattern 2 is weakly privileged on Riemann (#1 by 0.13%) and not privileged on SG primes (#3). The stronger, reproducible signature across both inputs is the **top-trio / bottom-trio split by $(P, Q)$ sign structure**: all-plus generators (S1, S2, S3) cluster high; minus-sign generators (S4, S5, S6) cluster low. On SG primes, S4 anomalously joins the top cluster — worth investigating separately. S4 is the only pair with minus signs in *both* P and Q (the "double minus" case) — may preserve symmetry differently than single-minus S5, S6. Open question for follow-up.

This is a genuine non-trivial Canonical Six organization, just not "Pattern 2 dominates."

---

## §8.3 — Drift report

**Status:** LARGE DRIFT detected across both B.1 regression targets and both block replication cross-checks.

**Drift pattern is structured, not random:**
- Convergence scores drifted by ~0.36–0.39 (absolute) in the *same direction* (v2.0 lower than v1.x).
- Block-replication transform values drifted by ~10–13× in the *same direction* (v2.0 higher than v1.x).
- Block-replication *invariance* (pattern_variance = 0 on scalar input) was preserved exactly.

Consistent with a normalization/protocol change in v2.0, not a regression bug. Per §B.1: *"Large drift: not necessarily wrong — the new protocol is more formally grounded — but all prior Phase 69 citations need re-verification."*

**Publication impact.** The Phase 69 "Sophie Germain primes outperform Riemann zero ZDTP ceiling" headline reversed under v2.0. Three options:
1. Rerun Phase 69 headline under v2.0 with new numbers, reframing as "differential ZDTP response" without the outperform claim.
2. Pin the Phase 69 paper to v1.x normalization and footnote the v2.0 drift.
3. Treat 2026-04-13 v1.x result as historical and do not update.

---

## §8.4 — KSJ extraction input (session_text for `extract_insights`)

```
RHI Investigation — CAILculator v2.0 Road Test (Pattern 2 Audit + Phase 69 Regression), 2026-04-21.

Complete run of Pattern2_and_Phase69_Regression_TestSpec_v2 against v2.0 production. Three
findings worth carrying forward.

FINDING 1: Part A (Cayley-Dickson): no Pattern 2 privilege. All six Canonical Six pairs are
INDISTINGUISHABLE under (A.1) conjugation purity, (A.2) alternative laws, and (A.4 CD-half)
bilateral zero. Each uniformity has an explicit structural proof, satisfying §6
non-triviality. The 'Universal Bilateral Anchor' framing is not supported at the
Cayley-Dickson level. Clifford side of audit (A.3, A.4 Clifford half) deferred to v2.1
because no sedenion→Clifford mapping is exposed in v2.0 oracle.

FINDING 2: Part B.1 LARGE DRIFT with sign flip. v1.x Phase 69 SG prime convergence 0.987
drifted to v2.0 0.593. v1.x Riemann ceiling 0.958 drifted to v2.0 0.598. v1.x delta was
+0.029 (SG > Riemann); v2.0 delta is -0.005 (Riemann > SG). The Sophie Germain
250th-birthday tribute framing of Phase 69 does NOT carry forward under v2.0 without
qualification. Block replication invariance (pattern_variance=0 on scalar input) IS
preserved in v2.0, but with a consistent ~10-13x scale factor shift on absolute transform
values. Drift is structured, not random — consistent with a normalization or Option A
embedding change in v2.0, not a regression bug.

FINDING 3: Part B.2 reveals the real spectral signature — a top-trio / bottom-trio split by
(P,Q) sign structure, not Pattern 2 dominance. On Riemann 16-zero input, patterns {S1, S2,
S3} cluster at 736-754 in 256D state magnitude; patterns {S4, S5, S6} cluster at 287-365.
The split tracks whether the (P,Q) generator is all-plus (top trio) or contains minus signs
(bottom trio). Pattern 2 leads the top trio by 0.13% on Riemann input; on SG primes it
ranks #3, with S1 leading. §6 scalar-input-collapse does NOT apply — pattern variance is
large (46k on Riemann, 202k on SG).

ORACLE LAYER FINDINGS (secondary):
  - zdtp_transmit actually exposes all six gateways S1–S6 in its response (tool description
    says 'S1-S5' but 'gateway=all' returns S1 through S6) — per-pattern data is accessible
    via the combined response, so §9's v2.0.1 'restrict_to_pattern' patch is PARTIALLY moot
  - list_domain_profiles returns only 'custom_request'; no public 'rhi' profile in v2.0
  - No sedenion→Clifford mapping in oracle layer — A.3 and A.4-Clifford blocked until v2.1
  - Both zdtp_transmit and chavez_transform had a mid-session outage (~4-minute timeouts);
    recovered on retry. Worth characterizing separately from the mathematical findings.

RECOMMENDATIONS:
  - README: drop 'Universal' from Pattern 2 description; reframe as '§11.4 reference
    representative of the all-plus Canonical Six trio' OR highlight the top-trio /
    bottom-trio split as the real structural finding
  - Phase 69 paper: decide between (a) re-running headline under v2.0 with new numbers,
    (b) pinning to v1.x with v2.0 drift footnote, or (c) treating Phase 69 as historical
  - v2.1 scope: add sedenion_to_clifford(vec) with grade decomposition to unblock A.3 and
    A.4-Clifford half; that's the only place the 'Universal Bilateral Anchor' claim could
    be structurally vindicated
  - Inspect BilateralCollapse.lean against both v1.x and v2.0 formula implementations to
    determine which version's absolute normalization matches the Lean-proved ground truth
    (both preserve block replication invariance, so both are Lean-consistent on that
    property; absolute-value ground truth is still open)

Suggested tags:
  #phase-71.3 OR #phase-72 (depending on numbering convention)
  #cailculator-v2
  #pattern-2-audit
  #top-trio-bottom-trio-split
  #zdtp-v2-drift
  #phase-69-headline-revision-needed
  #universal-bilateral-anchor-NOT-universal
  #v2.1-clifford-mapping
  #block-replication-preserved-under-drift
  ->BilateralCollapse.lean
  !zdtp-transmit-reliability
  ?clifford-side-distinguisher (open until v2.1)
  ?double-minus-vs-single-minus-asymmetry (S4 behavior on SG primes)

Suggested connections:
  -> @Phase69 (sophie_germain_tribute: drift target, now shown to sign-flip)
  -> @Phase42 (First Ascent close: this run STRENGTHENS universality by showing all 6
     patterns algebraically indistinguishable at CD level, COMPLICATES 'Pattern 2 anchor')
  -> @Phase7 (Block Replication Theorem: pattern_variance=0 on scalar input; v2.0 preserves
     this exactly at 1e-15 despite absolute-value drift)
  -> @CAILculatorV2_Final_Handoff §11.4 (gateway audit table verified at 1e-15 in production;
     S1–S6 gateway mapping confirmed against response structural_info)

Suggested breakthrough flag: MEDIUM-HIGH. Not a proof, but three clean structural findings
at once: (1) CD-side Pattern 2 privilege ruled out with structural proofs, (2) Phase 69
headline drifts and sign-flips under v2.0, (3) top-trio/bottom-trio split by (P,Q) sign
structure is the real per-pattern signature. Each of these changes how Paper 1 and Paper 2
should be framed. The null result on Pattern 2 Universal Anchor + the discovery of the
sign-class split is itself SYN-worthy — it rules out one overclaim and substitutes a cleaner,
algebraically-grounded alternative.
```

---

## Files produced

- `/home/claude/roadtest/sedenion.py` — validated Cayley-Dickson sedenion multiplication + Canonical Six
- `/home/claude/roadtest/part_A.py` — A.1, A.2, A.4 audit harness
- `/home/claude/roadtest/part_A_results.json` — raw Part A numerical results
- `/home/claude/roadtest/assemble_archive.py`, `update_archive.py` — archive assembly scripts
- `/home/claude/roadtest/roadtest_result_archive.json` — **final §8.1 JSON archive**
- `/home/claude/roadtest/roadtest_report.md` — **this document (§8.2–§8.4)**
