# Original User Request

## Initial Request — 2026-07-31T05:31:56Z

Đánh giá toàn bộ 360 chương của tiểu thuyết "Niên Đại Thương Gia" theo bộ tiêu chí tác phẩm văn học quốc tế và chỉnh sửa các chương chưa đạt cho đến khi 100% số chương đạt điểm từ 9.5/10 trở lên.

Working directory: c:\Dev\MythLab\Niên Đại Thương Gia
Integrity mode: development

## Requirements

### R1. Tiêu chí Đánh giá Chất lượng Quốc tế (International Quality Criteria)
Mỗi chương được đánh giá theo 5 tiêu chí cốt lõi:
1. Prose & Literary Quality (Văn phong, nhịp điệu, giác quan): Độ dài 3,000 - 4,200 từ, không lặp từ/từ đệm AI tics, có miêu tả đa giác quan (mùi, tiếng, ánh sáng, nhiệt độ).
2. Plot & Structure (Cốt truyện, cấu trúc): Mạch truyện hấp dẫn, tên chương phản ánh đúng nội dung, có cao trào và chuyển cảnh tự nhiên, cấu trúc chuẩn với header và bảng GHI NHẬN hệ thống.
3. Characterization & Dialogue (Nhân vật & Thoại): Đạt tối thiểu 10 dòng hội thoại tự nhiên, khắc họa rõ nét tính cách nhân vật (Hùng, Lan, bà Hà, Hạnh, Minh, v.v.).
4. Continuity & System Integrity (Tính liên tục & Hệ thống): Khớp nối dữ liệu sổ cái, không mâu thuẫn mốc thời gian, duy trì định dạng header chuẩn.
5. Zero Filler & High Density (Mật độ thông tin, không từ thừa): Không chứa các câu đệm vô nghĩa, marker rác, hoặc dòng lặp lại.

### R2. Tự động Đánh giá và Nâng cấp Chỉnh sửa (Audit & Rewrite Loop)
Xây dựng và chạy quy trình kiểm duyệt tự động (Audit script & AI Rewriter) duyệt từng chương trong số 360 chương. Với mỗi chương có score < 9.5:
- Xác định nguyên nhân bị trừ điểm (thiếu hội thoại, thiếu yếu tố giác quan, sai số lượng từ, lặp từ, filler).
- Thực hiện chỉnh sửa / bổ sung trực tiếp vào tệp chương `.txt` tương ứng.
- Chạy lại audit để đảm bảo điểm đạt >= 9.5/10.

### R3. Báo cáo & Kiểm tra độc lập (Reporting & Audit Verification)
Xuất báo cáo tổng hợp kết quả (ví dụ `score95_final.json`) chứng minh tất cả 360 chương đều đã được kiểm duyệt và đạt điểm từ 9.5/10 trở lên.

## Acceptance Criteria

### Audit Coverage & Score Threshold
- [ ] 100% các chương từ Chương 1 đến Chương 360 đạt điểm tổng hợp >= 9.5/10 theo bộ kiểm tra `audit_all.py`.
- [ ] Tất cả các chương đạt độ dài chuẩn (3,000 - 4,200 từ), không còn lỗi filler hay marker rác.
- [ ] File báo cáo tổng hợp `score95_final.json` thể hiện đầy đủ điểm số chi tiết từng chương.
