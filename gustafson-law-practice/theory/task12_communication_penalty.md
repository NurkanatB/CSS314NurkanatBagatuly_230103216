# Task 12 — Gustafson with a Communication Penalty

## Consistent normalisation
Compute part of the scaled run on P processors takes α + (1−α) = 1 (time unit = scaled compute time T_comp). Add communication/synchronisation time
γ(P) ≥ 0 **in the same unit** (dimensionless: communication time ÷ compute time, γ(1) = 0). Then

T_P = 1 + γ(P), T_1 = α + (1−α)P (one processor: no communication)

**S_mod(P) = [P − α(P−1)] / [1 + γ(P)] = S_G(P)/(1 + γ(P))** — a **multiplicative** model.

## Additive form
The sheet's form S = P − α(P−1) − C(P) is exact if C(P) is expressed in *speedup units* (equivalent lost processors):
C(P) = S_G(P)·γ/(1+γ). For small γ, C ≈ γ·S_G ≈ γ(1−α)P (grows with P, not with γ alone).
If one instead subtracts a constant-unit time term (C = γ(P) directly), the model is **not** consistent: it subtracts a fraction of one processor's time from a quantity measured in processors. Units must match.

## Candidate communication models (κ = ratio of per-step comm. time to compute time)
| Pattern | γ(P) | S_mod asymptotics | E_mod → |
|---|---|---|---|
| Nearest-neighbour halo | κ (constant) | (1−α)P/(1+κ) | (1−α)/(1+κ) |
| Tree reduction/broadcast | κ log₂P | ~(1−α)P/(κ log₂P) | 0 slowly |
| 2-D mesh collective / bisection-limited | κ√P | ~(1−α)√P/κ | 0 as P^{−1/2} |
| All-to-all (3-D torus bisection) | κP^{1/3} | ~(1−α)P^{2/3}/κ | 0 |

Efficiency: E_mod = (1 − α + α/P)/(1 + γ(P)).

## Conditions for meaningful speedup
S_mod > 1 ⇔ S_G > 1 + γ. For log: P − α(P−1) > 1 + κ log₂P (true for all P ≥ 2 when κ is small, e.g. κ ≤ (1−α)). For √P: need (1−α)(P−1) > κ√P ⇒ √P > κ/(1−α) approximately.
For a target efficiency E*: need 1 + γ(P) ≤ (1−α)/E*. Example: α = 0.04, κ = 0.02 log₂P: P = 1024 ⇒ γ = 0.2, S = 983.08/1.2 = 819.2 (E = 0.80); with κ√P at κ = 0.02: γ = 0.64, S = 599.4 (E = 0.585).

Remarks: (i) latency-bound pieces (barriers) are naturally additive in time; bandwidth-bound halos scale with surface/volume (Task 17); (ii) γ may exceed what overlap hides — with perfect overlap, T_P = max(1, γ) instead; (iii) α itself may contain a log P term (serial setup + broadcast), which this model captures by γ.
