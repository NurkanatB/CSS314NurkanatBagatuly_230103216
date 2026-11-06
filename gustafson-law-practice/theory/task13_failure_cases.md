# Task 13 — When Gustafson's Weak-Scaling Premise Fails

Premise: growing the problem ∝ P keeps *parallel runtime constant* with constant α. It fails if per-rank work, per-rank communication or iteration counts change with P.

## Case 1 — Unpreconditioned Conjugate Gradient on a 3-D Poisson problem (global synchronisation + changing complexity)
* Weak scaling with n³ local cells ⇒ global N = n·P^{1/3} cells per side. The condition number κ(A) ∝ N², CG iterations ∝ √κ ∝ N ∝ P^{1/3}.
* Per iteration, local work and halo exchange are constant, but 2 dot products need an **all-reduce**: latency ∝ log₂P.
* Runtime T(P) ∝ P^{1/3}·(t_comp + t_halo + t_lat·log₂P) — it **grows with P**; "constant time" is broken by algorithmic complexity (more iterations), not by hardware.
* Remedy: multigrid/preconditioning (iterations ~O(1)), communication-avoiding or pipelined CG (hide the all-reduce).

## Case 2 — Distributed 3-D FFT / all-to-all transpose (bisection-limited)
* Local data per rank constant (n³ points). A pencil/slab transpose needs data from all ranks: per-rank traffic ~n³, but a fraction ≈ ½ crosses the bisection.
  Total bisection traffic ∝ P·n³; on a 3-D torus the bisection bandwidth ∝ P^{2/3} ⇒ time ∝ P^{1/3}.
* FFT work itself is O(N log N): per-rank compute grows with log₂(global N), i.e. ∝ log P, a changing complexity class from O(N) to O(N log N).
* Consequence: weak-scaling efficiency decays as P^{−1/3}/log-type terms; α(P) is not constant.

## Case 3 — Direct N-body, all-pairs (O(N²)) (see Task 18)
Scaling N ∝ P gives total work ∝ P², per-processor work ∝ P — runtime grows linearly unless N ∝ √P, in which case the problem grows only as √P: Gustafson's W ∝ P is *not attainable at constant time*.

## Case 4 — Contended shared resources
Parallel file systems/metadata servers and shared network links: aggregate demand ∝ P against a fixed-capacity resource ⇒ serialisation (α grows ∝ P); e.g. N-to-1 checkpoint writes.

## Summary
| Failure mode | Why runtime grows | Growth |
|---|---|---|
| Iteration count grows with N | algorithmic | ∝ P^{1/3} (CG, 3-D) |
| Global collectives | latency | ∝ log P |
| All-to-all | bisection bandwidth | ∝ P^{1/3} (3-D torus) |
| Superlinear work in N | W(N) ∝ N² | ∝ P (direct N-body) |
| Shared-resource contention | queueing | ∝ P |
