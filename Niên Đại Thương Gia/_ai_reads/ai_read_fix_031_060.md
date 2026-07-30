# AI-read + fix — Chương 31–60

Ngày kiểm: 2026-08-08
Ngưỡng: ≥8.5
Rubric: MythLab strict_score, min 3000 scorer-words, max 4200, có panel hệ thống, continuity niên đại.

## Kết quả

- PASS: 30/30
- Điểm thấp nhất: 9.18 (ch.36, ch.50)
- Điểm cao nhất: 10.00 (ch.45, ch.53, ch.57)
- Hard-fail còn lại: 0
- Chương thiếu độ dài: 0
- Pad marker: 0
- Multi-panel: 0
- Cast violation (`vợ tôi|vợ anh|vợ Hùng`): 0

## Sửa

1. **Ch.31 — `Tổng kết năm 1983`**
   - Lỗi: panel ghi 1984, trong khi cảnh hiện tại mở ngày 3/1/1985; đây là buổi khóa hồi tố sổ 1983.
   - Sửa: `Năm: 1985`.
   - Sau sửa: 9.40; continuity 10; system 10.

2. **Ch.50 — `Cột mốc Chương 41–50`**
   - Lỗi AI-read: đoạn kết bị lặp/cô đặc lại bốn lần, cùng motif “sổ không nói dối / dòng còn mở / trang mới”. Máy không bắt vì các câu không trùng nguyên văn.
   - Sửa: xóa ba bản kết cô đặc, giữ một cảnh kết đầy đủ trước panel.
   - Sau sửa: 3.287 scorer-words; 9.18; hard-fail 0.

3. **Ch.60 — `Hoàn thành nhiệm vụ chi nhánh`**
   - Lỗi AI-read: `cash-flow` lặp dày ở đoạn cuối, lệch giọng niên đại.
   - Sửa: đổi hai chỗ thành `tờ kê thu chi`; giữ một lần trong thân và một lần ở ghi chú panel.
   - Sau sửa: 3.887 scorer-words; 9.71; hard-fail 0.

## Điểm chốt từng chương

| Chương | Điểm | Scorer-words |
|---:|---:|---:|
| 31 | 9.40 | 3398 |
| 32 | 9.40 | 3820 |
| 33 | 9.40 | 3712 |
| 34 | 9.71 | 4086 |
| 35 | 9.40 | 3677 |
| 36 | 9.18 | 3346 |
| 37 | 9.71 | 3392 |
| 38 | 9.71 | 3492 |
| 39 | 9.40 | 3999 |
| 40 | 9.71 | 3435 |
| 41 | 9.71 | 3539 |
| 42 | 9.71 | 3951 |
| 43 | 9.71 | 3549 |
| 44 | 9.71 | 3961 |
| 45 | 10.00 | 3063 |
| 46 | 9.71 | 3428 |
| 47 | 9.71 | 4014 |
| 48 | 9.71 | 3056 |
| 49 | 9.71 | 3585 |
| 50 | 9.18 | 3287 |
| 51 | 9.71 | 3700 |
| 52 | 9.71 | 3751 |
| 53 | 10.00 | 3111 |
| 54 | 9.71 | 3982 |
| 55 | 9.71 | 3669 |
| 56 | 9.71 | 3711 |
| 57 | 10.00 | 3286 |
| 58 | 9.71 | 3465 |
| 59 | 9.71 | 3348 |
| 60 | 9.71 | 3887 |

## Verdict

Ch.31–60 đạt ngưỡng yêu cầu. Các lỗi máy bỏ sót ở đuôi ch.50 và từ ngữ ch.60 đã được xử lý; không cần viết lại hàng loạt.
