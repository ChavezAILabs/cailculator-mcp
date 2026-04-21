"""
CAILculator v2.0 Tools - Production
Tool definitions governed by High-Precision Engine and Oracle Layer
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Force non-interactive matplotlib backend
os.environ.setdefault("MPLBACKEND", "Agg")

# v2.0 Core Imports
from .core.chavez_transform import ChavezTransform
from .core.canonical_six import get_canonical_six, get_pattern_metadata
from .core.stability import get_stability_constant, verify_bound
from .core.bilateral_collapse import verify_bilateral_collapse
from .core.extended_structures import generate_24_families, map_to_weyl_orbit, detect_g2_family
from .profiles.manager import ProfileManager
from .zdtp.protocol import get_zdtp_v2

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
                "gateway": {"type": ["string", "integer"], "description": "S1-S6, 1-6, or 'all'"},
                "restrict_to_pattern": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Explicit pattern ID (1-6) to use as gateway. Overrides 'gateway' if provided."},
                "profile": {"type": "string", "default": "general_data"}
            },
            "required": ["input_16d"]
        }
    },
    {
        "name": "illustrate",
        "description": "Generate high-precision visualizations of patterns and transforms.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "visualization_type": {"type": "string", "enum": ["canonical_six_universality", "custom"]},
                "data": {"type": "object"}
            },
            "required": ["visualization_type"]
        }
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
    elif name == "regime_detection":
        from .regime_detection import regime_detection
        return await regime_detection(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

# --- Tool Implementations ---

async def chavez_transform(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
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
            "pattern_metadata": get_pattern_metadata(1),
            "precision": "10^-15"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def detect_patterns(arguments: Dict[str, Any]) -> Dict[str, Any]:
    from .patterns import PatternDetector
    try:
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
        P = np.array(arguments.get("P"))
        Q = np.array(arguments.get("Q"))
        fw = arguments.get("framework", "cayley-dickson")
        return verify_bilateral_collapse(P, Q, framework=fw)
    except Exception as e:
        return {"success": False, "error": str(e)}

async def map_e8_orbit(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        v = np.array(arguments.get("vector"))
        return map_to_weyl_orbit(v)
    except Exception as e:
        return {"success": False, "error": str(e)}

async def list_domain_profiles(arguments: Dict[str, Any]) -> Dict[str, Any]:
    pm = ProfileManager()
    return {"success": True, "profiles": pm.list_profiles()}

async def zdtp_transmit(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
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
            # S1-S6 mapping
            pid_map = {
                "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5, "S6": 6,
                "S3A": 3, "S3B": 4 # Backward compatibility
            }
            pid = pid_map.get(gateway.upper(), 1)
            
        result = zdtp.transmit(input_16d, pid, profile_name=profile)
        result["success"] = True
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def illustrate(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from .visualizations import plot_canonical_six_universality, save_figure
        from pathlib import Path
        import time

        vis_type = arguments.get("visualization_type", "canonical_six_universality")
        data = arguments.get("data", {})
        
        # Absolute Path Fix for Claude Desktop
        current_file = Path(__file__).resolve()
        repo_root = current_file.parent.parent.parent
        assets_dir = repo_root / "assets" / "visualizations"
        assets_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{vis_type}_{time.strftime('%Y%m%d_%H%M%S')}.png"
        filepath = assets_dir / filename

        if vis_type == "canonical_six_universality":
            fig = plot_canonical_six_universality(data.get("values", {}))
            save_figure(fig, str(filepath))
            return {"success": True, "static_path": str(filepath), "engine": "v2.0 High-Precision"}
        
        return {"success": False, "error": f"Visualization {vis_type} not yet ported to v2.0"}
    except Exception as e:
        return {"success": False, "error": str(e)}
