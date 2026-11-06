# Task 16 — Dense GEMM Weak-Scaling Targets

## Derivation
Work W(N) = 2N³ flops (c₃N³). Ideal weak scaling with constant runtime T: each processor does the same work per unit time, so
total work must grow ∝ P: W(N_P) = P·W(N₁) ⇒ N_P³ = P·N₁³ ⇒ **N_P = N₁·P^(1/3)**.
* Computation: total ∝ P; per processor constant.
* Memory (3 matrices, 8 B): M = 24N² ∝ P^(2/3) ⇒ per-processor memory ∝ P^(−1/3) — *memory never limits GEMM weak scaling*;
  the memory per node actually shrinks (so Sun–Ni memory-bounded scaling would allow a **larger** N: N ∝ P^(1/2) at constant memory/node).
* Communication (2-D algorithms, e.g. SUMMA): per-processor words ∝ N²/√P ∝ P^(2/3 − 1/2) = P^(1/6): it *grows*, so strictly constant
  runtime is not achieved without a cost model — ideal weak scaling here is an upper bound.

## Numerical example (N₁ = 1000 on one processor — assumed baseline; float64)
| P | N_P | Total flops 2N³ | Flops per processor | Total memory (GB) | Memory/processor (MB) |
|---:|---:|---:|---:|---:|---:|
| 1 | 1,000.0 | 2.000e+09 | 2.000e+09 | 0.024 | 24.00 |
| 8 | 2,000.0 | 1.600e+10 | 2.000e+09 | 0.096 | 12.00 |
| 64 | 4,000.0 | 1.280e+11 | 2.000e+09 | 0.384 | 6.00 |
| 512 | 8,000.0 | 1.024e+12 | 2.000e+09 | 1.536 | 3.00 |
| 4,096 | 16,000.0 | 8.192e+12 | 2.000e+09 | 6.144 | 1.50 |
| 16,384 | 25,398.4 | 3.277e+13 | 2.000e+09 | 15.482 | 0.94 |
Example: P = 512 ⇒ N = 1000·8 = 8000 (verified: 8000³/1000³ = 512).
