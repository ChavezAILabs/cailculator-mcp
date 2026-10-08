"""
Fill in a *recorded* golden's expected values from the current code.

    python tests/golden/record_case.py <case_id> [<case_id> ...]

For each case with verification "recorded", runs the tool in-process and
copies the values at the case's `record_keys` (dotted paths) into `expected`,
and pins `expected_input_hash`. Refuses to touch a case that already has
expected values unless --force is given, and never touches hand/lean/literature
cases. Per the change policy, a --force re-record needs a CHANGELOG entry.

    python tests/golden/record_case.py --hash-only <case_id> ...

pins only `expected_input_hash` (allowed for every verification kind, and only
when the case has no hash yet).
"""

import argparse
import json
import sys

from runner import CASES_DIR, get_path, load_cases, run_inprocess


def nest(paths_values):
    out = {}
    for dotted, value in paths_values:
        node = out
        *parents, leaf = dotted.split(".")
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = value
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case_ids", nargs="+")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--hash-only", action="store_true")
    opts = ap.parse_args()

    cases = {c["id"]: c for c in load_cases()}
    for cid in opts.case_ids:
        case = cases[cid]
        if opts.hash_only:
            if case.get("expected_input_hash") and not opts.force:
                sys.exit(f"{cid}: input hash already pinned; use --force (and add a CHANGELOG entry)")
            result = run_inprocess(case["tool"], case["resolved_args"])
            path = CASES_DIR / f"{cid}.json"
            raw = json.loads(path.read_text(encoding="utf-8"))
            raw["expected_input_hash"] = result["provenance"]["input_hash"]
            path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"pinned input hash for {cid}")
            continue
        if case["verification"] != "recorded":
            sys.exit(f"{cid}: verification is {case['verification']!r}; only 'recorded' cases may be recorded")
        if case.get("expected") and not opts.force:
            sys.exit(f"{cid}: already has expected values; use --force (and add a CHANGELOG entry)")
        result = run_inprocess(case["tool"], case["resolved_args"])
        values = [(k, get_path(result, k)) for k in case.get("record_keys", [])]
        path = CASES_DIR / f"{cid}.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["expected"] = nest(values)
        raw["expected_input_hash"] = result["provenance"]["input_hash"]
        # Recorded floats: absolute tolerance scaled to magnitude (1e-9·|v|, floor 1e-12),
        # unless the case already sets one for that path.
        tol = raw.setdefault("tolerance", {})
        for dotted, value in values:
            if isinstance(value, float) and dotted not in tol:
                tol[dotted] = max(1e-12, 1e-9 * abs(value))
        path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"recorded {cid}: {[k for k, _ in values]}")


if __name__ == "__main__":
    main()
