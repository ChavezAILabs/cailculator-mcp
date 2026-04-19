# CAILculator MCP Server — Upgrade Handoff (v1.4.3 → v1.4.4)

**Date:** April 17, 2026 (amended April 18, 2026)
**Status:** Core Integration Complete / Surgical Audit Ongoing / `illustrate` Tool **REGRESSION
Repo:** `C:\\Users\\chave\\PROJECTS\\cailculator-mcp`

\---

## 1\. Mission Status

The integration of formally verified Chavez Transform results from `ChavezTransform\_genuine.lean` (April 2026) is **complete** for the core mathematical modules. The system is currently in a "Documentation \& Correctness" audit phase to ensure all stale references are removed before the v1.4.4 release.

**NEW (April 18):** The `illustrate` tool regression previously thought fixed has resurfaced in live MCP usage. See Section 6 below. Audit phase must now include a `illustrate` path-resolution fix before v1.4.4 can be released.

**DO NOT push to PyPI or Railway until explicitly instructed by Paul.**

\---

## 2\. Mathematical Integrity (Proved Results)

### Result 1 — Stability Constant

The stability constant $M$ has been updated from an empirical estimate to the proved tighter bound:

* **NEW (proved):** $M = 2\\cdot(|P|^2 + |Q|^2) / (\\alpha \\cdot e)$
* **Location:** `src/cailculator\_mcp/transforms.py` (Line 356)
* **Status:** Integrated.

### Result 2 — Parametric Domain

The integration domain $D = \[a, b]$ is now strictly defined as a **parametric choice**, not a mathematical constant of the transform.

* **Default:** `(-5.0, 5.0)` is maintained as the numerical default for implementation convenience.
* **Status:** Docstrings in `transforms.py` and `tools.py` updated to reflect this.

### Result 3 — Pattern Invariance (Theorem)

$K\_Z(P, Q, \\text{realToSed}(x)) = 2\\cdot x^2 \\cdot (|P|^2 + |Q|^2)$ is now a proved theorem.

* **Status:** Documented in `transforms.py`.

\---

## 3\. File Audit \& Integration Status

|File|Status|Key Changes|
|-|-|-|
|`transforms.py`|**UPDATED**|Proved stability constant, `verify\_stability\_bounds`, `stability\_constant()`, and domain notes.|
|`e8\_pathion\_bridge.py`|**UPDATED**|Formal verification note, 2-class partition finding logic.|
|`tools.py`|**AUDITED**|Updated `chavez\_transform` and `analyze\_dataset` wrappers to clarify parametric domain.|
|`illustrate` Tool|**REGRESSION (April 18)**|Fix no longer holding in live MCP environment — writes to `C:\\WINDOWS\\System32\\assets` and fails with `WinError 5`. See Section 6.|

\---

## 4\. `illustrate` Tool Verification (superseded by Section 6)

The fix as documented on April 17 was believed intact:

* **Save Path (intended):** `C:\\Users\\chave\\PROJECTS\\cailculator-mcp\\assets\\visualizations\\`
* **Verification (April 17):** The tool correctly mapped visualization types and used the updated `ChavezTransform` core.
* **Compatibility:** No direct dependencies on hardcoded constants; it pulls verified patterns dynamically.

**This section is superseded by Section 6 as of April 18, 2026.** The April 17 verification does not reflect behavior observed in live Claude Desktop MCP sessions.

\---

## 5\. Pending Tasks (Surgical Audit)

1. **OFFICIAL EQUATION:** Make sure the Lean definition of Chavez Transform is used throughout the MCP server architecture and in computations: 𝒞[f](P,Q,α,d) = ∫\_D f(x) · K\_Z(P,Q,x) · exp(-α‖x‖²) · Ω\_d(x) dx
2. **Surgical Refinement:** Final pass on `demo\_zdtp.py` to ensure parametric domain notation.
3. **Theorem Citation:** Add explicit `ChavezTransform\_genuine.lean` citations to `patterns.py` regarding Result 3.
4. **Validation:** Run one full `analyze\_dataset` pass to confirm $M$ bound compliance.
5. **NEW — `illustrate` path resolution:** Resolve the System32 write regression (Section 6) before v1.4.4 tag.

