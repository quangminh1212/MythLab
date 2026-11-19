# Post-strip AI re-read + fix — Batch ch.61–90

**Series:** Niên Đại Thương Gia  
**Phạm vi:** Chương 61–90 (Phần 2 → khóa → mở Phần 3)  
**Mode:** `read_file`/open FULL body (post P0 strip) · AI chấm tay · **không** tin strict_score làm chân lý  
**Ngày:** 2026-07-29  
**Nguồn:** `C:/Dev/MythLab/Niên Đại Thương Gia/Chương {N} - *.txt`  
**Backup trước fix post:** `_fix_backup_post_061_090/` (+ P0: `_fix_backup_p0_20260729/`)

---

## 1. Verdict tổng batch

| Metric | Giá trị |
|--------|--------:|
| Chương đọc lại | **30/30** |
| Full-file **≥ 9.5** | **0/30** |
| Full-file **≥ 9.0** (ứng viên mạnh) | **11/30** |
| Full-file **8.5–8.9** | **16/30** |
| Full-file **&lt; 8.5** | **3/30** |
| Body words (VI ≥2) sau fix | **all 3122–4197** (sàn 3k / trần ~4.2k) |
| Romance dump / `{a}{b}` | **0** (đã strip P0 + verify) |
| Panel GHI NHẬN hợp lệ | **30/30** (đã merge 70/75/82) |

### Kết luận cứng
**Chưa chương nào đạt ≥9.5 full-file** sau post-strip — nhưng **nhảy rõ so với pre-strip AI-read** (trước đó nhiều ch full ~5.2–6.8 vì romance dump / placeholder).

Thân thương trường **giữ được xương MTC** (xe đạp→máy cày/gặt→xe tải→tín dụng→trường→đào tạo→PK→NL→từ thiện→XK→BH→ra mắt máy).  
Fail còn lại chủ yếu: **panel≠body / skill dump nhẹ / seam năm / MW scale / residual template 1–2 câu / overclaim số**.

---

## 2. Việc đã sửa trong lượt post (cơ học + cast + panel)

| Hạng mục | Chi tiết |
|----------|----------|
| Inline sensory spam | Cắt câu inject: cân đồng, tờ tiền mòn, gầu nước, loa phường, nilon, khói than, “Cồn cào ruột…” (ch.61–77…) |
| Trim overlong | 61–64, 66, 69, 72–74, 76–78, 86… → **≤4197** VI-tokens body |
| Expand short | ch.87 + scene phụ tùng/cọc (~2930→3122) |
| Merge panel vỡ | **70, 75, 82** (orphan `Năm/EXP` trước header rỗng) |
| Fix panel quote/Teaser | **83** `"Hệ thống` → `「Hệ thống`; xóa Teaser rỗng |
| Rebuild panel | **89** (empty GHI NHẬN + `system_ledger` + double stats) |
| Cast wife-frame | **78** bà Hà≠vợ; **82** “người vợ”→mẹ; **83** “nhìn chồng”→con trai; **87** “chồng”→con; **89** Lan frame |
| Panel align body | **71** bà Tư→Bình/Mến; **81** diesel/may→unit tua-bin/thép TN; **75** note ledger→dedupe 30 trường |
| B2 residual | **88** cắt “Cảm xúc hôm nay nghiêng về…” |

Script hỗ trợ (có thể xóa sau): `_post_fix_061_090.py`, `_post_fix_061_090_r2.py`, `_post_fix_panels_cast.py`.

---

## 3. Scorecard AI (post-strip) — 6 trục ước · ≥9.5?

Rubric khó tính (van · cấu trúc · NV · cont · filler · hệ thống). **≥9.5 chỉ khi full-file sạch pad + panel khớp + logic liền.**

