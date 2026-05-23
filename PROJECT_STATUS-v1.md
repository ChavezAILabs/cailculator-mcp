# PROJECT STATUS

This file provides guidance to any AI platform when working with code in this repository.

## Commands

### Development environment
The project ships two virtual environments: `venv/` (general) and `mcp_env/` (MCP-specific). Activate whichever is current before running commands:
```powershell
# Windows
.\venv\Scripts\Activate.ps1
# or
.\mcp_env\Scripts\Activate.ps1
```

**Note:** pytest is installed in the system Python (`C:\Python313`), not in either venv. Run tests without activating a venv, or install pytest into the active venv with `pip install pytest`.

### Install (editable + dev extras)
```bash
pip install -e ".[dev]"
```

### Run the MCP server
```bash
# stdio mode (Claude Desktop)
python -m cailculator_mcp.server --transport stdio

# HTTP mode (Gemini CLI)
python -m cailculator_mcp.server --transport http --port 8080
```

The entry-point script is also available after install:
```bash
cailculator-mcp --transport stdio
```

### Tests
```bash
python -m pytest tests/
# Single test file
python -m pytest tests/test_v2_integration.py -v
# Single test
python -m pytest tests/test_v2_integration.py::test_stability_bound_holds_across_alpha_regime -v
```

### Lint / format
```bash
ruff check src/
black src/            # 100-char line length
```

### Deployment
Railway and PyPI deploys are fully manual — there is no CI/CD and the Railway↔GitHub auto-deploy link is broken.

```bash
# Railway (run from auth_server/ directory)
railway up

# PyPI
python -m build
python -m twine upload dist/*    # requires a fresh token — never reuse one from chat history
```

## Architecture

### Protocol layer — `server.py`
`MCPServer` is a hand-rolled JSON-RPC 2.0 server (no `mcp` SDK). It reads newline-delimited JSON from `stdin` and writes responses to `stdout` (stdio mode), or serves `aiohttp` routes in HTTP mode. All heavy imports are deferred at startup for fast cold-start. Tool dispatch flows:

```
stdin → MCPServer.handle_request()
          → handle_call_tool()
              → auth.validate_api_key()   # remote call, falls back if server down
              → tools.call_tool()         # routes by name
```

The server enforces a 900 KB response ceiling; oversized responses are automatically replaced with a summary (`_create_summary`).

### Tool layer — `tools.py`
`TOOLS_DEFINITIONS` is the MCP schema list exposed to clients. `call_tool()` is the router that dispatches to async implementations in the same file, plus a lazy import for `regime_detection`. The eight advertised tools are:

| Tool | What it does |
|---|---|
| `chavez_transform` | Integral transform anchored to Pattern 1 (Canonical Six) |
| `detect_patterns` | 4-stage pattern detection pipeline via `PatternDetector` |
| `verify_bilateral_oracle` | Exact P×Q=0 and Q×P=0 check at 10⁻¹⁵ |
| `map_e8_orbit` | Projects a vector onto verified E8 Weyl orbits |
| `zdtp_transmit` | Zero Divisor Transmission Protocol (16D→256D) |
| `list_domain_profiles` | Enumerates available domain profiles |
| `illustrate` | General-purpose chart renderer; accepts `plot_spec` dict, returns base64 PNG inline |
| `get_version` | Returns package version from `__init__.__version__` |

### Pattern detection — `patterns.py`
`PatternDetector.detect_all_patterns()` runs four stages in order, merges results, and sorts by confidence (descending):

1. **`_detect_numerical_patterns()`** — heuristic sequence analysis for general numerical data:
   - Linear (arithmetic): constant first differences
   - Geometric: constant successive ratios (all terms nonzero)
   - Fibonacci-type: additive recurrence `a[n] = a[n-1] + a[n-2]` within 10⁻⁶ relative error
   - Returns early on first match (linear → geometric → Fibonacci, mutually exclusive)

