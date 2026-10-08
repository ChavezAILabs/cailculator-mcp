"""
Golden suite runner library.

Loads case files, runs a case in-process (calling the tool handler directly)
or at the MCP level (a spawned `python -m cailculator_mcp.server` over stdio,
launched from a throwaway temp directory), and compares results against the
case's expectations. Used by test_golden.py and scripts/check_profile_gates.py.
"""

import asyncio
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

GOLDEN_DIR = Path(__file__).resolve().parent
REPO_ROOT = GOLDEN_DIR.parents[1]
SRC_DIR = REPO_ROOT / "src"
CASES_DIR = GOLDEN_DIR / "cases"
DATA_DIR = GOLDEN_DIR / "data"

VERIFICATION_KINDS = ("hand", "lean", "literature", "recorded")
DEFAULT_FLOAT_TOL = 1e-12
VOLATILE_PATHS = ("provenance.timestamp_utc",)
PROVENANCE_KEYS = (
    "server", "server_version", "engine_version", "build_commit", "tool", "algorithm",
    "framework", "dimension", "profile", "plan", "tolerance", "input_hash", "hash_scheme",
    "golden_suite", "timestamp_utc",
)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def suite_version() -> str:
    return (GOLDEN_DIR / "VERSION").read_text(encoding="utf-8").strip()


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                             capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=REPO_ROOT,
                               capture_output=True, timeout=10).returncode != 0
        return out.stdout.strip() + ("+dirty" if dirty else "") if out.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


# --- Case loading ---

def _resolve(value: Any) -> Any:
    """Expands {"$data": file} and {"$float": "nan"|"inf"|"-inf"} markers."""
    if isinstance(value, dict):
        if set(value) == {"$data"}:
            return json.loads((DATA_DIR / value["$data"]).read_text(encoding="utf-8"))
        if set(value) == {"$float"}:
            return float(value["$float"])
        return {k: _resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v) for v in value]
    return value


def load_cases() -> List[Dict[str, Any]]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        if case.get("id") != path.stem:
            raise ValueError(f"{path.name}: id {case.get('id')!r} must match file name")
        if case.get("verification") not in VERIFICATION_KINDS:
            raise ValueError(f"{path.name}: verification must be one of {VERIFICATION_KINDS}")
        if not case.get("source"):
            raise ValueError(f"{path.name}: source reference is required")
        case["resolved_args"] = _resolve(case["args"])
        cases.append(case)
    return cases


# --- Running ---

