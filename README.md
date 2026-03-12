**Applied Pathological Mathematics™** was born from this hypothesis:

*Higher-dimensional algebras following the Cayley-Dickson sequence, which have been wrongly dismissed as "pathological" mathematics, can be interpreted and exploited for computational advantage, with particular benefits for AGI research and development.*

---

# CAILculator MCP Server

**High-dimensional mathematical structure analysis for AI agents**

*"Better math, less suffering"*

## What This Is

A Model Context Protocol server that lets AI agents compute with Cayley-Dickson algebras (sedenions 16D, pathions 32D, up to 256D) and associated Clifford algebras. Built on verified mathematical research into zero divisor patterns and structural properties discovered through systematic computational enumeration. Formally verified with Lean 4 proofs via Harmonic Math's Aristotle.

## Why "Pathological" Might Mean "Powerful"

Beyond quaternions (4D) and octonions (8D), the Cayley-Dickson construction produces algebras with properties that violate conventional mathematical expectations:

- **Non-associativity**: (a × b) × c ≠ a × (b × c)
- **Zero divisors**: Non-zero numbers P, Q where P × Q = 0
- **Loss of division algebra structure**: Not every non-zero element has a multiplicative inverse
- **Dimensional complexity scaling**: Pattern counts grow superlinearly

These properties are called "pathological" because they break the rules of "nice" algebra that works for reals, complex numbers, quaternions, and octonions.

**Pathological, however, doesn't mean useless.**

Zero divisors exhibit patterns and symmetries. Non-associativity encodes order-dependence and context-sensitivity. The vast space of algebraic dark matter in higher-dimensional math becomes huntable through hypothesis-driven computational enumeration: structure over brute force, verification over assumption.

This server based on Applied Pathological Mathematics™ was designed to offer advantages for:
- High-dimensional representation learning
- Pattern detection in complex systems
- Algebraic approaches to neural architecture
- Structure-preserving embeddings
- Time series regime detection

## Mathematical Foundation

### Cayley-Dickson Construction

The Cayley-Dickson construction recursively doubles dimension:
- **R** (reals, 1D) → **C** (complex, 2D) → **H** (quaternions, 4D) → **O** (octonions, 8D)
- **S** (sedenions, 16D) → **P** (pathions, 32D) → 64D → 128D → 256D...

Each doubling loses algebraic properties:
- C: loses ordering
- H: loses commutativity
- O: loses associativity
- S and beyond: gain zero divisors, lose division algebra structure

### Zero Divisors

A **zero divisor** is a pair of non-zero elements P, Q in an algebra where P × Q = 0.

In our research, we focus on two-term zero divisors of the form:
```
(e_a ± e_b) × (e_c ± e_d) = 0
```

where e_i are basis elements and a, b, c, d are distinct indices.

**Verified Pattern Counts:**
- 16D (Sedenions): 84 base patterns, 168 ordered patterns
- 32D (Pathions): 460 base patterns, 920 ordered patterns

These patterns exhibit:
- **Block structure**: 16D blocks replicate with cross-block mixing
- **Conjugation symmetry**: Predictable sign-flip behavior
- **Computational stability**: Numerical verification to machine precision (< 1e-13)

### Research Foundation

Built on systematic computational enumeration published at DOI: [10.5281/zenodo.17402495](https://doi.org/10.5281/zenodo.17402495) - Framework-Independent Zero Divisor Patterns in Higher-Dimensional Cayley-Dickson Algebras: Discovery and Verification of The Canonical Six. Full formal verification in Lean 4 (zero sorry stubs) provides machine-verified mathematical proofs of all core structural claims, including E8 first shell membership and Weyl orbit unification of the Canonical Six P-vectors. Lean 4 verification also covers the Chavez Transform operator itself: convergence (the transform of any bounded, integrable function is finite) and stability (|C[f]| ≤ M · ‖f‖₁, where M depends on the kernel parameters).

Ongoing research will continue further development into 512D.

## System Requirements

### Python Version

- **Required:** Python 3.10, 3.11, 3.12, or 3.13 (64-bit)
- ❌ **NOT SUPPORTED:** Python 3.14+ (numba dependency limitation)
- ❌ **NOT SUPPORTED:** 32-bit Python (scipy/numba require 64-bit)

### Operating Systems

- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, Debian 10+, or equivalent)

## Installation

### Windows Installation

#### Step 1: Install Python (if needed)

1. Download Python 3.13 (64-bit): https://www.python.org/downloads/release/python-3131/
2. Scroll to "Files" section
3. Click "Windows installer (64-bit)" - NOT the 32-bit version
4. Run the installer
5. ✅ **CRITICAL:** Check "Add Python to PATH" during installation
6. Click "Install Now"

