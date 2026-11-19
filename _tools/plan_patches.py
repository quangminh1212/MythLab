import os, json

base = r"C:/Dev/MythLab/Niên Đại Thương Gia"

# Map user's desired chapters to actual files with character
# Strategy: for each character, find chapters where they have DIALOGUE/ACTION and add interiority

# TANAKA - key chapters with real scenes:
tanaka_patches = [
    # Ch.49 equivalent: Tanaka's first meeting (Ch.49 - Đón FDI đầu tiên.txt)
    # BUT this file doesn't show in directory listing, rg finds it
    # Let me try to find and read it
    {
        "ch_match": "Chương 49",
        "detail": "First meeting - Tanaka sizing up Hùng",
        "interiority": "\n\nTrong lòng Tanaka, một cảm giác quen thuộc trỗi dậy — cái nhìn của người đàn ông trẻ trước mặt khiến ông nhớ lại chính mình ba mươi năm trước, khi ông còn là một thương nhân tập sự ở Osaka, tay trắng nhưng mắt sáng. Ông biết mình sẽ ký hợp đồng này, dù rủi ro cao. Không phải vì số liệu — vì ánh mắt ấy.",
    },
    # Ch.129 - Bước lùi để tiến xa hơn - Tanaka phone call
    {
        "ch_match": "Chương 129 - Bước lùi để tiến xa hơn.txt",
        "old": "Tanaka im lặng ba giây — thời gian im lặng đủ để Hùng nghe tiếng thở của chính mình trong ống nghe. \"Đây là lần đầu tiên một đối tác Việt Nam yêu cầu thăm nhà máy. Ông có chắc không?\"",
        "new": "Tanaka im lặng ba giây — thời gian im lặng đủ để Hùng nghe tiếng thở của chính mình trong ống nghe. Trong ba giây ấy, Tanaka nhìn ra cửa sổ căn phòng làm việc của mình ở Osaka, nơi hoa anh đào đang rụng cánh sau cơn mưa sáng. Ông nghĩ về quyết định năm xưa — ký hợp đồng với một thanh niên Việt Nam khi chưa có gì bảo đảm ngoài lời hứa. Ông già rồi, nhưng trực giác vẫn còn. Và trực giác bảo ông: người đàn ông này sẽ đến. \"Đây là lần đầu tiên một đối tác Việt Nam yêu cầu thăm nhà máy. Ông có chắc không?\"",
    },
    # Ch.200 - Lễ kỷ niệm 10 năm - Tanaka's silent moment
    {
        "ch_match": "Chương 200 - Lễ kỷ niệm 10 năm.txt",
        "old": "Tanaka đứng dậy, bước về phía sân khấu. Ông ta không lên bục — chỉ đứng dưới, bắt tay Hùng. Không nói gì. Hùng cũng không nói gì. Hai người nhìn nhau — một cái nhìn dài. Rồi Tanaka quay về chỗ, ngồi xuống, nhắm mắt. Đúng kiểu Tanaka.",
        "new": "Tanaka đứng dậy, bước về phía sân khấu. Ông ta không lên bục — chỉ đứng dưới, bắt tay Hùng. Không nói gì. Trong lòng Tanaka, một niềm tự hào lặng lẽ dâng lên — không phải tự hào về bản thân, mà là cảm giác của một người thầy khi thấy học trò mình làm được nhiều hơn chính mình. Ông nghĩ về quyết định năm 2004 khi cả công ty bảo ông điên. Mười năm sau, ông muốn nói: \"Tôi đã đúng.\" Nhưng ông không nói. Ông chỉ bắt tay. Hùng cũng không nói gì. Hai người nhìn nhau — một cái nhìn dài. Rồi Tanaka quay về chỗ, ngồi xuống, nhắm mắt. Đúng kiểu Tanaka.",
    },
    # Ch.260 - Chuỗi giá trị toàn cầu - Tanaka gửi email hỏi
    {
        "ch_match": "Chương 260 - Chuỗi giá trị toàn cầu.txt",
        "old": "Tanaka gửi email",
        "new": "Tanaka gửi email và Hùng biết rằng đằng sau mấy dòng chữ ngắn ngủi ấy là cả một sự trăn trở. Người Nhật không dễ hỏi xin. Tanaka hỏi tức là ông ta đã kiểm tra, đã tính toán, đã thấy Thương Gia là lựa chọn tốt nhất. Hùng mỉm cười trước màn hình — không phải vì đơn hàng, mà vì chữ \"xin\" từ một người đàn ông chưa từng nói \"xin\" với ai suốt hai mươi năm hợp tác. Tanaka gửi email",
    },
]

# For Tuấn, the scene in Ch.49 - Mua đất miền Nam is his best appearance
# He's the restaurant manager, gives advice, helps measure land, etc.

print("Mapped patches:", len(tanaka_patches))
for t in tanaka_patches:
    print(f"  {t.get('ch_match', '?')}: {t.get('detail', '')}")
