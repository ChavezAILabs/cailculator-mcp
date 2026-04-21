# CAILculator v2.0.1 — Regression & Dispatch Investigation

**Handoff target:** Gemini CLI (pre-investigation analysis)
**Session date:** 2026-04-21
**Author:** Paul Chavez (via Claude Desktop)
**Status:** AIEX-505 (Canonical Six dispatch collapse) **not resolved** in v2.0.1; additional parameter-routing anomalies discovered
**Deployment:** `https://cailculator-mcp-production.up.railway.app` (redeployed 2026-04-21 after auth endpoint fix)

---

## 1. Executive Summary

CAILculator v2.0.1 is operational after today's Railway redeployment (Paul confirmed manually). Auth validates; all seven MCP tools respond with `success: true`. However, empirical testing against the original AIEX-505 test protocol (asymmetric input across all six `pattern_id` values) shows the **dispatch collapse is still present** in `chavez_transform`. Additional sanity checks reveal:

- `alpha` and `dimension_param` **do** influence output (these code paths are live)
- `pattern_id` is **ignored** at the computation layer in `chavez_transform` (metadata echoes the parameter, but the numerical transform does not)
- `zdtp_transmit` gateway dispatch is **partially working**: state vectors differ by gateway, but `magnitude_256d` collapses to a single value
- `verify_bilateral_oracle` exhibits an **indexing-convention mismatch** with the metadata strings returned by `chavez_transform` (see §4.3)

**Priority:** `!critical` — affects commercial story (Canonical Six universality is the headline claim of Paper 2 and the verified selling point).

---

## 2. Environment

| Component | Version / State |
| --- | --- |
| CAILculator MCP server | v2.0 (Railway production, redeployed 2026-04-21) |
| Auth endpoint | `https://cailculator-mcp-production.up.railway.app/validate` |
| Auth status | Returns 200 on valid `api_key`; previously 500 on `cail_l0r6ZFNe...` pre-redeploy |
| Client | `cailculator-mcp.exe` via Claude Desktop (Windows 11, Python 3.13) |
| Handshake timing | `initialize` completes in <1s; tools load cleanly |
| Related KSJ captures | AIEX-505, AIEX-506, AIEX-511, AIEX-519 |

---

## 3. AIEX-505 Regression Test — `chavez_transform` Dispatch Collapse

### 3.1 Protocol
Call `chavez_transform` with identical asymmetric input `[1.0, 2.5, 3.7, 4.2, 5.1, 6.8, 7.3, 8.9]`, varying only `pattern_id ∈ {1..6}`. All other parameters at defaults (`alpha=1.0`, `dimension_param=2`).

### 3.2 Raw Results

| `pattern_id` | P, Q formula (from response) | `transform_value` | `M` | `ratio` |
|---|---|---|---|---|
| 1 | (e₁+e₁₄) × (e₃+e₁₂) | 20.47681443694484 | 2.9430355293715387 | 0.1143209577944108 |
| 2 | (e₃+e₁₂) × (e₅+e₁₀) | 20.47681443694484 | 2.9430355293715387 | 0.1143209577944108 |
| 3 | (e₄+e₁₁) × (e₆+e₉) | 20.47681443694484 | 2.9430355293715387 | 0.1143209577944108 |
| 4 | (e₁−e₁₄) × (e₃−e₁₂) | 20.47681443694484 | 2.9430355293715387 | 0.1143209577944108 |
| 5 | (e₁−e₁₄) × (e₅+e₁₀) | 20.47681443694484 | 2.9430355293715387 | 0.1143209577944108 |
| 6 | (e₂−e₁₃) × (e₆+e₉) | 20.47681443694484 | 2.9430355293715387 | 0.1143209577944108 |

### 3.3 Diagnosis
**Bit-identical outputs across all six patterns** for both `transform_value` and `stability_bound`. Only `pattern_metadata` differs, and metadata is just the parameter echo — no evidence it participated in the numerical computation. This reproduces AIEX-505 exactly; the only change from v1.4.7 is the specific numeric value (v1.4.7 returned 73.00827836854258 on its test input; v2.0.1 returns 20.47681443694484 on this input), which reflects upstream changes to the base transform, not a fix to the dispatch logic.

**Conclusion:** v2.0.1 does **not** resolve AIEX-505. The `pattern_id` parameter is parsed and reflected in metadata, but the compute path does not branch on it.

