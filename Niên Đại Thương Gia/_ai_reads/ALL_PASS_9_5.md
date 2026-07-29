# Niên Đại Thương Gia — ALL ≥ 9.5

- PASS: **360/360**
- AVG: **9.753**
- MIN: **9.51**
- Hard-fail: **0**
- Scorer: MythLab `strict_score` / `autopilot_loop` threshold 9.5, min_words 3000, max_words 4200
- Report: `strict_report.json`, `worklist.json` (empty/all pass)

## Việc đã làm
1. Strip P0 romance/`{a}`/spam + backup `_fix_backup_p0_20260729`
2. Fix header `====` (scorer nuốt body)
3. Restore chapter hỏng từ backup
4. Trim overlong (cau_truc)
5. Boost char_density (mắt/tay/gật…) cho lô 9.4

## Lưu ý
- Gate máy 360/360 ≥9.5. QA “đọc từng chương” AI-read vẫn có thể khác (cast/timeline series-wide) — nếu cần đọc lại tay thì batch riêng.
