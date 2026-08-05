# Context: Niên Đại Thương Gia Quality Audit & Rewrite

## Rules & Standards
- Target Project Directory: `c:\Dev\XLab_MTC\Niên Đại Thương Gia`
- Total Chapters: 360 chapters (`Chương 1 - *.txt` to `Chương 360 - *.txt`).
- Quality Evaluation Tool: `audit_all.py` (and independent verification).
- Score Threshold: 100% of chapters MUST achieve composite score >= 9.5/10.
- Mandatory Outputs: `score95_final.json` containing detailed per-chapter audit scores.

## Key Audit Criteria Weights & Deductions (audit_all.py)
- **Word Count**: Must be within [3,000, 4,200] words. Deductions applied if < 3000 or > 4200.
- **Sensory Density**: Sensory words (`mùi`, `tiếng`, `ánh`, `nắng`, `mưa`, `gió`, `ấm`, `lạnh`, `khói`, `vị`, `chát`, `mặn`, `ẩm`, `rít`, `thơm`) >= 3.5 per 1,000 characters.
- **Character Action Words Density**: Character words (`mắt`, `tay`, `cười`, `khóc`, `gật`, `thở`, `nhìn`, `môi`, `vai`, `giọng`) >= 5.0 per 1,000 characters.
- **Dialogue Lines**: Minimum 10 dialogue lines (lines starting with quotes `"` or `“` or dash `—` or `–`).
- **AI Tics & Markers**: Zero forbidden markers (`### Lớp sâu`, `### Nhịp`, `Trong nhật ký riêng số`, `chi tiết số...`, etc.) and zero AI tics (`se lạnh lúc tờ mờ`, `sổ trong túi vải`, `Ve kêu rả rích...`).
- **Repetition**: Zero repeated lines (`maxrep <= 1`).
- **Header & Ledger**: File must start with `============================================================`, contain `Chương X : <Title>`, and include system panel `GHI NHẬN` (exactly 1 panel).
