/-
Lean version: leanprover/lean4:v4.24.0
Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

set_option linter.mathlibStandardSet false

open scoped BigOperators
open scoped Real
open scoped Nat
open scoped Classical
open scoped Pointwise

set_option maxHeartbeats 0
set_option maxRecDepth 4000
set_option synthInstance.maxHeartbeats 20000
set_option synthInstance.maxSize 128

set_option relaxedAutoImplicit false
set_option autoImplicit false

noncomputable section

def CD : Nat → Type
  | 0 => ℚ
  | n + 1 => CD n × CD n

instance instInhabitedCD (n : Nat) : Inhabited (CD n) :=
  match n with
  | 0 => inferInstanceAs (Inhabited ℚ)
  | n + 1 => @instInhabitedProd (CD n) (CD n) (instInhabitedCD n) (instInhabitedCD n)

instance instZeroCD (n : Nat) : Zero (CD n) :=
  match n with
  | 0 => inferInstanceAs (Zero ℚ)
  | n + 1 => @Prod.instZero (CD n) (CD n) (instZeroCD n) (instZeroCD n)

instance instOneCD (n : Nat) : One (CD n) :=
  match n with
  | 0 => inferInstanceAs (One ℚ)
  | n + 1 => @Prod.instOne (CD n) (CD n) (instOneCD n) (instOneCD n)

instance instAddCD (n : Nat) : Add (CD n) :=
  match n with
  | 0 => inferInstanceAs (Add ℚ)
  | n + 1 =>
    let _ : Add (CD n) := instAddCD n
    ⟨fun a b => (a.1 + b.1, a.2 + b.2)⟩

instance instNegCD (n : Nat) : Neg (CD n) :=
  match n with
  | 0 => inferInstanceAs (Neg ℚ)
  | n + 1 =>
    let _ : Neg (CD n) := instNegCD n
    ⟨fun a => (-a.1, -a.2)⟩

instance instSubCD (n : Nat) : Sub (CD n) :=
  match n with
  | 0 => inferInstanceAs (Sub ℚ)
  | n + 1 =>
    let _ : Sub (CD n) := instSubCD n
    ⟨fun a b => (a.1 - b.1, a.2 - b.2)⟩

instance instStarCD (n : Nat) : Star (CD n) :=
  match n with
  | 0 => inferInstanceAs (Star ℚ)
  | n + 1 =>
    let _ : Star (CD n) := instStarCD n
    let _ : Neg (CD n) := instNegCD n
    ⟨fun a => (star a.1, -a.2)⟩

instance instMulCD (n : Nat) : Mul (CD n) :=
  match n with
  | 0 => inferInstanceAs (Mul ℚ)
  | n + 1 =>
    let _ : Mul (CD n) := instMulCD n
    let _ : Add (CD n) := instAddCD n
    let _ : Sub (CD n) := instSubCD n
    let _ : Star (CD n) := instStarCD n
    ⟨fun a b => (a.1 * b.1 - star b.2 * a.2, b.2 * a.1 + a.2 * star b.1)⟩

def basis (n : Nat) (k : Nat) : CD n :=
  match n with
  | 0 => if k == 0 then 1 else 0
  | n + 1 =>
    if k < 2^n then
      (basis n k, 0)
    else
      (0, basis n (k - 2^n))

abbrev e (n : Nat) (k : Nat) : CD n := basis n k

def P1 (n : Nat) : CD n := e n 1 + e n 14
def Q1 (n : Nat) : CD n := e n 3 + e n 12

def IsBilateralZeroDivisor {α : Type} [Mul α] [Zero α] (a b : α) : Prop :=
  a * b = 0 ∧ b * a = 0

end -- close noncomputable section

def scalar (n : Nat) (q : ℚ) : CD n :=
  match n with
  | 0 => q
  | n + 1 => (scalar n q, 0)

instance (n : Nat) : Coe ℚ (CD n) := ⟨scalar n⟩

/-
PROVIDED SOLUTION
Unfold IsBilateralZeroDivisor, P1, Q1, e into basis definitions and then compute. The key challenge: decide/native_decide don't work under Classical. Instead, use `simp only [IsBilateralZeroDivisor]; constructor` to split, then unfold P1, Q1, e, and reduce each side. Try using `norm_num [P1, Q1, e, basis]` or `simp [P1, Q1, e, basis]; ring` or just `norm_num` on each goal. Another approach: `refine ⟨?_, ?_⟩` then on each goal `show ... = ...` and use `norm_num`. The type CD 4 = CD 3 × CD 3 = ... eventually becomes nested pairs of ℚ. You may need to unfold the multiplication definition deeply. Try `simp only [P1, Q1, e, basis]; norm_num` or just `norm_num` after constructor.

This is IsBilateralZeroDivisor (P1 4) (Q1 4), meaning P1 4 * Q1 4 = 0 ∧ Q1 4 * P1 4 = 0. P1 4 and Q1 4 are concrete elements of CD 4 (nested tuples of rationals). Unfold IsBilateralZeroDivisor and use constructor to split. Each goal is a concrete equality of CD 4 elements. Use unfold P1 Q1 e then norm_cast or norm_num. Do NOT use decide or native_decide.

This is a concrete computation showing P1 4 * Q1 4 = 0 and Q1 4 * P1 4 = 0. Unfold IsBilateralZeroDivisor, P1, Q1, e (= basis), then use norm_num or norm_cast. Do NOT use decide or native_decide. Try: refine ⟨?_, ?_⟩ then on each goal unfold P1 Q1 e and norm_num or norm_cast. Or: constructor; all_goals (unfold P1 Q1 e; norm_num). Since the elements are specific nested tuples of ℚ, after unfolding the computation should reduce to ℚ arithmetic.

Unfold IsBilateralZeroDivisor, then split with constructor. Each goal is P1 4 * Q1 4 = 0 or Q1 4 * P1 4 = 0. Since these are concrete elements, unfold P1, Q1, e, then use norm_num or norm_cast to close. Do NOT use decide or native_decide. Try: constructor <;> (simp only [P1, Q1, e, basis]; norm_num). Or: refine ⟨?_, ?_⟩ <;> simp [P1, Q1, e, basis, scalar].
-/
-- Simp lemmas for reducing CD operations to component-wise ℚ arithmetic
private lemma mul_cd (n : Nat) (a b : CD (n+1)) : a * b = (a.1 * b.1 - star b.2 * a.2, b.2 * a.1 + a.2 * star b.1) := rfl
private lemma add_cd (n : Nat) (a b : CD (n+1)) : a + b = (a.1 + b.1, a.2 + b.2) := rfl
private lemma sub_cd (n : Nat) (a b : CD (n+1)) : a - b = (a.1 - b.1, a.2 - b.2) := rfl
private lemma neg_cd (n : Nat) (a : CD (n+1)) : -a = (-a.1, -a.2) := rfl
private lemma star_cd (n : Nat) (a : CD (n+1)) : star a = (star a.1, -a.2) := rfl
private lemma zero_cd (n : Nat) : (0 : CD (n+1)) = (0, 0) := rfl
private lemma star_base (x : ℚ) : @Star.star (CD 0) (instStarCD 0) x = x := rfl

-- CD 0 is ℚ, so it has CommRing
private instance : CommRing (CD 0) := inferInstanceAs (CommRing ℚ)

