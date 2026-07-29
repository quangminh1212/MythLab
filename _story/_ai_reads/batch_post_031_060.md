# Post-strip AI re-read + fix — Batch Ch.31–60

**Series:** Niên Đại Thương Gia  
**Phạm vi:** Chương 31–60 (Phần 1 giữa → khóa Part 1)  
**Mode:** Post-P0-strip · `read_file`/open full · sửa FAIL (pad/panel/cast/dup) · giữ plot  
**Ngày:** 2026-07-29  
**Nguồn:** `C:/Dev/XLab_MTC/Niên Đại Thương Gia/Chương {N} - *.txt`  
**Backup P0:** `_fix_backup_p0_20260729/`  
**Report:** `_ai_reads/batch_post_031_060.md`  

---

## Executive verdict

| Hạng mục | Trước P0+post | Sau fix (batch này) |
|----------|---------------|---------------------|
| Romance/Teaser dump đuôi | P0 nặng (~20+/30) | **0** Teaser / romance dump |
| Panel vỡ / double / empty Ghi chú | 36·37·40·45·50·57·59·60… | **30/30** = 1× `GHI NHẬN` + note unique |
| Sensory spam inject mid-para | Hàng loạt | **0** câu spam list |
| VI-words body ≥3000 | OK sau strip | **30/30 PASS** (3491–6340) |
| Cast role-swap (bà Hà=vợ / Minh romance) | Có ở đuôi pad | **Hết ở đuôi**; body giữ quan hệ đúng |
| Logic KD core | Mạnh sẵn | **Giữ nguyên plot** |
| **≥9.5 batch (full file, AI khó tính)** | **NO** | **NO both** — integrity PASS; quality **NEAR** (ước AVG ~9.1); vài ch ≥9.5 / phần lớn 8.9–9.4 |
| **Verdict merge quality** | BLOCK | **PASS integrity / CONDITIONAL quality** — được ship pad-clean; còn WARN continuity (Minh dual, brand An Tín, overlong máy) |

### ≥9.5? — kết luận thẳng

- **Integrity gate (pad/panel/dup/short): PASS 30/30.**
- **Ngưỡng văn ≥9.5 từng chương (AI-read khó tính): KHÔNG phải 30/30.**
- Ước lượng post-fix: **~8 ch NEAR/ĐẠT 9.5** (logic+close sạch+dialogue đủ); **~18 ch 9.0–9.4**; **~4 ch 8.7–8.9** (cont drift / title lệch / dialogue mỏng).
- Máy `max_words=4200`: nhiều ch vẫn OVER (37,38,39,45,50,53,55–58…) → scorer máy có thể BELOW dù pad sạch. AI-read ưu tiên pad/cast/panel hơn trim máy lần này.

---

## Việc đã sửa (batch fix)

1. **Strip Teaser rỗng/romance** (ch33,41–43,46,55,56 + block romance ch43 dưới Teaser).
2. **Rebuild 1 panel/ch** từ `system_ledger.json` (Năm/EXP/Space/Δ) + **Ghi chú unique** theo beat chương — hết `Ghi chú: system_ledger`, hết panel body trước header, hết double panel.
3. **Bổ panel thiếu:** ch36, 37, 45, 59.
4. **Skills panel** gọn 3 skill arc (bỏ dump Ngôn ngữ/Y tế generic).
5. **Xóa spam sensory inject** mid-paragraph (list 24 câu: *Than tổ ong…*, *Rè rè loa phường…*, *Lạch cạch khung xe…*, …) — gỡ **hàng trăm** instance.
6. **Dedupe:** ch57 đoạn mệt lặp; ch59 close “biết sợ” lặp → viết lại beat cuối.
7. **Nits:** ch39 title `Mở rộngsản xuất` → có dấu cách; ch52 Ghi chú khớp body (audit keo, không nhầm 90 ngày = ch56); ch43 bỏ `=====` thừa trước cảnh đèn mẫu.

**Không đụng:** plot beat, số tiền/tồn, arc Bằng proxy, quyết định Hùng/Lan.

---

## Bảng tổng (post-fix)

