# CS482 Practice Lab - Variant B: Scalability Diagnostics (Student 230103216)

Scalability Diagnostics: Granularity & IPC Contention (Karp-Flatt analysis).

## Files
| File | Purpose |
|---|---|
| `exp_a_granularity.py` | Experiment A: Collatz, 1,000,000 items, chunksize 1 vs 10,000, P = 1/2/4/8 |
| `exp_b_queue.py` | Experiment B: one `Queue.put` per item, 400,000 items |
| `exp_c_buffered.py` | Experiment C: local buffers, batch 10,000, 10,000,000 items |
| `bench_common.py` | Part 0 environment introspection + Sp / Ep / Karp-Flatt formulas |
| `build_results.py` | Generates `RESULTS_B.md` from measured `outputs/*.json` |
| `outputs/` | `exp_*_output.txt` (raw console output) and `exp_*_results.json` |

## Run (Windows, PyCharm terminal or Git Bash, from this folder)
```
python exp_a_granularity.py
python exp_b_queue.py
python exp_c_buffered.py
python build_results.py
```
Close other heavy programs and plug in the laptop while benchmarking. Add `--quick` to any script for a tiny
smoke test (it writes no `.txt` and `build_results.py` rejects its JSON).

All scripts use the `spawn` start method (the Windows default) and guard with `if __name__ == "__main__":`.
Part 0 information (Python, OS, CPU, `os.cpu_count()`, `mp.cpu_count()`, start method) is printed at the top of each script.
