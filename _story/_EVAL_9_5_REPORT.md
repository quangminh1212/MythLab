# Đánh giá MythLab — Niên Đại Thương Gia @ threshold 9.5

- **Tổng chương:** 360
- **PASS ≥9.5:** 307/360 (85.3%)
- **BELOW <9.5:** 53/360
- **AVG final:** 9.687
- **MIN final:** 9.26
- **Hard-fail toàn series:** 0 (continuity / filler / system sạch)
- **Config:** min_words=3000 · max_words=4200 · rebirth=true · 1980–2024

## Phân bố điểm

| Band | Số ch |
|------|------:|
| <9.0 | 0 |
| 9.0-9.29 | 2 |
| 9.3-9.39 | 23 |
| 9.4-9.49 | 28 |
| 9.5-9.69 | 39 |
| 9.7-9.89 | 231 |
| 9.9-10 | 37 |

## Trung bình 6 trục

| Trục | AVG | MIN | Weight |
|------|----:|----:|-------:|
| van_chuong | 9.471 | 8.30 | 20 |
| cau_truc | 9.324 | 6.00 | 15 |
| nhan_vat | 9.292 | 9.00 | 15 |
| continuity | 10.000 | 10.00 | 25 |
| filler_pad | 10.000 | 10.00 | 15 |
| he_thong | 10.000 | 10.00 | 10 |

## Kết luận chấm

**Chưa ALL_PASS 9.5.** 307 chương ≥9.5; 53 chương còn **9.26–9.49**.

### Nguyên nhân chính (cơ học scorer)

Cả 53 chương BELOW đều **vượt `max_words=4200`** (thực tế **4345–7762** VI-tokens).
Công thức: `cau_truc -= min(2.5, (words-4200)/400)` → cấu trúc tụt 6.0–8.5 dù văn/nhân vật/continuity tốt.
**Không hard-fail pad/year/panel.** Đây là phình chữ từ các pass expand trước — không phải lỗi logic continuity.

### BELOW theo phần

- P1 1-60: **26** ch
- P2 61-120: **18** ch
- P3 121-180: **2** ch
- P4 181-240: **5** ch
- P6 301-360: **2** ch

### Danh sách 53 chương < 9.5

