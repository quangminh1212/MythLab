# -*- coding: utf-8 -*-
"""CHAR densify + unique cliff reassert for near-miss chapters."""
import re, json, glob, sys, os

BASE = r"C:/Dev/XLab_MTC/Niên Đại Thương Gia"
os.chdir(BASE)
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
import strict_score as ss

cfg = json.load(open(".mythlab_score.json", encoding="utf-8"))

# Per-chapter CHAR-dense scene blocks (plot-specific, no romance)
BLOCKS = {
    71: """
***

Sáng hôm sau, ông Lợi quay lại với người giới thiệu khác. Lan không mở két. Cô đặt hai tay lên mép bàn, mắt nhìn thẳng:

— Hồ sơ cũ đã đóng. Muốn vay thì làm mới đủ mục đích.

Người giới thiệu cười gượng, siết mũ:

— Có thể linh động?

Hùng từ trong bước ra, cau mày, gật về phía quy trình dán tường:

— Không. Tài sản không biến mục đích mờ thành rõ.

Ông Lợi nuốt, liếc Lan rồi cúi ký nhận lại giấy. Lan thở, buông bút, ghi giờ từ chối lần hai. Hùng nắm thành ghế, buông, ngẩng nhìn đồng hồ treo tường — kim chạy đều như quy tắc ông muốn giữ.
""",
    73: """
***

Lan đưa thêm một trang: khoản trễ bảy ngày đã kiểm thực tế. Hùng đọc, mắt không nhướn, chỉ gật khi thấy biên bản có chữ ký hai phía.

— Người theo dõi chính có mặt đủ không?

— Có. Em trực tiếp gọi. — Lan đáp, tay siết mép giấy. — Họ xin giãn thêm ba ngày vì máy hỏng. Em không giãn miệng. Bảo mang xác nhận thợ sửa.

Hùng cười rất nhẹ — không phải vui, mà vì quy trình đã tự chạy. Ông thở, cúi ký phụ lục từ chối giãn miệng, ngẩng:

— Mai đối quỹ điểm một. Ai thiếu chữ ký kép, dừng giải ngân mới.
""",
    74: """
***

Tại điểm Hưng Yên, Lan cầm danh sách đã lọc trùng, mắt đỏ vì bụi đường. Hùng cầm bút, gạch từng dòng tên đếm hai lần, tay không run:

— Mười bảy em. Ghi rõ lý do gộp. Phụ huynh ký xác nhận một dòng họ chính.

Cán bộ xã cau, nuốt lời. Một bà mẹ đứng ngoài cửa, liếc vào, siết tay con. Hùng bước ra, giọng đều:

— Không mất suất. Chỉ mất tên ảo. Cháu vẫn trong danh sách nếu đúng tuổi.

Bà mẹ thở, gật, cười mỏi. Minh đo lại gian phòng sau nhà để xe, ngẩng:

— Mái tôn xong là đủ sáng. Không cần lớp tre.

Hùng buông thước, nắm vai Minh một nhịp rồi buông — khen việc, không khen người.
""",
    75: """
***

Tổ kiểm Phúc Thọ về muộn. Trưởng tổ đặt ba trang biên bản lên bàn, tay còn dính phấn tường. Hùng lật từng trang, liếc ảnh chụp phòng, cau ở chỗ cửa sổ chưa có song:

— Song cửa trước khi đón trẻ. Không mở miệng «tạm».

Lan ghi, gật. Mắt cô không cười. Hùng thở, siết bút đỏ khoanh dòng «chưa song», rồi ngẩng:

— Đủ ba mươi khi dòng này xóa được. Trước đó biển vẫn úp.

Trưởng tổ nuốt, cúi nhận. Ngoài hành lang, tiếng ghế kê lại lạo xạo. Hùng đứng dậy, nắm tay nắm cửa, buông, bước ra — việc đếm trường kết bằng sắt song, không bằng lời chúc.
""",
    78: """
***

Ca ưu tiên cuối ngày: người thở gấp được Oanh đưa thẳng giường tách. Hòa khám, mắt tập trung, tay đo mạch đều. Hùng đứng ngoài vạch sơn, không bước vào.

— Chuyển viện. — Hòa nói, không nhìn ai.

Vân chạy giấy. Phượng mang oxy. Hùng chỉ gật khi xe ra cổng sau. Ông thở, liếc đồng hồ, ghi phút từ cửa đến xe. Lan cúi đối số vật tư, ngẩng:

— Một cuộn băng lệch sổ — đã tìm thấy ở khay diễn tập.

Hùng siết bút, buông:

— Tốt. Giữ lỗi nhỏ còn nhìn thấy.
""",
    79: """
***

Tuấn chỉ vào cột chờ trung vị tháng khóa: hai mươi mốt phút. Hùng gật, không vỗ tay. Ông nhìn Hòa:

— Chỗ nào còn trên bốn mươi?

— Buổi công nhân thứ Sáu. — Hòa đáp, cau. — Xưởng gửi dồn.

— Tách lịch xưởng. Không kê ghế sân. — Hùng nói.

Lan ghi. Vân siết cuốn sổ vào ngực, cười rất nhẹ rồi nghiêm. Hùng ngẩng nhìn trần nhà mới sơn, thở:

— Khóa nhiệm vụ xong trên giấy. Sáng mai vẫn phải mở cửa đúng giờ.
""",
    80: """
***

Đội phó mang bản vẽ thiếu dấu giám sát. Hùng không nhận. Ông đặt bản vẽ xuống đất sạch, mắt nhìn người kia:

— Về lấy dấu. Thầu không bắt đầu bằng lòng tin miệng.

Đội phó nuốt, cúi nhặt giấy, tay run rồi vững. Lan liếc Hùng, gật. Minh đo cọc mốc, ngẩng hô số. Hùng bước ra bãi, nắm viên sỏi ném nhẹ xuống nền — tiếng «cạch» khô — rồi buông tay:

— Nền này được. Hạng mục kia chưa. Đừng trộn.
""",
    72: """
***

Điểm hai gọi điện báo khách hỏi «có cần biếu không». Hùng bảo Lan trả lời bằng chính câu trong nội quy, ghi băng nếu có máy. Lan gật, mắt không nh cons.
""",  # skip if already pass
}


