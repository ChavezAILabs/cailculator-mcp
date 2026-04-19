import NoetherDuality
import Mathlib

/-!
# RH Investigation Phase 59 — Pillar 1: Universal Perimeter
Author: Paul Chavez, Chavez AI Labs LLC
Date: April 4, 2026

Defines the 24-member zero-divisor cage and the Universal Trapping Lemma.
-/

noncomputable section

open Real InnerProductSpace

/-- The 24-member bilateral zero-divisor family (48 signed pairs). -/
def is_perimeter_vector (v : Sed) : Prop :=
  ∃ i j : Fin 16, i ≠ j ∧
  (v = sedBasis i + sedBasis j ∨ v = sedBasis i - sedBasis j)

/-- The Perimeter Set. -/
def Perimeter24 : Set Sed := { v | is_perimeter_vector v }

/-- Canonical ROOT_16D prime root vectors. -/
def root_2  : Sed := sedBasis 3 - sedBasis 12
def root_3  : Sed := sedBasis 5 + sedBasis 10
def root_5  : Sed := sedBasis 3 + sedBasis 6
def root_7  : Sed := sedBasis 2 - sedBasis 7
def root_11 : Sed := sedBasis 2 + sedBasis 7
def root_13 : Sed := sedBasis 6 + sedBasis 9

private lemma hi4_lemma (t σ : ℝ) :
    @inner ℝ Sed _ (sedBasis 4) (F_param t σ) = (σ - 1/2) / Real.sqrt 2 := by
  unfold F_param F_base u_antisym sedBasis
  simp [inner_add_right, inner_smul_right, inner_sub_right,
        EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]
  norm_num; ring

private lemma hi5_lemma (t σ : ℝ) :
    @inner ℝ Sed _ (sedBasis 5) (F_param t σ) = -(σ - 1/2) / Real.sqrt 2 := by
  unfold F_param F_base u_antisym sedBasis
  simp [inner_add_right, inner_smul_right, inner_sub_right,
        EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]
  norm_num; ring

private lemma hi10_lemma (t σ : ℝ) :
    @inner ℝ Sed _ (sedBasis 10) (F_param t σ) = (σ - 1/2) / Real.sqrt 2 := by
  unfold F_param F_base u_antisym sedBasis
  simp [inner_add_right, inner_smul_right, inner_sub_right,
        EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]
  norm_num; ring

private lemma hi0_lemma (t σ : ℝ) :
    @inner ℝ Sed _ (sedBasis 0) (F_param t σ) = Real.cos (t * Real.log 2) := by
  unfold F_param F_base u_antisym sedBasis
  simp [inner_add_right, inner_smul_right, inner_sub_right,
        EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]

private lemma hi3_lemma (t σ : ℝ) :
    @inner ℝ Sed _ (sedBasis 3) (F_param t σ) = Real.sin (t * Real.log 2) := by
  unfold F_param F_base u_antisym sedBasis
  simp [inner_add_right, inner_smul_right, inner_sub_right,
        EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]

