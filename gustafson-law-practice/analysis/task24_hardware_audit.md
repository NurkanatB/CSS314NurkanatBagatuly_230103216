# Task 24 — Hardware Audit and Empirical-vs-Theoretical Discrepancy

> **Important:** everything below was measured in the sandbox where the repository was generated (a small virtual machine), **not** on your computer.
> Re-run `python benchmarks/hardware_info.py`, the benchmark and the fit on your own machine to obtain meaningful scaling data (see README).

## Detected hardware (output of `benchmarks/hardware_info.py`)
- **CPU model:** Intel(R) Xeon(R) Processor @ 2.10GHz
- **Physical cores:** 1
- **Logical processors:** 1
- **Usable by this process:** 1
- **Architecture:** x86_64
- **Operating system:** Linux 6.18.44-fc-v242 (#1 SMP PREEMPT_DYNAMIC @0)
- **Python:** 3.12.3
- **Total memory (GiB):** 3.90
- **Available memory (GiB):** 3.57
- **Cache sizes:** L1d cache:                               48 KiB (1 instance); L1i cache:                               32 KiB (1 instance); L2 cache:                                2 MiB (1 instance); L3 cache:                                260 MiB (1 instance)
- **NUMA:** NUMA node(s):                            1; NUMA node0 CPU(s):                       0
- **Memory channels:** not detected (not reliably exposed without root/dmidecode)
- **CPU frequency:** 2100 MHz


Cache sizes are reported by `lscpu` as seen by the virtual machine (the 260 MiB L3 is the host's shared cache exposed to the guest, not private to this VM). Memory channels, memory speed and thermal sensors were **not detected** (virtualised environment, no root/dmidecode).

## Benchmark actually executed
Workload: Monte Carlo π, 10,000,000 samples per worker (constant per worker), worker counts 1, 2, 4, 8, 16, 5 repetitions each (25 runs), spawn-based `ProcessPoolExecutor`, pool created/warmed before timing. All runs passed the statistical correctness check (π within 5σ). Raw data: `benchmarks/results.csv`.

| workers P | mean T (s) | std T (s) | scaled speedup S = P·T(1)/T(P) | std. error |
|---:|---:|---:|---:|---:|
| 1 | 0.0959 | 0.0058 | 1.000 | 0.038 |
| 2 | 0.2087 | 0.0115 | 0.919 | 0.034 |
| 4 | 0.5172 | 0.0652 | 0.741 | 0.046 |
| 8 | 1.0044 | 0.0741 | 0.764 | 0.033 |
| 16 | 2.2499 | 0.1224 | 0.682 | 0.025 |

Regression S = 1 + (1−α)(P−1), OLS through the origin on (S−1) vs. (P−1): **slope ≈ −0.026 ⇒ "α" ≈ 1.026 (R² < 0)**. This value is outside the physical range [0, 1] and must not be interpreted as a serial fraction.

## Why the data disagree with Gustafson's curve
The machine has **one logical processor**. With P workers on one core the P tasks time-slice, so T(P) ≈ P·T(1) and the scaled speedup is ≈ 1 for every P (measured 0.68–1.0, the extra loss being context switching, cache/TLB pollution, and process-scheduler overhead). That is *oversubscription*, not weak scaling: the model assumption "P independent processors" is violated, so the regression correctly returns ≈ "no parallel gain" (α ≈ 1). The plot (`plots/scaling_comparison.*`, `plots/weak_scaling_results.png`) shows ideal S=P, the Gustafson curve for the fitted α (clipped to [0,1] → α=1, i.e. S=1), Amdahl with the same s and the measured points with standard errors; theoretical curves for sensible α are in `plots/scaling_comparison_theory.*` and `plots/efficiency_comparison.*`.
**No conclusion about the real α of this workload can be drawn from this run.** A multi-core host is required.

## Effects to consider on a real multi-core machine
* **CPU scheduling:** more workers than logical CPUs ⇒ time slicing (as seen here); pin affinity or cap workers at the CPU count. Hyper-threads share execution units: P > physical cores gives well below 2× gain.
* **Thermal throttling / turbo:** all-core turbo frequency is lower than single-core turbo; sustained loads on laptops throttle, so T(P) rises with P and apparent α increases. Record frequency/temperature and let the machine cool between runs.
* **Memory bandwidth:** this workload streams ~16 MB chunks (random numbers) — bandwidth-light but not zero; bandwidth-bound kernels saturate at a few cores and break weak scaling.
* **NUMA:** on multi-socket systems remote-memory access (30–100% slower) appears when workers span sockets; first-touch placement and `numactl`/affinity matter. This VM reports one NUMA node.
* **Multiprocessing overhead:** process creation, pickling arguments/results, and result collection are serial in the parent. We exclude pool start-up from timing (pool warm-up), but the dispatch/collection remains in the timed region.
* **Windows process startup:** Windows has no `fork`; each worker is a fresh interpreter importing NumPy (hundreds of ms to seconds), which is why the code uses `spawn`, `if __name__ == "__main__"` and a warm-up before timing. Defender scanning and power plans can add noise.
