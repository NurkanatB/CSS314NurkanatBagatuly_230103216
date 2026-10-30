import multiprocessing as mp, ctypes, time, statistics, os, json

K = 5_000_000
PS = [1, 2, 4, 8]
REPEATS = 3
LINE_INTS = 8  # 64 bytes / 8 bytes

def worker(arr, idx, K, mode, bar):
    bar.wait()
    if mode == "privatized":
        local = 0
        for _ in range(K):
            local += 1
        arr[idx] = local            # single write
    else:
        for _ in range(K):
            arr[idx] += 1           # unpadded/padded: hammer the shared slot

def run(mode, P, ctx):
    arr = ctx.RawArray(ctypes.c_int64, 8 + 8 * 8 + 8)   # lock-free; extra room for alignment
    addr = ctypes.addressof(arr)
    base = ((-addr) % 64) // 8                           # first index on a 64B boundary
    stride = 1 if mode == "unpadded" else LINE_INTS      # padded + privatized -> own line
    bar = ctx.Barrier(P + 1)
    procs = [ctx.Process(target=worker, args=(arr, base + p * stride, K, mode, bar))
             for p in range(P)]
    for pr in procs: pr.start()
    bar.wait()
    t0 = time.perf_counter()
    for pr in procs: pr.join()
    t = time.perf_counter() - t0
    total = sum(arr[base + p * stride] for p in range(P))
    return t, total

def main():
    ctx = mp.get_context()
    rows, T1 = [], {}
    for mode in ["unpadded", "padded", "privatized"]:
        for P in PS:
            runs, total = [], None
            for _ in range(REPEATS):
                t, total = run(mode, P, ctx)
                runs.append(t)
            T = statistics.median(runs)
            if P == 1: T1[mode] = T
            S = T1[mode] / T
            e = (P * T / T1[mode] - 1) / (P - 1) if P > 1 else float("nan")
            ok = total == P * K
            rows.append((mode, P, K, T, S, S / P * 100, e, total, P * K, ok))
            print(f"{mode:10s} P={P} T={T:7.3f}s S={S:5.2f} e={e:7.4f} total={total} ok={ok}")
    os.makedirs("results", exist_ok=True)
    with open("results/false_sharing_karp_flatt.tsv", "w") as f:
        f.write("variant\tP\tK\tmedian_time_s\tspeedup\tefficiency_pct\tkarp_flatt_e\ttotal\texpected\texact\n")
        for r in rows:
            f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]:.6f}\t{r[4]:.4f}\t{r[5]:.2f}\t{r[6]:.6f}\t{r[7]}\t{r[8]}\t{r[9]}\n")

if __name__ == "__main__":
    main()