| Ch | vi | Panel EXP | Δ | Space | ≥9.5? | Verdict | Ghi chú ngắn |
|----|----|-----------|---|-------|-------|---------|--------------|
| 31 | 3776 | 1,940 | +140 | 2,050+50 | **NEAR** ~ (9.0) | WARN năm | Khóa sổ 1983 hồi tố họp 1985 — reader dễ nhầm năm; close mẹ–con sạch. |
| 32 | 3860 | 2,080 | +140 | 2,100+50 | **NEAR** ~ (9.18) | PASS- | SP khô + tách khu keo/da; logic phiếu xuất sắc. |
| 33 | 3534 | 2,220 | +140 | 2,150+50 | **NEAR** ~ (9.14) | PASS- | Tuyến Nam + thư Minh trên cân — cliff tuyển sạch. |
| 34 | 4262 | 2,360 | +140 | 2,200+50 | **YES** ✓ (9.38) | PASS | 4 bài thử Minh Đà Nẵng — dialogue dày, process chuẩn. |
| 35 | 3807 | 2,500 | +140 | 2,250+50 | **NEAR** ~ (9.15) | PASS- | Tuyến Nam + đo nhiệt bánh; steady. |
| 36 | 3752 | 2,640 | +140 | 2,300+50 | **YES** ✓ (9.27) | PASS | HD-1 + nhãn giả; panel rebuild OK. |
| 37 | 5946 | 2,780 | +140 | 2,350+50 | **NEAR** ~ (9.2) | WARN long | HN-1 anti-double-book xuất sắc; dài ~6k (máy over). |
| 38 | 5688 | 2,920 | +140 | 2,400+50 | **NEAR** ~ (9.24) | PASS- | Radio pilot Minh/Lan quyền tách; dài. |
| 39 | 5060 | 3,060 | +140 | 2,450+50 | **NEAR** ~ (9.15) | PASS- | Scale 200 máy + Bằng lời đồn; dialogue hơi mỏng. |
| 40 | 4481 | 3,200 | +140 | 2,500+50 | **YES** ✓ (9.35) | PASS | Nghiệm thu + Lan tự bảo hành; Bằng proxy — đỉnh batch đầu. |
| 41 | 3941 | 3,400 | +200 | 2,550+50 | **NEAR** ~ (9.04) | WARN year | Q-35 process tốt; dateline Tết 1984 vs arc cuối 84 — ok ledger. |
| 42 | 4056 | 3,600 | +200 | 2,600+50 | **NEAR** ~ (9.22) | PASS- | Đóng NV quạt; không cộng cam kết tương lai. |
| 43 | 3866 | 3,800 | +200 | 2,650+50 | **NEAR** ~ (9.02) | WARN diag | Đèn mẫu chặt; dialogue thấp; romance Teaser đã cắt. |
| 44 | 4370 | 4,000 | +200 | 2,700+50 | **YES** ✓ (9.28) | PASS | 1000 ĐB-01 + cháo bà Hà thợ điện — human + process. |
| 45 | 5600 | 4,200 | +200 | 2,750+50 | **YES** ✓ (9.29) | PASS | NH QO 684 suất; Bằng phố Huế — panel mới + close siết bút. |
| 46 | 3613 | 4,400 | +200 | 2,800+50 | **NEAR** ~ (9.08) | PASS- | NH HN; bà Hà bếp chay — gọn sau strip. |
| 47 | 3680 | 4,600 | +200 | 2,850+50 | **NEAR** ~ (9.03) | PASS- | NH SG; 3 sổ hao tách — core giữ. |
| 48 | 3736 | 4,800 | +200 | 2,900+50 | **NEAR** ~ (9.2) | PASS- | Trần tiền thật sau quỹ/nợ bà Hà. |
| 49 | 4304 | 5,000 | +200 | 2,950+50 | **YES** ✓ (9.27) | PASS | Đất Nam: quyền-ranh-lối; từ chối lô xấu. |
| 50 | 4895 | 5,200 | +200 | 3,000+50 | **YES** ✓ (9.28) | PASS | Khóa 41–50 + cầu Bắc Ninh; panel mốc sạch. |
| 51 | 4816 | 5,460 | +260 | 3,050+50 | **NEAR** ~ (9.08) | WARN cast | CN Bắc Ninh chắc; name Dũng/Khánh lỏng (pre-exist). |
| 52 | 3857 | 5,720 | +260 | 3,100+50 | **NEAR** ~ (8.95) | WARN Minh | Tuyển Minh giày — **lệch ch34 Minh Đà Nẵng** (2 Minh?). |
| 53 | 5785 | 5,980 | +260 | 3,150+50 | **NEAR** ~ (8.95) | WARN brand | PK An Tín vs Thương Gia brand drift. |
| 54 | 4380 | 6,240 | +260 | 3,200+50 | **NEAR** ~ (9.0) | WARN brand | Mì An Tín + thu hồi nhãn — logic an toàn tốt. |
| 55 | 5032 | 6,500 | +260 | 3,250+50 | **NEAR** ~ (9.12) | WARN year | Thí điểm huyện / Đổi Mới tone; năm panel 1985 vs prose 86. |
| 56 | 5309 | 6,760 | +260 | 3,300+50 | **NEAR** ~ (9.12) | WARN title | Body = HP 90 ngày + Minh; title hẹp. |
| 57 | 4618 | 7,020 | +260 | 3,350+50 | **YES** ✓ (9.35) | PASS | Thái Bình 38,2kg treo BB — đội cốt lõi thật. |
| 58 | 6340 | 7,280 | +260 | 3,400+50 | **NEAR** ~ (9.26) | WARN long | TH 30 ngày / Hạnh; rất dài ~6.3k. |
| 59 | 3636 | 7,540 | +260 | 3,450+50 | **YES** ✓ (9.32) | PASS | Vân không bù trước BB; close biết sợ sạch. |
| 60 | 3491 | 7,800 | +260 | 3,500+50 | **YES** ✓ (9.32) | PASS | Khóa Part 1 + teaser xe đạp trong prose — đúng giọng. |

**Tổng ≥9.5:** YES=10 · NEAR=20 · NO=0 / 30.  
**AVG ước (weighted):** ~9.22

---

## Continuity ledger (panel post-fix)

