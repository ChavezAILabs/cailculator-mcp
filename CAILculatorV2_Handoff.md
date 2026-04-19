# CAILculator v2.0 — Architecture Handoff

**From:** Claude Desktop (strategy, KSJ)
**To:** Gemini CLI (planning mode)
**Date:** April 19, 2026
**Status:** v2.0 planning, pre-implementation
**KSJ reference range:** AIEX-441 through AIEX-511

---

## 1. Purpose of this document

Gemini CLI has the Lean audit and a three-option architecture fork on the table. This handoff narrows the architecture decision, specifies the scope of "eliminate all heuristics," and gives a concrete target for planning-mode output: a detailed v2.0 architecture plan that can be reviewed before implementation begins.

This document consolidates decisions reached with Claude Desktop on April 19, 2026. Where decisions are open, they are flagged as **OPEN**. Where decisions have been made, they are flagged as **DECIDED**.

---

## 2. Why v2.0 exists — the v1.4.7 bug cluster

Four distinct failures on April 18–19, 2026, drove the decision to overhaul the engine rather than patch v1.x. All four share a single root cause: **the Python surface has drifted from the Lean-verified mathematical core.**

| KSJ ID | Bug | Diagnosis |
|---|---|---|
| AIEX-505 (!critical) | Canonical Six dispatch collapse — all six `pattern_id` values return bit-identical output on asymmetric input | Parameter parsed and echoed but not dispatched to distinct algebraic definitions |
| AIEX-506 | Stability bound `\|C[f]\| ≤ 8/(α·e)` holds at α=0.1 but violates at α=1.0 by 47.3% | Python empirics contradict a Lean-proved bound |
| AIEX-507 | 256D transport inflation — verified 256-length arrays rejected with inconsistent 261/267 coefficient reports | Transport-layer corruption between client and computation core |
| AIEX-510/511 | Alpha_sensitivity regression + 176s throughput degradation after timeout | Release notes decoupled from runtime behavior |

**Architectural lesson (AIEX-501):** Verified math survives broken tooling when data flows from the verified core. Data flowing from ad-hoc Python does not. This is the guiding principle for v2.0.

---

## 3. Architecture decision — DECIDED

v2.0 adopts a **hybrid of Options 1 and 3 from Gemini's original audit**, staged in three phases:

### Phase A — Oracle Layer (Lean as Source of Truth)
Build dedicated MCP tools backed by Lean-proved theorems. These are the ground-truth oracles:

- `verify_bilateral_collapse(P, Q)` — runs `P·Q = 0` check via proved multiplication table
- `stability_constant(P, Q, α)` — returns `2(‖P‖²+‖Q‖²)/(α·e)`, the Lean-proved bound (AIEX-478, AIEX-484)
- `kernel_distance(x)` — via `commutator_exact_identity`: `‖[u_antisym, x]‖ = 2·dist(x, ker)` (AIEX-215, AIEX-444)
- `chavez_transform(f, P, Q, α, d)` — with stability bound checked at output time (AIEX-476)
- `get_canonical_six()` — returns the six (P,Q) pairs from the Lean source of truth
- `identify_gateway(P, Q)` — returns which canonical pattern a given pair is (or is not)
- `map_to_weyl_orbit(v)` — E8 Weyl orbit projection (from `e8_weyl_orbit_unification.lean`)

### Phase B — Oracle-Backed Acceptance Suite
Use the oracle tools to write test cases that the v1.4.7 bugs would fail:

- Dispatch collapse test: oracle returns pattern-distinct outputs on asymmetric input; Python must match
- Stability bound test: oracle gives `2(‖P‖²+‖Q‖²)/(α·e)`; Python must never exceed
- 256D transport test: oracle accepts length-256 arrays; Python must too
- Release-notes-vs-behavior drift: oracle output is the spec; release notes describe oracle behavior

### Phase C — Selective Strict Replacement
Replace heuristics in `transforms.py`, `regime_detection.py`, `patterns.py` one module at a time, each gated by oracle agreement. Only replace where an oracle-backed test exists.

### Why not pure Option 2 (parallel engines)?
Rejected. AIEX-505 produces bit-identical output across patterns — a delta-comparison test against v1 would pass silently if v2 reproduced the same collapse. Parallel-engine strategies need **ground-truth tests**, not just delta checks. The oracle layer is that ground truth.

---

## 4. Lean file inventory — DECIDED

From the April 19 audit of `C:\Users\chave\PROJECTS\cailculator-mcp\lean`:

### Core Engine (ship in v2.0)
- `ChavezTransform_genuine.lean` — stability, convergence, `K_Z_realToSed` exact formula
- `BilateralCollapse.lean` — `P·Q = 0` algebraic collapse, bilateral_collapse_iff_RH

### Extended Structures (ship in v2.0 as new capabilities)
- `canonical_six_parents_of_24_phase4.lean`
- `g2_family_24_investigation.lean`
- `e8_weyl_orbit_unification.lean`
- `master_theorem_scaffold_phase5.lean`

### RH Investigation Stack (reserve inventory, expose selectively)
- 14 files including `RHForcingArgument.lean`, `MirrorSymmetry.lean`, `NoetherDuality.lean`, `AsymptoticRigidity.lean`, etc.
- **Do not discard.** `commutator_exact_identity` is the bilateral kernel in operator form and is useful beyond RH. Expose `kernel_distance(x)` in v2.0; reserve others for v2.1+.

### Deprecated (archive, do not import)
- `ChavezTransform_Specification_aristotle.lean` — vacuous (CD4_mul = 0; see AIEX-441, AIEX-482)
- `EulerAudit.lean`, `c038a2e4-alternative.lean`, `dc08bbac-primary.lean`, `output.lean`

**Critical check:** `#print axioms` is not sufficient for integration — it must be paired with non-triviality verification. The vacuous Aristotle file had zero sorries and passed `#print axioms` but was semantically empty. Every oracle tool must have a test proving it produces distinct outputs on distinct inputs.

---

## 5. The universal/domain boundary — DECIDED

The deepest architectural insight from April 19 planning:

**ZDTP and related analyses have two layers that v1.x conflated:**

1. **Universal algebraic layer** — the Canonical Six (P,Q) pairs, bilateral annihilation P·Q=0, E8 Weyl orbit structure, `(A₁)⁶` subspace, shared-Q dual structure. Lean-proved. Domain-independent.

2. **Domain projection layer** — what gets mapped into the six gateways. RHI: {log 2, log 3, log 5, ..., γₙ}. Quant: {price_open, price_close, volume, volatility, ...}. Climate: {temperature, pressure, humidity, ...}. Each domain has its own coefficients, labels, and interpretation.

**"S5 = Transformation Gateway" is not universal.** It is a domain-specific label. The gateway's algebraic identity (a specific (P,Q) pair) is universal; its semantic label depends on what project is running.

---

## 6. Domain profile system — DECIDED

v2.0 introduces **domain profiles** as first-class objects. The verified core stays universal; the domain layer becomes pluggable.

### Profile schema (required fields)

```
name                       # "rhi" | "quant_equity" | "climate_reanalysis" | ...
version                    # semver; referenced in KSJ entries for reproducibility
scope                      # one-line description
coefficient_mapping        # rules mapping domain fields → sedenion components
gateway_labels             # {S1: "Master Gateway", S2: ..., S6: ...} with (P,Q) anchors
used_theorems              # Lean theorems this profile invokes
empirical_dependencies     # empirical relationships, each with evidence reference
invariants                 # input data constraints (e.g., price > 0)
terminology                # three-tier: technical / standard / simple
interpretation_rules       # domain-specific decision logic (see Section 8)
```

### Directory layout

```
cailculator/
  core/                          # universal, Lean-anchored
    chavez_transform.py
    bilateral_collapse.py
    canonical_six.py
    stability.py
  profiles/
    quant_equity/
      __init__.py                # profile manifest
      terminology.py             # refactored from v1.x terminology.py
      indicators.py              # refactored from v1.x quant_indicators.py
      interpretation.py          # _interpret_* functions
      coefficient_mapping.py     # OHLCV → sedenion
    rhi/
      __init__.py
      terminology.py
      prime_embeddings.py        # log p → ROOT_16D
      zero_analysis.py           # γₙ, gateway labels, S3B=S4
      gateway_labels.py          # Master/Transformation/Diagonal-A/B with (P,Q) anchors
    template/                    # skeleton for creating new profiles
      __init__.py
      terminology.py
      README.md
```

### MCP tools for profile management

- `list_profiles()` — enumerate available profiles
- `load_profile(name, version=None)` — load profile for current session
- `describe_profile(name)` — return manifest contents for inspection
- `validate_input(profile, data)` — check input data against profile invariants

### Ship with two reference profiles from day one

- **RHI profile** — built from the existing investigation. Inventories Master/Transformation/Diagonal-A/Diagonal-B labels with (P,Q) anchors, prime exponential coefficient mapping, S3B=S4 as declared empirical invariant (AIEX-229), log-periodic convergence oscillation as declared empirical relationship (AIEX-231).
- **Quant_equity profile** — refactored from v1.x `terminology.py` and `quant_indicators.py`. OHLCV coefficient mapping, RSI/MACD/Bollinger interpretation rules, finance terminology translations.