| Ch | Final | cau | van | nv | words | file |
|---:|------:|----:|----:|---:|------:|------|
| 77 | 9.26 | 7.50 | 8.9 | 9.0 | 6084 | Chương 77 - Hoàn thành nhiệm vụ đào tạo.txt |
| 355 | 9.26 | 7.50 | 8.9 | 9.0 | 5391 | Chương 355 - Hoàn thành nhiệm vụ tối thượng.txt |
| 1 | 9.32 | 6.00 | 9.6 | 10.0 | 6498 | Chương 1 - Tỉnh lại.txt |
| 21 | 9.34 | 7.50 | 9.3 | 9.0 | 7267 | Chương 21 - Mở rộng làm giày.txt |
| 23 | 9.34 | 7.50 | 9.3 | 9.0 | 6279 | Chương 23 - Sản xuất túi xách.txt |
| 37 | 9.34 | 7.50 | 9.3 | 9.0 | 7434 | Chương 37 - Mở chi nhánh Hà Nội.txt |
| 38 | 9.34 | 7.50 | 9.3 | 9.0 | 7095 | Chương 38 - Sản xuất radio.txt |
| 39 | 9.34 | 7.50 | 9.3 | 9.0 | 5731 | Chương 39 - Mở rộng sản xuất radio.txt |
| 40 | 9.34 | 7.50 | 9.3 | 9.0 | 5785 | Chương 40 - Hoàn thành nhiệm vụ radio.txt |
| 50 | 9.34 | 7.50 | 9.3 | 9.0 | 6120 | Chương 50 - Cột mốc Chương 41–50.txt |
| 51 | 9.34 | 7.50 | 9.3 | 9.0 | 5537 | Chương 51 - Mở chi nhánh Bắc Ninh.txt |
| 55 | 9.34 | 7.50 | 9.3 | 9.0 | 6279 | Chương 55 - Đổi Mới 1986 – Hùng trình bày ý tưởng với cán bộ huyện.txt |
| 56 | 9.34 | 7.50 | 9.3 | 9.0 | 6758 | Chương 56 - Minh qua chín mươi ngày thử việc.txt |
| 58 | 9.34 | 7.50 | 9.3 | 9.0 | 7759 | Chương 58 - Xây dựng thương hiệu Thương Gia trong 30 ngày.txt |
| 61 | 9.34 | 7.50 | 9.3 | 9.0 | 5991 | Chương 61 - Sản xuất xe đạp.txt |
| 64 | 9.34 | 7.50 | 9.3 | 9.0 | 5559 | Chương 64 - Mua 30 xe tải.txt |
| 69 | 9.34 | 7.50 | 9.3 | 9.0 | 6449 | Chương 69 - Mở rộng phòng khám.txt |
| 73 | 9.34 | 7.50 | 9.3 | 9.0 | 6473 | Chương 73 - Hoàn thành nhiệm vụ cho vay.txt |
| 74 | 9.34 | 7.50 | 9.3 | 9.0 | 7273 | Chương 74 - Mở trường học tiếp.txt |
| 76 | 9.34 | 7.50 | 9.3 | 9.0 | 5472 | Chương 76 - Mở rộng trung tâm đào tạo.txt |
| 86 | 9.34 | 7.50 | 9.3 | 9.0 | 5427 | Chương 86 - Mở rộng bảo hiểm.txt |
| 99 | 9.34 | 7.50 | 9.3 | 9.0 | 5437 | Chương 99 - Mở rộng viễn thông.txt |
| 191 | 9.34 | 7.50 | 9.3 | 9.0 | 5205 | Chương 191 - Đầu tư công nghệ cao.txt |
| 63 | 9.37 | 7.75 | 9.3 | 9.0 | 5101 | Chương 63 - Sản xuất máy gặt.txt |
| 44 | 9.39 | 7.87 | 9.3 | 9.0 | 5052 | Chương 44 - Hoàn thành nhiệm vụ đèn.txt |
| 20 | 9.40 | 7.96 | 9.3 | 9.0 | 5014 | Chương 20 - Sản xuất giày dép.txt |
| 22 | 9.40 | 6.00 | 10.0 | 10.0 | 6505 | Chương 22 - Đi Thành phố Hồ Chí Minh.txt |
| 25 | 9.40 | 6.00 | 10.0 | 10.0 | 5210 | Chương 25 - Mở cửa hàng thứ hai.txt |
| 45 | 9.40 | 6.00 | 10.0 | 10.0 | 6716 | Chương 45 - Mở nhà hàng.txt |
| 52 | 9.40 | 7.92 | 9.3 | 9.0 | 5032 | Chương 52 - Tuyển kỹ sư Minh.txt |
| 53 | 9.40 | 6.00 | 10.0 | 10.0 | 7762 | Chương 53 - Mở phòng khám.txt |
| 57 | 9.40 | 6.00 | 10.0 | 10.0 | 6277 | Chương 57 - Xây đội ngũ cốt lõi.txt |
| 66 | 9.40 | 6.00 | 10.0 | 10.0 | 5519 | Chương 66 - Mở rộng trường học.txt |
| 72 | 9.40 | 6.00 | 10.0 | 10.0 | 5616 | Chương 72 - Mở rộng chi nhánh tài chính.txt |
| 78 | 9.40 | 6.00 | 10.0 | 10.0 | 5366 | Chương 78 - Mở rộng phòng khám tiếp.txt |
| 95 | 9.40 | 6.00 | 10.0 | 10.0 | 5973 | Chương 95 - Hùng chọn cô Hạnh.txt |
| 104 | 9.40 | 6.00 | 10.0 | 10.0 | 7485 | Chương 104 - Mở rộng xuất khẩu châu Âu.txt |
| 186 | 9.40 | 6.00 | 10.0 | 10.0 | 5446 | Chương 186 - Lan và chiến lược châu Á mới.txt |
| 187 | 9.40 | 6.00 | 10.0 | 10.0 | 5451 | Chương 187 - Nắm bắt cơ hội từ khủng hoảng.txt |
| 192 | 9.40 | 6.00 | 10.0 | 10.0 | 5373 | Chương 192 - Lan thiết lập chuỗi cung ứng toàn cầu.txt |
| 59 | 9.41 | 8.02 | 9.3 | 9.0 | 4994 | Chương 59 - Mở chi nhánh Ninh Bình.txt |
| 36 | 9.43 | 8.11 | 9.3 | 9.0 | 4957 | Chương 36 - Mở chi nhánh Hoài Đức.txt |
| 43 | 9.43 | 8.16 | 9.3 | 9.0 | 4935 | Chương 43 - Sản xuất đèn điện.txt |
| 145 | 9.43 | 8.15 | 9.3 | 9.0 | 4940 | Chương 145 - Đối mặt đối thủ Trung Quốc tại Mỹ.txt |
| 219 | 9.43 | 8.16 | 9.3 | 9.0 | 4934 | Chương 219 - Xe điện nguyên mẫu.txt |
| 49 | 9.45 | 8.81 | 8.9 | 9.0 | 4677 | Chương 49 - Mua đất miền Nam.txt |
| 54 | 9.45 | 8.28 | 9.3 | 9.0 | 4888 | Chương 54 - Sản xuất mì ăn liền và thực phẩm đóng gói đầu tiên.txt |
| 71 | 9.46 | 8.36 | 9.3 | 9.0 | 4858 | Chương 71 - Mở dịch vụ cho vay.txt |
| 180 | 9.46 | 9.64 | 8.3 | 9.0 | 4345 | Chương 180 - Lan đàm phán với đối tác châu Âu.txt |
| 319 | 9.47 | 8.41 | 9.3 | 9.0 | 4837 | Chương 319 - Cam kết không chia cắt tập đoàn.txt |
| 62 | 9.48 | 8.45 | 9.3 | 9.0 | 4822 | Chương 62 - Sản xuất máy cày.txt |
| 105 | 9.48 | 6.52 | 10.0 | 10.0 | 4992 | Chương 105 - Tổng kết Phần 3.txt |
| 35 | 9.49 | 8.55 | 9.3 | 9.0 | 4779 | Chương 35 - Mở rộng miền Nam.txt |

