from pathlib import Path
import re

base = Path('.')
markers = ['「Hệ thống','«Hệ thống','「PANEL」','「HỆ THỐNG','【Hệ thống','【HỆ THỐNG']

def count_tok(text):
    body = text[:max(text.rfind(m) for m in markers)] if any(m in text for m in markers) else text
    return len([w for w in body.split() if len(w) >= 2])

S1 = '''

Nửa đêm sau khi về đến nhà, Hùng không ngủ được. Ông ra hiên, ngồi xuống chiếc ghế tre cũ. Bà Hà thức dậy, ra ngồi cạnh, không hỏi. Bà chỉ đặt tay lên tay ông. Một lúc sau, bà vào nhà, mang ra chiếc áo len mới đan — màu nâu sẫm, cổ tròn, đường kim đều đặn. "Mày ra nước ngoài, mặc cái này cho ấm." Hùng mặc vào. Áo hơi rộng, nhưng ấm. Ông nghĩ: mẹ già rồi, vẫn ngồi đan cho mình. Đan bằng đôi tay run, bằng đôi mắt kém. Nhưng áo vẫn đẹp. Ông không nói gì. Chỉ ngồi đó, mặc áo len mới, nhìn sân nhà trong bóng tối, cảm thấy mình vẫn là đứa trẻ mười tuổi năm nào dù đã đi qua hai nước.
'''

S2 = '''

Lan ở bàn bên, mở cuốn sổ từ vựng, viết thêm: "Telex — máy điện tín. Sample — mẫu. Specification — quy cách kỹ thuật." Cô ghi chép cẩn thận như học sinh. Bên ngoài, nắng sớm tháng Mười hai chiếu xiên qua khung cửa sổ nhỏ. Một buổi sáng Hà Nội điển hình — lạnh, ẩm, có sương mờ. Nhưng hôm nay có một cảm giác khác: sự háo hức.
'''

S3 = '''

Đêm đó, Hùng nằm trên giường, mắt nhắm nhưng đầu óc vẫn chạy. Những hình ảnh về Tanaka đo bán kính quạt, về Park lật hợp đồng bằng ngón tay cái, về Busan với nghìn container xếp dài bất tận, hiện ra lần lượt. Ông nghĩ về điều Tanaka nói: "Muốn bán dài lâu, anh phải xây quy trình ổn định." Câu đó đơn giản nhưng sâu quá. Cả đời ông chạy theo đơn hàng, theo hợp đồng, theo mối quan hệ. Nhưng chưa bao giờ ông nghĩ về "quy trình ổn định" như một thứ tài sản. Ông trở mình, vặn nhỏ ngọn đèn dầu. Sáng mai ông sẽ ghi vào sổ: thuê người viết quy trình sản xuất.
'''

