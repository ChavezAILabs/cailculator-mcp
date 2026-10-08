# CAILculator MCP Server

**High-dimensional mathematical structure analysis for autonomous AI systems**

---

**Applied Pathological Mathematics™** was born from this hypothesis:

> *Higher-dimensional algebras following the Cayley-Dickson sequence—often dismissed as "pathological"—can be interpreted and exploited for computational advantage, specifically for AGI research and the development of structure-preserving embeddings.*

CAILculator puts that hypothesis to work — a Model Context Protocol (MCP) server that empowers AI agents to analyze and compute within high-dimensional algebraic spaces (16D sedenions to 256D), providing a ground-truth mathematical engine for representation learning, sequence detection, and regime analysis, anchored by the **Lean 4 formally verified** Chavez Transform and the Zero Divisor Transmission Protocol (ZDTP).

---

## Formal Verification

The core mathematical foundation of CAILculator is **formally verified** in Lean 4. Every calculation meets a **$10^{-15}$ machine precision** standard, ensuring rigorous proof backs every structural claim rather than numerical approximation.

- **[BilateralCollapse.lean](./lean/BilateralCollapse.lean)**: Proves the bilateral zero divisor identity ($PQ=0 \land QP=0$) used to gate all v2.0+ transmissions.
- **[ChavezTransform_genuine.lean](./lean/ChavezTransform_genuine.lean)**: Establishes the stability constant $M$, guaranteeing transform outputs never exceed theoretical bounds ($|C[f]| \leq M \cdot \|f\|_1$).
- **[e8_weyl_orbit_unification.lean](./lean/e8_weyl_orbit_unification.lean)**: An exploratory result connecting the Canonical Six to E8 lattice structure — the Lean 4 proof establishes that the six gateway P-vectors lie on the E8 first shell (norm² = 2) and fall within a single Weyl orbit, including an antipodal pair related by Weyl reflection. This is the most preliminary of CAILculator's formal components and an active area of work; the associated tooling (`map_e8_orbit`) is correspondingly experimental.
---

## The Chavez Transform

Just as Joseph Fourier revolutionized mathematical physics by extending transform analysis through complex exponential basis functions — introducing $e^{ix}$ as a transform kernel — the **Chavez Transform** takes the next structural leap. To our knowledge, it is the first integral transform to use zero divisor elements within its kernel.

**What the shipped tools compute (2.2.0).** The 1D transform behind the `chavez_transform` tool and `analyze_dataset` has an exact closed form. The series is embedded on a single basis element, so the kernel is the same for every gateway pair of the shipped shape, zero divisor or not, and the output is a fixed, center-weighted sum of the series: $T = \sum_i \text{data}_i \cdot w_i$, with weights that depend only on the series length, $\alpha$ and $d$. The formally verified property is the stability bound $|C[f]| \leq M \cdot \|f\|_1$. No noise-filtering or structure-detecting property has been verified or validated, and the 1D value carries no zero-divisor information. Both values are reported as experimental measurements. The n-dimensional transform, where zero divisors can annihilate part of the kernel, is not exposed by any tool and has not been tested. Details: [docs/chavez_transform.md](./docs/chavez_transform.md).

---

## The Zero Divisor Transmission Protocol (ZDTP)

ZDTP lifts a 16D sedenion state into 256D space through each of the six Canonical gateways and compares the resulting magnitudes. The six gateways have three independent K_Z kernel components — S3A and S3B share a Fano intersection origin, as do S4 and S5 — but all six are run independently in transmission, and the convergence score reflects the full spread of their output magnitudes.

> **Closed form (2.2.0).** The outputs reduce exactly to $\text{magnitude}_{256D}(k) = \sqrt{\|x\|^2 + 64x_0^2 + 16s_k^2}$, where $s_k$ is a signed sum of four input components, and the convergence score is a function of those six numbers. The zero-divisor property of the gateways does not enter the result: pairs of the same shape that are not zero divisors give the same values. ZDTP outputs are reported as experimental measurements, not structural findings. Derivation and checks: [docs/ZDTP_CLOSED_FORM.md](./docs/ZDTP_CLOSED_FORM.md).

### Transmission Mechanics

Each of the six Canonical Gateway Pairs is a verified bilateral zero divisor in the Cayley-Dickson algebra: two sedenion elements $P$ and $Q$ satisfying both $PQ = 0$ and $QP = 0$. S2 additionally holds bilateral status across both Cayley-Dickson and Clifford frameworks at 16D–256D — the only gateway to do so. Before any transmission begins, the oracle reconfirms this property numerically at $10^{-15}$ precision.

