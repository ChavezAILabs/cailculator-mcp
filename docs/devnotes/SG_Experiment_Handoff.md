# Experiment SG-1: Sophie Germain Primes — Chavez Transform Analysis

## Handoff Document for Claude Desktop + CAILculator MCP

**Researcher:** Paul Chavez, Chavez AI Labs
**Date:** February 16, 2026
**Roadmap Reference:** Experiment 1.1 (Prime Number Variants), item #2

---

## Objective

Apply the Chavez Transform and ZDTP gateway analysis to Sophie Germain primes to determine:

1. Whether the universal constant CV ≈ 0.146 holds for this structurally constrained prime subset
2. Whether the double primality constraint (both p and 2p+1 prime) produces higher conjugation symmetry than general primes (78–86% baseline)
3. How Germain prime gaps compare to general prime gaps under the transform
4. Whether specific ZDTP gateways specialize in detecting the paired structure of Germain/safe primes

---

## Dataset Summary

Source: `Sophie Germain Primes from 1 to 100,000.xlsx`
Extraction script: `sg_extract.py` (already run, outputs verified)

| Dataset | File | Count | Range |
|---|---|---|---|
| Sophie Germain primes (p) | `sg_germain_primes.json` | 1,171 | 2 to 99,839 |
| Safe primes (2p+1) | `sg_safe_primes.json` | 1,171 | 5 to 199,679 |
| Germain prime gaps | `sg_germain_gaps.json` | 1,170 | 1 to 798 |
| Safe prime gaps | `sg_safe_gaps.json` | 1,170 | 2 to 1,596 |

Pre-computed statistics are in `sg_summary.json`.

Notable observation from extraction: the most common Germain prime gap is **30** (8.0%), unlike general primes where gap 6 dominates (20.2%). This likely reflects the mod-30 residue constraints on Sophie Germain primes.

---

## Analysis Steps

### Step 1: Chavez Transform — Sophie Germain Primes (p)

Load `sg_germain_primes.json` and run the Chavez Transform with these parameters:

- **alpha:** 1.0
- **dimension_param:** 2
- **pattern_id:** 1 (Canonical Six pattern)
- **dimensions:** 1, 2, 3, 4, 5

Record:
- Coefficient of variation (CV) — expecting ≈ 0.146
- Conjugation symmetry percentage — expecting > 80%
- Dimensional persistence confidence — expecting > 85%
- Transform values at each dimension (1–5)
- Convergence reduction percentage (dim 1 → dim 5) — expecting ~33%

### Step 2: Chavez Transform — Safe Primes (2p+1)

Load `sg_safe_primes.json` and run the identical analysis.

Key comparison: since safe primes = 2 × (Germain prime) + 1, the linear mapping should **preserve** dimensional persistence but may shift symmetry scores. Record any differences from Step 1.

### Step 3: Chavez Transform — Germain Prime Gaps

Load `sg_germain_gaps.json` and run the same analysis.

Context: Germain prime gaps are much larger and more variable than general prime gaps (mean 85.3 vs ~10.8 for general primes up to 100K). The question is whether the transform still detects structure despite this sparsity.

### Step 4: Chavez Transform — Safe Prime Gaps

Load `sg_safe_gaps.json` and run the same analysis.

Note: safe prime gaps = 2 × Germain gaps (by construction). This serves as a scaling control — CV and symmetry should be identical to Step 3 if the transform is scale-invariant.

### Step 5: ZDTP Six-Gateway Analysis — Sophie Germain Primes

Run all six ZDTP gateways on `sg_germain_primes.json`:

For each gateway (1 through 6), use dimensions [16, 32, 64]:
- Gateway 1 (Master)
- Gateway 2 (Multi-modal)
- Gateway 3 (Discontinuous)
- Gateway 4 (Diagonal)
- Gateway 5 (Orthogonal)
- Gateway 6 (Incremental)

Record convergence score for each gateway, then compute overall convergence.

