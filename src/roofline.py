import json, time, argparse
import numpy as np

def measure_bw_gbs(n=40_000_000):
    a, b, c = np.ones(n), np.ones(n), np.ones(n)
    best = 1e9
    for _ in range(5):
        t0 = time.perf_counter(); np.add(b, c, out=a); best = min(best, time.perf_counter() - t0)
    return 3 * 8 * n / best / 1e9    # read b,c + write a (no write-allocate counted)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peak-bw-gbs", type=float, default=None, help="theoretical, e.g. 2ch DDR4-3200 = 51.2")
    ap.add_argument("--peak-gflops", type=float, default=None)
    ap.add_argument("--flops-per-cycle", type=int, default=16, help="DP FLOPs/cycle/core (AVX2 FMA=16)")
    a = ap.parse_args()
    host = json.load(open("results/host_profile.json"))
    prm = json.load(open("results/salted_params.json"))
    N = prm["N"]; l3 = host["cache"]["l3_bytes"] or 0
    flops, bytes_ideal, bytes_wa = 5, 16, 24   # 4 add + 1 mul; 8B read + 8B write (+8B write-allocate)
    ai, ai_wa = flops / bytes_ideal, flops / bytes_wa
    ws = 2 * N * N * 8
    freq = (host["cpu"]["base_freq_mhz"] or 2500) / 1000
    peak_gf = a.peak_gflops or host["cpu"]["physical_cores"] * freq * a.flops_per_cycle
    stream = measure_bw_gbs()
    peak_bw = a.peak_bw_gbs or stream
    ridge = peak_gf / peak_bw
    out = {"kernel": "5-point Jacobi stencil", "flops_per_cell": flops,
           "dram_bytes_per_cell_ideal": bytes_ideal, "dram_bytes_per_cell_write_allocate": bytes_wa,
           "arithmetic_intensity": ai, "arithmetic_intensity_flop_per_byte": ai, "arithmetic_intensity_write_allocate": ai_wa,
           "working_set_bytes": ws, "l3_bytes": l3, "working_set_exceeds_l3": ws > l3,
           "peak_gflops_assumed": peak_gf, "peak_bw_gbs_used": peak_bw,
           "measured_stream_like_bw_gbs": stream, "ridge_point_flop_per_byte": ridge,
           "attainable_gflops": min(peak_gf, ai * peak_bw),
           "regime": "Memory-Bandwidth Bound" if ai < ridge else "Compute Bound"}
    json.dump(out, open("results/roofline_summary.json", "w"), indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()