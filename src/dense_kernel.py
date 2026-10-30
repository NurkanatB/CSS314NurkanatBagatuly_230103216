import json, os, time, statistics, hashlib, argparse
import numpy as np
from salt import get_student_params

try:
    from numba import njit
    HAVE_NUMBA = True
except ImportError:
    HAVE_NUMBA = False

if HAVE_NUMBA:
    @njit(cache=True)
    def ijk(A, B, C, M):
        for i in range(M):
            for j in range(M):
                s = 0.0
                for k in range(M):
                    s += A[i * M + k] * B[k * M + j]   # B strides by M
                C[i * M + j] = s

    @njit(cache=True)
    def ikj(A, B, C, M):
        for i in range(M):
            for k in range(M):
                a = A[i * M + k]                       # hoisted
                for j in range(M):
                    C[i * M + j] += a * B[k * M + j]   # stride-1
else:
    def ijk(A, B, C, M):
        for i in range(M):
            for j in range(M):
                s = 0.0
                for k in range(M):
                    s += A[i * M + k] * B[k * M + j]
                C[i * M + j] = s

    def ikj(A, B, C, M):
        for i in range(M):
            for k in range(M):
                a = A[i * M + k]
                for j in range(M):
                    C[i * M + j] += a * B[k * M + j]

def timed(fn, A, B, M, runs=3):
    ts = []
    for _ in range(runs):
        C = np.zeros(M * M) if HAVE_NUMBA else [0.0] * (M * M)
        t0 = time.perf_counter()
        fn(A, B, C, M)
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts), ts, C

def digest(C):
    return hashlib.sha256(np.round(np.asarray(C), 6).tobytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, default=None, help="override sub-block size (default N/2)")
    a = ap.parse_args()
    p = json.load(open("results/salted_params.json"))
    N = p["N"]
    M = a.M or N // 2
    rng = np.random.default_rng(p["seed"])
    A = rng.random(M * M)
    B = rng.random(M * M)
    if not HAVE_NUMBA:
        print("WARNING: numba not found, pure Python fallback: use small --M (e.g. 128)")
        A, B = A.tolist(), B.tolist()
    else:
        w = np.zeros(4); ijk(w, w, np.zeros(4), 2); ikj(w, w, np.zeros(4), 2)  # JIT warmup

    t_naive, ts_n, C1 = timed(ijk, A, B, M)
    t_int, ts_i, C2 = timed(ikj, A, B, M)
    max_err = float(np.max(np.abs(np.asarray(C1) - np.asarray(C2))))
    res = {"N": N, "M": M, "numba": HAVE_NUMBA,
           "t_naive_ijk_s": t_naive, "t_interchanged_ikj_s": t_int,
           "runs_naive_s": ts_n, "runs_interchanged_s": ts_i,
           "speedup": t_naive / t_int, "max_abs_diff": max_err,
           "within_1e-12": max_err <= 1e-12,
           "digest_naive": digest(C1), "digest_interchanged": digest(C2)}
    os.makedirs("results", exist_ok=True)
    json.dump(res, open("results/loop_interchange.json", "w"), indent=2)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()