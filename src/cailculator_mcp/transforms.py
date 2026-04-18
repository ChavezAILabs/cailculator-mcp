"""
Chavez Transform - A Novel Integral Transform for High-Dimensional Data

This module implements the Chavez Transform, which uses bilateral zero divisor structure
from Cayley-Dickson algebras to transform high-dimensional data, analogous to
how Fourier Transforms work in frequency space.

Definition:
    For f in L^1(D), D subset of R^n:

    C[f] = integral_D f(x) * K_Z(P,Q,x) * exp(-alpha * ||x||^2) * Omega_d(x) dx

    Where:
        K_Z(P,Q,x) = |P·x|² + |x·Q|² + |Q·x|² + |x·P|²
        (P,Q) = bilateral zero divisor pairs from the Canonical Six
        P × Q = 0 AND Q × P = 0 (bilateral zero divisor property)
        exp(-alpha * ||x||^2) = exponential distance decay, alpha > 0
        Omega_d(x) = (1 + ||x||^2)^(-d/2) = dimensional weighting

    Full kernel: K(P,Q,x,alpha,d) = K_Z(P,Q,x) * exp(-alpha * ||x||^2) * Omega_d(x)

    Note: The three-factor kernel structure ensures:
        - K_Z encodes the bilateral zero divisor geometry (algebraic structure)
        - exp(-alpha * ||x||^2) ensures rapid decay at infinity (integrability)
        - Omega_d(x) provides additional dimensional decay control

The Canonical Six bilateral zero divisor pairs (sedenion indices):
    1. P=(e_1 + e_14), Q=(e_3 + e_12):  P×Q = 0 AND Q×P = 0
    2. P=(e_3 + e_12), Q=(e_5 + e_10):  P×Q = 0 AND Q×P = 0
    3. P=(e_4 + e_11), Q=(e_6 + e_9):   P×Q = 0 AND Q×P = 0
    4. P=(e_1 - e_14), Q=(e_3 - e_12):  P×Q = 0 AND Q×P = 0
    5. P=(e_1 - e_14), Q=(e_5 + e_10):  P×Q = 0 AND Q×P = 0
    6. P=(e_2 - e_13), Q=(e_6 + e_9):   P×Q = 0 AND Q×P = 0

Theorems (formally verified in ChavezTransform_genuine.lean, April 2026):
    1. Convergence: For bounded f in L^1(D) and alpha > 0, C[f] converges absolutely.
       Proof: unconditional on P*Q=0. Axiom footprint: [propext, Classical.choice, Quot.sound]
    2. Stability Bounds: |C[f]| <= stability_constant * ||f||_1
       where stability_constant(P,Q,alpha) = 2*(||P||^2 + ||Q||^2) / (alpha * exp(1))
       Proved constant is tighter than the earlier estimate (||P||^2+||Q||^2)*sqrt(pi/alpha).
       Proof: exact K_Z formula on scalar inputs + sharp bound t*exp(-t) <= 1/e.
       Axiom footprint: [propext, Classical.choice, Quot.sound]

Note on domain: The integration domain D is parametric. The default (-5.0, 5.0)
used in transform_1d and transform_nd is a numerical convenience, not a
mathematical constant of the transform definition.

GitHub: https://github.com/ChavezAILabs/CAIL-rh-investigation
Zenodo: https://doi.org/10.5281/zenodo.17402495
"""

import numpy as np
from scipy import integrate
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from typing import Callable, Tuple, List, Optional
import sys
import os

# Add parent directory to path for hypercomplex import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from hypercomplex import Pathion
except ImportError:
    print("Warning: hypercomplex library not found. Using mock implementation.")
    # Mock Pathion class for testing
    class Pathion:
        def __init__(self, *coeffs):
            self.coeffs = np.array(coeffs if coeffs else [0.0]*32)
        def __mul__(self, other):
            # Simplified mock multiplication
            result_coeffs = [0.0] * 32
            return Pathion(*result_coeffs)
        def __abs__(self):
            return np.linalg.norm(self.coeffs)


