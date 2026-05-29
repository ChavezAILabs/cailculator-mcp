# CAILculator MCP Server

**High-dimensional mathematical structure analysis for autonomous AI systems**

---

**Applied Pathological Mathematics™** was born from this hypothesis:

> *Higher-dimensional algebras following the Cayley-Dickson sequence—often dismissed as "pathological"—can be interpreted and exploited for computational advantage, specifically for AGI research and the development of structure-preserving embeddings.*

CAILculator puts that hypothesis to work — a Model Context Protocol (MCP) server that empowers AI agents to analyze and compute within high-dimensional algebraic spaces (16D Sedenions to 256D Voudons), providing a ground-truth mathematical engine for representation learning, sequence detection, and regime analysis, anchored by the **Lean 4 formally verified** Chavez Transform and the Zero Divisor Transmission Protocol (ZDTP).

---

## The Chavez Transform

Just as Joseph Fourier revolutionized mathematical physics by extending transform analysis through complex exponential basis functions — introducing $e^{ix}$ as a transform kernel — the **Chavez Transform** takes the next structural leap. To our knowledge, it is the first integral transform to use zero divisor elements within its kernel.

Rather than treating zero divisors as algebraic anomalies to be avoided, the Chavez Transform harnesses them as structural filters. When raw numerical data passes through the transform, noise collapses symmetrically near zero while underlying high-dimensional structural invariants scale cleanly. This is not a numerical trick — it is a formally verified mathematical property.

---

## The Zero Divisor Transmission Protocol (ZDTP)

ZDTP is the structural transmission layer of CAILculator. It lifts a 16D sedenion state into 256D space, then measures how consistently the data's structure propagates across six independent algebraic pathways.

### Transmission Mechanics

Each of the six Canonical Gateway Pairs is a verified bilateral zero divisor: two sedenion elements $P$ and $Q$ satisfying both $PQ = 0$ and $QP = 0$. Before any transmission begins, the oracle reconfirms this property numerically at $10^{-15}$ precision.

The transmission step is the four-factor interaction sum:

$$\text{interaction} = Px + xQ + Qx + xP$$

where $x$ is the 16D input. Because sedenions are non-associative, all four orderings are algebraically distinct — together they span the full interaction space of the gateway and the input. The result is appended to, not substituted for, the original input. The 16D input occupies the first 16 components of the output state unchanged.

This append-and-expand pattern repeats recursively: 16D → 32D → 64D → 128D → 256D. At each stage the original 16D gateway pair is zero-padded into the current dimension and the interaction is appended. The original 16D state is always recoverable as the first 16 components of any higher-dimensional output.

### Convergence Scoring

A single transmission through one gateway produces a 256D state. The full cascade runs the same 16D input through all six gateways and compares the resulting 256D magnitudes. The convergence score is:

$$\text{score} = 1 - \frac{\text{std}}{\text{mean}} \quad \text{over the six gateway output magnitudes}$$

| Score | Stability | Interpretation |
|-------|-----------|----------------|
| > 0.8 | HIGH | Structure propagates uniformly across all six pathways |
| 0.5–0.8 | MODERATE | Detectable structural variation across gateways |
| < 0.5 | LOW | Structural asymmetry or regime shift in the input data |

When all six gateways produce similar output magnitudes, the data carries stable high-dimensional structure — it propagates the same way regardless of which algebraic channel carries it. When magnitudes diverge, the data aligns with some gateways and not others, indicating a structural feature that is directionally asymmetric in the sedenion space.

### Formal Verification Basis

The six gateway coordinates are formally proved bilateral zero divisors in Lean 4 (`BilateralCollapse.lean`). That proof was computed once, offline. The verified coordinates are hardcoded as constants in the engine with the Lean file as their attribution source. At runtime, the oracle independently reconfirms the bilateral property numerically before each transmission — not as a Lean call, but as a $10^{-15}$-precision arithmetic gate.

The `scalar_channel` theorem additionally proves that any linear combination of a gateway pair always produces a scalar result under multiplication — structure collapses cleanly, never generating spurious imaginary components.

The Lean proof is the mathematical guarantee that these six pairs are valid gateways; the runtime oracle is the numerical lock that enforces it.

---

## Formal Verification

The core mathematical foundation of CAILculator is **formally verified** in Lean 4. Every calculation meets a **$10^{-15}$ machine precision** standard, ensuring rigorous proof backs every structural claim rather than numerical approximation.

