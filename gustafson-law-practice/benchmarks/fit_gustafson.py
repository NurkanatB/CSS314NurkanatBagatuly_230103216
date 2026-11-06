"""Regression of measured scaled speedup against Gustafson's law (Task 23) + plot (Task 24).

Run the benchmark first (writes benchmarks/results.csv), then:
    python benchmarks/fit_gustafson.py
Weak scaling with constant work per worker: S(P) = P * T(1) / T(P).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmarks.models import amdahl_speedup, gustafson_speedup  # noqa: E402


def summarize(raw: pd.DataFrame) -> pd.DataFrame:
    """Per-configuration mean/std of runtime and derived scaled speedup with errors."""
    g = raw.groupby("workers")["wall_seconds"]
    out = g.agg(["mean", "std", "count"]).rename(columns={"mean": "t_mean", "std": "t_std", "count": "n"})
    t1 = out.loc[1, "t_mean"]
    out["speedup"] = out.index.to_numpy() * t1 / out["t_mean"]
    rel1 = out.loc[1, "t_std"] / t1 if out.loc[1, "n"] > 1 else 0.0
    rel = (out["t_std"] / out["t_mean"]).fillna(0.0)
    out["speedup_std"] = out["speedup"] * np.sqrt(rel ** 2 + rel1 ** 2)  # first-order propagation
    out["speedup_sem"] = out["speedup_std"] / np.sqrt(out["n"])
    return out.reset_index()


def fit_alpha(p: np.ndarray, speedup: np.ndarray) -> dict:
    """OLS through the origin of (S-1) on (P-1): slope = 1 - alpha."""
    x, y = p - 1.0, speedup - 1.0
    keep = x > 0
    x, y = x[keep], y[keep]
    if len(x) < 1:
        raise ValueError("need at least one configuration with P > 1")
    slope = float(np.sum(x * y) / np.sum(x * x))
    resid = y - slope * x
    dof = max(len(x) - 1, 1)
    se = float(np.sqrt(np.sum(resid ** 2) / dof / np.sum(x * x)))
    sst = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum(resid ** 2)) / sst if sst > 0 and len(x) > 1 else float("nan")
    return {"slope": slope, "slope_se": se, "alpha": 1.0 - slope, "r2": r2, "n_points": len(x)}


def make_plot(summary: pd.DataFrame, fit: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    p = summary["workers"].to_numpy(dtype=float)
    grid = np.linspace(1, max(p.max(), 2), 200)
    alpha = min(max(fit["alpha"], 0.0), 1.0)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(grid, grid, ":", color="gray", label="Ideal S = P")
    ax.plot(grid, gustafson_speedup(grid, alpha), "-", label=f"Gustafson fit (α={fit['alpha']:.3f})")
    ax.plot(grid, amdahl_speedup(grid, alpha), "--", label=f"Amdahl, same s={alpha:.3f}")
    ax.errorbar(p, summary["speedup"], yerr=summary["speedup_sem"], fmt="o", capsize=3,
                color="k", label="Measured (± std. error)")
    ax.set_xlabel("Workers P")
    ax.set_ylabel("Scaled speedup S(P) = P·T(1)/T(P)")
    ax.set_title("Empirical weak scaling vs. models")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    for name in ("weak_scaling_results.png", "scaling_comparison.png", "scaling_comparison.pdf"):
        fig.savefig(out_dir / name, dpi=200)
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, default=Path("benchmarks/results.csv"))
    ap.add_argument("--plot-dir", type=Path, default=Path("plots"))
    args = ap.parse_args(argv)
    if not args.results.exists():
        print(f"error: {args.results} not found; run the benchmark first", file=sys.stderr)
        return 2
    raw = pd.read_csv(args.results)
    if raw["workers"].nunique() < 5:
        print("warning: fewer than 5 worker configurations in the data", file=sys.stderr)
    summary = summarize(raw)
    print(summary.to_string(index=False))
    fit = fit_alpha(summary["workers"].to_numpy(dtype=float), summary["speedup"].to_numpy())
    print("\nFit S = 1 + (1-alpha)(P-1), OLS through origin on (S-1) vs (P-1):")
    for k, v in fit.items():
        print(f"  {k}: {v}")
    summary.to_csv(args.results.with_name("results_summary.csv"), index=False)
    make_plot(summary, fit, args.plot_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