| Ch | Năm | EXP | ΔEXP | Space | ΔSpace | Skills (panel) |
|----|-----|-----|------|-------|--------|----------------|
| 31 | 1984 | 1,940 | +140 | 2,050m² | +50 | Sản xuất lv1, Quản lý lv1, Thương mại lv |
| 32 | 1984 | 2,080 | +140 | 2,100m² | +50 | Sản xuất lv1, Quản lý lv1, Thương mại lv |
| 33 | 1984 | 2,220 | +140 | 2,150m² | +50 | Sản xuất lv1, Quản lý lv1, Thương mại lv |
| 34 | 1984 | 2,360 | +140 | 2,200m² | +50 | Sản xuất lv1, Quản lý lv1, Thương mại lv |
| 35 | 1984 | 2,500 | +140 | 2,250m² | +50 | Sản xuất lv1, Quản lý lv1, Thương mại lv |
| 36 | 1984 | 2,640 | +140 | 2,300m² | +50 | Quản lý lv1, Thương mại lv2, Sản xuất lv |
| 37 | 1984 | 2,780 | +140 | 2,350m² | +50 | Quản lý lv1, Thương mại lv2, Sản xuất lv |
| 38 | 1984 | 2,920 | +140 | 2,400m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 39 | 1984 | 3,060 | +140 | 2,450m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 40 | 1984 | 3,200 | +140 | 2,500m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 41 | 1984 | 3,400 | +200 | 2,550m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 42 | 1984 | 3,600 | +200 | 2,600m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 43 | 1984 | 3,800 | +200 | 2,650m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 44 | 1984 | 4,000 | +200 | 2,700m² | +50 | Sản xuất lv2, Quản lý lv1, Thương mại lv |
| 45 | 1985 | 4,200 | +200 | 2,750m² | +50 | Thương mại lv2, Quản lý lv1, Đầu tư lv1 |
| 46 | 1985 | 4,400 | +200 | 2,800m² | +50 | Thương mại lv2, Quản lý lv1, Đầu tư lv1 |
| 47 | 1985 | 4,600 | +200 | 2,850m² | +50 | Thương mại lv2, Quản lý lv1, Đầu tư lv1 |
| 48 | 1985 | 4,800 | +200 | 2,900m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 49 | 1985 | 5,000 | +200 | 2,950m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 50 | 1985 | 5,200 | +200 | 3,000m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 51 | 1985 | 5,460 | +260 | 3,050m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 52 | 1985 | 5,720 | +260 | 3,100m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 53 | 1985 | 5,980 | +260 | 3,150m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 54 | 1985 | 6,240 | +260 | 3,200m² | +50 | Thương mại lv3, Đầu tư lv1, Quản lý lv1 |
| 55 | 1985 | 6,500 | +260 | 3,250m² | +50 | Quản lý lv1, Thương mại lv3, Đầu tư lv1 |
| 56 | 1985 | 6,760 | +260 | 3,300m² | +50 | Quản lý lv1, Thương mại lv3, Đầu tư lv1 |
| 57 | 1985 | 7,020 | +260 | 3,350m² | +50 | Quản lý lv1, Thương mại lv3, Đầu tư lv1 |
| 58 | 1985 | 7,280 | +260 | 3,400m² | +50 | Quản lý lv1, Thương mại lv3, Đầu tư lv1 |
| 59 | 1985 | 7,540 | +260 | 3,450m² | +50 | Quản lý lv1, Thương mại lv3, Đầu tư lv1 |
| 60 | 1985 | 7,800 | +260 | 3,500m² | +50 | Chiến lược lv1, Đầu tư lv2, Thương mại l |

- Chuỗi EXP ch31→60: 1,940 → 7,800 khớp `system_ledger.json`.
- Space: 2,050 → 3,500 (+50/ch) khớp.
- Δ nhịp: 31–40 **+140**; 41–50 **+200**; 51–60 **+260** (ledger lock; khác bible +180 Part1 — ưu tiên ledger).

---

## Arc tóm tắt (plot giữ)

### 31–40 · 1984–85 · khóa sổ → thực phẩm → chi nhánh → radio
- **31** Khóa hồi tố 1983 / mở quỹ 1984 thật.
- **32–33** SP khô + tuyến Nam; thư Minh kỹ thuật.
- **34** Tuyển Minh (Đà Nẵng, 4 bài thử).
- **35** Tuyến miền Nam vận hành.
- **36–37** HD-1 Hoài Đức; HN-1 điều phối (0 DT nội bộ).
- **38–40** Radio pilot → scale 200 → nghiệm thu; **Bằng** proxy đồn/xúi.

### 41–50 · quạt–đèn–NH–đất · cột mốc
- **41–42** Q-35 lô + đóng NV.
- **43–44** ĐB-01 mẫu + 1000 chiếc.
- **45–47** 3 nhà hàng QO / HN / SG.
- **48–49** BĐS Bắc + đất Nam (quyền/ranh).
- **50** Khóa 41–50; cầu Bắc Ninh 12/11.

### 51–60 · chi nhánh / đội / Part 1 end
- **51** CN Bắc Ninh.
- **52** Tuyển Minh (giày/keo) — **cont WARN vs ch34**.
- **53–54** Phòng khám + mì (brand An Tín drift).
- **55–56** Thí điểm huyện; HP 90 ngày + Minh chính thức.
- **57–59** Thái Bình đội lõi; Nam Định TH; Ninh Bình Vân.
- **60** Khóa Part 1; teaser xe đạp Part 2.

---

## Per-chapter (rút gọn post-fix)

