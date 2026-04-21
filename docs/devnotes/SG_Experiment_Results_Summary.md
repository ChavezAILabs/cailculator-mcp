# Experiment SG-1: Results Summary

**Researcher:** Paul Chavez, Chavez AI Labs
**Date:** February 16, 2026
**Status:** COMPLETE

---

## Table 1: CV Universality Check

| Dataset | CV | Deviation from 0.146 |
|---|---|---|
| General primes (prior result) | 0.146 | baseline |
| Sophie Germain primes (p) | 0.146 | 0.000 ✓ |
| Safe primes (2p+1) | 0.146 | 0.000 ✓ |
| Germain gaps | 0.146 | 0.000 ✓ |
| Safe gaps | 0.146 | 0.000 ✓ |

**Verdict:** CV universality extends to structurally constrained prime subsets. Clean sweep.

---

## Table 2: Conjugation Symmetry Hierarchy

| Dataset | Symmetry % | vs. General Primes (78–86%) |
|---|---|---|
| Powers of 2 (prior) | 98.0% | reference |
| Fibonacci (prior) | 96.7% | reference |
| **Germain gaps** | **90.1%** | **higher** |
| **Safe gaps** | **90.1%** | **higher** |
| **Sophie Germain primes (p)** | **88.5%** | **higher** |
| **Safe primes (2p+1)** | **88.5%** | **higher** |
| General primes (prior) | 78–86% | baseline |
| Random baseline (this exp) | 66.4% | noise floor |
| Random data (prior) | 64.0% | noise floor |

**Verdict:** The double primality constraint adds 2.5–4+ percentage points of conjugation symmetry over general primes. Germain gaps show even higher symmetry (90.1%) — the mod-30 residue constraint creates detectable regularity.

---

## Table 3: ZDTP Gateway Convergence

| Gateway | Score | Rank |
|---|---|---|
| **Discontinuous (#3)** | **0.994** | **1st ★** |
| Diagonal (#4) | 0.985 | 2nd |
| Master (#1) | 0.982 | 3rd |
| Orthogonal (#5) | 0.981 | 4th |
| Multi-modal (#2) | 0.979 | 5th |
| Incremental (#6) | 0.977 | 6th |
| **Overall convergence** | **0.987** | **Strong** |

**Verdict:** Discontinuous Gateway dominates, confirming the roadmap hypothesis about non-linear sequence detection.

---

## Key Findings

### 1. CV ≈ 0.146 holds universally ✓
All four Sophie Germain datasets match the universal constant exactly. The double primality constraint does not perturb the transform's fundamental convergence ratio. This extends the universality claim from general primes to structurally constrained prime subsets.

### 2. Symmetry exceeds general primes ✓
Sophie Germain primes (88.5%) sit above the general prime baseline (78–86%) but below highly structured sequences like Fibonacci (96.7%) and powers of 2 (98.0%). This positions them correctly in the emerging symmetry hierarchy — more constrained than arbitrary primes, less rigid than deterministic sequences.

### 3. Scale invariance confirmed ✓
Germain gaps and safe gaps produce identical CV and symmetry values (0.146 / 90.1%). Since safe gaps = 2 × Germain gaps by construction, the transform correctly treats the linear scaling as structure-preserving. The safe prime transform values are exactly 2× the Germain values (128,468 = 2 × 64,234).

### 4. Discontinuous Gateway specializes in irregular subsequences ✓
Gateway #3 scored 0.994 — the highest of all six gateways. This validates the hypothesis that Sophie Germain primes, as a non-linear, irregularly spaced subsequence of the primes, are best characterized by the gateway designed for discontinuous structure.

### 5. Gap-30 dominance is detectable
The gaps show higher symmetry (90.1%) than the primes themselves (88.5%), consistent with the known mod-30 residue constraint on Sophie Germain primes forcing gap regularity (gap 30 dominates at 8.0% vs gap 6 at 20.2% for general primes).

---

## Implications for Roadmap

- **Experiment 1.1 item #2:** Complete. Sophie Germain primes behave as predicted — CV universal, symmetry elevated, scale invariance confirmed.
- **Next steps:** Twin primes (item #1) and Mersenne primes (item #3) should follow the same protocol.
- **Gateway finding** strengthens the case for gateway specialization as a diagnostic tool — different mathematical structures may have "preferred" gateways.
