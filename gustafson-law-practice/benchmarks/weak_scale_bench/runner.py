"""Weak-scaling harness: samples per worker fixed, worker count varies.

Usage (repository root, Windows and Linux):
    python -m benchmarks.weak_scale_bench.runner --samples-per-worker 20000000 \
        --workers 1 2 4 8 16 --repetitions 5 --out benchmarks/results.csv
"""
from __future__ import annotations

import argparse
import csv
import math
import multiprocessing as mp
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks.weak_scale_bench.workload import count_hits, estimate_pi, pi_tolerance


def detect_cpu_count() -> int:
    """Logical CPUs available to this process (respects affinity where supported)."""
    if hasattr(os, "sched_getaffinity"):
        return len(os.sched_getaffinity(0))
    return os.cpu_count() or 1


def run_once(workers: int, samples_per_worker: int, base_seed: int) -> tuple[float, float]:
    """One weak-scaling measurement; returns (wall_seconds, pi_estimate).

    The pool is created and warmed up before the timer starts, so process start-up
    (large on Windows 'spawn') is excluded from the measured compute time.
    """
    seeds = [base_seed + i for i in range(workers)]
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn")) as pool:
        list(pool.map(count_hits, [1000] * workers, seeds))  # warm-up
        t0 = time.perf_counter()
        hits = list(pool.map(count_hits, [samples_per_worker] * workers, seeds))
        elapsed = time.perf_counter() - t0
    total = samples_per_worker * workers
    est = estimate_pi(sum(hits), total)
    if abs(est - math.pi) > pi_tolerance(total):
        raise RuntimeError(f"correctness check failed: pi estimate {est}")
    return elapsed, est


def run_suite(worker_counts: list[int], samples_per_worker: int, repetitions: int,
              out_csv: Path) -> list[dict]:
    rows: list[dict] = []
    for w in worker_counts:
        for rep in range(repetitions):
            elapsed, est = run_once(w, samples_per_worker, base_seed=1000 * rep + 7)
            rows.append({"workers": w, "repetition": rep, "samples_per_worker": samples_per_worker,
                         "wall_seconds": elapsed, "pi_estimate": est})
            print(f"workers={w} rep={rep} t={elapsed:.4f}s pi={est:.5f}", flush=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def default_worker_counts(cpus: int) -> list[int]:
    """Powers of two up to the CPU count, plus the CPU count itself."""
    counts = {2 ** k for k in range(0, 8) if 2 ** k <= max(cpus, 1)}
    counts.add(max(cpus, 1))
    return sorted(counts)


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--samples-per-worker", type=int, default=20_000_000)
    p.add_argument("--workers", type=int, nargs="+", default=None,
                   help="worker counts (default: powers of two up to detected CPUs)")
    p.add_argument("--repetitions", type=int, default=5)
    p.add_argument("--out", type=Path, default=Path("benchmarks/results.csv"))
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    cpus = detect_cpu_count()
    workers = args.workers or default_worker_counts(cpus)
    print(f"detected logical CPUs: {cpus}; worker counts: {workers}")
    if len(workers) < 5:
        print("note: fewer than 5 worker configurations; pass --workers explicitly "
              "(counts above the CPU count are oversubscribed and distort results)", file=sys.stderr)
    if 1 not in workers:
        print("error: worker count 1 is required as the baseline", file=sys.stderr)
        return 2
    run_suite(workers, args.samples_per_worker, args.repetitions, args.out)
    return 0


if __name__ == "__main__":  # required for 'spawn' on Windows
    mp.freeze_support()
    raise SystemExit(main())
