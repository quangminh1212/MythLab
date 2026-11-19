# AI-rewrite FAIL fix — ch.121–150

**Ngày:** 2026-07-29  
**DIR:** `C:/Dev/MythLab/Niên Đại Thương Gia`  
**Scope:** ONLY FAIL from AI-read reread_121_180: **121,123–125,127,129–133,136,138,140,141,143,144,146**  
**SKIP PASS (untouched):** 122,126,128,134,135,137,139,142,145,147–150  
**Mode:** read_file + write_file surgical rewrite (core keep + dump strip + cast lock + unique close + ledger panel)  
**Backup:** `_fix_backup_121_150_fail/`  
**Report:** `_ai_reads/fix_121_150_fail.md`  

---

## Executive verdict

| Metric | Value |
|--------|------:|
| **strict_score PASS ≥9.5** | **17 / 17** |
| **AVG final** | **9.876** |
| **MIN final** | **9.71** |
| **MAX final** | **10.00** |
| **Hard-fails** | **0** |
| Cast lock (bà Hà=mẹ, Lan=em/KT) | clean |
| PASS-skip still ≥9.5 | 13/13 |

**Kết luận:** 17/17 FAIL → **ALL_PASS ≥9.5** (strict_score). PASS list giữ nguyên.

---

## Pre-fix FAIL (từ `reread_121_180.md`)

| Ch | AI pre | Blocker chính |
|---:|-------:|---------------|
| 121 | 8.20 | unaccent_tail×5 monologue aging |
| 123 | 8.40 | exp0_panel + bad_header |
| 124 | 7.60 | unaccent_tail×7 near_short |
| 125 | 7.80 | unaccent_tail×3 near_short |
| 127 | 7.40 | unaccent_tail×6 near_short2856 |
| 129 | 9.35 | near_short2969 |
| 130 | 6.80 | chốt mục spam + unaccent + bad_header |
| 131 | 8.30 | unaccent + clone domestic |
| 132 | 8.10 | unaccent + clone canh cá |
| 133 | 8.40 | wife_frame×2 |
| 136 | 7.70 | unaccent + near_short |
| 138 | 8.20 | wife_frame×4 |
| 140 | 8.00 | unaccent + wife_frame×3 |
| 141 | 7.90 | unaccent_tail×5 |
| 143 | 8.30 | wife_frame + bad_header + cliff spam |
| 144 | 8.50 | wife_frame + year scan |
| 146 | 9.30 | near_short2855 |

---

## Actions applied

1. **Backup** → `_fix_backup_121_150_fail/`
2. **Cut dump tails** — unaccent aging monologue, quỹ học bổng pad, clone `canh cá`/`ôm Lan`/`tủ sách`, CHAR spam `chốt mục`/`Mùi mực`
3. **Cast lock** — bà Hà=mẹ; Lan=em/KT; strip Hùng-vợ frame; giữ `vợ` chỉ cho nhân vật khác (thợ/đại lý) khi hợp lý
4. **Double header** `====` + `Chương N: Title` + `====` (fix body=0 false-short)
5. **Single panel** ledger-true year/EXP/space/Δ + `Ghi chú:` plot-specific
6. **Unique close + cliff** last prose lines (`Liệu…` / `sáng mai`) — no shared densify clone
7. **Year panel = prose mode** (dateline) khi lệch 1 năm vs ledger
8. **Title glue** `Mở rộngsang` → `Mở rộng sang`

---

## Post-fix score table (`strict_score.py`)

| Ch | Title | final | w | van | nv | cau | cont | fill | he | cd | dlg | hf |
|---:|-------|------:|--:|----:|---:|----:|-----:|-----:|---:|---:|----:|:---|
| 121 | Mở rộng sang Thái Lan | **10.00** | 3329 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.83 | 71 | [] |
| 123 | Xây dựng đội ngũ xuất khẩu | **9.71** | 3476 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.07 | 62 | [] |
| 124 | Cạnh tranh với Trung Quốc | **10.00** | 3261 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 4.70 | 95 | [] |
| 125 | Lan trưởng thành | **10.00** | 3211 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 5.99 | 114 | [] |
| 127 | Lan nhận nhiệm vụ mới | **10.00** | 3053 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 4.21 | 128 | [] |
| 129 | Bước lùi để tiến xa hơn | **9.92** | 3073 | 9.6 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.86 | 93 | [] |
| 130 | Thử thách kế thừa | **10.00** | 3233 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 7.09 | 50 | [] |
| 131 | Mở rộng Đông Nam Á | **9.71** | 3063 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 2.90 | 96 | [] |
| 132 | Đối mặt hải quan Indonesia | **10.00** | 3054 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.68 | 109 | [] |
| 133 | Malaysia và Philippines | **10.00** | 3021 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 4.51 | 84 | [] |
| 136 | Nhật Bản — Thị trường khó tính nhất | **10.00** | 3035 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 4.60 | 96 | [] |
| 138 | Thử thách từ ông Sato | **10.00** | 3666 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.50 | 98 | [] |
| 140 | Chuẩn bị cho thị trường Mỹ | **9.71** | 3021 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 2.96 | 92 | [] |
| 141 | Chuyến bay đầu tiên đến Mỹ | **9.71** | 3054 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.02 | 98 | [] |
| 143 | Xây dựng hệ thống chất lượng Mỹ | **9.71** | 3031 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 2.48 | 96 | [] |
| 144 | Mở rộng đối tác Mỹ | **9.71** | 3168 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 2.16 | 83 | [] |
| 146 | Lan học cách đàm phán với người Mỹ | **9.71** | 3083 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | 3.31 | 80 | [] |

**Word band:** 3021–3666 (min_words=3000, max_words=4200)  
**AVG=9.876 MIN=9.71 MAX=10.00 PASS=17/17**

---

## SKIP PASS verification (untouched)

122,126,128,134,135,137,139,142,145,147–150 — re-scored still ≥9.5, hard_fails=[].

---

## Notes / residual risk

- ΔEXP 121–130 ledger +83/+84 (cuối P2) ≠ +180 P3 — **đúng ledger**, không đồng nhất giả.
- Một số `vợ` còn lại = vợ nhân vật phụ (thợ/đại lý) hoặc câu hỏi bị phủ định (`Cô là vợ anh?` → `Em gái`) — không phải bà Hà/Lan-as-wife.
- English QC lines (Tanaka fax) có thể bị scanner unaccent đếm — không phải dump aging VN.
- Core beat giữ: Somchai/Thái, đội XK, 3 lớp TQ, Madam Tan, 20t ủy thác, lùi kanban, chìa 3 ngày, SEA, Jakarta phí, MY/PH, Osaka 1mm, Sato dừng máy, hồ sơ Mỹ, LAX, QC 3 trạm, West Coast 30 ngày, Thompson bảo hành.

