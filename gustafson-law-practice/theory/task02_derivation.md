# Task 02 — Derivation of Gustafson's Law

**Setup.** Observe a run on P processors. Normalise its wall-clock time to 1:

(1) T_P = s′ + p′ = 1,

where s′ = time spent in the serial part (one processor busy, P−1 idle) and p′ = time spent in the parallel part (all P busy).
Let α ≡ s′, so p′ = 1 − α.

**Step 1 — Equivalent serial workload.** The parallel part, done by P processors in time p′, contains P·p′ units of single-processor work
(assuming perfect load balance and no parallel overhead). The serial part contains s′ units. A single processor executing the *same scaled
workload* needs

(2) T_1 = s′ + P·p′ = α + P(1 − α).

**Step 2 — Speedup.** S(P) = T_1/T_P = [α + P(1 − α)]/1 = α + P(1 − α).

**Step 3 — Algebra.**
S = α + P − αP = P − α(P − 1)  ∎ ⇒ (3) **S_G(P) = P − α(P − 1)**.

Equivalent forms: S = 1 + (1 − α)(P − 1) (add and subtract 1·(1−α)), and S = s′ + p′P (the form of the task sheet).

**Check.** P = 1 ⇒ S = 1 ✔; α = 0 ⇒ S = P ✔; α = 1 ⇒ S = 1 ✔; dS/dP = 1 − α (slope).
Efficiency: E = S/P = 1 − α(P−1)/P ∈ [1−α, 1].

**Assumptions to state honestly.** (i) The serial *time* s′ is independent of problem size; (ii) the parallel part scales perfectly
(no communication, no imbalance); (iii) T_1 is the *hypothetical* time of the scaled problem on one processor — in practice it is often not measurable
(memory!) and is extrapolated; (iv) the work in the parallel part grows exactly ∝ P.
