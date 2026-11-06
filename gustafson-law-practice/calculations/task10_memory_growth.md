# Task 10 — Memory Growth under Weak Scaling

## Model
Weak scaling: W(P) = P·W(1); memory M(P) = c·P (c = memory per node). Cap: 32 GB per node
(**assumption: 32 GB = 32×10⁹ bytes**; 32 GiB = 34.36×10⁹ would raise N by ×1.022).
For a 3-D grid with b bytes per cell: total cells N³ = P·(32×10⁹)/b ⇒ **N_max = (P·32×10⁹ / b)^(1/3)**.
Per-node local cube: n = (32×10⁹/b)^(1/3). Because N³ ∝ P, N ∝ P^(1/3): 8× more nodes ⇒ only 2× larger N (512/64 = 8).

## Bytes-per-cell assumption (required — the task cannot be answered without it)
Real solvers store several arrays (state variables, old/new time levels, halos, metadata). The task statement gives no constant,
so results are tabulated for three **illustrative** values: b = 8 (one float64 field), 40 (five float64 fields),
200 (e.g. 25 float64 fields). These are upper bounds: they ignore OS, MPI buffers, halo cells, and padding.

| b (B/cell) | Nodes | Total memory | Max cells N³ | Max global N | Local n per node |
|---:|---:|---:|---:|---:|---:|
| 8 | 64 | 2.048 TB | 2.5600e+11 | 6,350 | 1,587 |
| 8 | 512 | 16.384 TB | 2.0480e+12 | 12,699 | 1,587 |
| 40 | 64 | 2.048 TB | 5.1200e+10 | 3,713 | 928 |
| 40 | 512 | 16.384 TB | 4.0960e+11 | 7,427 | 928 |
| 200 | 64 | 2.048 TB | 1.0240e+10 | 2,172 | 543 |
| 200 | 512 | 16.384 TB | 8.1920e+10 | 4,343 | 543 |

## Why the exact N cannot be determined
M(N) = b·N³ with b unknown; N = (M/b)^(1/3) depends on b through a cube root, so the *scaling law* N ∝ P^(1/3) is exact but the
*value* of N is not. Example: for 512 nodes, b = 8 gives N ≈ 12,699 while b = 200 gives N ≈ 4,343 — a factor (200/8)^(1/3) = 2.92 smaller.
