"""Parametric Amdahl vs. Gustafson simulator (Task 21).

Example (from the repository root):
    python benchmarks/simulator.py --alpha 0.04 --max-processors 16384
    python benchmarks/simulator.py --alpha 0.01 0.04 0.1 --max-processors 65536
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmarks.models import (  # noqa: E402
    amdahl_efficiency, amdahl_speedup, gustafson_efficiency, gustafson_speedup,
)

MIN_P, MAX_P = 1, 65_536
MIN_ALPHA, MAX_ALPHA = 0.001, 0.20


def processor_counts(max_processors: int) -> list[int]:
    """Powers of two up to max_processors (max appended if not a power of two)."""
    if not MIN_P <= max_processors <= MAX_P:
        raise ValueError(f"max-processors must be in [{MIN_P}, {MAX_P}]")
    counts = [2 ** k for k in range(int(np.log2(max_processors)) + 1)]
    if counts[-1] != max_processors:
        counts.append(max_processors)
    return counts


def validate_alphas(alphas: list[float]) -> list[float]:
    for a in alphas:
        if not MIN_ALPHA <= a <= MAX_ALPHA:
            raise ValueError(f"alpha must be in [{MIN_ALPHA}, {MAX_ALPHA}], got {a}")
    return alphas


def simulate(alphas: list[float], max_processors: int) -> pd.DataFrame:
    """Return a tidy DataFrame with both models for every (alpha, P)."""
    ps = np.array(processor_counts(max_processors))
    frames = []
    for a in validate_alphas(alphas):
        frames.append(pd.DataFrame({
            "alpha": a, "P": ps,
            "gustafson_speedup": gustafson_speedup(ps, a),
            "gustafson_efficiency": gustafson_efficiency(ps, a),
            "amdahl_speedup": amdahl_speedup(ps, a),
            "amdahl_efficiency": amdahl_efficiency(ps, a),
        }))
    return pd.concat(frames, ignore_index=True)


def make_plots(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for kind, ylabel, fname, log_y in (
        ("speedup", "Speedup S(P)", "scaling_comparison_theory", True),
        ("efficiency", "Efficiency E(P)", "efficiency_comparison", False),
    ):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        for a, g in df.groupby("alpha"):
            ax.plot(g["P"], g[f"gustafson_{kind}"], "-o", ms=3, label=f"Gustafson α={a:g}")
            ax.plot(g["P"], g[f"amdahl_{kind}"], "--s", ms=3, label=f"Amdahl s={a:g}")
        if kind == "speedup":
            ps = np.sort(df["P"].unique())
            ax.plot(ps, ps, ":", color="gray", label="Ideal S=P")
        ax.set_xscale("log", base=2)
        if log_y:
            ax.set_yscale("log", base=2)
        ax.set_xlabel("Processors P")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Strong (Amdahl) vs. weak (Gustafson) scaling: {kind}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            path = out_dir / f"{fname}.{ext}"
            fig.savefig(path, dpi=200)
            written.append(path)
        plt.close(fig)
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--alpha", type=float, nargs="+", default=[0.04],
                   help="serial fraction(s), each in [0.001, 0.20]")
    p.add_argument("--max-processors", type=int, default=16384, help="max P in [1, 65536]")
    p.add_argument("--csv", type=Path, default=Path("benchmarks/simulator_output.csv"))
    p.add_argument("--plot-dir", type=Path, default=Path("plots"))
    p.add_argument("--no-plots", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        df = simulate(args.alpha, args.max_processors)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.csv, index=False)
    print(f"wrote {args.csv} ({len(df)} rows)")
    if not args.no_plots:
        for path in make_plots(df, args.plot_dir):
            print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
