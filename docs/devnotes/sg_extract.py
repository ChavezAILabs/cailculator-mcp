"""
Sophie Germain Primes — Data Extraction & Preparation
======================================================
Extracts data from the xlsx file and produces JSON datasets
ready for Chavez Transform analysis via CAILculator MCP.

Outputs:
  sg_germain_primes.json   — The p values (Sophie Germain primes)
  sg_safe_primes.json      — The 2p+1 values (safe primes)
  sg_germain_gaps.json     — Gaps between consecutive Germain primes
  sg_safe_gaps.json        — Gaps between consecutive safe primes
  sg_summary.json          — Combined summary with basic statistics

Usage:
  python sg_extract.py
"""

import json
import math
import openpyxl

XLSX_PATH = "Sophie Germain Primes from 1 to 100,000.xlsx"
DATA_START_ROW = 4  # Row index 3 in 0-based (row 4 in Excel: first data row)


def extract_from_xlsx(path):
    """Read Sophie Germain primes and safe primes from the xlsx file."""
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb["Sheet1"]

    germain_primes = []
    safe_primes = []

    for row in ws.iter_rows(values_only=True):
        p, sp = row[0], row[1]
        # Skip header rows, section dividers, and blanks
        if p is None or isinstance(p, str):
            continue
        germain_primes.append(int(p))
        safe_primes.append(int(sp))

    wb.close()
    return germain_primes, safe_primes


def compute_gaps(sequence):
    """Compute consecutive gaps in a sequence."""
    return [sequence[i + 1] - sequence[i] for i in range(len(sequence) - 1)]


def basic_stats(values, label):
    """Compute basic descriptive statistics for a sequence."""
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std = math.sqrt(variance)
    return {
        "label": label,
        "count": n,
        "min": min(values),
        "max": max(values),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "cv": round(std / mean, 6) if mean != 0 else None,
    }


def write_json(data, filename):
    """Write data to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Written: {filename} ({len(data) if isinstance(data, list) else 'summary'})")


def main():
    print("=" * 60)
    print("Sophie Germain Primes — Data Extraction")
    print("=" * 60)

    # --- Extract ---
    germain, safe = extract_from_xlsx(XLSX_PATH)
    print(f"\nExtracted {len(germain)} Sophie Germain primes from xlsx")
    print(f"  Range of p:    {germain[0]} to {germain[-1]}")
    print(f"  Range of 2p+1: {safe[0]} to {safe[-1]}")

    # --- Compute gaps ---
    germain_gaps = compute_gaps(germain)
    safe_gaps = compute_gaps(safe)

    # --- Statistics ---
    stats = {
        "germain_primes": basic_stats(germain, "Sophie Germain primes (p)"),
        "safe_primes": basic_stats(safe, "Safe primes (2p+1)"),
        "germain_gaps": basic_stats(germain_gaps, "Gaps between consecutive Germain primes"),
        "safe_gaps": basic_stats(safe_gaps, "Gaps between consecutive safe primes"),
    }

    print("\n--- Basic Statistics ---")
    for key, s in stats.items():
        print(f"  {s['label']}: n={s['count']}, range=[{s['min']}, {s['max']}], "
              f"mean={s['mean']}, std={s['std']}")

    # --- Gap distribution for Germain primes ---
    gap_freq = {}
    for g in germain_gaps:
        gap_freq[g] = gap_freq.get(g, 0) + 1
    top_gaps = sorted(gap_freq.items(), key=lambda x: -x[1])[:10]

    print("\n--- Top 10 Most Common Germain Prime Gaps ---")
    for gap, count in top_gaps:
        print(f"  Gap {gap:>4d}: {count:>4d} occurrences ({100*count/len(germain_gaps):.1f}%)")

    # --- Write outputs ---
    print("\n--- Writing JSON files ---")
    write_json(germain, "sg_germain_primes.json")
    write_json(safe, "sg_safe_primes.json")
    write_json(germain_gaps, "sg_germain_gaps.json")
    write_json(safe_gaps, "sg_safe_gaps.json")

    summary = {
        "experiment_id": "EXP_SG_2026_001",
        "date": "2026-02-16",
        "source_file": XLSX_PATH,
        "description": "Sophie Germain primes (p where both p and 2p+1 are prime)",
        "datasets": stats,
        "germain_gap_distribution_top10": {str(g): c for g, c in top_gaps},
    }
    write_json(summary, "sg_summary.json")

    print("\n" + "=" * 60)
    print("Done. JSON files are ready for CAILculator MCP analysis.")
    print("=" * 60)


if __name__ == "__main__":
    main()
