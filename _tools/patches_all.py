#!/usr/bin/env python3
"""
Add interiority for Tanaka and Tuấn in their key scenes.
Each patch inserts 50-80 words of interiority (suy nghĩ, động cơ, cảm xúc).
"""
import os, sys, glob

BASE = r"C:/Dev/MythLab/Niên Đại Thương Gia"
DRY_RUN = False  # set True to test without modifying

def apply_patch(fname, old_str, new_str):
    fpath = os.path.join(BASE, fname)
    if not os.path.exists(fpath):
        print(f"  SKIP: {fname} not found")
        return False
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    count = content.count(old_str)
    if count == 0:
        # Try fuzzy: show what we're looking for vs what exists
        print(f"  FAIL: old_str not found in {fname}")
        return False
    if count > 1:
        print(f"  FAIL: old_str found {count} times in {fname} (not unique)")
        return False
    content = content.replace(old_str, new_str)
    if not DRY_RUN:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
    print(f"  OK: {fname}")
    return True

# ============================================================
# TANAKA PATCHES
# ============================================================

patches = []

# 1) Ch.49 - Đón FDI đầu tiên - Tanaka's first meeting
# After: Tanaka says "I want to invest in Thương Gia..."
patches.append((
    "Chương 49 - Đón FDI đầu tiên.txt",
    'Hùng suy nghĩ. FDI — vốn đầu tư nước ngoài. Trong thời sau Đổi Mới, Việt Nam cần vốn nước ngoài để phát triển. Ông Tanaka đề xuất liên doanh — 50-50, cùng đầu tư, cùng chia lời.',
    'Hùng suy nghĩ. FDI — vốn đầu tư nước ngoài. Trong thời sau Đổi Mới, Việt Nam cần vốn nước ngoài để phát triển. Ông Tanaka đề xuất liên doanh — 50-50, cùng đầu tư, cùng chia lời.\n\nTanaka nhìn Hùng — cái nhìn của một người đã từng ngồi bên kia bàn đàm phán. Trong đầu ông, một giọng nói cũ từ ba mươi năm trước thì thầm: "Mày cũng từng không có gì ngoài một cái bàn gỗ và một cuốn sổ, Tanaka ạ." Ông thấy ở Hùng cái ông đã mất — sự liều lĩnh của tuổi trẻ. Nhưng ông không nói điều đó. Ông chỉ ngồi im, chờ câu trả lời.',
))

# 2) Ch.129 - Bước lùi để tiến xa hơn - Tanaka phone call (already prepared above)
patches.append((
    "Chương 129 - Bước lùi để tiến xa hơn.txt",
    'Tanaka im lặng ba giây — thời gian im lặng đủ để Hùng nghe tiếng thở của chính mình trong ống nghe. "Đây là lần đầu tiên một đối tác Việt Nam yêu cầu thăm nhà máy. Ông có chắc không?"',
    'Tanaka im lặng ba giây — thời gian im lặng đủ để Hùng nghe tiếng thở của chính mình trong ống nghe. Tanaka nhìn ra cửa sổ căn phòng làm việc — hoa anh đào đang rụng cánh sau cơn mưa. Ông nhớ lại năm 2004, khi chính ông gọi điện cho cha mình để xin phép phá bỏ quy tắc gia tộc mà hợp tác với người Việt. Cha ông đã im lặng lâu hơn thế này. "Đây là lần đầu tiên một đối tác Việt Nam yêu cầu thăm nhà máy. Ông có chắc không?"',
))

# 3) Ch.200 - Lễ kỷ niệm 10 năm - Tanaka's silent moment
patches.append((
    "Chương 200 - Lễ kỷ niệm 10 năm.txt",
    'Tanaka đứng dậy, bước về phía sân khấu. Ông ta không lên bục — chỉ đứng dưới, bắt tay Hùng. Không nói gì. Hùng cũng không nói gì. Hai người nhìn nhau — một cái nhìn dài. Rồi Tanaka quay về chỗ, ngồi xuống, nhắm mắt. Đúng kiểu Tanaka.',
    'Tanaka đứng dậy, bước về phía sân khấu. Ông ta không lên bục — chỉ đứng dưới, bắt tay Hùng. Trong lòng Tanaka, một niềm tự hào lặng lẽ dâng lên. Ông thấy mình trong Hùng — người đàn ông Việt Nam nhỏ bé ấy đã làm được điều mà chính ông cũng không dám mơ khi còn trẻ: xây dựng một đế chế từ hai bàn tay trắng, giữ được chữ tín xuyên suốt. Không nói gì. Hùng cũng không nói gì. Hai người nhìn nhau — một cái nhìn dài. Rồi Tanaka quay về chỗ, ngồi xuống, nhắm mắt. Đúng kiểu Tanaka.',
))