#### Step 2: Install CAILculator

Open PowerShell and run:

```powershell
py -3.13 -m pip install cailculator_mcp
```

Installation takes 2-5 minutes (downloads ~100MB of scientific computing dependencies).

#### Step 3: Get Your API Key

Visit the [CAILculator API Portal](https://cailculator-mcp-production.up.railway.app/) to:

- **Subscribe:** Choose from Individual, Academic, Commercial, Enterprise, or Quantitative Finance tiers
- Have a coupon code? Apply during checkout

> **Note:** API keys are delivered via email within 24 hours. For immediate access, email: iknowpi@gmail.com

#### Step 4: Configure Claude Desktop

Open the configuration file:

```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration (replace placeholders with your actual values):

```json
{
  "mcpServers": {
    "cailculator": {
      "command": "C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\cailculator-mcp.exe",
      "args": ["--transport", "stdio"],
      "env": {
        "CAILCULATOR_API_KEY": "cail_your_api_key_here",
        "CAILCULATOR_ENABLE_OFFLINE_FALLBACK": "true"
      }
    }
  }
}
```

**Important Notes:**
- Use double backslashes (`\\`) in Windows paths
- Replace `YOUR_USERNAME` with your actual Windows username
- Replace `cail_your_api_key_here` with your actual API key from the portal

Save and close Notepad.

#### Step 5: Restart Claude Desktop

Completely quit and restart Claude Desktop (not just refresh).

#### Step 6: Verify Installation

1. Open Claude Desktop
2. Look for the 🔌 icon in the bottom-right corner
3. Click it - you should see "cailculator" listed with available tools
4. Test with: "Use CAILculator to multiply two 16D sedenions"

### macOS/Linux Installation

#### Step 1: Verify Python Version

```bash
python3 --version
```

Ensure you have Python 3.10-3.13. If not, install from https://www.python.org/downloads/

#### Step 2: Install CAILculator

```bash
pip3 install cailculator_mcp
```

#### Step 3: Get Your API Key

Visit the [CAILculator API Portal](https://cailculator-mcp-production.up.railway.app/) to obtain your API key.

#### Step 4: Configure Claude Desktop

Edit the configuration file:

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

Add this configuration:

```json
{
  "mcpServers": {
    "cailculator": {
      "command": "/usr/local/bin/cailculator-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "CAILCULATOR_API_KEY": "cail_your_api_key_here",
        "CAILCULATOR_ENABLE_OFFLINE_FALLBACK": "true"
      }
    }
  }
}
```

> **Note:** The command path may vary. Find the correct path with:
> ```bash
> which cailculator-mcp
> ```

Save the file (Ctrl+O, Enter, Ctrl+X in nano).

#### Step 5: Restart Claude Desktop

Completely quit and restart Claude Desktop.

#### Step 6: Verify Installation

Look for the 🔌 icon in Claude Desktop and verify "cailculator" appears in the MCP servers list.

### Gemini CLI Installation (HTTP mode)

For Gemini CLI users who want access to the larger context window:

#### Step 1: Install with HTTP transport support

```bash
pip install cailculator-mcp[http]
```

#### Step 2: Start the HTTP server

```bash
export CAILCULATOR_API_KEY="cail_your_api_key_here"
cailculator-mcp --transport http --port 8080
```

Windows:
```powershell
set CAILCULATOR_API_KEY=cail_your_api_key_here
cailculator-mcp --transport http --port 8080
```

#### Step 3: Configure Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cailculator": {
      "manifestUrl": "http://localhost:8080/mcp/manifest"
    }
  }
}
```

#### HTTP endpoints:

- **GET /mcp/manifest** - Tool definitions
- **POST /message** - MCP JSON-RPC messages
- **GET /health** - Health check

## Troubleshooting

### Windows Issues

**"pip is not recognized as the name of a cmdlet"**

Use the Python launcher instead:
```powershell
py -3.13 -m pip install cailculator_mcp
```

**"Cannot install on Python version 3.14"**

Python 3.14 is not yet supported due to the numba dependency. Install Python 3.13 instead:
1. Uninstall Python 3.14
2. Download Python 3.13 (64-bit) from https://www.python.org/downloads/
3. Reinstall CAILculator

**"Failed to build 'scipy' when getting requirements"**

You likely installed 32-bit Python. CAILculator requires 64-bit Python:
1. Uninstall current Python
2. Download "Windows installer (64-bit)" from https://www.python.org/downloads/
3. Reinstall and verify with: `py -3.13 -c "import platform; print(platform.architecture())"`

