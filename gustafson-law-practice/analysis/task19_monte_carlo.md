# Task 19 — Monte Carlo: the Near-Ideal Weak-Scaling Workload

## Why it is the ideal case
Each worker draws n independent samples and returns one partial sum: no communication during compute. Work per worker is constant, so scaled problem size = P·n, giving statistical
error ∝ 1/√(Pn) — more samples in the same time. Our empirical benchmark (`benchmarks/weak_scale_bench`) is exactly this workload (π estimation).

## Sources of non-zero serial fraction α
1. **PRNG stream management.** Workers need statistically independent streams. Naive `seed + rank` with weak generators can give correlated streams; sound options: counter-based generators (Philox), jump-ahead / block splitting, or `numpy.random.SeedSequence.spawn` (used here). Cost: O(1) per worker if each worker derives its own stream from (seed, rank); **O(P) serial** if a master creates and ships P states. Reproducibility across different P requires fixing the stream-to-sample mapping (a design choice).
2. **Reduction of partial results.** A binomial tree needs ⌈log₂P⌉ levels, time T_red = t_lev·⌈log₂P⌉ (t_lev = latency + transfer per level).
3. **Output serialisation.** If all P partial results (or per-worker histograms/paths) are written by one rank, time T_out = P·t_w — **linear in P**.
4. **Startup/teardown:** launching processes, reading configuration; on Windows `spawn` start-up is large (Task 24).
5. **Statistics/variance post-processing** done on one rank: O(P) for gathering per-worker variance.

## Quantified model (illustrative constants, clearly assumptions — not measurements)
T_c = 1 s compute per worker; t_lev = 5 µs per tree level; t_w = 1 µs per serialised result; constant serial setup α₀ = 0.001.
α_tree = α₀ + T_red/T_c; α_ser = α_tree + T_out/T_c. Then S = P − α(P−1) (the overhead terms are treated as serial time in the parallel-frame).

| P | levels ⌈log₂P⌉ | T_red (µs) | T_out (ms) | α (tree only) | S (tree only) | α (+ serial output) | S (+ serial output) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 4 | 20 | 0.016 | 0.00102 | 16.0 | 0.00104 | 16.0 |
| 256 | 8 | 40 | 0.256 | 0.00104 | 255.7 | 0.00130 | 255.7 |
| 4,096 | 12 | 60 | 4.096 | 0.00106 | 4091.7 | 0.00516 | 4074.9 |
| 16,384 | 14 | 70 | 16.384 | 0.00107 | 16366.5 | 0.01745 | 16098.1 |
| 65,536 | 16 | 80 | 65.536 | 0.00108 | 65465.2 | 0.06662 | 61170.3 |

## Interpretation
* The tree reduction is almost free: even at 65,536 workers its cost (80 µs) is 8×10⁻⁵ of T_c: α stays ≈ α₀ and E ≈ 1 − α₀.
* Serialising output through one rank costs P·t_w and eventually dominates (65 ms ≈ 6.5% of T_c at 65,536 workers): a linear term beats a logarithmic one — use reductions instead of gathers and parallel I/O.
* A reduction that sums **scalars** is a log P latency problem; a reduction of vectors of size m costs t_lev ≈ t₀ + m·t_B and becomes bandwidth-bound for large histograms (use reduce-scatter).
* The sampling error improves as 1/√(Pn): weak scaling buys accuracy, whereas strong scaling would only reach the same accuracy sooner (and then hits α·T₁).