### Fix tối ưu để ALL_PASS 9.5

1. **Trim** 53 chương về **3000–4200** VI-tokens (giữ beat, cắt lặp giác quan/mở rộng máy).
2. Không cần rewrite toàn bộ — van/nv/cont đã ≥9.
3. Ch.180: van=8.3 (sensory 6.58) — thêm giác quan Berlin/Hà Nội khi trim.
4. (Tuỳ chọn) nới `max_words` lên 5500 nếu muốn giữ bản dài — premium target vẫn 3–3.5k.

## Tham khảo tình tiết MTC nên BỔ SUNG

Nguồn: MythLab `twists/*` + plot-mining ~32k MTC (xuyên/trọng sinh, hệ thống, đô thị, niên đại).
Đã scan series bằng grep — một số beat **chưa có / cực mỏng**.

### A. Gap lớn (0 hit trong series) — ưu tiên cắm

| # | Tình tiết MTC | Nguồn bank | Gợi ý cắm chương |
|---|---------------|------------|------------------|
| 1 | **Song trọng sinh** — kẻ thù/ân nhân cũng quay về | rebirth #2–3; MTC “Song Trọng Sinh” | P3–P4 (ch.160–220): đối thủ HK/TQ lộ chi tiết chỉ người kiếp trước biết |
| 2 | **Phá sản giả để thâu tóm** | business #8 | P4 khủng hoảng 2008 (ch.221–230): đối thủ giả vỡ nợ → Hùng suýt mua bẫy |
| 3 | **Franchise / clone logo** + kiện ngược | business #5 | P2–P3 (ch.90–140): chi nhánh giả “Thương Gia” tỉnh lẻ |
| 4 | **Công thức bí quyết thuộc đối tác đang nợ** | business #1 | P1–P2 thực phẩm/mì (~ch.54) |
| 5 | **Người tin cậy là CEO đối thủ ẩn** | business #9 | Mở rộng arc ch.180 (Tuấn/nội gián) thành 3–5 ch |
| 6 | **Butterfly: cứu người lẽ ra chết → timeline thù mới** | rebirth #7 | P1 sớm (ch.15–40) |
| 7 | **System không unique — bảng xếp hạng host** | system #3 | P5–P6 (ch.300–355): panel lộ Host #N |
| 8 | **Quest thưởng = nợ / khế ước ngầm** | system #2 | 1 lần thưởng space lớn + side-quest đạo đức (không phá ledger) |

