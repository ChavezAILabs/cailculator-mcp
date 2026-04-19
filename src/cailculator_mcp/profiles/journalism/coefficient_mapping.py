"""
Journalism Coefficient Mapping
Domain Projection Layer for CAILculator v2.0

Specialized mappings for investigative reporters focusing on:
1. Politics (Campaign Finance)
2. Public Health (Inspections/Outbreaks)
3. Poverty (Census/Economic Reports)
"""

import numpy as np
from typing import Dict, Any

def map_politics_to_sedenion(row: Dict[str, float], dimension: int = 16) -> np.ndarray:
    """
    Politics: Detects Tipping Points in funding velocity and expenditure.
    Indices: e1=Amount, e2=PAC_Count, e3=Burn_Rate, e4=Debt.
    """
    vec = np.zeros(dimension, dtype=np.float64)
    vec[1] = float(row.get("amount", 0))
    vec[2] = float(row.get("pac_count", 0))
    vec[3] = float(row.get("burn_rate", 0))
    vec[4] = float(row.get("debt", 0))
    return vec

def map_public_health_to_sedenion(row: Dict[str, float], dimension: int = 16) -> np.ndarray:
    """
    Public Health: Identifies anomalous clusters in inspections or outbreaks.
    Indices: e1=Count, e2=Severity, e3=Density, e4=Response_Time.
    """
    vec = np.zeros(dimension, dtype=np.float64)
    vec[1] = float(row.get("count", 0))
    vec[2] = float(row.get("severity", 0))
    vec[3] = float(row.get("density", 0))
    vec[4] = float(row.get("response_time", 0))
    return vec

def map_poverty_to_sedenion(row: Dict[str, float], dimension: int = 16) -> np.ndarray:
    """
    Poverty: Reveals hidden structural inequality patterns.
    Indices: e1=Income, e2=Housing_Cost, e3=Employment, e4=Assistance.
    """
    vec = np.zeros(dimension, dtype=np.float64)
    vec[1] = float(row.get("income", 0))
    vec[2] = float(row.get("housing_cost", 0))
    vec[3] = float(row.get("employment", 0))
    vec[4] = float(row.get("assistance", 0))
    return vec