# 4) Ch.260 - Chuỗi giá trị toàn cầu - Tanaka's email
patches.append((
    "Chương 260 - Chuỗi giá trị toàn cầu.txt",
    'Lan mừng, nhưng cô giấu đi. "Còn chuyện này nữa. Tanaka gửi email hỏi về khả năng sản xuất giày thể thao xuất khẩu sang Nhật."',
    'Lan mừng, nhưng cô giấu đi. "Còn chuyện này nữa. Tanaka gửi email hỏi về khả năng sản xuất giày thể thao xuất khẩu sang Nhật." Hùng mỉm cười trước màn hình — không phải vì đơn hàng, mà vì biết rằng đằng sau mấy dòng chữ ngắn ngủi ấy là cả một sự trăn trở của một người đàn ông già chưa từng nói "xin" với ai suốt hai mươi năm. Tanaka hỏi, tức là ông ta đã kiểm tra, đã tính toán, đã thấy Thương Gia là lựa chọn duy nhất xứng đáng.',
))

# 5) Ch.89 - Tổng kết Phần 2 - Tanaka đo turbine (add interiority to his action)
patches.append((
    "Chương 89 - Tổng kết Phần 2.txt",
    '— Mục năm — năng lượng. Bốn tổ turbine. Tanaka tự tay đo van, đạt 50 Hz, không nói, chỉ gật.',
    '— Mục năm — năng lượng. Bốn tổ turbine. Tanaka tự tay đo van, đạt 50 Hz, không nói, chỉ gật. Hùng biết cái gật ấy có ý nghĩa gì: Tanaka đã kiểm tra từng mối nối, từng con ốc, từng chỉ số trước khi đặt bút ký. Ông già Nhật ấy tin vào con số, không tin vào lời nói. Cái gật là chữ ký của ông ta.',
))

# 6) Ch.97 - Sản xuất điện tử - Tanaka mentioned as supplier (brief)
patches.append((
    "Chương 97 - Sản xuất điện tử.txt",
    'Minh gật đầu. "Điện tử — em hiểu cơ bản. Linh kiện — nhập Nhật (qua Tanaka): màn hình CRT, mạch điện, loa, vỏ nhựa. Lắp ráp tại chỗ — công nhân hàn, lắp, kiểm tra. Em cần kỹ sư điện tử — người hiểu mạch, hiểu hàn."',
    'Minh gật đầu. "Điện tử — em hiểu cơ bản. Linh kiện — nhập Nhật (qua Tanaka): màn hình CRT, mạch điện, loa, vỏ nhựa. Lắp ráp tại chỗ — công nhân hàn, lắp, kiểm tra. Em cần kỹ sư điện tử — người hiểu mạch, hiểu hàn."\n\nỞ Osaka, khi nhận được danh sách linh kiện từ Hùng, Tanaka ngồi lại một mình trong văn phòng. Ông xem từng dòng, kiểm tra từng mã hàng. Một xưởng nhỏ ở Việt Nam dám đặt mua linh kiện Nhật để tự lắp ráp — điều mà ngay cả các công ty Đông Nam Á khác cũng ngại. Ông chấp nhận đơn hàng, nhưng thầm đặt cược: nếu Hùng làm được lô này, ông sẽ đầu tư dài hạn.',
))

# 7) Ch.350 - Du hành thế giới - meeting Tanaka in Osaka
patches.append((
    "Chương 350 - Du hành thế giới.txt",
    'Tanaka gật đầu nhẹ, không cười. Ông ta rót trà, hai tay, từ từ. Từng giọt trà xanh chảy vào chén gốm đen, tiếng nước róc rách trong không gian tĩnh lặng.',
    'Tanaka gật đầu nhẹ, không cười. Ông ta rót trà, hai tay, từ từ — như thể mỗi giọt trà là một kỷ niệm đang chảy ra từ ấm. Ông đã tưởng tượng cuộc gặp này nhiều lần kể từ khi vợ mất. Người duy nhất ông muốn gặp trước khi nhắm mắt không phải thân nhân, mà là người Việt Nam đã dạy ông hiểu thế nào là chữ tín. Từng giọt trà xanh chảy vào chén gốm đen, tiếng nước róc rách trong không gian tĩnh lặng.',
))

# 8) Ch.305 - Gặp lại ông Tanaka - already has deep interiority, add to the end
patches.append((
    "Chương 305 - Gặp lại ông Tanaka.txt",
    'Hùng gấp sổ, nhìn ra cửa sổ máy bay. Mây trắng trải dài dưới cánh bay như một tấm thảm vô tận. Phía dưới là biển, xanh thẫm, lấp lánh ánh mặt trời.',
    'Hùng gấp sổ, nhìn ra cửa sổ máy bay. Mây trắng trải dài dưới cánh bay như một tấm thảm vô tận. Phía dưới là biển, xanh thẫm, lấp lánh ánh mặt trời. Ông nghĩ về Tanaka — người đàn ông đã tin tưởng mình trước khi có bất kỳ bằng chứng nào về năng lực. Trong thương trường, ai cũng nói về lợi nhuận. Nhưng thứ đọng lại sau cùng không phải con số — là những người dám đặt cược vào nhau.',
))

