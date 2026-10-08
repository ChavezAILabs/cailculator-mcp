# Changelog

All notable changes to the CAILculator MCP Server will be documented in this file.

## [2.2.0] - Unreleased (target; not yet published)

Golden test suite, response provenance, and real profile gates. Bundled with the
August input-validation and `chavez_transform` doc fixes below. No change to the math:
every algebra, transform and detector computes exactly what it did in 2.1.4.

### Added
- **Provenance block on every tool response** (`provenance.py`, applied once at dispatch in
  `tools.call_tool`): server/engine version, build commit, algorithm ID with version
  suffix, framework, dimension, profile (name, version, effective tier), the tolerance
  actually applied, and a SHA-256 `input_hash` of the normalized inputs
  (`canonical-json-v1`). Error responses carry it too. Additive: no existing key was
  renamed or removed. Spec and a standalone reference script: `docs/PROVENANCE.md`.
- **Golden test suite** (`tests/golden/`, suite v1, 55 cases): `pytest tests/golden -q` runs
  every case in-process *and* through a spawned server started from a temp directory
  (AIEX-499 pattern), checks both give identical output, pins input hashes, and prints a
  pass/fail table. Cases are labeled `lean` / `hand` / `literature` (correctness) versus
  `recorded` (regression only). The one correctness golden today is `cd16_s1_lean`
  (`BilateralCollapse.lean`, `Pattern1_CD4`). Change policy: `tests/golden/README.md`.
- **Profile gates G1–G5** (`profiles/gates.py`, `scripts/check_profile_gates.py`). A profile
  loads as `Official` only if its `GATES.json` exists, every gate passed, and the record
  matches the profile version; otherwise it loads as `Experimental`. `list_domain_profiles`
  now shows `tier` (effective), `requested_tier`, `gate_status`, `gates_passed` and
  `gates_failed` for every profile. Experimental profiles carry `gates_failed` and a plain
  `notice` in `provenance.profile`.
- **Release gate** (`scripts/release_gate.py`, `docs/RELEASE_CHECKLIST.md`): clean tree →
  golden suite → gate records current → clear `build/` and `dist/` → stamp commit and suite
  version → `python -m build`. Clearing matters: setuptools reuses `build/lib`, so a stale
  copy (one from June still held the journalism 2.0.0 files) can put deleted files into
  the wheel, and old wheels in `dist/` would be swept up by `twine upload dist/*`.
- `docs/EVALUATION_CONTRACT.md`: what each verdict means, which threshold decides it, and
  what backs it.
- Manifests: every profile now has `tier` (requested) and `documented_uses`;
  `quant_equity` and `rhi` previously had no `tier`.
- **Plan-based profile access** (access gating Phase 1, `plans.py`). The plan (`tier`)
  returned by the auth server's `/validate` now decides which domain profiles a call may
  use: Individual and Academic get `general_data` and `developer_v1`; Journalist adds
  `journalism`; the Quant plans add `quant_equity`; Commercial and Enterprise get all four.
  The table must match `PLAN_PROFILES` in `auth_server/main.py` (checked by
  `tests/golden/test_access.py`). Applied once, at dispatch:
  - an omitted `profile` gets the plan's default (`journalism` for Journalist,
    `quant_equity` for the Quant plans, otherwise `general_data`). Previously
    `analyze_dataset` defaulted to `quant_equity` for everyone, so a journalist who left it
    out silently got quant output. The `"default"` values were removed from the tool schemas;
  - a profile outside the plan returns `{"success": false, "error": "The <profile> profile
    is not included in the <plan> plan. Included: …. Upgrade: <url>"}`, with provenance;
  - `list_domain_profiles` adds `plan`, `default_profile`, and `included_in_plan` per profile;
  - `provenance.plan` names the plan (`null` for in-process calls without one).
  This runs on the customer's machine, so it is not tamper-proof; Phase 2 (enforcement in
  the auth server) is still open.
