"""
Pattern Detection - CAILculator v2.0 Staging
Structural Analysis governed by Lean-Verified Theorems

Refactored to use:
- detect_24_family() for algebraic membership
- map_to_weyl_orbit() for geometric projection
- ChavezTransform core for structural numerics
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging

from .core.chavez_transform import ChavezTransform
from .core.extended_structures import generate_24_families, map_to_weyl_orbit, detect_g2_family

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Represents a detected mathematical pattern."""
    pattern_type: str
    confidence: float
    description: str
    indices: Optional[List[int]] = None
    metrics: Optional[Dict[str, Any]] = None

class PatternDetector:
    """
    v2.0 Pattern Detector.
    Transitioned from heuristic symmetry to algebraic structural detection.
    """
    
    def __init__(self, alpha: float = 1.0, dimension: int = 32):
        self.alpha = alpha
        self.dimension = dimension
        self.ct = ChavezTransform(dimension=dimension, alpha=alpha)
    
    def detect_all_patterns(self, data: np.ndarray) -> List[Pattern]:
        """Orchestrates structural and geometric detection."""
        patterns = []

        # 1. Numerical sequence patterns (linear, geometric, Fibonacci-type)
        patterns.extend(self._detect_numerical_patterns(data))

        # 2. Algebraic 24-Family Detection
        patterns.extend(self._detect_algebraic_structure(data))

        # 3. Geometric E8 Weyl Projection
        patterns.extend(self._detect_geometric_projection(data))

        # 4. Traditional Symmetry (Refined)
        patterns.extend(self._detect_symmetry_v2(data))

        patterns.sort(key=lambda p: p.confidence, reverse=True)
        return patterns

    def _detect_numerical_patterns(self, data: np.ndarray) -> List[Pattern]:
        """Heuristic detection of common numerical sequence patterns."""
        patterns = []
        n = len(data)
        if n < 3:
            return patterns

        # Linear: constant first differences
        diffs = np.diff(data.astype(float))
        mean_diff = float(np.mean(diffs))
        tol = max(1e-12, abs(mean_diff) * 1e-9)
        if float(np.std(diffs)) <= tol:
            patterns.append(Pattern(
                pattern_type="linear_sequence",
                confidence=0.92,
                description=f"Linear (arithmetic) sequence — constant difference {mean_diff:.6g}",
                metrics={"common_difference": mean_diff, "std_of_differences": float(np.std(diffs))}
            ))
            return patterns

        # Geometric: constant ratios between successive terms
        if np.all(np.abs(data) > 1e-12):
            ratios = (data[1:] / data[:-1]).astype(float)
            mean_ratio = float(np.mean(ratios))
            tol_r = max(1e-12, abs(mean_ratio) * 1e-9)
            if float(np.std(ratios)) <= tol_r:
                patterns.append(Pattern(
                    pattern_type="geometric_sequence",
                    confidence=0.93,
                    description=f"Geometric sequence — common ratio {mean_ratio:.6g}",
                    metrics={"common_ratio": mean_ratio, "std_of_ratios": float(np.std(ratios))}
                ))
                return patterns

        # Fibonacci-type additive recurrence: a[n] = a[n-1] + a[n-2]
        if n >= 4:
            errors = []
            for i in range(2, n):
                expected = float(data[i - 1]) + float(data[i - 2])
                actual = float(data[i])
                denom = max(abs(actual), abs(expected), 1.0)
                errors.append(abs(actual - expected) / denom)
            if max(errors) < 1e-6:
                patterns.append(Pattern(
                    pattern_type="fibonacci_recurrence",
                    confidence=0.95,
                    description="Additive recurrence a[n] = a[n-1] + a[n-2] (Fibonacci-type)",
                    metrics={"max_relative_error": float(max(errors))}
                ))

        return patterns

    def _detect_algebraic_structure(self, data: np.ndarray) -> List[Pattern]:
        """Uses generate_24_families to check for algebraic alignments."""
        patterns = []
        # In v2.0, we treat the input data as a potential locus component
        # if the dimension matches or can be mapped.
        res = detect_g2_family(data, data) # Self-interaction check
        if res["is_g2_candidate"]:
            patterns.append(Pattern(
                pattern_type="G2_invariant_structure",
                confidence=0.9,
                description="Data aligns with G2-invariant bilateral families",
                metrics=res
            ))
        return patterns

    def _detect_geometric_projection(self, data: np.ndarray) -> List[Pattern]:
        """Projects data onto E8 Weyl orbits."""
        patterns = []
        res = map_to_weyl_orbit(data)
        if res["is_on_first_shell"]:
            patterns.append(Pattern(
                pattern_type="E8_weyl_resonance",
                confidence=0.95,
                description=f"Data projects to E8 Weyl Orbit {res['orbit_id']} ({res['classification']})",
                metrics=res
            ))
        return patterns

    def _detect_symmetry_v2(self, data: np.ndarray) -> List[Pattern]:
        """
        Multi-mode symmetry detection suite.

        Checks four symmetry classes plus a wildcard polynomial fallback:

        1. Conjugate (palindromic) symmetry  — data[k] ≈ data[n-1-k]
        2. Anti-symmetry                      — data[k] ≈ -data[n-1-k]
        3. Cyclic / periodic symmetry         — data repeats with period p
        4. Bilateral (functional)             — f(x) ≈ f(1-x)  (RHI-relevant)
        5. Wildcard polynomial fit            — low-degree polynomial describes data
        """
        patterns = []
        d = data.astype(float)
        n = len(d)
        if n < 2:
            return patterns

        norm = float(np.linalg.norm(d)) + 1e-15

        # ── 1. Conjugate (palindromic) symmetry ──────────────────────────────
        flipped = d[::-1]
        diff_conj = float(np.linalg.norm(d - flipped))
        conf_conj = max(0.0, 1.0 - diff_conj / norm)
        if conf_conj > 0.6:
            patterns.append(Pattern(
                pattern_type="conjugate_symmetry",
                confidence=conf_conj,
                description=f"Palindromic (conjugate) symmetry — data[k] ≈ data[n-1-k]  ({conf_conj:.2%})",
                metrics={"l2_diff": diff_conj, "relative_error": diff_conj / norm}
            ))

        # ── 2. Anti-symmetry ─────────────────────────────────────────────────
        diff_anti = float(np.linalg.norm(d + flipped))
        conf_anti = max(0.0, 1.0 - diff_anti / norm)
        if conf_anti > 0.6:
            patterns.append(Pattern(
                pattern_type="anti_symmetry",
                confidence=conf_anti,
                description=f"Anti-symmetry — data[k] ≈ -data[n-1-k]  ({conf_anti:.2%})",
                metrics={"l2_diff": diff_anti, "relative_error": diff_anti / norm}
            ))

        # ── 3. Cyclic / periodic symmetry ────────────────────────────────────
        if n >= 6:
            best_period, best_conf_cyc = None, 0.0
            # Check periods from 2 up to n//2
            for p in range(2, n // 2 + 1):
                if n % p != 0:
                    # Allow non-exact multiples: tile the shortest cycle and compare
                    tile = np.tile(d[:p], n // p + 1)[:n]
                else:
                    tile = np.tile(d[:p], n // p)
                err = float(np.linalg.norm(d - tile))
                c = max(0.0, 1.0 - err / norm)
                if c > best_conf_cyc:
                    best_conf_cyc = c
                    best_period = p
            if best_conf_cyc > 0.7:
                patterns.append(Pattern(
                    pattern_type="cyclic_symmetry",
                    confidence=best_conf_cyc,
                    description=f"Cyclic / periodic symmetry — period {best_period}  ({best_conf_cyc:.2%})",
                    metrics={"period": best_period, "confidence": best_conf_cyc}
                ))

        # ── 4. Bilateral functional symmetry  f(x) ≈ f(1-x) ─────────────────
        # Treats indices as x-values in [0, 1] and checks f(x) ≈ f(1-x).
        # Directly relevant to the RHI critical-line σ ↔ 1-σ symmetry.
        if n >= 4:
            xs = np.linspace(0.0, 1.0, n)
            # f(1-x) is simply the reversed array in this uniform-grid encoding
            diff_bil = float(np.linalg.norm(d - flipped))
            conf_bil = max(0.0, 1.0 - diff_bil / norm)
            if conf_bil > 0.6 and conf_bil != conf_conj:  # skip if identical to conjugate result
                patterns.append(Pattern(
                    pattern_type="bilateral_symmetry",
                    confidence=conf_bil,
                    description=f"Bilateral functional symmetry — f(x) ≈ f(1-x)  ({conf_bil:.2%})  [RHI: σ ↔ 1-σ]",
                    metrics={"l2_diff": diff_bil, "relative_error": diff_bil / norm}
                ))

        # ── 5. Wildcard: low-degree polynomial fit ───────────────────────────
        # Falls back to a degree-1..4 polynomial fit and reports R².
        # Catches monotone, quadratic, cubic trends that aren't arithmetic/geometric.
        xs = np.arange(n, dtype=float)
        best_deg, best_r2 = None, 0.0
        for deg in range(1, min(5, n - 1)):
            coeffs = np.polyfit(xs, d, deg)
            fitted = np.polyval(coeffs, xs)
            ss_res = float(np.sum((d - fitted) ** 2))
            ss_tot = float(np.sum((d - np.mean(d)) ** 2))
            r2 = 1.0 - ss_res / (ss_tot + 1e-15)
            if r2 > best_r2:
                best_r2 = r2
                best_deg = deg
        # Only report if not already captured by sequence detectors and R² is strong
        already_structured = any(
            p.pattern_type in ("linear_sequence", "geometric_sequence", "fibonacci_recurrence")
            for p in patterns
        )
        if not already_structured and best_r2 > 0.97:
            conf_poly = float(np.clip(best_r2, 0.0, 1.0))
            patterns.append(Pattern(
                pattern_type="polynomial_trend",
                confidence=conf_poly,
                description=f"Wildcard: degree-{best_deg} polynomial fit  (R² = {best_r2:.4f})",
                metrics={"degree": best_deg, "r_squared": best_r2}
            ))

        return patterns