\---

## 6\. `illustrate` Tool Regression — WinError 5 Access Denied (NEW, April 18, 2026)

### 6.1 Symptom

During a live Claude Desktop MCP session on April 18, 2026, two consecutive `illustrate` calls failed identically:

* `visualization\_type: "alpha\_sensitivity"` (with `transform\_results` payload, `output\_format: "both"`, `style: "publication"`)
* `visualization\_type: "zero\_divisor\_network"` (with `dimension: 16, pattern\_id: 1`, `output\_format: "static"`, `style: "publication"`)

Both returned:

```json
{
  "success": false,
  "error": "\[WinError 5] Access is denied: 'C:\\\\\\\\WINDOWS\\\\\\\\System32\\\\\\\\assets'"
}
```

The other CAILculator tools in the same session (`chavez\_transform` at α=0.1, 1.0, 5.0) executed normally and returned correct transform values (2.006, 0.727, 0.184 respectively), so the regression is isolated to the `illustrate` tool's asset-path resolution — not a broader server failure.

### 6.2 Root Cause Hypothesis

The `illustrate` tool is resolving its assets directory against the **process current working directory** rather than the **repository root or an absolute configured path**. When the MCP server is launched by Claude Desktop, the CWD inherited is `C:\\WINDOWS\\System32` (the default for services spawned without an explicit working directory). The tool then attempts to create/write `.\\assets\\visualizations\\...`, which resolves to `C:\\WINDOWS\\System32\\assets\\...` — a protected system path. Windows correctly denies the write and raises `WinError 5`.

This is consistent with the April 17 verification passing: when the tool was tested from a shell already sitting in the repo root, the relative path resolved correctly. The regression is invisible from a manual test and only appears under Claude Desktop's launch context.

### 6.3 Recommended Fix (priority order)

1. **Absolute path from package location (preferred).** In the `illustrate` tool, compute the assets directory relative to `\_\_file\_\_`:

```python
   from pathlib import Path
   ASSETS\_DIR = Path(\_\_file\_\_).resolve().parent.parent.parent / "assets" / "visualizations"
   ASSETS\_DIR.mkdir(parents=True, exist\_ok=True)
   ```

   This makes the path independent of CWD and robust to any launch context.

2. **Environment variable override.** Support `CAILCULATOR\_ASSETS\_DIR` as an optional override so users on the USB-drive Mathlib-cache pattern (`LAKE\_HOME=D:\\.lake`) can relocate assets similarly:

   ```python
   ASSETS\_DIR = Path(os.environ.get("CAILCULATOR\_ASSETS\_DIR", default\_path)).resolve()
   ```

3. **User-space fallback.** If the computed path is unwritable (caught `PermissionError`), fall back to `Path.home() / ".cailculator" / "visualizations"` with a warning logged. This prevents total failure when a user has an unusual install layout.

   ### 6.4 Acceptance Criteria for v1.4.4 Release

* \[ ] `illustrate` succeeds with `visualization\_type: "alpha\_sensitivity"` in a Claude Desktop MCP session.
* \[ ] `illustrate` succeeds with `visualization\_type: "zero\_divisor\_network"` in the same context.
* \[ ] Assets land in the repo `assets/visualizations/` directory (or user-configured override) — **never** under `C:\\WINDOWS\\System32`.
* \[ ] Test added that spawns a subprocess with `cwd="C:\\\\WINDOWS\\\\System32"` and confirms `illustrate` still writes to the correct location. This test would have caught the regression.

  ### 6.5 Evidence

* Session: Claude Desktop, April 18, 2026 (Chavez Transform visualization request).
* Both failures were silent from the user's perspective — the MCP returned `success: false` but the tool did not surface a clear user-facing message about the path issue. Consider adding a path-mentioning error message in addition to the raw `OSError` passthrough.

  \---

  **Handoff Complete.** Gemini CLI is ready to resume surgical documentation updates or perform final validation — **with Section 6 now a release blocker**.









  claude --resume 743b4d84-c3a4-4b06-9d20-6c16787f6946

