# Changelog

All notable changes to the CAILculator MCP Server will be documented in this file.

## [1.4.4] - 2026-04-17

### 🏆 THE FORMAL VERIFICATION MILESTONE
This release marks the transition of CAILculator from an empirical research project to a **formally verified** mathematical library. Core algebraic properties and transform behaviors are now backed by machine-verified Lean 4 proofs.

### Added
- **Formal Proofs**: Integrated `lean/ChavezTransform_genuine.lean` containing zero-sorry proofs for:
  - **Theorem 1 (Convergence)**: Unconditional absolute convergence for the Chavez Transform kernel.
  - **Theorem 2 (Stability)**: Proved tighter stability bound $M = 2 \cdot (\|P\|^2 + \|Q\|^2) / (\alpha \cdot e)$.
  - **Theorem 3 (Pattern Invariance)**: Proved that patterns identified on scalar inputs scale predictably to high-dimensional spaces.
- **Pattern Detector Theorem Citation**: Added explicit citations to `src/cailculator_mcp/patterns.py` linking code implementation to Lean proofs.
- **Parametric Domain Notation**: Updated `demo_zdtp.py` to reflect the parametric nature of the integration domain $D$.

### Changed
- **Stability Constant Implementation**: Updated `src/cailculator_mcp/transforms.py` to use the tighter, formally proved constant $M$ instead of earlier empirical estimates.
- **Documentation Overhaul**: Main `README.md` now features the "Badge of Honor" Lean verification section.
- **Sanitization**: Moved internal development artifacts and session payloads to `docs/devnotes/` to provide a cleaner public repository structure.

### Fixed
- **Clifford Integration**: Verified and tested `CliffordElement` multiplication logic to ensure 100% parity with formal bridge patterns.
- **Illustrate Tool**: Confirmed path resolution and visualization generation for Windows/Linux compatibility.

---
**Chavez AI Labs** - *"Better math, less suffering"*