2. **`_detect_algebraic_structure()`** — `detect_g2_family(data, data)` self-interaction check. Returns a result only when no component falls on boundary indices `{0, 7, 8, 15}`. This is strict by design — it expects sedenion-structured input, not arbitrary numerical data.

3. **`_detect_geometric_projection()`** — `map_to_weyl_orbit(data)` checks whether `‖v_8d‖² ≈ 2.0` (E8 first-shell norm). Rarely fires on general data; designed for algebraic element inputs.

4. **`_detect_symmetry_v2()`** — five symmetry modes with per-mode confidence thresholds:
   - Conjugate / palindromic symmetry (`data[k] ≈ data[n-1-k]`, conf > 0.6)
   - Anti-symmetry (`data[k] ≈ -data[n-1-k]`, conf > 0.6)
   - Cyclic / periodic (period 2…n/2, conf > 0.7)
   - Bilateral functional `f(x) ≈ f(1-x)` on uniform grid (RHI-relevant, conf > 0.6)
   - Wildcard polynomial fit degree 1–4 (R² > 0.97, only if no sequence type already detected)

### Visualization — `visualizations.py`
Pure matplotlib (Plotly was removed). The active renderer chain is:

- **`plot_custom(plot_spec, style_hints)`** — top-level entry point called by `illustrate`. Handles figure-level config (`figure.figsize/dpi/facecolor`) and the `subplots` multi-panel layout. Delegates each panel to `_render_axes`.
- **`_render_axes(ax, spec)`** — renders a single axes panel from a spec dict. Supported trace types: `bar`, `line`, `scatter`, `fill`, `hist`, `pie`, `heatmap`, `axhline`, `axvline`.

Key `plot_spec` keys and their types:
- `axes`: list of trace dicts (each with `type`, `x`, `y`, `color`, `alpha`, `label`, etc.)
- `grid`: **bool or dict**. `true` → `ax.grid(True)`. Dict passes `axis/alpha/linewidth/color` as kwargs.
- `legend`: **bool or dict**. `true` → `ax.legend()`. Dict passes kwargs through.
- `subplots`: list of sub-specs for multi-panel figures (each is its own full spec)
- `annotations`, `spines`, `xlim`, `ylim`, `xscale`, `yscale`, `xticks`, `xticklabels`, `tick_color`

The `illustrate` tool response includes `image` (base64 PNG) + `media_type: "image/png"` for inline display, plus `static_path` pointing to the saved file under `assets/visualizations/`.

Legacy named functions (`_plot_canonical_six_universality`, `_plot_gateway_magnitudes`, `_plot_bilateral_symmetry`, etc.) are still present for direct Python use but are no longer called by any tool.

### Core math engine — `src/cailculator_mcp/core/`
The ground truth for all mathematical computation. All modules here are Lean 4-verified:

- **`canonical_six.py`** — hardcoded bilateral zero divisor pairs (Patterns 1–6) as 32D numpy arrays; the source of truth for all gateway operations.
- **`chavez_transform.py`** — `ChavezTransform` class implementing the integral `C[f] = ∫ f(x) · K_Z(P,Q,x) · exp(-α‖x‖²) · Ω_d(x) dx`. Uses `scipy.integrate.quad` for 1D and Monte Carlo for N-D. Stability bound `|C[f]| ≤ M · ‖f‖₁` is checked after every integration.
- **`bilateral_collapse.py`** — oracle that verifies P×Q=0 AND Q×P=0.
- **`stability.py`** — computes the Lean-proved stability constant `M(P, Q, α)`.
- **`extended_structures.py`** — generates the 24-family extension, Weyl orbit mapping, and G2 family detection.
- **`clifford_element.py`** — Clifford algebra element wrapper.

