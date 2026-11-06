# Task 01 — Strong Scaling vs. Weak Scaling

**Notation.** P = processors/workers; s = serial fraction of the *fixed-size, one-processor* run (Amdahl);
α = serial fraction of the run *observed on the P-processor machine* with scaled workload (Gustafson).
S_A(P) = 1/[s + (1−s)/P]; S_G(P) = P − α(P−1) = 1 + (1−α)(P−1).

## 1. Amdahl (1967): fixed-size ("strong") scaling
**Assumption:** the problem is fixed; only the machine grows. With T(1) = s + p, s + p = 1, parallel time is T(P) = s + p/P, so
S_A(P) = 1/(s + (1−s)/P) → 1/s as P → ∞. Problem size N is constant, so work per processor ∝ N/P → 0, and the serial part
(constant in absolute time) eventually dominates. It is called **fixed-size** scaling because the workload is the invariant.
Amdahl's original argument (AFIPS 1967) was a case for the continued importance of single-processor performance.

## 2. Gustafson (1988): fixed-time ("weak") scaling
**Assumption:** users scale the problem to use the available machine so that **wall-clock time stays constant** (e.g. a forecast
must finish in an hour). Normalise the parallel run to s′ + p′ = 1. A serial machine would need s′ + p′P, hence
S_G(P) = s′ + p′P = P − α(P−1) with α = s′. Work grows ∝ P (for the parallel part), time is the invariant — **fixed-time** scaling.
The serial part is assumed not to grow with the problem (e.g. setup, I/O of a fixed header, fixed-cost sequential control logic).

## 3. Problem size as P → ∞
| | Amdahl | Gustafson |
|---|---|---|
| Problem size N(P) | N₀ (constant) | N(P) with W(N(P)) ≈ P·W(N₀) → ∞ |
| Work per processor | ∝ 1/P → 0 | constant |
| Runtime T(P) | → s·T(1) (floor) | constant by construction |
| Speedup limit | 1/s (bounded) | unbounded, ~(1−α)P |
| Efficiency limit | → 0 | → 1 − α |

## 4. Mathematical vs. physical difference
Mathematically, both are the same identity "speedup = serial time / parallel time" applied to different invariants: Amdahl fixes the
numerator's workload; Gustafson fixes the denominator's time. The two serial fractions are **not the same quantity**: s is relative
to T(1); α is relative to T(P). They are related by α = s/(s + (1−s)/P) (see Task 03), so a small fixed-size s corresponds to a much larger α
at large P, but under a scaled workload with a fixed absolute serial time, α stays small.
Physically: Amdahl describes "make this job faster"; Gustafson describes "do a bigger job in the same time", which is how most
simulations and analytics are actually used.

## 5. Practical HPC relevance
* Strong scaling matters for latency-bound products: real-time control, interactive analysis, fixed-size production runs, and when the problem cannot grow
  (fixed mesh from CAD, fixed dataset).
* Weak scaling matters for climate/weather, CFD, molecular dynamics, Monte Carlo, and training with fixed per-device batch.
* Real codes need both measurements; neither law accounts for communication growth, load imbalance or memory limits (Tasks 11–12).
