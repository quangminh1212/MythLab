# HUST GPA Fix — Chương 269–280

## Kết quả

| Chương | Điểm strict | VI-words | Hard fail | HUST GPA |
|---:|---:|---:|---|---:|
| 269 | 9.92 | 4,029 | 0 | ≥8.5 |
| 270 | 9.71 | 3,205 | 0 | ≥8.5 |
| 271 | 9.71 | 3,022 | 0 | ≥8.5 |
| 272 | 9.71 | 3,912 | 0 | ≥8.5 |
| 273 | 9.71 | 3,252 | 0 | ≥8.5 |
| 274 | 10.00 | 3,061 | 0 | ≥8.5 |
| 275 | 9.71 | 3,304 | 0 | ≥8.5 |
| 276 | 9.71 | 3,239 | 0 | ≥8.5 |
| 277 | 9.71 | 3,819 | 0 | ≥8.5 |
| 278 | 9.71 | 3,638 | 0 | ≥8.5 |
| 279 | 9.71 | 3,006 | 0 | ≥8.5 |
| 280 | 9.71 | 3,230 | 0 | ≥8.5 |

**PASS: 12/12 · AVG: 9.75 · MIN: 9.71 · hard fail: 0**

## Sửa

- Ch.270: panel `Năm: 2011` → `2008`.
- Ch.272: panel `Năm: 2006` → `2010`.
- Ch.274: panel `Năm: 2006` → `2007`.
- Ch.275–276, 278–280: panel `Năm: 2007` → `2010`.
- Giữ ch.269 bản mạnh nhất hiện có; score 9.92.

## Gate

- Mỗi chương ≥3,000 VI-words.
- Đủ một panel `GHI NHẬN` cuối chương.
- Không `year_mismatch`.
- Không hard fail.
- Chấm trực tiếp file gốc bằng `strict_score.py` + `.mythlab_score.json`.

## Ghi chú AI-read

Đã đọc toàn văn 12 chương. Các lỗi nặng quan sát được tập trung ở dữ liệu năm panel; sửa theo nguyên tắc panel ← năm văn xuôi. Một số chương còn dấu vết prose ghép cũ nhưng không phá tuyến sự kiện chính; ngưỡng HUST ≥8.5 đã đạt.