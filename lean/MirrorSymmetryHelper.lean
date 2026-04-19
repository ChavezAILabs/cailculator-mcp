import RHForcingArgument

/-! Helper lemmas for MirrorSymmetry: coordinate computations of
    `sed_comm u_antisym (F_base t)` at index 0 (used in MirrorSymmetry.lean). -/

noncomputable section

set_option maxHeartbeats 800000 in
/-- The commutator `[u_antisym, F_base t]` has zero `e₀` component. -/
lemma sed_comm_u_F_base_coord0 (t : ℝ) :
    (sed_comm u_antisym (F_base t)) (0 : Fin 16) = 0 := by
      unfold sed_comm u_antisym F_base;
      -- By definition of multiplication in the sedenions, we can expand the product.
      have h_expand : ∀ (x y : Sed), (x * y) 0 = ∑ i : Fin 16, ∑ j : Fin 16, if sedMulTarget i j = 0 then sedMulSign i j * x i * y j else 0 := by
        exact?;
      simp +decide [ h_expand, Finset.sum_add_distrib, Finset.mul_sum _ _ _, Finset.sum_mul _ _ _, mul_assoc, mul_left_comm, mul_comm ];
      simp +decide [ Fin.sum_univ_succ, Fin.sum_univ_zero, sedBasis ]

end