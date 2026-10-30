"""Experiment B - Inter-process Queue choke-point (one put() per item).
Run:  python exp_b_queue.py          (full workload: 400,000 items)
      python exp_b_queue.py --quick  (smoke test, NOT valid for submission)"""
import sys, time, queue, multiprocessing as mp
from multiprocessing import Process, Queue
from bench_common import (Tee, print_env, speedup, karp_flatt, save_json)

WORKERS = [1, 2, 4, 8]


def queue_worker(out_queue, items_per_worker):
    for i in range(items_per_worker):
        # Pathological pattern: every single iteration crosses an IPC boundary
        out_queue.put(i % 7)


def run_queue_benchmark(p, total_items=400_000):
    q = Queue()
    base, extra = divmod(total_items, p)      # exact split, no items lost
    counts = [base + (1 if r < extra else 0) for r in range(p)]
    workers = [Process(target=queue_worker, args=(q, c)) for c in counts]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    collected, checksum = 0, 0
    try:
        while collected < total_items:        # master drains EVERY item (no deadlock)
            try:
                checksum += q.get(timeout=30)
                collected += 1
            except queue.Empty:
                if not any(w.is_alive() for w in workers):
                    raise RuntimeError(f"workers exited early, only {collected} items received")
    finally:
        for w in workers:
            w.join(timeout=60)
            if w.is_alive():
                w.terminate()
        t1 = time.perf_counter()
        q.close(); q.join_thread()            # release pipe + feeder-thread resources
    return t1 - t0, collected, checksum


def expected_checksum(total_items, p):
    base, extra = divmod(total_items, p)
    tot = 0
    for r in range(p):
        c = base + (1 if r < extra else 0)
        tot += sum(i % 7 for i in range(c))
    return tot


def main():
    quick = "--quick" in sys.argv
    total = 8_000 if quick else 400_000
    out = Tee()
    env = print_env(out)
    if quick:
        out("*** QUICK SMOKE TEST - reduced workload, results NOT valid for submission ***\n")
    out(f"=== Experiment B: Queue Contention | items={total:,} ===")
    times, ok_all = {}, True
    for p in WORKERS:
        t, n, chk = run_queue_benchmark(p, total)
        good = (n == total) and (chk == expected_checksum(total, p))
        ok_all &= good
        times[p] = t
        out(f"  P={p}: T={t:8.3f}s collected={n:,} checksum={chk:,} -> {'PASS' if good else 'FAIL'}")
    t1 = times[1]
    out("\n--- Queue Contention Karp-Flatt Analysis ---")
    hdr = f"{'P':>3}{'Runtime(s)':>12}{'Speedup':>10}{'vs T1':>10}{'Karp-Flatt':>12}"
    out(hdr); out("-" * len(hdr))
    rows = []
    for p in WORKERS:
        tp = times[p]
        kf = None if p == 1 else karp_flatt(t1, tp, p)
        rows.append({"p": p, "time": tp, "speedup": speedup(t1, tp),
                     "runtime_ratio": tp / t1, "karp_flatt": kf})
        kfs = "     n/a" if kf is None else f"{kf:12.3f}"
        out(f"{p:>3}{tp:>12.3f}{speedup(t1, tp):>10.2f}{tp / t1:>9.2f}x{kfs:>12}")
    mono = times[1] < times[2] < times[4] < times[8]
    out(f"\nVerification: collected == {total:,} for every P, checksums match -> {'PASS' if ok_all else 'FAIL'}")
    out(f"Runtime strictly increases with P (T1<T2<T4<T8)? {mono}")
    out(f"T8 > T1 (negative scaling)? {times[8] > t1}")
    save_json("exp_b_results.json", {"env": env, "quick": quick, "total_items": total,
                                     "rows": rows, "verified": bool(ok_all), "monotonic": mono})
    if not quick:
        out.save("exp_b_output.txt")
        print("Saved outputs/exp_b_output.txt")


if __name__ == "__main__":
    mp.freeze_support()
    mp.set_start_method("spawn")
    main()
