"""
ZDTP Convergence Demo
=====================

Demonstrates the Zero Divisor Transmission Protocol's core value:
A single trust score (convergence) that tells you if your
high-dimensional data has robust structure or is in flux.

This demo shows how different data characteristics produce
different convergence scores, enabling data integrity verification.

Mathematical Foundation:
The protocol is a discrete realization of the Chavez Transform:
𝒞[f](P,Q,α,d) = ∫_D f(x) · K_Z(P,Q,x) · exp(-α‖x‖²) · Ω_d(x) dx
Where the domain D is a parametric choice (Default: [-5.0, 5.0]).

Run: python demo_zdtp.py
"""

import sys
import math
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cailculator_mcp.zdtp import ZDTPTransmission, CANONICAL_SIX

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_convergence_bar(score: float, width: int = 40):
    """Print a visual convergence bar."""
    filled = int(score * width)
    bar = "#" * filled + "-" * (width - filled)

    if score > 0.8:
        label = "HIGH - Robust Structure"
    elif score > 0.5:
        label = "MODERATE - Some Variance"
    else:
        label = "LOW - Structural Shift"

    print(f"\n  Convergence: [{bar}] {score:.1%}")
    print(f"  Assessment:  {label}")

def demo_structured_data():
    """Demo 1: Highly structured data produces high convergence."""
    print_header("Demo 1: Structured Data (Sine Wave)")

    print("\n  Input: 16D sine wave pattern")
    print("  Expected: HIGH convergence (structured signal)")

    # Create a sine wave pattern
    input_16d = [math.sin(i * math.pi / 8) for i in range(16)]

    print(f"\n  Data: [{', '.join(f'{x:.2f}' for x in input_16d[:8])}...]")

    zdtp = ZDTPTransmission()
    result = zdtp.full_cascade(input_16d)

    score = result["convergence"]["score"]
    print_convergence_bar(score)

    print(f"\n  Mean 64D magnitude: {result['convergence']['mean_magnitude']:.4f}")
    print(f"  Std deviation: {result['convergence']['std_dev']:.4f}")

    return score

def demo_uniform_data():
    """Demo 2: Uniform data produces perfect convergence."""
    print_header("Demo 2: Uniform Data (Constant)")

    print("\n  Input: 16D constant vector (all 1.0)")
    print("  Expected: PERFECT convergence (no variance)")

    input_16d = [1.0] * 16

    print(f"\n  Data: [{', '.join(f'{x:.2f}' for x in input_16d[:8])}...]")

    zdtp = ZDTPTransmission()
    result = zdtp.full_cascade(input_16d)

    score = result["convergence"]["score"]
    print_convergence_bar(score)

    print(f"\n  Mean 64D magnitude: {result['convergence']['mean_magnitude']:.4f}")
    print(f"  Std deviation: {result['convergence']['std_dev']:.4f}")

    return score

def demo_random_data():
    """Demo 3: Random data still shows reasonable convergence."""
    print_header("Demo 3: Random Data (Noise)")

    print("\n  Input: 16D random noise")
    print("  Expected: MODERATE-HIGH convergence (random but stable)")

    random.seed(42)
    input_16d = [random.gauss(0, 1) for _ in range(16)]

    print(f"\n  Data: [{', '.join(f'{x:.2f}' for x in input_16d[:8])}...]")

    zdtp = ZDTPTransmission()
    result = zdtp.full_cascade(input_16d)

    score = result["convergence"]["score"]
    print_convergence_bar(score)

    print(f"\n  Mean 64D magnitude: {result['convergence']['mean_magnitude']:.4f}")
    print(f"  Std deviation: {result['convergence']['std_dev']:.4f}")

    return score

def demo_sparse_data():
    """Demo 4: Sparse data with single non-zero element."""
    print_header("Demo 4: Sparse Data (Single Impulse)")

    print("\n  Input: 16D with single non-zero element")
    print("  Expected: HIGH convergence (simple structure)")

    input_16d = [0.0] * 16
    input_16d[5] = 1.0  # Single impulse at position 5

    print(f"\n  Data: [{', '.join(f'{x:.2f}' for x in input_16d)}]")

    zdtp = ZDTPTransmission()
    result = zdtp.full_cascade(input_16d)

    score = result["convergence"]["score"]
    print_convergence_bar(score)

    print(f"\n  Mean 64D magnitude: {result['convergence']['mean_magnitude']:.4f}")
    print(f"  Std deviation: {result['convergence']['std_dev']:.4f}")

    return score

