# BÁO CÁO KIỂM TRA TOÀN BỘ 360 CHƯƠNG — Niên Đại Thương Gia

**Ngày:** 2026-08-04  
**Phương pháp:** Scan tự động (year, encoding, cast, filler) + đọc thủ công xác nhận  
**Phạm vi:** Chương 1–360, TOÀN BỘ

---

## 📊 TỔNG QUAN

| Chỉ số | Kết quả |
|--------|---------|
| Tổng chương | 360 |
| Panel-Prose match | **301/360 (83.6%)** ✅ |
| Panel-Prose mismatch | 59/360 (16.4%) — phần lớn do flashback |
| Year jump ngược (thứ tự) | 74/360 (20.6%) — THỨ TỰ CHƯƠNG |
| File encoding | **360/360 SẠCH** ✅ (null bytes = false positive) |
| Word count | **360/360 ≥3000 tokens** (min=3056, avg=4160) ✅ |
| Filler patterns | 784+ occurrences |
| Title trùng | 3 cặp |
| Chinese chars | 3 file |

---

## 1. TIMELINE — THỨ TỰ CHƯƠNG KHÔNG THEO NĂM 🔴

### Phát hiện quan trọng

**Panel year GẦN NHƯ ĐÚNG** — 301/360 chương có panel year khớp với prose year. Vấn đề KHÔNG PHẢI panel sai, mà là **thứ tự các chương không theo trật tự thời gian**.

### Minh họa:
```
Ch.9  (1983) → Ch.10 (1986) → Ch.11 (1983) → Ch.12 (1984)
            ↑ nhảy +3 năm    ↑ nhảy -3 năm   ↑ nhảy +1 năm
```

Năm 1986 (Ch.10) đứng giữa hai chương 1983, tạo ra "nhảy ngược". Panel và prose của từng chương đều ghi đúng năm — nhưng thứ tự chapter sai.

### Phạm vi:
- **74 lần nhảy ngược** (năm chương sau < năm chương trước)
- Nhảy lớn nhất: Ch.306 (2003) sau Ch.305 (2014) → lùi 11 năm
- Phổ biến: nhảy 1-2 năm (do chapter được viết xen kẽ)

### Phân bổ năm (chỉ readable):
```
1983: 11 ch  │ 1984: 26 ch  │ 1985: 22 ch  │ 1986: 17 ch
1987: 18 ch  │ 1988: 18 ch  │ 1989: 15 ch  │ 1990: 11 ch
1991: 10 ch  │ 1992: 10 ch  │ 1993: 13 ch  │ 1994: 11 ch
1995: 10 ch  │ 1996: 3 ch   │ 1997: 7 ch   │ 1998: 12 ch
1999: 6 ch   │ 2003: 4 ch   │ 2005: 1 ch   │ 2006: 5 ch
2007: 8 ch   │ 2008: 21 ch  │ 2009: 16 ch  │ 2010: 18 ch
2011: 9 ch   │ 2012-2024: phân bổ đều
```

→ Năm 1996 chỉ có **3 chương** cho 15 năm kinh doanh. Năm 2008 có **21 chương** (khủng hoảng Lehman).

### Cách xử lý:
Đây là vấn đề **cấu trúc**, không thể fix bằng cách đổi panel year. Cần:
1. **Chấp nhận non-linear** nếu deliberate (flashback chapters có thể hợp lý)
2. **Hoặc reorder chapters** theo chronological (rủi ro phá vỡ narrative flow)

---

## 2. PANEL-PROSE MISMATCH — 59 CHƯƠNG CẦN XEM XÉT 🟠

301/360 match (83.6%). Trong 59 mismatch:

### False positives (panel ĐÚNG, prose mention flashback):
- **Ch.263**: Panel 2010, prose mentions "1984" — **FLASHBACK** (title: "Flashback 25 năm")
- **Ch.357**: Panel 2023, prose mentions "1983" — **FLASHBACK** (title: "Flashback toàn hành trình")
- Nhiều chương khác mention "1983" vì đó là năm sáng lập

### Cần xem xét kỹ:
| Chương | Panel | Prose dominant | Ghi chú |
|--------|-------|---------------|---------|
| Ch.91 | 1988 | 1987 | Prose nói 1988 ở opening, 1987 ở ghi chú |
| Ch.188 | 1996 | 1995 | Có thể panel đúng |
| Ch.220 | 1999 | 2007 | Ghi chú "Triển lãm CN châu Á 2007" |
| Ch.327 | 2015 | — | "Lễ 30 năm" → 1983+30=2013, nhưng panel 2015 |