def run_inprocess(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    from cailculator_mcp.tools import call_tool
    # Same plan the spawned server gets for its dev key, so both modes are gated alike.
    return asyncio.run(call_tool(tool, args, plan="developer"))


class MCPServer:
    """One spawned CAILculator server speaking JSON-RPC over stdio."""

    def __init__(self, cwd: Optional[str] = None):
        self.cwd = cwd or tempfile.mkdtemp(prefix="cail_golden_cwd_")
        self._owns_cwd = cwd is None
        env = dict(os.environ)
        env.update({
            "PYTHONPATH": str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", ""),
            "CAILCULATOR_API_KEY": "dev_golden_suite",
            "CAILCULATOR_ENABLE_DEV_MODE": "true",
            "CAILCULATOR_ENABLE_OFFLINE_FALLBACK": "false",
            "PYTHONIOENCODING": "utf-8",
        })
        self.stderr_log = open(os.path.join(self.cwd, "server_stderr.log"), "w", encoding="utf-8")
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "cailculator_mcp.server"], cwd=self.cwd, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr_log,
            text=True, encoding="utf-8", bufsize=1,
        )
        self._next_id = 0
        self.lock = threading.Lock()
        init = self._request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                            "clientInfo": {"name": "golden-suite", "version": "1"}})
        self.server_info = init.get("result", {}).get("serverInfo")

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._next_id += 1
        msg = {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError(f"server exited (code {self.proc.poll()}); see {self.stderr_log.name}")
        return json.loads(line)

    def call_tool(self, tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            response = self._request("tools/call", {"name": tool, "arguments": args})
        if "error" in response:
            return {"success": False, "mcp_error": response["error"]}
        result = response["result"]
        texts = [c["text"] for c in result.get("content", []) if c.get("type") == "text"]
        parsed = json.loads(texts[-1]) if texts else {}
        if result.get("isError"):
            parsed["mcp_is_error"] = True
        return parsed

    def close(self) -> None:
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=30)
        except Exception:
            self.proc.kill()
        self.stderr_log.close()
        if self._owns_cwd:
            shutil.rmtree(self.cwd, ignore_errors=True)


# --- Comparison ---

def get_path(obj: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        else:
            raise KeyError(dotted)
    return obj


def compare(expected: Any, actual: Any, tolerances: Dict[str, float], path: str = "") -> List[str]:
    """Subset comparison: only keys present in `expected` are checked."""
    problems = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path or '<root>'}: expected object, got {type(actual).__name__}"]
        for key, exp_val in expected.items():
            sub = f"{path}.{key}" if path else key
            if key not in actual:
                problems.append(f"{sub}: missing")
            else:
                problems.extend(compare(exp_val, actual[key], tolerances, sub))
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            got = len(actual) if isinstance(actual, list) else type(actual).__name__
            return [f"{path}: expected list of {len(expected)}, got {got}"]
        for i, (e, a) in enumerate(zip(expected, actual)):
            problems.extend(compare(e, a, tolerances, f"{path}[{i}]"))
    elif isinstance(expected, bool) or expected is None or isinstance(expected, str):
        if actual != expected or type(actual) is not type(expected):
            problems.append(f"{path}: expected {expected!r}, got {actual!r}")
    elif isinstance(expected, (int, float)):
        if isinstance(actual, bool) or not isinstance(actual, (int, float)):
            return [f"{path}: expected number {expected!r}, got {actual!r}"]
        tol = tolerances.get(path, DEFAULT_FLOAT_TOL)
        if not (math.isfinite(actual) and abs(actual - expected) <= tol):
            problems.append(f"{path}: expected {expected!r} ± {tol}, got {actual!r}")
    else:
        problems.append(f"{path}: unsupported expected type {type(expected).__name__}")
    return problems


def structural_findings(result: Dict[str, Any]) -> List[str]:
    """Positive structural findings asserted by an analyze_dataset response.

    A response is "flagged as structured" if it asserts a regime shift
    (classification transitioning/shifting; since 2.2.0 always "not_assessed",
    kept so a future regime detector is gated the same way) or reports any
    detected pattern.
    Measured quantities (convergence score, magnitudes) are not findings.
    """
    findings = []
    regime = result.get("regime", {})
    if regime.get("classification") in ("transitioning", "shifting"):
        findings.append(f"regime:{regime['classification']}")
    analysis = result.get("structural_analysis", {})
    for p in analysis.get("top_patterns", []):
        findings.append(f"pattern:{p.get('type')}")
    if analysis.get("patterns_detected", 0) and not analysis.get("top_patterns"):
        findings.append(f"patterns_detected:{analysis['patterns_detected']}")
    return findings


def check_case(case: Dict[str, Any], result: Dict[str, Any]) -> List[str]:
    """All problems with `result` for this case (empty list means pass)."""
    problems = compare(case.get("expected", {}), result, case.get("tolerance", {}))

    prov = result.get("provenance")
    if not isinstance(prov, dict):
        problems.append("provenance: missing")
    else:
        missing = [k for k in PROVENANCE_KEYS if k not in prov]
        if missing:
            problems.append(f"provenance: missing keys {missing}")
        if prov.get("tool") != case["tool"]:
            problems.append(f"provenance.tool: expected {case['tool']!r}, got {prov.get('tool')!r}")
        if "expected_input_hash" in case and prov.get("input_hash") != case["expected_input_hash"]:
            problems.append(f"provenance.input_hash: expected {case['expected_input_hash']}, "
                            f"got {prov.get('input_hash')}")
        if case.get("profile"):
            prof = prov.get("profile") or {}
            for key in ("name", "version", "tier"):
                if not prof.get(key):
                    problems.append(f"provenance.profile.{key}: missing")
            if prof.get("name") != case["profile"]:
                problems.append(f"provenance.profile.name: expected {case['profile']!r}, "
                                f"got {prof.get('name')!r}")

    if "expected_structural_findings" in case:
        found = structural_findings(result)
        if found != case["expected_structural_findings"]:
            problems.append(f"structural findings: expected {case['expected_structural_findings']}, "
                            f"got {found}")
    return problems


def strip_volatile(result: Any) -> Any:
    result = json.loads(json.dumps(result))
    for dotted in VOLATILE_PATHS:
        *parents, leaf = dotted.split(".")
        node = result
        for part in parents:
            node = node.get(part, {}) if isinstance(node, dict) else {}
        if isinstance(node, dict):
            node.pop(leaf, None)
    return result