---

## 4. Sanity Checks

### 4.1 `alpha` Parameter — ✅ WORKING

Input `[1.0, 2.5, 3.7, 4.2, 5.1, 6.8, 7.3, 8.9]`, `pattern_id=1`, varying `alpha`:

| `alpha` | `transform_value` | `M` | `theoretical_max` |
|---|---|---|---|
| 0.1 | 157.6049252730455 | 29.430355293715383 | 1791.168901311108 |
| 1.0 (default) | 20.47681443694484 | 2.9430355293715387 | 179.11689013111084 |
| 5.0 | 2.9339582635083024 | 0.5886071058743078 | 35.823378026222166 |

Monotonic decrease with α. `M` scales proportionally with α⁻¹, consistent with the documented `M = 8/(α·e)` bound formula. **Note:** does not directly contradict AIEX-506 (stability-bound empirical violation at α=1.0 and α=5.0 on baseline Gaussian); that test used a different input and different comparison logic — needs separate re-test.

### 4.2 `dimension_param` — ✅ WORKING

Input `[1.0, 2.5, 3.7, 4.2, 5.1, 6.8, 7.3, 8.9]`, `alpha=1.0`, `pattern_id=1`:

| `dimension_param` | `transform_value` |
|---|---|
| 2 (default) | 20.47681443694484 |
| 4 | 11.495816406143584 |
| 8 | 5.007000868825958 |

Clear monotonic dependence. Parameter is reaching the compute layer. `M` does **not** scale with `dimension_param` (stays at 2.9430...) — this is a separate observation worth confirming against theory: should the stability constant be dimension-dependent?

### 4.3 `verify_bilateral_oracle` — ⚠️ INDEXING CONVENTION MISMATCH

Pattern 1 metadata from `chavez_transform` says: `(e_1 + e_14) × (e_3 + e_12) = 0`.

Attempted verifications with 16-dim basis vectors:

| Interpretation | P | Q | Result |
|---|---|---|---|
| 0-indexed: P at {1,14}, Q at {3,12} | `[0,1,0,...,1,0]` (pos 1,14) | `[0,0,0,1,...,1,0,0,0]` (pos 3,12) | ✅ `is_bilateral_zero_divisor: true`, PQ_norm=0 |
| 1-indexed: P at {0,13}, Q at {2,11} | `[1,0,...,1,0,0]` (pos 0,13) | `[0,0,1,...,1,0,0,0,0]` (pos 2,11) | ❌ PQ_norm=2 |
| 1-indexed alt: P at {2,13}, Q at {4,10} | `[0,0,1,...,1,0,0]` (pos 2,13) | `[0,0,0,0,1,...,1,...]` (pos 4,10) | ❌ PQ_norm=2 |

**Finding:** The `chavez_transform` `pattern_metadata.formula` string uses **1-indexed** basis labels (e_1 through e_14 appear), but the actual `verify_bilateral_oracle` vector indices are **0-indexed**. That means:
- `e_1 + e_14` in the metadata string → position 1 and position 14 in a 0-indexed vector
- `e_3 + e_12` → position 3 and position 12 in a 0-indexed vector

This is not a bug per se, but it is a **documentation / API consistency issue** that will trip up any external user trying to cross-validate the six patterns against the oracle. Either the formula strings should be 0-indexed (`e_0 + e_13`), or the oracle should accept 1-indexed inputs.

### 4.4 `zdtp_transmit` Gateway Dispatch — ⚠️ PARTIAL

Input 16D vector `[1.0, 2.0, ..., 16.0]`, varying `gateway`:

| `gateway` | `magnitude_256d` | state_32d nonzero positions (beyond base 0-15) |
|---|---|---|
| 1 | 141.61920773680384 | 16 (=-68), 17, 19, 28, 30 |
| 3 | 141.61920773680384 | 16 (=-68), 20, 22, 25, 27 |

**Finding:** State vectors differ meaningfully by gateway (the nonzero positions encode distinct zero-divisor structure), but `magnitude_256d` collapses to the same value. Partial dispatch — the state-construction branches on gateway, but the magnitude metric is gateway-invariant. Worth asking: **is magnitude invariance expected** (e.g., an orthogonality property of the canonical six), **or is this a second dispatch-collapse bug on a different metric**?

### 4.5 `detect_patterns` on Short Input — OBSERVATION

