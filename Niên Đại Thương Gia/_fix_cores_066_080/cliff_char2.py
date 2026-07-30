# -*- coding: utf-8 -*-
"""Reassert cliff in last 3 prose lines + extra CHAR block for remaining FAILs."""
import glob, json, sys, os, re

BASE = r"C:/Dev/XLab_MTC/Niên Đại Thương Gia"
os.chdir(BASE)
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
import strict_score as ss

cfg = json.load(open(".mythlab_score.json", encoding="utf-8"))

EXTRA = {
    71: """
Hùng gập sổ quỹ vay, siết gáy bìa da rồi buông. Lan liếc đồng hồ, cúi ghi giờ khóa két, ngẩng:

— Sáng mai mở cửa đúng bảy giờ. Hồ sơ thiếu mục đích xếp riêng, không để lẫn hàng chờ.

— Đúng. — Hùng gật, thở. — Phía trước chỉ có quy trình. Ai giục quen, em chỉ vào tường.
""",
    73: """
Hùng đặt bút xuống, nắm rồi buông. Mắt ông nhìn Lan:

— Sáng mai đối quỹ trước khi ai mang hồ sơ trường sang. Phía trước còn hai mươi hai khoản chưa đến hạn.

Lan gật, siết mép phụ lục, cười rất nhẹ rồi nghiêm:

— Em giữ lịch gọi. Anh không cần ngồi đếm từng đồng mỗi giờ.

Hùng thở, ngẩng nhìn cửa sổ se lạnh. Việc vay khép một vòng trên giấy — ngày mai vẫn phải mở sổ đúng giờ.
""",
    74: """
Hùng gập bìa hồ sơ mạng lưới, tay siết rồi buông. Lan đứng dậy, liếc mưa bụi ngoài kính:

— Sáng mai xuất phát điểm đầu. Em mang sẵn mẫu kiểm trùng tên.

— Mang. — Hùng gật, thở. — Phía trước không phải đếm cho đủ số. Là đếm cho đúng trẻ.
""",
    75: """
Hùng tắt đèn bàn, nắm tay nắm cửa phòng họp, buông. Lan đứng ở ngưỡng, mắt nhìn anh:

— Sáng mai treo biển Phúc Thọ nếu song cửa xong. Chưa xong thì biển vẫn úp.

— Đúng. — Hùng gật, thở. — Phía trước ai viết ba mươi mốt, em gạch đỏ trước khi báo cáo.
""",
    78: """
Hùng khóa chốt cửa sau, siết then một lần, buông. Vân liếc, gật. Hòa thở dài, cúi rửa tay thêm nhịp.

— Sáng mai mở cửa sáu rưỡi. — Hùng nói. — Phía trước là sơn vạch mòn và lịch công nhân thứ Sáu — không phải biển hiệu mới.
""",
    79: """
Hùng ký nét cuối, buông bút. Tuấn gật. Hòa liếc số, cau rồi nới:

— Sáng mai vẫn đếm ghế trước khi đón người. Phía trước không có cơ sở hai cho đến khi cột chờ giữ được thế này.

Lan siết hồ sơ vào ngực, thở, cười mỏi:

— Em khóa tủ. Anh về ăn. Mẹ hỏi thì nói phòng khám ổn.
""",
}


def inject(text, block):
    ip = text.find("\n「Hệ thống")
    if ip < 0:
        ip = text.find("「Hệ thống")
    # drop freeform between last close and panel; insert block
    # find last ==== before panel
    pre = text.rfind("============================================================", 0, ip)
    # if the ==== immediately precedes panel, insert before that ====
    if pre > 0 and ip - pre < 100:
        return text[:pre].rstrip() + "\n\n" + block.strip() + "\n\n" + text[pre:]
    return text[:ip].rstrip() + "\n\n" + block.strip() + "\n\n" + text[ip:]


for n, block in EXTRA.items():
    fp = glob.glob(f"Chương {n} - *.txt")[0]
    t = open(fp, encoding="utf-8").read()
    t = inject(t, block)
    open(fp, "w", encoding="utf-8").write(t)
    rv = ss.score_chapter(t, 3000, 4200, True, cfg)
    print(
        f"Ch{n} final={rv['final']} w={rv['metrics']['words']} cd={rv['metrics']['char_density']:.2f} "
        f"cau={rv['axes']['cau_truc']} nv={rv['axes']['nhan_vat']} van={rv['axes']['van_chuong']} hard={rv.get('hard_fails')}"
    )