### B. Mỏng (đã có nhưng chưa đủ xương)

| Tình tiết | Hit hiện tại | Bổ sung |
|-----------|-------------|---------|
| Tem phiếu giả / cắt tem sổ | ~2 file | 1 arc P1 (ch.8–25) |
| Chỉ điểm / sổ đen thôn–đơn vị | ~38 file | 1 reveal “người tốt là chỉ điểm” (niendai #1) ở P1 |
| Hàng cấm / buôn lậu chuỗi cung | ~10 file | 1 bẫy pháp lý P2–P3 (business #4) |
| Kiểm toán / audit | ~92 file | Đủ; có thể thêm 1 lần sổ sạch che quỹ đen gia đình |
| Đổi Mới / policy whiplash | rất nhiều | Thêm 1 nhát đúng lúc vừa build xong chuỗi (niendai #10) |

### C. Đã đủ — không nhồi (tránh pad)

- Space/kho hệ thống, mở chi nhánh, nhà máy, M&A, xuất khẩu, từ thiện, tri ân đối tác, panel GHI NHẬN, motif bà Hà / sổ tay.
- **Không copy prose** từ `D:\Dev\MTC_*`; chỉ mượn **xương twist + texture niên đại**.

### D. Template cắm 1 tình tiết/chương (anti-pad)

```
Setup (trước 5–20 ch) → giá phải trả trong ch → goal MC đổi nhẹ → micro-reveal cliff
CẤM: monologue giải thích twist; CẤM: lặp khung độn chữ.
```

## Đọc mẫu chất lượng (thủ công)

| Ch | Điểm | Nhận xét ngắn |
|----|------|---------------|
| 1 | 9.32 | Hook trùng sinh mạnh, sensory tốt; **dài 6498w** → cau=6.0 |
| 77 | 9.26 | Đào tạo Đà Nẵng chi tiết số liệu tốt; phình 6084w |
| 180 | 9.46 | Lan Berlin + nội gián Tuấn hay; van thấp (sensory 6.58) |
| 200 | ≥9.5 | Lễ 10 năm — giọng lễ + bà Hà/Lan ổn |
| 350 | ≥9.5 | Tri ân đối tác — gọn, đúng di sản |
| 355 | 9.26 | Climax nhiệm vụ tối thượng tốt; **5391w** phình |

## File kèm

- `_eval_95_live.json` — full scorer dump
- `_eval_95_toanbo.csv` — 360 dòng điểm
- `worklist.json` — 53 ch cần fix
- `.mythlab_score.json` — config scorer

## Next (khi bảo sửa)

1. Batch trim 53 ch (disjoint, cap 6 agent) về ≤4200w
2. Inject 6–8 twist MTC gap vào outline + rewrite đúng beat (không đụng ledger năm/EXP)
3. `python C:/Dev/MythLab/scripts/autopilot_loop.py --dir "..." --threshold 9.5` đến ALL_PASS