class ChavezTransform:
    """
    Implements the Chavez Transform for high-dimensional data using zero divisor kernels.
    """

    def __init__(self, dimension: int = 32, alpha: float = 1.0):
        """
        Initialize the Chavez Transform.

        Args:
            dimension: Dimension of the ambient space (default: 32 for pathions)
            alpha: Convergence parameter (must be > 0)
        """
        if alpha <= 0:
            raise ValueError("alpha must be positive")

        self.dimension = dimension
        self.alpha = alpha

    def zero_divisor_kernel(self, P: Pathion, Q: Pathion, x: np.ndarray) -> float:
        """
        Compute the bilateral zero divisor kernel K_Z(P, Q, x) with distance decay.

        Full kernel component: K_Z(P,Q,x) * exp(-alpha * ||x||^2)

        K_Z(P,Q,x) = |P·x|² + |x·Q|² + |Q·x|² + |x·P|²

        Where P and Q are bilateral zero divisor pairs (P×Q = 0 AND Q×P = 0)
        from the Canonical Six. The bilateral structure (all four products) is
        required because Cayley-Dickson multiplication is non-commutative:
        P·x ≠ x·P in general.

        Note: This method returns K_Z * exp(-alpha*||x||^2). The dimensional
        weighting Omega_d(x) = (1 + ||x||^2)^(-d/2) is applied separately in
        the integrand() method. The full kernel is:
            K(P,Q,x,alpha,d) = K_Z(P,Q,x) * exp(-alpha*||x||^2) * Omega_d(x)

        Args:
            P: First pathion element of bilateral zero divisor pair
            Q: Second pathion element of bilateral zero divisor pair
            x: Point in R^n where to evaluate kernel

        Returns:
            K_Z(P,Q,x) * exp(-alpha * ||x||^2)
        """
        # Convert x to Pathion
        x_coeffs = np.zeros(32)
        x_len = min(len(x), 32)
        x_coeffs[:x_len] = x[:x_len]
        x_pathion = Pathion(*x_coeffs)

        # Four bilateral products
        Px = P * x_pathion
        xQ = x_pathion * Q
        Qx = Q * x_pathion
        xP = x_pathion * P

        # Sum of squared magnitudes
        kernel_value = abs(Px)**2 + abs(xQ)**2 + abs(Qx)**2 + abs(xP)**2

        # Distance decay
        distance_decay = np.exp(-self.alpha * np.linalg.norm(x)**2)

        return kernel_value * distance_decay

    def dimensional_weighting(self, x: np.ndarray, d: int) -> float:
        """
        Compute dimensional weighting Omega_d(x).

        Omega_d(x) = (1 + ||x||^2)^(-d/2)

        Args:
            x: Point in R^n
            d: Dimension parameter

        Returns:
            Weighting value at x
        """
        norm_sq = np.linalg.norm(x) ** 2
        return (1.0 + norm_sq) ** (-d / 2.0)

    def integrand(self, x: np.ndarray, f: Callable, P: Pathion, Q: Pathion, d: int) -> float:
        """
        Compute the full integrand: f(x) * K_Z(P,Q,x) * exp(-alpha*||x||^2) * Omega_d(x)

        This is the complete three-factor kernel:
            f(x)                         — function to transform
            K_Z(P,Q,x)*exp(-alpha*||x||²) — bilateral kernel with decay (from zero_divisor_kernel)
            Omega_d(x)                   — dimensional weighting (from dimensional_weighting)

        Args:
            x: Point in R^n
            f: Function to transform
            P: First pathion of bilateral zero divisor pair
            Q: Second pathion of bilateral zero divisor pair
            d: Dimension parameter for weighting

        Returns:
            f(x) * K_Z(P,Q,x) * exp(-alpha*||x||^2) * (1+||x||^2)^(-d/2)
        """
        f_val = f(x)
        kernel_val = self.zero_divisor_kernel(P, Q, x)
        weight_val = self.dimensional_weighting(x, d)

        return f_val * kernel_val * weight_val

    def transform_1d(self, f: Callable, P: Pathion, Q: Pathion, d: int,
                     domain: Tuple[float, float] = (-5.0, 5.0)) -> float:
        """
        Compute the Chavez Transform in 1D using numerical integration.

        Args:
            f: Function to transform (callable taking 1D array)
            P: First pathion of zero divisor pair
            Q: Second pathion of zero divisor pair
            d: Dimension parameter
            domain: Integration domain (a, b). Default (-5.0, 5.0) is a numerical
                    convenience. The canonical mathematical definition uses parametric
                    D = [a,b] — see ChavezTransform_genuine.lean for the formal statement.

        Returns:
            Transform value C[f]
        """
        def integrand_1d(x_scalar):
            x = np.array([x_scalar])
            return self.integrand(x, f, P, Q, d)

        result, error = integrate.quad(integrand_1d, domain[0], domain[1])
        return result

    def transform_nd(self, f: Callable, P: Pathion, Q: Pathion, d: int,
                     domain_ranges: List[Tuple[float, float]],
                     method: str = 'monte_carlo',
                     num_samples: int = 10000) -> float:
        """
        Compute the Chavez Transform in N-D using numerical integration.

        Args:
            f: Function to transform (callable taking ND array)
            P: First pathion of zero divisor pair
            Q: Second pathion of zero divisor pair
            d: Dimension parameter
            domain_ranges: List of (min, max) for each dimension
            method: Integration method ('monte_carlo' or 'grid')
            num_samples: Number of samples for Monte Carlo

        Returns:
            Transform value C[f]
        """
        n = len(domain_ranges)

        if method == 'monte_carlo':
            # Monte Carlo integration
            samples = np.random.uniform(
                low=[r[0] for r in domain_ranges],
                high=[r[1] for r in domain_ranges],
                size=(num_samples, n)
            )

            volume = np.prod([r[1] - r[0] for r in domain_ranges])

            integrand_values = np.array([
                self.integrand(x, f, P, Q, d)
                for x in samples
            ])

            result = volume * np.mean(integrand_values)

        elif method == 'grid':
            # Grid-based integration (only practical for low dimensions)
            if n > 3:
                raise ValueError("Grid integration only practical for n <= 3")

            # Create grid
            grid_size = int(num_samples ** (1/n))
            grids = [np.linspace(r[0], r[1], grid_size) for r in domain_ranges]
            mesh = np.meshgrid(*grids, indexing='ij')
            points = np.stack([m.ravel() for m in mesh], axis=-1)

            # Evaluate integrand
            integrand_values = np.array([
                self.integrand(x, f, P, Q, d)
                for x in points
            ])

            # Trapezoidal rule
            dx = np.prod([(r[1] - r[0]) / (grid_size - 1) for r in domain_ranges])
            result = np.sum(integrand_values) * dx

        else:
            raise ValueError(f"Unknown method: {method}")

        return result

    def verify_convergence_theorem(self, f: Callable, P: Pathion, Q: Pathion, d: int,
                                   domain: Tuple[float, float] = (-5.0, 5.0),
                                   num_trials: int = 10) -> dict:
        """
        Verify Theorem 1: Convergence theorem.

        For bounded f in L^1(D) and alpha > 0, C[f] converges absolutely.

        Args:
            f: Test function
            P: First pathion of zero divisor pair
            Q: Second pathion of zero divisor pair
            d: Dimension parameter
            domain: Integration domain
            num_trials: Number of different alpha values to test

        Returns:
            Dictionary with convergence analysis results
        """
        alphas = np.logspace(-1, 2, num_trials)  # Test alpha from 0.1 to 100
        results = []

        for alpha_test in alphas:
            # Temporarily change alpha
            old_alpha = self.alpha
            self.alpha = alpha_test

            try:
                transform_value = self.transform_1d(f, P, Q, d, domain)
                converged = np.isfinite(transform_value)
                results.append({
                    'alpha': alpha_test,
                    'value': transform_value,
                    'converged': converged
                })
            except Exception as e:
                results.append({
                    'alpha': alpha_test,
                    'value': np.nan,
                    'converged': False,
                    'error': str(e)
                })
            finally:
                self.alpha = old_alpha

        convergence_rate = sum(r['converged'] for r in results) / len(results)

        return {
            'theorem': 'Convergence (Theorem 1)',
            'convergence_rate': convergence_rate,
            'all_converged': convergence_rate == 1.0,
            'results': results
        }

    def verify_stability_bounds(self, f: Callable, P: Pathion, Q: Pathion, d: int,
                               domain: Tuple[float, float] = (-5.0, 5.0),
                               num_trials: int = 10) -> dict:
        """
        Verify Theorem 2: Stability bounds.

        |C[f]| <= M * ||f||_1
        where M = 2*(||P||^2 + ||Q||^2) / (alpha * exp(1))
        Formally proved in ChavezTransform_genuine.lean (April 2026).
        Axiom footprint: [propext, Classical.choice, Quot.sound]

        Args:
            f: Test function
            P: First pathion of zero divisor pair
            Q: Second pathion of zero divisor pair
            d: Dimension parameter
            domain: Integration domain
            num_trials: Number of tests with different functions

        Returns:
            Dictionary with stability analysis results
        """
        # Proved stability constant from ChavezTransform_genuine.lean:
        #   stability_constant(P,Q,alpha) = 2*(||P||^2 + ||Q||^2) / (alpha * exp(1))
        # Derived from exact K_Z formula on scalar inputs + sharp bound t*exp(-t) <= 1/e.
        # Supersedes earlier estimate (||P||^2 + ||Q||^2) * sqrt(pi/alpha).
        import math
        P_norm = abs(P)
        Q_norm = abs(Q)
        M = 2.0 * (P_norm ** 2 + Q_norm ** 2) / (self.alpha * math.e)

        # Compute L1 norm of f
        def abs_f(x_scalar):
            x = np.array([x_scalar])
            return np.abs(f(x))

        f_L1_norm, _ = integrate.quad(abs_f, domain[0], domain[1])

        # Compute transform
        transform_value = self.transform_1d(f, P, Q, d, domain)

        # Check bound
        bound = M * f_L1_norm
        satisfied = np.abs(transform_value) <= bound

        ratio = np.abs(transform_value) / bound if bound > 0 else np.inf

        return {
            'theorem': 'Stability Bounds (Theorem 2)',
            'transform_value': transform_value,
            'stability_constant_M': M,
            'f_L1_norm': f_L1_norm,
            'theoretical_bound': bound,
            'bound_satisfied': satisfied,
            'ratio': ratio,
            'alpha': self.alpha,
            'P_norm': P_norm,
            'Q_norm': Q_norm
        }

    def canonical_six_analysis(self, f: Callable, d: int,
                              domain: Tuple[float, float] = (-5.0, 5.0)) -> dict:
        """
        Complete Canonical Six Analysis across all bilateral zero-divisor loci.

        Applies the transform using all six Canonical Six patterns and returns
        a comprehensive analysis showing which loci interact most strongly with
        the data.

        Args:
            f: Function to transform (callable taking array)
            d: Dimension parameter for weighting
            domain: Integration domain (a, b)

        Returns:
            Dictionary containing:
            - 'locus_1' through 'locus_6': Transform values for each pattern
            - 'dominant_locus': Which locus had strongest response (1-6)
            - 'mean_response': Mean across all six loci
            - 'std_response': Standard deviation across loci
            - 'dimension': Pathion dimension used
        """
        results = {}

        # Apply transform with each of the six patterns
        for locus_id in range(1, 7):
            P, Q = create_canonical_six_pattern(locus_id)
            results[f'locus_{locus_id}'] = self.transform_1d(f, P, Q, d, domain)

        # Compute statistics
        values = [results[f'locus_{i}'] for i in range(1, 7)]
        results['dominant_locus'] = max(range(1, 7), key=lambda i: abs(results[f'locus_{i}']))
        results['mean_response'] = np.mean(values)
        results['std_response'] = np.std(values)
        results['dimension'] = self.dimension

        return results

    def transform_auto(self, f: Callable, d: int,
                      domain: Tuple[float, float] = (-5.0, 5.0)) -> dict:
        """
        Auto-select best locus from Canonical Six with interestingness detection.

        Internally runs all six patterns, returns result from the dominant one,
        plus metadata about the analysis including whether the results show
        interesting patterns that warrant deeper investigation.

        Args:
            f: Function to transform (callable taking array)
            d: Dimension parameter for weighting
            domain: Integration domain (a, b)

        Returns:
            Dictionary containing:
            - 'value': Transform value from dominant locus
            - 'dominant_locus': Which locus was strongest (1-6)
            - 'locus_values': All six locus values for transparency
            - 'mean_response': Mean across all loci
            - 'std_response': Standard deviation across loci
            - 'interesting': Boolean flag - true if patterns warrant attention
            - 'interestingness_reason': Why it's interesting (if applicable)
            - 'suggest_full_analysis': Recommendation to run full analysis
            - 'coefficient_of_variation': CV = std/mean
            - 'dominance_ratio': How much stronger dominant locus is vs mean
            - 'dimension': Pathion dimension used
        """
        # Run full analysis internally
        analysis = self.canonical_six_analysis(f, d, domain)

        dominant = analysis['dominant_locus']
        dominant_value = analysis[f'locus_{dominant}']
        mean = analysis['mean_response']
        std = analysis['std_response']

        # Calculate interestingness metrics
        cv = std / abs(mean) if abs(mean) > 1e-10 else 0.0
        dominance_ratio = abs(dominant_value) / abs(mean) if abs(mean) > 1e-10 else 1.0

        # Check if all loci are responding (multi-modal)
        all_active = all(abs(analysis[f'locus_{i}']) > 1e-3 for i in range(1, 7))

        # Detect interesting patterns
        interesting = False
        reason = None

        if cv > 0.5:  # High variance - different loci responding very differently
            interesting = True
            reason = "high_variance"
        elif dominance_ratio > 2.0:  # One locus much stronger than others
            interesting = True
            reason = "strong_dominance"
        elif all_active:  # All loci active - complex structure
            interesting = True
            reason = "multi_modal"

        return {
            'value': dominant_value,
            'dominant_locus': dominant,
            'locus_values': {f'locus_{i}': analysis[f'locus_{i}'] for i in range(1, 7)},
            'mean_response': mean,
            'std_response': std,
            'interesting': interesting,
            'interestingness_reason': reason,
            'suggest_full_analysis': interesting,
            'coefficient_of_variation': cv,
            'dominance_ratio': dominance_ratio,
            'dimension': analysis['dimension']
        }