/-
PROVIDED SOLUTION
IsBilateralZeroDivisor (P1 4) (Q1 4) means P1 4 * Q1 4 = 0 ∧ Q1 4 * P1 4 = 0. Use constructor to split. Each goal is a concrete CD 4 equality. Use the same approach as p1_sq and q1_sq: unfold P1 Q1 e basis then norm_cast. Or try: unfold IsBilateralZeroDivisor P1 Q1 e basis; norm_cast. Or constructor then on each goal: unfold P1 Q1 e basis; norm_cast. Do NOT use decide or native_decide.

IMPORTANT: Previous proofs using `norm_cast` after unfolding have failed in the full build even though they pass isolated verification. The issue is that `norm_cast` doesn't fully reduce the custom CD multiplication in the full build context.

Instead, use the simp lemmas mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base which are already defined in the file (just above this theorem). These explicitly reduce CD operations to component-wise operations.

The proof approach:
1. constructor to split into two goals
2. For each goal: simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base] to reduce to ℚ arithmetic in nested Prod
3. Then decompose with nested Prod.ext and close each ℚ goal with ring

Specifically try:
  constructor
  · simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base]
    refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)))
    all_goals ring
  · simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base]
    refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)))
    all_goals ring

DO NOT use norm_cast or decide or native_decide.

CRITICAL: Do NOT use norm_cast, decide, or native_decide. These tactics fail in the full build context even if they seem to work in isolation.

Approach: unfold IsBilateralZeroDivisor, then refine ⟨?_, ?_⟩. For each goal (P1 4 * Q1 4 = 0 and Q1 4 * P1 4 = 0):
1. simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base]
2. refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)))
3. all_goals ring

The simp lemmas mul_cd, add_cd, etc. are defined in the file above this theorem. They reduce CD operations to component-wise ℚ arithmetic. After Prod.ext, each goal is ℚ arithmetic that ring can close.

CRITICAL CONSTRAINTS:
- Do NOT use norm_cast, decide, or native_decide
- Do NOT use ring (too slow, times out the build)

The proof requires computing Cayley-Dickson products at level 4. Here's the fastest approach:

1. unfold IsBilateralZeroDivisor
2. refine ⟨?_, ?_⟩
3. For each goal, use: simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base]
4. Then decompose with Prod.ext 4 levels deep to get 16 CD 0 = ℚ goals
5. Close each with: show (_ : ℚ) = _; norm_num

The simp lemmas mul_cd, add_cd, etc. expand the CD operations. After Prod.ext, each goal is ℚ arithmetic with 0s and 1s. The `show (_ : ℚ) = _` converts from CD 0 to ℚ (they're definitionally equal), then `norm_num` closes.

The CommRing (CD 0) instance is also available: `private instance : CommRing (CD 0) := inferInstanceAs (CommRing ℚ)`

Unfold IsBilateralZeroDivisor and use And.intro. For each goal, use simp only with mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base (already defined in the file) to fully expand. Then use Prod.ext 4 levels deep to decompose into 16 CD 0 = ℚ goals. Then close each goal with: show (_ : ℚ) = _; norm_num. CRITICAL: Do NOT use norm_cast, decide, native_decide. The CD 0 = ℚ but ring/norm_num don't find CommRing (CD 0), so you MUST use `show (_ : ℚ) = _` to convert the type first.
-/
theorem Pattern1_CD4 : IsBilateralZeroDivisor (P1 4) (Q1 4) := by
  unfold IsBilateralZeroDivisor; constructor <;> (simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base]; refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))); all_goals (show (_ : ℚ) = _; norm_num))

/-
PROVIDED SOLUTION
P1 4 * P1 4 = (-2 : ℚ) where the RHS coerces to scalar 4 (-2). Unfold P1, e, basis and the multiplication. Try: `change P1 4 * P1 4 = scalar 4 (-2)` then unfold everything and use norm_num. Or just try `norm_num [P1, e, basis, scalar]`. Or use `simp only [P1, e, basis]` then `norm_num`.

P1 4 * P1 4 = (-2 : ℚ). The RHS coerces via the Coe instance to scalar 4 (-2). This is a concrete computation. Try: change P1 4 * P1 4 = scalar 4 (-2); unfold P1 e; simp only [basis]; norm_num [scalar]. Or use norm_cast. Do NOT use decide or native_decide.

P1 4 * P1 4 = (-2 : ℚ). Change to: P1 4 * P1 4 = scalar 4 (-2). Then use the simp lemmas mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar to reduce to ℚ component equalities. Decompose with Prod.ext and close with ring or norm_num. Do NOT use decide or native_decide.

Specifically:
  change P1 4 * P1 4 = scalar 4 (-2)
  simp only [P1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar]
  refine Prod.ext ... (16 components)
  all_goals ring

IMPORTANT: Previous proofs using `norm_cast` have failed in the full build. Use simp lemmas mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base instead.

  change P1 4 * P1 4 = scalar 4 (-2)
  simp only [P1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar]
  refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)))
  all_goals ring

DO NOT use norm_cast.

CRITICAL: Do NOT use norm_cast. It fails in the full build.

Approach:
1. change P1 4 * P1 4 = scalar 4 (-2)
2. simp only [P1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar]
3. refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) ...) (...)
4. all_goals ring

change to scalar 4 (-2). Then simp with mul_cd etc. and scalar. Then Prod.ext 4 levels. Then show (_ : ℚ) = _; norm_num on each goal. CRITICAL: Do NOT use norm_cast or ring.
-/
lemma p1_sq : P1 4 * P1 4 = (-2 : ℚ) := by
  change P1 4 * P1 4 = scalar 4 (-2); simp only [P1, Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar]; refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))); all_goals (show (_ : ℚ) = _; norm_num)

/-
PROVIDED SOLUTION
Same approach as p1_sq. Try norm_num [Q1, e, basis, scalar].

Same as p1_sq but for Q1. Try norm_cast or unfold Q1 e and norm_num. Do NOT use decide or native_decide.

Same as p1_sq but for Q1. Try: change Q1 4 * Q1 4 = scalar 4 (-2); simp only [Q1, e, basis, scalar]; norm_num. Or: unfold Q1 e; simp only [basis]; norm_num [scalar]. Do NOT use decide or native_decide.

Same as p1_sq. Change Q1 4 * Q1 4 to scalar 4 (-2), then simp with mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar. Then Prod.ext and ring. Do NOT use decide or native_decide.

Same approach as p1_sq. change to scalar 4 (-2), then simp with mul_cd etc., then Prod.ext decompose, then ring on each ℚ component. DO NOT use norm_cast.

CRITICAL: Do NOT use norm_cast. It fails in the full build.

Same approach as p1_sq but for Q1. change to scalar 4 (-2), simp, Prod.ext, ring.

Same as Pattern1_CD4 but for P1 4 * P1 4 = (-2 : ℚ). Use change to scalar 4 (-2), simp with mul_cd etc. and scalar, Prod.ext, show (_ : ℚ) = _, norm_num. Do NOT use norm_cast, decide, native_decide, or ring (ring times out).

