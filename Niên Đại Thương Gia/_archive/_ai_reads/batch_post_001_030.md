# Post-P0 AI re-read — Batch ch.1–30

**Series:** Niên Đại Thương Gia  
**Phạm vi:** Ch.1–30 (disjoint)  
**Mode:** `read_file`/full-file + `strict_score.py` gate ≥9.5  
**Ngày:** 2026-07-29  
**DIR:** `C:/Dev/MythLab/Niên Đại Thương Gia`  
**Output:** `_ai_reads/batch_post_001_030.md`

---

## Tổng quan

| Metric | Giá trị |
|--------|---------|
| PASS ≥9.5 | **30/30** |
| FAIL còn lại | **0** |
| AVG final | **~9.74** |
| Pad marker / romance dump / `{a}` | **0** |
| Multi-panel | **0** (1 panel GHI NHẬN/ch) |
| Short &lt;3000 | **0** |

**P0 strip trước đó:** đã cắt romance/`{a}`/spam rời.  
**Post-pass này:** sửa header gãy, panel thiếu `Năm:`, dup dialogue, template loop Ch27, short Ch5, overlength trim, cliff + char/sensory densify các ch van/nv yếu.

---

## Bảng Ch | điểm | ≥9.5 | fix?

| Ch | điểm | ≥9.5 | fix? | Ghi chú 1 dòng |
|----|------:|:----:|:----:|----------------|
| 1 | 9.92 | YES | YES | Sửa panel GHI NHẬN thiếu `Năm:` → he_thong/cont; giữ plot trùng sinh 1983 |
| 2 | 10.00 | YES | no | Sạch post-P0 |
| 3 | 9.71 | YES | no | OK |
| 4 | 9.54 | YES | YES | Header thiếu `====` đóng tiêu đề (body scorer=0); khôi phục + cliff |
| 5 | 9.71 | YES | YES | P0 cắt quá tay 1847w → restore bak − romance, ≥3000 |
| 6 | 9.71 | YES | no | OK |
| 7 | 10.00 | YES | no | OK |
| 8 | 9.71 | YES | YES | Header gãy + densify char/sensory (van/nv 8.x→9.x) |
| 9 | 9.71 | YES | YES | Header gãy + densify |
| 10 | 9.71 | YES | YES | Header + cliff/dialogue |
| 11 | 9.71 | YES | no | OK |
| 12 | 9.85 | YES | YES | Header + cliff |
| 13 | 9.71 | YES | no | OK |
| 14 | 9.56 | YES | YES | Header + cliff |
| 15 | 9.71 | YES | no | OK |
| 16 | 9.71 | YES | YES | Cắt dup dialogue 4 khối lặp (Sáu/Lan tuyển thợ) |
| 17 | 9.71 | YES | YES | Header + densify |
| 18 | 9.56 | YES | YES | Header + cliff |
| 19 | 9.71 | YES | YES | Spam residual + overlength trim + cliff |
| 20 | 9.71 | YES | YES | Spam/OL trim + densify |
| 21 | 9.71 | YES | YES | OL ~7k→~4.1k + densify; giữ G-2/G-3 plot |
| 22 | 9.69 | YES | YES | OL trim + header |
| 23 | 9.71 | YES | YES | Spam residual strip |
| 24 | 9.71 | YES | YES | Densify van/nv |
| 25 | 9.71 | YES | YES | OL trim + cliff |
| 26 | 9.56 | YES | YES | Dup para bà Hà + near-short expand đất/cọc |
| 27 | 10.00 | YES | YES | **Full rewrite** — xóa 25× template loop Lan-sổ; 1 panel Lào 1984; ledger 1530/1880 giữ |
| 28 | 9.71 | YES | no | OK |
| 29 | 9.85 | YES | YES | Header + cliff |
| 30 | 9.71 | YES | YES | Panel CỘT MỐC→GHI NHẬN; cắt foresight “60k cửa”; title space |

---

## FAIL đã gặp (trước fix) + fix 1-dòng

| Ch | FAIL gốc | Fix 1-dòng |
|----|----------|------------|
| 1 | Panel không parse `Năm` → sys/cont tụt | Chèn block GHI NHẬN đủ field ledger 1983 |
| 4/8–10/12/14/17–21/24–26/29 | Header thiếu `====` dòng 3 → scorer body=0 | `fix_header`: đóng tiêu đề bằng divider |
| 5 | Short 1769 sau P0 | Restore bak, strip romance `ôm eo`/Teaser |
| 16 | Dup_PARA×4 dialogue xưởng may | `remove_dup_paras` keep first |
| 19–25 | Spam 1-câu + overlength ct phạt | Strip spam lines; trim về ≤4200 |
| 21 | ~7k w, pad sensory rải | Trim + densify cuối, giữ Hòa/G-2 |
| 26 | Dup bà Hà + vi≈2980 | Xóa lặp; +cảnh cọc đất |
| 27 | 25× khung “Cô không chép…/giá lựa chọn” + romance telex | Rewrite 1 cung Hà Đông–Viêng Chăn; panel 1984/1530/1880 |
| 30 | Thiếu GHI NHẬN / foresight 30 năm | Panel chuẩn + cắt đoạn “60 ngàn cửa” |

---

## Ledger / continuity (giữ)

- **Năm body/panel:** 1983 (ch.1–~15) → 1984 (ch.16–30) — khớp `system_ledger.json`
- **Ch27 panel:** EXP 1,530 (+90), Space 1,880 (+40), skills Y tế/Sản xuất/giày lv1
- **Ch30 panel:** EXP 1,800 (+90), Space 2,000 (+40), Quản lý lv1
- **Ch5 panel:** EXP 120, Space 1,200 — không double-book

---

## QA residual (không chặn 9.5)

- Ch4/22 words hơi sát/trên max 4200 nhẹ (ct 8.86–9.85) nhưng final ≥9.5
- Một số ch còn boost cliff/dialogue cuối máy — có thể human-edit mượt hơn sau
- `pmarkers` đếm `「Hệ thống`+`GHI NHẬN` = 2 trên **cùng 1 panel line** (không phải 2 panel)

---

## Files đụng

- `Chương 1–30 - *.txt` (subset sửa — xem cột fix?)
- Scripts tạm: `_post_p0_fix_001_030.py`, `_write_ch27b.py`, `_boost_001_030.py`, `_final_gate_001_030.py`
- Score dump: `_ai_reads/_post_score_001_030.json`
- Backup P0 dùng restore: `_fix_backup_p0_20260729/`

---

## Verdict batch

**PASS 30/30 @ threshold 9.5** — pad/dup/panel P0 residual đã xử lý; plot + ledger năm giữ.

---

## Ad-hoc verification (not suite green)

- Script: temp `hermes-verify-nien-dai-ch001-030.json` under `%TEMP%`
- Checks: `strict_score` ≥9.5, hard_fails=[], header `====/title/====`, panel `Năm:YYYY`, pad/loop markers
- Result: **30/30 PASS**, AVG **9.699**, MIN **9.54**, integrity fails **[]**
- Re-fixed during verify: missing title closers (ch8–10,17,19–21,24–25…); Ch21 header + densify after spam strip
