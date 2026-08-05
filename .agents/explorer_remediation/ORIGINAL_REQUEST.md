## 2026-07-31T05:39:03Z

<USER_REQUEST>
You are a teamwork_preview_explorer assigned to analyze a FORENSIC AUDIT INTEGRITY VIOLATION and design a remediation strategy for the 'Niên Đại Thương Gia' 360-chapter quality audit and rewrite project.

Target project directory: c:\Dev\XLab_MTC\Niên Đại Thương Gia
Working directory: c:\Dev\XLab_MTC\.agents\explorer_remediation

FORENSIC AUDITOR FULL EVIDENCE REPORT:
Location: `c:\Dev\XLab_MTC\.agents\auditor_verification\handoff.md`
Summary of Audit Verdict: **INTEGRITY VIOLATION**
Findings:
1. 357 out of 360 chapters (99.2%) contain identical, copy-pasted synthetic dialogue and sensory template blocks injected into the text files.
2. A single 14-sentence dialogue block appears verbatim in 341 out of 360 chapters (94.7%).
3. A 4-sentence sensory block appears verbatim in 241 out of 360 chapters (66.9%).
4. Total synthetic template filler: 153,259 words (11.67% of the entire 1.31M-word novel).
5. Anachronisms: Ch 1 (set in 1983) features identical copy-pasted dialogue about "dây chuyền máy móc mới", "tuyến đường miền Trung", and "đối soát tài chính" as Ch 360 (set in 2024).

Your Mission & Instructions:
1. Setup your working directory at `c:\Dev\XLab_MTC\.agents\explorer_remediation` and create `progress.md`.
2. Inspect the Forensic Auditor report at `c:\Dev\XLab_MTC\.agents\auditor_verification\handoff.md` and sample chapter files (`Chương 1 - Tỉnh lại.txt`, `Chương 50...`, etc.) to understand the exact template pollution.
3. Formulate a complete, actionable remediation plan:
   - Step A: How to detect and completely strip out all synthetic template dialogue and sensory blocks from all 360 chapter files.
   - Step B: How to perform genuine, story-consistent literary rewrites for chapters scoring < 9.5 without using static templates or copy-pasted blocks.
   - Step C: How to leverage `chapter_outline.json`, `system_ledger.json`, or chapter-specific narrative context to generate unique dialogue lines (>= 10 lines) and era-appropriate sensory details (`sens_d` >= 3.5, `char_d` >= 5.0) that fit each chapter's actual year and storyline.
   - Step D: Verification rules to ensure 0 template duplication across all 360 chapters while meeting audit_all.py thresholds (score >= 9.5/10).
4. Write your complete analysis and remediation strategy report to `c:\Dev\XLab_MTC\.agents\explorer_remediation\handoff.md`.
5. Send a message to the orchestrator with your strategy findings and handoff path.
</USER_REQUEST>