### ZDTP — `src/cailculator_mcp/zdtp/`
Zero Divisor Transmission Protocol transmits a 16-element vector through verified bilateral gateways up to 256D. `protocol.py` contains `ZDTPTransmission` which:
1. Fetches the `(P, Q)` gateway pair from `gateways.py` (backed by Canonical Six).
2. Runs the oracle verification before any transmission.
3. Expands state iteratively: 16D→32D→64D→128D→256D using the 4-factor bilateral interaction `{Px, xQ, Qx, xP}`.
4. `full_cascade()` runs all 6 gateways and returns a convergence score (coefficient of variation of 256D magnitudes).

### Domain profiles — `src/cailculator_mcp/profiles/`
Profiles provide domain-specific labeling without changing the math. Each profile directory contains:
- `manifest.json` — metadata discovered by `ProfileManager.list_profiles()`
- `coefficient_mapping.py` — maps domain data (OHLCV, political indices, etc.) to 16D sedenion coefficients
- `terminology.py` — `translate_output()` that relabels algebraic output in domain language
- `gateway_labels.py` — `get_label(pattern_id)` for human-readable gateway names

Available profiles: `quant_equity`, `journalism`, `rhi`, `general_data`, `developer_v1`.

`ProfileManager` dynamically imports profile modules at runtime via `importlib`. It falls back gracefully if a profile sub-module is missing.

### Authentication — `auth.py` + `config.py`
Every tool call hits `validate_api_key()` before execution. It POSTs to `CAILCULATOR_AUTH_ENDPOINT` (default: Railway-hosted server). If the auth server is unreachable and `CAILCULATOR_ENABLE_OFFLINE_FALLBACK=true`, the call proceeds. Dev mode bypasses auth for keys prefixed `dev_`. Settings are pydantic-settings with `CAILCULATOR_` prefix.

### Lean 4 formal proofs — `lean/`
Mathematical correctness proofs live here. Key files:
- `BilateralCollapse.lean` — proves P×Q=0 AND Q×P=0 for Canonical Six
- `ChavezTransform_genuine.lean` — proves convergence and stability bound
- `e8_weyl_orbit_unification.lean` — E8 first shell / Weyl orbit membership

The `lakefile.toml` at the project root is the Lake build file. Running proofs requires Lean 4 / Mathlib installed separately — it is not part of the Python build.

### Hypercomplex wrapper — `hypercomplex.py`
Thin adapter over the `hypercomplex` PyPI package. `create_hypercomplex(dimension, coeffs, framework)` is the single factory used throughout the codebase to instantiate algebra elements in either Cayley-Dickson or Clifford mode.

## Key invariants

- **Canonical Six are the only zero divisor patterns used as gateways.** They are hardcoded in `core/canonical_six.py` and verified in Lean. Never substitute numerically-discovered pairs.
- **E0 channel avoidance:** The Chavez Transform kernel maps input data to indices `e_1…e_{n-1}`, skipping `e_0`, to prevent scalar-channel invariance collapse (Option A fix).
- **AIEX-506 regression guard:** `tests/test_v2_integration.py` asserts the stability bound holds at α∈{0.1, 1.0, 5.0}. This test exists because v1.4.7 violated the bound at α=1.0 and α=5.0.
- **AIEX-684 regression guard:** `detect_patterns` was silently returning empty for all inputs because `_detect_algebraic_structure` and `_detect_geometric_projection` are too strict for general numerical data. Fixed in v2.1.1 by adding `_detect_numerical_patterns()` as stage 1 of the pipeline. Do not remove this stage.
- **AIEX-685 regression guard:** `illustrate` crashed with `'bool' object has no attribute 'get'` when `plot_spec` contained multiple `axes` traces alongside boolean `grid` or `legend` keys. Fixed in v2.1.1 in `_render_axes()`. The `grid` handler must always guard with `isinstance(g, dict)` before calling `.get()`.
- **Response size cap:** `MAX_RESPONSE_SIZE = 900_000` bytes in `server.py` prevents MCP 1 MB limit errors.
- **`plot_spec` boolean keys:** Both `grid` and `legend` accept `bool` or `dict`. `grid: true` must call `ax.grid(True)` directly — never `.get()` on the value without a type check first.
