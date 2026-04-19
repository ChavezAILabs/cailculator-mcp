"""
Quant Equity Coefficient Mapping
Domain Projection Layer for CAILculator v2.0

Systematic mapping of financial data fields to hypercomplex component channels.
Strictly maps domain fields (OHLCV) to non-real sedenion components (e1-e15).
"""

import numpy as np
from typing import Dict, List

# OHLCV+V Mapping Schema (e1-e6)
# Verified in v2.0 Architecture Audit
MAPPING_SCHEMA = {
    "open": 1,
    "high": 2,
    "low": 3,
    "close": 4,
    "volume": 5,
    "volatility": 6
}

def map_ohlcv_to_sedenion(ohlcv_row: Dict[str, float], dimension: int = 16) -> np.ndarray:
    """
    Maps a single row of market data to a sedenion/pathion vector.
    
    Adheres to Prerequisite Option A: Avoids e0 (scalar channel) to enable
    proper pattern differentiation across the Canonical Six.
    """
    vec = np.zeros(dimension, dtype=np.float64)
    
    for field, idx in MAPPING_SCHEMA.items():
        if field in ohlcv_row and idx < dimension:
            vec[idx] = float(ohlcv_row[field])
            
    return vec

def get_field_from_index(index: int) -> str:
    """Reverse lookup: returns domain field for a given component index."""
    for field, idx in MAPPING_SCHEMA.items():
        if idx == index:
            return field
    return f"e{index}"