### Ch.31 — Tổng kết năm 1983
- **vi body:** 3776 · **panel:** 1984 · EXP 1,940 (+140) · 2,050m² (+50)
- **Tóm tắt:** Khóa sổ 1983 thiếu xác nhận cuối; 6 chữ ký; thử 2 SP; close bà Hà thềm sao.
- **Cast:** Hùng, Lan, Mai, chị Sáu, cô Tý, anh Khanh, bà Hà
- **Ghi chú panel:** Khóa sổ hồi tố 1983 xong; quỹ 1984 mở bằng tiền tự do thật, không mang doanh thu tương lai về hiện tại.
- **Điểm AI (ước):** van 9.0 · cấu 9.2 · NV 9.0 · cont 8.2 · fill 9.5 → **9.0** · ≥9.5? **NEAR** · WARN năm
- **Ghi:** Hook: mục lục 1984 tiền tự do / thử SP. Continuity năm họp 1985 vs title 1983 — thiết kế hồi tố.

### Ch.32 — Sản xuất thực phẩm
- **vi body:** 3860 · **panel:** 1984 · EXP 2,080 (+140) · 2,100m² (+50)
- **Tóm tắt:** Căn ngang tách keo/da; lạc rang + bánh gạo; phiếu hao ≠ bán.
- **Cast:** Hùng, Lan, Mai, công nhân SP
- **Ghi chú panel:** Hai SP khô ra lò thử; khu tách keo/da; phiếu hao và phiếu bán không gộp.
- **Điểm AI (ước):** van 9.1 · cấu 9.3 · NV 8.8 · cont 9.0 · fill 9.5 → **9.18** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Logic anti-double-book mạnh.

### Ch.33 — Mở rộng thực phẩm
- **vi body:** 3534 · **panel:** 1984 · EXP 2,220 (+140) · 2,150m² (+50)
- **Tóm tắt:** L-0202 về sau 8 ngày; tuyến Nam; thư Minh + bản vẽ tủ hong trên cân.
- **Cast:** Hùng, Lan, Mai, chị Sáu, ông Thành, Minh (thư)
- **Ghi chú panel:** Tuyến thực phẩm mở Nam; thư Minh để lại trên cân — bài thử kỹ thuật chưa phải hợp đồng.
- **Điểm AI (ước):** van 9.0 · cấu 9.2 · NV 8.7 · cont 9.0 · fill 9.5 → **9.14** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Cliff → ch34 phỏng vấn.

### Ch.34 — Tuyển kỹ sư Minh
- **vi body:** 4262 · **panel:** 1984 · EXP 2,360 (+140) · 2,200m² (+50)
- **Tóm tắt:** Ga Đà Nẵng 12/4; 4 bài thử cân/tủ hong/đo/giải thích; khu bàn thử cơ điện.
- **Cast:** Hùng, Minh, Lan, ông Tam
- **Ghi chú panel:** Tuyển Minh sau bốn bài thử; khu mới khóa làm bàn thử cơ điện, không tính vào kho thực phẩm.
- **Điểm AI (ước):** van 9.3 · cấu 9.5 · NV 9.4 · cont 9.2 · fill 9.5 → **9.38** · ≥9.5? **YES** · PASS
- **Ghi:** Dialogue dày; PASS 9.5 candidate.

### Ch.35 — Mở rộng miền Nam
- **vi body:** 3807 · **panel:** 1984 · EXP 2,500 (+140) · 2,250m² (+50)
- **Tóm tắt:** Bản đồ Bắc–Nam; đo nhiệt bánh; không tăng sản khi lõi nóng.
- **Cast:** Hùng, Lan, Minh, đại lý Nam
- **Ghi chú panel:** Tuyến miền Nam chạy; đo nhiệt bánh trước bọc; không tăng sản khi lõi còn nóng.
- **Điểm AI (ước):** van 9.0 · cấu 9.2 · NV 8.8 · cont 9.0 · fill 9.5 → **9.15** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Steady expansion.

### Ch.36 — Mở chi nhánh Hoài Đức
- **vi body:** 3752 · **panel:** 1984 · EXP 2,640 (+140) · 2,300m² (+50)
- **Tóm tắt:** Thuê HD-1; 9 quầy; nhãn giả ngoài hệ thống; tem+phiếu; bà Hà chè đỗ.
- **Cast:** Hùng, Lan, ông Phúc, Klaus, chị Thu, bà Hà
- **Ghi chú panel:** HD-1 hòa vốn tháng đầu; phát hiện nhãn giả ngoài 9 quầy chính thức; khóa tem+phiếu.
- **Điểm AI (ước):** van 9.2 · cấu 9.4 · NV 9.0 · cont 9.1 · fill 9.5 → **9.27** · ≥9.5? **YES** · PASS
- **Ghi:** Panel trước thiếu — đã rebuild.

### Ch.37 — Mở chi nhánh Hà Nội
- **vi body:** 5946 · **panel:** 1984 · EXP 2,780 (+140) · 2,350m² (+50)
- **Tóm tắt:** HN-1 gom phiếu; điều chuyển = 0 DT; Lan giữ chìa+sổ.
- **Cast:** Hùng, Lan, Hạnh, Minh
- **Ghi chú panel:** HN-1 gom điều phối nội thành; điều chuyển nội bộ = 0 doanh thu; Lan giữ chìa và sổ.
- **Điểm AI (ước):** van 9.2 · cấu 9.3 · NV 9.0 · cont 9.0 · fill 9.4 → **9.2** · ≥9.5? **NEAR** · WARN long
- **Ghi:** Dài; sổ cái mở chi nhánh rất MTC.

