# Evaluation Contract

This page says what each CAILculator verdict means, what threshold decides it, and what
backs it. When this page and a response's `provenance.tolerance` disagree, the provenance
block is authoritative: it records the threshold that was actually applied.

## "Zero divisor" means bilateral

A pair (P, Q) is reported as a zero divisor only if **P·Q = 0 and Q·P = 0**. One-sided
annihilation (for example PQ = 0 but QP ≠ 0, as S1 shows in the Clifford framework) is
reported as `is_bilateral_zero_divisor: false`. The individual norms `PQ_norm` and
`QP_norm` are always returned so a one-sided result is visible.

"= 0" means "Euclidean norm of the product below the zero threshold".

## Zero thresholds

| Tool | Threshold on ‖PQ‖ and ‖QP‖ | Frameworks | Dimensions |
|---|---|---|---|
| `compute_high_dimensional` (`is_zero_divisor`) | **1e-10** | Cayley-Dickson | 16, 32, 64, 128, 256 |
| `verify_bilateral_oracle` | **1e-15** | Cayley-Dickson or Clifford | any length (Clifford: power of 2) |
| `zdtp_transmit` (gateway check before transmission) | 1e-15 | Cayley-Dickson, 16D | 16 |

**Why there are two.** The repo does not record a reason for `compute_high_dimensional`
using 1e-10. The oracle's 1e-15 matches the engine's float64 "10^-15" standard.

**When they can disagree.** Only when a product's norm falls between 1e-15 and 1e-10.
Then `compute_high_dimensional` says "zero divisor" and the oracle says "not". Pairs made
of ±1 basis coefficients (the Canonical Six and every golden case) have norms of exactly
0 or at least 1, so the two tools agree on them. The golden suite checks that agreement.
Dense or irrational coefficients can leave rounding residue near 1e-16 × dimension, and
that is where 1e-15 becomes fragile.

**Decision pending (Paul):** keep two thresholds and document them here, or have both
tools share one. A shared threshold would most naturally be relative, e.g.
‖PQ‖ ≤ ε·‖P‖·‖Q‖. The math has **not** been changed in v2.2.0; both tools behave
exactly as before.

## "precision" is not "threshold"

- `precision` (`"10^-15"` string in most tools, `1e-15` float in the oracle) is a label for
  the engine's numerical standard: float64 arithmetic. It is kept unchanged for backward
  compatibility. It does **not** say what cutoff decided a verdict.
- `threshold` (and `provenance.tolerance`) is the cutoff that decided the verdict.
  `compute_high_dimensional` returning `"precision": "10^-15"` next to
  `"threshold": 1e-10` means "computed in float64; declared zero below 1e-10".

## Other verdicts

| Output | Rule | Backing |
|---|---|---|
| `analyze_dataset` `regime.classification` and `stability_level`; `zdtp_transmit` (gateway `all`) `convergence.stability_level` | Always `"not_assessed"` since 2.2.0, for every profile. | The old cutoffs (≥ 0.8 stable / HIGH, ≥ 0.5 transitioning / MODERATE) carried no information: on the G3 null series the score fell in 0.54–0.65, and so did every structured series tested, including a 50% step break; 198/200 nulls were "transitioning". The score itself is still reported as a measurement. A replacement detector is planned. |
| `detect_patterns` / `top_patterns` | Per-detector thresholds (see `provenance.tolerance`) | Since 2.2.0, conjugate, bilateral and cyclic symmetry are scored on deviations from the mean. Before that they were scored against the raw norm, so a series with a large mean scored high even when it was noise (175/200 G3 nulls flagged). After the change: 0/200 nulls flagged by any pattern detector; a period-12 sine is still found at SNR 5. |
| `chavez_transform` `stability_bound.satisfied` | \|C[f]\| ≤ M·‖f‖₁ + 1e-15 | Theorem 2, `lean/ChavezTransform_genuine.lean`. |
| `map_e8_orbit` `is_on_first_shell` | \|‖v₈‖² − 2\| < 1e-10 | Definition of the E8 first shell. |

Profiles with `output_policy: "measured_only"` (journalism 3.0.0) also withhold pattern
verdicts. They report measured quantities only.

## What backs a profile

`list_domain_profiles` reports, for every profile:

- `used_theorems`: results the profile's math relies on, each a Lean file under `lean/`.
  The gate check confirms the file exists and contains no `sorry`/`admit`. It does not
  compile Lean.
- `empirical_dependencies`: claims that rest on evidence rather than proof. To count
  toward the `Official` tier (gate G1), each must cite a reproducible record (a KSJ AIEX
  entry, DOI, or URL) **and** state the controls in that record. A claim referenced to
  experience or to "v1.x heuristics" does not pass G1.
- `tier`: the tier the profile actually loaded at (`Template`, `Experimental`, or
  `Official`), decided by its gate record, never by the manifest alone.
  `requested_tier`, `gate_status`, `gates_passed` and `gates_failed` show why.

Gates G1–G5 are defined in `scripts/check_profile_gates.py`. The false-positive ceiling
for G3 is 5% on at least 200 seeded null series.
