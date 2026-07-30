# -*- coding: utf-8 -*-
"""Large expand ch67/ch76 to clear short hard-fail."""
import glob, json, sys, os

BASE = r"C:/Dev/XLab_MTC/Niên Đại Thương Gia"
os.chdir(BASE)
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
import strict_score as ss

cfg = json.load(open(".mythlab_score.json", encoding="utf-8"))

EXP67 = """
***

Ngày thứ tư, một phụ huynh mang theo cán bộ tổ dân phố đến xin xác nhận miễn giảm. Hạnh tiếp ở phòng giáo viên. Lan đối giấy. Hùng chỉ ngồi góc, lắng nghe, không xen khi câu hỏi còn thuộc chuyên môn lớp.

— Nhà tôi bốn miệng, chồng ốm. — Người mẹ nói, tay siết mép áo. — Cho cháu học miễn hết được không?

Lan mở mẫu:

— Miễn một phần theo xác nhận tổ. Miễn hết chỉ khi hộ đói ghi sổ địa phương. Chị có sổ không?

— Có. Để ở nhà.

— Mai mang. Hôm nay cho cháu vào học đã. — Hạnh gật, mắt dịu. — Không để cháu ngồi ngoài cổng chờ giấy.

Hùng liếc Hạnh, thở nhẹ — đúng thứ tự ông muốn: trẻ vào đã, giấy đi theo, không giấy chặn cửa. Cán bộ tổ ký nháy xác nhận tạm. Lan ghi «chờ sổ gốc», siết bút, buông.

Chiều cùng ngày, thợ điện kéo dây công tơ. Mất điện một tiếng. Trẻ đang học bài đọc — Hạnh chuyển ra sân dưới bóng cây, viết chữ lên nền đất bằng que. Hùng đứng nhìn, không bảo vào lại phòng tối. Ông chỉ bảo ông Tư kiểm giếng và xô nước dự phòng nếu cúp dài.

— Điện về là lau chân trước khi lên gạch. — Hạnh dặn. — Không trượt.

Trẻ cười. Mùi đất ẩm sau mưa hôm trước. Hùng ghi sổ: «Cúp điện — lớp không vỡ.»

***

Sáng ngày thứ năm, Minh gọi đường dài từ Hà Nội. Tiếng xì. Anh báo lô bàn ghế phụ trễ hai ngày vì xe hỏng dọc đường. Hùng cau, rồi gật phía bên này dây:

— Lớp vẫn học. Thiếu bàn thì ghép tạm, không ghép trẻ ngồi đất. Có ghế là được.

Ông quay ra sân, cùng thợ kê lại bàn. Hạnh không than. Cô chỉ xin thêm phấn và giẻ lau. Lan đối phiếu tạm ứng với ông Tư: tiền tôn, tiền sơn, tiền công thợ. Một khoản «tiếp khách phường» ông Tư tự ý chi — Hùng gạch:

— Không hoàn. Không có trong dự toán. Lần sau hỏi trước.

Ông Tư đỏ mặt, nuốt, gật. Hùng không nâng giọng. Ông chỉ giữ sổ sạch.

Trưa, Hùng ăn cơm bụi đầu hẻm. Mùi nước dùng, mùi ớt. Ông ngồi ghế nhựa, nghe hàng xóm bàn «trường mới». Có người khen. Có người nghi «lấy đất công». Ông không cải. Ông lau miệng, trả tiền, về trường kiểm lại nhà vệ sinh mới — vòi nước yếu. Gọi thợ khoan giếng kiểm lại, không để phụ huynh mai mắng chuyện bẩn.

***

Chiều, một thanh niên mang theo em gái mười tuổi đến xin học. Em đã qua tuổi vào lớp theo quy định sở một chút. Hạnh giải thích lộ trình bổ túc. Hùng đứng cạnh, gật:

— Không nhét vào sĩ số chính để đẹp số. Xếp lớp bổ túc buổi chiều nếu đủ năm em.

Thanh niên siết tay em, thở:

— Có học là được. Không cần tên đẹp.

Lan ghi tên vào sổ riêng màu khác — tránh lẫn sĩ số chính. Hùng nhìn hai màu sổ, hài lòng hơn mọi biển hiệu.

***

Đêm trước ngày về, Hùng đi bộ một vòng hẻm. Tiếng radio nhà ai đó. Mùi cơm cháy nhẹ. Một ông già ngồi ghế mây hỏi:

— Trường tư hả?

— Trường công ty mở cho trẻ quanh đây. Có thủ tục. — Hùng đáp. — Không hứa đại học. Chỉ hứa biết chữ và tính.

Ông già gật, cười thiếu răng:

— Thế cũng được. Chữ đã hơn đói chữ.

Hùng về phòng trọ, rửa mặt nước lạnh, cảm giác mệt lắng xuống gáy. Ông viết thư ngắn gửi bà Hà: «Trường đã mở. Con về sớm. Nhờ mẹ giữ áo ấm.» Không viết dài. Không kể nắng. Gấp thư, siết mép phong bì, buông.

Sáng ra ga, Lan đi cùng đoạn đầu. Cô dặn Hạnh lần cuối về biên lai và khóa tủ phấn. Hạnh gật, mắt cười rồi nghiêm khi thấy phụ huynh đã đứng ngoài cổng sớm. Hùng nhìn cảnh đó từ cửa xe ôm, gật với chính mình: cửa đã mở — phần giữ cửa mới là việc dài.
"""