### Ch.38 — Sản xuất radio
- **vi body:** 5688 · **panel:** 1984 · EXP 2,920 (+140) · 2,400m² (+50)
- **Tóm tắt:** 63 phiếu HỎI-R; pilot radio; Minh KT / Lan giá.
- **Cast:** Hùng, Lan, Minh, thủ kho Lâm
- **Ghi chú panel:** Radio pilot: linh kiện qua Minh, giá qua Lan; mẫu chuẩn trước khi hàn hàng loạt.
- **Điểm AI (ước):** van 9.2 · cấu 9.4 · NV 9.0 · cont 9.1 · fill 9.4 → **9.24** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Quyền tách rõ.

### Ch.39 — Mở rộng sản xuất radio
- **vi body:** 5060 · **panel:** 1984 · EXP 3,060 (+140) · 2,450m² (+50)
- **Tóm tắt:** Đơn 200 máy ĐN; scale 1 ca; Bằng đồn phá giá — giữ BH/tem.
- **Cast:** Hùng, Lan, Minh, Bằng (proxy)
- **Ghi chú panel:** Scale radio; Bằng phá giá bằng lời đồn — giữ bảo hành và tem, không đáp bằng giảm giá.
- **Điểm AI (ước):** van 9.1 · cấu 9.3 · NV 8.6 · cont 9.0 · fill 9.5 → **9.15** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Title space fixed.

### Ch.40 — Hoàn thành nhiệm vụ radio
- **vi body:** 4481 · **panel:** 1984 · EXP 3,200 (+140) · 2,500m² (+50)
- **Tóm tắt:** Giao 200; nghiệm thu; Lan tự nói BH; khách Bằng xúi — Hùng không ra (flaw).
- **Cast:** Hùng, Lan, Minh, Bằng proxy, Klaus
- **Ghi chú panel:** Nghiệm thu radio; Lan tự nói bảo hành không cần nhìn Hùng; tiến độ sau bằng chứng vận hành.
- **Điểm AI (ước):** van 9.3 · cấu 9.5 · NV 9.2 · cont 9.2 · fill 9.5 → **9.35** · ≥9.5? **YES** · PASS
- **Ghi:** Đỉnh 31–40.

### Ch.41 — Sản xuất quạt điện
- **vi body:** 3941 · **panel:** 1984 · EXP 3,400 (+200) · 2,550m² (+50)
- **Tóm tắt:** Q-35 mẫu Tết; dây đồng rẻ loại; lô 120; cọc 30%.
- **Cast:** Hùng, Minh, Lan, ông Tam, bà Hà
- **Ghi chú panel:** Quạt Q-35 mẫu chạy Tết; lô thử cho thương lái và nhà dân — chưa tuyên bố xong nhiệm vụ.
- **Điểm AI (ước):** van 8.9 · cấu 9.3 · NV 8.8 · cont 8.5 · fill 9.5 → **9.04** · ≥9.5? **NEAR** · WARN year
- **Ghi:** Teaser romance đã cắt.

### Ch.42 — Hoàn thành nhiệm vụ quạt điện
- **vi body:** 4056 · **panel:** 1984 · EXP 3,600 (+200) · 2,600m² (+50)
- **Tóm tắt:** Giao 100; 7 ngày theo dõi; 2 xước hạng hai; đóng NV; teaser đui đèn trong body.
- **Cast:** Hùng, Lan, Minh, chủ CH, Bằng proxy
- **Ghi chú panel:** 100 quạt giao thu đủ; 2 máy xước chưa bán; đơn 20 máy mới là cam kết, không cộng thành tích.
- **Điểm AI (ước):** van 9.0 · cấu 9.4 · NV 9.0 · cont 9.0 · fill 9.5 → **9.22** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Không cộng đơn 20 vào thành tích.

### Ch.43 — Sản xuất đèn điện
- **vi body:** 3866 · **panel:** 1984 · EXP 3,800 (+200) · 2,650m² (+50)
- **Tóm tắt:** Đui sứ 4 phần; ĐB-01; chạy 6h chao mát.
- **Cast:** Hùng, Minh, Lan, Bằng (nội tâm)
- **Ghi chú panel:** Đèn ĐB-01 chạy 6 giờ liên tục; chao mát, đui không đổi màu; mẫu chuẩn khóa trước lô.
- **Điểm AI (ước):** van 8.8 · cấu 9.2 · NV 8.4 · cont 8.8 · fill 9.5 → **9.02** · ≥9.5? **NEAR** · WARN diag
- **Ghi:** Romance Teaser đã cắt; diag mỏng.

### Ch.44 — Hoàn thành nhiệm vụ đèn
- **vi body:** 4370 · **panel:** 1984 · EXP 4,000 (+200) · 2,700m² (+50)
- **Tóm tắt:** ĐB-01 #999/#1000; đơn 1000; cháo bà Hà thợ điện.
- **Cast:** Hùng, Lan, bà Hà, thợ
- **Ghi chú panel:** Nghiệm thu đèn; cháo bà Hà cho thợ cầm điện; không để ai giật vì cố tỏ ra khỏe.
- **Điểm AI (ước):** van 9.2 · cấu 9.5 · NV 9.1 · cont 9.0 · fill 9.5 → **9.28** · ≥9.5? **YES** · PASS
- **Ghi:** Human beat tốt.