Same as p1_sq. CRITICAL: Do NOT use norm_cast or ring.
-/
lemma q1_sq : Q1 4 * Q1 4 = (-2 : ℚ) := by
  change Q1 4 * Q1 4 = scalar 4 (-2); simp only [Q1, e, basis, mul_cd, add_cd, sub_cd, neg_cd, star_cd, zero_cd, star_base, scalar]; refine Prod.ext (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))) (Prod.ext (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_)) (Prod.ext (Prod.ext ?_ ?_) (Prod.ext ?_ ?_))); all_goals (show (_ : ℚ) = _; norm_num)

instance instAddCommGroupCD (n : Nat) : AddCommGroup (CD n) :=
  match n with
  | 0 => inferInstanceAs (AddCommGroup ℚ)
  | n + 1 =>
    let _ : AddCommGroup (CD n) := instAddCommGroupCD n
    @Prod.instAddCommGroup (CD n) (CD n) (instAddCommGroupCD n) (instAddCommGroupCD n)


noncomputable section

lemma neg_zero_CD (n : Nat) : -(0 : CD n) = 0 := by
  induction' n with n ih
  · norm_num
  · exact Prod.ext ih ih

lemma star_zero_CD (n : Nat) : star (0 : CD n) = 0 := by
  induction' n with n ih
  · simp [star, Star.star]
  · show (star (0 : CD n), -(0 : CD n)) = (0, 0)
    rw [ih, neg_zero_CD]

lemma add_zero_CD (n : Nat) (x : CD n) : x + 0 = x := by
  induction' n with n ih
  · exact add_zero x
  · exact Prod.ext (ih x.1) (ih x.2)

lemma zero_add_CD (n : Nat) (x : CD n) : 0 + x = x := by
  induction' n with n ih
  · exact zero_add x
  · exact Prod.ext (ih x.1) (ih x.2)

lemma sub_zero_CD (n : Nat) (x : CD n) : x - 0 = x := by
  induction' n with n ih
  · exact sub_zero x
  · exact Prod.ext (ih x.1) (ih x.2)

lemma zero_sub_CD (n : Nat) (x : CD n) : 0 - x = -x := by
  induction' n with n ih
  · exact zero_sub x
  · exact Prod.ext (ih x.1) (ih x.2)

lemma neg_add_CD (n : Nat) (x y : CD n) : -(x + y) = -x + -y := by
  induction' n with n ih
  · exact neg_add x y
  · exact Prod.ext (ih x.1 y.1) (ih x.2 y.2)

lemma add_comm_CD (n : Nat) (x y : CD n) : x + y = y + x := by
  induction' n with n ih
  · exact add_comm x y
  · exact Prod.ext (ih x.1 y.1) (ih x.2 y.2)

lemma add_assoc_CD (n : Nat) (x y z : CD n) : x + y + z = x + (y + z) := by
  induction' n with n ih
  · exact add_assoc x y z
  · exact Prod.ext (ih x.1 y.1 z.1) (ih x.2 y.2 z.2)

lemma sub_eq_add_neg_CD (n : Nat) (x y : CD n) : x - y = x + -y := by
  induction' n with n ih
  · exact sub_eq_add_neg x y
  · exact Prod.ext (ih x.1 y.1) (ih x.2 y.2)

/-
PROVIDED SOLUTION
Induction on n. Base case: ⟨zero_mul, mul_zero⟩ on ℚ. Inductive step: assume ih : (∀ x, 0*x=0) ∧ (∀ x, x*0=0) at level n. For zero_mul at n+1: (0,0)*(x1,x2) = (0*x1 - star x2 * 0, x2*0 + 0*star x1). Use ih.1, ih.2, star_zero_CD, sub_zero_CD, zero_add_CD to get (0,0). For mul_zero: (x1,x2)*(0,0) = (x1*0 - star 0 * x2, 0*x1 + x2*star 0). Use ih.2, ih.1, star_zero_CD, zero_sub_CD, neg_zero_CD, zero_add_CD to get (0,0). Show each with Prod.ext.
-/
lemma zero_mul_and_mul_zero_CD (n : Nat) :
    (∀ x : CD n, 0 * x = 0) ∧ (∀ x : CD n, x * 0 = 0) := by
  -- We proceed by induction on $n$.
  induction' n with n ih;
  · aesop;
  · -- We simplify the goal using the fact that multiplication in CD n+1 is defined as the product of the components.
    have h_mul : (0 : CD (n + 1)) = (0, 0) := by
      rfl;
    -- By definition of multiplication in CD (n + 1), we have:
    have h_mul_def : ∀ (a b : CD (n + 1)), a * b = (a.1 * b.1 - star b.2 * a.2, b.2 * a.1 + a.2 * star b.1) := by
      exact?
    generalize_proofs at *; (
    have h_star_zero : star (0 : CD n) = 0 := by
      exact?
    generalize_proofs at *; (
    simp_all +decide [ Prod.ext_iff ];
    -- By definition of subtraction and addition in the product type, we have:
    have h_sub_add : (0 : CD n) - (0 : CD n) = 0 ∧ (0 : CD n) + (0 : CD n) = 0 := by
      exact ⟨ sub_zero_CD n 0, add_zero_CD n 0 ⟩
    generalize_proofs at *; (
    rw [ h_sub_add.1, h_sub_add.2 ])))

lemma zero_mul_CD (n : Nat) (x : CD n) : 0 * x = 0 :=
  (zero_mul_and_mul_zero_CD n).1 x

lemma mul_zero_CD (n : Nat) (x : CD n) : x * 0 = 0 :=
  (zero_mul_and_mul_zero_CD n).2 x

lemma scalar_star (n : Nat) (q : ℚ) : star (scalar n q) = scalar n q := by
  induction' n with n ih
  · simp [scalar, star, Star.star]
  · show (star (scalar n q), -(0 : CD n)) = (scalar n q, 0)
    rw [ih, neg_zero_CD]

lemma scalar_add (n : Nat) (a b : ℚ) : scalar n (a + b) = scalar n a + scalar n b := by
  induction' n with n ih
  · rfl
  · show (scalar n (a + b), (0 : CD n)) = (scalar n a + scalar n b, 0 + 0)
    rw [ih]
    congr 1
    exact (add_zero_CD n 0).symm

lemma scalar_neg (n : Nat) (a : ℚ) : scalar n (-a) = -scalar n a := by
  induction' n with n ih
  · rfl
  · show (scalar n (-a), (0 : CD n)) = (-scalar n a, -(0 : CD n))
    rw [ih, neg_zero_CD]

lemma scalar_sub (n : Nat) (a b : ℚ) : scalar n (a - b) = scalar n a - scalar n b := by
  induction' n with n ih
  · rfl
  · show (scalar n (a - b), (0 : CD n)) = (scalar n a - scalar n b, 0 - 0)
    rw [ih]
    congr 1
    exact (sub_zero_CD n 0).symm

/-
PROVIDED SOLUTION
Induction on n. Base case: rfl (ℚ multiplication). Inductive step: scalar (n+1) a * scalar (n+1) b = (scalar n a, 0) * (scalar n b, 0) = (scalar n a * scalar n b - star 0 * 0, 0 * scalar n a + 0 * star (scalar n b)). Use star_zero_CD, zero_mul_CD, mul_zero_CD, sub_zero_CD, zero_add_CD, and IH to get (scalar n (a*b), 0) = scalar (n+1) (a*b).
-/
lemma scalar_mul_scalar (n : Nat) (a b : ℚ) : scalar n a * scalar n b = scalar n (a * b) := by
  induction' n with n ih generalizing a b;
  · rfl;
  · -- By definition of scalar, we have scalar (n+1) a = (scalar n a, 0) and scalar (n+1) b = (scalar n b, 0).
    have h_scalar_succ : ∀ a : ℚ, scalar (n + 1) a = (scalar n a, 0) := by
      exact?;
    simp +decide [ h_scalar_succ, ih ];
    rw [ ← ih ];
    erw [ Prod.mk_inj ] ; norm_num;
    erw [ zero_mul_CD, mul_zero_CD ];
    erw [ sub_zero_CD, zero_mul_CD, zero_add_CD ] ; norm_num

