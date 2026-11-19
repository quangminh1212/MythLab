#!/usr/bin/env python3
"""
Thêm nội tâm cho Tanaka và Tuấn.
Mỗi patch: 50-80 từ interiority vào đoạn họ xuất hiện (đối thoại/hành động).
"""
import os

BASE = r"C:/Dev/MythLab/Niên Đại Thương Gia"
DRY_RUN = False

def apply(fname, old, new):
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"  SKIP: {fname} not found")
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old not in content:
        print(f"  FAIL: old_str not found in {fname}")
        print(f"        Looking for: {old[:80]}...")
        return False
    count = content.count(old)
    if count > 1:
        print(f"  FAIL: {count} occurrences in {fname}")
        return False
    content = content.replace(old, new)
    if not DRY_RUN:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print(f"  OK: {fname}")
    return True

count = 0

# ==============================
# TANAKA (8 patches)
# ==============================

# T1: Ch.49 - Đón FDI đầu tiên - Tanaka's first meeting, after he proposes JV
count += apply(
    "Chương 49 - Đón FDI đầu tiên.txt",
    'Hùng suy nghĩ. FDI — vốn đầu tư nước ngoài. Trong thời sau Đổi Mới, Việt Nam cần vốn nước ngoài để phát triển. Ông Tanaka đề xuất liên doanh — 50-50, cùng đầu tư, cùng chia lời.',
    'Hùng suy nghĩ. FDI — vốn đầu tư nước ngoài. Trong thời sau Đổi Mới, Việt Nam cần vốn nước ngoài để phát triển. Ông Tanaka đề xuất liên doanh — 50-50, cùng đầu tư, cùng chia lời.\n\nTanaka nhìn Hùng — cái nhìn của một người đã từng ngồi bên kia bàn đàm phán. Trong đầu ông, một giọng nói từ ba mươi năm trước vọng về: "Mày cũng từng không có gì ngoài một cái bàn gỗ và một cuốn sổ, Tanaka ạ." Ông thấy ở Hùng cái ông đã mất — sự liều lĩnh của tuổi trẻ. Nhưng ông không nói điều đó. Ông chỉ ngồi im, chờ câu trả lời.',
)

# T2: Ch.129 - Bước lùi để tiến xa hơn - Tanaka phone call
count += apply(
    "Chương 129 - Bước lùi để tiến xa hơn.txt",
    'Tanaka im lặng ba giây — thời gian im lặng đủ để Hùng nghe tiếng thở của chính mình trong ống nghe. "Đây là lần đầu tiên một đối tác Việt Nam yêu cầu thăm nhà máy. Ông có chắc không?"',
    'Tanaka im lặng ba giây — thời gian im lặng đủ để Hùng nghe tiếng thở của chính mình trong ống nghe. Tanaka nhìn ra cửa sổ căn phòng làm việc — hoa anh đào đang rụng cánh sau cơn mưa sớm. Ông nhớ lại năm 2004, khi chính ông gọi cho cha mình để xin phép phá bỏ quy tắc gia tộc mà hợp tác với một người Việt vô danh. Cha ông đã im lặng lâu hơn thế này. "Đây là lần đầu tiên một đối tác Việt Nam yêu cầu thăm nhà máy. Ông có chắc không?"',
)

# T3: Ch.200 - Lễ kỷ niệm 10 năm - Tanaka bắt tay không nói
count += apply(
    "Chương 200 - Lễ kỷ niệm 10 năm.txt",
    'Tanaka đứng dậy, bước về phía sân khấu. Ông ta không lên bục — chỉ đứng dưới, bắt tay Hùng. Không nói gì. Hùng cũng không nói gì. Hai người nhìn nhau — một cái nhìn dài. Rồi Tanaka quay về chỗ, ngồi xuống, nhắm mắt. Đúng kiểu Tanaka.',
    'Tanaka đứng dậy, bước về phía sân khấu. Ông ta không lên bục — chỉ đứng dưới, bắt tay Hùng. Trong lòng Tanaka, một niềm tự hào lặng lẽ dâng lên. Ông thấy chính mình thời trẻ trong Hùng — người đàn ông Việt Nam ấy đã xây dựng cả một đế chế từ hai bàn tay trắng, giữ trọn chữ tín suốt mười năm. Ông muốn nói: "Tôi đã đúng khi tin anh." Nhưng ông không nói. Không nói gì. Hùng cũng không nói gì. Hai người nhìn nhau — một cái nhìn dài. Rồi Tanaka quay về chỗ, ngồi xuống, nhắm mắt. Đúng kiểu Tanaka.',
)

# T4: Ch.89 - Tổng kết Phần 2 - Tanaka đo turbine
count += apply(
    "Chương 89 - Tổng kết Phần 2.txt",
    '— Mục năm — năng lượng. Bốn tổ turbine. Tanaka tự tay đo van, đạt 50 Hz, không nói, chỉ gật.',
    '— Mục năm — năng lượng. Bốn tổ turbine. Tanaka tự tay đo van, đạt 50 Hz, không nói, chỉ gật. Hùng biết cái gật ấy là cả một sự đánh giá: Tanaka đã kiểm tra từng mối nối, từng con ốc, từng thông số kỹ thuật trước khi đặt bút ký. Ông già Nhật tin vào con số đo được, không tin vào lời hứa. Với ông, một cái gật nặng hơn mọi chữ ký.',
)

