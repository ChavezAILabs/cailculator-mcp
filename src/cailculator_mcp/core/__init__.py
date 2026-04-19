"""
CAILculator Core - Lean-Verified Ground Truth
"""

from .canonical_six import get_canonical_six, get_pattern_metadata
from .stability import get_stability_constant, verify_bound
from .chavez_transform import ChavezTransform
from .bilateral_collapse import verify_bilateral_collapse
from .extended_structures import generate_24_families, map_to_weyl_orbit, detect_g2_family
from .clifford_element import CliffordElement

__all__ = [
    'get_canonical_six',
    'get_pattern_metadata',
    'get_stability_constant',
    'verify_bound',
    'ChavezTransform',
    'verify_bilateral_collapse',
    'generate_24_families',
    'map_to_weyl_orbit',
    'detect_g2_family',
    'CliffordElement'
]