lemma scalar_zero (n : Nat) : scalar n 0 = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [scalar, ih]; rfl

instance instSMulCD (n : Nat) : SMul ℚ (CD n) :=
  ⟨fun q x => scalar n q * x⟩

lemma star_add_CD (n : Nat) (x y : CD n) : star (x + y) = star x + star y := by
  induction' n with n ih
  · simp [star, Star.star]
  · show (star (x.1 + y.1), -(x.2 + y.2)) = (star x.1 + star y.1, -x.2 + -y.2)
    rw [ih, neg_add_CD]

/-
PROVIDED SOLUTION
Induction on n. Base: exact fun x => mul_comm q x. Inductive step with x = (x1, x2):
scalar (n+1) q * (x1,x2) = (scalar n q, 0) * (x1, x2) = (scalar n q * x1 - star x2 * 0, x2 * scalar n q + 0 * star x1).
By mul_zero_CD: star x2 * 0 = 0. By zero_mul_CD: 0 * star x1 = 0. By sub_zero_CD and add_zero_CD: = (scalar n q * x1, x2 * scalar n q).

(x1, x2) * (scalar n q, 0) = (x1 * scalar n q - star 0 * x2, 0 * x1 + x2 * star (scalar n q)).
By star_zero_CD: star 0 = 0. By zero_mul_CD: 0 * x2 = 0 and 0 * x1 = 0. By sub_zero_CD and zero_add_CD: = (x1 * scalar n q, x2 * scalar_star).
By scalar_star: star (scalar n q) = scalar n q. So = (x1 * scalar n q, x2 * scalar n q).

By IH (ih q x1): scalar n q * x1 = x1 * scalar n q. So both sides are equal.
Use Prod.ext with ih applied to each component.
-/
lemma scalar_comm (n : Nat) (q : ℚ) (x : CD n) : scalar n q * x = x * scalar n q := by
  -- By definition of multiplication in CD n, we can expand both sides.
  have h_expand : ∀ (n : ℕ) (q : ℚ) (x : CD n), scalar n q * x = x * scalar n q := by
    intro n;
    induction' n with n ih;
    · exact fun q x => mul_comm q x;
    · intro q x; rcases x with ⟨ x₁, x₂ ⟩ ; simp +decide [ *, scalar ] ;
      erw [ Prod.mk_inj ] ; simp +decide [ ih ] ;
      constructor <;> simp +decide [ *, zero_mul_CD, mul_zero_CD, star_zero_CD ];
      rw [ zero_add_CD, add_zero_CD, scalar_star ];
  exact h_expand n q x

/-
PROBLEM
Helper lemmas for distributivity

PROVIDED SOLUTION
Induction on n. Base case: sub_add_eq_sub_sub on ℚ (or use ring). Inductive step: component-wise using ih, i.e., Prod.ext (ih a.1 b.1 c.1) (ih a.2 b.2 c.2).
-/
lemma sub_add_eq_sub_sub_CD (n : Nat) (a b c : CD n) : a - (b + c) = a - b - c := by
  -- By definition of subtraction in CD n, we can write a - (b + c) as a + (- (b + c)).
  have h_def : a - (b + c) = a + (- (b + c)) := by
    exact?;
  -- By definition of negation in CD n, we can write -(b + c) as -b + -c.
  have h_neg_def : -(b + c) = -b + -c := by
    exact?
  rw [h_def, h_neg_def];
  -- By definition of subtraction in CD n, we can write a - b as a + (-b).
  have h_sub_def : ∀ a b : CD n, a - b = a + (-b) := by
    exact?
  rw [h_sub_def, h_sub_def];
  exact?

/-
PROVIDED SOLUTION
Induction on n. Base case: ring on ℚ. Inductive step: component-wise, Prod.ext (ih a.1 b.1 c.1 d.1) (ih a.2 b.2 c.2 d.2).
-/
lemma sub_add_sub_CD (n : Nat) (a b c d : CD n) : (a - b) + (c - d) = (a + c) - (b + d) := by
  -- By the properties of the eightfold way, we can simplify the expression component-wise for each dimension.
  have h_ind : ∀ (n : ℕ) (a b c d : CD n), a - b + (c - d) = a + c - (b + d) := by
    intro n
    induction' n with n ih;
    · grind;
    · intros a b c d
      have h_comp : ∀ (x y : CD n), x - y + (x - y) = x + x - (y + y) := by
        exact fun x y => ih x y x y;
      exact Prod.ext ( ih _ _ _ _ ) ( ih _ _ _ _ );
  exact h_ind n a b c d

/-
PROVIDED SOLUTION
Induction on n. Base case: ring on ℚ. Inductive step: component-wise, Prod.ext (ih a.1 b.1 c.1 d.1) (ih a.2 b.2 c.2 d.2).
-/
lemma add_add_add_comm_CD (n : Nat) (a b c d : CD n) : (a + b) + (c + d) = (a + c) + (b + d) := by
  -- By the associativity and commutativity of addition in CD n, we can rearrange the terms.
  have h_assoc_comm : ∀ (a b c d : CD n), (a + b) + (c + d) = (a + c) + (b + d) := by
    induction' n with n ih;
    · grind;
    · simp +zetaDelta at *;
      exact fun a b c d => by exact Prod.ext ( ih _ _ _ _ ) ( ih _ _ _ _ ) ;
  exact h_assoc_comm a b c d

/-
PROVIDED SOLUTION
Joint induction on n. Base case: ⟨mul_add, add_mul⟩ on ℚ. Inductive step: assume ih gives both left_distrib and right_distrib at level n. Denote ih.1 = left_distrib_n, ih.2 = right_distrib_n.

For left_distrib at n+1: Let x=(x1,x2), y=(y1,y2), z=(z1,z2).
x*(y+z) = (x1*(y1+z1) - star(y2+z2)*x2, (y2+z2)*x1 + x2*star(y1+z1))
x*y + x*z = (x1*y1 - star(y2)*x2 + (x1*z1 - star(z2)*x2), y2*x1 + x2*star(y1) + (z2*x1 + x2*star(z1)))

First component: x1*(y1+z1) = x1*y1 + x1*z1 by ih.1. star(y2+z2) = star(y2) + star(z2) by star_add_CD. (star(y2)+star(z2))*x2 = star(y2)*x2 + star(z2)*x2 by ih.2. So first comp = x1*y1 + x1*z1 - (star(y2)*x2 + star(z2)*x2) = (x1*y1 - star(y2)*x2) + (x1*z1 - star(z2)*x2) by sub_add_sub_CD.

