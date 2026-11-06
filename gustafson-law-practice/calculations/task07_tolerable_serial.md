# Task 07 — Maximum Tolerable Serial Fraction

Given P = 8192 and S(P) ≥ 7500.

## Derivation
S(P) = P − α(P − 1) ≥ S_req
⇒ α(P − 1) ≤ P − S_req            (P − 1 > 0, so the inequality direction is kept)
⇒ **α_max = (P − S_req)/(P − 1) = (8192 − 7500)/8191 = 692/8191**.

## Numerical result
α_max = 692/8191 = **0.0844829691** ≈ 8.4483% (exact fraction 692/8191; 8191 = 2¹³ − 1 is prime).

## Verification (Python)
* S(P) at α_max = 7500.0000000000 (equals 7500 within float rounding).
* S(P) at α = 0.0844 = 7500.679600 ≥ 7500 ✔
* S(P) at α = 0.0846 = 7499.041400 < 7500 ✘

Interpretation: an 8.45 % serial fraction (measured on the 8192-core machine, scaled workload) is tolerable —
in sharp contrast with Amdahl, where s = 0.0845 would cap speedup at 1/s ≈ 11.84.
Equivalent efficiency requirement: E ≥ 7500/8192 = 0.915527.
