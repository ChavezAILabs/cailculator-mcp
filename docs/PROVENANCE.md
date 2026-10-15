# Response Provenance

Every CAILculator tool response, including error responses, carries a top-level
`provenance` object. It states what produced the result, so anyone can see exactly
how a number was made and re-check it. The block is added alongside the existing
response fields and never replaces them.

```json
"provenance": {
  "server": "cailculator-mcp",
  "server_version": "2.2.0",
  "engine_version": "v2.0 High-Precision",
  "build_commit": "abc1234",
  "build_commit_source": "build",
  "tool": "compute_high_dimensional",
  "algorithm": "cayley_dickson.is_zero_divisor/1",
  "framework": "cayley-dickson",
  "signature": null,
  "dimension": 64,
  "profile": null,
  "plan": "individual",
  "tolerance": { "zero_threshold": 1e-10 },
  "input_hash": "sha256:…",
  "input_basis": "normalized",
  "hash_scheme": "canonical-json-v1",
  "golden_suite": "1",
  "timestamp_utc": "2026-09-22T21:10:00Z"
}
```

## Fields

| Field | Meaning |
|---|---|
| `server_version` | Package version (`get_version`). |
| `engine_version` | Numerical engine generation. |
| `build_commit` | Git commit the package was built from, stamped by `scripts/release_gate.py`. |
| `build_commit_source` | `build` = stamped at release; `git` = read live from a source checkout (a `+dirty` suffix means uncommitted changes); `unknown` = neither was available. |
| `tool` | Tool that ran. |
| `algorithm` | Stable ID with a version suffix, e.g. `bilateral_oracle.clifford/1`. The suffix is bumped whenever the math or a default changes, even if nothing else in the release does. `<tool>/unreported` means the call failed before the tool described itself. |
| `framework` | `cayley-dickson`, `clifford`, or `null` when no algebra product is involved. |
| `signature` | Clifford metric signature actually used, e.g. `Cl(5,0)` for a 32D `verify_bilateral_oracle` call (Cl(n,0), n = log₂ dimension; every generator squares to +1). Whether a pair is a zero divisor can depend on the signature. `null` for Cayley-Dickson and for tools with no Clifford product. Added 2026-10-14. |
| `dimension` | Algebra dimension used, or `null` for multi-dimension pipelines (`analyze_dataset`). |
| `profile` | `null`, or `{name, version, tier, gate_status}`. An `Experimental` profile also carries `gates_failed` and a plain `notice` explaining why. |
| `plan` | The caller's subscription plan, which decides the profiles it may use (`plans.py`). `"developer"` for dev keys in a source checkout; `null` for in-process calls made without a plan. |
| `tolerance` | The thresholds **actually applied** to produce this answer (for example `zero_threshold`). This is what tells the two zero-divisor tools apart: see `EVALUATION_CONTRACT.md`. |
| `input_hash` | SHA-256 of the normalized inputs (scheme below). |
| `input_basis` | `normalized` = the inputs the tool actually used, after parsing and validation, with defaults filled in and dimension inferred. `raw_request` = the call failed validation, so the raw arguments were hashed instead. |
| `golden_suite` | Version of the golden test suite this build passed (`tests/golden/VERSION`); `null` for unstamped source checkouts. |
| `timestamp_utc` | When the response was produced. |

## Hash scheme: `canonical-json-v1`

1. Take the **normalized** inputs the tool reports: parsed, validated, defaults filled in.
   Coefficient vectors are zero-padded to the working dimension, and numeric arrays are
   floats.
2. Serialize as JSON with keys sorted, no whitespace (`","` and `":"` separators), UTF-8,
   non-ASCII characters kept as-is, floats written with Python `repr()` (the shortest
   form that round-trips), and integers written as integers. So `2` and `2.0` hash
   differently, which is why vectors are normalized to floats first. NaN and Infinity
   never appear, because validation rejects them.
3. Take the SHA-256 of those bytes and prefix it with `sha256:`.

### Reference script

This recomputes a hash without CAILculator. Pass the normalized inputs as a JSON object:

```python
import hashlib, json, sys

def canonical_json_v1(obj):
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()

if __name__ == "__main__":
    print(canonical_json_v1(json.load(sys.stdin)))
```

Python's `json` module writes floats with `repr()`, so this matches the server
byte for byte.

### What each tool hashes

| Tool | Normalized inputs |
|---|---|
| `compute_high_dimensional` | `operation`, `dimension` (inferred if omitted), `a` (zero-padded floats), `b` when the operation uses it |
| `verify_bilateral_oracle` | `P`, `Q` (floats), `framework` (default filled in) |
| `chavez_transform` | `data` (floats), `alpha`, `dimension_param` (defaults filled in) |
| `detect_patterns` | `data` (floats), `alpha` |
| `zdtp_transmit` | `input_16d` (floats), `gateway: "all"` or the resolved `pattern_id`, `profile` |
| `analyze_dataset` | `close` (the analyzed series, floats), `profile`, `terminology_level` |
| `map_e8_orbit` | `vector` (floats) |
| `illustrate` | `plot_spec`, `style_hints`, `description` |
| `list_domain_profiles`, `get_version` | `{}` |

Worked example: the golden case `tests/golden/cases/cd64_zd_positive.json` pins its
`expected_input_hash`. Its normalized inputs are
`{"a": [64 floats with 1.0 at 4 and 11], "b": [64 floats with 1.0 at 6 and 9], "dimension": 64, "operation": "is_zero_divisor"}`.

The golden suite checks every case's hash against the committed value, so a silent
change to input normalization fails the build.