Second component: (y2+z2)*x1 = y2*x1 + z2*x1 by ih.2. star(y1+z1) = star(y1) + star(z1) by star_add_CD. x2*(star(y1)+star(z1)) = x2*star(y1) + x2*star(z1) by ih.1. So second comp = y2*x1 + z2*x1 + x2*star(y1) + x2*star(z1) = (y2*x1 + x2*star(y1)) + (z2*x1 + x2*star(z1)) by add_add_add_comm_CD.

For right_distrib at n+1: (x+y)*z = ((x1+y1)*z1 - star(z2)*(x2+y2), z2*(x1+y1) + (x2+y2)*star(z1))
x*z + y*z = (x1*z1 - star(z2)*x2 + (y1*z1 - star(z2)*y2), z2*x1 + x2*star(z1) + (z2*y1 + y2*star(z1)))

First component: (x1+y1)*z1 = x1*z1 + y1*z1 by ih.2. star(z2)*(x2+y2) = star(z2)*x2 + star(z2)*y2 by ih.1. So (x1*z1+y1*z1) - (star(z2)*x2+star(z2)*y2) = (x1*z1-star(z2)*x2) + (y1*z1-star(z2)*y2) by sub_add_sub_CD.

Second component: z2*(x1+y1) = z2*x1+z2*y1 by ih.1. (x2+y2)*star(z1) = x2*star(z1)+y2*star(z1) by ih.2. So (z2*x1+z2*y1)+(x2*star(z1)+y2*star(z1)) = (z2*x1+x2*star(z1))+(z2*y1+y2*star(z1)) by add_add_add_comm_CD.

Use Prod.ext for each direction. Use star_add_CD, sub_add_sub_CD, add_add_add_comm_CD as key helpers.
-/
lemma distrib_CD (n : Nat) :
    (∀ x y z : CD n, x * (y + z) = x * y + x * z) ∧
    (∀ x y z : CD n, (x + y) * z = x * z + y * z) := by
  induction' n with n ih;
  · exact ⟨ fun x y z => by exact Rat.mul_add _ _ _, fun x y z => by exact Rat.add_mul _ _ _ ⟩;
  · constructor;
    · intro x y z;
      -- Expand both sides using the definition of multiplication in CD (n + 1).
      have h_expand : x * (y + z) = (x.1 * (y.1 + z.1) - star (y.2 + z.2) * x.2, (y.2 + z.2) * x.1 + x.2 * star (y.1 + z.1)) ∧ x * y + x * z = (x.1 * y.1 - star y.2 * x.2 + (x.1 * z.1 - star z.2 * x.2), y.2 * x.1 + x.2 * star y.1 + (z.2 * x.1 + x.2 * star z.1)) := by
        exact ⟨ rfl, rfl ⟩;
      rw [ h_expand.1, h_expand.2 ];
      simp +decide only [ih.1, star_add_CD, ih.2, sub_add_sub_CD, add_add_add_comm_CD];
    · -- Let's unfold the definition of multiplication for CD (n + 1).
      intro x y z
      simp [CD] at *;
      -- By definition of multiplication in CD (n + 1), we can expand both sides.
      have h_expand : (x + y) * z = ((x.1 + y.1) * z.1 - star z.2 * (x.2 + y.2), z.2 * (x.1 + y.1) + (x.2 + y.2) * star z.1) ∧ x * z + y * z = ((x.1 * z.1 - star z.2 * x.2) + (y.1 * z.1 - star z.2 * y.2), z.2 * x.1 + x.2 * star z.1 + (z.2 * y.1 + y.2 * star z.1)) := by
        exact ⟨ rfl, rfl ⟩;
      have h_sub : star z.2 * (x.2 + y.2) = star z.2 * x.2 + star z.2 * y.2 := by
        exact ih.1 _ _ _
      have h_add : (x.2 + y.2) * star z.1 = x.2 * star z.1 + y.2 * star z.1 := by
        exact ih.2 _ _ _
      simp_all +decide [ sub_add_sub_CD, add_add_add_comm_CD ]

lemma left_distrib_CD (n : Nat) (x y z : CD n) : x * (y + z) = x * y + x * z :=
  (distrib_CD n).1 x y z

lemma right_distrib_CD (n : Nat) (x y z : CD n) : (x + y) * z = x * z + y * z :=
  (distrib_CD n).2 x y z

/-
PROBLEM
Helper: scalar distributes over negation

PROVIDED SOLUTION
Induction on n. Base case: use mul_neg on ℚ. Inductive step: scalar (n+1) q * (-(x1,x2)) = (scalar n q, 0) * (-x1, -x2) = (scalar n q * (-x1) - star(-x2) * 0, (-x2) * scalar n q + 0 * star(-x1)). By mul_zero_CD, zero_mul_CD, sub_zero_CD, add_zero_CD: = (scalar n q * (-x1), (-x2) * scalar n q). By IH: scalar n q * (-x1) = -(scalar n q * x1). By scalar_comm: (-x2) * scalar n q = scalar n q * (-x2) = -(scalar n q * x2) [by IH]. And -(scalar n q * (x1, x2)) = -(scalar n q * x1, x2 * scalar n q) using the computation of scalar * pair above. Actually, -(scalar n q * x1, scalar n q * x2) = (-(scalar n q * x1), -(scalar n q * x2)) by definition of negation. Wait, the scalar multiplication gives (scalar n q * x1, x2 * scalar n q). Hmm, let me be more careful. Just use induction on n, base case mul_neg, inductive step decompose and use IH componentwise.
-/
lemma scalar_mul_neg_CD (n : Nat) (q : ℚ) (x : CD n) : scalar n q * (-x) = -(scalar n q * x) := by
  induction' n with n ih;
  · exact mul_neg q x;
  · -- By definition of scalar multiplication in CD (n+1), we have:
    have h_scalar_mul : ∀ (x : CD (n + 1)), scalar (n + 1) q * x = (scalar n q * x.1, scalar n q * x.2) := by
      -- By definition of scalar multiplication in CD (n+1), we have scalar (n+1) q = (scalar n q, 0).
      have h_scalar_def : scalar (n + 1) q = (scalar n q, 0) := by
        exact?;
      -- By definition of multiplication in CD (n+1), we have:
      have h_mul_def : ∀ (a b : CD (n + 1)), a * b = (a.1 * b.1 - star b.2 * a.2, b.2 * a.1 + a.2 * star b.1) := by
        aesop;
      have h_star_zero : star (0 : CD n) = 0 := by
        exact?;
      have h_zero_mul : ∀ (x : CD n), 0 * x = 0 := by
        exact?
      have h_mul_zero : ∀ (x : CD n), x * 0 = 0 := by
        exact fun x => by simpa [ h_star_zero ] using zero_mul_and_mul_zero_CD n |>.2 x;
      simp [h_scalar_def, h_mul_def, h_star_zero, h_zero_mul, h_mul_zero];
      -- By definition of multiplication in CD n, we have x.2 * scalar n q = scalar n q * x.2.
      have h_comm : ∀ (x : CD n), x * scalar n q = scalar n q * x := by
        exact?;
      simp [h_comm];
      -- By definition of subtraction and addition in CD n, we have:
      have h_sub_add : ∀ (x : CD n), x - 0 = x ∧ x + 0 = x := by
        exact fun x => ⟨ sub_zero_CD n x, add_zero_CD n x ⟩;
      exact fun x => Prod.ext ( h_sub_add _ |>.1 ) ( h_sub_add _ |>.2 );
    -- By definition of scalar multiplication in CD (n+1), we have that scalar (n+1) q * -x = (scalar n q * (-x.1), scalar n q * (-x.2)).
    have h_neg : scalar (n + 1) q * -x = (scalar n q * (-x.1), scalar n q * (-x.2)) := by
      exact h_scalar_mul _;
    aesop

