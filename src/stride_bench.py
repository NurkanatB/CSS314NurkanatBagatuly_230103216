import time, statistics, os
import numpy as np

STRIDES = [1, 2, 4, 8, 16, 32, 64, 128]
N = 16_777_216

def main():
    data = np.ones(N, dtype=np.float64)
    rows = []
    for s in STRIDES:
        view = data[::s]                 # strided view: reads every s-th element
        touched = view.shape[0]
        for _ in range(5):               # warmup
            view.sum()
        times = []
        for _ in range(5):
            t0 = time.perf_counter_ns()
            total = view.sum()
            times.append(time.perf_counter_ns() - t0)
        med = statistics.median(times)
        assert total == touched          # sanity: array of ones
        rows.append((s, touched, med, med / touched))
        print(f"stride={s:4d} touched={touched:9d} median={med/1e6:9.3f} ms  {med/touched:7.3f} ns/elem")
    os.makedirs("results", exist_ok=True)
    with open("results/stride_results.tsv", "w") as f:
        f.write("stride\telements_touched\tmedian_time_ns\tlatency_ns\n")
        for r in rows:
            f.write(f"{r[0]}\t{r[1]}\t{r[2]:.0f}\t{r[3]:.4f}\n")

if __name__ == "__main__":
    main()