| Ch | Tiêu đề ngắn | w | AI | ≥9.5? | Ghi chú ngắn |
|---:|--------------|--:|---:|:-----:|--------------|
| 61 | Xe đạp | 3978 | 8.9 | **NO** | Process QC mạnh; panel nhắc Minh ít hiện body |
| 62 | Máy cày | 4115 | **9.25** | **NO** (gần) | Top process; bà Hà “chừa đường sửa” |
| 63 | Máy gặt | 3987 | 9.05 | **NO** | Đối chứng lúa đổ tốt; panel skill gọn hơn |
| 64 | 30 xe tải | 4197 | **9.15** | **NO** | Thân top; dump romance **đã hết** |
| 65 | CN tài chính | 3534 | 8.85 | **NO** | Kỷ luật quầy/sổ tốt |
| 66 | Trường học | 3978 | 9.0 | **NO** | Mái dột→nghiệm thu mưa thật |
| 67 | Trường SG | 3310 | 8.75 | **NO** | Bình An + “trả lại Sài Gòn” |
| 68 | TT đào tạo | 3476 | 8.8 | **NO** | Thư thợ Năm Quảng Ngãi = hook tốt |
| 69 | PK mở rộng | 3879 | 8.95 | **NO** | An Tín đếm người chờ |
| 70 | HT vận chuyển | 3464 | 9.0 | **NO** | Panel đã merge; Buchi/lốp |
| 71 | Cho vay | 3986 | **9.2** | **NO** | Anti-deposit wall; panel=Bình |
| 72 | CN TC mở rộng | 3922 | 9.0 | **NO** | 3 điểm + két 2 khóa; chờ 1 kỳ thu |
| 73 | HT cho vay | 4043 | **9.25** | **NO** | Ông Bảy trễ 2 ngày — không tô hồng 100% |
| 74 | 30 trường | 4091 | 9.0 | **NO** | 6 mục kiểm; không lễ |
| 75 | Dedupe 30 | 3622 | 8.85 | **NO** | Quốc Oai đếm trùng — bài học sổ |
| 76 | TTĐT mở rộng | 4011 | 8.9 | **NO** | 30→60 HV; an toàn trước tay nghề |
| 77 | HT đào tạo | 4059 | **9.3** | **NO** | 48/60; Cường/Nguyệt; **sạch romance** |
| 78 | PK tiếp | 4190 | 8.6 | **NO** | Body Đức/Hà Đông mạnh; panel “7 cơ sở” lệch scale |
| 79 | HT PK | 3552 | 8.75 | **NO** | 3 tiêu chí nghiệm thu; panel overclaim sĩ số |
| 80 | Cty xây dựng | 3521 | 8.85 | **NO** | Thợ Tư→cty; thầu chợ |
| 81 | NM điện | 3359 | **9.1** | **NO** | Kỹ thuật ngày dài; panel đã khớp beat |
| 82 | HT NL | 3921 | 8.9 | **NO** | 8.5 MW ĐN mạnh; scale vs ch.81 vẫn soft-fail |
| 83 | Quỹ từ thiện | 3323 | 8.8 | **NO** | Ông Mão mái; ký đôi |
| 84 | HT từ thiện | 3557 | 9.0 | **NO** | Hiện trường > giấy |
| 85 | XK 10 ĐT | 3914 | **9.2** | **NO** | L/C–barter + **Bằng seed** qua Tuấn |
| 86 | Bảo hiểm | 4087 | 8.85 | **NO** | Đại lý + lô NL biến mất (tension) |
| 87 | MC-01 ra mắt | 3122 | 9.0 | **NO** | Demo + 7 cọc; bà Hà=mẹ |
| 88 | MG ra mắt | 3753 | 8.7 | **NO** | Còn hơi khung template; đã cắt B2 emotion |
| 89 | TK Phần 2 | 3399 | 8.55 | **NO** | Checklist OK; seam “đi nước ngoài” lệch beat khóa |
| 90 | BĐ Phần 3 | 3805 | 9.0 | **NO** | Hàng Bông/Hạnh/sàn hứa; EXP +182 lệch nhịp |

### Ứng viên gần cửa (≥9.2 body, full chưa 9.5)
**62 · 71 · 73 · 77 · 85** (+ 64, 81 nếu siết panel/cont thêm 1 nhịp).

---

## 4. Chi tiết theo nhóm arc

### 61–64 · Cơ khí / logistics nền
- **Xương:** xe đạp lô thử → máy cày R&D ruộng → máy gặt đối chứng → mua 30 xe (giấy trước máy).
- **Pre-strip P0:** romance dump (64 nặng), `{a}{b}` (63), spill đuôi (61).
- **Post:** dump/placeholder **0**; thân process **giữ**.  
- **Còn:** panel skill chung chung; ch.61 panel “Minh chỉnh cổ lái” vs body thợ/Lan; ch.64 panel “mỗi tỉnh hai chiếc” (nếu còn) vs đội nội địa.

### 65–70 · Tài chính / giáo dục / y / vận chuyển
- CN TC + trường + TTĐT + PK + chốt vận chuyển Đà Nẵng.
- **Post:** panel 70/75 merge OK.  
- **Còn:** title typo body “Mở rộngchi nhánh” (thiếu space — cosmetic); ch.69/78 scale PK.

### 71–80 · Tín dụng → trường 30 → đào tạo → PK → xây
- **Đỉnh batch:** 71–73 (microcredit 1985–86), 77 (nghiệm thu đào tạo có số thật).  
- **Còn:** 78/79 panel overclaim số PK/bác sĩ; 76 “anh” POV xưng hô lạ so giọng series.