Should show: `('64bit', 'WindowsPE')`

**PATH Warnings During Installation**

Warnings like `WARNING: The script cailculator-mcp.exe is installed in '...' which is not on PATH` are safe to ignore. You can still run CAILculator by using the full path in your Claude Desktop configuration.

**"API key validation failed"**
- Verify your API key is correct in `claude_desktop_config.json`
- Ensure `CAILCULATOR_ENABLE_OFFLINE_FALLBACK` is set to `"true"`
- Check that you used double backslashes (`\\`) in Windows paths
- Restart Claude Desktop completely (quit and reopen, not just refresh)
- If issues persist, contact support: paul@chavezailabs.com

**CAILculator Not Showing in MCP Servers**
- Verify the command path in your config file is correct
- Check for syntax errors in your `claude_desktop_config.json` (use a JSON validator)
- Ensure you restarted Claude Desktop completely
- Check Claude Desktop logs for errors

### macOS/Linux Issues

**"command not found: cailculator-mcp"**

The installation path may not be in your PATH. Find it with:
```bash
find / -name cailculator-mcp 2>/dev/null
```
Use the full path in your Claude Desktop configuration.

**Permission Denied**

If you get permission errors during installation:
```bash
pip3 install --user cailculator_mcp
```

Then update the command path in your config to point to `~/.local/bin/cailculator-mcp`.

---

## API Key Tiers

