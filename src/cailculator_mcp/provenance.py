"""
Response provenance for CAILculator tool calls.

Every tool response carries a top-level ``provenance`` block stating exactly
what produced it: server and engine version, build commit, algorithm ID, the
tolerance that was actually applied, the profile (with tier), and a hash of the
normalized inputs. See docs/PROVENANCE.md for the public spec.

Tools report their details through ``report()``; the dispatch wrapper in
``tools.call_tool`` collects them and builds the block, so a new tool gets
provenance automatically even if it reports nothing.
"""

import contextvars
import functools
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

SERVER_NAME = "cailculator-mcp"
ENGINE_VERSION = "v2.0 High-Precision"
HASH_SCHEME = "canonical-json-v1"

_collector: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "cailculator_provenance", default=None
)


# --- Canonical JSON / input hashing (canonical-json-v1) ---

def _normalize(obj: Any) -> Any:
    """Converts numpy/tuple values to plain JSON types, keeping int vs float distinct."""
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return [_normalize(v) for v in obj.tolist()]
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
    except ImportError:
        pass
    if isinstance(obj, dict):
        return {str(k): _normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_normalize(v) for v in obj]
    return obj


def canonical_json(obj: Any) -> bytes:
    """Keys sorted, no whitespace, UTF-8, floats as Python repr(), ints as ints."""
    return json.dumps(
        _normalize(obj), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def input_hash(obj: Any) -> str:
    try:
        return "sha256:" + hashlib.sha256(canonical_json(obj)).hexdigest()
    except (TypeError, ValueError):
        # Raw requests can hold values canonical JSON rejects (NaN, objects).
        return "sha256:" + hashlib.sha256(repr(obj).encode("utf-8")).hexdigest() + "#repr"


# --- Build info ---

@functools.lru_cache(maxsize=1)
def is_source_checkout() -> bool:
    """True when running from this project's own source tree (including an editable
    install), False for an installed wheel. Dev API keys are honored only here."""
    pyproject = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    try:
        return pyproject.exists() and 'name = "cailculator-mcp"' in pyproject.read_text(encoding="utf-8")
    except OSError:
        return False


@functools.lru_cache(maxsize=1)
def build_info() -> Dict[str, Any]:
    """Commit and golden-suite version baked in at release time.

    ``scripts/release_gate.py`` writes ``_build_info.py`` after the golden suite
    passes. A source checkout without it falls back to asking git (marked
    ``source: "git"``); anything else reports ``"unknown"`` rather than failing.
    """
    try:
        from . import _build_info
        return {
            "build_commit": _build_info.BUILD_COMMIT,
            "build_commit_source": "build",
            "golden_suite": _build_info.GOLDEN_SUITE,
        }
    except ImportError:
        pass
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parent.parent
    try:
        # Only trust git when running from this project's own source checkout.
        if not is_source_checkout():
            raise OSError("not a cailculator-mcp source checkout")
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=pkg_dir,
            capture_output=True, text=True, timeout=5,
        )
        if commit.returncode == 0:
            dirty = subprocess.run(
                ["git", "diff", "--quiet", "HEAD", "--", "."], cwd=repo_root,
                capture_output=True, timeout=5,
            ).returncode != 0
            return {
                "build_commit": commit.stdout.strip() + ("+dirty" if dirty else ""),
                "build_commit_source": "git",
                "golden_suite": None,
            }
    except (OSError, subprocess.SubprocessError):
        pass
    return {"build_commit": "unknown", "build_commit_source": "unknown", "golden_suite": None}


# --- Collection interface used by tools ---

def report(**fields: Any) -> None:
    """Called by a tool to describe what it actually did.

    Recognized fields: algorithm, framework, dimension, tolerance, inputs
    (the normalized inputs to hash), profile (name string).
    """
    rec = _collector.get()
    if rec is not None:
        rec.update(fields)


class collecting:
    """Context manager that opens a fresh provenance record for one tool call."""

    def __enter__(self) -> Dict[str, Any]:
        self.record: Dict[str, Any] = {}
        self._token = _collector.set(self.record)
        return self.record

    def __exit__(self, *exc) -> None:
        _collector.reset(self._token)


def build_provenance(tool: str, raw_arguments: Any, record: Dict[str, Any]) -> Dict[str, Any]:
    from . import __version__
    from .plans import current_plan

    if "inputs" in record:
        inputs, basis = record["inputs"], "normalized"
    else:
        inputs, basis = raw_arguments if raw_arguments is not None else {}, "raw_request"

    profile = None
    if record.get("profile") is not None:
        from .profiles.manager import ProfileManager
        profile = ProfileManager().describe(record["profile"])

    info = build_info()
    return {
        "server": SERVER_NAME,
        "server_version": __version__,
        "engine_version": ENGINE_VERSION,
        "build_commit": info["build_commit"],
        "build_commit_source": info["build_commit_source"],
        "tool": tool,
        "algorithm": record.get("algorithm", f"{tool}/unreported"),
        "framework": record.get("framework"),
        "dimension": record.get("dimension"),
        "profile": profile,
        "plan": current_plan(),
        "tolerance": record.get("tolerance"),
        "input_hash": input_hash(inputs),
        "input_basis": basis,
        "hash_scheme": HASH_SCHEME,
        "golden_suite": info["golden_suite"],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
