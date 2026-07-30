# -*- coding: utf-8 -*-
import glob, json, sys, os
BASE = r"C:/Dev/XLab_MTC/Niên Đại Thương Gia"
os.chdir(BASE)
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
import strict_score as ss
cfg = json.load(open(".mythlab_score.json", encoding="utf-8"))

A67 = """
***

Trên toa tàu về Hà Nội, Hùng mở sổ lần nữa. Ông kẻ ba cột: việc đã chốt ở Bình An, việc Lan theo từ xa, việc ông phải thúc giấy phép. Tiếng bánh xe đều. Mùi than đầu máy len qua khe cửa. Một hành khách hỏi mượn lửa; Hùng lắc — không hút. Ông chỉ ngồi nhìn mưa bụi dọc đường sắt, tay siết gáy sổ rồi buông.

Tối đến ga Hà Nội, bà Hà không ra đón — Hùng dặn trước. Ông đạp xe về, mồ hôi lạnh ở sống lưng. Trong nhà mùi canh bí. Bà Hà nhìn con, gật:

— Ăn đi đã. Trường thế nào?

— Mở rồi mẹ. Có trẻ chân đất vào học. — Hùng rửa tay, nước lạnh làm ngón tay tê. — Mai con lên sở lo giấy.

— Giấy thì lo. Cửa đã mở thì đừng để trẻ đứng ngoài. — Bà múc cơm, mắt dịu.

Lan ghé tối muộn mang bản sao sổ thu chi Sài Gòn. Hai anh em đối nhanh dưới đèn. Không chuyện dài. Chỉ số và việc sáng mai. Hùng gật khi cột chi khớp. Ông ngẩng:

— Phía trước là giấy phép và tuần học thử còn ba ngày. Em giữ lương Hạnh đúng hạn.

— Em chuyển rồi. — Lan siết cặp, thở. — Anh ngủ. Mặt anh xanh.
"""

A76 = """
***

Xe về Hà Nội chạy giữa chiều muộn. Hùng gục gối vài phút rồi ngẩng viết tiếp: nhận ê-tô sáu, tỷ lệ đạt cô lập nguồn, danh sách chờ còn lại. Mùi bụi đỏ còn trong tóc. Minh ngồi cạnh ngủ gật, thước cặp trên đùi — Hùng khẽ lấy để khỏi rơi, đặt xuống sàn, không đánh thức.

Về tới văn phòng, Lan đã để sẵn ấm trà và bìa tiểu khoản. Hùng uống một ngụm, ấm lan nơi cổ họng, rồi ký xác nhận chi tuần. Bà Hà gọi điện hỏi ăn chưa — Lan bắt máy, cười nói «anh ấy đang ký». Hùng liếc, gật với máy như mẹ thấy được.

— Sáng mai họp ngắn với Lâm qua điện thoại. — Ông dặn. — Không để lịch thực hành trống khi tôi không có mặt.

— Em ghi lịch gọi. — Lan đáp, tay nắm bút. — Phía trước còn một trăm người chờ. Anh đừng hứa khóa mới trước khi khóa này qua kiểm tra an toàn.

Hùng thở, cười mỏi:

— Đúng. Phanh trước, ga sau.
"""

def inj(n, block):
    fp = glob.glob(f"Chương {n} - *.txt")[0]
    t = open(fp, encoding="utf-8").read()
    ip = t.find("「Hệ thống")
    pre = t.rfind("============================================================", 0, ip)
    if pre > 0 and ip - pre < 120:
        t = t[:pre].rstrip() + "\n\n" + block.strip() + "\n\n" + t[pre:]
    else:
        t = t[:ip].rstrip() + "\n\n" + block.strip() + "\n\n" + t[ip:]
    open(fp, "w", encoding="utf-8").write(t)
    rv = ss.score_chapter(t, 3000, 4200, True, cfg)
    print(f"Ch{n} final={rv['final']} w={rv['metrics']['words']} hard={rv.get('hard_fails')} cd={rv['metrics']['char_density']:.2f} cau={rv['axes']['cau_truc']}")

inj(67, A67)
inj(76, A76)
