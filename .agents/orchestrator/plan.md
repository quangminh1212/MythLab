# Project Plan: Niên Đại Thương Gia — 360 Chapter Quality Audit & Rewrite

## Overview
Quality assessment, rewriting, and verification of all 360 chapters of the novel "Niên Đại Thương Gia" to meet international literary standards R1, R2, R3 with 100% of chapters scoring >= 9.5/10 on audit_all.py.

## Quality Criteria (R1)
1. **Prose & Literary Quality (Score weight 1.0)**: Word count 3,000–4,200 words, no AI tics/filler phrases, rich sensory details (smell, sound, light, temperature, texture).
2. **Plot & Structure (Score weight 1.0)**: Engaging plot, title matching content, natural climax/transitions, standardized header & system log table `GHI NHẬN`.
3. **Characterization & Dialogue (Score weight 1.0)**: Minimum 10 natural dialogue lines per chapter, distinct character traits (Hùng, Lan, bà Hà, Hạnh, Minh, etc.).
4. **Continuity & System Integrity (Score weight 1.5)**: System ledger alignment, no timeline contradictions, standard header format `Chương X : <Title>`.
5. **Zero Filler & High Density (Score weight 2.0)**: No padding markers, no repetitive lines (`maxrep <= 1`), high information density.

Overall weighted formula in `audit_all.py`:
`Score = (Prose * 1.0 + Plot * 1.0 + Char * 1.0 + Cont * 1.5 + Filler * 2.0) / 6.5`
Target: **100% of chapters >= 9.5/10**.

## Milestones & Decomposition

| Milestone | Scope | Description | Target | Status |
|-----------|-------|-------------|--------|--------|
| **M0** | Baseline Audit | Run `audit_all.py` across all 360 chapters (updating loop range if needed), collect initial score list & identify all chapters < 9.5. | Baseline inventory json | PLANNED |
| **M1** | Part 1 (Ch 1-60) | Audit & rewrite any chapters in 1-60 scoring < 9.5 until all >= 9.5. | 60/60 >= 9.5 | PLANNED |
| **M2** | Part 2 (Ch 61-120) | Audit & rewrite any chapters in 61-120 scoring < 9.5 until all >= 9.5. | 60/60 >= 9.5 | PLANNED |
| **M3** | Part 3 (Ch 121-180) | Audit & rewrite any chapters in 121-180 scoring < 9.5 until all >= 9.5. | 60/60 >= 9.5 | PLANNED |
| **M4** | Part 4 (Ch 181-240) | Audit & rewrite any chapters in 181-240 scoring < 9.5 until all >= 9.5. | 60/60 >= 9.5 | PLANNED |
| **M5** | Part 5 (Ch 241-300) | Audit & rewrite any chapters in 241-300 scoring < 9.5 until all >= 9.5. | 60/60 >= 9.5 | PLANNED |
| **M6** | Part 6 (Ch 301-360) | Audit & rewrite any chapters in 301-360 scoring < 9.5 until all >= 9.5. | 60/60 >= 9.5 | PLANNED |
| **M7** | Final Verification & Report | Run full audit for all 360 chapters, verify 100% >= 9.5, generate `score95_final.json`, and perform forensic audit verification. | `score95_final.json` produced | PLANNED |

## Orchestration Topology & Strategy
- **Worker**: Executes audit scripts, identifies failing chapters, applies targeted chapter rewrites (enhancing sensory descriptions, adding dialogues, fixing word count to 3000-4200, eliminating AI tics/filler/repetition), and verifies score >= 9.5. Updates `audit_all.py` so that default CLI run audits all 360 chapters.
- **Reviewer**: Independently re-audits chapters, verifies line count, dialogue count, word count, sensory density, header compliance, ledger integrity.
- **Forensic Auditor**: Performs static analysis & execution verification to ensure no hardcoded score falsification or dummy output cheating exists.
