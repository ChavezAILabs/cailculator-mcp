"""
CAILculator Tools
Tool definitions (TOOLS_DEFINITIONS), routing and implementations.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

# Force non-interactive matplotlib backend before any matplotlib import
os.environ.setdefault("MPLBACKEND", "Agg")

# Heavy dependencies (numpy, scipy, clifford, hypercomplex, etc.) are imported
# lazily inside each tool function so that tools/list responds instantly.

from .provenance import report

logger = logging.getLogger(__name__)

# --- Tool Definitions for MCP ---

TOOLS_DEFINITIONS = [
    {
        "name": "chavez_transform",
        "description": "1D Chavez Transform of a numerical series (experimental; not validated as a structural signal). The value has an exact closed form: sum_i data_i * w_i, where the weights w_i depend only on the series length, alpha and dimension_param, and are largest in the middle of the series. It does not depend on the zero-divisor pair: any pair of the same shape, zero divisor or not, gives the identical value. It is reversal-symmetric (insensitive to sequence direction) and should not be used as a structural or pattern-detection signal. stability_bound is the Lean-verified bound |C[f]| <= M * ||f||_1. See docs/chavez_transform.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "number"}},
                "alpha": {"type": "number", "default": 1.0},
                "dimension_param": {"type": "integer", "default": 2, "description": "Exponent d in the dimensional weighting term Omega_d(x) = (1+||x||^2)^(-d/2). This is a decay-sharpness hyperparameter of the numerical integration, NOT the hypercomplex algebra dimension (which is fixed at 32 internally). Its effect on the output is dominated by this weighting formula and is largely independent of the input data's content."}
            },
            "required": ["data"]
        }
    },
    {
        "name": "detect_patterns",
        "description": "Checks a numeric series for simple patterns: linear, geometric and Fibonacci-type sequences, polynomial trend, and conjugate, anti-, cyclic and bilateral symmetry. Each of these carries a confidence that is a fixed value per pattern type or a fit measure, not a probability. Two further checks, G2_invariant_structure and E8_weyl_resonance, are experimental and not validated: they are reported with experimental=true and confidence null.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "number"}},
                "alpha": {"type": "number", "default": 1.0}
            },
            "required": ["data"]
        }
    },
    {
        "name": "verify_bilateral_oracle",
        "description": "Numerical check that P*Q and Q*P are both zero for any two vectors: reports the norms ||PQ|| and ||QP|| and declares the pair bilateral when both are below 1e-15. Runs in the Cayley-Dickson or Clifford framework. The Clifford framework uses the positive signature Cl(n,0) with n = log2(dimension) (every generator squares to +1; 16D sedenion indices map to Cl(4,0) blades by bitmask); other signatures are not available, and they can give different answers. The signature used is reported in provenance.signature.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "P": {"type": "array", "items": {"type": "number"}},
                "Q": {"type": "array", "items": {"type": "number"}},
                "framework": {"type": "string", "enum": ["cayley-dickson", "clifford"], "default": "cayley-dickson"}
            },
            "required": ["P", "Q"]
        }
    },
    {
        "name": "map_e8_orbit",
        "description": "Experimental. Projects the first 8 components (octonion half) of a 16D/32D input onto E8 first-shell Weyl orbits. Components e8-e15 of a 16D sedenion input are not included in the projection; a full-sedenion input returning is_on_first_shell=false is expected behavior.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vector": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["vector"]
        }
    },
    {
        "name": "list_domain_profiles",
        "description": "Lists available domain profiles (Quant Equity, Journalism, General Data, Developer) plus custom-request info.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "zdtp_transmit",
        "description": "Zero Divisor Transmission Protocol (experimental; not validated as a structural signal). Lifts a 16D input through one or all six Canonical Six gateways to 256D. The outputs have an exact closed form: for gateway k, magnitude_256d = sqrt(||x||^2 + 64*x0^2 + 16*s_k^2), where s_k is a signed sum of four input components; the convergence score is 1 - (std / mean) of the six magnitudes, clipped to [0, 1]. The zero-divisor property of the gateways does not enter the result. See docs/ZDTP_CLOSED_FORM.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_16d": {"type": "array", "items": {"type": "number"}, "minItems": 16, "maxItems": 16},
                "gateway": {"type": ["string", "integer"], "description": "S1, S2, S3A, S3B, S4, S5, 1-6, or 'all'"},
                "restrict_to_pattern": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Explicit pattern ID (1-6) to use as gateway. Overrides 'gateway' if provided."},
                "profile": {"type": "string", "description": "Domain profile. Omit to use your plan's default profile (see list_domain_profiles)."}
            },
            "required": ["input_16d"]
        }
    },
    {
        "name": "illustrate",
        "description": (
            "Generate a visualization from any data. "
            "Construct a plot_spec dict describing exactly what you want rendered — "
            "chart type, axes, colors, labels, layout. The server executes and returns "
            "the image inline. Use for any field: journalism, finance, mathematics, "
            "research, or general data analysis. No pre-programmed chart types."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "plot_spec": {
                    "type": "object",
                    "description": (
                        "Figure specification. Keys: "
                        "figure ({figsize, dpi, facecolor}), "
                        "axes (list of trace dicts with type/x/y/color/label/etc), "
                        "xlabel, ylabel, title, legend, grid, spines, xlim, ylim, "
                        "xscale, yscale, xticks, xticklabels, tick_color, annotations, "
                        "subplots (list of sub-specs for multi-panel figures). "
                        "Trace types: bar, line, scatter, fill, hist, pie, heatmap, axhline, axvline."
                    )
                },
                "description": {
                    "type": "string",
                    "description": "Plain language description of what this visualization shows. Used for logging and filename context."
                },
                "style_hints": {
                    "type": "object",
                    "description": "Optional metadata: audience, tone, theme. Not used for rendering — informational only."
                }
            },
            "required": ["plot_spec"]
        }
    },
    {
        "name": "analyze_dataset",
        "description": (
            "Full structural analysis pipeline for financial or numerical data. "
            "Runs three layers in one call: pattern detection (linear/geometric/Fibonacci/symmetry), "
            "the 1D Chavez Transform value, and the ZDTP full cascade (all six Canonical gateways "
            "to 256D). Returns top patterns, per-gateway magnitudes and a convergence score. "
            "The Chavez value and the ZDTP outputs are experimental and have exact closed forms "
            "that do not involve the zero-divisor property (a center-weighted sum of the series; "
            "norms plus signed four-term sums of the last 15 values), so treat them as "
            "measurements, not structural findings. regime.classification is 'not_assessed': the convergence "
            "score has not been validated as a regime detector, so no verdict is drawn from it. "
            "Accepts a close-price list or an OHLCV dict. Minimum 16 data points. "
            "Omit profile to use your plan's default profile."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {
                    "description": (
                        "Price series: either a list of numbers (treated as close prices) "
                        "or an object with a 'close' key (and optionally 'open','high','low','volume'). "
                        "Minimum 16 points."
                    )
                },
                "profile": {
                    "type": "string",
                    "description": (
                        "Domain profile for terminology and gateway labels. "
                        "Omit to use your plan's default profile (see list_domain_profiles)."
                    )
                },
                "terminology_level": {
                    "type": "string",
                    "enum": ["technical", "standard", "simple"],
                    "default": "standard",
                    "description": "Output terminology level."
                }
            },
            "required": ["data"]
        }
    },
    {
        "name": "compute_high_dimensional",
        "description": (
            "Cayley-Dickson algebra operations on hypercomplex elements from 16D (sedenions) to 256D. "
            "multiply/add/conjugate return the full coefficient vector (all N components). "
            "norm returns the scalar magnitude. is_zero_divisor checks bilateral annihilation (PQ=0 AND QP=0), "
            "declaring zero when both norms are below 1e-15, the same threshold as verify_bilateral_oracle; "
            "see docs/EVALUATION_CONTRACT.md. Every response carries a "
            "provenance block stating the threshold applied."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["multiply", "add", "conjugate", "norm", "is_zero_divisor"],
                    "description": "Algebraic operation to perform."
                },
                "a": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "First operand coefficient vector."
                },
                "b": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Second operand. Required for multiply, add, is_zero_divisor."
                },
                "dimension": {
                    "type": "integer",
                    "enum": [16, 32, 64, 128, 256],
                    "description": "Cayley-Dickson dimension. Inferred from the longer operand if omitted."
                }
            },
            "required": ["operation", "a"]
        }
    },
    {
        "name": "get_version",
        "description": "Returns the current version of the CAILculator MCP server.",
        "inputSchema": {"type": "object", "properties": {}}
    }
]

# --- Tool Routing ---

_KNOWN_TOOLS = {t["name"] for t in TOOLS_DEFINITIONS}


async def call_tool(name: str, arguments: Dict[str, Any], plan: Optional[str] = None) -> Dict[str, Any]:
    """Route a tool call and attach the provenance block to its response.

    Provenance and plan gating are applied here, in one place, so every tool
    (including new ones) gets them. ``plan`` is the caller's subscription plan from
    the auth server; None (in-process use, tests) applies no gating. Tool
    exceptions and denied profiles become {"success": False, "error": ...}
    responses, which also carry provenance.
    """
    from .provenance import collecting, build_provenance
    from .plans import apply_plan, normalize_plan, using_plan

    if name not in _KNOWN_TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    if plan is not None:
        plan = normalize_plan(plan)

    with using_plan(plan), collecting() as record:
        try:
            result = await _route(name, apply_plan(name, arguments, plan))
        except Exception as e:
            logger.error(f"Tool {name} raised: {e}", exc_info=True)
            result = {"success": False, "error": str(e)}
        if not isinstance(result, dict):
            result = {"success": True, "result": result}
        result["provenance"] = build_provenance(name, arguments, record)
    return result


async def _route(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Route tool call to v2.0 implementations."""
    logger.info(f"v2.0 Routing: {name}")

    if name == "chavez_transform":
        return await chavez_transform(arguments)
    elif name == "detect_patterns":
        return await detect_patterns(arguments)
    elif name == "verify_bilateral_oracle":
        return await verify_bilateral_oracle(arguments)
    elif name == "map_e8_orbit":
        return await map_e8_orbit(arguments)
    elif name == "list_domain_profiles":
        return await list_domain_profiles(arguments)
    elif name == "zdtp_transmit":
        return await zdtp_transmit(arguments)
    elif name == "illustrate":
        return await illustrate(arguments)
    elif name == "analyze_dataset":
        return await analyze_dataset(arguments)
    elif name == "compute_high_dimensional":
        return await compute_high_dimensional(arguments)
    elif name == "get_version":
        return await get_version(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

# --- Tool Implementations ---

def _parse_numeric_data(data: Any, field_name: str = "data", allow_empty: bool = False):
    """Validates and converts `data` into a finite float64 numpy array.

    Raises ValueError (caught by each tool's own try/except) with a clear
    message instead of letting a raw numpy/scipy exception leak through for
    non-numeric elements (e.g. a stray string) or non-finite values (NaN/Inf,
    including numeric-looking strings like "NaN"/"Infinity" that numpy would
    otherwise silently parse into real NaN/Inf).
    """
    import numpy as np

    if data is None or (isinstance(data, (list, tuple)) and len(data) == 0):
        if allow_empty:
            return np.array([], dtype=np.float64)
        raise ValueError(f"'{field_name}' is required and must be a non-empty array of numbers")

    if not isinstance(data, (list, tuple)):
        raise ValueError(f"'{field_name}' must be an array of numbers, got {type(data).__name__}")

    missing = [i for i, v in enumerate(data) if v is None]
    if missing:
        raise ValueError(f"'{field_name}' has missing value(s) (null) at index/indices {missing}")

    try:
        arr = np.asarray(data, dtype=np.float64)
    except (ValueError, TypeError) as e:
        raise ValueError(f"'{field_name}' must contain only numbers: {e}")

    bad = np.where(~np.isfinite(arr))[0]
    if bad.size > 0:
        raise ValueError(
            f"'{field_name}' contains non-finite value(s) (NaN/Inf) at index/indices {bad.tolist()}"
        )

    return arr

# Thresholds each tool actually applies, reported in provenance["tolerance"].
# These mirror the literals in the implementations; they document, not configure.
_CHAVEZ_TOLERANCE = {
    "quad_epsabs": 1.49e-08, "quad_epsrel": 1.49e-08,  # scipy.integrate.quad defaults
    "stability_bound_slack": 1e-15,
}
_PATTERN_THRESHOLDS = {
    "sequence_relative_tol": 1e-9, "fibonacci_relative_tol": 1e-6,
    "symmetry_min_confidence": 0.6, "cyclic_min_confidence": 0.7, "polynomial_min_r2": 0.97,
    "e8_first_shell_tol": 1e-10,
}
_ORACLE_ZERO_THRESHOLD = 1e-15
# One zero threshold for both zero-divisor tools (Paul, 2026-10-22: "precision to 15 zeros").
# compute_high_dimensional used 1e-10 through 2.2.0 development.
_CD_ZERO_THRESHOLD = _ORACLE_ZERO_THRESHOLD

# The convergence score once mapped to stable (>= 0.8) / transitioning (>= 0.5) / shifting.
# On the 2.2.0 G3 null series it fell in 0.54-0.65, and so did every structured series
# tested (sine, palindrome, trend, 50% step break, constant), so the verdict carried no
# information: 198/200 nulls were "transitioning". It is withheld for every profile until
# a validated regime detector replaces it.
_REGIME_WITHHELD_NOTE = (
    "No regime verdict: the convergence score has not passed a validation gate (on seeded "
    "null series it falls in the same range as structured series). It is reported as a "
    "measurement only."
)

# Decision 1 (2.2.0): the 1D Chavez value and the ZDTP outputs are kept, labeled as what
# they compute. Closed forms: docs/chavez_transform.md, docs/ZDTP_CLOSED_FORM.md.
_CHAVEZ_1D_NOTE = (
    "Experimental, not validated as a structural signal. Closed form: sum_i data_i * w_i, a "
    "fixed center-weighted sum of the series (weights depend only on length, alpha and d). "
    "Identical for any zero-divisor or non-zero-divisor pair of the same shape."
)

_ZDTP_NOTE = (
    "Experimental, not validated as a structural signal. Closed form: magnitude_256d(k) = "
    "sqrt(||x||^2 + 64*x0^2 + 16*s_k^2), s_k a signed sum of four input components; the "
    "convergence score is 1 - (std / mean) of the six magnitudes. The "
    "zero-divisor property does not enter the result (docs/ZDTP_CLOSED_FORM.md)."
)

_MEASURED_ONLY_NOTE = (
    "The {profile} profile reports measured quantities only (output_policy "
    "'measured_only'): no interpretation of this score has passed a validation gate."
)


def _require_profile(profile_name: Any) -> None:
    """Reject a profile name with no manifest, instead of silently running with defaults."""
    import os
    from .profiles.manager import ProfileManager
    pm = ProfileManager()
    if not (isinstance(profile_name, str) and profile_name.isidentifier()
            and os.path.exists(os.path.join(pm.profiles_dir, profile_name, "manifest.json"))):
        available = sorted(
            d for d in os.listdir(pm.profiles_dir)
            if os.path.exists(os.path.join(pm.profiles_dir, d, "manifest.json"))
        )
        raise ValueError(f"unknown profile {profile_name!r}; available: {available}")


def _profile_withholds_verdicts(profile_name: str) -> bool:
    from .profiles.manager import ProfileManager
    return ProfileManager().output_policy(profile_name).get("verdicts") == "measured_only"


async def chavez_transform(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.chavez_transform import ChavezTransform
        from .core.canonical_six import get_canonical_six

        alpha = float(arguments.get("alpha", 1.0))
        d = int(arguments.get("dimension_param", 2))

        data_arr = _parse_numeric_data(arguments.get("data"), "data")
        report(
            algorithm="chavez_transform.transform_1d/1", framework="cayley-dickson", dimension=32,
            tolerance=_CHAVEZ_TOLERANCE,
            inputs={"data": data_arr, "alpha": alpha, "dimension_param": d},
        )

        ct = ChavezTransform(dimension=32, alpha=alpha)
        # Use Pattern 1 as the default anchor for the general transform
        P_arr, Q_arr = get_canonical_six(32)[1]

        def f(x):
            x_scalar = x[0] if x.ndim > 0 and len(x) > 0 else float(x)
            indices = np.linspace(-5, 5, len(data_arr))
            return float(np.sum(data_arr * np.exp(-((x_scalar - indices)**2))))

        result = ct.transform_1d(f, P_arr, Q_arr, d)

        return {
            "success": True,
            "transform_value": float(result["value"]),
            "stability_bound": result["stability_bound"],
            "precision": "10^-15",
            "note": _CHAVEZ_1D_NOTE,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def detect_patterns(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from .patterns import PatternDetector
        data = _parse_numeric_data(arguments.get("data"), "data", allow_empty=True)
        alpha = float(arguments.get("alpha", 1.0))
        report(
            algorithm="pattern_detector.detect_all_patterns/1", tolerance=_PATTERN_THRESHOLDS,
            inputs={"data": data, "alpha": alpha},
        )
        detector = PatternDetector(alpha=alpha)
        patterns = detector.detect_all_patterns(data)
        return {
            "success": True,
            "patterns_detected": [
                {"type": p.pattern_type, "confidence": p.confidence, "experimental": p.experimental,
                 "description": p.description, "metrics": p.metrics}
                for p in patterns
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def verify_bilateral_oracle(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.bilateral_collapse import verify_bilateral_collapse
        fw = arguments.get("framework", "cayley-dickson")
        report(algorithm=f"bilateral_oracle.{fw}/1", framework=fw)
        if fw not in ("cayley-dickson", "clifford"):
            raise ValueError(f"framework must be 'cayley-dickson' or 'clifford', got {fw!r}")
        P = _parse_numeric_data(arguments.get("P"), "P")
        Q = _parse_numeric_data(arguments.get("Q"), "Q")
        dim = int(len(P))
        # Clifford products use the positive signature Cl(n,0), n = log2(dimension):
        # every generator squares to +1 (core/clifford_element.py). The answer depends on it.
        signature = None
        if fw == "clifford" and dim > 0 and dim & (dim - 1) == 0:
            signature = f"Cl({dim.bit_length() - 1},0)"
        report(
            algorithm=f"bilateral_oracle.{fw}/1", framework=fw, dimension=dim, signature=signature,
            tolerance={"zero_threshold": _ORACLE_ZERO_THRESHOLD},
            inputs={"P": P, "Q": Q, "framework": fw},
        )
        result = verify_bilateral_collapse(P, Q, precision=_ORACLE_ZERO_THRESHOLD, framework=fw)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def map_e8_orbit(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.extended_structures import map_to_weyl_orbit
        v = _parse_numeric_data(arguments.get("vector"), "vector")
        report(
            algorithm="e8.map_to_weyl_orbit/1", dimension=int(len(v)),
            tolerance={"zero_component": 1e-8, "first_shell": 1e-10},
            inputs={"vector": v},
        )
        return {"success": True, **map_to_weyl_orbit(v)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def list_domain_profiles(arguments: Dict[str, Any]) -> Dict[str, Any]:
    from .profiles.manager import ProfileManager
    report(algorithm="profiles.list/2", inputs={})
    from .plans import PLAN_PROFILES, current_plan, default_profile
    pm = ProfileManager()
    profiles = pm.list_profiles()
    plan = current_plan()
    if plan is None:
        return {"success": True, "profiles": profiles}
    included = PLAN_PROFILES[plan]
    for p in profiles:
        if p.get("name") != "custom_request":
            p["included_in_plan"] = p.get("name") in included
    return {"success": True, "plan": plan, "default_profile": default_profile(plan),
            "profiles": profiles}

async def zdtp_transmit(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from .zdtp.protocol import get_zdtp_v2
        input_16d = list(arguments.get("input_16d", []))
        gateway = arguments.get("gateway")
        restrict_to_pattern = arguments.get("restrict_to_pattern")
        profile = arguments.get("profile", "general_data")
        report(profile=profile)
        _require_profile(profile)

        zdtp = get_zdtp_v2()
        common = dict(framework="cayley-dickson", dimension=256, profile=profile,
                      tolerance={"oracle_zero_threshold": _ORACLE_ZERO_THRESHOLD})

        if gateway == "all":
            report(algorithm="zdtp.full_cascade/1",
                   inputs={"input_16d": [float(v) for v in input_16d], "gateway": "all",
                           "profile": profile},
                   **common)
            result = zdtp.full_cascade(input_16d, profile_name=profile)
            convergence = result.get("convergence", {})
            if "stability_level" in convergence:
                convergence["stability_level"] = "not_assessed"
                convergence["note"] = (_MEASURED_ONLY_NOTE.format(profile=profile)
                                       if _profile_withholds_verdicts(profile) else _REGIME_WITHHELD_NOTE)
            result["zdtp_note"] = _ZDTP_NOTE
            result["success"] = True
            return result
        
        # Determine Pattern ID
        pid = 1 # Default
        
        if restrict_to_pattern is not None:
            pid = int(restrict_to_pattern)
        elif isinstance(gateway, int):
            pid = gateway
        elif isinstance(gateway, str):
            pid_map = {
                "S1": 1, "S2": 2, "S3A": 3, "S3B": 4, "S4": 5, "S5": 6
            }
            pid = pid_map.get(gateway.upper(), 1)

        report(algorithm="zdtp.transmit/1",
               inputs={"input_16d": [float(v) for v in input_16d], "pattern_id": int(pid),
                       "profile": profile},
               **common)
        result = zdtp.transmit(input_16d, pid, profile_name=profile)
        result["zdtp_note"] = _ZDTP_NOTE
        result["success"] = True
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def illustrate(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from . import visualizations as viz, __version__
        from pathlib import Path
        import time
        import base64 as _b64

        plot_spec = arguments.get("plot_spec", {})
        style_hints = arguments.get("style_hints", {})
        description = arguments.get("description", "")
        report(algorithm="illustrate.plot_custom/1",
               inputs={"plot_spec": plot_spec, "style_hints": style_hints, "description": description})

        if not plot_spec:
            return {
                "success": False,
                "error": "plot_spec is required. Construct a plot_spec dict describing the figure and pass it with the data."
            }

        # Absolute path fix for Claude Desktop
        current_file = Path(__file__).resolve()
        repo_root = current_file.parent.parent.parent
        assets_dir = repo_root / "assets" / "visualizations"
        assets_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"custom_{timestamp}.png"
        filepath = assets_dir / filename

        fig = viz.plot_custom(plot_spec, style_hints=style_hints)

        # Encode BEFORE _fig_to_base64 closes the figure
        image_b64 = viz._fig_to_base64(fig)

        with open(str(filepath), 'wb') as f:
            f.write(_b64.b64decode(image_b64))

        return {
            "success": True,
            "static_path": str(filepath),
            "image": image_b64,
            "media_type": "image/png",
            "description": description,
            "engine": f"v{__version__}"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

async def analyze_dataset(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.chavez_transform import ChavezTransform
        from .core.canonical_six import get_canonical_six
        from .patterns import PatternDetector, by_confidence
        from .zdtp.protocol import get_zdtp_v2
        from .profiles.manager import ProfileManager
        from . import __version__

        raw = arguments.get("data")
        profile_name = arguments.get("profile", "quant_equity")
        level = arguments.get("terminology_level", "standard")
        report(algorithm="analyze_dataset.pipeline/1", profile=profile_name)
        _require_profile(profile_name)

        if raw is None:
            return {"success": False, "error": "data is required"}

        # Accept list of numbers (close prices) or OHLCV dict
        if isinstance(raw, list):
            close = _parse_numeric_data(raw, "data")
        elif isinstance(raw, dict):
            close_key = next((k for k in ("close", "Close", "price", "Price") if k in raw), None)
            if not close_key:
                return {"success": False, "error": "data dict must contain a 'close' key"}
            close = _parse_numeric_data(raw[close_key], "data.close")
        else:
            return {"success": False, "error": "data must be a list of numbers or a dict with a 'close' key"}

        report(
            algorithm="analyze_dataset.pipeline/1", framework="cayley-dickson", profile=profile_name,
            tolerance={"oracle_zero_threshold": _ORACLE_ZERO_THRESHOLD,
                       "pattern_thresholds": _PATTERN_THRESHOLDS},
            inputs={"close": close, "profile": profile_name, "terminology_level": level},
        )

        if len(close) < 16:
            return {"success": False, "error": f"Minimum 16 data points required, got {len(close)}"}

        # --- Layer 1: Pattern detection ---
        detector = PatternDetector(alpha=1.0)
        patterns = detector.detect_all_patterns(close)

        # --- Layer 2: Chavez Transform (S2 as structural anchor) ---
        ct = ChavezTransform(dimension=32, alpha=1.0)
        P_arr, Q_arr = get_canonical_six(32)[2]  # pid 2 = S2, Universal Bilateral Anchor
        indices = np.linspace(-5, 5, len(close))
        def f(x):
            x_s = float(x[0]) if hasattr(x, '__len__') and len(x) > 0 else float(x)
            return float(np.sum(close * np.exp(-((x_s - indices) ** 2))))
        ct_result = ct.transform_1d(f, P_arr, Q_arr, 2)

        # --- Layer 3: ZDTP full cascade ---
        # Build 16D input: last 15 close values normalized to e1-e15 (Option A: e0=0)
        window = close[-15:].copy()
        if window[0] != 0:
            window = window / window[0]  # relative to oldest bar in window
        input_16d = [0.0] + list(window)

        zdtp = get_zdtp_v2()
        cascade = zdtp.full_cascade(input_16d, profile_name=profile_name)
        convergence = cascade.get("convergence", {})
        conv_score = float(convergence.get("score", 0.0))

        # --- Per-gateway breakdown ---
        gateways_raw = cascade.get("gateways", {})
        gateway_breakdown = {}
        for gw in ("S1", "S2", "S3A", "S3B", "S4", "S5"):
            gw_data = gateways_raw.get(gw, {})
            gateway_breakdown[gw] = {
                "label": gw_data.get("gateway_label", gw),
                "magnitude_256d": round(float(gw_data.get("magnitude_256d", 0.0)), 6)
            }

        result = {
            "success": True,
            "profile": profile_name,
            "data_points": int(len(close)),
            "regime": {
                "classification": "not_assessed",
                "stability_level": "not_assessed",
                "convergence_score": round(conv_score, 4),
                "interpretation": _REGIME_WITHHELD_NOTE,
            },
            "structural_analysis": {
                "chavez_transform_value": round(float(ct_result["value"]), 6),
                "chavez_transform_note": _CHAVEZ_1D_NOTE,
                "stability_bound": ct_result["stability_bound"],
                "patterns_detected": len(patterns),
                "top_patterns": [
                    {
                        "type": p.pattern_type,
                        "confidence": None if p.confidence is None else round(float(p.confidence), 3),
                        "experimental": p.experimental,
                        "description": p.description
                    }
                    for p in sorted(patterns, key=by_confidence, reverse=True)[:3]
                ]
            },
            "gateway_breakdown": gateway_breakdown,
            "zdtp_convergence": {
                "score": round(conv_score, 4),
                "mean_magnitude": round(float(convergence.get("mean_magnitude", 0.0)), 6),
                "std_dev": round(float(convergence.get("std_dev", 0.0)), 6),
                "note": _ZDTP_NOTE,
            },
            "engine": f"v{__version__}"
        }

        # Profiles with output_policy "measured_only" get measured quantities, no verdicts
        if _profile_withholds_verdicts(profile_name):
            result["regime"]["interpretation"] = _MEASURED_ONLY_NOTE.format(profile=profile_name)
            result["structural_analysis"].update({
                "patterns_detected": 0,
                "top_patterns": [],
                "patterns_withheld": (
                    "Pattern-detector results are withheld under this profile: its detection "
                    "thresholds have not been validated against null data."
                ),
            })

        # Apply profile terminology translation at non-technical levels
        if level != "technical":
            pm = ProfileManager()
            pm.load_profile(profile_name)
            translate = pm.get_translator()
            result = translate(result, level)

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


async def compute_high_dimensional(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from hypercomplex import Sedenion, Pathion, Chingon, CD128, CD256

        _DIM_CLASS = {16: Sedenion, 32: Pathion, 64: Chingon, 128: CD128, 256: CD256}
        VALID_OPS = {"multiply", "add", "conjugate", "norm", "is_zero_divisor"}

        operation = arguments.get("operation")
        # Version suffixes per PROVENANCE.md; is_zero_divisor/2 = 1e-15 threshold (was 1e-10)
        _ALGO = {"is_zero_divisor": "cayley_dickson.is_zero_divisor/2"}
        algo = _ALGO.get(operation, f"cayley_dickson.{operation}/1")
        report(algorithm=algo, framework="cayley-dickson")
        if operation not in VALID_OPS:
            return {"success": False, "error": f"operation must be one of {sorted(VALID_OPS)}"}

        a_coeffs = list(arguments.get("a") or [])
        b_coeffs = list(arguments.get("b") or [])

        dimension = arguments.get("dimension")
        if dimension is None:
            max_len = max(len(a_coeffs), len(b_coeffs) if b_coeffs else 0)
            dimension = next((d for d in [16, 32, 64, 128, 256] if d >= max_len), None)
            if dimension is None:
                return {"success": False, "error": f"Input length {max_len} exceeds max supported dimension 256"}
        else:
            dimension = int(dimension)

        if dimension not in _DIM_CLASS:
            return {"success": False, "error": f"dimension must be one of [16, 32, 64, 128, 256], got {dimension}"}

        longest = max(len(a_coeffs), len(b_coeffs))
        if longest > dimension:
            return {"success": False, "error": (
                f"Operand has {longest} components but dimension is {dimension}; "
                "refusing to truncate silently")}

        cls = _DIM_CLASS[dimension]

        def pad(coeffs):
            return (list(coeffs) + [0.0] * dimension)[:dimension]

        uses_b = operation in ("multiply", "add", "is_zero_divisor")
        report(
            algorithm=algo, framework="cayley-dickson", dimension=dimension,
            tolerance={"zero_threshold": _CD_ZERO_THRESHOLD} if operation == "is_zero_divisor" else None,
            inputs={"operation": operation, "dimension": dimension,
                    "a": [float(v) for v in pad(a_coeffs)],
                    **({"b": [float(v) for v in pad(b_coeffs)]} if uses_b and b_coeffs else {})},
        )

        a_elem = cls(*pad(a_coeffs))

        if operation == "conjugate":
            return {
                "success": True, "operation": operation, "dimension": dimension,
                "result": list(a_elem.conjugate()), "precision": "10^-15"
            }

        if operation == "norm":
            return {
                "success": True, "operation": operation, "dimension": dimension,
                "norm": float(abs(a_elem)), "precision": "10^-15"
            }

        if not b_coeffs:
            return {"success": False, "error": f"operation '{operation}' requires argument 'b'"}
        b_elem = cls(*pad(b_coeffs))

        if operation == "multiply":
            return {
                "success": True, "operation": operation, "dimension": dimension,
                "result": list(a_elem * b_elem), "precision": "10^-15"
            }

        if operation == "add":
            return {
                "success": True, "operation": operation, "dimension": dimension,
                "result": list(a_elem + b_elem), "precision": "10^-15"
            }

        # is_zero_divisor
        pq_norm = float(abs(a_elem * b_elem))
        qp_norm = float(abs(b_elem * a_elem))
        threshold = _CD_ZERO_THRESHOLD
        return {
            "success": True, "operation": operation, "dimension": dimension,
            "is_bilateral_zero_divisor": pq_norm < threshold and qp_norm < threshold,
            "PQ_norm": pq_norm, "QP_norm": qp_norm,
            "threshold": threshold, "precision": "10^-15"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_version(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the version information for the CAILculator MCP."""
    from . import __version__
    from .provenance import ENGINE_VERSION
    report(algorithm="server.get_version/1", inputs={})
    return {
        "success": True,
        "version": __version__,
        "engine": ENGINE_VERSION,
        "precision": "10^-15",
        "status": "Production Stable"
    }
