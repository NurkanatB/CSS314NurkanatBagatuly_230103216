# Task 18 — N-Body Scaling: All-Pairs vs. Barnes–Hut

No exact serial/parallel ratio can be claimed without a partitioning and overhead model, so we **define one** (toy model, stated assumptions) and derive scaling only from it.

## Model
Per time step on P processors: T_P = t_u·N [serial integrator/bookkeeping, one rank] + t_f·F(N)/P [force evaluation, perfectly balanced] + t_c·(comm).
F(N) = N² (direct) or N log₂N (Barnes–Hut). Tree construction for BH is either serial (t_b·N log N) or parallel.

## Growth of N with P at constant step time
* **Direct, O(N²):** constant t_f·N²/P ⇒ **N = N₁√P**. Particles per processor N/P = N₁/√P *decreases*; the problem grows only ∝ √P, not ∝ P.
* **Barnes–Hut:** N log N ∝ P ⇒ **N ≈ cP/ log(cP) ~ Θ(P/log P)**: almost linear weak scaling. Work per processor is constant by construction in both cases.

## Serial/parallel ratio r = (serial time)/(parallel time) under the model
| | Serial O(N) part | Parallel part (const.) | r(P) |
|---|---|---|---|
| Direct | t_u N₁√P | t_f N₁²  (per-proc. const.) | ∝ √P — **grows** |
| BH, serial integrator | t_u·cP/log N | t_f·c | ∝ P/ log P — **grows faster** |
| BH, serial tree build | t_b·N log N = t_b·cP | t_f·c | ∝ P — α → 1 |
| BH, everything parallel except O(1) setup | O(1) | const. | constant ⇒ Gustafson holds |
So even though both methods keep the *force* work per processor constant, any **serial** O(N) component grows with N ∝ √P or ∝ P/ log P and eventually breaks the constant-α assumption. Barnes–Hut weak-scales better in N but exposes serial O(N) code to a faster-growing N.

## Communication (depends on decomposition; stated assumptions)
* Direct, replicated-particles ("atom") decomposition: each rank needs all N positions: allgather volume O(N) per rank ∝ √P per step, latency O(log P). Force-decomposition/2-D schemes reduce it to O(N/√P) = O(1) here (N/√P = N₁).
* Barnes–Hut with locally-essential trees: remote data per rank ~ O((N/P)^{2/3} + log P)-type surface terms plus the tree top replicated — communication per rank is roughly constant or slowly growing, but irregular and dependent on particle distribution and load balance (costzones/ORB partitioning).
* Constant iteration time assumption: strictly requires T_P(N(P)) = const., which fails when (i) comm. grows (above), (ii) the clustered particle distribution imbalances work in BH, (iii) the step count or time step must shrink with N (e.g. smaller dt for close encounters).

## Take-away
Direct N-body "weak scaling" at constant time is √P growth of N; Barnes–Hut gives near-linear growth but needs the serial/bookkeeping and tree-build phases parallelised. Quantities such as α must be measured on the specific implementation.
References: Barnes & Hut, Nature 324, 446 (1986); Warren & Salmon, "A parallel hashed oct-tree N-body algorithm", SC'93; Plimpton, J. Comp. Phys. 117 (1995) (force decomposition).