---

## 3. TITLE ISSUES 🟡

### Trùng lặp:
| Pair | Title | Vấn đề |
|------|-------|--------|
| Ch.34 & Ch.52 | "Tuyển kỹ sư Minh" | Trùng title hoàn toàn |
| Ch.65 & Ch.72 | "Mở rộng chi nhánh tài chính" | Trùng title |
| Ch.105 & Ch.199 | "Tổng kết Phần 3" | Trùng title + Ch.199 có thể duplicate |

### Mismatch:
- **Ch.31**: Title "Tổng kết năm **1983**" nhưng panel ghi 1985

### Part structure trùng lặp:
Phần 3 có **3 chương "kết thúc"**:
- Ch.105: "Tổng kết Phần 3" (1987)
- Ch.112: "Hoàn thành phần 3" (1990)
- Ch.199: "Tổng kết Phần 3" (binary content)

→ Không rõ ranh giới thực sự của Phần 3.

---

## 4. ENCODING ✅

**360/360 file sạch UTF-8.** Null bytes scan ban đầu là **false positive** — verify lại bằng full scan cho thấy 0 file có null bytes.

---

## 5. CAST CONSISTENCY 🟡

### Cast lock yêu cầu:
- bà Hà = **MẾ** (mother-figure)
- Lan = **EM GÁI** Hùng (sister)
- Minh = **CON TRAI** Hùng (son)

### "bà nội" violations — 10 chương:
Ch.5, 32, 45, 60, 232, 260, 262, 263(x3), 330, 351

→ Gọi "bà nội" đúng với perspective MINH (cháu nội) nhưng có thể mâu thuẫn với established lock "MẾ". **Xác nhận: "bà nội" đúng hay sai?**

### "vợ Hùng" — 51 chương:
Phần lớn là reference đến **cô Hạnh** (vợ Hùng). Không vi phạm cast lock vì cast chỉ khóa bà Hà/Lan/Minh.

### Hai nhân vật tên Minh:
- **Nguyễn Đức Minh** (kỹ sư cơ khí, Ch.34/52)
- **Minh con Hùng** (con trai, Ch.89+)

→ Cần phân biệt rõ trong prose.

---

## 6. FILLER PATTERNS 🟠

784+ occurrences (trung bình 3/chapter):

| Pattern | Lần | Mức độ |
|---------|-----|--------|
| "không khí" | 261 | Overuse |
| "cảm giác" | 209 | Overuse |
| "tiếng gió" | 137 | Overuse |
| "mùi đất ẩm" | 95 | Overuse |
| "nắng chiều" | 82 | Overuse |

---

## 7. CHINESE CHARACTERS 🟡

3 file có ký tự Hán:
- **Ch.36**: 2 ký tự
- **Ch.171**: 3 ký tự
- **Ch.295**: 4 ký tự

---

## 8. WORD COUNT ✅

Tất cả 360 chương ≥3000 VI-tokens:
- Min: 3,056 (Ch.140)
- Max: 5,886 (Ch.194)
- Avg: 4,160

---

## ƯU TIÊN XỬ LÝ

### P0 — ẢNH HƯỞNG ĐẾN ĐỌC HIỂU:
1. **Thứ tự chương timeline** — 74 backward jumps. Quyết định: reorder hay chấp nhận non-linear?
2. **Part structure** — Phần 3 có 3 kết thúc. Cần chọn 1.

### P1 — CẦN FIX:
3. **Title trùng** — Ch.34/52, Ch.65/72, Ch.105/199
4. **Panel-prose mismatch** — 59 chương cần review kỹ (phần lớn OK)
5. **Chinese characters** — 3 file

### P2 — CHẤT LƯỢNG:
6. **"bà nội" vs "MẾ"** — Xác nhận cast lock
7. **Filler cleanup** — 784+ occurrences
8. **Hai Minh** — Phân biệt tên

---

## KẾT LUẬN

**Niên Đại Thương Gia có nền tảng tốt:** 83.6% panel-prose match, word count ổn, encoding sạch.

**Vấn đề lớn nhất là STRUCTURAL:** thứ tự chương không theo chronological timeline. Đây là vấn đề CẦN QUYẾT ĐỊNH (chứ không phải bug đơn giản).

**Nếu chấp nhận non-linear:** chỉ cần fix title duplicates + filler + cast niggles.
**Nếu cần chronological:** phải reorder 74+ chapter positions — công việc lớn.

Câu hỏi cho tác giả: Thứ tự chương có deliberate non-linear không?
