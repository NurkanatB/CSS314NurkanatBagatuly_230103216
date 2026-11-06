# Task 03 — The Serial-Fraction Invariance Paradox

## The apparent paradox
Amdahl: a serial fraction s measured on one processor throttles speedup at 1/s. Gustafson: a serial fraction α of 4% still gives speedup ≈ 0.96P.
Both cannot be true of "the same program with 4% serial code" — unless the "4%" is measured in different frames.

## Frames of reference
* **Uniprocessor frame (Amdahl):** s = t_serial / (t_serial + t_par,1) for a *fixed* job. As P grows, t_par shrinks as 1/P but t_serial does not.
* **Parallel-machine frame (Gustafson):** α = t′_serial / T_P measured on the P-processor run of the *scaled* job. Here t′_serial is the same absolute time, but T_P is held constant.

**Relating them.** Let the serial job have serial time σ (constant) and parallel work w (on one processor). Fixed-size run on P processors: T = σ + w/P,
so the parallel-frame fraction is α_fixed(P) = σ/(σ + w/P) = s·P/(sP + 1 − s) — which grows toward 1 as P grows. So measuring α on a parallel machine for a *fixed* problem
shows serial fraction rising with P: exactly Amdahl's collapse.
If the work is scaled, w_P = P·w₀ with σ fixed, then T = σ + w₀, α = σ/(σ + w₀) is **independent of P**, and one-processor equivalent s_eq = σ/(σ + P w₀) = α/(α + (1−α)P) shrinks with P.
Hence the uniprocessor-frame fraction of the scaled problem **decreases**, while the parallel-frame α is **invariant**: s_eq = α/(P − α(P−1)) = α/S_G(P).

## Why the contradiction disappears
Amdahl's s and Gustafson's α are different quantities attached to different workloads (one job vs. a family of jobs growing with P). The statement
"the serial fraction is constant" is true for α only under the scaled-workload, fixed-serial-time assumption; it is false for s under the same assumption.
Gustafson's measurement on the parallel machine is simply the natural place to observe α when the job is too large for one processor.

## Limitations of the invariance assumption
1. Some serial work grows with problem size (mesh generation, input parsing, global convergence checks): then σ = σ(P) and α rises.
2. Communication adds latency terms growing with P (Task 12), which behave like extra serial time in the parallel frame.
3. Load imbalance idles processors in the "parallel" phase: α measured from timelines is inflated by it.
4. Memory limits may prevent the scaled job from running on one processor, so T_1 is extrapolated and the "speedup" is a model value.
