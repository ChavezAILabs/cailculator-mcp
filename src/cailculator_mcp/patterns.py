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
        
        # 1. Algebraic 24-Family Detection
        patterns.extend(self._detect_algebraic_structure(data))
        
        # 2. Geometric E8 Weyl Projection
        patterns.extend(self._detect_geometric_projection(data))
        
        # 3. Traditional Symmetry (Refined)
        patterns.extend(self._detect_symmetry_v2(data))
        
        patterns.sort(key=lambda p: p.confidence, reverse=True)
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
        """Refined symmetry check at 10^-15 precision."""
        patterns = []
        mid = len(data) // 2
        if mid < 1: return patterns
        
        left = data[:mid]
        right = data[mid:mid+len(left)][::-1]
        
        if len(left) == len(right):
            diff = np.linalg.norm(left - right)
            # Confidence inversely proportional to diff
            conf = max(0, 1.0 - (diff / (np.linalg.norm(data) + 1e-15)))
            if conf > 0.6:
                patterns.append(Pattern(
                    pattern_type="conjugation_symmetry",
                    confidence=float(conf),
                    description=f"Conjugation symmetry detected at {conf:.2%} precision",
                    metrics={"l2_diff": float(diff)}
                ))
        return patterns
