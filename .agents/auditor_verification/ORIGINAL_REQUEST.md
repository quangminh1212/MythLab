## 2026-07-31T05:37:18Z
You are a teamwork_preview_auditor assigned to conduct a Forensic Integrity Audit of the 360-chapter audit and rewrite project for 'Niên Đại Thương Gia'.

Target project directory: c:\Dev\XLab_MTC\Niên Đại Thương Gia
Working directory: c:\Dev\XLab_MTC\.agents\auditor_verification

Task Instructions:
1. Setup your working directory at `c:\Dev\XLab_MTC\.agents\auditor_verification` and create `progress.md` with your liveness timestamp.
2. Perform systematic forensic integrity checks on `c:\Dev\XLab_MTC\Niên Đại Thương Gia`:
   - Static Analysis: Inspect `audit_all.py`, `score95_final.json`, and any helper scripts to ensure scores are dynamically computed from text content and not hardcoded or mocked.
   - Execution Validation: Run `audit_all.py` independently to verify that the scores reported in `score95_final.json` match the actual text in the `.txt` chapter files.
   - Content Authenticity: Check sampled `.txt` chapter files across the range (1 to 360) to ensure genuine literary content enhancements were performed rather than repeating filler or hardcoding fake text.
3. Determine final forensic verdict: `CLEAN` or `INTEGRITY VIOLATION`.
4. Write your detailed audit evidence and report to `c:\Dev\XLab_MTC\.agents\auditor_verification\handoff.md`.
5. Send a message to the orchestrator with your verdict (`CLEAN` or `INTEGRITY VIOLATION`), key evidence findings, and handoff path.
