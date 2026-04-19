import Mathlib

/-!
# Phase 66/67 Audit — Euler Product Infrastructure in Mathlib v4.28.0
Author: Paul Chavez, Chavez AI Labs LLC
Date: April 2026

Audits what Mathlib has for the Euler product of the Riemann zeta function.
This file makes no changes to the CAIL stack. It is a pure reference audit.

## Confirmed Available (Phase 66 audit)

- `riemannZeta_eulerProduct` — basic Euler product statement
- `riemannZeta_eulerProduct_hasProd` — HasProd form
- `riemannZeta_eulerProduct_tprod` — tprod form: ∏' p : Primes, (1−p^{−s})⁻¹ = ζ(s) for Re(s) > 1
- `riemannZeta_eulerProduct_exp_log` — exp(∑' p, −log(1−p^{−s})) = ζ(s) for Re(s) > 1
- `riemannZeta_one_sub` — full functional equation with Γ/cos prefactors
- `riemannZeta_ne_zero_of_one_le_re` — ζ(s) ≠ 0 for Re(s) ≥ 1
- `differentiableAt_riemannZeta` — holomorphic (s ≠ 1)

## NOT in Mathlib v4.28.0

- Any theorem about the location of non-trivial zeros (RH is open)
- Hardy's theorem (infinitely many zeros on the critical line)
- Zero-free region beyond Re(s) ≥ 1
- `riemannZeta_zero_symmetry` in a directly applicable form
-/

set_option maxHeartbeats 800000

section EulerAudit

open Complex

-- ================================================================
-- Euler product theorems (all in Mathlib.NumberTheory.EulerProduct.DirichletLSeries)
-- ================================================================

#check @riemannZeta
#check @riemannZeta_eulerProduct
#check @riemannZeta_eulerProduct_hasProd
#check @riemannZeta_eulerProduct_tprod
-- tprod form: ∀ {s : ℂ}, 1 < s.re → ∏' (p : Nat.Primes), (1 - ↑↑p ^ (-s))⁻¹ = riemannZeta s
#check @riemannZeta_eulerProduct_exp_log
-- exp-log form: ∀ {s : ℂ}, 1 < s.re →
--   Complex.exp (∑' (p : Nat.Primes), -Complex.log (1 - ↑↑p ^ (-s))) = riemannZeta s

-- ================================================================
-- Functional equation and analytic properties
-- ================================================================

#check @riemannZeta_one_sub
-- riemannZeta_one_sub : ∀ (s : ℂ), ↑(Gamma s) ≠ 0 →
--   riemannZeta (1 - s) = 2 ^ s * π ^ (s - 1) * sin (π * s / 2) * Gamma s * riemannZeta s

#check @differentiableAt_riemannZeta
-- holomorphic at s ≠ 1

-- Non-vanishing on Re(s) ≥ 1:
#check @riemannZeta_ne_zero_of_one_le_re
-- riemannZeta_ne_zero_of_one_le_re : ∀ {s : ℂ}, 1 ≤ s.re → s ≠ 1 → riemannZeta s ≠ 0

-- ================================================================
-- Phase 69 relevance
-- ================================================================

-- The Euler product holds only for Re(s) > 1.
-- Non-trivial zeros are in the critical strip 0 < Re(s) < 1.
-- A proof of euler_sedenion_bridge requires connecting:
--   (1) Euler product structure (Re(s) > 1)
--   (2) to zero behavior (Re(s) < 1)
-- via analytic continuation — the genuine open analytic step.

end EulerAudit