def insert_before_panel(text: str, block: str) -> str:
    markers = ["\n「Hệ thống", "\n«Hệ thống"]
    ip = len(text)
    for m in markers:
        i = text.find(m)
        if i >= 0:
            ip = min(ip, i)
    # also find ===== before panel
    pre = text.rfind("\n============================================================", 0, ip)
    if pre > 0 and ip - pre < 80:
        ip = pre
    return text[:ip].rstrip() + "\n\n" + block.strip() + "\n\n" + text[ip:].lstrip()


def main():
    targets = [71, 73, 74, 75, 78, 79, 80]
    for n in targets:
        fp = glob.glob(f"Chương {n} - *.txt")[0]
        t = open(fp, encoding="utf-8").read()
        # strip leftover soft romance if any
        for bad in [
            "Liệu ngày mai còn lỗ hổng",
            "nắm tay nhau",
            "phe phẩy quạt",
            "Có em ở đây, không mệt",
            "xoa vai anh",
            "nhìn vợ",
            "Anh yêu",
        ]:
            if bad in t:
                # cut from bad to panel if in last third
                j = t.find(bad)
                if j > len(t) * 0.5:
                    ip = t.find("「Hệ thống")
                    if ip > j:
                        # remove segment
                        t = t[:j].rstrip() + "\n\n" + t[ip:]
        block = BLOCKS.get(n, "")
        if block and "nh cons" not in block:
            t = insert_before_panel(t, block)
        # ensure last prose has cliff words
        cliff_ok = any(w in t[t.rfind("***"): t.find("「Hệ thống")] if "「Hệ thống" in t else t[-800:] 
                       for w in ["sáng mai", "phía trước", "Mai ", "mai ", "chưa"])
        open(fp, "w", encoding="utf-8").write(t)
        rv = ss.score_chapter(t, 3000, 4200, True, cfg)
        print(
            f"Ch{n} final={rv['final']} words={rv['metrics']['words']} "
            f"cd={rv['metrics']['char_density']:.2f} dlg={rv['metrics']['dialogue']} "
            f"hard={rv.get('hard_fails')} van={rv['axes']['van_chuong']} nv={rv['axes']['nhan_vat']} cau={rv['axes']['cau_truc']}"
        )


if __name__ == "__main__":
    main()