def create_canonical_six_pattern(pattern_id: int) -> Tuple[Pathion, Pathion]:
    """
    Create a Pathion pair corresponding to one of the Canonical Six bilateral
    zero divisor patterns.

    The Canonical Six are the fundamental bilateral zero divisor pairs in
    sedenions (16D Cayley-Dickson algebra). BILATERAL means P×Q = 0 AND Q×P = 0.
    Implemented here in 32D pathion space — sedenion components occupy indices
    0–15; indices 16–31 are zero.

    Canonical Six bilateral pairs (P, Q):
        1. P=(e_1+e_14), Q=(e_3+e_12):  P×Q=0 AND Q×P=0
        2. P=(e_3+e_12), Q=(e_5+e_10):  P×Q=0 AND Q×P=0
        3. P=(e_4+e_11), Q=(e_6+e_9):   P×Q=0 AND Q×P=0
        4. P=(e_1-e_14), Q=(e_3-e_12):  P×Q=0 AND Q×P=0
        5. P=(e_1-e_14), Q=(e_5+e_10):  P×Q=0 AND Q×P=0
        6. P=(e_2-e_13), Q=(e_6+e_9):   P×Q=0 AND Q×P=0

    Formally verified in BilateralCollapse.lean (Lean 4, zero sorries):
        #print axioms bilateral_collapse
        → [propext, Classical.choice, Quot.sound]

    Args:
        pattern_id: Which canonical pattern to use (1-6)

    Returns:
        Tuple of (P, Q) where P×Q = 0 AND Q×P = 0
    """
    # Canonical Six bilateral pairs: ((P_idx_a, P_idx_b, P_sign), (Q_idx_c, Q_idx_d, Q_sign))
    # P = e_a + sign*e_b,  Q = e_c + sign*e_d
    patterns = {
        1: ((1, 14, +1), (3, 12, +1)),   # P=(e_1+e_14), Q=(e_3+e_12): P×Q=0 AND Q×P=0
        2: ((3, 12, +1), (5, 10, +1)),   # P=(e_3+e_12), Q=(e_5+e_10): P×Q=0 AND Q×P=0
        3: ((4, 11, +1), (6,  9, +1)),   # P=(e_4+e_11), Q=(e_6+e_9):  P×Q=0 AND Q×P=0
        4: ((1, 14, -1), (3, 12, -1)),   # P=(e_1-e_14), Q=(e_3-e_12): P×Q=0 AND Q×P=0
        5: ((1, 14, -1), (5, 10, +1)),   # P=(e_1-e_14), Q=(e_5+e_10): P×Q=0 AND Q×P=0
        6: ((2, 13, -1), (6,  9, +1)),   # P=(e_2-e_13), Q=(e_6+e_9):  P×Q=0 AND Q×P=0
    }

    if pattern_id not in patterns:
        raise ValueError(f"pattern_id must be 1-6, got {pattern_id}")

    (a, b, sign_P), (c, d, sign_Q) = patterns[pattern_id]

    # Create first pathion P = e_a ± e_b
    coeffs_P = [0.0] * 32
    coeffs_P[a] = 1.0
    coeffs_P[b] = float(sign_P)
    P = Pathion(*coeffs_P)

    # Create second pathion Q = e_c ± e_d
    coeffs_Q = [0.0] * 32
    coeffs_Q[c] = 1.0
    coeffs_Q[d] = float(sign_Q)
    Q = Pathion(*coeffs_Q)

    return P, Q