The transmission step is the four-factor interaction sum:

$$\text{interaction} = Px + xQ + Qx + xP$$

where $x$ is the 16D input. Because Cayley-Dickson algebras are quadratic ($uv + vu = -2\langle u, v\rangle$ for pure imaginary $u, v$), this sum simplifies to $2x_0(P+Q) - 2\langle P+Q, x\rangle e_0$: only the input's real part and one signed four-term sum survive. The result is appended to, not substituted for, the original input. The 16D input occupies the first 16 components of the output state unchanged.

This append-and-expand pattern repeats recursively: 16D → 32D → 64D → 128D → 256D. At each stage the original 16D gateway pair is zero-padded into the current dimension and the interaction is appended (the upper-half interaction term is identically zero). The original 16D state is always recoverable as the first 16 components of any higher-dimensional output.

### Convergence Scoring

A single transmission through one gateway produces a 256D state. The full cascade runs the same 16D input through all six gateways and compares the resulting 256D magnitudes. The convergence score is:

$$\text{score} = 1 - \frac{\text{std}}{\text{mean}} \quad \text{over the six gateway output magnitudes}$$

| Score | Stability | Interpretation |
|-------|-----------|----------------|
| > 0.8 | HIGH | Structure propagates uniformly across all six pathways |
| 0.5–0.8 | MODERATE | Detectable structural variation across gateways |
| < 0.5 | LOW | Structural asymmetry or regime shift in the input data |

> **Since 2.2.0 the tools no longer report these levels as verdicts.** `stability_level`
> and `regime.classification` are `"not_assessed"`. On 200 seeded null series the score
> fell in 0.54–0.65, the same range as every structured series tested (including a 50%
> step break), so the bands above did not separate structure from noise. The score itself
> is still reported. See `docs/EVALUATION_CONTRACT.md`.

By the closed form, the six magnitudes differ only through the six signed four-term sums $s_k$. Similar magnitudes mean those sums are similar in size; different magnitudes mean they are not. That is a statement about four-component sums of the input, not about structure in the data.

### Formal Verification Basis

The six gateway coordinates are formally proved bilateral zero divisors in Lean 4 (`BilateralCollapse.lean`). That proof was computed once, offline. The verified coordinates are hardcoded as constants in the engine with the Lean file as their attribution source. At runtime, the oracle independently reconfirms the bilateral property numerically before each transmission — not as a Lean call, but as a $10^{-15}$-precision arithmetic gate.

The `scalar_channel` theorem additionally proves that any linear combination of a gateway pair always produces a scalar result under multiplication — structure collapses cleanly, never generating spurious imaginary components.

The Lean proof is the mathematical guarantee that these six pairs are valid gateways; the runtime oracle is the numerical lock that enforces it.

---

## Why "Pathological" Means "Powerful"

Beyond the 8D Octonions, algebras following the Cayley-Dickson construction lose traditional properties like associativity and division algebra structure. These "pathologies" are actually rich features for AI research:

- **Non-associativity**: Encodes order-dependence and context-sensitivity directly into the algebraic operation.
- **Zero Divisors**: Create branching structures and bifurcation points in high-dimensional representations.
- **Structural Invariants**: Reveal hidden symmetries in complex datasets that are invisible to Euclidean or Hilbert-space analysis.

CAILculator makes this "algebraic dark matter" huntable through hypothesis-driven computational enumeration.

---

## Deep-Dive Documentation

Extended theoretical frameworks and protocol specifications for researchers:

- **[Chavez Transform Explainer](./docs/chavez_transform.md)**: The historical context, zero divisor kernel, the 1D closed form, stability bound, scalar channel theorem, formal verification chain, and research applications across RHI, finance, and journalism.
- **[ZDTP Protocol Specification](./docs/zdtp_protocol.md)**: The Zero Divisor Transmission Protocol in full — Cayley-Dickson tower mechanics, four-factor interaction, recursive 16D→256D expansion, convergence scoring, and the Lean-to-runtime verification pipeline. Read with **[ZDTP_CLOSED_FORM.md](./docs/ZDTP_CLOSED_FORM.md)**, which derives what the outputs reduce to.
- **[Project Glossary](./GLOSSARY.md)**: Definitive terminology for high-dimensional algebraic structures (sedenions, pathions, and higher-dimensional algebras) and their domain projections in journalism and quantitative finance.

---

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