# ----- CH 135 (1515t) -----
f = next(base.glob('Chương 135 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('135 before:', count_tok(text))

# Insert S1 before panel
text = text[:p] + S1 + text[p:]
# Insert S2 before the Buoi sang scene
p2 = text.find('Buổi sáng, Hùng nhận được telex')
if p2 > 0:
    text = text[:p2] + S2 + text[p2:]
# Insert S3 right before panel
p3 = text.rfind('「Hệ thống')
text = text[:p3] + S3 + text[p3:]

t = count_tok(text)
print('135 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    print('  STILL SHORT, adding more')
    # One more expansion at the end
    p4 = text.rfind('「Hệ thống')
    S4 = '\n\nTrong lòng ông lúc ấy dịu lại — cái dịu hiếm hoi của một người đàn ông vừa đặt một bước chân khác vào thế giới rộng lớn. Ông tự nhủ: đường xa, nhưng đi được bước nào hay bước ấy.\n'
    text = text[:p4] + S4 + text[p4:]
    t = count_tok(text)
    print('135 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

# ----- CH 133 (1801t) -----
ch133_insert = '''
Giữa lúc chờ Lim trả lời telex, Hùng ngồi một mình ngoài hiên kho. Chiếc radio cũ đặt trên bệ gạch đang phát bản tin thời sự — giá gạo xuống, giá phân bón lên, một đoàn tàu chở hàng từ Trung Quốc vừa qua biên giới. Hùng tắt radio. Ông không cần tin tức để biết mình đang ở đâu. Ông cần tin từ Penang và Manila.
'''
ch133_s2 = '''
Buổi tối hôm nhận được telex Lim đồng ý, Hùng mở cuốn sổ tay bìa đen, viết: "Lim — người Hoa Penang. Cách làm: mẫu in thử trước, giảm 1% + quà. Nhớ cho lần sau." Ông dừng bút, nghĩ về bài học vừa học: đàm phán không chỉ là giá, mà là cách làm cho đối phương cảm thấy họ thắng. Nếu Lim không được giảm, có thể ông ta sẽ tìm người khác. Nếu Hùng không chịu giảm gì, cuộc đàm phán tan vỡ. Cả hai đều nhượng bộ một chút — và cả hai đều thắng.
'''

f = next(base.glob('Chương 133 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('133 before:', count_tok(text))

text = text[:p] + ch133_insert + text[p:]
p2 = text.find('Hai tháng sau, telex xác nhận')
if p2 > 0:
    text = text[:p2] + ch133_s2 + text[p2:]

t = count_tok(text)
print('133 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    # Add more
    p3 = text.rfind('「Hệ thống')
    S = '\n\nĐêm đó, Lan nằm trên giường nhìn trần nhà. Cô nhẩm tính: Malaysia 7%, Philippines 7.5%. Hai thị trường mới, hai cấu trúc giá khác nhau. Cô thấy rõ một điều: Thương Gia đang lớn nhanh hơn cô tưởng. Ba năm trước, cô còn chưa biết telex là gì. Bây giờ cô đã tự trả lời khách hàng quốc tế. Cô mỉm cười trong bóng tối, và thiếp đi.\n'
    text = text[:p3] + S + text[p3:]
    t = count_tok(text)
    print('133 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

# ----- CH 178 (1924t) -----
ch178_insert = '''
Trên chuyến bay từ Frankfurt đi Paris, Lan ngồi cạnh ô cửa sổ. Bên dưới, những cánh đồng xanh và nâu trải dài như tấm thảm ghép mảng — vuông vức, thẳng hàng, khác hẳn những thửa ruộng nhỏ lẻ Việt Nam. Cô tự hỏi: người ta làm thế nào để sắp xếp mọi thứ ngăn nắp đến vậy? Từ cánh đồng, đến nhà máy, đến lịch trình gặp gỡ. Chị Phương ngồi bên cạnh, ngủ gật, đầu tựa vào cửa kính. Lan nhìn chị — một phụ nữ bốn mươi tuổi, chưa từng ra nước ngoài, nhưng sẵn sàng đi để học. Cô thấy chính mình trong chị.
'''
ch178_s2 = '''
Tối hôm đó, Lan ngồi một mình trong phòng khách sạn Frankfurt, mở cuốn sổ tay. Cô viết: "Ngày 1 — Weber. 0.1% lỗi. ISO sáu tháng. Nếu Thương Gia đạt được ISO, cánh cửa châu Âu sẽ mở." Cô dừng bút. Bảy trang ghi chép sau một ngày — nhiều hơn bất kỳ ngày nào trong đời. Cô nhận ra: sự khác biệt giữa Việt Nam và châu Âu không phải là tiền, không phải là máy móc. Mà là thái độ với chi tiết. Cô gấp sổ, tắt đèn.
'''

f = next(base.glob('Chương 178 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('178 before:', count_tok(text))

text = text[:p] + ch178_insert + text[p:]
# Insert s2 before the scene where Lan calls Hanoi
p2 = text.find('Lan gọi về Hà Nội')
if p2 > 0:
    text = text[:p2] + ch178_s2 + text[p2:]

t = count_tok(text)
print('178 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    p3 = text.rfind('「Hệ thống')
    S = '\n\nKhi máy bay đáp xuống Nội Bài, Lan nhìn qua ô cửa sổ. Những cánh đồng lúa xanh mướt trải dài dưới nắng, những con sông uốn khúc, mái nhà thấp thoáng sau lũy tre. Một cảm giác ấm áp dâng lên — cô đã học được nhiều hơn mong đợi. Cô mở cuốn sổ đen, viết dòng cuối cùng trước khi xuống máy bay: "Người châu Âu giỏi không phải vì họ thông minh hơn. Mà vì họ kỹ hơn. Mình có thể kỹ."\n'
    text = text[:p3] + S + text[p3:]
    t = count_tok(text)
    print('178 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

# ----- CH 271 (1899t) -----
ch271_insert = '''
Sau buổi họp, Hùng bước ra ban công tầng ba. Hà Đông chiều muộn, những mái tôn loang lổ dưới nắng vàng nhạt. Một người đàn ông đang chở củi bằng xe đạp thồ, lưng áo ướt đẫm mồ hôi. Hùng nhìn, thấy mình hai mươi năm trước. Ông tự hỏi: nếu ngày đó mình không mở được xưởng, bây giờ mình có đang làm gì? Câu trả lời không quan trọng. Điều quan trọng là: mình biết ơn những gì đã qua. Ông nhìn xuống bàn tay mình — những vết chai đã mềm, những ngón tay đã bớt sần sùi vì bao năm làm lụng. Nhưng trong lòng, ông vẫn là người thợ ngày nào.
'''
ch271_s2 = '''
Sau cuộc điện thoại với bà Hà, Hùng đặt máy xuống, tay vẫn giữ ống nghe một lúc lâu. Giọng mẹ già yếu nhưng ấm, như ngọn lửa nhỏ trong bếp lạnh. Ông nhớ lại những ngày bà gánh hàng rong đi bán, những đêm bà ngồi vá áo dưới ngọn đèn dầu. Bây giờ bà đã già, không còn đi bán, không còn vá áo — nhưng bà vẫn lo cho ông, vẫn hỏi "ăn cơm chưa", vẫn dặn "đừng làm việc quá khuya". Hùng gấp cuốn sổ tay, cất vào ngăn kéo. Ông tự nhủ: mẹ là lý do để mình không ngừng.
'''

f = next(base.glob('Chương 271 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('271 before:', count_tok(text))

text = text[:p] + ch271_insert + text[p:]
p2 = text.find('Tối, bà Hà gọi điện thoại')
if p2 > 0:
    text = text[:p2] + ch271_s2 + text[p2:]

t = count_tok(text)
print('271 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    p3 = text.rfind('«Hệ thống')
    S = '\n\nTrước khi đi ngủ, Hùng mở cuốn sổ tay, viết thêm một dòng: "15/3/2006 — không phải ngày ký hợp đồng lớn nhất, nhưng là ngày quyết định lớn nhất. Giao mảng ảnh hưởng xã hội cho Lan. Tin tưởng là một canh bạc. Nhưng không tin tưởng còn rủi ro hơn."\n'
    text = text[:p3] + S + text[p3:]
    t = count_tok(text)
    print('271 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

# ----- CH 282 (2240t) -----
ch282_insert = '''
Hùng cầm tập báo cáo tài chính dày bốn mươi bảy trang, lật từng trang một. Những con số nhảy múa trước mắt ông — tiền vào, tiền ra, số dư. Nhưng sau mỗi con số, ông thấy một khuôn mặt: đứa trẻ vùng cao, người mẹ đơn thân, ông già không nơi nương tựa. Ông gấp tập báo cáo và nghĩ: con số nào cũng là một phận người. Sai con số là sai phận người. Từng chữ ký, từng dấu mộc trên hóa đơn — mỗi cái là một lời hứa mà quỹ đã đưa ra với người nghèo.
'''
ch282_s2 = '''
Một tháng sau khi công khai báo cáo, quỹ nhận được phong bì gửi qua đường bưu điện — không tên người gửi, chỉ có một dòng chữ nắn nót: "Cảm ơn chú vì đã làm điều đúng đắn." Bên trong là năm tờ tiền hai mươi nghìn đồng cũ — bà lão thợ may dành dụm gửi tặng quỹ. Hùng đứng im một lúc lâu. Năm tờ tiền nhàu nát đó nói với ông nhiều hơn bất kỳ bản báo cáo tài chính nào.
'''

f = next(base.glob('Chương 282 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('282 before:', count_tok(text))

text = text[:p] + ch282_insert + text[p:]
p2 = text.find('Cuối năm, ông Dũng hỏi Hùng')
if p2 > 0:
    text = text[:p2] + ch282_s2 + text[p2:]

t = count_tok(text)
print('282 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    p3 = text.rfind('「Hệ thống')
    S = '\n\nChiều hôm đó, Hùng ngồi ở quán cóc đầu phố Trần Hưng Đạo, uống cốc chè đỗ đen. Người bán chè — một bà cụ bảy mươi tuổi tai đã lãng, nhưng miệng luôn cười — hỏi ông: "Hôm nay làm việc vui không?" "Vui," Hùng nói. "Vì hôm nay tôi làm được một việc mà tôi nên làm từ hai mươi năm trước."\n'
    text = text[:p3] + S + text[p3:]
    t = count_tok(text)
    print('282 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

# ----- CH 129 (2282t) -----
ch129_insert = '''
Sau cuộc họp khiến cả đội sững sờ, Hùng ra ngồi một mình ở bậc thềm kho. Trời lạnh, gió thổi từ cánh đồng hoang bên cạnh lùa vào từng kẽ áo. Ông lấy gói thuốc lào từ túi áo khoác, vấn một điếu, rít một hơi dài. Khói thuốc tan trong không khí lạnh, quyện với hơi thở thành một làn khói mỏng. Ông nghĩ về câu hỏi của Tuấn chưa được trả lời: "Cắt rồi không biết còn mọc lại không?" Trong lòng ông cũng có câu hỏi đó. Nhưng ông không thể hiện ra. Người lãnh đạo không được phép sợ hãi trước đội ngũ. Nỗi sợ hãi là thứ giống như men rượu — càng giấu lâu càng mạnh, nhưng càng phơi ra sớm càng hỏng cả vại.
'''
ch129_s2 = '''
Đêm hôm đó, Lan ngồi một mình trong phòng trọ, không ngủ được. Cô lấy một tờ giấy học sinh kẻ ngang, bắt đầu viết. Viết ra tất cả những con số: tiền mặt còn lại, nợ phải trả, đơn hàng đã ký, đơn hàng sắp tới. Cô tính đi tính lại ba lần. Mỗi lần, kết quả đều cho thấy: nếu đóng xưởng Hà Đông, Thương Gia vẫn sống thêm được một năm. Một năm, trong tay ba người. Cô không sợ con số. Cô sợ khoảng lặng sau khi đóng cửa — khoảng lặng khi không còn tiếng máy may, không còn bước chân thợ, không còn tiếng cười nói trong xưởng. Nhưng cô biết: khoảng lặng nào cũng sẽ qua. Cô gấp tờ giấy, cất vào sổ tay.
'''

f = next(base.glob('Chương 129 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('129 before:', count_tok(text))

text = text[:p] + ch129_insert + text[p:]
p2 = text.find('Một tuần sau, xưởng Hà Đông đóng cửa')
if p2 > 0:
    text = text[:p2] + ch129_s2 + text[p2:]

t = count_tok(text)
print('129 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    p3 = text.rfind('「Hệ thống')
    S = '\n\nHùng cầm cuốn sổ chỉ tiêu 1990, đọc lại ba dòng mục tiêu: "Giữ được Tanaka. Học được quy trình kiểm soát. Lan làm được vận hành." Ba điều — nhưng là tất cả. Ông biết, nếu hoàn thành được ba điều này trong năm tới, Thương Gia sẽ trở lại mạnh hơn. Còn nếu không — ông không dám nghĩ tiếp. Nhưng ông không cho phép mình nghĩ đến thất bại.\n'
    text = text[:p3] + S + text[p3:]
    t = count_tok(text)
    print('129 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

# ----- CH 144 (2107t) -----
ch144_insert = '''
Hôm đầu tiên ở Vernon, Hùng và Lan dậy từ năm giờ sáng giờ Mỹ — nhưng là mười giờ đêm Hà Nội. Hai người ngồi trong căn phòng khách sạn rẻ tiền gần kho, uống cà phê hòa tan, mở bản đồ Los Angeles trải dài trên sàn. Hùng dùng bút chì khoanh vùng có đông người Việt: Westminster, Garden Grove, San Jose. Lan tra mã bưu điện trong cuốn niên giám mua từ tiệm sách cũ. Bên ngoài, một chiếc xe tải chạy qua, tiếng động cơ diesel ầm ầm làm rung cả cửa kính.
'''
ch144_s2 = '''
Sau khi lô đầu tiên đến San Jose, Hùng nhận được một tấm thiệp từ vợ chồng chủ cửa hàng — trên thiệp có hình lá cờ Mỹ và dòng chữ: "Welcome to America. Your products are beautiful." Hùng đọc đi đọc lại ba lần. Ông không trả lời thiệp — tiếng Anh viết tay của ông không đủ tốt. Nhưng ông gấp tấm thiệp, cất vào cuốn sổ bìa xanh, giữa trang San Jose.
'''

f = next(base.glob('Chương 144 - *.txt'))
text = f.read_text(encoding='utf-8-sig')
p = max(text.rfind(m) for m in markers)
print('144 before:', count_tok(text))

text = text[:p] + ch144_insert + text[p:]
p2 = text.find('Mười hai ngày sau, điện tín từ San Jose')
if p2 > 0:
    text = text[:p2] + ch144_s2 + text[p2:]

t = count_tok(text)
print('144 after:', t)
if t >= 3000:
    f.write_text(text, encoding='utf-8-sig')
    print('  WRITTEN')
else:
    p3 = text.rfind('「Hệ thống')
    S = '\n\nTrên chuyến bay về Việt Nam, Hùng mở cuốn sổ bìa xanh. Từ Los Angeles đến San Jose, từ Houston đến Florida — những cái tên nay đã in vào trí nhớ. Ông đếm: mười lô hàng, sáu đối tác, một lần bị trả. Không tệ cho một năm đầu. Ông ghi vào sổ: "Năm 1990 — mở được Mỹ. Năm 1991 — giữ và nhân rộng."\n'
    text = text[:p3] + S + text[p3:]
    t = count_tok(text)
    print('144 after extra:', t)
    if t >= 3000:
        f.write_text(text, encoding='utf-8-sig')
        print('  WRITTEN')

print('\n=== DONE ===')
