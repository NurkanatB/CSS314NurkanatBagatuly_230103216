# Conclusions

1. **Gustafson and Amdahl answer different questions.** Amdahl: fixed work, time shrinks; speedup ≤ 1/s. Gustafson: fixed time, work grows; speedup ≈ (1−α)P. Efficiency limits: 1−α vs. 0 (Task 04).
2. **α and s are different measurements.** α is the serial share of the *parallel* run of the scaled job; s is the share of the one-processor run of a fixed job (Task 03). Equating them (Task 08: s = α = 0.08 ⇒ 11.47 vs 117.84 at P = 128) is a modelling choice, not a fact.
3. **Real programs have α(P).** Communication (log P, √P, P^{1/3} terms), growing iteration counts, serial I/O and imbalance turn constant α into a growing function (Tasks 12, 13, 18, 19, 20). The multiplicative model S_G/(1+γ(P)) captures this.
4. **Memory and complexity decide the right law.** GEMM needs N ∝ P^{1/3} for constant time (Task 16); stencils keep communication/computation constant at fixed local size (Task 17); memory-bounded scaling (Sun–Ni) can exceed Gustafson when work grows faster than memory.
5. **Isoefficiency Θ(P) is the ideal;** any overhead growing faster than P demands superlinear workload growth (Task 14). Energy follows the same scaling: dynamic energy tracks work, static energy tracks P·T, so serial phases waste α(P−1)·T·P_idle (Task 15).
6. **Empirical caveat.** The benchmark was run for real in the generation sandbox, which has a single logical CPU, so the data show oversubscription (S ≈ 0.7–1, fitted "α" ≈ 1.03, outside [0,1]), not parallel behaviour. The pipeline (benchmark → CSV → regression → plots) is validated; scientific conclusions require re-running on a multi-core host (Task 24).

Guidance for parallel software engineers: measure α on the parallel machine at several P; design for weak scaling when the problem can grow; minimise anything serial or O(P); prefer tree/collective patterns over gathers; avoid global synchronisation; report both strong- and weak-scaling results.
