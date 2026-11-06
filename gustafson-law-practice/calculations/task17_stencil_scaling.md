# Task 17 — 3-D 7-Point Stencil

Setup: cubic global domain N³ split into P equal sub-cubes of edge n = N/P^(1/3). Per step each rank updates n³ cells
(≈ 8 flops/cell) and exchanges 6 faces of n² cells (halo width 1).

* Computation per rank ∝ n³; communication volume per rank ∝ 6n²; **ratio = 6n²/n³ = 6/n**.

## Case 1 — weak scaling, fixed local domain (Gustafson-style; global N³ ∝ P)
n stays constant (here n = 128), so the ratio stays **6/n = 0.0469, independent of P**: neither improves nor degrades.
Per-rank neighbour communication is O(1); global N grows as N = n·P^(1/3).

## Case 2 — strong scaling, fixed global domain (here N = 1024)
n = N/P^(1/3) shrinks, ratio 6P^(1/3)/N **degrades** as P^(1/3).

## Case 3 — growing the local domain
If instead the per-rank problem grows (e.g. memory-bounded with larger memory/node), ratio ∝ 1/n **improves** — the surface-to-volume
effect favours bigger sub-domains.

| P | Global N (weak, n=128) | Ratio 6/n (weak) | Local n (strong, N=1024) | Ratio 6/n (strong) |
|---:|---:|---:|---:|---:|
| 1 | 128 | 0.0469 | 1,024.0 | 0.0059 |
| 8 | 256 | 0.0469 | 512.0 | 0.0117 |
| 64 | 512 | 0.0469 | 256.0 | 0.0234 |
| 512 | 1,024 | 0.0469 | 128.0 | 0.0469 |
| 4096 | 2,048 | 0.0469 | 64.0 | 0.0937 |

Conclusion: under Gustafson (weak) scaling the 3-D stencil is almost ideal because halo cost per rank is constant; the remaining
serial-like terms are latency (not volume), global reductions (convergence checks, O(log P)), I/O, and network contention.
The "improves" statement is true only relative to strong scaling at fixed global size, where the ratio degrades instead.
