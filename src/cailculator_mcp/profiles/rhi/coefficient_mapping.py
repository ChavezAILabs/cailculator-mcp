"""
RHI Coefficient Mapping
Domain Projection Layer for CAILculator v2.0

Verified in RHForcingArgument.lean (Phase 61/63).
"""

import numpy as np
from .prime_embeddings import get_parametric_lift

def map_generic_to_sedenion(data: list) -> np.ndarray:
    """
    Standard fallback: maps first 16 values of data to sedenion.
    """
    v = np.zeros(16)
    n = min(len(data), 16)
    v[:n] = data[:n]
    return v
