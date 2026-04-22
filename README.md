**Applied Pathological Mathematics™** was born from this hypothesis:

*Higher-dimensional algebras following the Cayley-Dickson sequence, which have been wrongly dismissed as "pathological" mathematics, can be interpreted and exploited for computational advantage, with particular benefits for AGI research and development.*

---

# CAILculator MCP Server

**High-dimensional mathematical structure analysis for AI agents**

### 🏆 Milestone: Formally Verified (v2.0.3 - April 2026)
The core mathematical foundation of CAILculator is **formally verified** in Lean 4. Unlike libraries that rely solely on numerical approximation, CAILculator's structural claims—including zero divisor patterns and transform stability—are backed by machine-verified proofs located in the `lean/` directory. Every calculation meets a **$10^{-15}$ machine precision** standard.

- **[BilateralCollapse.lean](./lean/BilateralCollapse.lean)**: Formally proves the bilateral zero divisor identity ($PQ=0 \land QP=0$) used to gate all v2.0 transmissions.
- **[ChavezTransform_genuine.lean](./lean/ChavezTransform_genuine.lean)**: Proved stability constant $M$, ensuring transform outputs never exceed rigorous theoretical bounds.
- **Dual Frameworks**: v2.0 natively supports both non-associative **Cayley-Dickson** and associative **Clifford (Geometric)** algebras.
- **Aristotle Integration**: Harmonic Math's Aristotle engine was used to ensure "zero sorry" stubs in all core proofs.

## Overview

A Model Context Protocol server that enables AI agents to compute with Cayley-Dickson algebras (sedenions 16D, pathions 32D, up to 256D) and associated Clifford algebras. 

Built on verified mathematical research into zero divisor patterns and structural properties discovered through systematic computational enumeration. CAILculator integrates formal methods directly into analytical AI pipelines, providing a validation framework grounded in algebraic certainty.

## Structural Capabilities

Beyond quaternions (4D) and octonions (8D), the Cayley-Dickson construction produces algebras with properties that violate conventional mathematical expectations:

- **Non-associativity**: (a × b) × c ≠ a × (b × c)
- **Zero divisors**: Non-zero numbers P, Q where P × Q = 0
- **Loss of division algebra structure**: Not every non-zero element has a multiplicative inverse
- **Dimensional complexity scaling**: Pattern counts grow superlinearly

Zero divisors exhibit specific patterns and symmetries. Non-associativity encodes order-dependence and context-sensitivity. This server enables the search for structure within these higher-dimensional spaces for:
- High-dimensional representation learning
- Pattern detection in complex systems
- Algebraic approaches to neural architecture
- Structure-preserving embeddings
- Time series regime detection

## Specialized Profiles
v2.0 introduces the **Profile Manager**, which projects universal algebraic patterns into domain-specific insights:

*   **Journalism Profile**: Optimized for data reporting and investigation.
    *   **Tipping Points**: Detects sudden structural collapses in budgets, consensus, or policy (Bilateral Zeros).
    *   **Sourcing Confidence**: Measures signal robustness against noisy data (Transform Convergence).
*   **Quant Equity Profile**: Designed for financial analysis and market regime detection.
    *   **Regime Detection**: Bridges HMM statistical baselines with algebraic structural analysis.
    *   **Volatility Anchors**: Identifies bifurcation risks using verified zero-divisor loci.
*   **RHI (Riemann Hypothesis Investigation)**: Spectral research mapping and prime embedding analysis ($log p \to ROOT_{16D}$).

## Mathematical Foundation

### Cayley-Dickson Construction

The Cayley-Dickson construction recursively doubles dimension:
- **R** (reals, 1D) → **C** (complex, 2D) → **H** (quaternions, 4D) → **O** (octonions, 8D)
- **S** (sedenions, 16D) → **P** (pathions, 32D) → 64D → 128D → 256D...

### Zero Divisors

A **zero divisor** is a pair of non-zero elements P, Q in an algebra where P × Q = 0. We focus on two-term zero divisors of the form:
```
(e_a ± e_b) × (e_c ± e_d) = 0
```
where e_i are basis elements and a, b, c, d are distinct indices.

**Verified Pattern Counts:**
- 16D (Sedenions): 84 base patterns, 168 ordered patterns
- 32D (Pathions): 460 base patterns, 920 ordered patterns

### Research Foundation

Built on systematic computational enumeration published at DOI: [10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495). Lean 4 verification covers E8 first shell membership, Weyl orbit unification of the Canonical Six, and Chavez Transform operator convergence and stability ($|C[f]| \leq M \cdot \|f\|_1$).

## System Requirements

- **Python:** 3.10 to 3.13 (64-bit)
- **Architecture:** 64-bit required for high-precision `scipy` and `numpy` operations.
- **OS:** Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)

## Installation

### Windows

```powershell
pip install cailculator_mcp
```

#### Configuration (Claude Desktop)

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "cailculator": {
      "command": "cailculator-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "CAILCULATOR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools (v2.0)

### 🔬 High-Precision Operations
*   **`chavez_transform`**: Apply the formally verified transform to find hidden structure in data.
*   **`detect_patterns`**: Algebraic detection of Tipping Points and Pattern Consistency.
*   **`verify_bilateral_oracle`**: High-precision check ($10^{-15}$) for any zero divisor pair. Supports both **Cayley-Dickson** and **Clifford** frameworks.
*   **`map_e8_orbit`**: Project 16D/32D vectors onto verified E8 Weyl orbits.

### 📰 Domain Intelligence
*   **`list_domain_profiles`**: Explore Journalism, Quant, and RHI tiers.
*   **`zdtp_transmit`**: Zero Divisor Transmission Protocol (ZDTP) - transmit data through verified mathematical gateways (S1–S6) to 32D and 64D spaces.
*   **`illustrate`**: Generate high-precision visualizations of algebraic structures.

### 📈 Financial Analysis
*   **`regime_detection`**: Dual-method market analysis combining HMM and Chavez Transform.
*   **`batch_analyze_market`**: Smart sampling strategy for large-scale datasets.

## Contact & Collaboration

Interested in custom profile development or research access? 
Contact **Chavez AI Labs** at [paul@chavezailabs.com](mailto:paul@chavezailabs.com).

---
**Chavez AI Labs**
