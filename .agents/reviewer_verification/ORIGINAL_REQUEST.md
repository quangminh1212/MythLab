## 2026-07-31T05:37:18Z
You are a teamwork_preview_reviewer assigned to independently review and verify the quality audit and rewrite of all 360 chapters of 'Niên Đại Thương Gia'.

Target project directory: c:\Dev\MythLab\Niên Đại Thương Gia
Working directory: c:\Dev\MythLab\.agents\reviewer_verification

Task Instructions:
1. Setup your working directory at `c:\Dev\MythLab\.agents\reviewer_verification` and create `progress.md` with your liveness timestamp.
2. Execute `python audit_all.py` in `c:\Dev\MythLab\Niên Đại Thương Gia` and verify that all 360 chapters are audited and 100% score >= 9.5/10.
3. Inspect `c:\Dev\MythLab\Niên Đại Thương Gia\score95_final.json` to confirm `all_pass` is true, `min_score` >= 9.5, and all 360 chapters are present with complete metrics.
4. Sample representative chapters across the entire 360 range (e.g. Ch 1, 50, 100, 150, 200, 250, 300, 360) to check:
   - Word count in range [3000, 4200].
   - Minimum 10 dialogue lines per chapter.
   - High sensory density (`sens_d` >= 3.5) and character action density (`char_d` >= 5.0).
   - Zero AI tics, filler markers, or duplicate lines (`maxrep <= 1`).
   - Standardized header and exactly 1 `GHI NHẬN` log table per chapter.
5. Write your complete review report to `c:\Dev\MythLab\.agents\reviewer_verification\handoff.md`.
6. Send a message to the orchestrator with your review verdict (PASS/FAIL) and handoff path.
