"""
General Data Coefficient Mapping
Domain Projection Layer for CAILculator v2.0

Maps generic data fields to hypercomplex component channels.
Supports dynamic column-to-index mapping for CSV/JSON inputs.
"""

import numpy as np
from typing import Dict, List, Optional

def map_generic_to_sedenion(data_row: Dict[str, float], 
                           column_mapping: Optional[Dict[str, int]] = None,
                           dimension: int = 32) -> np.ndarray:
    """
    Maps a generic dictionary or row to a hypercomplex vector.
    
    If column_mapping is provided:
        Uses {column_name: sedenion_index}
    Else:
        Maps first N fields found in row to e1, e2, ... (skipping e0).
    """
    vec = np.zeros(dimension, dtype=np.float64)
    
    if column_mapping:
        for col, idx in column_mapping.items():
            if col in data_row and idx < dimension:
                vec[idx] = float(data_row[col])
    else:
        # Default auto-mapping (skip e0)
        for i, (key, val) in enumerate(data_row.items()):
            idx = i + 1
            if idx < dimension:
                vec[idx] = float(val)
            else:
                break
                
    return vec