- **Closed two bypasses.** `dev_` API keys are accepted only from a source checkout, not
  from the installed package, even with `CAILCULATOR_ENABLE_DEV_MODE=true`. Offline
  fallback (off by default) now grants only the Individual plan's profiles. A plan this
  package doesn't recognize is also treated as Individual.

### Changed — Journalism profile 2.0.0 → 3.0.0 (outputs change)
Heuristics with no backing were removed.
- Dropped the empirical dependency "Tipping Points precede structural collapse"
  (reference: "30+ years reporting expertise"), which was not a tested result.
- Gateway labels "Data Integrity Gateway", "Consensus Tipping Point", "Budgetary Anomaly
  Pathway", "Source Reliability Check", "Policy Shift Indicator", "Public Health Sentinel"
  → `S1`…`S5`.
- Newsroom terminology layer ("Tipping Point", "Systemic Breakdown Warning",
  "Sourcing Confidence", "Narrative Alignment", "Cross-Jurisdictional Stability",
  "breakdown_risk", …) removed; output passes through unchanged at every level.
- New `output_policy: measured_only`. `analyze_dataset` and `zdtp_transmit` (gateway
  `all`) report `classification` / `stability_level` as `"not_assessed"`, replace the
  regime narrative ("potential regime shift in progress", "structural break detected")
  with a plain note, and withhold pattern-detector verdicts (`patterns_detected: 0`,
  `top_patterns: []`, `patterns_withheld` explains why). Under 2.0.0, every journalism
  input tested, including a constant series and seeded noise, was reported as
  "transitioning — potential regime shift in progress". Convergence score, gateway
  magnitudes and the Chavez Transform value are unchanged.
- Coefficient-mapping docstrings no longer claim detection ("Detects Tipping Points",
  "Reveals hidden structural inequality patterns"). The mappings themselves (field →
  channel) are unchanged. No tool currently calls them.