### 81–90 · NL → từ thiện → XK/BH → ra mắt máy → khóa P2 → P3
- **81–82:** kỹ thuật tua-bin/thử tải **mạnh**; soft-fail **công suất/location** nếu đọc liền (unit lớn vs 4×2 MW).  
- **85:** export matrix + Bằng hỏi lộ trình — **seed antagonist đúng chỗ**.  
- **89–90:** khóa/mở ý OK; **tháng** (Chạp vs Tháng Chín) + EXP 90 (+182) lệch nhịp Part2 (+213/250).

---

## 5. Continuity / ledger notes (batch)

| Issue | Ch | Mức |
|-------|---:|-----|
| Năm narr 1985→1986 | 70→73 | OK (Tết) |
| EXP nhịp +213/214 rồi +250 (76+) | 61–90 | Chấp nhận scale Part2; **90 +182** lệch |
| Space ~+46/47 rồi +57 | 61–90 | OK pattern |
| MW/địa điểm NL | 81↔82 | **WARN** reconcile |
| Panel PK số cơ sở | 78–79 | **WARN** |
| Bà Hà = mẹ (sau fix) | 78,82,83,87 | OK |
| Lan = em/KT (sau fix 89) | 89 | OK |
| Minh kỹ sư | 63,66,87–88 | OK vai |
| Bằng proxy | 85 (+86 tension) | Giữ — Mode F/E seed |

---

## 6. So sánh pre vs post (AI full-file)

| Ch mẫu | Pre-strip AI | Post-strip AI | Delta |
|-------:|-------------:|--------------:|------:|
| 61 | ~6.8 | ~8.9 | +2.1 |
| 63 | ~5.7 | ~9.05 | +3.3 |
| 64 | ~5.4 | ~9.15 | +3.7 |
| 65 | ~5.5 | ~8.85 | +3.3 |
| 69 | ~5.2 | ~8.95 | +3.7 |
| 77 | ~9.1 (sạch sẵn) | ~9.3 | +0.2 |
| 81 | ~7.5 (panel sai) | ~9.1 | +1.6 |

→ **P0 strip + post fix = đúng hướng.** Cửa ≥9.5 còn cần **panel rewrite khớp body + 1 pass cont (MW/year/EXP 90) + cắt nốt template residual** — không cần expand thêm.

---

## 7. Việc còn lại để push ≥9.5 (ưu tiên)

1. **Panel rewrite 1:1 body** cho: 61, 71✓, 75✓, 78, 79, 81✓, 82 (diesel bill vs 8.5MW — giữ cliff nhưng bỏ overclaim “sản xuất tăng gấp đôi” nếu body không chứng).  
2. **Reconcile 81↔82** công suất/địa điểm (cùng KCN hay 2 nhà máy).  
3. **Seam 89→90:** tháng năm + EXP increment chuẩn Part2/Part3.  
4. **ch.88:** 1 pass anti-template (homecoming / “lời hứa rà”) nếu còn khung B2.  
5. **ch.89:** cắt hoặc neo lại “đi nước ngoài” cho khớp khóa P2 (không nhảy foresight trắng).  
6. **Không** nhồi sensory/template mới — words đã trong band.

### MTC bổ sung (sau sạch — xương only)
| Twist | Gợi ý ch |
|-------|----------|
| Tem/kiểm định giả linh kiện xe-máy | 61–64 |
| Policy whiplash máy NN | 62–63, 87–88 |
| Phá sản giả đại lý xe/bảo hiểm | 64, 86 |
| Clone franchise trường/PK | 74–79 |
| Bằng escalate (sau seed 85) | 100–160 |

---

## 8. Integrity gate (post-fix)

```
ch.61–90:
  words body ∈ [3122, 4197]     ✓
  「Hệ thống GHI NHẬN」 ×1       ✓
  Năm+EXP trong panel           ✓
  romance "Hai ly nước ấm"      0
  {a}/{b}                       0
  a bà Hà (prefix vỡ)           0 (false+ trong "của bà Hà")
  wife-frame bà Hà              0 (đã vá 78/82/83/87)
```

---

## 9. File đụng chạm

- **Sửa nội dung:** `Chương 61` … `Chương 90` (toàn dải; mức độ khác nhau)  
- **Backup:** `_fix_backup_post_061_090/`  
- **Report:** `_ai_reads/batch_post_061_090.md` (file này)  
- **Digest phụ:** `_ai_reads/_digest_061_090.json` (pre-final snapshot; scores lấy từ re-read sau fix)

---

**Bottom line:** Post-strip ch.61–90 **sạch pad P0**, dài đúng band, panel không còn rỗng — **0/30 ≥9.5** nhưng **~11 ch ≥9.0** và 5 ứng viên ≥9.2. Tiếp theo: panel+cont surgical, không expand.
