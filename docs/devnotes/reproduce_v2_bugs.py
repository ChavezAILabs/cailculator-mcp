
import numpy as np
import sys
import os
from typing import Callable
import math

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from cailculator_mcp.core.chavez_transform import ChavezTransform
from cailculator_mcp.core.canonical_six import get_canonical_six, get_pattern_metadata
from cailculator_mcp.zdtp.protocol import get_zdtp_v2
from cailculator_mcp.core.bilateral_collapse import verify_bilateral_collapse

def reproduce_aiex_505():
    print("\n--- Reproducing AIEX-505 (Dispatch Collapse) ---")
    data = [1.0, 2.5, 3.7, 4.2, 5.1, 6.8, 7.3, 8.9]
    alpha = 1.0
    d = 2
    
    ct = ChavezTransform(dimension=32, alpha=alpha)
    six_pairs = get_canonical_six(32)
    
    data_arr = np.array(data)
    def f(x):
        x_scalar = x[0] if x.ndim > 0 and len(x) > 0 else float(x)
        indices = np.linspace(-5, 5, len(data_arr))
        return float(np.sum(data_arr * np.exp(-((x_scalar - indices)**2))))
    
    results = []
    for pid in range(1, 7):
        P_arr, Q_arr = six_pairs[pid]
        res = ct.transform_1d(f, P_arr, Q_arr, d)
        val = res["value"]
        M = res["stability_bound"]["M"]
        results.append((pid, val, M))
        print(f"Pattern {pid}: value={val:.10f}, M={M:.10f}")
        
    unique_vals = len(set(f"{v:.10f}" for _, v, _ in results))
    if unique_vals == 1:
        print("RESULT: Confirmed Dispatch Collapse (Bit-identical values across all 6 patterns)")
    else:
        print(f"RESULT: Dispatch working? Found {unique_vals} unique values.")

def check_zdtp_magnitude_collapse():
    print("\n--- Checking ZDTP Magnitude Collapse ---")
    input_16d = [float(i) for i in range(1, 17)]
    zdtp = get_zdtp_v2()
    
    results = []
    for pid in range(1, 7):
        res = zdtp.transmit(input_16d, pid)
        mag = res["magnitude_256d"]
        results.append((pid, mag))
        print(f"Gateway {pid}: magnitude_256d={mag:.10f}")
        
    unique_mags = len(set(f"{m:.10f}" for _, m in results))
    if unique_mags == 1:
        print("RESULT: Confirmed ZDTP Magnitude Collapse")
    else:
        print(f"RESULT: ZDTP Magnitude varying. Found {unique_mags} unique values.")

def check_indexing_mismatch():
    print("\n--- Checking Indexing Mismatch ---")
    # Pattern 1 metadata: (e_1 + e_14) x (e_3 + e_12) = 0
    meta = get_pattern_metadata(1)
    print(f"Metadata Formula: {meta['formula']}")
    
    # Let's see what P and Q look like in the arrays
    P_arr, Q_arr = get_canonical_six(16)[1]
    p_indices = np.where(P_arr != 0)[0]
    q_indices = np.where(Q_arr != 0)[0]
    
    print(f"P_arr non-zero indices: {p_indices}")
    print(f"Q_arr non-zero indices: {q_indices}")
    
    # verify_bilateral_oracle check
    res = verify_bilateral_collapse(P_arr, Q_arr)
    print(f"Oracle says (P,Q) is bilateral zero divisor: {res['is_bilateral_zero_divisor']}")
    
    # Manual 1-indexed vectors (if user interpreted e_1 as index 0)
    P_0 = np.zeros(16)
    P_0[0] = 1.0; P_0[13] = 1.0
    Q_0 = np.zeros(16)
    Q_0[2] = 1.0; Q_0[11] = 1.0
    
    res_0 = verify_bilateral_collapse(P_0, Q_0)
    print(f"Oracle check for (e_0, e_13) x (e_2, e_11): {res_0['is_bilateral_zero_divisor']}")

if __name__ == "__main__":
    reproduce_aiex_505()
    check_zdtp_magnitude_collapse()
    check_indexing_mismatch()