- **[BilateralCollapse.lean](./lean/BilateralCollapse.lean)**: Proves the bilateral zero divisor identity ($PQ=0 \land QP=0$) used to gate all v2.0+ transmissions.
- **[ChavezTransform_genuine.lean](./lean/ChavezTransform_genuine.lean)**: Establishes the stability constant $M$, guaranteeing transform outputs never exceed theoretical bounds ($|C[f]| \leq M \cdot \|f\|_1$).
- **Dual Algebraic Frameworks**: Native support for both non-associative **Cayley-Dickson** and associative **Clifford (Geometric)** algebras.
- **Zero Sorry**: Aristotle (Harmonic Math's independent Lean 4 verification engine) independently verifies all proofs with zero `sorry` stubs — meaning no unproven axiom placeholders anywhere in the proof chain.

---

## Why "Pathological" Means "Powerful"

Beyond the 8D Octonions, algebras following the Cayley-Dickson construction lose traditional properties like associativity and division algebra structure. These "pathologies" are actually rich features for AI research:

- **Non-associativity**: Encodes order-dependence and context-sensitivity directly into the algebraic operation.
- **Zero Divisors**: Create branching structures and bifurcation points in high-dimensional representations.
- **Structural Invariants**: Reveal hidden symmetries in complex datasets that are invisible to Euclidean or Hilbert-space analysis.

CAILculator makes this "algebraic dark matter" huntable through hypothesis-driven computational enumeration.

---

## System Requirements

### Python Environment
- **Required:** Python 3.10, 3.11, 3.12, or 3.13 (64-bit).
- **Incompatible:** Python 3.14+ (pending `numba` support) and all 32-bit versions.

### Supported Operating Systems
- **Windows 10/11**
- **macOS 10.15+**
- **Linux (Ubuntu 20.04+, Debian 10+)**

---

## API Key Acquisition

CAILculator requires a valid API key for tool execution.

1. **Visit the Portal**: Access the [CAILculator API Portal](https://cailculator-mcp-production.up.railway.app/) to review subscription tiers (Individual, Journalist, Academic, Commercial, and Quantitative Finance).
2. **Request Access**: Email **[paul@chavezailabs.com](mailto:paul@chavezailabs.com)**. Keys are typically issued within 24 hours.
3. **Enterprise/Research**: For custom profile development or large-scale research collaborations, include project details in your request.

---

## Installation & Setup

### 1. Install CAILculator
```bash
pip install cailculator-mcp
```
*This will download several hundred MB of scientific computing dependencies (`numpy`, `scipy`, `numba`).*

### 2. Configure Your MCP Client

#### Claude Desktop
Add the following to your configuration file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

#### Any HTTP-mode MCP Client (including Gemini CLI)
To leverage larger context windows, run the server locally over HTTP:

1. **Install with HTTP support:**
   ```bash
   pip install "cailculator-mcp[http]"
   ```

2. **Start the local server:**
   ```bash
   cailculator-mcp --transport http --port 8080
   ```

3. **Register in your client's settings:**
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

The **Profile Manager** projects universal algebraic patterns into domain-specific intelligence:

- **Journalism Profile**: Detects structural "Tipping Points" and data inconsistencies for investigative reporting.
- **Quant Equity Profile**: Benchmarks market regime transitions using Chavez Transform stability measures.
- **RHI (Riemann Hypothesis Investigation)**: Advanced spectral research mapping prime embeddings ($\log p \to ROOT_{16D}$).

---

## Available Tools

### High-Precision Research
- **`chavez_transform`**: Apply the verified integral transform to identify hidden structures in numerical data.
- **`detect_patterns`**: Multi-stage pipeline identifying linear, geometric, Fibonacci, and complex symmetry patterns.
- **`verify_bilateral_oracle`**: High-precision check ($10^{-15}$) for zero divisor pairs across both Cayley-Dickson and Clifford frameworks.
- **`map_e8_orbit`**: Project high-dimensional vectors onto verified E8 Weyl orbits.
- **`compute_high_dimensional`**: Direct sedenion algebra operations (multiply, add, conjugate, norm, zero divisor classification) extended into 32D–256D spaces.

### Analysis & Visualization
- **`zdtp_transmit`**: Transmit 16D data through six verified mathematical gateways (S1, S2, S3A, S3B, S4, S5) into 256D spaces.
- **`illustrate`**: Generate mathematical visualizations (bar charts, heatmaps, multi-panel plots) saved as high-fidelity PNG files.
- **`regime_detection`**: Dual-method regime classification: HMM statistical baseline benchmarked against Chavez Transform structural analysis.
- **`get_version`**: Verify engine status and formal verification metadata.

### Financial Analysis
- **`analyze_dataset`**: Full structural analysis pipeline — pattern detection, regime classification, and Chavez Transform scoring in a single call.
- **`load_market_data`**: Ingest OHLCV market data for structural analysis; auto-detects column names and handles chunked files over 1GB.
- **`market_indicators`**: Compute standard technical indicators (RSI, MACD, Bollinger Bands) alongside sedenion structural metrics.
- **`batch_analyze_market`**: Run structural analysis across multiple instruments or time windows simultaneously, using smart sampling (~5,000 points) for GB-scale datasets with automatic deep-dives on flagged periods.

---

## Technical Specifications

- **General Precision**: $10^{-15}$ floating-point standard applied across all computations.
- **Zero Divisor Detection Gate**: $|P \times Q| < 10^{-10}$ — a separate threshold governing whether a candidate pair qualifies as a bilateral zero divisor. These two numbers measure different things: the first is the engine's general numerical precision; the second is the algebraic classification boundary for zero divisor pairs.
- **Research Citation**: Grounded in systematic computational enumeration published at Zenodo: [10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495).
- **Core Libraries**: `numpy` and `scipy`.

---

## Glossary & Terminology

To support rigorous cross-disciplinary collaboration, we maintain a definitive **[Project Glossary](./GLOSSARY.md)** establishing terminology for high-dimensional algebraic structures (Sedenions, Chingons, Voudons) and their domain projections in journalism and quantitative finance.

---

## Contact & Collaboration

**Research & Engineering:** [paul@chavezailabs.com](mailto:paul@chavezailabs.com)  
**GitHub:** [ChavezAILabs/cailculator-mcp](https://github.com/ChavezAILabs/cailculator-mcp)

---

**Chavez AI Labs**  
*"Better math, less suffering"*