Input `[1.0, 2.5, 3.7, 4.2, 5.1, 6.8, 7.3, 8.9]` (8 elements) → `patterns_detected: []`. Likely a length/threshold issue (detector probably needs ≥16 or ≥N samples). Not a bug, but worth documenting the minimum input length for pattern detection.

---

## 5. Reproduction Snippets

### 5.1 Reproduce AIEX-505 (dispatch collapse)
```python
import asyncio
from cailculator_mcp.client import CailculatorClient  # hypothetical direct client

async def reproduce():
    client = CailculatorClient(api_key="<REDACTED>")
    data = [1.0, 2.5, 3.7, 4.2, 5.1, 6.8, 7.3, 8.9]
    results = []
    for pid in range(1, 7):
        r = await client.chavez_transform(data=data, pattern_id=pid)
        results.append((pid, r["transform_value"]))
    # Expected: 6 distinct values. Actual: all == 20.47681443694484
    assert len(set(v for _, v in results)) == 6, f"Dispatch collapse: {results}"
```

### 5.2 Reproduce the indexing mismatch
```python
# chavez_transform says pattern 1 is (e_1 + e_14) × (e_3 + e_12) = 0
# verify_bilateral_oracle requires these 0-indexed vectors to return true:
P = [0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0]  # positions 1, 14
Q = [0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0]  # positions 3, 12
# → is_bilateral_zero_divisor: true
```

---

## 6. Hypotheses for Gemini to Evaluate

Candidate root causes for the dispatch collapse, ranked by prior likelihood:

1. **Dispatcher calls into a single compute function without passing `pattern_id`.** The metadata is being stamped on the response object post-compute from a lookup table, while the compute call itself uses a hardcoded default pattern. Easy to verify: inspect the handler for `chavez_transform` and check whether `pattern_id` flows into the compute call or only into the response envelope.
2. **Compute path is correct, but the output is provably pattern-invariant under the current aggregation.** If the final scalar is something like `||transform(f, P_i, Q_i)||` and the norm happens to be invariant across the canonical six (by Weyl-orbit symmetry or similar), then collapse is a **feature, not a bug**, and the paper argument changes accordingly. This would be a significant theoretical finding. Gemini should check whether the canonical six are related by a Weyl group element that preserves the scalar output of the transform.
3. **v1.4.7 → v2.0 refactor introduced a feature flag** (e.g., `enable_pattern_dispatch`) that defaults off. Less likely given the metadata pass-through, but possible.
4. **Stability constant `M` not dimension-dependent** (§4.2 observation) is a separate issue that may indicate the bound formula needs revision, independent of dispatch.

---

## 7. Recommended Gemini Tasks

1. **Diff v1.4.7 → v2.0 → v2.0.1 source** for the `chavez_transform` handler and confirm whether `pattern_id` is passed through to the compute kernel.
2. **Theoretical check:** is the scalar `transform_value` **provably invariant** across the Canonical Six for a fixed input? If yes, the collapse is expected and the paper needs a different observable to demonstrate universality. If no, it's a bug.
3. **Re-test AIEX-506** (stability-bound violation at α=1.0, α=5.0 on baseline Gaussian) under v2.0.1 to see whether that regression is also still present.
4. **Flag the indexing-convention mismatch** (§4.3) for a docs fix and consider whether `verify_bilateral_oracle` should accept a convention flag.
5. **Explore ZDTP magnitude invariance** (§4.4): is `magnitude_256d` mathematically required to be gateway-invariant, or is this a second dispatch bug?

---

## 8. Open Questions for KSJ

- `?` Is the Canonical Six `transform_value` **mathematically required** to be invariant under the Weyl orbit, or should it differ?
- `?` Does the `M = 8/(α·e)` stability bound depend on `dimension_param`, and if so, how?
- `?` Should `chavez_transform` metadata strings be 0-indexed to match `verify_bilateral_oracle`?
- `?` Is `magnitude_256d` a gateway-invariant quantity by construction in ZDTP?

---

## 9. Session Artifacts

- **KSJ captures:** not yet committed. Awaiting Paul's approval before `extract_insights` → `commit_aiex`.
- **Proposed new tags:** `#cailculator-v2.0.1`, `#dispatch-collapse`, `#indexing-mismatch`
- **Proposed `!critical` flag** on the v2.0.1 regression insight

---

*End of handoff document.*