# T5: Ch.97 - Sản xuất điện tử - Tanaka cung cấp linh kiện
count += apply(
    "Chương 97 - Sản xuất điện tử.txt",
    'Minh gật đầu. "Điện tử — em hiểu cơ bản. Linh kiện — nhập Nhật (qua Tanaka): màn hình CRT, mạch điện, loa, vỏ nhựa. Lắp ráp tại chỗ — công nhân hàn, lắp, kiểm tra. Em cần kỹ sư điện tử — người hiểu mạch, hiểu hàn."',
    'Minh gật đầu. "Điện tử — em hiểu cơ bản. Linh kiện — nhập Nhật (qua Tanaka): màn hình CRT, mạch điện, loa, vỏ nhựa. Lắp ráp tại chỗ — công nhân hàn, lắp, kiểm tra. Em cần kỹ sư điện tử — người hiểu mạch, hiểu hàn."\n\nỞ Osaka, khi nhận được danh sách linh kiện từ Hùng, Tanaka ngồi lại một mình trong văn phòng. Một xưởng nhỏ ở Việt Nam dám đặt mua linh kiện Nhật để tự lắp ráp — điều mà ngay cả các công ty Đông Nam Á khác cũng ngại. Ông chấp nhận đơn hàng, nhưng thầm đặt cược: nếu Hùng làm được, ông sẽ đầu tư dài hạn.',
)

# T6: Ch.350 - Du hành thế giới - Tanaka rót trà ở Osaka
count += apply(
    "Chương 350 - Du hành thế giới.txt",
    'Tanaka gật đầu nhẹ, không cười. Ông ta rót trà, hai tay, từ từ. Từng giọt trà xanh chảy vào chén gốm đen, tiếng nước róc rách trong không gian tĩnh lặng.',
    'Tanaka gật đầu nhẹ, không cười. Ông ta rót trà, hai tay, từ từ — như thể mỗi giọt trà là một kỷ niệm đang chảy ra từ chiếc ấm gốm cũ. Ông đã tưởng tượng cuộc gặp này nhiều lần kể từ khi vợ mất. Người duy nhất ông muốn gặp trước khi nhắm mắt không phải thân nhân, mà là người Việt Nam đã dạy ông rằng chữ tín vượt qua mọi rào cản ngôn ngữ. Từng giọt trà xanh chảy vào chén gốm đen, tiếng nước róc rách trong không gian tĩnh lặng.',
)

# T7: Ch.305 - Gặp lại ông Tanaka - thêm interiority vào cuối cảnh máy bay
count += apply(
    "Chương 305 - Gặp lại ông Tanaka.txt",
    'Hùng gấp sổ, nhìn ra cửa sổ máy bay. Mây trắng trải dài dưới cánh bay như một tấm thảm vô tận. Phía dưới là biển, xanh thẫm, lấp lánh ánh mặt trời.',
    'Hùng gấp sổ, nhìn ra cửa sổ máy bay. Mây trắng trải dài dưới cánh bay như một tấm thảm vô tận. Phía dưới là biển, xanh thẫm, lấp lánh ánh mặt trời. Ông nghĩ về Tanaka — người đàn ông đã tin tưởng mình trước khi có bất kỳ bằng chứng nào. Trong thương trường, ai cũng nói về lợi nhuận. Nhưng thứ đọng lại sau cùng không phải con số — là những người dám đặt cược vào nhau giữa vô vàn rủi ro.',
)

# T8: Ch.260 - Chuỗi giá trị toàn cầu - Tanaka email interiority (add after the line that's already about Tanaka)
count += apply(
    "Chương 260 - Chuỗi giá trị toàn cầu.txt",
    'Lan mừng, nhưng cô giấu đi. "Còn chuyện này nữa. Tanaka gửi email hỏi về khả năng sản xuất giày thể thao. Họ muốn đặt hàng thử nghiệm một lô nhỏ, khoảng năm trăm đôi, để kiểm tra chất lượng trước khi \n\nTanaka ở Tokyo không biết rằng cái email ấy ông đã viết đi viết lại ba lần. Lần đầu quá cứng nhắc — người Nhật quen giữ khoảng cách. Lần hai quá mềm — sợ mất mặt với đối tác cũ. Lần ba ông bỏ hết khuô',
    'Lan mừng, nhưng cô giấu đi. "Còn chuyện này nữa. Tanaka gửi email hỏi về khả năng sản xuất giày thể thao. Họ muốn đặt hàng thử nghiệm một lô nhỏ, khoảng năm trăm đôi, để kiểm tra chất lượng trước khi ký hợp đồng lớn."\n\nKhông ai biết rằng cái email ấy Tanaka đã viết đi viết lại ba lần. Lần đầu quá cứng nhắc — người Nhật quen giữ khoảng cách. Lần hai quá mềm — sợ mất mặt với đối tác cũ. Lần ba ông bỏ hết khuôn mẫu, viết như viết cho một người bạn. Vì sau bao nhiêu năm, Hùng không còn là đối tác — là người ông tin nhất.',
)

print(f"\nTotal successful patches: {count}")
