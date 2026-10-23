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
| `compute_high_dimensional` (`is_zero_divisor`) | **1e-15** | Cayley-Dickson | 16, 32, 64, 128, 256 |
| `verify_bilateral_oracle` | **1e-15** | Cayley-Dickson or Clifford | any length (Clifford: power of 2) |
| `zdtp_transmit` (gateway check before transmission) | 1e-15 | Cayley-Dickson, 16D | 16 |

**One threshold.** Decided by Paul on 2026-10-22: zero means below 1e-15 ("precision to
15 zeros"), matching the engine's float64 "10^-15" standard. Until then
`compute_high_dimensional` used 1e-10 (no recorded reason), so the two tools could
disagree when a product's norm fell between 1e-15 and 1e-10. They now agree. The
provenance `algorithm` for `is_zero_divisor` is `cayley_dickson.is_zero_divisor/2`.

**What to watch.** Pairs made of ±1 basis coefficients (the Canonical Six and every
golden case) have product norms of exactly 0 or at least 1, so the threshold does not
affect them. Dense or irrational coefficients can leave float64 rounding residue near
1e-16 × dimension (about 2.6e-14 at 256D), which is above 1e-15: such a pair can be a
true zero divisor and still be reported as not one. A relative threshold
(‖PQ‖ ≤ ε·‖P‖·‖Q‖) would handle that; it is not implemented.

## "precision" is not "threshold"

- `precision` (`"10^-15"` string in most tools, `1e-15` float in the oracle) is a label for
  the engine's numerical standard: float64 arithmetic. It is kept unchanged for backward
  compatibility. It does **not** say what cutoff decided a verdict.
- `threshold` (and `provenance.tolerance`) is the cutoff that decided the verdict.
  `compute_high_dimensional` returning `"precision": "10^-15"` next to
  `"threshold": 1e-15` means "computed in float64; declared zero below 1e-15".

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