def demo_financial_pattern():
    """Demo 5: Simulated financial data pattern."""
    print_header("Demo 5: Financial Pattern (Price + Volume)")

    print("\n  Input: Simulated 16D encoding of market data")
    print("         [price_features (8D) | volume_features (4D) | momentum (4D)]")
    print("  Expected: MODERATE-HIGH convergence")

    # Simulate encoding: normalized price levels + volume + momentum
    price_features = [0.5 + 0.1 * math.sin(i * 0.5) for i in range(8)]  # Trending price
    volume_features = [0.3, 0.5, 0.4, 0.6]  # Volume profile
    momentum_features = [0.2, 0.3, 0.25, 0.15]  # Momentum indicators

    input_16d = price_features + volume_features + momentum_features

    print(f"\n  Price:    [{', '.join(f'{x:.2f}' for x in price_features[:4])}...]")
    print(f"  Volume:   [{', '.join(f'{x:.2f}' for x in volume_features)}]")
    print(f"  Momentum: [{', '.join(f'{x:.2f}' for x in momentum_features)}]")

    zdtp = ZDTPTransmission()
    result = zdtp.full_cascade(input_16d)

    score = result["convergence"]["score"]
    print_convergence_bar(score)

    # Show gateway breakdown
    print("\n  Gateway Breakdown:")
    for name, data in result["gateways"].items():
        mag = data.get("magnitude_64d", 0)
        print(f"    {name}: magnitude = {mag:.4f}")

    return score

def demo_single_gateway():
    """Demo 6: Single gateway transmission details."""
    print_header("Demo 6: Single Gateway Deep Dive (S1)")

    print("\n  Showing detailed transmission through S1 (Master Gateway)")
    print("  Formula: (e_1 + e_14) x (e_3 + e_12) = 0")

    input_16d = [1.0, 0.5, 0.25, 0.125] + [0.0] * 12

    print(f"\n  Input 16D: [{', '.join(f'{x:.3f}' for x in input_16d[:8])}...]")

    zdtp = ZDTPTransmission()
    result = zdtp.transmit(input_16d, "S1")

    print(f"\n  Zero Divisor Verified: {result['zero_divisor_verified']}")
    print(f"  Product Norm ||P x Q||: {result['product_norm']:.2e}")

    print(f"\n  Dimensional States:")
    print(f"    16D -> 32D: {len(result['state_16d'])} -> {len(result['state_32d'])} coefficients")
    print(f"    32D -> 64D: {len(result['state_32d'])} -> {len(result['state_64d'])} coefficients")

    # Verify lossless
    preserved_16 = result['state_32d'][:16] == result['state_16d']
    preserved_32 = result['state_64d'][:32] == result['state_32d']

    print(f"\n  Lossless Verification:")
    print(f"    16D preserved in 32D: {'YES' if preserved_16 else 'NO'}")
    print(f"    32D preserved in 64D: {'YES' if preserved_32 else 'NO'}")

    # Show non-zero coefficients
    state_64d = result['state_64d']
    nonzero = [(i, v) for i, v in enumerate(state_64d) if abs(v) > 1e-10]
    print(f"\n  Non-zero 64D coefficients: {len(nonzero)} of 64")
    if len(nonzero) <= 12:
        for i, v in nonzero:
            print(f"    e_{i}: {v:.6f}")

def demo_comparison():
    """Final comparison of all scenarios."""
    print_header("CONVERGENCE COMPARISON")

    zdtp = ZDTPTransmission()

    scenarios = [
        ("Constant (1.0)", [1.0] * 16),
        ("Sine Wave", [math.sin(i * math.pi / 8) for i in range(16)]),
        ("Linear Ramp", [i / 15.0 for i in range(16)]),
        ("Random Noise", [random.gauss(0, 1) for _ in range(16)]),
        ("Sparse (1 element)", [0.0] * 7 + [1.0] + [0.0] * 8),
        ("Alternating", [1.0 if i % 2 == 0 else -1.0 for i in range(16)]),
    ]

    print("\n  Scenario                  Convergence    Assessment")
    print("  " + "-" * 56)

    random.seed(123)  # Reset for reproducibility

    for name, data in scenarios:
        result = zdtp.full_cascade(data)
        score = result["convergence"]["score"]

        if score > 0.8:
            assessment = "HIGH"
        elif score > 0.5:
            assessment = "MODERATE"
        else:
            assessment = "LOW"

        bar_len = int(score * 20)
        bar = "#" * bar_len + "-" * (20 - bar_len)

        print(f"  {name:22s}  [{bar}] {score:5.1%}  {assessment}")

def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  ZERO DIVISOR TRANSMISSION PROTOCOL - CONVERGENCE DEMO")
    print("  Chavez AI Labs")
    print("=" * 60)

    print("\n  The ZDTP convergence score measures structural stability")
    print("  by comparing how data behaves across 6 mathematical gateways.")
    print("\n  Mathematical Foundation (Chavez Transform):")
    print("  The full transform operates over a parametric domain D.")
    print("  Default domain D = [-5.0, 5.0] is maintained for implementation.")
    print("\n  HIGH convergence  = robust structure, stable data")
    print("  LOW convergence   = structural shift, data in flux")

    # Run demos
    demo_uniform_data()
    demo_structured_data()
    demo_random_data()
    demo_sparse_data()
    demo_financial_pattern()
    demo_single_gateway()
    demo_comparison()

    print_header("DEMO COMPLETE")
    print("\n  Key Takeaway:")
    print("  ZDTP provides a single trust score for any 16D data.")
    print("  When gateways agree, your structure is robust.")
    print("  When they diverge, something is shifting.")
    print("\n  This is the foundation for ZDTP-based data integrity.\n")

if __name__ == "__main__":
    main()