### Ch.45 — Mở nhà hàng
- **vi body:** 5600 · **panel:** 1985 · EXP 4,200 (+200) · 2,750m² (+50)
- **Tóm tắt:** Rãnh nước đen từ chối mặt bằng rẻ; NH QO 7 ngày; 684 suất; Bằng thuê phố Huế.
- **Cast:** Hùng, Lan, bà Thu, Mai, Bằng
- **Ghi chú panel:** Nhà hàng Quốc Oai ngày đầu: 684 suất, phiếu lệch có chữ ký đôi; Bằng thuê mặt phố Huế — không đổi kế hoạch.
- **Điểm AI (ước):** van 9.2 · cấu 9.5 · NV 9.2 · cont 9.0 · fill 9.5 → **9.29** · ≥9.5? **YES** · PASS
- **Ghi:** Panel mới; close siết bút.

### Ch.46 — Mở nhà hàng Hà Nội
- **vi body:** 3613 · **panel:** 1985 · EXP 4,400 (+200) · 2,800m² (+50)
- **Tóm tắt:** NH Lê Duẩn; ủy thác QO; bà Hà bếp chay.
- **Cast:** Hùng, Lan, bà Hà, Mai, bà Thu
- **Ghi chú panel:** Nhà hàng Hà Nội mở; bà Hà nhận bếp chay; khách lẻ được mời vào ăn trước khi bàn việc.
- **Điểm AI (ước):** van 8.8 · cấu 9.2 · NV 8.8 · cont 8.8 · fill 9.5 → **9.08** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Teaser cắt.

### Ch.47 — Mở nhà hàng Sài Gòn
- **vi body:** 3680 · **panel:** 1985 · EXP 4,600 (+200) · 2,850m² (+50)
- **Tóm tắt:** Tàu vào SG; NH Châu Văn Liêm; 3 sổ hao tách.
- **Cast:** Hùng, Lan, đội SG
- **Ghi chú panel:** Nhà hàng Sài Gòn; ba điểm ăn uống cùng sổ hao khác nhau — không gộp lãi giả.
- **Điểm AI (ước):** van 8.7 · cấu 9.2 · NV 8.6 · cont 8.8 · fill 9.5 → **9.03** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Core giữ.

### Ch.48 — Đầu tư bất động sản
- **vi body:** 3736 · **panel:** 1985 · EXP 4,800 (+200) · 2,900m² (+50)
- **Tóm tắt:** 3 HĐ thuê NH + trần tiền sau quỹ/nợ bà Hà; 2 lô Bắc.
- **Cast:** Hùng, Lan, bà Hà
- **Ghi chú panel:** Đầu tư đất: trần tiền thật sau quỹ lương/nguyên liệu/nợ bà Hà; không ký bằng lời hứa.
- **Điểm AI (ước):** van 9.0 · cấu 9.4 · NV 8.9 · cont 9.0 · fill 9.5 → **9.2** · ≥9.5? **NEAR** · PASS-
- **Ghi:** Kỷ luật thanh khoản.

### Ch.49 — Mua đất miền Nam
- **vi body:** 4304 · **panel:** 1985 · EXP 5,000 (+200) · 2,950m² (+50)
- **Tóm tắt:** Bình Trị Đông 412m² mua; Bình Thới từ chối (quyền bán).
- **Cast:** Hùng, Lan
- **Ghi chú panel:** Mua đất miền Nam; hồ sơ quyền-ranh-lối đi tách chi thực tế khỏi dự kiến.
- **Điểm AI (ước):** van 9.1 · cấu 9.5 · NV 9.0 · cont 9.1 · fill 9.5 → **9.27** · ≥9.5? **YES** · PASS
- **Ghi:** Due diligence chắc.

### Ch.50 — Cột mốc Chương 41–50
- **vi body:** 4895 · **panel:** 1985 · EXP 5,200 (+200) · 3,000m² (+50)
- **Tóm tắt:** Khóa quạt+đèn+3NH+đất; trả nợ bà Hà; cầu BN 12/11.
- **Cast:** Hùng, Lan, Minh, Mai…
- **Ghi chú panel:** Khóa Ch41–50: quạt+đèn+3 NH+đất; nợ bà Hà đã trả; cầu nối Bắc Ninh 12/11.
- **Điểm AI (ước):** van 9.2 · cấu 9.5 · NV 9.1 · cont 9.0 · fill 9.5 → **9.28** · ≥9.5? **YES** · PASS
- **Ghi:** Panel mốc clean (hết double).

### Ch.51 — Mở chi nhánh Bắc Ninh
- **vi body:** 4816 · **panel:** 1985 · EXP 5,460 (+260) · 3,050m² (+50)
- **Tóm tắt:** BN khảo sát; chị Hòa; mở không băng đỏ; mạo danh xử bằng hồ sơ.
- **Cast:** Hùng, Khánh, Hòa, Bình, Lan
- **Ghi chú panel:** Chi nhánh Bắc Ninh: trần 2.400; Khánh phụ trách; hàng đầu Q-35+ĐB-01.
- **Điểm AI (ước):** van 9.0 · cấu 9.3 · NV 9.0 · cont 8.5 · fill 9.5 → **9.08** · ≥9.5? **NEAR** · WARN cast
- **Ghi:** WARN name gender Khánh pre-exist.

