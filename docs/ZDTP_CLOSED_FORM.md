# ZDTP Closed Form: What the Cascade Computes

**Status:** finding, 2026-10-06. Verified in-process on this checkout
(`src/cailculator_mcp/zdtp/protocol.py`, ZDTP 2.0 as shipped in 2.2.0), to about 1e-15.
**Prompted by** Paul's question: could the transmission "bus" be any multiplication
(2×10 → 2×100 → 2×1000) and ZDTP would handle it the same way, so that the 16D algebra
is never really invoked?
**Answer:** yes. As implemented, the cascade is six signed sums of four input components
each. Neither the zero-divisor property nor the non-associative structure of the
Cayley–Dickson algebras affects any output.

## The result

For gateway k with Canonical Six pair (P_k, Q_k), let S_k = P_k + Q_k and
s_k = ⟨S_k, x⟩. Then

    magnitude_256d(k) = √( ‖x‖² + 64·x₀² + 16·s_k² )

The convergence score is `1 − std/mean` of the six magnitudes, so it is a function of
‖x‖, x₀ and the six sums s₁…s₆, nothing else. Each S_k has four ±1 entries:

| Gateway | S_k = P_k + Q_k | s_k |
|---|---|---|
| S1 | e1 + e3 + e12 + e14 | x₁ + x₃ + x₁₂ + x₁₄ |
| S2 | e3 + e5 + e10 + e12 | x₃ + x₅ + x₁₀ + x₁₂ |
| S3A | e4 + e6 + e9 + e11 | x₄ + x₆ + x₉ + x₁₁ |
| S3B | e1 + e3 − e12 − e14 | x₁ + x₃ − x₁₂ − x₁₄ |
| S4 | e1 + e5 + e10 − e14 | x₁ + x₅ + x₁₀ − x₁₄ |
| S5 | e2 + e6 + e9 − e13 | x₂ + x₆ + x₉ − x₁₃ |

## Why

Three facts, each elementary.

**1. The 16D interaction is an inner product.** Cayley–Dickson algebras are quadratic:
every element satisfies z² − 2Re(z)·z + ‖z‖² = 0. Polarizing gives, for pure imaginary
u and v, u·v + v·u = −2⟨u, v⟩. The Canonical Six P and Q are pure imaginary, so for
x = x₀ + x_im:

    P·x + x·Q + Q·x + x·P = (S·x + x·S) = 2·x₀·S − 2⟨S, x⟩·e₀

The symmetrized sum cancels exactly the parts of the product that are non-commutative
or non-associative. The map has rank 2 for every sparse pure-imaginary pair, whether or
not it is a zero divisor. Measured on (e1+e2, e3+e4), (e1+e3, e5+e7), (e2+e6, e9+e13) and
(e1+e10, e4+e11), none of which is a zero divisor: rank 2, the same singular values as the
Canonical Six.

**2. The upper-half term vanishes.** At 32D and above, `_expand_dimension` adds
x₂·P + x₂·Q̄ + x₂·Q + x₂·P̄ = x₂·(P + P̄) + x₂·(Q + Q̄) = x₂·2Re(P) + x₂·2Re(Q) = 0.

**3. "Lossless" comes from concatenation.** Each level returns `state ⊕ interaction`:
the input is copied verbatim into the first half. Any map x ↦ (x, f(x)) is lossless,
whatever f is.

Putting them together: every level from 16D to 256D appends one block 2x₀S − 2s·e₀,
whose squared norm is 16x₀² + 4s² (‖S‖² = 4). The original x is carried unchanged, the
second-half terms are zero, and there are four levels, which gives the formula above.

## Verification

Run in-process, this checkout, cwd = repo root, 2026-10-06:

| Check | Inputs | Max error |
|---|---|---|
| Identity 1 (16D interaction) | 6 gateways × 5 random x ∈ ℝ¹⁶ | 8.9e-16 (absolute) |
| Identity 2 (upper-half term = 0) | 6 gateways, random x₂ ∈ ℝ³² | 4.4e-16 (absolute) |
| Closed form, x₀ = 0 (`analyze_dataset` input) | 6 gateways × 3 random x | 3.1e-16 (relative) |
| Closed form, x₀ ≠ 0 (`zdtp_transmit` input) | 6 gateways × 3 random x | 3.8e-16 (relative) |
| Rank of the 16D interaction map | Canonical Six, 4 non-ZD sparse pairs, 2 dense random pairs | 2, 2, 16 |