EXP76 = """
***

Ngày thứ ba của khóa, Hùng bất chợt kiểm tủ dụng cụ. Thiếu một thước cặp. Hải tập hợp tổ thực hành, mắt đỏ:

— Ai cầm ra ngoài xưởng?

Im. Một học viên nuốt, bước tới, tay run đưa thước:

— Em mang đo ở tổ tiện. Quên ký mượn.

— Ký muộn vẫn hơn giấu. — Hùng nói. — Giấu một lần, lần sau mất cả tay vì thiếu dụng cụ đúng.

Ông không đuổi học. Ông bắt em viết lại quy trình mượn trả, đọc trước lớp. Lâm liếc Hùng, gật — kỷ luật đủ để sợ, không đủ để hận.

Chiều, đại diện xưởng lân cận đến xin «gửi» thêm mười người ngoài danh sách, trả thêm tiền ngoài quỹ. Hùng lắc ngay:

— Không nhận tiền ngoài tiểu khoản. Không nhận người ngoài trần chỗ. Anh muốn gửi, chờ khóa sau, đúng cửa.

Người kia cau, rồi cười gượng:

— Nghe nói anh cứng.

— Cứng với chỗ làm ẩu. — Hùng đáp, tay nắm mép bàn rồi buông. — Mềm với người làm đủ bước.

***

Sáng hôm sau, bài cô lập nguồn được kiểm từng người. Hải đứng với đồng hồ. Minh đứng với bảng điểm. Hùng đứng góc, không nhắc bài. Một học viên làm thiếu bước khóa biển — bị dừng, làm lại. Người ấy thở hổn hển, mặt đỏ, siết kìm:

— Em nhớ rồi.

— Nhớ khi bình tĩnh mới tính. — Hải nói. — Lúc cuống là lúc đứt tay.

Hùng ghi biên bản nội bộ: «Tỷ lệ đạt lần một: ba mươi tám / năm mươi sáu.» Không giấu số thấp. Ông bảo Lâm treo số đó trong phòng giảng viên — không treo sân để làm nhục.

Trưa, cơm tập thể. Mùi canh bí. Hùng ngồi cùng học viên, nghe họ phàn nàn ca kíp. Ông không hứa giảm ca. Ông chỉ hứa lịch thực hành không đổi đột ngột nếu không có sự cố an toàn.

— Đổi lịch thì báo trước một ngày. — Ông nói. — Không báo miệng lúc tan ca.

***

Chiều, Lan gửi xe thư từ Hà Nội: xác nhận tiểu khoản, hóa đơn năm ê-tô, công văn nhắc hồ sơ an toàn lao động. Hùng đọc, gật, đưa Lâm bản sao. Một dòng Lan viết thêm bằng bút chì: «Mẹ hỏi con ăn có đều không.» Hùng cười mỏi, viết sau tờ giấy: «Ăn đều. Về sớm.»

Ông đi một vòng gian thực hành mới. Ế-tô thứ sáu vẫn chưa về. Minh gọi nhà cung cấp, giọng cứng. Hùng không xen. Ông chỉ ghi hạn: nếu mai chưa có, mượn tạm từ xưởng chính có biên bản — không «lấy tạm» không giấy.

***

Đêm trước về Hà Nội, Hùng ngồi với Minh dưới mái hiên xưởng. Tiếng dế. Mùi dầu loãng trong gió. Minh ngẩng:

— Anh có sợ mở rộng nhanh quá không?

— Sợ. — Hùng thở. — Nên mới bắt ký từng tay. Sợ mà vẫn làm thì phải có phanh.

Minh gật, siết cuốn sổ kỹ thuật. Hai người không nói thêm. Phía trước là ca sáng mai và một chuyến xe về — còn danh sách chờ một trăm mười bảy trừ đi năm mươi sáu, vẫn là bài toán chưa xong.

Trước lúc lên xe, Lâm đưa bản điểm danh đã sửa. Hùng ký xác nhận tuần một, mắt nhìn dòng «đạt cô lập nguồn», gật:

— Giữ nhịp này. Đừng đuổi số. Sáng mai tôi không ở đây — quy trình vẫn phải ở đây.
"""


def inject(path, block):
    t = open(path, encoding="utf-8").read()
    # Remove previous short expand markers if duplicate risk - just append before panel
    ip = t.find("\n「Hệ thống")
    if ip < 0:
        ip = t.find("「Hệ thống")
    pre = t.rfind("============================================================", 0, ip)
    if pre > 0 and ip - pre < 120:
        t = t[:pre].rstrip() + "\n\n" + block.strip() + "\n\n" + t[pre:]
    else:
        t = t[:ip].rstrip() + "\n\n" + block.strip() + "\n\n" + t[ip:]
    open(path, "w", encoding="utf-8").write(t)
    return t


for n, block in [(67, EXP67), (76, EXP76)]:
    fp = glob.glob(f"Chương {n} - *.txt")[0]
    t = inject(fp, block)
    rv = ss.score_chapter(t, 3000, 4200, True, cfg)
    print(
        f"Ch{n} final={rv['final']} w={rv['metrics']['words']} cd={rv['metrics']['char_density']:.2f} "
        f"hard={rv.get('hard_fails')} cau={rv['axes']['cau_truc']} nv={rv['axes']['nhan_vat']}"
    )
