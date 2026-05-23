# CAILculator MCP Server

**High-dimensional mathematical structure analysis for autonomous AI systems**

---

**Applied Pathological Mathematics™** was born from this hypothesis:

> *Higher-dimensional algebras following the Cayley-Dickson sequence—often dismissed as "pathological"—can be interpreted and exploited for computational advantage, specifically for AGI research and the development of structure-preserving embeddings.*

---

## Overview

CAILculator is a Model Context Protocol (MCP) server that empowers AI agents to analyze and compute within high-dimensional algebraic spaces (16D Sedenions to 256D Voudons). It provides a ground-truth mathematical engine for representation learning, sequence detection, and regime analysis, anchored by the **Lean 4 formally verified** Chavez Transform and the Zero Divisor Transmission Protocol (ZDTP).

## Operational Status: Formally Verified (v2.1.1)

The core mathematical foundation of CAILculator is **formally verified** in Lean 4. Every calculation meets a **$10^{-15}$ machine precision** standard, ensuring that structural claims are backed by rigorous proof rather than numerical approximation.

*   **[BilateralCollapse.lean](./lean/BilateralCollapse.lean)**: Proves the bilateral zero divisor identity ($PQ=0 \land QP=0$) used to gate all v2.0+ transmissions.
*   **[ChavezTransform_genuine.lean](./lean/ChavezTransform_genuine.lean)**: Establishes the stability constant $M$, guaranteeing transform outputs never exceed theoretical bounds ($|C[f]| \leq M \cdot \|f\|_1$).
*   **Dual Algebraic Frameworks**: Native support for both non-associative **Cayley-Dickson** and associative **Clifford (Geometric)** algebras.
*   **Formal Audit**: Aristotle-integrated proofs ensure a "zero sorry" implementation for all core analytical operations.

---

## Why "Pathological" Means "Powerful"

Beyond the 8D Octonions, algebras following the Cayley-Dickson construction lose traditional properties like associativity and division algebra structure. These "pathologies" are actually rich features for AI research:

*   **Non-associativity**: Encodes order-dependence and context-sensitivity directly into the algebraic operation.
*   **Zero Divisors**: Create branching structures and bifurcation points in high-dimensional representations.
*   **Structural Invariants**: Reveal hidden symmetries in complex datasets that are invisible to Euclidean or Hilbert-space analysis.

CAILculator makes this "algebraic dark matter" huntable through hypothesis-driven computational enumeration.

---

## Glossary & Terminology

To support rigorous cross-disciplinary collaboration, we maintain a definitive **[Project Glossary](./GLOSSARY.md)**. This document reintroduces and establishes the terminology for high-dimensional algebraic structures (Sedenions, Chingons, Voudons) and their domain projections in journalism and quantitative finance.

---

## System Requirements

### Python Environment
*   **Required:** Python 3.10, 3.11, 3.12, or 3.13 (64-bit).
*   **Incompatible:** Python 3.14+ (pending `numba` support) and all 32-bit versions.

### Supported Operating Systems
*   **Windows 10/11**
*   **macOS 10.15+**
*   **Linux (Ubuntu 20.04+, Debian 10+)**

---

## API Key Acquisition

CAILculator requires a valid API key for tool execution. 

1.  **Visit the Portal**: Access the [CAILculator API Portal](https://cailculator-mcp-production.up.railway.app/) to review subscription tiers (Individual, Academic, Commercial, and Quantitative Finance).
2.  **Request Access**: To obtain a key, please email **[paul@chavezailabs.com](mailto:paul@chavezailabs.com)**. Keys are typically issued within 24 hours.
3.  **Enterprise/Research**: For custom profile development or large-scale research collaborations, please include project details in your request.

---

## Installation & Setup

### 1. Install CAILculator
From your preferred shell, run:
```bash
pip install cailculator-mcp
```
*Note: This will download approximately 100MB of scientific computing dependencies (`numpy`, `scipy`).*

### 2. Configure Your MCP Client

#### Claude Desktop
Add the following to your configuration file (Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "cailculator": {
      "command": "cailculator-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "CAILCULATOR_API_KEY": "your_api_key_here",
        "CAILCULATOR_ENABLE_OFFLINE_FALLBACK": "true"
      }
    }
  }
}
```

#### Gemini CLI / Antigravity CLI (HTTP Mode)
To leverage larger context windows, run the server locally over HTTP:

1. **Install with HTTP support:**
   ```bash
   pip install "cailculator-mcp[http]"
   ```

2. **Start the local server:**
   ```bash
   cailculator-mcp --transport http --port 8080
   ```

3. **Register in `settings.json`:**
   ```json
   {
     "mcpServers": {
       "cailculator": {
         "manifestUrl": "http://localhost:8080/mcp/manifest"
       }
     }
   }
   ```

---

## Specialized Profiles

The **Profile Manager** परियोजनाओं projects universal algebraic patterns into domain-specific intelligence:

*   **Journalism Profile**: Detects structural "Tipping Points" and data inconsistencies for investigative reporting.
*   **Quant Equity Profile**: Benchmarks market regime transitions using Chavez Transform stability measures.
*   **RHI (Riemann Hypothesis Investigation)**: Advanced spectral research mapping prime embeddings ($log p \to ROOT_{16D}$).

---

## Available Tools

### 🔬 High-Precision Research
*   **`chavez_transform`**: Apply the verified integral transform to identify hidden structures in numerical data.
*   **`detect_patterns`**: Multi-stage pipeline identifying linear, geometric, Fibonacci, and complex symmetry patterns.
*   **`verify_bilateral_oracle`**: High-precision check ($10^{-15}$) for zero divisor pairs across both CD and Clifford frameworks.
*   **`map_e8_orbit`**: Project high-dimensional vectors onto verified E8 Weyl orbits.

### 📉 Analysis & Visualization
*   **`zdtp_transmit`**: Transmit 16D data through verified mathematical gateways (S1–S6) to 256D spaces.
*   **`illustrate`**: Generate high-fidelity mathematical visualizations (heatmaps, multi-panel plots) with inline PNG support.
*   **`regime_detection`**: Benchmark HMM statistical baselines against structural transform stability.
*   **`get_version`**: Verify engine status and formal verification metadata.

---

## Technical Specifications & Foundation

*   **Numerical Precision**: $10^{-15}$ (Zero divisor threshold: $|P \times Q| < 10^{-10}$).
*   **Research Citation**: Built on systematic computational enumeration published at Zenodo: [10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495).
*   **Core Library**: Leverages `numpy`, `scipy`, and `hypercomplex` for robust numerical stability.

## Contact & Collaboration

**Research & Engineering:** [paul@chavezailabs.com](mailto:paul@chavezailabs.com)  
**GitHub:** [ChavezAILabs/cailculator-mcp](https://github.com/ChavezAILabs/cailculator-mcp)

---
**Chavez AI Labs**  
*"Better math, less suffering"*