def stability_constant(P: Pathion, Q: Pathion, alpha: float) -> float:
    """
    Compute the proved stability constant for the Chavez Transform.

    Formally verified in ChavezTransform_genuine.lean (Lean 4, April 2026):
        stability_constant(P, Q, alpha) = 2*(||P||^2 + ||Q||^2) / (alpha * exp(1))

    This is the tight bound from the exact K_Z formula on scalar inputs:
        K_Z(P, Q, realToSed(x)) = 2*x^2*(||P||^2 + ||Q||^2)  [exact, not an estimate]
    combined with the sharp inequality t*exp(-t) <= 1/e.

    The stability theorem guarantees:
        |C[f](P,Q,alpha,d)| <= stability_constant(P,Q,alpha) * L1_norm(f)
    unconditionally — P*Q=0 is not required.

    Axiom footprint: [propext, Classical.choice, Quot.sound]
    GitHub: https://github.com/ChavezAILabs/CAIL-rh-investigation

    Args:
        P: First pathion of bilateral zero divisor pair
        Q: Second pathion of bilateral zero divisor pair
        alpha: Gaussian decay parameter (must be > 0)

    Returns:
        Proved stability constant M such that |C[f]| <= M * ||f||_1
    """
    import math
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    P_norm = abs(P)
    Q_norm = abs(Q)
    return 2.0 * (P_norm ** 2 + Q_norm ** 2) / (alpha * math.e)