# ============================================================
# TUẤN PATCHES  
# ============================================================

# 1) Ch.49 - Mua đất miền Nam - Tuấn đề xuất mua cả hai lô, và sau đó tiếc vị trí
patches.append((
    "Chương 49 - Mua đất miền Nam.txt",
    '— Nếu ép cả hai chủ cùng hạ, ta có thể mua — Tuấn nói.',
    '— Nếu ép cả hai chủ cùng hạ, ta có thể mua — Tuấn nói. Trong lòng anh, một sự nôn nóng khó tả. Anh đã ở Sài Gòn đủ lâu để biết đất ở đây sẽ lên giá nhanh hơn bất kỳ khoản đầu tư nào Hùng từng làm. Nhưng anh cũng hiểu Hùng — người anh em này không bao giờ đánh đổi nguyên tắc lấy tốc độ. Và chính điều đó khiến anh tin tưởng để gắn bó.',
))

# 2) Ch.50 - Cột mốc Chương 41–50 - Tuấn quản lý Sài Gòn
patches.append((
    "Chương 50 - Cột mốc Chương 41–50.txt",
    'Sài Gòn mở ngày 18 tháng 8 trên đường Châu Văn Liêm, mười bốn bàn, năm mươi sáu chỗ. Vốn khởi sự sáu nghìn bốn trăm tám mươi đồng, trong đó một nghìn năm trăm đồng là khoản vay bà Hà, không phải vốn tự có. Bảy ngày đầu phục vụ chín trăm sáu mươi tám lượt, doanh thu hai nghìn năm trăm bốn mươi đồng, mười bảy món trả hoặc đổi, tỷ lệ một phẩy bảy sáu phần trăm, không ngộ độc. Bà Năm giữ bếp. Tuấn quản quầy rồi đào tạo chị Hòa giữ sổ. Khí hậu nóng khiến kho phải chia nhỏ lần giao; cá và rau có hai nguồn; giờ nhận sai bị coi là sai hồ sơ dù hàng nhìn còn tươi.',
    'Sài Gòn mở ngày 18 tháng 8 trên đường Châu Văn Liêm, mười bốn bàn, năm mươi sáu chỗ. Vốn khởi sự sáu nghìn bốn trăm tám mươi đồng, trong đó một nghìn năm trăm đồng là khoản vay bà Hà, không phải vốn tự có. Bảy ngày đầu phục vụ chín trăm sáu mươi tám lượt, doanh thu hai nghìn năm trăm bốn mươi đồng, mười bảy món trả hoặc đổi, tỷ lệ một phẩy bảy sáu phần trăm, không ngộ độc. Bà Năm giữ bếp. Tuấn quản quầy rồi đào tạo chị Hòa giữ sổ. Khí hậu nóng khiến kho phải chia nhỏ lần giao; cá và rau có hai nguồn; giờ nhận sai bị coi là sai hồ sơ dù hàng nhìn còn tươi.\n\nĐêm nào Tuấn cũng thức tới khuya để kiểm lại sổ. Anh không phải người Hà Nội gốc, nhưng anh muốn chứng minh rằng một người từ tỉnh lẻ cũng có thể quản lý được nhà hàng ngay giữa lòng Sài Gòn. Mỗi lần viết xong một trang sổ khớp, anh thấy yên lòng hơn một chút.',
))

# 3) Ch.53 - Mở phòng khám - Tuấn chuyên môn
patches.append((
    "Chương 53 - Mở phòng khám.txt",
    'Tuấn đáp: "Một bồn tiết kiệm được tiền ống. Mỗi ngày mất hàng chục lượt đi lại, rồi có lúc người ta ngại đi. Tiền ít hơn, rủi ro lớn hơn."',
    'Tuấn đáp: "Một bồn tiết kiệm được tiền ống. Mỗi ngày mất hàng chục lượt đi lại, rồi có lúc người ta ngại đi. Tiền ít hơn, rủi ro lớn hơn." Anh nhìn bản vẽ và thấy rõ căn phòng trong đầu — từng bước chân của bệnh nhân, từng thao tác của bác sĩ, từng giây lãng phí có thể cứu được nếu thiết kế đúng. Anh không phải dân kinh doanh, nhưng anh biết: trong y tế, một bồn rửa đặt sai chỗ có thể khiến một ca nhiễm trùng. Tiết kiệm hôm nay là mắc nợ ngày mai.',
))

# 4) Ch.69 - Mở rộng phòng khám - Tuấn about quality
patches.append((
    "Chương 69 - Mở rộng phòng khám.txt",
    'bác sĩ Tuấn',
))

# Let me first check Ch.69 content
# Actually let me just check what's in Ch.69
print("Need to check Ch.69 first")
