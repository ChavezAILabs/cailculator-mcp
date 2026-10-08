"""
Profile gate check (Job 3C). Writes src/cailculator_mcp/profiles/<name>/GATES.json.

    python scripts/check_profile_gates.py                 # all non-Template profiles
    python scripts/check_profile_gates.py journalism rhi  # selected profiles
    options: --nulls 200  --workers 4  --stop-early

Gates a profile must pass to load as Official:
  G1 Claims       every empirical dependency cites an AIEX entry / DOI / URL AND states the
                  controls in that record ("controls" field); every used theorem is a Lean
                  file under lean/ with no `sorry`/`admit` (static check; Lean is not compiled)
  G2 Goldens      >=1 golden case per documented use plus >=1 null control, all passing
                  in-process (a known_failure case counts as failing)
  G3 Nulls        on >=200 seeded null series run through analyze_dataset with this profile,
                  the fraction flagged as structured is <= 5% (FP ceiling confirmed by Paul
                  2026-09-22). "Flagged" = runner.structural_findings() non-empty.
  G4 Determinism  one golden per documented use, run twice, identical output
  G5 Provenance   responses carry profile name, version (matching the manifest) and tier

Runs in-process against this checkout. Slow: analyze_dataset takes ~35 s per call, so a
full G3 run is ~200 calls per profile (use --workers). --stop-early ends G3 as soon as the
ceiling is certain to be exceeded; the record then says so.
"""

import argparse
import json
import logging
import math
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests" / "golden"))
import runner  # noqa: E402  (also puts src/ on sys.path)

PROFILES_DIR = REPO / "src" / "cailculator_mcp" / "profiles"
LEAN_DIR = REPO / "lean"
FP_CEILING = 0.05
REFERENCE_RE = re.compile(r"^(AIEX-\d+|doi:\S+|10\.\d{4,}/\S+|https?://\S+)$", re.IGNORECASE)


def _quiet():
    logging.disable(logging.CRITICAL)
    import warnings
    warnings.filterwarnings("ignore")


def _run(task):
    tool, args = task
    return runner.run_inprocess(tool, args)


# --- G1 ---

def gate_g1(manifest):
    problems = []
    for theorem in manifest.get("used_theorems", []):
        path = LEAN_DIR / f"{theorem}.lean"
        if not path.exists():
            problems.append(f"theorem {theorem}: no lean/{theorem}.lean")
            continue
        code = re.sub(r"--.*", "", path.read_text(encoding="utf-8"))
        code = re.sub(r"/-.*?-/", "", code, flags=re.DOTALL)
        holes = len(re.findall(r"\b(sorry|admit)\b", code))
        if holes:
            problems.append(f"theorem {theorem}: {holes} sorry/admit in lean/{theorem}.lean")
    for dep in manifest.get("empirical_dependencies", []):
        ref = str(dep.get("reference", ""))
        if not REFERENCE_RE.match(ref):
            problems.append(f"claim {dep.get('claim')!r}: reference {ref!r} is not a reproducible "
                            "test record (need an AIEX entry, DOI, or URL)")
        elif not dep.get("controls"):
            problems.append(f"claim {dep.get('claim')!r}: {ref} cited, but the manifest does not state "
                            "the controls in that record (add a 'controls' field once confirmed)")
    return {"passed": not problems, "details": problems or ["all claims and theorems traceable"]}


# --- G2 / G4 / G5 ---

def profile_cases(name):
    return [c for c in runner.load_cases() if c.get("profile") == name]


def gate_g2_g4_g5(name, manifest, pool):
    cases = profile_cases(name)
    uses = manifest.get("documented_uses", [])
    problems = []
    for use in uses:
        if not any(c["tool"] == use for c in cases):
            problems.append(f"no golden case for documented use {use!r}")
    if not any(c.get("null_control") for c in cases):
        problems.append("no null-control golden case")

    results = list(pool.map(_run, [(c["tool"], c["resolved_args"]) for c in cases]))
    for case, result in zip(cases, results):
        issues = runner.check_case(case, result)
        if issues:
            problems.append(f"{case['id']} fails: {issues[0]}" + (" (known failure)" if case.get("known_failure") else ""))
        elif case.get("known_failure"):
            problems.append(f"{case['id']} is marked known_failure but passes; review the marker")
    g2 = {"passed": not problems, "cases": len(cases), "details": problems or ["all profile goldens pass"]}

    # G4: rerun the first successful case for each documented use
    det_problems, reruns = [], []
    for use in uses:
        for case, first in zip(cases, results):
            if case["tool"] == use and first.get("success"):
                reruns.append((case, first))
                break
    seconds = list(pool.map(_run, [(c["tool"], c["resolved_args"]) for c, _ in reruns]))
    for (case, first), second in zip(reruns, seconds):
        if runner.strip_volatile(first) != runner.strip_volatile(second):
            det_problems.append(f"{case['id']}: output differs between two identical runs")
    if not reruns:
        det_problems.append("no successful case to rerun")
    g4 = {"passed": not det_problems, "details": det_problems or [f"{len(reruns)} case(s) identical on rerun"]}

    # G5: provenance on every profile response
    prov_problems = []
    for case, result in zip(cases, results):
        prof = (result.get("provenance") or {}).get("profile") or {}
        if prof.get("name") != name or prof.get("version") != manifest.get("version") or not prof.get("tier"):
            prov_problems.append(f"{case['id']}: provenance.profile = {prof}")
    g5 = {"passed": bool(cases) and not prov_problems,
          "details": prov_problems or [f"{len(cases)} response(s) carry name, version, tier"]}
    return g2, g4, g5