Hypothesis: Discontinuous Gateway (#3) may give the strongest signal because Sophie Germain primes form a non-linear, irregularly spaced subsequence.

### Step 6: Baseline Comparison

Generate 1,171 random integers in the range [2, 99839] and run the Chavez Transform (same parameters). Record CV and symmetry as a noise baseline.

Expected: CV ≈ 0.146 (transform property), symmetry ≈ 64% (random baseline from previous experiments).

---

## Results Template

Please fill in this structure after each analysis:

```json
{
  "experiment_id": "EXP_SG_2026_001",
  "date": "2026-02-16",
  "analyses": {
    "germain_primes": {
      "dataset": "sg_germain_primes.json",
      "count": 1171,
      "chavez_transform": {
        "cv": null,
        "conjugation_symmetry": null,
        "dimensional_persistence": null,
        "transform_values": [null, null, null, null, null],
        "dimensions_tested": [1, 2, 3, 4, 5],
        "convergence_reduction_pct": null
      }
    },
    "safe_primes": {
      "dataset": "sg_safe_primes.json",
      "count": 1171,
      "chavez_transform": {
        "cv": null,
        "conjugation_symmetry": null,
        "dimensional_persistence": null,
        "transform_values": [null, null, null, null, null],
        "dimensions_tested": [1, 2, 3, 4, 5],
        "convergence_reduction_pct": null
      }
    },
    "germain_gaps": {
      "dataset": "sg_germain_gaps.json",
      "count": 1170,
      "chavez_transform": {
        "cv": null,
        "conjugation_symmetry": null,
        "dimensional_persistence": null,
        "transform_values": [null, null, null, null, null],
        "dimensions_tested": [1, 2, 3, 4, 5],
        "convergence_reduction_pct": null
      }
    },
    "safe_gaps": {
      "dataset": "sg_safe_gaps.json",
      "count": 1170,
      "chavez_transform": {
        "cv": null,
        "conjugation_symmetry": null,
        "dimensional_persistence": null,
        "transform_values": [null, null, null, null, null],
        "dimensions_tested": [1, 2, 3, 4, 5],
        "convergence_reduction_pct": null
      }
    },
    "zdtp_gateways": {
      "dataset": "sg_germain_primes.json",
      "gateway_convergence": {
        "master": null,
        "multimodal": null,
        "discontinuous": null,
        "diagonal": null,
        "orthogonal": null,
        "incremental": null
      },
      "overall_convergence": null,
      "convergence_classification": null
    },
    "random_baseline": {
      "count": 1171,
      "range": [2, 99839],
      "chavez_transform": {
        "cv": null,
        "conjugation_symmetry": null
      }
    }
  }
}
```

---

## Comparisons to Make After Analysis

### Table 1: CV Universality Check

| Dataset | CV | Deviation from 0.146 |
|---|---|---|
| General primes (prior result) | 0.146 | baseline |
| Sophie Germain primes (p) | ? | ? |
| Safe primes (2p+1) | ? | ? |
| Germain gaps | ? | ? |
| Safe gaps | ? | ? |

### Table 2: Conjugation Symmetry Hierarchy

| Dataset | Symmetry % | vs. General Primes (78–86%) |
|---|---|---|
| Sophie Germain primes (p) | ? | higher / same / lower? |
| Safe primes (2p+1) | ? | higher / same / lower? |
| Germain gaps | ? | higher / same / lower? |
| Powers of 2 (prior: 98%) | 98% | reference |
| Fibonacci (prior: 96.7%) | 96.7% | reference |
| Random data (prior: 64%) | 64% | baseline |

### Table 3: ZDTP Gateway Convergence (fill from Step 5)

| Gateway | Score | Strongest for SG primes? |
|---|---|---|
| Master | ? | |
| Multi-modal | ? | |
| Discontinuous | ? | |
| Diagonal | ? | |
| Orthogonal | ? | |
| Incremental | ? | |

---

## Key Questions to Answer

1. **Does CV ≈ 0.146 hold?** If yes, this extends the universality claim to structurally constrained prime subsets.

2. **Is symmetry > 86%?** If Sophie Germain primes show higher symmetry than general primes, the double primality constraint adds detectable algebraic structure.

3. **Are Germain gaps and safe gaps identical under the transform?** They should be (safe gaps = 2 × Germain gaps), confirming scale invariance.

4. **Which ZDTP gateway dominates?** If Discontinuous (#3) leads, it validates the roadmap hypothesis about non-linear sequence detection.

5. **Does the gap-30 dominance (vs. gap-6 for general primes) show up in the transform?** The mod-30 constraint on Sophie Germain primes is a known number-theoretic property — does the transform detect it?

---

## Files in This Directory

| File | Purpose |
|---|---|
| `Sophie Germain Primes from 1 to 100,000.xlsx` | Raw source data |
| `sg_extract.py` | Extraction script (already run) |
| `sg_germain_primes.json` | Dataset: 1,171 Germain primes |
| `sg_safe_primes.json` | Dataset: 1,171 safe primes |
| `sg_germain_gaps.json` | Dataset: 1,170 Germain prime gaps |
| `sg_safe_gaps.json` | Dataset: 1,170 safe prime gaps |
| `sg_summary.json` | Pre-computed statistics |
| `SG_Experiment_Handoff.md` | This document |
| `Experimental_Roadmap.md` | Full research roadmap |
| `CLAUDE.md` | Repository guidance for Claude Code |