def test_functions():
    """
    Create a suite of test functions for validation.

    Returns:
        Dictionary of test functions
    """
    return {
        'gaussian': lambda x: np.exp(-np.linalg.norm(x)**2),
        'polynomial': lambda x: 1.0 + np.sum(x**2),
        'exponential_decay': lambda x: np.exp(-np.abs(np.sum(x))),
        'sinc': lambda x: np.sinc(np.linalg.norm(x)),
        'bounded_oscillatory': lambda x: np.sin(np.linalg.norm(x)) * np.exp(-0.1 * np.linalg.norm(x)**2),
    }


if __name__ == "__main__":
    print("="*80)
    print("CHAVEZ TRANSFORM - CANONICAL SIX IMPLEMENTATION")
    print("="*80)
    print()

    # Initialize
    ct = ChavezTransform(dimension=32, alpha=1.0)
    f_test = lambda x: np.exp(-np.linalg.norm(x)**2)
    d = 2
    domain = (-3.0, 3.0)

    print("Initialized Chavez Transform")
    print(f"  Dimension: {ct.dimension}")
    print(f"  Alpha: {ct.alpha}")
    print()

    # Test that zero divisor pairs work correctly
    print("="*80)
    print("PART 1: CANONICAL SIX VERIFICATION")
    print("="*80)
    print()

    print("Verifying bilateral zero divisor properties:")
    for pattern_id in range(1, 7):
        P, Q = create_canonical_six_pattern(pattern_id)
        product_norm = abs(P * Q)
        status = "OK" if product_norm < 1e-10 else "FAILED"
        print(f"  Pattern {pattern_id}: ||P x Q|| = {product_norm:.6e} [{status}]")
    print()

    print("="*80)
    print("PART 2: CANONICAL SIX ANALYSIS (Full)")
    print("="*80)
    print()

    full_analysis = ct.canonical_six_analysis(f_test, d, domain)

    print("Complete locus analysis:")
    for i in range(1, 7):
        print(f"  Locus {i}: {full_analysis[f'locus_{i}']:.6e}")
    print(f"\nDominant locus: {full_analysis['dominant_locus']}")
    print(f"Mean response: {full_analysis['mean_response']:.6e}")
    print(f"Std response: {full_analysis['std_response']:.6e}")
    print()

    print("="*80)
    print("PART 3: TRANSFORM AUTO (Smart Default)")
    print("="*80)
    print()

    auto_result = ct.transform_auto(f_test, d, domain)

    print(f"Auto-selected result: {auto_result['value']:.6e}")
    print(f"Dominant locus: {auto_result['dominant_locus']}")
    print(f"Coefficient of variation: {auto_result['coefficient_of_variation']:.3f}")
    print(f"Dominance ratio: {auto_result['dominance_ratio']:.2f}")
    print(f"\nInteresting: {auto_result['interesting']}")
    if auto_result['interesting']:
        print(f"Reason: {auto_result['interestingness_reason']}")
        print(f"Suggest full analysis: {auto_result['suggest_full_analysis']}")

    print()
    print("="*80)
    print("IMPLEMENTATION COMPLETE")
    print("="*80)