- **Journalism Profile**: Reports measured structural quantities for public-records data. Since 3.0.0 it gives no verdicts (`measured_only`).
- **Quant Equity Profile**: Reports measured structural quantities and standard technical indicators for OHLCV price data. Since 2.2.0 the regime verdict is withheld (`not_assessed`).

The RHI (Riemann Hypothesis Investigation) profile was removed in 2.2.0. The RH research
described in the docs continues, using the general tools.

---

## Available Tools

CAILculator computes natively across two fundamentally different algebraic frameworks — non-associative **Cayley-Dickson** and associative **Clifford (Geometric)** — at dimensions from 16D to 256D. This is a rare capability: most mathematical software commits to one framework. CAILculator runs the same structural computation in both and surfaces where they disagree — which is how S2 stands out as the only Canonical Six gateway bilateral in both frameworks, a distinction invisible from inside either one alone. With `verify_bilateral_oracle`'s `framework` argument you can reproduce this directly.

### High-Precision Research
- **`chavez_transform`** *(experimental)*: 1D Chavez Transform of a series. Returns a fixed center-weighted sum of the series (closed form above) and the verified stability bound. Not a structure detector.
- **`detect_patterns`**: Multi-stage pipeline identifying linear, geometric, Fibonacci, and complex symmetry patterns.
- **`verify_bilateral_oracle`**: Exact bilateral zero-divisor check ($PQ = 0 \land QP = 0$) at $10^{-15}$ precision, runnable in either the non-associative **Cayley-Dickson** or associative **Clifford** framework via the `framework` argument. Running both and comparing is the point: S2 is the only Canonical Six gateway bilateral in both, while the others (e.g. S1) collapse in Cayley-Dickson but stay one-sided in Clifford ($\|QP\| = 2\sqrt{2}$). The divergence is the structural signal. Returns the residual $\|PQ\|$ and $\|QP\|$ norms.
- **`map_e8_orbit`** *(experimental)*: Projects a vector onto E8 first-shell Weyl orbits. Currently maps the first 8 coordinates (the octonion half) only — 16D inputs with support in e₈–e₁₅ have that half dropped, so a full-16D vector can report as off-shell. Under active development.
- **`compute_high_dimensional`**: Direct sedenion algebra operations (multiply, add, conjugate, norm, zero divisor classification) extended into 32D–256D spaces.

### Analysis & Visualization
- **`analyze_dataset`**: Pattern detection, the 1D Chavez value and the ZDTP full cascade in a single call. Returns top patterns, the convergence score and per-gateway magnitudes; the Chavez and ZDTP values are experimental measurements with closed forms (above). The regime classification is withheld (`not_assessed`) until a detector passes a validation gate. Accepts a close-price list or OHLCV dict. Minimum 16 data points.
- **`zdtp_transmit`** *(experimental)*: Lifts a 16D input through one or all six Canonical gateways (S1, S2, S3A, S3B, S4, S5) to 256D. Outputs have the closed form above.
- **`illustrate`**: Generate mathematical visualizations (bar charts, heatmaps, multi-panel plots) saved as high-fidelity PNG files.
- **`get_version`**: Verify engine status and formal verification metadata.

> **Additional financial tools** (`regime_detection`, `load_market_data`, `batch_analyze_market`) are implemented as standalone modules and will be wired into a future release.

---

## Technical Specifications

- **General Precision**: $10^{-15}$ floating-point standard applied across all computations.
- **Zero Divisor Detection Gate**: $|P \times Q| < 10^{-10}$ — a separate threshold governing whether a candidate pair qualifies as a bilateral zero divisor. These two numbers measure different things: the first is the engine's general numerical precision; the second is the algebraic classification boundary for zero divisor pairs.
- **Research Citation**: Grounded in systematic computational enumeration published at Zenodo: [10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495).
- **Core Libraries**: `numpy` and `scipy`.

---

## Glossary & Terminology

To support rigorous cross-disciplinary collaboration, we maintain a definitive **[Project Glossary](./GLOSSARY.md)** establishing terminology for high-dimensional algebraic structures (sedenions, pathions, and higher-dimensional algebras) and their domain projections in journalism and quantitative finance.

---

## Contact & Collaboration

**Research & Engineering:** [paul@chavezailabs.com](mailto:paul@chavezailabs.com)  
**GitHub:** [ChavezAILabs/cailculator-mcp](https://github.com/ChavezAILabs/cailculator-mcp)

---

**Chavez AI Labs**  
*"Better math, less suffering"*
