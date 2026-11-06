# Task 15 — Energy Scaling under Gustafson's Model

## Conventions
Per node: **static power P_idle** (drawn always, whether working or not) and **dynamic power P_active** *above* static while computing (so a computing node draws P_idle + P_active). If the sheet's P_active
is instead meant as the *total* active power, replace P_active by P_active − P_idle below. Wall-clock time T is the same in all cases. α = serial fraction (time), S = S_G(P).

## One processor, time T
E�� = T·(P_idle + P_active) = E_static + E_dynamic with E_static = T·P_idle, E_dynamic = T·P_active. Work done: 1 unit.

## P processors, scaled workload, time T
Serial phase (αT): one node active, P−1 only static. Parallel phase ((1−α)T): all P active.
* Static: E_static(P) = P·T·P_idle
* Dynamic: E_dyn(P) = P_active·T·[α·1 + (1−α)·P] = P_active·T·S_G(P)
* **Total: E_P = T·[P·P_idle + P_active·S_G(P)]**. Work done: S_G(P) units.

## Comparisons
1. **Energy per unit of work:** e(P) = E_P/S_G = T[P_idle/E_G(P) + P_active] (E_G = efficiency S_G/P) vs. e(1) = T(P_idle + P_active).
   **Energy efficiency η(P) = e(1)/e(P) = (P_idle + P_active)/(P_idle/E_G + P_active)**, → (P_idle+P_active)/(P_idle/(1−α)+P_active) as P→∞.
2. **Same job on one core:** a core running the scaled job takes S_G·T and burns E_ser = S_G·T·(P_idle + P_active). Difference
   E_P − E_ser = T·P_idle·(P − S_G) = **T·P_idle·α(P−1) ≥ 0**: dynamic energy is identical; the parallel run pays only the static energy of idle nodes during the serial phase (plus nothing else in this ideal model, since total static scales with node-time P·T vs. S_G·T).
3. **Power proportionality:** if P_idle = 0 (perfect proportionality) η = 1 and energy ∝ work regardless of P. With P_idle > 0, η = 1 − O(α·P_idle/(P_idle+P_active)): the larger the idle-power share, the more serial fraction costs.
Example: P_idle = 100 W, P_active = 150 W, α = 0.04, P = 1024: E_G = 0.96004, η = 250/(100/0.96004 + 150) = 250/254.16 = 0.9836.
4. Shorter time to solution at constant power per work is a benefit: weak scaling does P-times more work in the same T with nearly proportional energy; strong scaling of a fixed job instead reduces T but static energy P·T·P_idle grows when E_A falls.
