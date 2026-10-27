"""
Generates the small, seeded input datasets used by the golden suite.

These are synthetic, public-domain-style series shaped like real reporting and
market data. They are committed to the repo; this script exists so anyone can
see exactly how they were made and regenerate them bit-for-bit.

    python tests/golden/data/generate_data.py

Do not regenerate casually: case files pin input hashes derived from these
values, so any change here must go through the golden change policy
(tests/golden/README.md).
"""

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent


def _round(values, digits=2):
    return [round(float(v), digits) for v in values]


def politics_contributions():
    """Monthly itemized contributions ($) to a House campaign, 48 months.

    Two-year cycle that ramps toward each election month, with bumps in
    quarter-end months (filing deadlines) and lognormal noise.
    """
    rng = np.random.default_rng(20260922)
    months = np.arange(48)
    cycle_pos = months % 24                      # 0..23, election at 22
    ramp = 40_000 + 9_000 * cycle_pos
    quarter_end = np.where(months % 3 == 2, 1.35, 1.0)
    noise = rng.lognormal(mean=0.0, sigma=0.12, size=48)
    return _round(ramp * quarter_end * noise)


def public_health_violations():
    """Monthly critical food-safety violations found by inspectors, 48 months.

    Summer peak (warm-weather seasonality) around a stable base, Poisson counts.
    """
    rng = np.random.default_rng(20260923)
    months = np.arange(48)
    expected = 120 + 25 * np.sin(2 * np.pi * (months - 3) / 12)
    return [float(v) for v in rng.poisson(expected)]


def poverty_snap_enrollment():
    """Monthly SNAP household enrollment (thousands), 60 months.

    Stable base, a step up at month 24 (downturn), then slow decay back.
    """
    rng = np.random.default_rng(20260924)
    months = np.arange(60)
    step = np.where(months >= 24, 45 * np.exp(-(months - 24) / 18.0), 0.0)
    return _round(410 + step + rng.normal(0, 3.0, size=60))


def quant_prices():
    """Daily close prices, 60 days, geometric Brownian motion."""
    rng = np.random.default_rng(20260925)
    returns = rng.normal(0.0004, 0.012, size=60)
    return _round(100 * np.exp(np.cumsum(returns)))


def shuffled(values, seed):
    rng = np.random.default_rng(seed)
    out = list(values)
    rng.shuffle(out)
    return out


def main():
    politics = politics_contributions()
    health = public_health_violations()
    poverty = poverty_snap_enrollment()

    datasets = {
        "journalism_politics_contributions.json": politics,
        "journalism_public_health_violations.json": health,
        "journalism_poverty_snap_enrollment.json": poverty,
        "null_constant.json": [250.0] * 48,
        "null_noise_seed1234.json": _round(np.random.default_rng(1234).normal(250, 25, size=48)),
        "null_linear_trend.json": _round(100 + 3.5 * np.arange(48)),
        "null_shuffled_politics.json": shuffled(politics, 7),
        "null_shuffled_public_health.json": shuffled(health, 7),
        "null_shuffled_poverty.json": shuffled(poverty, 7),
        "quant_prices_gbm.json": quant_prices(),
    }
    for name, values in datasets.items():
        (OUT / name).write_text(json.dumps(values) + "\n", encoding="utf-8")
        print(f"wrote {name} ({len(values)} points)")


if __name__ == "__main__":
    main()
