"""Experiment C - Local buffer chunking (batch size 10,000, None sentinel).
Run:  python exp_c_buffered.py          (full workload: 10,000,000 items)
      python exp_c_buffered.py --quick  (smoke test, NOT valid for submission)"""
import sys, time, queue, multiprocessing as mp
from multiprocessing import Process, Queue
from bench_common import (Tee, print_env, speedup, efficiency, karp_flatt, save_json)

WORKERS = [1, 2, 4, 8]


def buffered_worker(out_queue, items_per_worker, batch_size=10_000):
    buffer = []
    for i in range(items_per_worker):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))   # one IPC message per 10,000 items
            buffer.clear()
    if buffer:                           # final partial batch
        out_queue.put(sum(buffer))
    out_queue.put(None)                  # sentinel: this worker is done


def run_buffered(p, total_items=10_000_000, batch_size=10_000):
    q = Queue()
    base, extra = divmod(total_items, p)
    counts = [base + (1 if r < extra else 0) for r in range(p)]
    workers = [Process(target=buffered_worker, args=(q, c, batch_size)) for c in counts]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    total_sum, active = 0, p
    try:
        while active > 0:
            try:
                val = q.get(timeout=60)
            except queue.Empty:
                if not any(w.is_alive() for w in workers):
                    raise RuntimeError("workers exited before sending all sentinels")
                continue
            if val is None:
                active -= 1
            else:
                total_sum += val
    finally:
        for w in workers:
            w.join(timeout=60)
            if w.is_alive():
                w.terminate()
        t1 = time.perf_counter()
        q.close(); q.join_thread()
    return t1 - t0, total_sum


def expected_sum(total_items, p):
    """Closed form: each worker sums i%7 for i in range(count)."""
    base, extra = divmod(total_items, p)
    tot = 0
    for r in range(p):
        c = base + (1 if r < extra else 0)
        full, rem = divmod(c, 7)
        tot += full * 21 + sum(range(rem))   # 0+1+...+6 = 21 per full cycle
    return tot


def main():
    quick = "--quick" in sys.argv
    total = 200_000 if quick else 10_000_000
    out = Tee()
    env = print_env(out)
    if quick:
        out("*** QUICK SMOKE TEST - reduced workload, results NOT valid for submission ***\n")
    out(f"=== Experiment C: Buffered Batches | items={total:,} batch=10,000 ===")
    times, ok_all = {}, True
    for p in WORKERS:
        t, s = run_buffered(p, total)
        exp = expected_sum(total, p)
        good = s == exp
        ok_all &= good
        times[p] = t
        out(f"  P={p}: T={t:8.3f}s sum={s:,} expected={exp:,} -> {'PASS' if good else 'FAIL'}")
    t1 = times[1]
    out()
    hdr = f"{'P':>3}{'Runtime(s)':>12}{'Speedup':>10}{'Eff(%)':>9}{'Karp-Flatt':>12}"
    out(hdr); out("-" * len(hdr))
    rows = []
    for p in WORKERS:
        tp = times[p]
        kf = None if p == 1 else karp_flatt(t1, tp, p)
        rows.append({"p": p, "time": tp, "speedup": speedup(t1, tp),
                     "efficiency": efficiency(t1, tp, p), "karp_flatt": kf})
        kfs = "     n/a" if kf is None else f"{kf:12.4f}"
        out(f"{p:>3}{tp:>12.3f}{speedup(t1, tp):>10.2f}{efficiency(t1, tp, p):>9.1f}{kfs:>12}")
    out(f"\nVerification: every total equals the closed-form expected sum -> {'PASS' if ok_all else 'FAIL'}")
    save_json("exp_c_results.json", {"env": env, "quick": quick, "total_items": total,
                                     "rows": rows, "verified": bool(ok_all)})
    if not quick:
        out.save("exp_c_output.txt")
        print("Saved outputs/exp_c_output.txt")


if __name__ == "__main__":
    mp.freeze_support()
    mp.set_start_method("spawn")
    main()