/--
**The Universal Trapping Lemma.**
With the Phase 61 u_antisym having non-zero components at {4,5,10,11},
F_param at indices 4, 5, and 10 are all non-zero when σ ≠ 1/2.
Since a perimeter vector v = e_i ± e_j has ⟨e_k, v⟩ ≠ 0 only when k ∈ {i,j},
all three of {4,5,10} would need to be in the 2-element set {i,j} — impossible.
-/
theorem universal_trapping_lemma (σ : ℝ) (h_neq : σ ≠ 1/2) :
    ∀ t, F_param t σ ∉ Perimeter24 := by
  intro t ⟨i, j, hij, hcase⟩
  have hδ : σ - 1/2 ≠ 0 := sub_ne_zero.mpr h_neq
  have hrt2 : Real.sqrt 2 ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num)
  have hi4 := hi4_lemma t σ
  have hi5 := hi5_lemma t σ
  have hi10 := hi10_lemma t σ
  have h4_ne : @inner ℝ Sed _ (sedBasis 4) (F_param t σ) ≠ 0 := by
    rw [hi4]; exact div_ne_zero hδ hrt2
  have h5_ne : @inner ℝ Sed _ (sedBasis 5) (F_param t σ) ≠ 0 := by
    rw [hi5]; exact div_ne_zero (neg_ne_zero.mpr hδ) hrt2
  have h10_ne : @inner ℝ Sed _ (sedBasis 10) (F_param t σ) ≠ 0 := by
    rw [hi10]; exact div_ne_zero hδ hrt2
  have ij_inner : ∀ k m : Fin 16, @inner ℝ Sed _ (sedBasis k) (sedBasis m) =
      if k = m then (1 : ℝ) else 0 := fun k m => by
    simp only [sedBasis, EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]
    split_ifs <;> simp_all
  rcases hcase with heq | heq <;> {
    rw [heq] at h4_ne h5_ne h10_ne
    simp only [inner_add_right, inner_sub_right, ij_inner] at h4_ne h5_ne h10_ne
    have h4_in : (4 : Fin 16) = i ∨ (4 : Fin 16) = j := by
      by_contra hc; push_neg at hc
      exact h4_ne (by simp [if_neg hc.1, if_neg hc.2])
    have h5_in : (5 : Fin 16) = i ∨ (5 : Fin 16) = j := by
      by_contra hc; push_neg at hc
      exact h5_ne (by simp [if_neg hc.1, if_neg hc.2])
    have h10_in : (10 : Fin 16) = i ∨ (10 : Fin 16) = j := by
      by_contra hc; push_neg at hc
      exact h10_ne (by simp [if_neg hc.1, if_neg hc.2])
    -- {4,5,10} ⊆ {i,j} impossible since |{i,j}| = 2
    rcases h4_in with rfl | rfl <;> rcases h5_in with h5i | h5j <;>
      rcases h10_in with h10i | h10j <;> simp_all [Fin.ext_iff] <;> omega
  }

/--
The **core** perimeter: index families that avoid {4, 5, 10, 11}.
-/
theorem perimeter_orthogonal_balance (v : Sed) (hv : v ∈ Perimeter24)
    (h_no : ∀ i j : Fin 16, i ≠ j →
      (v = sedBasis i + sedBasis j ∨ v = sedBasis i - sedBasis j) →
      i.val ≠ 4 ∧ i.val ≠ 5 ∧ j.val ≠ 4 ∧ j.val ≠ 5 ∧
      i.val ≠ 10 ∧ i.val ≠ 11 ∧ j.val ≠ 10 ∧ j.val ≠ 11) :
  @inner ℝ Sed _ v u_antisym = 0 := by
  obtain ⟨i, j, hij, hcase⟩ := hv
  obtain ⟨hi4, hi5, hj4, hj5, hi10, hi11, hj10, hj11⟩ := h_no i j hij hcase
  have hbi : @inner ℝ Sed _ (sedBasis i) u_antisym = 0 := by
    simp only [sedBasis, u_antisym, inner_smul_right, inner_sub_right, inner_add_right,
               EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]
    have h1 : i ≠ (4 : Fin 16) := fun h => hi4 (congrArg Fin.val h)
    have h2 : i ≠ (5 : Fin 16) := fun h => hi5 (congrArg Fin.val h)
    have h3 : i ≠ (10 : Fin 16) := fun h => hi10 (congrArg Fin.val h)
    have h4 : i ≠ (11 : Fin 16) := fun h => hi11 (congrArg Fin.val h)
    simp [if_neg h1, if_neg h2, if_neg h3, if_neg h4]
  have hbj : @inner ℝ Sed _ (sedBasis j) u_antisym = 0 := by
    simp only [sedBasis, u_antisym, inner_smul_right, inner_sub_right, inner_add_right,
               EuclideanSpace.inner_single_left, EuclideanSpace.single_apply]
    have h1 : j ≠ (4 : Fin 16) := fun h => hj4 (congrArg Fin.val h)
    have h2 : j ≠ (5 : Fin 16) := fun h => hj5 (congrArg Fin.val h)
    have h3 : j ≠ (10 : Fin 16) := fun h => hj10 (congrArg Fin.val h)
    have h4 : j ≠ (11 : Fin 16) := fun h => hj11 (congrArg Fin.val h)
    simp [if_neg h1, if_neg h2, if_neg h3, if_neg h4]
  rcases hcase with rfl | rfl
  · simp [inner_add_left, hbi, hbj]
  · simp [inner_sub_left, hbi, hbj]

end