### Changed — Quant Equity profile 2.0.0 → 3.0.0 (outputs change)
The claim that zero divisors detect or predict volatility clustering was removed. It was
never tested: its only reference was "v1.x heuristics". The 1D Chavez Transform value
`analyze_dataset` reports also has a closed form with no zero-divisor content (it gives
bit-identical values for pairs that aren't zero divisors; see `docs/chavez_transform.md`),
so it couldn't have supported the claim.
- Dropped the empirical dependency "Zero divisors predict volatility clustering"
  (reference: "v1.x heuristics").
- Gateway labels "Primary Volatility Anchor", "Multi-Asset Resonance Path", "Bifurcation
  Trigger (A)", "Mean-Reversion Discontinuity", "Bifurcation Trigger (B)", "Structural
  Regime Shift Path" → `S1`…`S5`, as in journalism 3.0.0.
- Terminology layer: algebraic quantities now pass through under their own names. Removed
  translations: `bilateral_zeros` ("Volatility regime shift signals", "Major market mood
  changes", renamed to `regime_shifts` / `mood_changes`), `zero_divisor` ("Structural
  weakness point in data"), `conjugation_symmetry` ("Mean reversion strength", cited
  AIEX-231, which is about prime spectra), `dimensional_persistence` ("Patterns that work
  on multiple chart timeframes") and `transform_convergence` ("Analysis confidence
  score"). Standard technical-indicator terms (RSI, Bollinger, bullish/bearish) remain.
  The `chavez_transform` wording was settled by the 1D closed-form decision (below).
- Scope: manifest "Financial Market Regime Detection" and the `list_domain_profiles`
  text ("volatility anchors") now describe measured quantities.
- Gateway magnitudes, convergence score, the Chavez Transform value and the technical
  indicators are unchanged.

### Changed — documentation and site wording (journalism and quant)
Statements that outlived the removed heuristics (the journalism "30+ years reporting
expertise" dependency, removed in journalism 3.0.0, and the quant claim above) were
brought in line with what the tools compute:
- `GLOSSARY.md`: removed "Tipping Point", "Sourcing Confidence", "Volatility Regime Shift"
  and "Mean Reversion Strength" projections.
- `docs/chavez_transform.md`, `docs/zdtp_protocol.md`: no longer say the transform or ZDTP
  identifies "tipping points", or that `analyze_dataset` returns STABLE / TRANSITIONING /
  SHIFTING (withheld since 2.2.0). The Bitcoin rolling-window result is labeled a
  single-series observation without controls.
- `README.md`: Quant Equity description updated.
- `auth_server/templates/index.html`: profile cards and the Journalist plan no longer
  advertise "tipping point detection", "signal robustness checks" or a regime
  classification.

### Changed — ZDTP and the 1D Chavez Transform labeled as what they compute
Both have exact closed forms that do not involve the zero-divisor property
(`docs/ZDTP_CLOSED_FORM.md`; `docs/chavez_transform.md`, "What the shipped tools
compute"). Paul chose to keep them, relabeled and marked experimental. No value changes,
and no field is renamed or removed.
- **1D Chavez value** (`chavez_transform` tool, `analyze_dataset`): T = Σᵢ dataᵢ·wᵢ with
  wᵢ = ∫₋₅⁵ e^{−(x−tᵢ)²}·8x²e^{−αx²}(1+x²)^{−d/2} dx, a fixed center-weighted sum. Pairs
  that are not zero divisors give bit-identical values (checked at default and non-default
  α and d). The kernel collapse is lemma `K_Z_realToSed` in `ChavezTransform_genuine.lean`.
- **ZDTP** (`zdtp_transmit`, `analyze_dataset`): magnitude_256d(k) =
  √(‖x‖² + 64x₀² + 16sₖ²), sₖ a signed sum of four input components; convergence is
  1 − std/mean of the six.
- **Tool descriptions** for `chavez_transform`, `zdtp_transmit` and `analyze_dataset` state
  the closed forms and say the values are experimental, not structural signals.
- **Additive output notes:** `chavez_transform.note`, `zdtp_transmit.zdtp_note`,
  `analyze_dataset.structural_analysis.chavez_transform_note` and
  `analyze_dataset.zdtp_convergence.note`.
- **Docs:** README, GLOSSARY, `docs/chavez_transform.md` and `docs/zdtp_protocol.md` no
  longer claim structural filtering ("noise collapses near zero"), that the four-factor
  interaction "spans the full interaction space" (it reduces to
  2x₀(P+Q) − 2⟨P+Q,x⟩e₀), that HIGH convergence is "the signature of a genuine structural
  invariant", or the Chavez-then-ZDTP workflow. The Lean convergence theorem is described
  as true but empty (its bound is the transform's own value); the stability bound is the
  substantive result. The RH critical-line convergence results are marked as under
  re-check.
- quant_equity terminology: `chavez_transform` is described as a center-weighted sum, and
  its key is no longer renamed to `pattern_analysis` / `pattern_finder`.

### Changed — other
- `verify_bilateral_oracle` and `map_e8_orbit` responses now include `"success": true`
  (envelope consistency; additive).
- `verify_bilateral_oracle` rejects an unknown `framework` instead of silently computing in
  Cayley-Dickson, and validates `P`/`Q` like the other numeric inputs.
- `analyze_dataset` and `zdtp_transmit` reject an unknown `profile` with an error listing
  the available profiles. They used to run with default behaviour and label the output
  with the requested name (only `provenance.profile.found: false` showed it), which would
  have let `profile: "rhi"` keep "working" after its removal.
- `compute_high_dimensional` refuses an operand longer than the requested `dimension`.
  It used to truncate silently, answering a different question than was asked.
- Missing values (JSON `null`) now get their own error message ("missing value(s)
  (null) at index …") instead of the NaN/Inf message.
- Tool descriptions: `compute_high_dimensional` no longer claims its 1e-10 check is
  "consistent with" the 1e-15 oracle; it states both thresholds. `chavez_transform` now
  says it uses S1 (Canonical Six pattern 1), which is what the code has always done; the
  August description said S2.

### Changed — shared detectors (outputs change for every profile)
The first gate run (below) found the false positives came from code shared by all
profiles. A validated replacement is planned for a later release.
- **Regime verdict withheld.** `analyze_dataset` `regime.classification` and
  `stability_level`, and `zdtp_transmit` (gateway `all`) `convergence.stability_level`, are
  now `"not_assessed"` for every profile, with a note explaining why. The convergence score
  and gateway magnitudes are unchanged and still reported. The old cutoffs (≥ 0.8 / ≥ 0.5)
  carried no information: on G3 null series the score fell in 0.54–0.65, and so did every
  structured series tested, including a 50% step break and a constant series.
  `provenance.tolerance` no longer lists the regime cutoffs.
- **`regime_detection` (unadvertised tool) returns no verdict.**
  `regime_classification.statistical_method` was a hard-coded `"sideways"` (the HMM was
  never implemented), and `structural_method` reported the top detected pattern's name, or
  `"stable"` when there was none. Both are now `"not_assessed"`, `overall_confidence` is
  `null`, and a `note` explains why. `mathematical_structure` is unchanged.
- **Symmetry detectors scored on deviations from the mean.** `conjugate_symmetry`,
  `bilateral_symmetry` and `cyclic_symmetry` used to measure error against the raw norm, so a
  series' level dominated: iid noise around 500 scored ~85% "palindromic". A constant
  offset is palindromic and periodic for every period, so subtracting it changes no true
  pattern's score. A constant series now reports no symmetry; it is still reported as
  `linear_sequence`. Measured: G3 nulls flagged by any pattern detector went from 175/200
  to 0/200. A period-12 sine is still detected with noise at SNR 5. `anti_symmetry` and
  the sequence and polynomial detectors are unchanged.

### Removed — rhi profile
- The `rhi` (Riemann Hypothesis Investigation) profile is removed from the package. It was
  specific to Chavez AI Labs' own RH research, which continues with the general tools. Its
  code (prime embeddings, gateway labels, terminology) is in git history before this
  release.
- Auth server: the Academic plan now includes `general_data` and `developer_v1` (it
  previously offered `rhi`), and the pricing card reads "General Data profile access".
  `rhi` is also removed from the Commercial and Enterprise plans. No existing subscribers
  were affected. Deploy the auth server after the package release.

### Golden suite 1 → 2
- `known_failure` removed from `detect_patterns_null_offset_noise` and from
  `{general_data,quant_equity}_analyze_null_noise`. Their expectations (no findings) were
  already correct; the code now meets them.
- `quant_equity_analyze_gbm`, `general_data_zdtp_all`: expected `classification` /
  `stability_level` changed to `"not_assessed"` (regime verdict withheld, above). No
  measured value changed.
- `quant_equity_analyze_gbm`: `patterns_detected` 2 → 0. The two patterns were
  `cyclic_symmetry` (0.965) and `conjugate_symmetry` (0.943) on a GBM random walk between
  95 and 106: the offset artifact fixed above.
- `rhi_analyze_null_noise` and `rhi_zdtp_log_primes` removed with the profile.

### Golden suite 2 → 3
- Both modes now run under the `developer` plan (the spawned server's dev key gets it, and
  the in-process runner passes it), so their outputs still match. `plan` added to the
  checked provenance keys.
- `quant_equity_analyze_gbm`: `profile: "quant_equity"` is now passed explicitly instead of
  relying on the old `analyze_dataset` default. Expected output and pinned input hash are
  unchanged (the normalized inputs already named the profile). Defaults per plan are tested
  in the new `test_access.py`.

### Golden suite 3 → 4
- `quant_equity_analyze_gbm`: expected gateway labels changed to `S1`…`S5` (quant_equity
  3.0.0, above). Magnitudes, input hash and every other expected value are unchanged.

### Changed — profile tiers
**First gate run** (suite v1, 200 seeded null series, 5% FP ceiling):
general_data, quant_equity and rhi all failed G2 and G3, each with 200/200 null series
flagged and identical findings (`regime:transitioning` 198, `pattern:cyclic_symmetry`
175, `pattern:conjugate_symmetry` 175, `regime:shifting` 2). Identical counts across
profiles meant the cause was the shared detectors, which are fixed above. quant_equity
also failed G1 (the claim "Zero divisors predict volatility clustering" cites "v1.x
heuristics", which is not a test record). rhi also failed G1 (AIEX-229 and AIEX-231 are
cited without their controls) and has since been removed.

**After the detector fixes** (suite v2, same nulls and ceiling):
- **general_data: Official.** Passes G1–G5, 0/200 null series flagged (was 200/200). The
  regime verdict is withheld, so the pass is earned by the pattern detectors, which stay
  active. G3 only checks that noise isn't flagged. A probe showed the fixed detectors still
  find real structure (period-12 sine at SNR 5, palindromes, trends), but no sensitivity
  gate checks that yet (a sensitivity gate, G6, is planned).
- **quant_equity: Experimental.** G2–G5 pass, 0/200 null series flagged (was 200/200).
  Still fails G1: the claim "Zero divisors predict volatility clustering" cites "v1.x
  heuristics", not a test record.
- **journalism (3.0.0): stays Official.** Passes G1–G5 with 0/200 false positives, but
  only because `measured_only` withholds every verdict: it makes no structural claims at
  all. This is not evidence that a detector works.

### Not changed (flagged for Paul)
- The two zero-divisor thresholds (1e-10 vs 1e-15) are unchanged and now documented. The
  decision is open (see `EVALUATION_CONTRACT.md`).

## [Unreleased — August audit, folded into 2.2.0]

### Context
Joint audit session (this session + a parallel Claude Desktop session) investigating a suspected anomaly in Chavez Transform usage, prompted by a prior chat that flagged something off in the Riemann Hypothesis Investigation work. Investigation ran 2026-08-21 to 2026-08-22. Not yet pushed to GitHub or published to PyPI — still pending the MCP 2.0 protocol update and independent reproduction of the "Detector Encoding baseline" / "Q-18 ensemble" figures referenced by the Desktop audit (see Investigated, below).

### Fixed
- **Input validation hardening** (`tools.py`): added a shared `_parse_numeric_data()` helper, now used by `chavez_transform`, `detect_patterns`, and `analyze_dataset`. Rejects non-numeric elements and non-finite values (NaN/Inf) with a clear `ValueError` message instead of leaking a raw numpy `ufunc` `TypeError`. Also closes a silent-corruption gap in `analyze_dataset`, which previously converted with `dtype=float` and never checked finiteness afterward — a numeric-looking string like `"NaN"` or `"Infinity"` was silently parsed into a real NaN/Inf and passed downstream undetected.
- **Not yet live**: this fix is in the source tree (editable install) but the currently-running MCP server process (in both this session and Claude Desktop) loaded the old module before the edit — Python doesn't hot-reload. Requires restarting/reconnecting the `cailculator-mcp` server in each client to take effect. Not yet re-verified post-restart.

### Documentation
- **`chavez_transform` tool schema**: `dimension_param` is now documented as the exponent in the dimensional-weighting term Ω_d(x) = (1+‖x‖²)^(-d/2) — a numerical-integration decay hyperparameter, **not** the hypercomplex algebra dimension (which is hardcoded to 32 regardless of this value). Tool description also now notes the transform is reversal-symmetric and amplitude-driven, and should not be used alone as a structural/pattern-detection signal.
- **Internal Riemann analysis notes**: added a retraction header (dated 2026-08-21). The document's headline "Dimensional Persistence" finding — cited as supportive evidence for the Riemann Hypothesis — is invalid; see Investigated below for the root cause. Document body preserved for historical reference, not deleted.

### Investigated (no code change)
- **Root cause of the RH-analysis anomaly**: the archived "Dimensional Persistence" finding (CV≈0.146, ~33% decrease sweeping `dimension_param` 1→5) is a mathematical artifact of the Ω_d weighting formula, not a property of prime numbers. Confirmed via a null-hypothesis control: sweeping the same range on the first 100 primes, 100 random integers, and a flat constant array all produced statistically indistinguishable decay curves (CV≈0.41 in every case, using the current transform). A second, independent proof: the transform's 1D kernel is exactly invariant under reversing the input sequence (the kernel is quadratic/even in the scalar embedding, and the integration domain is symmetric) — verified both algebraically and empirically to 10 significant figures. The pattern types the archived report cites ("Dimensional Persistence", "Conjugation Symmetry") no longer exist anywhere in `patterns.py`, which was fully rewritten in the v2.0 refactor.
- **Blast-radius check**: confirmed by reading code (not assuming) that the ZDTP full-cascade / convergence-score pathway (`zdtp/protocol.py`) and `detect_patterns` do not share any code path with `dimension_param`/`Omega_d` — both instantiate a `ChavezTransform` object in `__init__` but never call a method on it (dead references). `analyze_dataset`'s regime classification and convergence score come from the ZDTP layer, not the Chavez Transform layer, and are unaffected. **Pending**: could not find "AIEX-742", "Detector Encoding baseline" (z=8.42, AUC=0.866), or "Q-18 ensemble" anywhere in this repository — cited by the parallel Desktop audit but unverifiable from source here; presumed external research notes, not fabricated, but not independently confirmed.
- **Full Canonical Six × both frameworks** bilateral zero-divisor re-verification (S1, S2, S3A, S3B, S4, S5) — all results match the documented Class A/B partition; S2 reconfirmed as the only pair bilateral in both Cayley-Dickson and Clifford frameworks; all others show the identical unilateral residual (‖QP‖ = 2√2) in Clifford.
- **S3A≡S3B kernel-degeneracy** spot check (single test point) — confirmed equal (K_Z=8 both), consistent with AIEX-610. S4≡S5 not independently re-derived this session.
- **`chavez_transform` edge cases**: empty array, alpha boundary (0, -1, exactly 5.0, 5.0000001), and determinism (3x identical input, bit-identical output) all behave as documented, aside from the input-validation gap fixed above.

---

## [1.4.4] - 2026-04-17

### 🏆 THE FORMAL VERIFICATION MILESTONE
This release marks the transition of CAILculator from an empirical research project to a **formally verified** mathematical library. Core algebraic properties and transform behaviors are now backed by machine-verified Lean 4 proofs.

### Added
- **Formal Proofs**: Integrated `lean/ChavezTransform_genuine.lean` containing zero-sorry proofs for:
  - **Theorem 1 (Convergence)**: Unconditional absolute convergence for the Chavez Transform kernel.
  - **Theorem 2 (Stability)**: Proved tighter stability bound $M = 2 \cdot (\|P\|^2 + \|Q\|^2) / (\alpha \cdot e)$.
  - **Theorem 3 (Pattern Invariance)**: Proved that patterns identified on scalar inputs scale predictably to high-dimensional spaces.
- **Pattern Detector Theorem Citation**: Added explicit citations to `src/cailculator_mcp/patterns.py` linking code implementation to Lean proofs.
- **Parametric Domain Notation**: Updated `demo_zdtp.py` to reflect the parametric nature of the integration domain $D$.

### Changed
- **Stability Constant Implementation**: Updated `src/cailculator_mcp/transforms.py` to use the tighter, formally proved constant $M$ instead of earlier empirical estimates.
- **Documentation Overhaul**: Main `README.md` now features the "Badge of Honor" Lean verification section.
- **Sanitization**: Moved internal development artifacts and session payloads to `docs/devnotes/` to provide a cleaner public repository structure.

### Fixed
- **Clifford Integration**: Verified and tested `CliffordElement` multiplication logic to ensure 100% parity with formal bridge patterns.
- **Illustrate Tool**: Confirmed path resolution and visualization generation for Windows/Linux compatibility.

---
**Chavez AI Labs** - *"Better math, less suffering"*
