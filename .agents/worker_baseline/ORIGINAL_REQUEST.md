## 2026-07-31T12:32:55Z
You are a teamwork_preview_worker assigned to execute the 360-chapter quality audit and rewrite project for 'Niên Đại Thương Gia'.

Target project directory: c:\Dev\XLab_MTC\Niên Đại Thương Gia
Working directory: c:\Dev\XLab_MTC\.agents\worker_baseline

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Task Instructions:
1. Setup your working directory at `c:\Dev\XLab_MTC\.agents\worker_baseline` and create `progress.md` with your liveness timestamp.
2. Inspect `c:\Dev\XLab_MTC\Niên Đại Thương Gia\audit_all.py`. Note that line 139 currently defaults to `range(1, 71)`. Update `audit_all.py` so that its default CLI run audits all 360 chapters (`range(1, 361)`), and returns detailed metrics for all 360 chapters.
3. Run `python audit_all.py` on all 360 chapters. Save initial audit baseline results to understand which chapters score < 9.5/10.
4. For every chapter scoring < 9.5 or failing quality thresholds:
   - Perform genuine literary content enhancements directly in the `.txt` chapter files in `c:\Dev\XLab_MTC\Niên Đại Thương Gia`.
   - Ensure word count is within [3,000, 4,200] words.
   - Boost sensory details (`sens_d` >= 3.5) and character action details (`char_d` >= 5.0).
   - Ensure at least 10 lines of natural dialogue per chapter.
   - Eliminate all AI tics, filler markers, and repeated lines (`maxrep <= 1`).
   - Preserve standardized headers (`============================================================`, `Chương X : <Title>`) and exactly 1 `GHI NHẬN` log table per chapter.
5. Re-run `audit_all.py` on all 360 chapters until 100% of chapters achieve score >= 9.5/10.
6. Generate `c:\Dev\XLab_MTC\Niên Đại Thương Gia\score95_final.json` containing detailed per-chapter scores (1 to 360), verifying `all_pass: true` and `min_score >= 9.5`.
7. Write your execution report to `c:\Dev\XLab_MTC\.agents\worker_baseline\handoff.md` following the Handoff Protocol (Observation, Logic Chain, Caveats, Conclusion, Verification Method with audit output).
8. Send a message to the orchestrator with your results and handoff path.
