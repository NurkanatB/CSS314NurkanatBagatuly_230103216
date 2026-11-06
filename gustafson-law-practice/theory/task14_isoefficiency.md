# Task 14 — Isoefficiency and Gustafson-Compliant Weak Scaling

## Definitions (Grama, Gupta, Kumar; Kumar & Rao)
W = serial work (time on one processor). T_P = parallel time. Total overhead T_o(W,P) = P·T_P − W. Then
E = W/(P·T_P) = 1/(1 + T_o/W). Holding E constant requires T_o/W = (1−E)/E, i.e.

**isoefficiency relation: W = K·T_o(W,P), K = E/(1−E).** The isoefficiency function is the W(P) solving it; lower growth ⇒ more scalable. Since all P processors must have work, W = Ω(P) always, so **Θ(P) is the best possible isoefficiency**.

## Gustafson model as an overhead model
Normalise T_P = 1 (fixed). During the serial phase of length α, P−1 processors idle: T_o = P·1 − W with W = α + (1−α)P ⇒ **T_o = α(P−1)**. Then
E = W/P = 1 − α(P−1)/P (matches Task 04). Imposing the isoefficiency condition W = K·T_o with T_o = α(P−1) gives
W = K·α(P−1) ⇒ **W(P) = Θ(P)**. For the asymptotic efficiency E_∞ = 1−α, K = E/(1−E) = (1−α)/α and W → (1−α)P, exactly Gustafson's scaled workload.
**The isoefficiency function of a Gustafson-compliant program is linear, W = Θ(P)** — the ideal, since T_o is linear in P and independent of W.

## Distinction between ideal weak scaling and classical isoefficiency
| | Ideal weak scaling (Gustafson) | Isoefficiency |
|---|---|---|
| Asks | work growth for constant *time* | work growth for constant *efficiency* |
| Overhead | serial time fixed, independent of W | any T_o(W,P) |
| Result | W ∝ P by construction | W(P) derived, may be P log P, P^{3/2}, ... |
| Equivalent when | T_o depends on P only (T_o = c·P) | — |

Counter-examples: if the serial portion scales with the problem (σ = s·W, Amdahl-type), T_o = (P−1)·s·W and E = 1/(1 + s(P−1)) cannot be kept constant by any W: *no isoefficiency function exists*.
If T_o = c·P log P (tree-based overhead per processor), W = Θ(P log P) while constant *time* needs W ∝ P — then constant-time weak scaling and constant-efficiency scaling disagree, and efficiency falls under pure fixed-time scaling.
