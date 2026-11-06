# Task 11 — Amdahl vs. Gustafson vs. Sun–Ni Memory-Bounded Speedup

## Formulations (α = serial fraction of the work; G(P) = factor by which the parallel workload grows when memory grows P-fold)
| Model | Workload | Speedup |
|---|---|---|
| Amdahl (fixed-size) | G(P) = 1 | S_A = 1/[α + (1−α)/P] |
| Gustafson (fixed-time) | G(P) = P | S_G = α + (1−α)P |
| Sun–Ni (memory-bounded) | G(P) from the memory/work relation | **S* = [α + (1−α)G(P)] / [α + (1−α)G(P)/P]** |

With G = 1 the Sun–Ni formula reduces to Amdahl; with G = P to Gustafson, so it is a genuine generalisation (X.-H. Sun & L. Ni, "Another view on parallel speedup", Supercomputing '90; "Scalable problems and memory-bounded speedup", JPDC 19, 1993).
**Memory assumption:** the usable memory is M(P) = P·M₁; the problem grows to fill it. If work is W ∝ N^a and memory M ∝ N^b, then W ∝ M^{a/b} and **G(P) = P^{a/b}**.

## When Gustafson mis-estimates
* **G(P) > P (Gustafson underestimates the achievable speedup of the memory-filled problem):** dense linear algebra: a = 3 (GEMM/LU), b = 2 ⇒ G = P^{3/2}.
  α = 0.04, P = 64: S_A = 18.18, S_G = 61.48, **S\* = 63.67** (G = 512). But the runtime of that scaled job *grows* (∝ P^{1/2}), so this is not fixed-time speedup.
* **G(P) = P** (a = b, e.g. stencil iteration counts fixed, linear-time PDE steps): Sun–Ni = Gustafson.
* **G(P) < P (Gustafson overestimates):** when work grows sublinearly with memory (e.g. a ≈ 1 but extra memory is spent on buffers/replicated data, or sorting-like b>a cases),
  or when time constraints, not memory, limit the size. Also overestimates whenever communication/imbalance growth is ignored, which neither formula models.

## Advantages / limitations
* Amdahl: simple lower-bound reasoning for fixed jobs; ignores problem growth.
* Gustafson: matches fixed-time use; ignores memory capacity and communication; presumes work ∝ P is possible.
* Sun–Ni: includes memory capacity and algorithm complexity through G(P); needs knowledge of the work–memory relation; with G>P the "speedup" compares a larger job on P processors against the same job on one processor *if it fitted* (it would not), so it is a model quantity; no communication term either.
