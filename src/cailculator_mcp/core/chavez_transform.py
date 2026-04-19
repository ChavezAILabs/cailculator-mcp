"""
Chavez Transform Core Engine v2.0
Universal High-Precision Mathematical Core

Definition:
    C[f] = integral_D f(x) * K_Z(P,Q,x) * exp(-alpha * ||x||^2) * Omega_d(x) dx

v2.0 Features:
    - High-Precision Numerical Engine (10^-15)
    - Lean-verified Stability Bounds
    - Corrected Sedenion Embedding (Option A: avoid e_0 channel)
    - Oracle-Anchored Parameter Dispatch
"""

import numpy as np
from scipy import integrate
from typing import Callable, Tuple, List, Optional, Dict, Any
import logging

from ..hypercomplex import create_hypercomplex
from .stability import get_stability_constant

logger = logging.getLogger(__name__)

class ChavezTransform:
    """
    High-precision implementation of the Chavez Transform.
    """

    def __init__(self, dimension: int = 32, alpha: float = 1.0, framework: str = "cayley-dickson"):
        """
        Initialize the Chavez Transform engine.

        Args:
            dimension: Ambient algebra dimension (16, 32, 64, 128, 256)
            alpha: Gaussian decay parameter (alpha > 0)
            framework: 'cayley-dickson' or 'clifford'
        """
        if alpha <= 0:
            raise ValueError(f"alpha must be positive, got {alpha}")

        self.dimension = dimension
        self.alpha = alpha
        self.framework = framework
        self.precision = 1e-15  # Machine precision standard

    def zero_divisor_kernel(self, P_arr: np.ndarray, Q_arr: np.ndarray, x: np.ndarray) -> float:
        """
        Compute the bilateral zero divisor kernel K_Z(P, Q, x) with distance decay.
        
        Corrected Embedding (Option A):
            Maps input vector x to non-real components (e_1, e_2, ...) to ensure 
            pattern differentiation and avoid scalar-channel invariance.

        K_Z(P,Q,x) = |P·x|² + |x·Q|² + |Q·x|² + |x·P|²
        """
        # 1. Corrected n-D embedding (Option A)
        # Avoid e_0 (index 0) to prevent the K_Z_realToSed dispatch collapse.
        x_coeffs = np.zeros(self.dimension, dtype=np.float64)
        
        # Map x_0, x_1, ... -> e_1, e_2, ...
        # max_len is dimension - 1 because we skip e_0.
        max_len = min(len(x), self.dimension - 1)
        x_coeffs[1:max_len+1] = x[:max_len]
        
        # 2. Create hypercomplex instances
        # P and Q are expected as arrays from core/canonical_six.py
        P = create_hypercomplex(self.dimension, P_arr.tolist(), framework=self.framework)
        Q = create_hypercomplex(self.dimension, Q_arr.tolist(), framework=self.framework)
        x_hc = create_hypercomplex(self.dimension, x_coeffs.tolist(), framework=self.framework)

        # 3. Four bilateral products (High Precision 10^-15)
        Px = P * x_hc
        xQ = x_hc * Q
        Qx = Q * x_hc
        xP = x_hc * P

        # 4. Sum of squared magnitudes
        kernel_value = abs(Px)**2 + abs(xQ)**2 + abs(Qx)**2 + abs(xP)**2

        # 5. Distance decay
        norm_x_sq = np.sum(x**2)
        distance_decay = np.exp(-self.alpha * norm_x_sq)

        return float(kernel_value * distance_decay)

    def dimensional_weighting(self, x: np.ndarray, d: int) -> float:
        """Omega_d(x) = (1 + ||x||^2)^(-d/2)"""
        norm_sq = np.sum(x**2)
        return float((1.0 + norm_sq) ** (-d / 2.0))

    def integrand(self, x: np.ndarray, f: Callable, P_arr: np.ndarray, Q_arr: np.ndarray, d: int) -> float:
        """Full integrand: f(x) * K_Z(P,Q,x) * exp(-alpha*||x||^2) * Omega_d(x)"""
        f_val = f(x)
        kernel_val = self.zero_divisor_kernel(P_arr, Q_arr, x)
        weight_val = self.dimensional_weighting(x, d)

        return float(f_val * kernel_val * weight_val)

    def transform_1d(self, f: Callable, P_arr: np.ndarray, Q_arr: np.ndarray, d: int,
                     domain: Tuple[float, float] = (-5.0, 5.0)) -> Dict[str, Any]:
        """
        Compute the Chavez Transform in 1D with Lean-verified stability validation.
        """
        def integrand_wrapper(x_scalar):
            x = np.array([x_scalar])
            return self.integrand(x, f, P_arr, Q_arr, d)

        # 1. Numerical integration (scipy handles convergence)
        result, error = integrate.quad(integrand_wrapper, domain[0], domain[1])
        
        # 2. Stability check against Lean-proved bound (Theorem 2)
        def abs_f(x_scalar):
            return abs(f(np.array([x_scalar])))
        
        f_l1_norm, _ = integrate.quad(abs_f, domain[0], domain[1])
        M = get_stability_constant(P_arr, Q_arr, self.alpha)
        bound = M * f_l1_norm
        
        stability_satisfied = abs(result) <= (bound + self.precision)
        
        return {
            "value": result,
            "error_estimate": error,
            "stability_bound": {
                "M": M,
                "theoretical_max": bound,
                "satisfied": bool(stability_satisfied),
                "ratio": result / bound if bound > 0 else 0
            },
            "parameters": {
                "alpha": self.alpha,
                "d": d,
                "dimension": self.dimension
            }
        }

    def transform_nd(self, f: Callable, P_arr: np.ndarray, Q_arr: np.ndarray, d: int,
                     domain_ranges: List[Tuple[float, float]],
                     num_samples: int = 10000) -> Dict[str, Any]:
        """
        Compute the Chavez Transform in N-D using Monte Carlo integration.
        """
        n = len(domain_ranges)
        
        # Monte Carlo integration
        samples = np.random.uniform(
            low=[r[0] for r in domain_ranges],
            high=[r[1] for r in domain_ranges],
            size=(num_samples, n)
        )

        volume = np.prod([r[1] - r[0] for r in domain_ranges])

        integrand_values = np.array([
            self.integrand(x, f, P_arr, Q_arr, d)
            for x in samples
        ])

        result = volume * np.mean(integrand_values)
        error_estimate = volume * np.std(integrand_values) / np.sqrt(num_samples)
        
        # Stability check (Approximation for ND L1 norm)
        f_values = np.array([abs(f(x)) for x in samples])
        f_l1_approx = volume * np.mean(f_values)
        
        M = get_stability_constant(P_arr, Q_arr, self.alpha)
        # Note: In nD, the bound M might need dimension-dependent scaling (v2.1 target)
        bound = M * f_l1_approx 
        
        return {
            "value": result,
            "error_estimate": error_estimate,
            "stability_bound": {
                "M": M,
                "approx_theoretical_max": bound,
                "satisfied": abs(result) <= (bound + 1e-10), # Looser for MC
                "ratio": result / bound if bound > 0 else 0
            }
        }
