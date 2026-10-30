# Git steps (Git Bash, run inside your cloned repo)
```bash
cd ~/PycharmProjects/CSS314NurkanatBagatuly_230103216      # your existing clone
git status
git fetch origin
git branch -a                                              # make sure variant-b-230103216 doesn't already exist
git checkout -b variant-b-230103216                        # (use: git checkout variant-b-230103216 if it exists)
cp -r /path/to/CSS482_Variant_B .                          # or copy the folder in with Explorer

git add CSS482_Variant_B/bench_common.py CSS482_Variant_B/README.md
git commit -m "chore: initialize Variant B environment and branch"
git add CSS482_Variant_B/exp_a_granularity.py CSS482_Variant_B/outputs/exp_a_output.txt
git commit -m "feat: implement granularity benchmark and Karp-Flatt analysis"
git add CSS482_Variant_B/exp_b_queue.py CSS482_Variant_B/outputs/exp_b_output.txt
git commit -m "feat: reproduce IPC queue contention and negative scaling"
git add CSS482_Variant_B/exp_c_buffered.py CSS482_Variant_B/outputs/exp_c_output.txt
git commit -m "feat: optimize IPC using local buffer aggregation"
git add CSS482_Variant_B/RESULTS_B.md CSS482_Variant_B/build_results.py CSS482_Variant_B/outputs
git commit -m "docs: add Variant B experimental results and final analysis"
git push -u origin variant-b-230103216
```
The handout also asks for `RESULTS_B.md` in the repo root; if your instructor wants it there, copy it
(`cp CSS482_Variant_B/RESULTS_B.md .`) and add it too. No force-push is needed or used.
If push asks for credentials: a browser sign-in window from Git Credential Manager appears - sign in to GitHub
as NurkanatB. If none appears, use a Personal Access Token (GitHub > Settings > Developer settings) as the password.
