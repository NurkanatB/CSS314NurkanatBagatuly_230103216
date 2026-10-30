import multiprocessing as mp, ctypes, time, statistics, os, argparse

PS = [1, 2, 4, 8]
LINE_INTS = 8  # 64 bytes / 8 bytes
MODES = ["unpadded", "padded", "privatized"]

def cpu_plan():
    """Logical CPU order: one thread per physical core first, SMT siblings last.
    Assumes siblings are adjacent (0,1),(2,3),... as on Windows."""
    try:
        import psutil
        logical = psutil.cpu_count(logical=True)
        phys = psutil.cpu_count(logical=False) or logical
    except ImportError:
        return None
    if logical == phys:
        return list(range(logical))
    return [2 * i for i in range(phys)] + [2 * i + 1 for i in range(phys)]

def worker(arr, idx, K, mode, bar, cpu):
    if cpu is not None:
        try:
            import psutil
            psutil.Process().cpu_affinity([cpu])
        except Exception:
            pass
    bar.wait()
    if mode == "privatized":
        local = 0
        for _ in range(K):
            local += 1
        arr[idx] = local            # single write
    else:
        for _ in range(K):
            arr[idx] += 1           # hammer the shared slot

def run(mode, P, K, ctx, plan):
    arr = ctx.RawArray(ctypes.c_int64, 8 + 8 * 8 + 8)
    addr = ctypes.addressof(arr)
    base = ((-addr) % 64) // 8                      # first index on a 64B boundary
    stride = 1 if mode == "unpadded" else LINE_INTS
    cpus = [plan[p % len(plan)] for p in range(P)] if plan else [None] * P
    bar = ctx.Barrier(P + 1)
    procs = [ctx.Process(target=worker, args=(arr, base + p * stride, K, mode, bar, cpus[p]))
             for p in range(P)]
    for pr in procs: pr.start()
    bar.wait()
    t0 = time.perf_counter()
    for pr in procs: pr.join()
    t = time.perf_counter() - t0
    total = sum(arr[base + p * stride] for p in range(P))
    return t, total

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5_000_000)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--no-affinity", action="store_true")
    a = ap.parse_args()
    K = a.k
    plan = None if a.no_affinity else cpu_plan()
    print("CPU affinity plan:", plan)
    ctx = mp.get_context()
    times = {(m, P): [] for m in MODES for P in PS}
    exact = {(m, P): True for m in MODES for P in PS}
    totals = {}
    for r in range(a.repeats):                     # interleave variants to cancel drift
        for P in PS:
            for m in MODES:
                t, total = run(m, P, K, ctx, plan)
                times[(m, P)].append(t)
                totals[(m, P)] = total
                exact[(m, P)] &= (total == P * K)
        print(f"repeat {r + 1}/{a.repeats} done")
    rows, T1 = [], {m: statistics.median(times[(m, 1)]) for m in MODES}
    for m in MODES:
        for P in PS:
            T = statistics.median(times[(m, P)])
            S = T1[m] / T
            e = (P * T / T1[m] - 1) / (P - 1) if P > 1 else float("nan")
            rows.append((m, P, K, T, S, S / P * 100, e, totals[(m, P)], P * K, exact[(m, P)]))
            print(f"{m:10s} P={P} T={T:7.3f}s S={S:5.2f} e={e:7.4f} total={totals[(m, P)]} ok={exact[(m, P)]}")
    print(f"sanity: unpadded/padded T1 ratio = {T1['unpadded'] / T1['padded']:.2f} (should be ~1.0)")
    os.makedirs("results", exist_ok=True)
    by = {(r[0], r[1]): r for r in rows}
    cols = (["P", "K"] + [f"T_{m}_s" for m in MODES] + [f"S_{m}" for m in MODES] + [f"e_{m}" for m in MODES]
            + [f"total_{m}" for m in MODES] + ["expected_total", "exact"])
    with open("results/false_sharing_karp_flatt.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for P in PS:
            g = lambda m: by[(m, P)]
            vals = ([P, K] + [f"{g(m)[3]:.6f}" for m in MODES] + [f"{g(m)[4]:.4f}" for m in MODES]
                    + [f"{g(m)[6]:.6f}" for m in MODES] + [g(m)[7] for m in MODES]
                    + [P * K, all(g(m)[9] for m in MODES)])
            f.write("\t".join(str(v) for v in vals) + "\n")

if __name__ == "__main__":
    main()
