# Task 09 — Multi-Component Workload

| Phase | Share of parallel execution time | Treated as |
|---|---:|---|
| A: disk I/O + parameter broadcast | 2% | serial |
| B: boundary synchronisation | 6% | serial (stated assumption) |
| C: domain flux computation | 92% | parallel |

Aggregate serial fraction under the stated assumption: **α = 0.02 + 0.06 = 0.08**, p = 0.92.

| P | S(P) = P − 0.08(P − 1) | E(P) |
|---:|---:|---:|
| 512 | 471.1200 | 0.92016 |
| 2048 | 1884.2400 | 0.92004 |

Check P = 512: 512 − 0.08·511 = 512 − 40.88 = 471.12. P = 2048: 2048 − 0.08·2047 = 2048 − 163.76 = 1884.24.

## Are all phases genuinely serial?
* **A (I/O, broadcast):** parallel file systems (MPI-IO, striping) make reads parallel; a broadcast is a tree
  operation costing O(log P) latency steps — not constant, not strictly serial, but not P-parallel either.
* **B (boundary sync):** neighbour halo exchange is executed *concurrently* by all ranks; its cost per rank is roughly constant
  under weak scaling (Task 17), so it behaves like per-rank overhead that does not shrink — a "serial-like" cost in time, but
  not work that only one processor can do. Global barriers/reductions in B do grow with P.
* **C:** parallel provided load balance is perfect.
Limitation: lumping A+B into α is a conservative (pessimistic) simplification for B and a time-accounting convenience, not a
physical statement. A correct model uses α(P) = α_serial + c(P) with communication terms as in Task 12.
