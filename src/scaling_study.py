import json, math, os, time, argparse, hashlib, ctypes
import multiprocessing as mp
import numpy as np

ITERS = 100

def worker(p, P, N, iters, bufA, bufB, bar_start, bar_iter):
    a = np.frombuffer(bufA, dtype=np.float64).reshape(N, N)
    b = np.frombuffer(bufB, dtype=np.float64).reshape(N, N)
    lo = 1 + (N - 2) * p // P
    hi = 1 + (N - 2) * (p + 1) // P
    src, dst = a, b
    bar_start.wait()
    for _ in range(iters):
        d = dst[lo:hi, 1:-1]
        np.add(src[lo - 1:hi - 1, 1:-1], src[lo + 1:hi + 1, 1:-1], out=d)
        np.add(d, src[lo:hi, :-2], out=d)
        np.add(d, src[lo:hi, 2:], out=d)
        np.multiply(d, 0.25, out=d)
        bar_iter.wait()
        src, dst = dst, src

def run(N, P, seed, iters):
    rng = np.random.default_rng(seed)
    u0 = rng.random((N, N))
    bufA = mp.RawArray(ctypes.c_double, N * N)
    bufB = mp.RawArray(ctypes.c_double, N * N)
    a = np.frombuffer(bufA, dtype=np.float64).reshape(N, N); a[:] = u0
    b = np.frombuffer(bufB, dtype=np.float64).reshape(N, N); b[:] = u0
    bs, bi = mp.Barrier(P + 1), mp.Barrier(P)
    ps = [mp.Process(target=worker, args=(p, P, N, iters, bufA, bufB, bs, bi)) for p in range(P)]
    for x in ps: x.start()
    bs.wait()
    t0 = time.perf_counter()
    for x in ps: x.join()
    t = time.perf_counter() - t0
    final = a if iters % 2 == 0 else b
    chk = hashlib.sha256(np.round(final, 6).tobytes()).hexdigest()
    return t, float(final.sum()), chk

def amdahl_fit(Ps, Ss):
    xs = [(1 - 1 / P) for P in Ps if P > 1]
    ys = [(1 / S - 1 / P) for P, S in zip(Ps, Ss) if P > 1]
    s = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)  # least squares on 1/S = 1/P + s(1-1/P)
    return min(max(s, 1e-9), 1.0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=ITERS)
    ap.add_argument("--max-p", type=int, default=None)
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()
    prm = json.load(open("results/salted_params.json"))
    host = json.load(open("results/host_profile.json"))
    N, seed = prm["N"], prm["seed"]
    maxp = a.max_p or host["cpu"]["physical_cores"]
    Ps = [1]
    while Ps[-1] * 2 <= maxp: Ps.append(Ps[-1] * 2)
    if Ps[-1] != maxp: Ps.append(maxp)

    def best(N_, P):
        res = [run(N_, P, seed, a.iters) for _ in range(a.repeats)]
        t = sorted(r[0] for r in res)[len(res) // 2]
        return t, res[0][1], res[0][2]

    rows, ref = [], None
    T1s = None
    for P in Ps:                                   # strong scaling
        t, ssum, chk = best(N, P)
        if P == 1: T1s, ref = t, (ssum, chk)
        S = T1s / t; E = S / P * 100
        e = (1 / S - 1 / P) / (1 - 1 / P) if P > 1 else float("nan")
        rows.append(("strong", P, N, t, S, E, e, "", ssum, chk, chk == ref[1]))
        print(f"strong P={P} N={N} T={t:.3f}s S={S:.2f} E={E:.1f}%")
    s = amdahl_fit(Ps, [r[4] for r in rows])
    smax = 1 / s
    W1 = N * N * a.iters
    T1w = None
    for P in Ps:                                   # weak scaling
        NP = math.ceil(N * math.sqrt(P))
        t, ssum, chk = best(NP, P)
        if P == 1: T1w = t
        WP = NP * NP * a.iters
        S_scaled = P * W1 * T1w / (WP * t)          # formula from the handout
        S_thr = (WP / t) / (W1 / T1w)               # throughput-based scaled speedup
        rows.append(("weak", P, NP, t, S_scaled, T1w / t * 100, "", S_thr, ssum, chk, ""))
        print(f"weak   P={P} N={NP} T={t:.3f}s S_scaled={S_scaled:.2f} thr_speedup={S_thr:.2f}")

    os.makedirs("results", exist_ok=True)
    with open("results/scaling_metrics.tsv", "w") as f:
        f.write("mode\tP\tN\ttime_s\tspeedup_or_scaled\tefficiency_pct\tkarp_flatt_e\tthroughput_speedup\tchecksum_sum\tsha256_r6\tmatches_serial_ref\n")
        for r in rows:
            f.write("\t".join(f"{x:.6f}" if isinstance(x, float) else str(x) for x in r) + "\n")
        f.write(f"# amdahl_serial_fraction\t{s:.6f}\t# S_max\t{smax:.3f}\t# iters\t{a.iters}\n")
    print(f"Amdahl: s={s:.4f}, S_max={smax:.2f}")

if __name__ == "__main__":
    main()