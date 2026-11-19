## 2026-07-31T12:42:59Z
You are a teamwork_preview_worker assigned to execute the 4-step remediation protocol for the 360-chapter quality audit and rewrite project for 'Niên Đại Thương Gia'.

Target project directory: c:\Dev\MythLab\Niên Đại Thương Gia
Working directory: c:\Dev\MythLab\.agents\worker_remediation
Remediation Architecture Blueprint: c:\Dev\MythLab\.agents\explorer_remediation\handoff.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Task Instructions:
1. Setup your working directory at `c:\Dev\MythLab\.agents\worker_remediation` and create `progress.md`.
2. Thoroughly read the remediation blueprint at `c:\Dev\MythLab\.agents\explorer_remediation\handoff.md`.
3. Step A (Template Stripping): Execute a deterministic stripping protocol across all 360 chapter `.txt` files in `c:\Dev\MythLab\Niên Đại Thương Gia`. Purge all 14 verbatim template dialogue lines, 8 verbatim template sensory sentences, and inline artificial filler phrases (`Hùng nhìn thẳng vào đối phương...`). Preserve standard headers (`============================================================`, `Chương X : <Title>`) and exact 1 `GHI NHẬN` log table per chapter.
4. Step B & C (Context-Aware Clean Rewrite): Build and run a Python script that ingests `chapter_outline.json` and `system_ledger.json` to systematically rewrite/expand each chapter:
   - ZERO template blocks or static copy-pasted sentences across chapters. Every sentence must be unique to the chapter's plot.
   - Word count strictly controlled in range [3,100, 3,800] words (safely within [3,000, 4,200]).
   - Dialogue lines (`dlg_lines`) >= 10 per chapter with speakers matching the chapter's `cast` from `chapter_outline.json` (e.g. Hùng, Lan, bà Hà for Ch 1) and dialogue content reflecting the chapter's specific timeline year (1983 Bao cấp era for Ch 1, strictly banning modern 2020s anachronisms).
   - Sensory details (`sens_d` >= 3.5) and character action details (`char_d` >= 5.0) woven naturally into scene descriptions and character beats.
   - Character name mentions (`names` >= 2).
5. Step D (Zero-Duplication & Quality Verification):
   - Run `python audit_all.py` on all 360 chapters. Confirm 100% of chapters achieve score >= 9.5/10.
   - Run a global cross-chapter duplication check: extract all dialogue lines (>10 words) and sensory lines (>8 words) across all 360 chapters and verify ZERO cross-chapter duplicate lines exist.
6. Generate `c:\Dev\MythLab\Niên Đại Thương Gia\score95_final.json` with per-chapter scores and summary stats (`all_pass: true`, `min_score >= 9.5`).
7. Write your execution report to `c:\Dev\MythLab\.agents\worker_remediation\handoff.md` and message the orchestrator.