/-
PROBLEM
Helper: scalar distributes over subtraction

PROVIDED SOLUTION
Use scalar_mul_neg_CD: scalar n q * (x - y) = scalar n q * (x + (-y)) [by sub_eq_add_neg_CD] = scalar n q * x + scalar n q * (-y) [by left_distrib_CD] = scalar n q * x + (-(scalar n q * y)) [by scalar_mul_neg_CD] = scalar n q * x - scalar n q * y [by sub_eq_add_neg_CD backwards].
-/
lemma scalar_mul_sub_CD (n : Nat) (q : ℚ) (x y : CD n) :
    scalar n q * (x - y) = scalar n q * x - scalar n q * y := by
  -- Substitute the equalities `h_sub` and `h_neg` back into the goal.
  rw [sub_eq_add_neg_CD, left_distrib_CD, scalar_mul_neg_CD];
  exact?

/-
PROBLEM
Helper: star commutes with scalar multiplication

PROVIDED SOLUTION
Induction on n. Base case: star on ℚ is the identity (trivial involution), so star (q * x) = q * x = q * star x. Inductive step: scalar (n+1) q * (x1, x2) = (scalar n q * x1, x2 * scalar n q) [computed via mul_zero_CD, zero_mul_CD, sub_zero_CD, add_zero_CD]. star of this = (star(scalar n q * x1), -(x2 * scalar n q)). And scalar (n+1) q * star (x1, x2) = (scalar n q, 0) * (star x1, -x2) = (scalar n q * star x1, (-x2) * scalar n q). By IH: star(scalar n q * x1) = scalar n q * star x1. For the second component: -(x2 * scalar n q). By scalar_comm: x2 * scalar n q = scalar n q * x2. So -(scalar n q * x2). And (-x2) * scalar n q = scalar n q * (-x2) [by scalar_comm] = -(scalar n q * x2) [by scalar_mul_neg_CD]. So both components match.
-/
lemma star_scalar_mul_CD (n : Nat) (q : ℚ) (x : CD n) :
    star (scalar n q * x) = scalar n q * star x := by
  revert x;
  induction' n with n ih;
  · bound;
  · -- By definition of scalar multiplication, we have:
    have h_scalar_mul : ∀ q : ℚ, ∀ x : CD (n + 1), scalar (n + 1) q * x = (scalar n q * x.1, x.2 * scalar n q) := by
      intros q x
      rw [scalar];
      -- By definition of multiplication in CD (n + 1), we have:
      have h_mul_def : ∀ (a b : CD (n + 1)), a * b = (a.1 * b.1 - star b.2 * a.2, b.2 * a.1 + a.2 * star b.1) := by
        bound;
      simp [h_mul_def];
      congr <;> simp +decide [ zero_mul_CD, mul_zero_CD ];
      · exact sub_zero_CD _ _;
      · exact add_zero_CD _ _;
    -- By definition of star, we have:
    have h_star : ∀ x : CD (n + 1), star x = (star x.1, -x.2) := by
      aesop;
    simp +decide [ h_scalar_mul, h_star, ih ];
    -- By definition of multiplication, we have:
    have h_mul : ∀ x : CD n, x * scalar n q = scalar n q * x := by
      exact?;
    simp +decide [ h_mul ];
    exact fun x => by rw [ ← scalar_mul_neg_CD ] ;

/-
PROBLEM
Helper: computing scalar times a pair explicitly

PROVIDED SOLUTION
Unfold the definitions. scalar (n+1) q = (scalar n q, 0). The multiplication (scalar n q, 0) * (x1, x2) by instMulCD gives (scalar n q * x1 - star x2 * 0, x2 * scalar n q + 0 * star x1). Use mul_zero_CD for star x2 * 0 = 0 and 0 * star x1 = 0. Use sub_zero_CD and add_zero_CD. Then x2 * scalar n q = scalar n q * x2 by scalar_comm. Result: (scalar n q * x1, scalar n q * x2).
-/
lemma scalar_mul_pair (n : Nat) (q : ℚ) (x1 x2 : CD n) :
    @HMul.hMul (CD (n+1)) (CD (n+1)) (CD (n+1)) instHMul
      (scalar (n+1) q) (x1, x2) = (scalar n q * x1, scalar n q * x2) := by
  -- By definition of scalar multiplication, we have:
  have h_scalar : scalar (n + 1) q = (scalar n q, 0) := by
    rfl;
  rw [ h_scalar ];
  -- By definition of multiplication in $CD (n + 1)$, we have:
  have h_mul : ∀ (a b : CD (n + 1)), a * b = (a.1 * b.1 - star b.2 * a.2, b.2 * a.1 + a.2 * star b.1) := by
    exact?;
  simp +decide [ h_mul, mul_comm ];
  -- Since $0 * star x1 = 0$ and $x2 * scalar n q = scalar n q * x2$, we can simplify the expression.
  have h_simp : star x2 * 0 = 0 ∧ x2 * scalar n q = scalar n q * x2 := by
    exact ⟨ mul_zero_CD _ _, scalar_comm _ _ _ |> Eq.symm ⟩;
  simp +decide [ h_simp, zero_mul_CD ];
  exact Prod.ext ( sub_zero_CD _ _ ) ( add_zero_CD _ _ )

/-
PROBLEM
Part 1: scalar (n+1) q * (x * y) = (scalar (n+1) q * x) * y

PROVIDED SOLUTION
Given ih1: ∀ x y : CD n, scalar n q * (x * y) = (scalar n q * x) * y, and ih2: ∀ x y : CD n, x * (scalar n q * y) = scalar n q * (x * y). Prove: ∀ x y : CD (n+1), scalar (n+1) q * (x * y) = (scalar (n+1) q * x) * y.

Intro ih1 ih2 x y. Obtain ⟨x1, x2⟩ := x and ⟨y1, y2⟩ := y.

Use scalar_mul_pair to compute:
- scalar (n+1) q * (x*y) = (scalar n q * (x1*y1 - star y2 * x2), scalar n q * (y2*x1 + x2 * star y1))
- scalar (n+1) q * x = (scalar n q * x1, scalar n q * x2)
- (scalar n q * x1, scalar n q * x2) * (y1, y2) = ((scalar n q*x1)*y1 - star y2*(scalar n q*x2), y2*(scalar n q*x1) + (scalar n q*x2)*star y1)

Apply Prod.ext, then prove each component:

Component 1: scalar n q * (x1*y1 - star y2 * x2) = (scalar n q*x1)*y1 - star y2*(scalar n q*x2)
  By scalar_mul_sub_CD: LHS = scalar n q*(x1*y1) - scalar n q*(star y2*x2)
  By ih1: scalar n q*(x1*y1) = (scalar n q*x1)*y1
  By ih2: star y2 * (scalar n q * x2) = scalar n q * (star y2 * x2)
  So RHS second term = star y2*(scalar n q*x2). We need scalar n q*(star y2*x2) = star y2*(scalar n q*x2).
  This follows from ih2 (with x := star y2, y := x2): star y2 * (scalar n q * x2) = scalar n q * (star y2 * x2).

