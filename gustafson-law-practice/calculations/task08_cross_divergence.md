# Task 08 — Amdahl vs. Gustafson (s = α = 0.08, P = 128)

## Step-by-step
* Amdahl: S_A = 1 / (0.08 + 0.92/128) = 1 / (0.08 + 0.0071875) = 1 / 0.0871875 = **11.4695**
* Gustafson: S_G = 128 − 0.08·127 = 128 − 10.16 = **117.8400**
* Absolute difference: S_G − S_A = **106.3705**
* Speedup ratio: S_G / S_A = **10.2742**
* Efficiencies: E_A = 0.0896 (8.96%), E_G = 0.9206 (92.06%)

## Percentage-discrepancy convention (explicit)
Primary: **Δ% = (S_G − S_A) / S_A × 100 = 927.42%** (Amdahl is the baseline; Gustafson is 927% larger).
Alternative (Gustafson as baseline): (S_G − S_A)/S_G × 100 = 90.27% (Amdahl underestimates by that fraction).
Always state the baseline: the two conventions give very different numbers.

## Why the models diverge
They answer different questions. Amdahl keeps the **total work fixed**: the serial part (8% of the 1-processor time) stays
8% of T(1) while the parallel part shrinks, so S_A → 1/s = 12.5 (already 91.8% of the cap at P = 128).
Gustafson keeps the **parallel time fixed** and lets work grow with P; the serial part is 8% of the *parallel-machine* time,
so the equivalent serial time is s + pP = 0.08 + 0.92·128 = 117.84 (normalised units).
As P → ∞, S_A saturates at 12.5 while S_G grows without bound with slope 0.92, so the gap widens linearly.
Setting s = α is itself an assumption: the same number means different things (fraction of T(1) vs. fraction of T(P)).
