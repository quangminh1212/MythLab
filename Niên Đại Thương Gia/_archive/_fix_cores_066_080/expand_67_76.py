# -*- coding: utf-8 -*-
"""Expand ch67 and ch76 with mid-chapter scenes before panel."""
import glob, json, sys, os

BASE = r"C:/Dev/MythLab/Niên Đại Thương Gia"
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

Đêm trước ngày về, Hùng đi bộ một vòng hẻm. Tiếng radio nhà ai đó. Mùi cơm cháy nhẹ. Một ông già ngồi ghế mây hỏi:

— Trường tư hả?

— Trường công ty mở cho trẻ quanh đây. Có thủ tục. — Hùng đáp. — Không hứa đại học. Chỉ hứa biết chữ và tính.

Ông già gật, cười thiếu răng:

— Thế cũng được. Chữ đã hơn đói chữ.

Hùng về phòng trọ, rửa mặt nước lạnh, cảm giác mệt lắng xuống gáy. Ông viết thư ngắn gửi bà Hà: «Trường đã mở. Con về sớm. Nhờ mẹ giữ áo ấm.» Không viết dài. Không kể nắng. Gấp thư, siết mép phong bì, buông.
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

Đêm trước về Hà Nội, Hùng ngồi với Minh dưới mái hiên xưởng. Tiếng dế. Mùi dầu loãng trong gió. Minh ngẩng:

— Anh có sợ mở rộng nhanh quá không?

— Sợ. — Hùng thở. — Nên mới bắt ký từng tay. Sợ mà vẫn làm thì phải có phanh.

Minh gật, siết cuốn sổ kỹ thuật. Hai người không nói thêm. Phía trước là ca sáng mai và một chuyến xe về — còn danh sách chờ một trăm mười bảy trừ đi năm mươi sáu, vẫn là bài toán chưa xong.
"""


def inject(path, block):
    t = open(path, encoding="utf-8").read()
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
        f"hard={rv.get('hard_fails')} cau={rv['axes']['cau_truc']}"
    )