Component 2: scalar n q * (y2*x1 + x2*star y1) = y2*(scalar n q*x1) + (scalar n q*x2)*star y1
  By left_distrib_CD: LHS = scalar n q*(y2*x1) + scalar n q*(x2*star y1)
  By ih2: y2*(scalar n q*x1) = scalar n q*(y2*x1)
  By ih1: scalar n q*(x2*star y1) = (scalar n q*x2)*star y1
-/
lemma scalar_mul_assoc_ind (n : Nat) (q : ℚ) :
    (∀ x y : CD n, scalar n q * (x * y) = (scalar n q * x) * y) →
    (∀ x y : CD n, x * (scalar n q * y) = scalar n q * (x * y)) →
    (∀ x y : CD (n+1), scalar (n+1) q * (x * y) = (scalar (n+1) q * x) * y) := by
  intro h1 h2 x y;
  convert Prod.ext _ _ using 1;
  · erw [ scalar_mul_pair, mul_cd ];
    erw [ scalar_mul_pair ];
    erw [ scalar_mul_sub_CD, h1, h2 ];
  · erw [ scalar_mul_pair, mul_cd ] ; simp +decide [ * ] ;
    erw [ scalar_mul_pair, left_distrib_CD ] ; simp +decide [ * ] ;

/-
PROBLEM
Part 2: x * (scalar (n+1) q * y) = scalar (n+1) q * (x * y)

PROVIDED SOLUTION
Given ih1: ∀ x y : CD n, scalar n q * (x * y) = (scalar n q * x) * y, and ih2: ∀ x y : CD n, x * (scalar n q * y) = scalar n q * (x * y). Prove: ∀ x y : CD (n+1), x * (scalar (n+1) q * y) = scalar (n+1) q * (x * y).

Let x = (x1, x2), y = (y1, y2). Use Prod.ext to split into components.

By scalar_mul_pair: scalar (n+1) q * y = (scalar n q * y1, scalar n q * y2).
By scalar_mul_pair: scalar (n+1) q * (x*y) = (scalar n q * (x1*y1 - star(y2)*x2), scalar n q * (y2*x1 + x2*star(y1))).

x * (scalar n q * y1, scalar n q * y2) = (x1*(scalar n q*y1) - star(scalar n q*y2)*x2, (scalar n q*y2)*x1 + x2*star(scalar n q*y1)).

First component:
LHS: x1*(scalar n q*y1) - star(scalar n q*y2)*x2
RHS: scalar n q * (x1*y1 - star(y2)*x2) = scalar n q*(x1*y1) - scalar n q*(star(y2)*x2) [scalar_mul_sub_CD]

x1*(scalar n q*y1) = scalar n q*(x1*y1) by ih2. ✓
star(scalar n q*y2) = scalar n q*star(y2) by star_scalar_mul_CD.
So star(scalar n q*y2)*x2 = (scalar n q*star(y2))*x2 = scalar n q*(star(y2)*x2) by ih1. ✓

Second component:
LHS: (scalar n q*y2)*x1 + x2*star(scalar n q*y1)
RHS: scalar n q * (y2*x1 + x2*star(y1)) = scalar n q*(y2*x1) + scalar n q*(x2*star(y1)) [left_distrib_CD]

(scalar n q*y2)*x1 = scalar n q*(y2*x1) by ih1. ✓
star(scalar n q*y1) = scalar n q*star(y1) by star_scalar_mul_CD.
x2*(scalar n q*star(y1)) = scalar n q*(x2*star(y1)) by ih2. ✓
-/
lemma mul_scalar_assoc_ind (n : Nat) (q : ℚ) :
    (∀ x y : CD n, scalar n q * (x * y) = (scalar n q * x) * y) →
    (∀ x y : CD n, x * (scalar n q * y) = scalar n q * (x * y)) →
    (∀ x y : CD (n+1), x * (scalar (n+1) q * y) = scalar (n+1) q * (x * y)) := by
  intro h1 h2 x y; exact (by
  -- By definition of scalar multiplication and multiplication in CD (n + 1), we can expand both sides.
  obtain ⟨x1, x2⟩ := x
  obtain ⟨y1, y2⟩ := y
  simp [scalar_mul_pair, h1, h2];
  erw [ scalar_mul_pair ];
  -- Apply the induction hypotheses to each component.
  have h_comp1 : x1 * (scalar n q * y1) - star (scalar n q * y2) * x2 = scalar n q * (x1 * y1 - star y2 * x2) := by
    rw [ h2, star_scalar_mul_CD ];
    simp +decide only [mul_assoc, scalar_mul_sub_CD];
    exact congr_arg _ ( by rw [ h1 ] )
  have h_comp2 : scalar n q * y2 * x1 + x2 * star (scalar n q * y1) = scalar n q * (y2 * x1 + x2 * star y1) := by
    rw [ left_distrib_CD, h1 ];
    rw [ ← h2, star_scalar_mul_CD ];
  exact Prod.ext h_comp1 h_comp2);

-- Joint proof of left and right scalar associativity
lemma scalar_assoc_joint (n : Nat) (q : ℚ) :
    (∀ x y : CD n, scalar n q * (x * y) = (scalar n q * x) * y) ∧
    (∀ x y : CD n, x * (scalar n q * y) = scalar n q * (x * y)) := by
  induction n with
  | zero =>
    refine ⟨fun x y => ?_, fun x y => ?_⟩ <;> (change ℚ at x y; change _ = (_ : ℚ); ring)
  | succ n ih => exact ⟨scalar_mul_assoc_ind n q ih.1 ih.2, mul_scalar_assoc_ind n q ih.1 ih.2⟩

lemma scalar_mul_assoc (n : Nat) (q : ℚ) (x y : CD n) :
    scalar n q * (x * y) = (scalar n q * x) * y :=
  (scalar_assoc_joint n q).1 x y

lemma smul_eq (n : Nat) (q : ℚ) (x : CD n) : q • x = scalar n q * x := rfl

lemma smul_mul_right (n : Nat) (q : ℚ) (x y : CD n) :
    (q • x) * y = q • (x * y) := by
  show (scalar n q * x) * y = scalar n q * (x * y)
  exact (scalar_mul_assoc n q x y).symm

lemma mul_smul_left (n : Nat) (q : ℚ) (x y : CD n) :
    x * (q • y) = q • (x * y) :=
  (scalar_assoc_joint n q).2 x y

/-
PROVIDED SOLUTION
Expand using right_distrib_CD and left_distrib_CD:
(a • P1 4 + b • Q1 4) * (b • P1 4 + c • Q1 4)
= (a • P1 4) * (b • P1 4) + (a • P1 4) * (c • Q1 4) + (b • Q1 4) * (b • P1 4) + (b • Q1 4) * (c • Q1 4)

Using smul_mul_right and mul_smul_left to pull out scalars. Each term becomes:
- smul_mul_right: (q • x) * y = q • (x * y)
- mul_smul_left: x * (q • y) = q • (x * y)

So:
(a • P1) * (b • P1) = a • ((P1) * (b • P1)) = a • (b • (P1 * P1)) [smul_mul_right then mul_smul_left]

