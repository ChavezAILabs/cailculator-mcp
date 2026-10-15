# Zero Divisor Transmission Protocol (ZDTP)

**Structural transmission through verified algebraic gateways from 16D to 256D**

---

## Overview

The Zero Divisor Transmission Protocol is the structural transmission layer of CAILculator. It lifts a 16-dimensional sedenion state into 256-dimensional space — preserving the original state throughout — then measures how consistently the data's structure propagates across six algebraic transmission pathways.

ZDTP was designed to ask whether data carries structure that is stable across the Cayley-Dickson algebraic geometry, or aligns with some algebraic channels and not others. The answer is a single convergence score.

> **Closed form (2.2.0). Read this first.** The outputs reduce exactly to
> $$m_k = \text{magnitude}_{256D}(k) = \sqrt{\|x\|^2 + 64x_0^2 + 16s_k^2}, \qquad s_k = \langle P_k + Q_k, x\rangle,$$
> where $s_k$ is a signed sum of four input components, and the convergence score is a function of the six $m_k$. The zero-divisor property of the gateways does not enter the result: same-shape pairs that are not zero divisors give the same rank-2 interaction map and the same values. ZDTP outputs are therefore reported as experimental measurements, not structural findings. The algebraic facts below (the tower, the bilateral identities, the oracle) are correct; the interpretive claims in earlier versions of this page are corrected where they appear. Derivation and numerical checks: [ZDTP_CLOSED_FORM.md](./ZDTP_CLOSED_FORM.md).

---

## Algebraic Foundation

### The Cayley-Dickson Tower

The sedenions $\mathbb{S}$ are the 16-dimensional algebra produced by applying the Cayley-Dickson construction to the octonions $\mathbb{O}$. Each doubling step:

$$\mathbb{R} \to \mathbb{C} \to \mathbb{H} \to \mathbb{O} \to \mathbb{S} \to \mathbb{P} \to \cdots$$

preserves the previous algebra as a subalgebra while introducing new structure. The sedenions are the first algebra in this tower to contain **zero divisors** — non-zero elements whose product is zero. The 32-dimensional **pathions** $\mathbb{P}$ and the 64-dimensional, 128-dimensional, and 256-dimensional algebras beyond them each inherit and extend this zero divisor structure.

ZDTP transmits a 16D sedenion state upward through this tower to 256D, using a zero divisor pair at each level. As the closed form shows, the result does not depend on the pair being a zero divisor.

### Why Non-Associativity Matters

Beyond the octonions, Cayley-Dickson algebras are non-associative: $(a \times b) \times c \neq a \times (b \times c)$ in general. This is not a defect — it is the feature that makes ZDTP structurally meaningful.

When a 16D input $x$ interacts with a gateway pair $(P, Q)$, the four orderings:

$$Px, \quad xQ, \quad Qx, \quad xP$$

are individually distinct products. Their sum is not: Cayley-Dickson algebras are quadratic, so $uv + vu = -2\langle u, v\rangle$ for pure imaginary $u, v$, and the four-factor sum collapses to

$$Px + xQ + Qx + xP = 2x_0(P + Q) - 2\langle P + Q, x\rangle e_0.$$

Only the input's real part $x_0$ and one signed four-term sum survive; the interaction map has rank 2. Non-associativity plays no part in the result.

---

## The Canonical Six Gateways

ZDTP uses six formally verified bilateral zero divisor pairs as transmission gateways. A bilateral zero divisor pair $(P, Q)$ satisfies:

$$P \times Q = 0 \quad \text{and} \quad Q \times P = 0$$

with $P \neq 0$ and $Q \neq 0$. The Canonical Six are:

| Gateway | P | Q | Properties |
|---------|---|---|------------|
| S1 | $e_1 + e_{14}$ | $e_3 + e_{12}$ | Cayley-Dickson bilateral; Clifford-asymmetric (‖QP‖ = 2√2, dimension-invariant); antipodal partner of S4 (Lean 4-proved); Class B |
| S2 | $e_3 + e_{12}$ | $e_5 + e_{10}$ | Universal Bilateral Anchor — bilateral in both Cayley-Dickson and Clifford frameworks (16D–256D); Class A |
| S3A | $e_4 + e_{11}$ | $e_6 + e_9$ | Cayley-Dickson bilateral; same Fano origin as S3B (sign-distinguished); K_Z kernel-degenerate with S3B; Class A |
| S3B | $e_1 - e_{14}$ | $e_3 - e_{12}$ | Cayley-Dickson bilateral; same Fano origin as S3A (sign-distinguished); K_Z kernel-degenerate with S3A; magnitude-equal to S4 universally; Class B |
| S4 | $e_1 - e_{14}$ | $e_5 + e_{10}$ | Cayley-Dickson bilateral; antipodal partner of S1 (Lean 4-proved); magnitude-equal to S3B universally; K_Z kernel-degenerate with S5; Class B |
| S5 | $e_2 - e_{13}$ | $e_6 + e_9$ | Cayley-Dickson bilateral; K_Z kernel-degenerate with S4; Class A |

### Why These Six

The Canonical Six are not an arbitrary selection from the 84 bilateral zero divisor pairs in 16D sedenion space. Two of their properties are formally verified; a third is an active area of exploratory research:

1. **E8 first shell membership (exploratory)**: An exploratory Lean 4 result (`e8_weyl_orbit_unification.lean`) establishes that the five distinct P-vectors of the Canonical Six have norm² = 2, consistent with lying on the E8 first shell, and that all five reduce to the same dominant weight under sequences of Weyl reflections — suggesting a connection to a single Weyl orbit. One antipodal pair is formally connected by a single simple reflection (sα₄). This is the most preliminary of CAILculator's formal components; the E8 orbit structure is an active area of work.

2. **Cross-framework presence (formally verified)**: Zero divisor structure persists across both Cayley-Dickson and Clifford (Geometric) algebraic representations. S2 is fully bilateral (PQ=0 ∧ QP=0) in both frameworks across 16D–256D. The remaining five are bilateral in Cayley-Dickson and unilateral in Clifford (PQ=0, QP≠0 — e.g. S1 produces ‖QP‖ = 2√2). This persistence across frameworks and dimensional doublings confirms these patterns are not artifacts of a particular algebraic convention.

3. **Bilateral zero divisor identity (formally verified)**: The bilateral property PQ=0 ∧ QP=0 for each of the six gateway pairs is proved in `lean/BilateralCollapse.lean` and independently confirmed at runtime at 10⁻¹⁵ precision.

The cross-framework discovery initiated the research program, published at [DOI 10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495).

---

## Transmission Mechanics

### The Four-Factor Interaction

For a 16D input vector $x$ and a gateway pair $(P, Q)$, the interaction step computes:

$$\text{interaction} = Px + xQ + Qx + xP$$

Each term is a sedenion product, but the sum collapses to $2x_0(P+Q) - 2\langle P+Q, x\rangle e_0$ (see above): two numbers, $x_0$ and $\langle P+Q, x\rangle$, determine it.

The result is **appended** to the original input, not substituted for it:

$$\text{output} = [x \,|\, \text{interaction}] \in \mathbb{R}^{32}$$

The original 16D input occupies the first 16 components of the 32D output unchanged. This is the critical structural invariant of ZDTP: **the original state is always recoverable** as the first 16 components of any higher-dimensional output.

### Recursive Dimensional Expansion

The append-and-expand pattern repeats recursively through the Cayley-Dickson tower:

$$16\text{D} \xrightarrow{S_i} 32\text{D} \xrightarrow{S_i} 64\text{D} \xrightarrow{S_i} 128\text{D} \xrightarrow{S_i} 256\text{D}$$

At each stage, the original 16D gateway pair is **zero-padded** into the current dimension before the interaction step. The same pair is used at every stage. Above 16D the upper-half interaction term is identically zero, and the growth in dimension comes from concatenation (state plus interaction), not from new algebraic content.

The full transmission through a single gateway produces a 256D state vector. The original 16D input is always the first 16 components.

### The Runtime Oracle

Before any transmission begins, the bilateral oracle independently reconfirms the zero divisor property of the gateway pair numerically:

$$|P \times Q| < 10^{-10} \quad \text{and} \quad |Q \times P| < 10^{-10}$$

This check runs at $10^{-15}$ floating-point precision. It is not a Lean call — it is a numpy arithmetic gate that runs on every transmission. The Lean proof (`BilateralCollapse.lean`) established which pairs are valid gateways; the runtime oracle enforces this on every execution.

*Note on thresholds*: The $10^{-15}$ figure is the engine's general floating-point precision standard. The $10^{-10}$ figure is the zero divisor classification gate — the threshold below which a product is classified as algebraically zero. These measure different things and are not contradictory.

---

## Convergence Scoring

### The Full Cascade

A single gateway transmission produces one 256D state. The **full ZDTP cascade** runs the same 16D input through all six gateways and collects six 256D output magnitudes:

$$\{m_{S1}, m_{S2}, m_{S3A}, m_{S3B}, m_{S4}, m_{S5}\} = \{\|\text{output}_{S1}\|, \|\text{output}_{S2}\|, \|\text{output}_{S3A}\|, \|\text{output}_{S3B}\|, \|\text{output}_{S4}\|, \|\text{output}_{S5}\|\}$$

The six gateways have three independent K_Z bilateral kernel components: S3A and S3B are kernel-degenerate (same Fano intersection pair, sign-distinguished), as are S4 and S5. All six transmissions are run because the convergence score operates on 256D magnitudes — which reflect the full structural response of each pathway, not kernel values alone.

### The Convergence Score

The convergence score measures how uniformly the input's structure propagates across all six pathways:

$$\text{score} = 1 - \frac{\sigma(\{m_i\})}{\mu(\{m_i\})}$$

where $\sigma$ is the standard deviation and $\mu$ is the mean of the six magnitudes. A score of 1.0 would mean all six gateways produce identical output magnitudes — perfect structural uniformity. A score near 0 means the magnitudes are as variable as their mean — complete structural asymmetry.

| Score | Stability | Interpretation |
|-------|-----------|----------------|
| > 0.8 | HIGH | Structure propagates uniformly across all six pathways |
| 0.5–0.8 | MODERATE | Detectable structural variation across gateways |
| < 0.5 | LOW | Structural asymmetry or regime shift in the input data |

> **Validation status (2.2.0):** these bands are not applied as verdicts. `stability_level`
> is reported as `"not_assessed"` because, on 200 seeded null series fed through
> `analyze_dataset`, the score fell in 0.54–0.65, the same range as every structured series
> tested. The interpretations in this section are hypotheses until a gate run supports them.
> See `docs/EVALUATION_CONTRACT.md`.

### What Convergence Means

By the closed form, the six magnitudes differ only through the six signed four-term sums $s_k$, so the score measures how similar those sums are in size relative to $\|x\|$ and $x_0$. It is not evidence of gateway-independent structure. Earlier versions of this page read HIGH convergence as "the signature of a genuine structural invariant" and LOW convergence as preceding market regime transitions; neither reading has been validated, and on 200 seeded null series the score fell in the same range as every structured series tested. The Riemann critical-line results (see Research Applications) are being re-checked against the closed form.

---

## Formal Verification Basis

### BilateralCollapse.lean

`BilateralCollapse.lean` formally proves two theorems:

**Bilateral Zero Divisor Identity**: The six canonical gateway pairs satisfy $PQ = 0 \wedge QP = 0$ in 16D sedenion space. This proof was verified by Aristotle (Harmonic Math's independent Lean 4 engine) with zero sorry stubs.

**scalar_channel**: For any scalars $a, b, c$, the product $(aP + bQ)(bP + cQ) = (-2b(a+c)) \cdot e_0$. Any product of two elements drawn from the span of a gateway pair — with matched cross-coefficient structure — collapses cleanly to the real channel. No spurious imaginary components are generated at any transmission stage.

The scalar_channel theorem is a statement about products within a gateway pair's span. It does not, by itself, say anything about how data passes through ZDTP; that is fixed by the closed form above.

### The Lean-to-Runtime Pipeline

The formal verification chain operates in three stages:

1. **Offline proof** — `BilateralCollapse.lean` establishes which coordinates are valid gateways. This computation happens once, independently of any runtime.

2. **Hardcoded constants** — The verified coordinates are stored as constants in `core/canonical_six.py` with `BilateralCollapse.lean` as their explicit attribution. The engine does not rediscover the gateways at runtime.

3. **Runtime gate** — The bilateral oracle reconfirms the property numerically before each transmission. This is the bridge between the static formal proof and the dynamic execution environment.

---

## Research Applications

### Riemann Hypothesis Investigation

The deepest application of ZDTP to date is the CAIL-RH Investigation (74+ phases as of May 2026). The protocol maps Riemann zeros $\gamma_n$ into 16D sedenion space via the RHI mapping ($\log p \to ROOT_{16D}$; shipped as the `rhi` profile until 2.2.0) and transmits them through the full ZDTP cascade.

Empirical finding across CAILculator Runs A–C: inputs corresponding to zeros on the critical line ($\text{Re}(s) = \frac{1}{2}$) consistently produce HIGH convergence (>0.8) across all six gateways, while perturbed inputs do not. This convergence universality — confirmed across Runs A–C and holding at every tested zero, not merely on average — is a numerical observation. It is being re-checked: by the closed form it reduces to four-term sums of the mapped zeros, and it has not yet been compared with same-shape non-zero-divisor pairs.

Separately, and not to be conflated with it, the CAIL-RH Investigation has developed three independent standard-axiom characterizations of the critical line in Lean 4: the energy-minimum, spectral-containment, and arithmetic-integrality routes (Phase 74+). These are formally proved results; the HIGH-convergence empirical finding is a distinct, corroborating numerical observation from the same research program.

### Quantitative Finance

Bitcoin rolling window analysis (718 windows, January 2024–January 2026) using the Quant Equity profile identified:

- **LOW stability events** at June and December 2024 consolidation periods — both preceded large directional moves
- **HIGH stability** at the January 2025 correction — structural coherence despite price turbulence

This is a single-series observation without controls, not a validated signal. No test has shown that ZDTP convergence predicts or coincides with market regime changes, and since 2.2.0 `analyze_dataset` withholds its regime classification (`not_assessed`) until a detector passes a validation gate.

### Investigative Journalism

The Journalism profile reports ZDTP convergence and gateway magnitudes for public datasets such as campaign finance records. Since profile 3.0.0 it gives no verdicts (`measured_only`): no journalism-specific reading of these quantities (such as "tipping points") has passed a validation gate.

---

## Relationship to the Chavez Transform

Both have exact closed forms in the shipped tools, and neither uses the zero-divisor property:

| | Chavez Transform (1D, as shipped) | ZDTP |
|---|---|---|
| **Input** | A numerical series | 16D sedenion state |
| **Output** | Center-weighted sum of the series | Six magnitudes and a convergence score |
| **Closed form** | $\sum_i \text{data}_i w_i$ ([chavez_transform.md](./chavez_transform.md)) | $\sqrt{\|x\|^2 + 64x_0^2 + 16s_k^2}$ ([ZDTP_CLOSED_FORM.md](./ZDTP_CLOSED_FORM.md)) |
| **Status** | Experimental measurement | Experimental measurement |

Earlier versions of this page proposed using the Chavez Transform to find inputs with "structural content" and ZDTP to test whether that structure is gateway-independent. Neither step has been validated, so that workflow is withdrawn.

---

## Further Reading

- **[Chavez Transform Explainer](./chavez_transform.md)** — The kernel mechanism, stability bound, and formal verification chain for the transform underlying the ZDTP gateways.
- **[Project Glossary](./GLOSSARY.md)** — Definitions for sedenions, pathions, and higher-dimensional algebraic structures; bilateral zero divisors and all domain-specific terminology.
- **Research DOI**: [10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495) — *"Framework-Independent Zero Divisor Patterns in Higher-Dimensional Cayley-Dickson Algebras: Discovery and Verification of The Canonical Six"*
- **Lean source**: [`lean/BilateralCollapse.lean`](../lean/BilateralCollapse.lean)

---

*Chavez AI Labs — Applied Pathological Mathematics™*  
*"Better math, less suffering."*
