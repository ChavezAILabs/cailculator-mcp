# ChavezTransform_genuine.lean — Gemini CLI Handoff
**Date:** April 16, 2026  
**From:** Claude Code session (hit context limit)  
**To:** Gemini CLI (or next Claude session)

---

## What Was Done

`ChavezTransform_genuine.lean` has been **written and copied to the build directory**.  
This is the companion paper Lean file for the Chavez Transform formalization.  
It supersedes `ChavezTransform_Specification_aristotle.lean` (UUID 0bfec79d), where  
`CD4_mul` was defined as zero (vacuous), making all theorems trivial.

**Both locations are in sync (identical files):**
- Canonical: `C:\dev\projects\Experiments_January_2026\Primes_2026\CAIL-rh-investigation\lean\ChavezTransform_genuine.lean`
- Build dir:  `C:\dev\projects\Experiments_January_2026\Primes_2026\AsymptoticRigidity_aristotle\ChavezTransform_genuine.lean`

**`lakefile.toml` already updated** — the `ChavezTransformGenuine` target is registered:
```toml
[[lean_lib]]
name = "ChavezTransformGenuine"
globs = ["ChavezTransform_genuine"]
```

---

## What You Need to Do

### Step 1: Run the build (Paul runs this in PowerShell)

```powershell
cd 'C:\dev\projects\Experiments_January_2026\Primes_2026\AsymptoticRigidity_aristotle'
lake exe cache get
lake build ChavezTransformGenuine
```

### Step 2: Check axioms

Create `axiom_check_ct.lean` in the project root:
```lean
import ChavezTransformGenuine
#print axioms chavez_transform_stability
```

Then run:
```powershell
lake env lean axiom_check_ct.lean
```

**Expected output:** `[propext, Classical.choice, Quot.sound]` — no `riemann_critical_line`, no `sorryAx`.

### Step 3: Report

Report verbatim:
- Job count (e.g. `8,054 jobs`)
- Error count (target: `0 errors`)
- Sorry count (target: `0 sorries`)
- Full `#print axioms` output

---

## File Architecture (290 lines)

```
§1  mul_apply         — (P*Q).k = ∑ i j, table formula; proved by Real.ext_cauchy rfl
§2  Table facts        — sedMulTarget_col0/row0, sedMulSign_col0/row0 via decide on ∀ forms
§3  e₀ identity        — sed_mul_sedBasis0, sedBasis0_mul_sed via Finset.sum_eq_single
§4  realToSed          — def + sed_mul_realToSed, realToSed_mul_sed (uses sed_mul_smul_right/left)
§5  Kernel defs        — K_Z (bilateral), K (K_Z * Gaussian * power-law)
§6  Exact K_Z formula  — K_Z P Q (realToSed x) = 2*x²*(‖P‖²+‖Q‖²); nlinarith [sq_abs x, ...]
§7  Helper bounds      — exp_decay_le_one, rpow_decay_le_one, mul_exp_neg_le, sq_mul_exp_neg
§8  Transform defs     — L1_norm, stability_constant, chavez_transform_1d (all on Set.Ioc a b)
§9  K nonneg/bounded   — K_Z_nonneg, K_nonneg, K_bound
§10 Main theorems      — chavez_transform_convergence (trivial ⟨_, le_refl _⟩)
                        chavez_transform_stability (MeasureTheory integral bound)
```

---

## Key Design Decisions (do not change)

1. **`realToSed x = x • sedBasis 0`** — embeds ℝ into Sed via scalar channel e₀.  
   This gives the exact formula `K_Z P Q (realToSed x) = 2*x²*(‖P‖²+‖Q‖²)` without needing `sed_norm_mul_le`.

2. **e₀ is a two-sided identity** — proved from the `sedMulTarget`/`sedMulSign` table via `decide` on universally-quantified propositions.

3. **Domain is `Set.Ioc a b`** (half-open interval), NOT `Set.Icc`. This matches `IntervalIntegrable` which uses `Set.uIoc`.

4. **`stability_constant P Q α = 2*(‖P‖²+‖Q‖²)/(α·e)`** — derived from `x²·exp(-αx²) ≤ 1/(α·e)` via `mul_exp_neg_le`.

5. **`le_div_iff₀`** (not `le_div_iff`) — correct Mathlib 4.28 name.

6. **`sed_mul_smul_right/left`** from `RHForcingArgument.lean` lines 449/459 — must import `RHForcingArgument`.

---

## If the Build Fails

### Likely residual issues and fixes:

**A. `mul_apply` fails** (`Real.ext_cauchy rfl` doesn't close goal):
- Try: `native_decide` (for a closed-form check) or `rfl` directly
- Or unfold `instMulSed` manually and use `funext k; simp [PiLp.toLp_apply]`

**B. `Finset.sum_eq_single` goal shape mismatch** (in sed_mul_sedBasis0/sedBasis0_mul_sed):
- The `intro j _ hj; simp [hj]` branch needs the outer `if` to be `0` when `j ≠ 0`
- Try: `split_ifs with h1 h2 <;> simp_all` instead

**C. `integral_mono_of_nonneg` argument order wrong**:
- Check: in Mathlib 4.28, `MeasureTheory.integral_mono_of_nonneg` takes `(hf : 0 ≤ f)` first, then integrability, then `(h : f ≤ g)`
- If signature changed, try `integral_mono` with explicit positivity side-goal

**D. `h_integrable.norm.1.const_mul _` type error**:
- `IntervalIntegrable.norm` gives norm integrability
- `.1` extracts `MeasureTheory.IntegrableOn` for `Set.Ioc`
- `.const_mul` multiplies by a constant
- Alternative: `(h_integrable.norm.1).smul_const _` or build integrability manually

**E. `positivity` fails somewhere**:
- `stability_constant P Q α`: unfold first, then `positivity` (needs `0 < α`)
- `K_nonneg`: the `unfold K K_Z; apply mul_nonneg; apply mul_nonneg` chain should work

---

## Context: Where This Fits

This is the **Chavez Transform companion paper** Lean file.  
The main RH stack (13 files in `AsymptoticRigidity_aristotle/`) has:
- `[riemann_critical_line, propext, Classical.choice, Quot.sound]` axiom footprint
- 8,051 jobs · 0 errors · 0 sorries (verified April 15, 2026)

`ChavezTransform_genuine.lean` is a **standalone companion** — it proves the transform is well-defined and stable without touching the RH axiom. Its axiom footprint should be `[propext, Classical.choice, Quot.sound]` only.

The file imports `RHForcingArgument` (for `Sed`, `instMulSed`, `sedBasis`, `sed_mul_smul_right/left`). It does NOT import `RiemannHypothesisProof` or `ZetaIdentification`.

---

## Files Do NOT Touch

Per `CLAUDE.md`: Files 1–9 of the main stack are frozen (zero sorries, phases closed).  
Do not modify `RHForcingArgument.lean` or any other file in the main 13-file stack.

---

*Chavez AI Labs LLC — Applied Pathological Mathematics*
