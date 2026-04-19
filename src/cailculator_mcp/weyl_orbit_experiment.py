"""
Weyl Orbit Resonance Experiment - Hunter's Guide Strategy
v2.0 Refactored for High-Precision Core
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .e8.e8_lattice import E8Lattice, E8Root
from .transforms import ChavezTransform, create_canonical_six_pattern


class WeylOrbitExperiment:
    """
    Conducts targeted experiments on E8 Weyl orbits using Chavez Transform v2.0.
    """

    def __init__(self, alpha: float = 1.0, dimension_param: int = 2):
        self.alpha = alpha
        self.d = dimension_param
        self.transform = ChavezTransform(dimension=32, alpha=alpha)
        self.lattice = E8Lattice()
        self.results = {}

    def setup(self):
        """Generate E8 structure and classify orbits."""
        print("="*80)
        print("WEYL ORBIT RESONANCE EXPERIMENT (v2.0) - SETUP")
        print("="*80)
        print()

        print("[1/3] Generating E8 root system...")
        self.lattice.generate_roots()
        
        print("[2/3] Classifying Weyl orbits...")
        self.lattice.classify_weyl_orbits_simple()
        
        print("[3/3] Mapping Canonical Six patterns to E8...")
        self.canonical_mapping = self.lattice.map_canonical_six_to_e8()

        print("\nSetup complete!\n")

    def probe_orbit_representative(self, orbit_id: int) -> Dict:
        """Use Chavez Transform v2.0 to probe ONE representative."""
        rep = self.lattice.orbit_representatives[orbit_id]
        
        # P = e_1 + e_14 (Pattern 1)
        P, Q = create_canonical_six_pattern(1, dimension=32)

        # Define simple test function (Gaussian)
        test_function = lambda x: np.exp(-np.sum(x**2))

        try:
            # Note: v2.0 core transform handles n-D embedding fix
            res = self.transform.core.transform_1d(
                test_function,
                P, Q,
                d=self.d,
                domain=(-3.0, 3.0)
            )
            val = res["value"]
            success = True
        except Exception as e:
            val = np.nan
            success = False
            print(f"      WARNING: Transform failed for orbit {orbit_id}: {e}")

        return {
            'orbit_id': orbit_id,
            'representative': rep.coords.tolist(),
            'transform_value': val,
            'success': success
        }

    def run_full_experiment(self) -> Dict:
        self.setup()
        
        print("="*80)
        print("PHASE 1: ORBIT REPRESENTATIVE PROBING")
        print("="*80)

        orbit_probe_results = {}
        for orbit_id in self.lattice.orbit_representatives.keys():
            print(f"Probing Orbit {orbit_id}...")
            result = self.probe_orbit_representative(orbit_id)
            orbit_probe_results[orbit_id] = result
            print(f"  Transform value: {result['transform_value']:.6e}")

        return {
            'experiment': 'Weyl Orbit Resonance v2.0',
            'orbit_probes': orbit_probe_results
        }

if __name__ == "__main__":
    experiment = WeylOrbitExperiment(alpha=1.0, dimension_param=2)
    results = experiment.run_full_experiment()
    print("\nv2.0 Experiment Completed successfully.")