Visit the [CAILculator API Portal](https://cailculator-mcp-production.up.railway.app) for current pricing and tier details:

- **Individual**: For personal projects and research
- **Academic**: Special rates for educational institutions
- **Commercial**: For business applications
- **Enterprise**: Custom solutions with priority support
- **Quantitative Finance**: Specialized tier for financial analysis and trading

---

## Quick Start Examples

Once installed and configured, try these examples in Claude Desktop:

**Basic Multiplication:**
```
Use CAILculator to multiply two 16D sedenions:
P = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Q = [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
```

**Zero Divisor Detection:**
```
Use CAILculator to test if (e1 + e14) × (e3 + e12) is a zero divisor in 128D using both Cayley-Dickson and Clifford frameworks
```

**Data Analysis:**
```
Use CAILculator to analyze this dataset for patterns: [1.2, 2.3, 3.1, 2.9, 4.2, 5.1, 4.8, 6.2]
```

**Market Regime Detection:**
```
Load Bitcoin price data and use CAILculator to detect market regimes
```

## Available Tools

### Core Mathematical Operations

#### `chavez_transform`
Apply proprietary transform that maps data into high-dimensional Cayley-Dickson space for structural analysis.

**Parameters:**
- `data`: Input numerical data
- `dimension`: Target dimension (16, 32, 64, 128, 256)
- `framework`: Algebra framework ("cayley_dickson" or "clifford")

**Returns:** Transformed representation with structural metadata

---

#### `detect_patterns`
Find conjugation symmetries and zero divisor resonances in transformed data.

**Parameters:**
- `transformed_data`: Output from chavez_transform
- `pattern_type`: "conjugation", "zero_divisor", or "all"

**Returns:** Detected patterns with confidence scores

---

#### `compute_high_dimensional`
Direct high-dimensional algebra calculations.

**Parameters:**
- `operation`: "multiply", "add", "conjugate", "norm", "is_zero_divisor"
- `operands`: List of hypercomplex numbers (as coefficient arrays)
- `dimension`: Dimension of algebra (16, 32, 64, 128, 256)

**Returns:** Result of computation

---

#### `analyze_dataset`
End-to-end analysis pipeline combining transform, pattern detection, and interpretation.

**Parameters:**
- `data`: Input dataset
- `dimension`: Analysis dimension
- `analysis_type`: "full", "quick", "custom"

**Returns:** Complete analysis report with detected structures

---

#### `illustrate`
Generate visualizations of algebraic structures and patterns.

**Parameters:**
- `visualization_type`: "zero_divisor_network", "pattern_heatmap", "e8_mandala", "dimension_comparison"
- `data`: Optional data for visualization context

**Returns:** Image or structured visualization data

---

#### `zdtp_transmit`
Zero Divisor Transmission Protocol - transmit 16D data through verified mathematical gateways to 32D and 64D spaces with convergence analysis.

**Parameters:**
- `input_16d`: 16-element coefficient array
- `gateway`: Gateway to use:
  - `"S1"` - Master Gateway: (e₁ + e₁₄) × (e₃ + e₁₂) = 0
  - `"S2"` - Multi-Modal Gateway: (e₃ + e₁₂) × (e₅ + e₁₀) = 0
  - `"S3A"` - Discontinuous Gateway: (e₄ + e₁₁) × (e₆ + e₉) = 0
  - `"S3B"` - Conjugate Pair Gateway: (e₁ - e₁₄) × (e₃ - e₁₂) = 0
  - `"S4"` - Linear Gateway: (e₁ - e₁₄) × (e₅ + e₁₀) = 0
  - `"S5"` - Transformation Gateway: (e₂ - e₁₃) × (e₆ + e₉) = 0
  - `"all"` - Full cascade through all 6 gateways with convergence scoring

**Returns:**
- Dimensional states (16D → 32D → 64D lossless transmission)
- Zero divisor verification status
- Convergence score (for "all"): 0.0-1.0 measuring structural stability
  - **>0.8**: High convergence - robust structure
  - **0.5-0.8**: Moderate - some variance
  - **<0.5**: Low - structural shift detected

**Use Cases:**
- Data integrity verification through mathematical structure
- High-dimensional embedding stability analysis
- Detecting structural shifts in time series data

### Financial Analysis Tools

The server includes specialized tools for time series and financial data analysis:

#### `load_market_data`
Load and validate financial time series data from CSV, Excel, or JSON files.

**Features:**
- Auto-detects OHLCV columns (flexible naming: "Close"/"close"/"CLOSE"/"price")
- Data quality validation and cleaning
- Large file handling (>1GB via chunked reading)
- Date range filtering
- Multi-symbol support

---

#### `market_indicators`
Calculate technical indicators with signal interpretation.

**Available indicators:**
- **Momentum**: RSI, MACD, Stochastic Oscillator
- **Trend**: SMA, EMA, ADX, Ichimoku Cloud
- **Volatility**: Bollinger Bands, ATR
- **Volume**: OBV, VWAP

**Terminology levels:**
- `technical`: Full mathematical notation
- `standard`: Industry terminology
- `simple`: Plain English explanations

---

#### `regime_detection`
Dual-method regime analysis combining statistical and structural approaches.

**Two independent methods:**
1. **Statistical baseline**: Hidden Markov Models (HMM) for momentum-based regime classification
2. **Mathematical structure**: Chavez Transform analysis in 32D sedenion space

**Output includes:**
- Regime classification (bull/bear/sideways) from both methods
- Conjugation symmetry (structural stability measure)
- Zero divisor count (bifurcation risk indicator)
- Agreement score between methods
- Confidence assessment
- Actionable interpretation

**When methods agree:** High confidence in regime classification
**When methods disagree:** Potential regime transition warning

---

#### `batch_analyze_market`
Smart sampling strategy for GB-scale datasets.

**Process:**
1. Sample ~5000 points for quick analysis
2. Calculate confidence score
3. If confidence > 70%, identify suspicious periods
4. Deep dive on flagged periods only

**Analysis types:**
- Regime detection
- Pattern discovery
- Anomaly detection

## For AGI Researchers

If you're working on:
- **High-dimensional embedding spaces**: Explore algebraic structure beyond Euclidean/Hilbert spaces
- **Pattern emergence**: Study how zero divisors create branching structures in representations
- **Neural architecture design**: Investigate non-associative operations for context-dependent computation
- **Time series modeling**: Use structural stability measures alongside statistical methods
- **Representation learning**: Test whether "pathological" algebras offer benefits for certain data types

### Research Collaboration

Interested in applying these tools to AGI research? Contact Paul Chavez at iknowpi@gmail.com for:
- Research access and collaboration
- Custom tool development
- Mathematical consultation
- Data analysis support

## Technical Details

### Numerical Precision
- Zero divisor threshold: |P × Q| < 1e-10
- Typical verified patterns: norm < 1e-13
- Uses Python's `hypercomplex` library for stable computation

### Supported Dimensions
- 16D (Sedenions): 84 base zero divisor patterns
- 32D (Pathions): 460 base patterns
- 64D, 128D, 256D: Pattern catalogs under active research

### Pattern Classes (32D)
1. **Within-block patterns**: Inherited from 16D structure (84 base per block)
2. **Cross-block patterns**: Terms span different 16D blocks (132 base)
3. **Constant-offset patterns**: Same offset k for both terms (126 base)
4. **Variable-offset patterns**: Different offsets k1, k2 (216 base)

## Known Issues

- Large file processing (>10GB) may require manual chunking for optimal memory usage.

## Contact

**Research Collaboration:** paul@chavezailabs.com
**GitHub:** https://github.com/ChavezAILabs/cailculator-mcp
**General Inquiries:** iknowpi@gmail.com

---

**Chavez AI Labs** - *"Better math, less suffering"*
