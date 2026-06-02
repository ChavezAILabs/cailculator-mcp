"""
CAILculator v2.0 Tools - Production
Tool definitions governed by High-Precision Engine and Oracle Layer
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

logger = logging.getLogger(__name__)

# --- Tool Definitions for MCP ---

TOOLS_DEFINITIONS = [
    {
        "name": "chavez_transform",
        "description": "Apply the High-Precision Chavez Transform (v2.0) to numerical data. A general integral transform for convergence and stability analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "number"}},
                "alpha": {"type": "number", "default": 1.0},
                "dimension_param": {"type": "integer", "default": 2}
            },
            "required": ["data"]
        }
    },
    {
        "name": "detect_patterns",
        "description": "Detect mathematical patterns (v2.0) using verified algebraic structures.",
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
        "description": "Exact P*Q=0 and Q*P=0 check at 10^-15 precision for any two vectors.",
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
        "description": "Projects a 16D/32D vector onto verified E8 Weyl orbits.",
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
        "description": "Lists available v2.0 domain profiles (Quant, Journalism, RHI).",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "zdtp_transmit",
        "description": "Zero Divisor Transmission Protocol v2.0 - High-precision structural transmission up to 256D (Algebraic Ceiling).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_16d": {"type": "array", "items": {"type": "number"}, "minItems": 16, "maxItems": 16},
                "gateway": {"type": ["string", "integer"], "description": "S1, S2, S3A, S3B, S4, S5, 1-6, or 'all'"},
                "restrict_to_pattern": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Explicit pattern ID (1-6) to use as gateway. Overrides 'gateway' if provided."},
                "profile": {"type": "string", "default": "general_data"}
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
            "Runs three layers in one call: Chavez Transform (stability scoring), "
            "pattern detection (linear/geometric/Fibonacci/symmetry), and ZDTP full cascade "
            "(structural regime health via all six Canonical gateways to 256D). "
            "Returns regime classification (STABLE/TRANSITIONING/SHIFTING), top patterns, "
            "per-gateway magnitudes with domain labels, and a convergence score. "
            "Accepts a close-price list or an OHLCV dict. Minimum 16 data points. "
            "Default profile: quant_equity."
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
                    "default": "quant_equity",
                    "description": "Domain profile for terminology and gateway labels."
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
            "norm returns the scalar magnitude. is_zero_divisor checks bilateral annihilation (PQ=0 AND QP=0) "
            "at 10^-10 — consistent with the verify_bilateral_oracle tool."
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

async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
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
    elif name == "regime_detection":
        from .regime_detection import regime_detection
        return await regime_detection(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

# --- Tool Implementations ---

async def chavez_transform(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.chavez_transform import ChavezTransform
        from .core.canonical_six import get_canonical_six

        data = arguments.get("data")
        alpha = float(arguments.get("alpha", 1.0))
        d = int(arguments.get("dimension_param", 2))

        if not data: return {"success": False, "error": "No data"}

        ct = ChavezTransform(dimension=32, alpha=alpha)
        # Use Pattern 1 as the default anchor for the general transform
        P_arr, Q_arr = get_canonical_six(32)[1]

        data_arr = np.array(data)
        def f(x):
            x_scalar = x[0] if x.ndim > 0 and len(x) > 0 else float(x)
            indices = np.linspace(-5, 5, len(data_arr))
            return float(np.sum(data_arr * np.exp(-((x_scalar - indices)**2))))

        result = ct.transform_1d(f, P_arr, Q_arr, d)

        return {
            "success": True,
            "transform_value": float(result["value"]),
            "stability_bound": result["stability_bound"],
            "precision": "10^-15"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def detect_patterns(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .patterns import PatternDetector
        data = np.array(arguments.get("data", []))
        alpha = float(arguments.get("alpha", 1.0))
        detector = PatternDetector(alpha=alpha)
        patterns = detector.detect_all_patterns(data)
        return {
            "success": True,
            "patterns_detected": [
                {"type": p.pattern_type, "confidence": p.confidence, "description": p.description, "metrics": p.metrics}
                for p in patterns
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def verify_bilateral_oracle(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.bilateral_collapse import verify_bilateral_collapse
        P = np.array(arguments.get("P"))
        Q = np.array(arguments.get("Q"))
        fw = arguments.get("framework", "cayley-dickson")
        return verify_bilateral_collapse(P, Q, framework=fw)
    except Exception as e:
        return {"success": False, "error": str(e)}

async def map_e8_orbit(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import numpy as np
        from .core.extended_structures import map_to_weyl_orbit
        v = np.array(arguments.get("vector"))
        return map_to_weyl_orbit(v)
    except Exception as e:
        return {"success": False, "error": str(e)}

async def list_domain_profiles(arguments: Dict[str, Any]) -> Dict[str, Any]:
    from .profiles.manager import ProfileManager
    pm = ProfileManager()
    return {"success": True, "profiles": pm.list_profiles()}

async def zdtp_transmit(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from .zdtp.protocol import get_zdtp_v2
        input_16d = list(arguments.get("input_16d", []))
        gateway = arguments.get("gateway")
        restrict_to_pattern = arguments.get("restrict_to_pattern")
        profile = arguments.get("profile", "general_data")

        zdtp = get_zdtp_v2()
        
        if gateway == "all":
            result = zdtp.full_cascade(input_16d, profile_name=profile)
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
            
        result = zdtp.transmit(input_16d, pid, profile_name=profile)
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
        from .patterns import PatternDetector
        from .zdtp.protocol import get_zdtp_v2
        from .profiles.manager import ProfileManager
        from . import __version__

        raw = arguments.get("data")
        profile_name = arguments.get("profile", "quant_equity")
        level = arguments.get("terminology_level", "standard")

        if raw is None:
            return {"success": False, "error": "data is required"}

        # Accept list of numbers (close prices) or OHLCV dict
        if isinstance(raw, list):
            close = np.array(raw, dtype=float)
        elif isinstance(raw, dict):
            close_key = next((k for k in ("close", "Close", "price", "Price") if k in raw), None)
            if not close_key:
                return {"success": False, "error": "data dict must contain a 'close' key"}
            close = np.array(raw[close_key], dtype=float)
        else:
            return {"success": False, "error": "data must be a list of numbers or a dict with a 'close' key"}

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
        stability_level = convergence.get("stability_level", "UNKNOWN")

        # --- Regime classification from convergence ---
        if conv_score >= 0.8:
            regime = "stable"
        elif conv_score >= 0.5:
            regime = "transitioning"
        else:
            regime = "shifting"

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
                "classification": regime,
                "stability_level": stability_level,
                "convergence_score": round(conv_score, 4),
                "interpretation": (
                    "High structural coherence across all six gateways - market in equilibrium."
                    if regime == "stable" else
                    "Moderate coherence - potential regime shift in progress."
                    if regime == "transitioning" else
                    "Low coherence - structural break detected, regimes diverging."
                )
            },
            "structural_analysis": {
                "chavez_transform_value": round(float(ct_result["value"]), 6),
                "stability_bound": ct_result["stability_bound"],
                "patterns_detected": len(patterns),
                "top_patterns": [
                    {
                        "type": p.pattern_type,
                        "confidence": round(float(p.confidence), 3),
                        "description": p.description
                    }
                    for p in sorted(patterns, key=lambda p: p.confidence, reverse=True)[:3]
                ]
            },
            "gateway_breakdown": gateway_breakdown,
            "zdtp_convergence": {
                "score": round(conv_score, 4),
                "mean_magnitude": round(float(convergence.get("mean_magnitude", 0.0)), 6),
                "std_dev": round(float(convergence.get("std_dev", 0.0)), 6)
            },
            "engine": f"v{__version__}"
        }

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

        cls = _DIM_CLASS[dimension]

        def pad(coeffs):
            return (list(coeffs) + [0.0] * dimension)[:dimension]

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
        threshold = 1e-10
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
    return {
        "success": True,
        "version": __version__,
        "engine": "v2.0 High-Precision",
        "precision": "10^-15",
        "status": "Production Stable"
    }
