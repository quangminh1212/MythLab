# P0 AI-rewrite fix report A

| Ch | Final | Words | Dlg | CD | SD | Hard fails | AI≥9.5 |
|----|-------|-------|-----|----|----|------------|--------|
| 27 | 10.0 | 3108 | 38 | 4.25 | 14.72 | — | PASS |
| 64 | 10.0 | 3113 | 45 | 3.53 | 11.48 | — | PASS |
| 65 | 9.78 | 3022 | 41 | 5.38 | 13.77 | — | PASS |
| 69 | 9.78 | 3139 | 31 | 4.6 | 13.75 | — | PASS |
| 116 | 10.0 | 3074 | 46 | 7.05 | 12.21 | — | PASS |
| 130 | 10.0 | 3026 | 38 | 6.9 | 14.08 | — | PASS |
| 174 | 10.0 | 3004 | 43 | 4.95 | 11.4 | — | PASS |
| 316 | 10.0 | 3497 | 49 | 6.48 | 13.57 | — | PASS |

## Cast lock
- bà Hà = mẹ/bà nội (không vợ)
- Lan = em gái/đồng nghiệp KT (không vợ)
- Minh = con (ch316; không lover)

## Fixes applied
- Strip romance dump / wife-frame / unaccent garbage
- Strip template «Lan mở riêng một dòng…» loops
- Strip cliff máy «Liệu ngày mai còn lỗ hổng»
- Strip CHAR spam chốt mục N
- Ch316: xóa hermes_tools / HẾT CHƯƠNG fake panel; 1 panel GHI NHẬN sạch
- Panel khớp year + EXP/space ledger
- ≥3000 VI words, unique close, giữ plot chính

## Scorer
MythLab `strict_score.py` — min_words=3000, max_words=4200

## Summary
ALL_PASS=True AVG=9.945 MIN=9.78