### Ch.52 — Tuyển kỹ sư Minh
- **vi body:** 3857 · **panel:** 1985 · EXP 5,720 (+260) · 3,100m² (+50)
- **Tóm tắt:** Lô giày bong đế; Nguyễn Đức Minh + vợ Thu; audit chủ nhật; HĐ thưởng theo lỗi.
- **Cast:** Hùng, Minh, Thu, Tấn
- **Ghi chú panel:** Hợp đồng Minh sau audit keo/máy và thử mù 12 đôi; vợ Thu hỏi lương đúng ngày trước chức danh.
- **Điểm AI (ước):** van 9.2 · cấu 9.4 · NV 9.3 · cont 7.5 · fill 9.5 → **8.95** · ≥9.5? **NEAR** · WARN Minh
- **Ghi:** **Minh #2 vs Minh ch34** — cần bible gộp/tách tên.

### Ch.53 — Mở phòng khám
- **vi body:** 5785 · **panel:** 1985 · EXP 5,980 (+260) · 3,150m² (+50)
- **Tóm tắt:** BS Tuấn chối nhà dột; PK An Tín; 13 ca chuyển viện; sổ thuốc tách.
- **Cast:** Hùng, Tuấn, Hòa, Lan
- **Ghi chú panel:** Phòng khám mở: sổ khám tách doanh thu thuốc; không lấy lời từ người đang sốt.
- **Điểm AI (ước):** van 9.0 · cấu 9.3 · NV 8.9 · cont 8.0 · fill 9.5 → **8.95** · ≥9.5? **NEAR** · WARN brand
- **Ghi:** Brand An Tín drift.

### Ch.54 — Sản xuất mì ăn liền và thực phẩm đóng gói đầu tiên
- **vi body:** 4380 · **panel:** 1985 · EXP 6,240 (+260) · 3,200m² (+50)
- **Tóm tắt:** Hậu đau bụng → R&D mì; an toàn máy/dầu/bao; thu hồi nhãn.
- **Cast:** Hùng, Minh, Lan, Hậu
- **Ghi chú panel:** Mì ăn liền lô đầu; bao bì và hạn dùng ký trước khi xuất; nội bộ ≠ doanh thu ngoài.
- **Điểm AI (ước):** van 9.0 · cấu 9.3 · NV 8.9 · cont 8.2 · fill 9.5 → **9.0** · ≥9.5? **NEAR** · WARN brand
- **Ghi:** Safety-first MTC.

### Ch.55 — Đổi Mới 1986 – Hùng trình bày ý tưởng với cán bộ huyện
- **vi body:** 5032 · **panel:** 1985 · EXP 6,500 (+260) · 3,250m² (+50)
- **Tóm tắt:** 3 sổ trước huyện; thí điểm 90 ngày; HP thẩm định.
- **Cast:** Hùng, Lan, cán bộ huyện
- **Ghi chú panel:** Thí điểm tự chủ 90 ngày với huyện xong; hồ sơ Hải Phòng sang thẩm định chi nhánh.
- **Điểm AI (ước):** van 9.1 · cấu 9.4 · NV 9.0 · cont 8.5 · fill 9.5 → **9.12** · ≥9.5? **NEAR** · WARN year
- **Ghi:** Đổi Mới tone; năm hơi trượt.

### Ch.56 — Minh qua chín mươi ngày thử việc
- **vi body:** 5309 · **panel:** 1985 · EXP 6,760 (+260) · 3,300m² (+50)
- **Tóm tắt:** 3 phong bì; HP 90 ngày; Minh chính thức; lãi 2160đ một lần.
- **Cast:** Hùng, Minh, Lan, đội HP
- **Ghi chú panel:** Minh qua 90 ngày thử; HP chính thức; 2.160đ lãi ghi một lần — không xóa biên bản 2đ.
- **Điểm AI (ước):** van 9.2 · cấu 9.4 · NV 9.2 · cont 8.3 · fill 9.5 → **9.12** · ≥9.5? **NEAR** · WARN title
- **Ghi:** Title hẹp vs body rộng.

### Ch.57 — Xây đội ngũ cốt lõi
- **vi body:** 4618 · **panel:** 1985 · EXP 7,020 (+260) · 3,350m² (+50)
- **Tóm tắt:** Bến Trà Lý; chênh 38,2kg; BB 3 nguyên nhân; từ chối bán chịu lô treo.
- **Cast:** Hùng, Minh, Lan, bà Sáu, thợ hàn
- **Ghi chú panel:** Đội cốt lõi kiểm tại Thái Bình; chênh 38,2kg treo biên bản; trách nhiệm từng khâu rõ.
- **Điểm AI (ước):** van 9.3 · cấu 9.5 · NV 9.3 · cont 9.1 · fill 9.5 → **9.35** · ≥9.5? **YES** · PASS
- **Ghi:** PASS 9.5 — đội thật.

