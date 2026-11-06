# Task 05 — The Historical nCUBE Experiment (1988)

> Facts below are drawn from the sources listed at the end. Details not confirmed from those sources (e.g. per-node memory size, clock rate) are
> deliberately **not stated**; consult §3 of the SIAM paper for the machine parameters.

## Setting
At Sandia National Laboratories, J. L. Gustafson, G. R. Montry and R. E. Benner developed three full-scale applications — wave mechanics (baffled-surface wave
simulation with explicit finite differences), fluid dynamics (unstable flow with flux-corrected transport) and structural analysis (beam stress using conjugate gradients) —
on a **1024-processor MIMD hypercube (nCUBE)**. A hypercube of 1024 = 2¹⁰ nodes has each node connected to 10 neighbours; the machine was driven by a host processor with the
nodes executing the parallel program (the paper details host and node algorithms). Message passing, not shared memory, was the programming model.

## Reported measurements
* **Fixed problem size:** speedups of **502 to 637** on 1024 processors, with serial component s of about 0.0006–0.001 (SIAM abstract/introduction).
* **Fixed problem size per processor (scaled):** speedups of **1009 to 1020**, with the equivalent serial component dropping to 3–10 parts per million (SIAM paper).
* **Gustafson's CACM note** (*Reevaluating Amdahl's Law*, May 1988): for three applications with serial fraction s = 0.4–0.8% (parallel-machine frame), the scaled
  speedups were **1021** (beam stress, CG), **1020** (baffled-surface wave, finite differences) and **1016** (unstable fluid flow, FCT).
* Sustained performance 70–130 MFLOPS (SIAM abstract). A related Sandia paper on the structural problem reports 502 (fixed size), 987 (fixed time), 1019 (fixed size per processor).

## Comparison with Amdahl's prediction
With s = 0.004 (the 0.4% quoted in the task sheet) Amdahl would predict S_A(1024) = 1/(0.004 + 0.996/1024) = **201.1**; with s = 0.008, **111.5**; the Amdahl cap
is 1/s = 250 and 125 respectively. Gustafson's formula with the same numbers: S_G = 1024 − 0.004·1023 = **1019.9** and 1024 − 0.008·1023 = **1015.8**,
consistent with the reported 1016–1021. (Our computation; Gustafson's CACM text shows the same agreement.)

## Why scaled workloads permit larger speedups
The 0.4% was a serial fraction of the *parallel* run on the scaled problem. Enlarging the problem (finer mesh, more particles) with P keeps the parallel run time constant,
the parallel part grows ~P, while setup/host-side serial work is nearly independent of N. In Amdahl's frame the same fixed absolute serial time becomes ever smaller relative
to T(1) of the larger problem. Gustafson's explanation: Amdahl's implicit assumption that the problem size is independent of P "may not be valid for large parallel ensembles" — i.e. the serial fraction
is not a property of the program alone but of the (program, problem size, machine size) triple.
Important nuance: the paper also gives the fixed-size results (502–637) — the same machine is *both* bounded by Amdahl for a fixed problem and near-linear for the scaled one.
Secondary sources (e.g. the Academia.edu record of the paper) state that this work received the Gordon Bell Award and the Karp Prize; verify the exact award year before citing it.

## References
1. G. M. Amdahl, "Validity of the single processor approach to achieving large scale computing capabilities", AFIPS Conf. Proc. 30, 1967, pp. 483–485.
2. J. L. Gustafson, "Reevaluating Amdahl's Law", Commun. ACM 31(5), 1988, pp. 532–533.
3. J. L. Gustafson, G. R. Montry, R. E. Benner, "Development of parallel methods for a 1024-processor hypercube", SIAM J. Sci. Stat. Comput. 9(4), 1988, pp. 609–638, doi:10.1137/0909041.
4. R. E. Benner, J. L. Gustafson, G. R. Montry, "Development and analysis of scientific application programs on a 1024-processor hypercube", SAND 88-0317, Sandia National Laboratories, Feb. 1988.
5. OSTI record 6525354, "A structural analysis algorithm for massively parallel computers" (Sandia) — three speedup definitions.