The dense random pairs have rank 16 because they have a real part. Only the
pure-imaginary structure matters, not whether the pair is a zero divisor.

## Consequences

- **Convergence score.** On `analyze_dataset`'s input (last 15 points divided by the
  first, x₀ = 0) every component is near 1, so s₁, s₂, s₃ ≈ 4, s₄ ≈ 0, and s₅, s₆ ≈ 2.
  The fixed spread of the six magnitudes comes from the sign patterns, not the data. That
  is why the score sat at 0.54–0.65 for noise and for every structured series in the
  2.2.0 gate work.
- **Gateway magnitudes** are ‖x‖ plus one four-point sum each. On dollar-valued input
  they restate dollar amounts.
- **Oracle "verification: SUCCESS"** checks the fixed gateway pair before the data is
  used. It is true for every input and cannot fail on data.
- **Claims built on ZDTP outputs need re-checking against this closed form.** In
  particular, the documented empirical finding that Riemann zeros on the critical line
  produce HIGH convergence (`docs/zdtp_protocol.md`, `docs/chavez_transform.md`) reduces
  to a statement about four-point sums of the mapped zeros. Whatever separates on- from
  off-line inputs has to be explainable by those sums and that mapping. This is the same
  family of problem as the retracted Ω_d "dimensional persistence" finding.

What this does **not** affect: the Lean-proved facts about the Canonical Six themselves
(that each (P, Q) is a bilateral zero divisor), the Chavez Transform's stability bound,
and `compute_high_dimensional` / `verify_bilateral_oracle`, which use the algebra
directly.

## Requirement for APM operators: the substitution test

An Applied Pathological Mathematics operator is doing work in its own region of
mathematics only if its output changes when the pathology is removed. Before an APM
quantity backs a claim, run the same inputs with:

1. the Canonical Six (P, Q);
2. sparse pairs of the same shape that are **not** zero divisors;
3. a division algebra (quaternion or octonion analogue), which has no zero divisors at all;
4. an associative algebra (Clifford, already supported by `verify_bilateral_oracle`).

If (1) is indistinguishable from (2)–(4) on the quantity being reported, the zero-divisor
structure is not what produces it. This sits next to the null-series gate (G3): G3 asks
whether the output means anything, and the substitution test asks whether the algebra is
the reason.

## Where zero divisors can do real work

What sets a zero divisor apart is a **nonzero annihilator**: for zero-divisor P, the set
{x : x·P = 0} (and its left counterpart) is a nonzero subspace. In a division algebra it
is always {0}. Candidate operators that keep this in play:

- **One-sided products** x ↦ x·P and x ↦ P·x, which are not symmetrized. Their kernels
  are the annihilators, which exist only because P is a zero divisor.
- **Annihilator projection:** the fraction of ‖x‖² lying in ann(P_k), for each Canonical
  Six gateway. A data-dependent, six-component signature that a division algebra cannot
  produce.
- **The associator** (x·P)·Q − x·(P·Q) = (x·P)·Q, since P·Q = 0. It measures how
  non-associativity acts on the data along a gateway, which is zero in any associative
  algebra.

Each would still need the null gate (G3), the planned sensitivity gate (G6), and the
substitution test before it backs a verdict.

## Suggested next steps

1. Decide whether ZDTP keeps its current form, documented as a fixed linear feature map,
   or is rebuilt on one-sided or annihilator operators. If it is rebuilt, version it
   (ZDTP 3.0) so recorded results stay attributable to the version that produced them.
2. Re-run the RH critical-line convergence result with the closed form alongside it, and
   with the substitution test.
3. Until then, documentation describing ZDTP as lossless "through the zero-divisor
   gateways", or the cascade as revealing high-dimensional structure, should point here.
