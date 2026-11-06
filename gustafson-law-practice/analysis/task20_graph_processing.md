# Task 20 — Graph Analytics (BFS, PageRank) vs. Dense Linear Algebra

## Why dense linear algebra weak-scales well
GEMM: arithmetic intensity grows with N (≈ N/12 flops per byte for blocked float64); data access is regular and prefetchable, partitions are equal-sized,
communication is predictable (SUMMA broadcasts), and there is no data-dependent control flow.

## Graph workloads
**Power-law structure.** Degree distribution P(k) ∝ k^{−γ}, typically 2 < γ < 3 (social/web graphs, Graph500 RMAT/Kronecker). A few hubs have degree ≫ mean.
* *Load imbalance:* a 1-D vertex partition gives the rank owning hubs far more edges; equal vertices ≠ equal edges. Edge-balanced or 2-D partitioning (Buluç & Madduri, SC'11) and vertex-cut (PowerGraph, Gonzalez et al., OSDI'12) mitigate but do not remove it.
* *Irregular memory access:* neighbour lookups are random gathers: intensity ≈ O(1) flop (or edge) per cache line, so performance is bounded by memory latency/bandwidth and measured in TEPS, not FLOPS.
* *Communication:* a random partition cuts ≈ (1 − 1/P) of edges, so almost every edge traversal is remote; per-level traffic is all-to-all-like and its volume does not shrink with locality (no surface-to-volume benefit, unlike Task 17).

**BFS (level-synchronous).**
```python
frontier = {src}; dist = {src: 0}
while frontier:                      # one global barrier per level
    nxt = set()
    for u in frontier:               # frontier size varies by orders of magnitude
        for v in adj[u]:             # random access, remote on most partitions
            if v not in dist:
                dist[v] = dist[u] + 1; nxt.add(v)
    frontier = nxt                   # all-to-all exchange of newly discovered vertices
```
* Frontier imbalance: the first and last levels are tiny, middle levels contain most of the graph and are dominated by hubs; processors idle at barriers.
* Synchronisation: levels ≈ diameter D = O(log N) for power-law graphs, so barrier count grows slowly — but each level costs ≥ t_lat·log P and one all-to-all, i.e. T(P) grows with P and N (more levels, bigger exchanges).
* Direction-optimising BFS (Beamer, Asanović, Patterson, SC'12) switches top-down/bottom-up to cut edge checks but increases irregular comm./data-dependence.

**PageRank (power iteration).** r ← d·A·D⁻¹ r + (1−d)/N · 1. Each iteration is an SpMV; iteration count ≈ log ε / log d (≈ 50–100 for d = 0.85) is *independent of N* — the one favourable property for weak scaling. But each iteration: gathers remote ranks (all-to-all of cut edges), a global dangling-node sum and convergence norm (all-reduce, O(log P)), and imbalance from hub rows/columns.

## Why Gustafson weak scaling is hard to reach on graphs
1. Work per rank is not constant after "N ∝ P": edge counts per rank vary with skew; hubs can serialise.
2. α(P) grows: barriers per level × levels, all-reduces per iteration, partitioning/graph-ingest/I/O are largely serial or I/O-bound.
3. Communication ∝ edge cut ~ constant fraction of edges instead of surface ∝ N^{2/3}; there is no geometric locality.
4. Memory-bound kernels: adding cores per node does not add bandwidth.
5. Graph generators and real graphs cannot be enlarged "uniformly": diameter and degree skew change with size, so the scaled problem is not the same problem.
Result: reported Graph500 weak scaling shows TEPS growing sub-linearly with P and strongly dependent on partitioning and aggregation; ideal Gustafson efficiency (1−α) with constant α is rarely observed.