Two reference implementations prove the profile system generalizes. One proves nothing.

---

## 7. Elimination of heuristics — DECIDED scope

"Eliminate all heuristics" does **not** mean strip all names. It means:

1. **Every name must be a label on a formally defined object.** Gateway S1 is labeled `Master Gateway` in the RHI profile; the underlying (P,Q) pair is Lean-proved. The label is rendered in output; the pair is dispatched on.

2. **Every runtime decision must dispatch on the object, never on the label.** `pattern_id` becomes `(P, Q)` or `profile_gateway_key`, never a semantic string.

3. **Every empirical relationship must be labeled empirical.** S3B=S4 is proved (AIEX-229) and lives in `used_theorems`. Log-periodic oscillation is empirical (AIEX-231) and lives in `empirical_dependencies` with evidence reference.

4. **Every domain translation (e.g., `bilateral_zeros → volatility_regime_shift` in v1.x terminology) is audited as a domain hypothesis** and assigned:
   - evidence reference (KSJ entry, paper, backtest)
   - confidence tier (high / medium / low)
   - fallback behavior when evidence is weak

### Audit task for Phase A (concrete deliverable)

Produce the mapping table `{S1, S2, S3A, S3B, S4, S5, S6} → (P, Q) pair → Lean theorem name → current semantic labels per profile}`. Any row where the Lean theorem is missing or ambiguous is a heuristic that must be eliminated or formally adopted.

**Known open item:** AIEX-509 recorded model-level uncertainty about Canonical Six membership (shared-Q pairs initially mis-classified). The S1–S6 labeling may have absorbed some of this uncertainty. The audit table is how that gets pinned down.

---

## 8. Specialized files vs on-the-fly generation — DECIDED

**Specialized files exist. They are not generated on the fly.**

Rationale:

1. **Domain knowledge is irreducible.** RSI thresholds at 30/70, MACD crossover semantics, gateway-label interpretation — these are conventions honed over years, not derivable from first principles.
2. **Reproducibility requires it.** A KSJ entry referencing a v1.x interpretation must trace back to a specific, versioned implementation. On-the-fly generation breaks this.
3. **Library orchestration requires it.** `pandas_ta` column-name drift (visible in `quant_indicators.py` lines 117–134) is pragmatic glue code that cannot be generated reliably mid-session.
4. **Audit trails require it.** Domain hypotheses need evidence references attached to code, not invented at runtime.

**What is legitimately on-the-fly:** configuration *within* a profile's declared schema. Column bindings, threshold overrides, terminology level. These are parameters, not new code.

### Profile quality tiers (for future)

- **Official profiles** — maintained by Chavez AI Labs, guaranteed compatible with verified core releases (RHI, quant_equity initially)
- **Community profiles** — contributable via template, marked clearly in `list_profiles()` output
- **Profile certification process** — v2.5+ feature

---

## 9. v1.x code disposition — DECIDED

| v1.x file | v2.0 disposition |
|---|---|
| `terminology.py` | Refactored into `profiles/quant_equity/terminology.py`. Keep three-tier tech/standard/simple structure; scope to finance domain; add evidence references to all domain-claim translations. |
| `quant_indicators.py` | Refactored into `profiles/quant_equity/indicators.py` + `profiles/quant_equity/interpretation.py`. Preserve RSI/MACD/Bollinger logic; preserve `_prepare_dataframe` data-shape handling; separate indicator calculation from interpretation. |
| `transforms.py` | Replaced module-by-module in Phase C, gated by oracle agreement. Heuristic pattern detection removed in favor of Lean-anchored dispatch. |
| `regime_detection.py` | Replaced module-by-module in Phase C. Premium dual-method regime detection preserved as empirical tool, clearly marked as such. |
| `patterns.py` | Replaced with `core/canonical_six.py` (Lean-anchored definitions) + `profiles/*/gateway_labels.py` (domain labels). |
| `zdtp/*` | Universal transmission logic goes to `core/`; gateway semantic labels go to profile `gateway_labels.py`. The shared-Q dual structure (AIEX-508) is Lean-proved and goes to core. |

---

## 10. Acceptance criteria for v2.0 — DECIDED

v2.0 ships when all four of the following are true:

1. **All four v1.4.7 bugs are structurally impossible.** Not fixed — structurally impossible. Dispatch collapse cannot happen because dispatch is on (P,Q) objects, not labels. Stability violations cannot happen because output is checked against the Lean-proved bound. Transport inflation cannot happen because the core validates array length before transport. Release-note drift cannot happen because the oracle *is* the spec.

2. **Two reference profiles ship.** RHI profile and quant_equity profile, both with full manifests, tested against the core.

3. **Oracle-backed acceptance suite passes.** Every oracle tool has tests proving it produces distinct outputs on distinct inputs (non-triviality check to guard against vacuous-theorem failure mode).

4. **CI includes subprocess-with-adversarial-CWD tests.** Per AIEX-499: spawn MCP server from a non-repo working directory and verify illustrate / asset-resolving tools still work. CWD inheritance is a latent vulnerability class that caught v1.x and must be pinned.

---

## 11. Requests for Gemini CLI planning mode

Please produce the following as planning-mode output. Each is a prerequisite to implementation, not part of implementation itself.

### 11.1 Architectural plan
- Module-level dependency graph for the v2.0 layout in Section 6
- Oracle tool interface specifications (signatures, return types, error modes)
- Profile manifest schema (formal specification, likely as JSON Schema or Pydantic model)
- Interface contract between `core/` and `profiles/*`

### 11.2 Migration plan
- Module-by-module migration order for Phase C (which `transforms.py` / `regime_detection.py` functions get oracle-gated first)
- Data format compatibility strategy (v1.x users continuing during transition)
- Deprecation timeline for v1.x MCP tools

### 11.3 Acceptance test specifications
- Concrete test cases for each of the four v1.4.7 bug classes
- Non-triviality test template (to prevent vacuous-Lean-theorem failures)
- CWD-hardness test specification

### 11.4 Gateway audit table
- Enumerate all current S1–S6 / Master / Transformation / Diagonal-A / Diagonal-B labels found in v1.x code
- Pair each with (P, Q) from the Lean canonical six
- Pair each with the Lean theorem that proves the pair's properties
- Flag any label with missing or ambiguous Lean backing as a heuristic-elimination target

### 11.5 RHI profile specification
- Full manifest per Section 6 schema
- Gateway labels with (P,Q) anchors
- Coefficient mapping for primes and Riemann zeros
- Declared theorems (list all Lean-proved results the profile invokes)
- Declared empirical dependencies (S3B=S4, log-periodic convergence, Q-vector outperformance, etc.) with KSJ references

### 11.6 Quant_equity profile specification
- Full manifest per Section 6 schema
- Terminology refactored from v1.x `terminology.py` with evidence references added to every domain-claim translation
- Indicator and interpretation logic refactored from v1.x `quant_indicators.py`
- Coefficient mapping for OHLCV and common derived features

---

## 12. Non-goals for v2.0

- RH proof completion. `riemann_critical_line` remains an axiom. v2.0 is an engine overhaul, not an RH milestone.
- Chavez Transform paper publication. Paper is tracked separately; v2.0 provides the callable API the paper describes.
- Community profile contribution workflow. Design for it (template directory) but do not build it. v2.5+ feature.
- New MCP tools beyond the oracle layer and profile management. Additional tools can ship in v2.1+ once the architecture is proven.
- Performance optimization. v2.0 is correctness-first. Benchmarking and optimization are v2.1.

---

## 13. Dependencies and references

- **KSJ entries:** AIEX-441, AIEX-476 through AIEX-511 for April 2026 context; AIEX-215, AIEX-229, AIEX-231, AIEX-357, AIEX-358, AIEX-408, AIEX-444, AIEX-478, AIEX-484, AIEX-501, AIEX-508, AIEX-509 for specific technical anchors.
- **Lean repository:** `C:\Users\chave\PROJECTS\cailculator-mcp\lean` — 26+ files audited April 19, 2026.
- **v1.x code under refactor:** `terminology.py`, `quant_indicators.py`, `transforms.py`, `regime_detection.py`, `patterns.py`, `zdtp/*`.
- **Verified core anchor:** `ChavezTransform_genuine.lean` (0 errors, 0 sorries, standard axioms only as of Phase 71 Part 2).

---

## 14. Workflow protocol

- **Claude Code writes Lean files; Aristotle verifies them. Never the reverse.**
- **Claude Desktop (strategy, KSJ) and Gemini CLI (planning, pre-handoff analysis) operate on handoff documents like this one.**
- **Every phase closes with a KSJ extract_insights → user approval → commit_aiex cycle. No auto-commits.**
- **Platform-agnostic handoff docs (per AIEX-283) — track labels, not AI labels, so the workflow survives platform changes.**

---

*End of handoff document.*
