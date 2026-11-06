# Task 04 — Asymptotic Efficiency

## Gustafson
E_G(P) = [P − α(P−1)]/P = 1 − α + α/P. For fixed α ∈ [0,1]:

**lim_{P→∞} E_G(P) = 1 − α** (since α/P → 0). Proof: |E_G − (1−α)| = α/P → 0. E_G decreases monotonically from 1 (P=1) toward 1−α
(dE/dP = −α/P² < 0). Speedup is asymptotically linear: S_G ~ (1−α)P.

## Amdahl
E_A(P) = S_A/P = 1/[sP + (1−s)]. For s > 0:

**lim_{P→∞} E_A(P) = 0**, with E_A ~ 1/(sP). Proof: the denominator sP + (1−s) → ∞. (For s = 0 the limit is 1.) Speedup saturates at 1/s.

## Contrast
| | α or s = 0.04 | P = 10³ | P = 10⁶ | P → ∞ |
|---|---|---|---|---|
| E_G | 0.96 + 0.04/P | 0.96004 | 0.96000004 | **0.96** |
| E_A | 1/(0.04P + 0.96) | 0.0245 | 2.5×10⁻⁵ | **0** |

**Mathematical difference:** Amdahl's serial term sP grows linearly in the denominator; Gustafson's serial term α/P vanishes.
**Physical difference:** under fixed size, the amount of useful work per processor goes to zero while serial time is constant ⇒ processors idle.
Under scaled size, each processor always has the same amount of parallel work, and the serial phase costs a fixed fraction α of the run during which P−1 processors idle: a constant loss α(P−1)/P → α.
Caveat: the limit 1−α assumes α is truly constant; with α(P) growing (e.g. 1 + κ log P in the denominator, Task 12) the limit can be 0.