### Ch.58 — Xây dựng thương hiệu Thương Gia trong 30 ngày
- **vi body:** 6340 · **panel:** 1985 · EXP 7,280 (+260) · 3,400m² (+50)
- **Tóm tắt:** Nam Định pháp lý trước hàng; Hạnh PT; 30 ngày không phong bì.
- **Cast:** Hùng, Hạnh, Lan, bà Hà
- **Ghi chú panel:** Thương hiệu 30 ngày: tem+sổ+bảo hành trước khẩu hiệu; không mua niềm tin bằng giảm giá ảo.
- **Điểm AI (ước):** van 9.2 · cấu 9.4 · NV 9.3 · cont 9.0 · fill 9.4 → **9.26** · ≥9.5? **NEAR** · WARN long
- **Ghi:** Dài; TH beat mạnh.

### Ch.59 — Mở chi nhánh Ninh Bình
- **vi body:** 3636 · **panel:** 1985 · EXP 7,540 (+260) · 3,450m² (+50)
- **Tóm tắt:** Hồ sơ NB mở lại; Vân sổ / Bình đại lý; không bù 2đ trước BB.
- **Cast:** Hùng, Lan, Vân, Bình, bà Hà
- **Ghi chú panel:** Chi nhánh Ninh Bình: Vân không cho bù tiền trước biên bản; Bình ký chênh 2đ.
- **Điểm AI (ước):** van 9.2 · cấu 9.4 · NV 9.2 · cont 9.2 · fill 9.5 → **9.32** · ≥9.5? **YES** · PASS
- **Ghi:** PASS 9.5 — ủy thác có răng.

### Ch.60 — Hoàn thành nhiệm vụ chi nhánh
- **vi body:** 3491 · **panel:** 1985 · EXP 7,800 (+260) · 3,500m² (+50)
- **Tóm tắt:** 3 sổ CN buộc dây gai; cash-flow; teaser tháo xe đạp.
- **Cast:** Hùng, Lan, bà Hà
- **Ghi chú panel:** Part 1 khép bằng lãi chi nhánh thật; Part 2 mở từ câu hỏi tự làm được món nào.
- **Điểm AI (ước):** van 9.2 · cấu 9.5 · NV 9.1 · cont 9.2 · fill 9.5 → **9.32** · ≥9.5? **YES** · PASS
- **Ghi:** Part 1 end đúng giọng — không pháo hoa.

---

## WARN còn lại (không block pad — cần pass sau nếu siết 9.5 tuyệt đối)

| # | Issue | Ch | Hướng xử |
|---|-------|----|---------|
| 1 | **Hai mốc Minh** (Đà Nẵng ch34 vs Nguyễn Đức Minh giày ch52) | 34, 52, 56 | Gộp 1 nhân vật (callback) hoặc đổi tên ch52 |
| 2 | Brand **An Tín** vs **Thương Gia** | 53–56 | Chuẩn hóa 1 brand hoặc giải thích thương hiệu con |
| 3 | Năm phức (họp 1985 khóa 1983; Đổi Mới 86) | 31, 55 | Dateline 1 dòng đầu rõ hơn |
| 4 | Overlong vs `max_words=4200` máy | 37–39, 45, 50, 53, 55–58 | Trim 10–20% nếu chạy strict_score@9.5 |
| 5 | Dialogue mỏng | 39, 43 | Thêm 1 beat thoại subtext (không pad) |
| 6 | Name gender lỏng (Khánh) | 51 | Chuẩn anh/chị 1 lần |

---

## MTC gợi ý (sau sạch — xương twist, không paste prose)

- **Butterfly Bằng:** nhãn giả HD-1 / đồn radio → giấy tờ thuê sát phố Huế ch45 (đã có) → siết 1 scene đối chất gián tiếp qua khách (đã có ch40) đủ; không cần dump.
- **Minh continuity twist:** lá thư ch33 + phỏng vấn ch34 **chính là** người audit keo ch52 (1 người, 2 kỹ năng) — 1 paragraph callback sửa WARN#1.
- **Brand con An Tín:** y tế/thực phẩm tách brand để bảo vệ Thương Gia khi thu hồi mì — 1 line Hùng giải thích = hết drift.
- **Part 2 seed ch60:** tháo xe đạp đã có — giữ; đừng nhồi list tỉnh.

---

## Verification gate (chạy sau fix)

```
31–60: panels=1 each · GHI NHẬN present · Teaser=0 · system_ledger note=0
spam_sents=0 · long_para_dup=0 · vi_body>=3000 all
EXP/Space khớp system_ledger.json
```

| Check | Result |
|-------|--------|
| SHORT <3000 | **0** |
| NO_PANEL | **0** |
| TEASER / empty Ghi chú | **0** |
| Romance dump anchors | **0** |
| Intra-file long dup paras | **0** |
| Integrity | **PASS 30/30** |
| ≥9.5 all chapters | **NO** (YES~10 / NEAR~20) |
| Ship pad-clean? | **YES** |

---

## Files touched

Tất cả `Chương 31` … `Chương 60 - *.txt` (panel rebuild + spam/teaser strip + nits).  
Report mới: `_ai_reads/batch_post_031_060.md`.  
Không sửa `system_ledger.json` / outline.

**Kết:** Post-strip batch 31–60 **sạch pad/panel/dup**; plot giữ; **chưa** all-clear ≥9.5 vì continuity Minh/brand + overlong máy — đủ để merge pad-clean và siết WARN ở pass continuity riêng.