But actually let me be careful:
(a • P1) * (b • P1) = (scalar 4 a * P1) * (scalar 4 b * P1)
= scalar 4 a * (P1 * (scalar 4 b * P1)) [by smul_mul_right backwards: (s*x)*y = s*(x*y)]
= scalar 4 a * (scalar 4 b * (P1 * P1)) [by mul_smul_left: x*(s*y) = s*(x*y)]
= scalar 4 a * scalar 4 b * (P1 * P1) [by scalar_mul_assoc: s*(s'*z) = (s*s')*z ... wait, this uses assoc of scalars]

Actually, scalar_mul_assoc gives: scalar * (x * y) = (scalar * x) * y. So:
scalar 4 a * (scalar 4 b * (P1 * P1)) = (scalar 4 a * scalar 4 b) * (P1 * P1) [by scalar_mul_assoc with x=scalar 4 b, y=P1*P1... no that's not right]

Wait. scalar_mul_assoc (n:=4) (q:=a) (x:=scalar 4 b * (P1*P1)) ... no, that's not the right form.

Let me use scalar_mul_scalar and scalar_mul_assoc more carefully.

scalar 4 a * (scalar 4 b * z) where z = P1*P1.
By scalar_mul_assoc: scalar 4 a * (scalar 4 b * z) = (scalar 4 a * scalar 4 b) * z [viewing scalar 4 b * z as a product]
Wait, scalar_mul_assoc says: scalar n q * (x * y) = (scalar n q * x) * y. So with q=a, x=scalar 4 b, y=z:
scalar 4 a * (scalar 4 b * z) = (scalar 4 a * scalar 4 b) * z. ✓

Then (scalar 4 a * scalar 4 b) = scalar 4 (a*b) [by scalar_mul_scalar]. And z = P1*P1 = scalar 4 (-2) [by p1_sq, viewing (-2:ℚ) as scalar 4 (-2)].

Wait, p1_sq says P1 4 * P1 4 = (-2 : ℚ). The coercion (-2 : ℚ) : CD 4 goes through the Coe instance which is scalar 4. So P1 4 * P1 4 = scalar 4 (-2).

So (scalar 4 (a*b)) * scalar 4 (-2) = scalar 4 (a*b*(-2)) [by scalar_mul_scalar].

Similarly:
(a • P1) * (c • Q1) = scalar 4 (a*c) * (P1*Q1) = scalar 4 (a*c) * 0 = 0 [Pattern1_CD4 gives P1*Q1 = 0, then mul_zero_CD]

(b • Q1) * (b • P1) = scalar 4 (b*b) * (Q1*P1) = 0 [Pattern1_CD4 gives Q1*P1 = 0]

(b • Q1) * (c • Q1) = scalar 4 (b*c) * Q1*Q1 = scalar 4 (b*c) * scalar 4 (-2) = scalar 4 (b*c*(-2))

So total = scalar 4 (a*b*(-2)) + 0 + 0 + scalar 4 (b*c*(-2))
= scalar 4 (a*b*(-2) + b*c*(-2)) [by scalar_add backwards]
= scalar 4 ((-2)*b*(a+c)) [by ring on rationals]

The key steps use: right_distrib_CD, left_distrib_CD, smul_mul_right, mul_smul_left, scalar_mul_scalar, p1_sq, q1_sq, Pattern1_CD4, mul_zero_CD, add_zero_CD, zero_add_CD, scalar_add.

Do the proof by: rw [right_distrib_CD, left_distrib_CD, left_distrib_CD], then simplify each of the 4 terms using the above, then combine.
-/
theorem bilateral_collapse (a b c : ℚ) :
  (a • P1 4 + b • Q1 4) * (b • P1 4 + c • Q1 4) =
  scalar 4 ((-2) * b * (a + c)) := by
  -- By the properties of scalar multiplication and the results from the previous theorems, we can simplify each term.
  have h1 : (a • P1 4) * (b • P1 4) = scalar 4 (-2 * a * b) := by
    -- By the properties of scalar multiplication and the results from the previous theorems, we can simplify each term using the distributive property.
    have h1 : (a • P1 4) * (b • P1 4) = a • (b • (P1 4 * P1 4)) := by
      rw [ smul_mul_right, mul_smul_left ];
    rw [ h1, p1_sq ];
    simp +decide [ mul_assoc, mul_comm, mul_left_comm, smul_smul, scalar_mul_scalar ];
    simp +decide [ neg_mul, mul_assoc, scalar_mul_scalar, smul_eq ]
  have h2 : (b • Q1 4) * (c • Q1 4) = scalar 4 (-2 * b * c) := by
    convert scalar_mul_assoc 4 b ( Q1 4 * ( c • Q1 4 ) ) using 1 ; ring;
    constructor <;> intro h <;> simp_all +decide [ mul_assoc, scalar_mul_assoc ];
    rw [ mul_smul_left, smul_mul_right ] ; ring;
    rw [ q1_sq ] ; norm_num [ smul_eq, scalar_mul_scalar ] ; ring;
  have h3 : (a • P1 4) * (c • Q1 4) = 0 := by
    convert mul_smul_left 4 c ( P1 4 ) ( Q1 4 ) using 1;
    · rw [ show P1 4 * c • Q1 4 = 0 from ?_ ];
      · rw [ smul_mul_right, mul_smul_left, show P1 4 * Q1 4 = 0 from ?_ ] ; norm_num [ smul_eq, scalar_mul_scalar, p1_sq, q1_sq, Pattern1_CD4 ];
        · rw [ mul_zero_CD, mul_zero_CD ];
        · exact Pattern1_CD4.1;
      · convert mul_smul_left 4 c ( P1 4 ) ( Q1 4 ) using 1;
        rw [ show P1 4 * Q1 4 = 0 from by exact Pattern1_CD4.1 ];
        rw [ smul_eq, mul_zero_CD ];
    · rw [ show P1 4 * Q1 4 = 0 from by exact Pattern1_CD4.1 ];
      rw [ smul_eq, mul_zero_CD ]
  have h4 : (b • Q1 4) * (b • P1 4) = 0 := by
    -- By the properties of scalar multiplication and the results from the previous theorems, we can simplify each term. Specifically, we use the fact that $Q1 4 * P1 4 = 0$.
    have h4 : (b • Q1 4) * (b • P1 4) = b • (Q1 4 * (b • P1 4)) := by
      rw [ smul_mul_right ];
    rw [ h4, mul_smul_left ];
    -- By the properties of scalar multiplication and the results from the previous theorems, we can simplify each term. Specifically, we use the fact that $Q1 4 * P1 4 = 0$ to conclude the proof.
    have h5 : Q1 4 * P1 4 = 0 := by
      exact Pattern1_CD4.2
    rw [h5]
    simp [smul_eq];
    rw [ mul_zero_CD, mul_zero_CD ];
  -- Combine the results of the four terms.
  have h_combined : (a • P1 4 + b • Q1 4) * (b • P1 4 + c • Q1 4) = scalar 4 (-2 * a * b) + scalar 4 (-2 * b * c) := by
    rw [ ← h1, ← h2, right_distrib_CD, left_distrib_CD, left_distrib_CD ] ; aesop;
  rw [ h_combined, ← scalar_add ] ; ring

theorem scalar_channel (a b c : ℚ) :
  ∃ (k : ℚ), (a • P1 4 + b • Q1 4) * (b • P1 4 + c • Q1 4) = scalar 4 k :=
  ⟨(-2) * b * (a + c), bilateral_collapse a b c⟩