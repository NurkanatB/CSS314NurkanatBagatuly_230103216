# weak_scale_bench — empirical weak-scaling benchmark (Task 22)

Workload: Monte Carlo estimate of π. Each worker processes a **constant** number of samples (`--samples-per-worker`); total work = P × that.
Pure Python + NumPy, no compilation required. Works on Windows and Linux (uses the `spawn` start method and a `__main__` guard).

```bash
# from the repository root
pip install -r requirements.txt
python -m benchmarks.weak_scale_bench.runner                       # workers = 1,2,4,... up to detected CPUs
python -m benchmarks.weak_scale_bench.runner --workers 1 2 4 6 8 --repetitions 5 --samples-per-worker 20000000
python benchmarks/fit_gustafson.py                                  # regression + plots
```
* Timing: `time.perf_counter()` around the parallel section; pool start-up and a warm-up task are excluded.
* Correctness: π estimate must lie within 5 standard errors of π, otherwise the run aborts.
* Use worker counts ≤ the number of logical CPUs (printed at start); more workers are oversubscribed and invalidate the weak-scaling interpretation.
* Close other applications; on laptops use mains power and let the CPU cool between sessions.
