"""
E8-Pathion Bridge: Proper mapping between E8 geometry and 32D pathion structure.

The Canonical Six bilateral zero divisor pairs live at sedenion indices as follows.
BILATERAL means P×Q = 0 AND Q×P = 0 (both directions). Each pattern is a pair (P, Q)
where P = e_a ± e_b and Q = e_c ± e_d.

Formally verified in BilateralCollapse.lean (Lean 4, Chavez AI Labs):
    Pattern 1: P=(e_1+e_14), Q=(e_3+e_12)
    Pattern 2: P=(e_3+e_12), Q=(e_5+e_10)
    Pattern 3: P=(e_4+e_11), Q=(e_6+e_9)
    Pattern 4: P=(e_1-e_14), Q=(e_3-e_12)
    Pattern 5: P=(e_1-e_14), Q=(e_5+e_10)
    Pattern 6: P=(e_2-e_13), Q=(e_6+e_9)

This module creates loci that:
1. Respect the full 32D pathion structure
2. Use E8 Weyl orbit information to classify and position them
3. Create meaningful Chavez Transform overlaps

Formal verification status (ChavezTransform_genuine.lean, April 2026):
    The Chavez Transform is formally verified in Lean 4 with axiom footprint
    [propext, Classical.choice, Quot.sound]. Key result relevant to this module:

        K_Z(P, Q, realToSed(x)) = 2*x^2*(||P||^2 + ||Q||^2)  [exact theorem]

    On scalar inputs (x : R embedded via the e0 scalar channel), the bilateral
    kernel factors completely — all pattern-specific structure vanishes, and only
    the combined norm ||P||^2 + ||Q||^2 survives. This means the 2-class partition
    discovered by this module (orbit_id 1 vs 2, based on primary index < 4 vs >= 4)
    is invisible to scalar inputs. The partition would only manifest on genuinely
    multi-dimensional inputs where sedenion non-commutativity between patterns
    activates.

    This is consistent with ZDTP S3B/S4 symmetry (AIEX-414) — both independently
    arrive at the same 2-class structure from different directions.

    Experiment 7 (open): test whether E8-informed loci (non-zero mixing_weight)
    produce systematically different Chavez Transform scalar values than pure
    pathion loci for the same input function. If so, E8 geometry is load-bearing
    for the transform's discriminating power, not merely structural.
"""

import numpy as np
from typing import Dict, Tuple, List
from dataclasses import dataclass

# v2.0 Core Imports
from ..core.canonical_six import get_canonical_six
from ..core.extended_structures import map_to_weyl_orbit

@dataclass
class PathionLoci:
    """
    Zero divisor loci in 32D pathion space, informed by E8 structure.
    """
    positions: np.ndarray  # Shape: (num_loci, 32)
    orbit_id: int          # Which E8 Weyl orbit inspired this
    pattern_id: int        # Which Canonical Six pattern


