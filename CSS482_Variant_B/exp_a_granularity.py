"""Experiment A - The Granularity Trap (chunksize=1 vs chunksize=10,000).
Run:  python exp_a_granularity.py          (full workload: 1,000,000 items)
      python exp_a_granularity.py --quick  (tiny smoke test, NOT valid for submission)"""
import sys, time, multiprocessing as mp
from multiprocessing import Pool
from bench_common import (Tee, print_env, env_info, speedup, efficiency,
                          karp_flatt, save_json)

WORKERS = [1, 2, 4, 8]
CHUNKS = [("Micro (k=1)", 1), ("Coarse (k=10,000)", 10_000)]


def collatz_steps(n):
    """Number of Collatz steps to reach 1 (pure-Python CPU work per item)."""
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers, total_items=1_000_000, chunk_size=1):
    numbers = range(1, total_items + 1)
    t0 = time.perf_counter()
    # chunk_size=1 -> one pickled IPC task envelope per number (micro-tasks)
    with Pool(processes=workers) as pool:
        results = pool.map(collatz_steps, numbers, chunksize=chunk_size)
    elapsed = time.perf_counter() - t0
    return elapsed, sum(results)


def main():
    quick = "--quick" in sys.argv
    total = 20_000 if quick else 1_000_000
    coarse = 200 if quick else 10_000
    chunks = [("Micro (k=1)", 1), ("Coarse (k=%s)" % format(coarse, ","), coarse)]
    out = Tee()
    env = print_env(out)
    if quick:
        out("*** QUICK SMOKE TEST - reduced workload, results NOT valid for submission ***\n")
    out(f"=== Experiment A: Granularity Trap | items={total:,} ===")
    rows, sums = [], set()
    for label, k in chunks:
        times = {}
        for p in WORKERS:
            try:
                t, s = run_granularity(p, total, k)
            except Exception as exc:  # report and abort cleanly
                out(f"ERROR in config {label}, P={p}: {exc!r}")
                raise
            times[p] = t
            sums.add(s)
            out(f"  finished {label:18s} P={p}  T={t:8.3f}s  sum={s:,}")
        t1 = times[1]  # separate baseline per chunk configuration
        for p in WORKERS:
            rows.append({
                "config": label, "chunk": k, "p": p, "time": times[p],
                "speedup": speedup(t1, times[p]),
                "efficiency": efficiency(t1, times[p], p),
                "karp_flatt": None if p == 1 else karp_flatt(t1, times[p], p)})
    out()
    hdr = f"{'Configuration':<20}{'P':>3}{'Runtime(s)':>12}{'Speedup':>10}{'Eff(%)':>9}{'Karp-Flatt':>12}"
    out(hdr); out("-" * len(hdr))
    for r in rows:
        kf = "     n/a" if r["karp_flatt"] is None else f"{r['karp_flatt']:12.4f}"
        out(f"{r['config']:<20}{r['p']:>3}{r['time']:>12.3f}{r['speedup']:>10.2f}{r['efficiency']:>9.1f}{kf:>12}")
    out()
    ok = len(sums) == 1
    out(f"Verification: all {len(WORKERS)*len(chunks)} runs produced the same Collatz step sum "
        f"({next(iter(sums)):,}) -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        out(f"  DIFFERENT SUMS: {sorted(sums)}")
    if not quick:
        out("Reference: sum of Collatz steps for n=1..1,000,000 is 131,434,424 -> "
            + ("PASS" if sums == {131_434_424} else "MISMATCH"))
    save_json("exp_a_results.json", {"env": env, "quick": quick, "total_items": total,
                                     "rows": rows, "sum": sorted(sums)[0], "verified": ok})
    if not quick:
        out.save("exp_a_output.txt")
        print("Saved outputs/exp_a_output.txt")


if __name__ == "__main__":
    mp.freeze_support()           # needed for frozen Windows executables; harmless otherwise
    mp.set_start_method("spawn")  # Windows default; forced so Linux/macOS behave the same
    main()