# --- G3 ---

def null_series(n):
    """Deterministic null set: half iid noise at realistic levels, half shuffled real-shaped series."""
    import numpy as np
    bases = [json.loads((runner.DATA_DIR / f).read_text(encoding="utf-8")) for f in (
        "journalism_politics_contributions.json", "journalism_public_health_violations.json",
        "journalism_poverty_snap_enrollment.json", "quant_prices_gbm.json")]
    out = []
    for i in range(n):
        rng = np.random.default_rng(10_000 + i)
        if i % 2 == 0:
            level = rng.uniform(10, 1000)
            out.append([round(float(v), 4) for v in rng.normal(level, level * rng.uniform(0.02, 0.2), size=48)])
        else:
            base = list(bases[(i // 2) % len(bases)])
            rng.shuffle(base)
            out.append(base)
    return out


def gate_g3(name, pool, n_nulls, stop_early):
    series = null_series(n_nulls)
    allowed = math.floor(FP_CEILING * n_nulls)
    flagged, run, kinds = 0, 0, {}
    batch = max(4, pool._max_workers * 2)
    for start in range(0, n_nulls, batch):
        chunk = series[start:start + batch]
        results = pool.map(_run, [("analyze_dataset", {"data": s, "profile": name}) for s in chunk])
        for res in results:
            run += 1
            if not res.get("success"):
                flagged += 1  # a crash on a null is not a clean negative
                kinds["error"] = kinds.get("error", 0) + 1
                continue
            findings = runner.structural_findings(res)
            if findings:
                flagged += 1
                for f in findings:
                    kinds[f] = kinds.get(f, 0) + 1
        if stop_early and flagged > allowed:
            break
    rate = flagged / run
    return {
        "passed": run == n_nulls and rate <= FP_CEILING,
        "false_positive_rate": rate,
        "null_series_run": run,
        "null_series_planned": n_nulls,
        "flagged": flagged,
        "stopped_early": run < n_nulls,
        "finding_counts": dict(sorted(kinds.items(), key=lambda kv: -kv[1])),
        "details": [f"{flagged}/{run} null series flagged as structured ({rate:.1%}); ceiling {FP_CEILING:.0%}"
                    + (" — stopped early once the ceiling was certain to be exceeded" if run < n_nulls else "")],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profiles", nargs="*")
    ap.add_argument("--nulls", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stop-early", action="store_true")
    opts = ap.parse_args()
    if opts.nulls < 200:
        print("WARNING: fewer than 200 null series; G3 requires >= 200 and will not pass.")

    _quiet()
    names = opts.profiles or sorted(p.name for p in PROFILES_DIR.iterdir() if (p / "manifest.json").exists())
    commit, suite = runner.git_commit(), runner.suite_version()
    with ProcessPoolExecutor(max_workers=opts.workers, initializer=_quiet) as pool:
        for name in names:
            manifest = json.loads((PROFILES_DIR / name / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("tier") == "Template":
                print(f"{name}: Template — gates not applicable, skipped")
                continue
            print(f"{name}: checking gates ...", flush=True)
            g1 = gate_g1(manifest)
            g2, g4, g5 = gate_g2_g4_g5(name, manifest, pool)
            g3 = gate_g3(name, pool, opts.nulls, opts.stop_early)
            gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5}
            if opts.nulls < 200:
                g3["passed"] = False
                g3["details"].append("fewer than 200 null series")
            record = {
                "profile": name,
                "profile_version": manifest.get("version"),
                "requested_tier": manifest.get("tier"),
                "all_passed": all(g["passed"] for g in gates.values()),
                "gates": gates,
                "false_positive_rate": g3["false_positive_rate"],
                "null_series": g3["null_series_run"],
                "fp_ceiling": FP_CEILING,
                "golden_suite": suite,
                "commit": commit,
                "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            (PROFILES_DIR / name / "GATES.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            status = "PASS" if record["all_passed"] else "FAIL"
            print(f"{name}: {status}  " + "  ".join(f"{k}={'pass' if v['passed'] else 'FAIL'}" for k, v in gates.items())
                  + f"  FP={g3['false_positive_rate']:.1%} ({g3['flagged']}/{g3['null_series_run']})", flush=True)
            for k, v in gates.items():
                if not v["passed"]:
                    for d in v["details"]:
                        print(f"    {k}: {d}")


if __name__ == "__main__":
    main()