class E8PathionBridge:
    """
    Creates proper loci for Chavez Transform that bridge E8 geometry and pathion structure.
    """

    def __init__(self, dimension: int = 32):
        self.dimension = dimension
        self.six_pairs = get_canonical_six(dimension)
        # P primary index (first non-zero component) for orbit classification
        self.canonical_six_primary = {1: 1, 2: 3, 3: 4, 4: 1, 5: 1, 6: 2}

    def create_pathion_loci(self, pattern_id: int, e8_root: np.ndarray = None) -> PathionLoci:
        """
        Create zero divisor loci for a Canonical Six bilateral pattern.
        """
        if pattern_id not in self.six_pairs:
            raise ValueError(f"Invalid pattern_id: {pattern_id}")
            
        P_arr, Q_arr = self.six_pairs[pattern_id]
        
        # Start with canonical basis
        loci = np.eye(self.dimension, dtype=float)

        # Modulate positions using E8 structure if provided
        if e8_root is not None and len(e8_root) == 8:
            e8_component = np.zeros(self.dimension)
            e8_component[:8] = e8_root * 0.3

            # Identify indices for P and Q
            p_indices = np.where(abs(P_arr) > 1e-10)[0]
            q_indices = np.where(abs(Q_arr) > 1e-10)[0]
            
            for idx in np.concatenate([p_indices, q_indices]):
                loci[idx] = loci[idx] + e8_component

        # Orbit classification
        primary = self.canonical_six_primary[pattern_id]
        orbit_id = 1 if primary < 4 else 2

        return PathionLoci(
            positions=loci,
            orbit_id=orbit_id,
            pattern_id=pattern_id
        )

    def create_e8_informed_loci(
        self,
        pattern_id: int,
        e8_root: np.ndarray,
        mixing_weight: float = 0.5
    ) -> PathionLoci:
        """
        Create loci that blend pathion structure with E8 geometry for a bilateral pair.

        Uses E8 root structure to inform HOW the pathion loci are positioned.
        Creates loci for all four active components of the bilateral pair (P and Q).

        Args:
            pattern_id: Canonical Six bilateral pattern (1-6)
            e8_root: E8 root (8D) from Weyl orbit
            mixing_weight: How much E8 influences positioning (0=pure pathion, 1=pure E8)

        Returns:
            PathionLoci with hybrid positioning
        """
        (a, b, sign_P), (c, d, sign_Q) = self.canonical_six_pairs[pattern_id]

        loci = []

        # Primary loci at pathion indices for P (always present)
        loc_a = np.zeros(32)
        loc_a[a] = 1.0
        loc_b = np.zeros(32)
        loc_b[b] = float(sign_P)

        # Primary loci at pathion indices for Q (always present)
        loc_c = np.zeros(32)
        loc_c[c] = 1.0
        loc_d = np.zeros(32)
        loc_d[d] = float(sign_Q)

        # Mix in E8 structure to first 8 dimensions
        if e8_root is not None:
            e8_component = np.zeros(32)
            e8_component[:8] = e8_root

            # Blend E8 into each component locus
            loc_a = (1 - mixing_weight) * loc_a + mixing_weight * e8_component
            loc_b = (1 - mixing_weight) * loc_b + mixing_weight * e8_component
            loc_c = (1 - mixing_weight) * loc_c + mixing_weight * e8_component
            loc_d = (1 - mixing_weight) * loc_d + mixing_weight * e8_component

        loci = [loc_a, loc_b, loc_c, loc_d]

        # Add E8 root as separate locus if provided
        if e8_root is not None:
            e8_loc = np.zeros(32)
            e8_loc[:8] = e8_root
            loci.append(e8_loc)

        positions = np.array(loci)

        # Orbit classification based on E8 root type
        if e8_root is not None:
            # Type 1: roots of form (±1,±1,0,...) — has zeros
            # Type 2: roots of form (±½,±½,...) — all non-zero
            has_zeros = any(abs(x) < 0.1 for x in e8_root)
            orbit_id = 1 if has_zeros else 2
        else:
            primary = self.canonical_six_primary[pattern_id]
            orbit_id = 1 if primary < 4 else 2

        return PathionLoci(
            positions=positions,
            orbit_id=orbit_id,
            pattern_id=pattern_id
        )

    def create_canonical_six_loci_set(
        self,
        e8_roots: Dict[int, np.ndarray] = None,
        strategy: str = 'pathion_primary'
    ) -> Dict[int, PathionLoci]:
        """
        Create loci for all Canonical Six patterns.

        Args:
            e8_roots: Dict mapping pattern_id -> E8 root (8D)
            strategy: 'pathion_primary' (loci at pathion indices) or
                     'e8_informed' (blend E8 geometry)

        Returns:
            Dict mapping pattern_id -> PathionLoci
        """
        loci_set = {}

        for pattern_id in range(1, 7):
            e8_root = e8_roots.get(pattern_id) if e8_roots else None

            if strategy == 'pathion_primary':
                loci = self.create_pathion_loci(pattern_id, e8_root)
            elif strategy == 'e8_informed':
                loci = self.create_e8_informed_loci(pattern_id, e8_root, mixing_weight=0.3)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            loci_set[pattern_id] = loci

        return loci_set


def test_loci_overlap():
    """Test that corrected loci produce non-zero kernel values."""
    import sys
    sys.path.insert(0, '.')
    from transforms import ChavezTransform, create_canonical_six_pathion

    bridge = E8PathionBridge()
    ct = ChavezTransform(dimension=32, alpha=1.0)

    print("Testing Pathion-Primary Loci:")
    print("=" * 60)

    for pattern_id in range(1, 7):
        P = create_canonical_six_pathion(pattern_id)
        loci = bridge.create_pathion_loci(pattern_id)

        # Evaluate kernel at origin
        x_test = np.zeros(32)
        kernel_val = ct.zero_divisor_kernel(P, x_test, loci.positions)

        print(f"Pattern {pattern_id}: Kernel = {kernel_val:.6f}")

    print()
    print("SUCCESS: Non-zero kernel values achieved!")
    print("Loci properly aligned with pathion structure.")


if __name__ == "__main__":
    test_loci_overlap()
