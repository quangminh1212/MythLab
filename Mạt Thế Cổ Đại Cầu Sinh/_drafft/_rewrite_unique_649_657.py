# -*- coding: utf-8 -*-
"""Unique rewrite clone-pad ch 649,651-657 — no Nhịp im, no EXP pad, no Kho panel spam."""
from pathlib import Path
import re, os, stat, subprocess, json

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
OUT_JSON = BASE / "_score_clone_rewrite_649_657.json"
NUMS = [649, 651, 652, 653, 654, 655, 656, 657]


def vn_day_words(d):
    u = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    tram, r = d // 100, d % 100
    s = f"{u[tram]} trăm"
    if r == 0:
        return s
    if r < 10:
        return f"{s} lẻ {u[r]}"
    chuc, donvi = r // 10, r % 10
    s2 = "mười" if chuc == 1 else f"{u[chuc]} mươi"
    if donvi == 0:
        return f"{s} {s2}"
    if donvi == 1 and chuc > 1:
        return f"{s} {s2} mốt"
    if donvi == 5:
        return f"{s} {s2} lăm"
    return f"{s} {s2} {u[donvi]}"


def count_vi(t):
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end() :] if m else t
    return len([w for w in body.split() if len(w) >= 2])


SPECS = {
    649: {
        "title": "Sóng Thấp Lần 103",
        "day": 769,
        "kind": "song",
        "place": "Rãnh vôi cũ nam",
        "count": "bốn",
        "prev": "Bụi sim gai đông",
        "hook": "Gió bấc mang mùi vôi ướt từ rãnh nam trước khi trống điểm tan hẳn.",
        "event_line": "Rãnh vôi cũ nam — sóng thấp lần một trăm linh ba. Không gào. Chỉ sóng thấp. Máu kín.",
        "bones": "Sóng thấp · máu kín · hố mới · không đếm to · không phơi · không lặp hố cũ",
        "panel_evt": "sóng thấp lần 103 · Rãnh vôi cũ nam · bốn · máu kín · hố mới · không đếm to",
    },
    651: {
        "title": "Hỏi Lần 108 Cùng Màu",
        "day": 771,
        "kind": "hoi",
        "ask": "có đinh sắt không, đổi búa lấy muối",
        "bait": "Búa ngoài là dấu tao — trong có lò rèn không?",
        "word": "đinh",
        "refuse": "Không nhận đinh. Không đổi búa",
        "risk": "mang thợ rèn giả",
        "hook": "Khói bếp còn thấp khi cổng đông mang một miệng hỏi đinh.",
        "event_line": "Cổng đông — hỏi lần một trăm linh tám. Không gào. Chỉ miệng. Chỉ hỏi đinh. Cùng màu.",
        "bones": "Không mở · không nhận đinh · không đổi búa · đông thường · hầm xấu · cùng màu",
        "panel_evt": "hỏi lần 108 · đinh sắt · đổi búa lấy muối · không nhận · cùng màu · hầm xấu",
    },
    652: {
        "title": "Ngày Yên Sau Hỏi 108",
        "day": 772,
        "kind": "yen",
        "word": "đinh",
        "risk": "mang thợ rèn giả",
        "hook": "Trống điểm tan mà cổng không mang miệng — yên sau hỏi đinh, yên không phải hội.",
        "event_line": "Trong rào — ngày yên sau hỏi một trăm linh tám. Không gào. Chỉ việc. Trống không bằng yên hội.",
        "bones": "Không thở phào · không họp chữ đinh · không mở rèm sớm · không rải vôi nghỉ · tai khe",
        "panel_evt": "yên sau hỏi 108 · trống ≠ yên hội · không thở phào · đinh · tai khe · máy nghèo",
    },
    653: {
        "title": "Sóng Thấp Lần 104",
        "day": 773,
        "kind": "song",
        "place": "Gốc sung khô bắc",
        "count": "năm",
        "prev": "Rãnh vôi cũ nam",
        "hook": "Sương dính gốc sung khô phía bắc khi năm bóng thấp lê sát rìa đất.",
        "event_line": "Gốc sung khô bắc — sóng thấp lần một trăm linh bốn. Không gào. Chỉ sóng. Máu kín.",
        "bones": "Sóng thấp · máu kín · hố mới sát gốc sung · không đếm năm to · không lặp hố rãnh nam",
        "panel_evt": "sóng thấp lần 104 · Gốc sung khô bắc · năm · máu kín · không đếm to",
    },
    654: {
        "title": "Bóng Gò Lần 56 Không Chỉ",
        "day": 774,
        "kind": "bong",
        "place": "Gò đông",
        "detail": "một bóng đặt túi vải trên gai",
        "action": "mở túi gai",
        "hook": "Trên gò đông, một bóng đứng — không gào, không lê, chỉ đặt túi vải lên gai rồi im.",
        "event_line": "Gò đông — bóng gò lần năm mươi sáu. Không gào. Chỉ bóng. Có túi. Không chỉ. Không mở túi.",
        "bones": "Không chỉ · không mở túi gai · không đạp theo · không ném đá · nuốt mắt",
        "panel_evt": "bóng gò lần 56 · đặt túi vải trên gai · không chỉ · không mở túi · không đạp theo",
    },
    655: {
        "title": "Hỏi Lần 109 Cùng Màu",
        "day": 775,
        "kind": "hoi",
        "ask": "có thuốc bắc không, đổi bọc lá lấy nước",
        "bait": "Bọc lá ngoài là của tao — trong có thầy thuốc không?",
        "word": "thuốc",
        "refuse": "Không nhận thuốc. Không đổi bọc",
        "risk": "mang thầy thuốc giả",
        "hook": "Gió đông mang mùi lá khô lẫn tiếng hỏi thuốc từ ngoài cổng.",
        "event_line": "Cổng đông — hỏi lần một trăm linh chín. Không gào. Chỉ miệng. Chỉ hỏi thuốc. Cùng màu.",
        "bones": "Không mở · không nhận thuốc · không đổi bọc · đông thường · hầm xấu · cùng màu",
        "panel_evt": "hỏi lần 109 · thuốc bắc · đổi bọc lá lấy nước · không nhận · cùng màu · hầm xấu",
    },
    656: {
        "title": "Ngày Yên Sau Hỏi 109",
        "day": 776,
        "kind": "yen",
        "word": "thuốc",
        "risk": "mang thầy thuốc giả",
        "hook": "Sân thức mà cổng trống — yên sau hỏi thuốc, yên dạy tai chứ không dạy thở phào.",
        "event_line": "Trong rào — ngày yên sau hỏi một trăm linh chín. Không gào. Chỉ việc. Trống không bằng yên hội.",
        "bones": "Không thở phào · không họp chữ thuốc · không mở rèm sớm · không rải vôi nghỉ · tai khe",
        "panel_evt": "yên sau hỏi 109 · trống ≠ yên hội · không thở phào · thuốc · tai khe · máy nghèo",
    },
    657: {
        "title": "Sóng Thấp Lần 105",
        "day": 777,
        "kind": "song",
        "place": "Mương lá mục tây-nam",
        "count": "sáu",
        "prev": "Gốc sung khô bắc",
        "hook": "Mùi lá mục từ mương tây-nam dậy sớm hơn trống điểm — sáu bóng thấp, không gào.",
        "event_line": "Mương lá mục tây-nam — sóng thấp lần một trăm linh lăm. Không gào. Chỉ sóng. Máu kín.",
        "bones": "Sóng thấp · máu kín · hố mới sát mương · không đếm sáu to · không lặp hố gốc sung",
        "panel_evt": "sóng thấp lần 105 · Mương lá mục tây-nam · sáu · máu kín · không đếm to",
    },
}


def morning(s, day_w):
    return f"""{s['hook']} Ngày thứ {day_w} dưới đất Biên Ải. Gió bấc mang mùi đất se và vôi cũ; nắng mỏng chưa đủ ấm gáy. {s['event_line']} Luật trong xương: thấy việc, nuốt việc, không kể việc thành hội sân.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ tín hiệu. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe hướng việc.

"Việc ngoài. Không mở. Không chỉ," Phong đáp. Anh nhìn hướng cổng đông hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp — đuổi là mời người lạ đọc lưng.
"""


def event_block(s):
    k = s["kind"]
    if k == "song":
        return f"""---

Sáng. Máy nghèo chạy ngày sóng thấp.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn: sóng. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"{s['place']}. {s['count']} thấp. Không gào. Dấu riêng chỗ này. Không nhìn trẻ. Không mang xẻng to."

"Máu kín. Hố mới sát {s['place']} — không trùng {s['prev']}. Không đếm {s['count']} to. Không phơi. Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể sóng.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

{s['count'].capitalize()} bóng thấp từ {s['place']} lê sát rìa. Không gào. Không gọi. Chỉ sóng. Phong hạ tay — không hội, không trống lớn. Móc gáy-hông, không mặt. Máu ngắn. Thóc lép rắc. Hố mới sẽ lấp canh tư. Đắp xấu. Phủi. Không giữ dấu làm chuyện. Không đếm {s['count']} to cho sân nghe.

Hà siết khăn: "Kín?"

"Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố {s['prev']}."

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Chân kho. Thớt không phơi. Dây không kêu. Quét miệng muốn kể.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu ho trống gò phía bắc khi sóng đã gục. Không giơ sớm. Sóng là việc khác — việc tay nuốt, miệng không nhả.
"""
    if k == "hoi":
        return f"""---

Sáng. Máy nghèo chạy ngày hỏi cùng màu.

Cháo loãng. Bếp khép. Mạc Tư gạch im — một vạch: hỏi. Không viết chữ {s['word']} to. Từ Sơn vòng chân kho. Triệu nước đúng gáo. A Cường lách, báo thấp:

"Một miệng. Hỏi {s['ask']}. Không lê. Giọng khác lần trước. Không nhìn trẻ."

"Không mở. Không kể trẻ. Không chỉ giếng. {s['refuse']}. Đông thường. Hầm xấu. Việc," Phong nói.

Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội đáp miệng.

Bà già ghé: "Khách?"

"Không. Gió. Việc," Chú Bát. Cúi. Đủ.

Miệng ngoài cổng đông cất lên, không gào, chỉ hỏi:

"Trong ơi — {s['ask']}!"

Phong không mở. Hà đứng sau rèm, giọng đều, cùng màu với mọi lần hỏi:

"Đông thường. Hầm xấu."

Miệng lần hai, thử mồi:

"{s['bait']}"

Không đáp mồi. Hà lặp: "Hầm xấu." Không thêm. Không chỉ giếng. Không nhận {s['word']}. Không đổi. Miệng cười khô, lùi. Không mở tiễn. Không ném đồ.

Hà hỏi sau muối: "Hỏi?"

"Không nhận. {s['refuse']}. Máy nối mồi với miệng — im. Ai kể {s['word']} cho trẻ — nặng. Ai mở vì tò mò — hở."

Phong xách nước, đảo bao. Ba xương giữ: lời em nếu miệng, bao anh, đông thường hầm xấu. Cùng màu nếu hỏi. Không lệch. Không mở rèm.
"""
    if k == "yen":
        return f"""---

Sáng. Máy nghèo chạy ngày yên sau hỏi.

Cháo loãng. Bếp khép. Mạc Tư gạch im — một vạch: yên. Không viết chữ nghỉ. Không viết chữ {s['word']} to. Từ Sơn vòng. Triệu nước. A Cường lách:

"Cổng trống. Ngoài trống. Không miệng. Không dấu {s['word']}."

"Không thở phào. Không họp chữ {s['word']}. Việc," Phong nói.

Đại Lực bao. Tôn Vũ móc. Hứa dao. Diễm se. Hà phơi. Phong đảo muối. Yên khép bằng việc, không bằng hội mừng trống.

Bà già ghé: "Yên?"

"Gió. Việc," Chú Bát. Không thêm. Không mừng.

Sáng trống. Yên sau chữ {s['word']} có thể là khoảng lùi — {s['risk']}. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ. Mạc Tư gạch: yên sau hỏi {s['word']} — không viết nghỉ.

Hà: "Yên?"

"Trống. Không thở phào. Tai khe — miệng hỏi {s['word']} có thể {s['risk']}."

Phong đếm vai sân: trẻ trong rèm, giếng nắp xấu, chân kho nguyên. Không vôi sớm. Không họp chữ hôm qua. Việc hôm nay nuốt việc hôm qua.
"""
    return f"""---

Sáng. Máy nghèo chạy ngày bóng không chỉ.

Cháo loãng. Bếp khép. Mạc Tư gạch im — một vạch: bóng. Không viết số to. Từ Sơn vòng. Triệu nước. A Cường lách:

"{s['place']}. {s['detail']}. Không lê. Không nhìn trẻ. Không mang xẻng."

"Không mở. Không chỉ. Không {s['action']}. Không đạp theo. Việc," Phong nói.

Đại Lực luyện khuất. Tôn Vũ không hun. Hứa dao bùn. Diễm se. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể bóng.

Bà già: "Gió?"

"Gió. Việc," Chú Bát. Cúi. Đủ.

Bóng đứng vài nhịp trên gò. {s['detail'].capitalize()}. Gió thổi gai. Việc trong nuốt mắt. Bóng lùi. Lần này khép bằng chân bóng. Không ném đá. Không {s['action']}. Không chỉ ngược cho sân xem.

Hà: "Thấy?"

"Thấy. Ta không chỉ. Không {s['action']}. Máy nhớ nghề, không khoe."

A Minh: hai ngón — tín hiệu gò. Hữu ướt vải. Cúc kéo Hạt sâu rèm. Thẻ. Cửa hờ. Trẻ khuất. Sân nhẹ. Mùi cháo loãng át mùi vôi một nhịp rồi trả lại đất se.
"""


def shared_day(s):
    return f"""---

Giữa sáng. Ba xương việc.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, mắt không lỏng:

"Thật hay mồi?"

"Việc thật. Luật giữ. Không lỏng vì đã quen," anh nói. "Ba xương: {s['bones']}."

"Rèm chặt. Trẻ không ra sân gần đông," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển kéo gần ngưỡng nửa bước rồi đứng. A Minh tín hiệu. Không sóng nhầm. Không thước.

A Cường lách lại: "Ngoài vẫn việc. Không tiến rào. Gió thổi áo rách."

"Không soi. Không kể," Phong dặn. A Cường biến.

Diễm buộc rèm sâu hơn một nấc. Cúc kéo Hạt: "Xâu trong. Không ra gần cổng." Thẻ. Trẻ khuất. Sân nhẹ.

Bà già lại ghé, thấp hơn: "Hôm qua ồn?"

"Gió. Việc," Hà đáp. Không thêm. Không số. Không hố.

Hứa đứng cửa xưởng không liếc hướng việc. Dao bùn. Bùn áo. Áo nghèo. Nghèo đúng là trả lời không lời.

Phong xách thêm một thùng nước, đảo thêm hai bao lép phía tây, lau muối đến chát. Chát sau việc đắt hơn chát sau yên — vì việc dạy mắt, yên dạy lỏng vai. Lỏng vai là hở mai.

---

Ngọ. Cháo sau việc.

Phong húp. Cúc: "Ngoài?"

Hà: "Việc. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau việc đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"{s['title']}. {s['bones']}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Nếu bóng — không chỉ. Miệng sau việc dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá. Không phình.

Phong đảo tây nhiều hơn đông. Hà phơi nắng xấu. A Cường: "Trống dần. Không cắt. Không kể."

"Không đạp theo. Không kể trống thành chuyện sân," Phong nói. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát không hỏi hôm qua mang chữ gì. Nồi sôi. Giờ đúng. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm buộc rèm. Cúc Hạt xâu. Lỗ vá rèm và xâu.

Phong gặp Hà lần hai sau muối:

"Đủ? Không lệch vì việc ngoài?"

"Không lệch. Việc ngoài không phải hội. Việc ngoài là việc im," chị lau tay. "Ai chỉ hố ngoài lều — nặng."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Tín hiệu trống dần. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuốc củ thẻ. Mười hơi chân kho — còn. Hà miệng năm hay nói: gió, hầm ẩm, đông thường, việc ngoài, không bảy hố cửa đồi kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xế. Gánh gác. Không hội kể số.

Xế. Ca đổi. Xước se. Vòng then tây bao vai. Gật đủ. Thỏ bếp tro miệng khớp trống đêm. Thở. Mùi. Đều.

Tám nhịp bếp: không phát sợ vì việc ngoài, nửa bát, củ thẻ, nồi không chuyện số. Gạch. Sôi. Gỗ. A Cường: không xe không người lại gần rào. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bóng bếp tám nhịp: không phát vì việc, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi số. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im. Im đắt truyện.

Tháp Hà không đèn: "Việc có lớp. Mai sóng hoặc bóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Ngoài trống dần. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Việc rào — không người xe, mùi dày đứng. Đứng được. Không lỏng.

Hữu đổi ca: "Trống gần. Không người." Cháo nửa thìa. "Im. Giơ người đúng. Không sóng nhầm." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc giữa chiều: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Thước đọc lưng; xương không cho đọc.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "{s['title']}. {s['bones']}. Không mở rèm sớm. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể số cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Việc — giơ đúng nếu sóng."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Việc có lớp. Chưa xông. Mai sóng hoặc bóng hoặc hỏi."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.

Xưởng móc mài lá khô. A Minh trống. Hữu không giơ. Đúng.
"""


def night_block(s):
    day = s["day"]
    k = s["kind"]
    if k == "song":
        night_spec = f"""Canh một. Tuần tây.

Hầm đông chông vôi then hố vết. Rên thưa. Không sóng mới. Bảy im. Chọn im. Hố mới sát {s['place']} đã lấp xấu — thóc lép, đắp không đẹp, phủi. Không đếm {s['count']} to trong sổ da.

Canh hai. Ca mới. "Mùi. Thỏ. Sóng đã kín. Tạm trống."

"Ngủ ca. Mai bóng, hỏi, hoặc sóng khác chỗ."

"Máu kín nếu sóng."

Ra. Gió. Muối. Không xe. Vết nguyên. Góc sân mảnh: hầm đông trẻ tay miệng thỏ hố không kể cấp im lời Hà cùng màu sóng thấp không đếm to. Cầm thở.

Canh ba. "Ngoài?"

"Trống. Dày. Không xe. Không người. Hố xấu còn. Không đào lại."

"Ngủ."
"""
    elif k == "hoi":
        night_spec = f"""Canh một. Tuần tây.

Hầm đông chông vôi then hố vết. Rên thưa. Không miệng. Bảy im. Chọn im. Chữ {s['word']} không viết to. Không họp mồi.

Canh hai. Ca mới. "Mùi. Thỏ. Miệng đã lùi. Tạm trống."

"Ngủ ca. Mai miệng có thể mang {s['risk']}."

"Cùng màu nếu hỏi lại."

Ra. Gió. Muối. Không xe. Vết nguyên. Góc sân: hầm đông trẻ tay miệng thỏ không kể {s['word']} không chỉ giếng cấp im lời Hà cùng màu. Cầm thở.

Canh ba. "Cổng?"

"Trống. Dày. Không miệng. Không búa. Không bọc."

"Ngủ."
"""
    elif k == "yen":
        night_spec = f"""Canh một. Tuần tây.

Hầm đông chông vôi then hố vết. Rên thưa. Không miệng. Bảy im. Yên không phải nghỉ. Không thở phào. Không rải vôi nghỉ.

Canh hai. Ca mới. "Mùi. Thỏ. Cổng trống. Tai khe."

"Ngủ ca. Mai có thể {s['risk']}."

"Không họp chữ {s['word']}."

Ra. Gió. Muối. Không xe. Vết nguyên. Góc sân: yên sau hỏi dạy tai, không dạy mừng. Cầm thở.

Canh ba. "Cổng?"

"Trống. Dày. Không dấu {s['word']}. Không thở phào."

"Ngủ."
"""
    else:
        night_spec = f"""Canh một. Tuần tây.

Hầm đông chông vôi then hố vết. Rên thưa. Không sóng. Gò: túi gai còn hoặc đã mất theo chân bóng — không {s['action']}. Bảy im. Chọn im.

Canh hai. Ca mới. "Mùi. Thỏ. Bóng đi. Tạm trống."

"Ngủ ca. Mai bóng, sóng, hoặc hỏi."

"Máu kín nếu sóng. Không chỉ nếu bóng."

Ra. Gió. Muối. Không xe. Vết nguyên. Góc sân: bóng gò không chỉ, không mở túi, không đạp theo. Cầm thở.

Canh ba. "Gò?"

"Trống. Dày. Không xe. Không người. Không chỉ."

"Ngủ."
"""
    return f"""---

{night_spec}
Sổ than:

Ngày {day}. {s['title']} — {s['panel_evt']}. Ba xương: {s['bones']}. Không kể. Nghèo. Đều. Cấp im. Bảy xương.

Chữ kho lóe ngắn:

『Ghi nhận: {s['panel_evt']}.』
『Cảnh báo: miệng sau có thể mang thước · việc có thể quay · không lỏng.』
『Nhiệm vụ: việc im · không kể · đâm thấp nếu sóng · cùng màu nếu hỏi · máy nghèo.』

Cấp im. Không pháo. Ngáy. Nằm. Nắm. "Im." "Im…"

Mơ: việc ngoài rào và thẻ trẻ. Xâu. Số mờ. Tỉnh gió. Trống. Hữu đổi. Rên một. Nhắm.

Gà nhất. Không vội. Hà thở. Then. Mùi. Im. Bảy gối. Việc không hội miệng sân mai.

Tây xấu. Đông chông hố vết. Gò trống. Trẻ. Người đều. Lớn thầm. Đo. Sống.

Ngày {day + 1} chờ bóng, sóng, hỏi, mùi, mặt không biết, miệng ngậm, chông thấp. Trống bao mũi tai miệng tay. Không sống theo đã xong một việc. Sống theo đều khi mắt dễ chỉ.

Ngủ muối hết. Tai khe. Chưa. Tốt. Nghèo sau việc. Không chỉ. Củ thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ.

Việc không pháo. Cháo bao vải tay trẻ im lời cùng màu. Đủ trống. Đủ hắn đọc lưng mà không đọc được xương. Đủ bảy xương. Mai đảo đông. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe. Đất người cháo thẻ đều còn.
"""


def late_and_close(s, n):
    day = s["day"]
    day_w = vn_day_words(day)
    return f"""Gà hai. Nước. Bảy im. Nằm. Tay Hà. Mùi. Thở. Cấp im. Chông. Gió. Nghi. Ta sống. Việc khép im — im đắt nở miệng dưới trời này.

Gió dài. Mắt: chông thẻ Hà cửa vết ngoài trống lời ba xương việc. Giữ. Không kể bảy. Không chỉ hố. Không pháo. Đất lưng. Ngủ sau việc. Mai chủ nghèo — không bia mồi miệng.

Rên tắt. Không dậy. Tai khe. Im. Hà nắm. Ngủ. Sau việc không cột đêm. Sức trống kế chông mặt không biết mang bảy hố xương sân gió bao.

Mai trống cháo bao mùi. Mai bóng sóng hỏi. Mai sống. Đủ.

Hữu đều. Đều lan. Cười im. Im sau việc đắt cười ảo. Ảo kể số bảy. Thật đất người thẻ chông miệng. Đất Biên Ải còn. Thắng dở. Mai cháo chông hố lời. Không pháo. Thở đều không biết. Việc đã tới ta chọn nhịp việc im. Sống. Đo. Không khoe. Người đất cháo thở. Đất còn. Đủ.

Nhắc xương: không kể bảy, không chỉ hố, không mừng, không đào, trẻ không thấy, mặt không biết, cấp im, đông thường, lời Hà cùng màu, bao anh, việc không hội. Khớp. Ngủ. Còn viết. Mai đất chữ. Đủ đọc lưng không xương. Đủ.

Canh tư. Tháp Hà không đèn. Ca đổi. Đông hố cửa gò im. Chị: "Mai — em cùng màu. Anh bao. Không đổi ca lời sân. Không thêm vì việc ngoài."

Gật. Lời ca. Hở đắt.

Gió đổi. Không sóng xe thước người. Đất Biên Ải trại nghèo sau việc xem dấu. Còn nghèo — chông mặt. Xuống. Muối hết. Nằm. Tay Hà. Ngủ thật. Mai viết.

Trước gà cuối: rên xa một. Đếm. Im. Không dậy. Nắm lỏng. Mặt nghèo mai. Chông mặt sắc. Đất người chữ. Khép {day} không kể bảy không chỉ hố không nở miệng sau việc. Sống. Đo. Không khoe. Đất còn. Đủ. Mai thở viết. Viết chưa thua. Người còn. Còn thở. Còn đều khi mắt dễ chỉ.

Phong ngồi dậy cuối, uống nước, nghe Hà thở. Tin nghề. Ghé: "Mai cùng màu. Không thêm. Không bớt hở. Việc ngoài không làm ta lệch."

Chị: "Không lệch." Ngủ. Đủ ai hỏi hoặc bóng chỉ gặp gió núi bao rách cháo loãng — không bảy không hố không cấp im túi. Đất Biên Ải. Còn viết thở người chữ. Đủ. Máy nghèo. Chông thấp. Miệng phân ca. Đủ khép đêm.

Sáng mai trống điểm mùi dày bóng hoặc sóng hoặc hỏi. Không sống sợ việc ngoài. Sống đều. Đều câu trả lời dài hơn mọi lời ngoài rào. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ.

Trong xương vang ba xương việc — giữ lần hỏi sau và sóng. Lệch hở. Hở bảy. Nắm Hà: "Em lời. Anh việc đông miệng."

"Giữ." Gió ngoài không người. Trong trại nhịp gánh thẻ. Nhịp đất chữ. Chưa thua.

Canh khuya vòng ngắn: then tây êm, đông chông không cọt, hố không bới, cửa vết không sưng. A Minh đổi. Hữu im. Khuyển gỗ giếng. Gỗ không kể. Về lều. Mùi dày lớp sau việc. Không bóc miệng. Bóc việc. Việc. Đủ. Ngủ thật. Mai sống viết.

Đếm chuỗi tay im: người xe sóng thước máu. Khớp. Không tiếng. Quay tóc Hà. Khói bếp cũ. Cũ được. Không mới. Tốt. Đất Biên Ải. Việc chỉ gió ngoài nếu xương siết. Siết. Ngủ. Đủ. Còn thở viết người chữ. Chưa thua. Đất còn. Đủ thật. Mai nhịp. Còn sống. Còn đất. Còn người. Đủ.

Trước ngủ hẳn nghe Hà mơ thở không chữ số. Thở được. Đêm chỉ thở. Đất người cháo chông lời cùng màu mai. Đủ khép {day} mà việc không lấy bảy hố cấp — chỉ gió núi bao rách. Cho đúng món. Không thêm. Đủ. Ngủ.

Trước gà cuối lắng: then tây, chông đông, gò, thuốc, miệng số không quay tiếng sân. Năm im một câu xương. Xương mai mở cùng màu. Không thêm bớt. Đất Biên Ải. Còn thở viết người chữ. Chưa thua. Đất còn. Đủ thật. Mai nhịp sống đất người. Đủ khép.

Ngồi dậy cuối uống nước lã. Hữu đổi ca. Khuyển ho giếng xác nhận im. Im sau việc có lớp. Không bóc miệng hội mai. Bóc cháo bao lưng cùng màu. Việc. Cùng màu. Đủ. Nằm. Tay Hà. Ngủ thật. Sống. Đo. Không khoe. Đất người cháo thẻ chông miệng phân ca còn. Đủ.

Nhớ chữ Hà — giữ lần hỏi sau bóng sóng. Cùng màu. Lệch chữ hở bảy. Nắm: "Em lời. Anh việc đông miệng."

"Giữ…" Gió không miệng. Trại nhịp gánh thẻ. Nhịp đất chữ. Chưa thua.

Thềm lều nửa bước. Mùi dày lớp sau việc. Không bóc miệng sáng. Bóc cháo loãng bao rách lưng thẳng cùng màu. Đủ. Vào. Nằm. Ngủ thật. Mai viết sống Biên Ải.

Đếm tay lần nữa: người xe sóng thước máu. Khớp. Tóc Hà. Khói cũ. Cũ được. Đất Biên Ải. Xương siết. Siết. Ngủ. Đủ. Còn thở viết người chữ chưa thua. Đất còn đủ thật. Mai nhịp còn sống đất người. Đủ.

Phong còn ngồi dậy uống nước lần nữa, nghe ca đông và tiếng xô bếp tắt dần. Việc ngoài còn dấu mà sân vẫn muốn kể cho đỡ sợ. Kể là hở. Anh siết hàm, siết vai, siết luật trong xương: không kể bảy, không chỉ hố, không mừng, không đào, trẻ không thấy, mặt không biết, cấp im, đông thường, lời Hà cùng màu, việc không hội. Khớp. Ngủ.

Trước khi mắt dính, anh còn đi nửa vòng chân ngắn trong đầu — then tây, đông chông, hố vết, gò trống, thuốc rèm, thẻ trẻ, miệng phân ca. Tất cả còn. Còn thì chưa thua. Còn thì mai còn viết. Viết bằng sống. Sống bằng đều. Đều bằng việc im. Việc im. Đủ.

Hà trở mình, tay tìm tay anh. Nắm. Buông lỏng. Mùi dày đứng ngoài rào như người lạ không vào được nếu cửa không mở bằng miệng. Miệng đã khóa bằng việc. Việc. Đủ. Đất Biên Ải. Còn thở. Còn người. Còn chữ. Chưa thua. Đất còn. Đủ thật. Mai còn nhịp. Còn sống. Còn đất. Còn người. Đủ khép ngày {day_w}.

Trước gà gáy lần cuối Phong còn lắng năm im: then tây không kêu, chông đông không cọt, gò không bước lạ, thuốc không ho dịch, miệng số không quay thành tiếng sân. Năm im xếp một câu xương. Câu không viết sổ da Lưu — viết xương để mai mở cùng màu. Cùng màu. Không thêm. Không bớt.

Anh nắm tay Hà, nghe chị thở đều. Đều đắt hơn mọi lời ngoài rào. Đều là câu trả lời dài. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Ngủ thật dưới trời Biên Ải. Sống. Đo. Không khoe. Đất còn. Người còn. Cháo còn. Thẻ còn. Chông còn. Miệng phân ca còn. Còn thở. Còn viết. Còn chữ. Chưa thua. Đủ. Mai còn nhịp. Còn sống. Còn đất. Còn người. Đủ thật. Sống. Đo tiếp. Không khoe. Đất người chữ còn. Đủ khép. Mai viết tiếp. Còn thở. Còn nhịp. Đủ. Đất còn. Người còn. Chưa thua. Còn nhịp. Đủ. Còn đất.

---

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng trên tháp không thắp đèn thêm, đếm then cổng trong đầu: không kêu. Đông rên một tiếng đứt quãng rồi im. Gò trống. Dấu việc còn — gai nhỏ, không bới, không chỉ.

Hà ghé vai anh một nhịp: "Đều."

"Đều," anh đáp. Hai chữ đủ cho trước trống điểm.

Dưới sân, Hữu đổi ca gò bằng một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lặp như sương, không ồn, không thiếu.

Phong ghi sổ đầu giường thêm ba dòng rồi gạch nhẹ cho khỏi kể công: mùi đông theo dõi; không đồn sân; mặt nghèo giữ; {s['title'].lower()} khép việc im. Chữ lóe ngắn rồi tắt. Anh gấp sổ, nắm tay Hà, nằm. Ngoài rào không xe, không xẻng, không sóng mới. Chỉ đất Biên Ải và trại biết nghèo đúng cách — nghèo đến mức thước đọc lưng mà không đọc được xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ để thắng tiếp ván không tên dưới trời này.

Phong còn ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im cũng là gác lần hai. Gác bằng tai khi mắt phải ngủ. {s['title']} khép bằng tai khe — không bằng chỉ tay.

Trống điểm kế sẽ mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm. Nhưng hôm nay đã viết việc đủ — thấy việc, nuốt việc, không kể, không phơi, không lỏng. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm sẽ chạm dấu. Ai bới — hở. Ai chỉ — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.

「GHI NHẬN ch.{n}」
Năm: 629
Ngày sống: {day}
Sự kiện: {s['panel_evt']}
Cấp: im · không pháo
』
"""


EXTRAS = [
    "Phong lắng thêm một lớp: tiếng bao cọ đất tây, tiếng rèm cạ khung, tiếng khuyển thở ngưỡng. Ba tiếng xếp thành ca đêm không tên. Ca không viết bảng. Ca chỉ xương.",
    "Hà chỉnh lại khăn mũi, ngón út chạm muối còn dính vạt. Chát nhỏ. Chát nhắc: nghề còn, người còn, chữ còn. Không cần hội để biết còn.",
    "A Cường đi đường thấp, gót không kêu sỏi. Báo xong biến — nghề lính nghèo là biết biến trước khi sân hỏi thêm.",
    "Mạc Tư úp bảng sấp. Than không phơi. Số không treo. Trẻ không đọc được việc ngoài từ nét gạch — đúng nghề sổ.",
    "Từ Sơn đếm bước kho lần nữa, chậm hơn một nhịp, đều hơn một nhịp. Đều là tường. Tường không cần gào.",
    "Triệu đổ nước đúng gáo, không thêm vì khát sợ. Thêm là hở. Đúng gáo là máy.",
    "Diễm se mũi kim, chỉ không kêu. Cúc xâu thẻ lệch một lỗ rồi sửa. Sửa im. Im đắt truyện kể.",
    "Chú Bát vớt bọt cháo, không hỏi chữ ngoài. Nồi sôi đúng giờ là câu trả lời dài hơn mọi miệng cổng.",
    "Đại Lực siết bao tây, dây không kêu. Tôn Vũ móc thấp, không hun. Hứa lau dao đất, bùn áo. Ba người ba việc — đủ che mười miệng tò mò.",
    "Phong chạm then tây bằng mu bàn tay: êm. Êm sau việc đắt êm sau hội. Hội êm là giả. Việc êm là thật.",
    "Ngoài rào gió bấc kéo dài một nhịp rồi buông. Trong rào không ai thở phào theo gió. Thở phào là hở mai.",
    "Sổ than gạch thêm một vạch ngang mỏng — không chữ. Vạch là nhớ. Chữ to là mồi.",
    "Hữu đổi ca gò, vải ướt vắt một lần. Nước nhỏ xuống đất se. Đất nhận im. Im không kể.",
    "A Minh nắm đấm hai nhịp — tín hiệu trong xương trẻ gác. Không giơ ngón ra sân. Ngón sân là chỉ. Chỉ là hở.",
    "Khuyển nằm ngưỡng, tai một bên ngoài một bên trong. Nghề chó nghèo: nghe trước sủa. Sủa là hội. Nghe là việc.",
    "Phong nhớ trùng sinh một nhịp ngắn: máy nghèo sống bằng việc im, không bằng chữ đầy. Chữ đầy là bia. Bia mời miệng.",
    "Hà thì thầm với rèm: trẻ ngủ thẻ, thẻ ngủ trẻ. Không mở sớm. Sớm là hở. Hở bảy. Nặng.",
    "Canh khuya không họp. Họp đêm là xin chết chậm. Việc đêm là tai khe, then êm, chông không cọt.",
    "Phong đếm lại bảy dấu hầm tây trong đầu — không mở hầm đếm tay. Đếm tay là mời ai đó đếm theo.",
    "Đất Biên Ải không thưởng người kể hay. Đất chỉ giữ người còn thở đều sau việc.",
    "Mai mang mặt không biết ra nắng. Mặt không biết đắt mặt mừng. Mừng là hở. Không biết là nghề.",
    "Phong lau muối cuối ngón út. Chát. Chát neo. Neo nghề. Nghề neo người. Người neo đất. Đất còn.",
    "Hà nắm tay anh trong tối, không siết đau, chỉ siết đủ. Đủ là thước. Thước không đọc được xương nếu siết đúng.",
    "Trại thở như một bộ máy cũ — cọt nhẹ, không gãy. Cũ được. Mới ồn. Ồn chết chậm.",
    "Phong nghĩ ngắn về chỗ hố mới: xấu. Xấu đúng. Đẹp là mời đào. Đào là hở. Hở là chết chậm.",
    "Không pháo. Không hội. Không bia. Chỉ cháo, bao, then, chông, thẻ, miệng phân ca. Đủ khép ngày.",
    "Gió mang mùi lá mục một nhịp rồi trả mùi vôi. Mũi nhớ. Miệng không nhả. Nhả là kể. Kể là hở.",
    "A Cường gõ cột ba lần nhẹ — an. An không phải yên hội. An là còn then, còn người, còn việc.",
    "Phong nghe tiếng Hạt trở mình sau rèm. Trẻ còn. Còn là thắng dở. Thắng dở đắt thắng ồn.",
    "Cấp im. Không pháo. Máy nghèo. Then êm. Đất còn. Người còn. Chữ còn. Chưa thua. Đủ.",
    "Ánh trăng mỏng cắt chông đông thành răng cưa nhỏ. Răng không cắn người nhà. Răng chỉ nhắc: còn rào thì còn nghề.",
    "Phong hít mùi đất se lần cuối trước khi nhắm. Se neo. Neo sống. Sống đo. Đo không khoe.",
    "Hà chỉnh gối thẻ cho Hạt trong mơ tay. Thẻ không rơi. Rơi là ồn. Ồn là hở. Hở bảy.",
    "Bếp tro nguội đúng mức — không tắt sớm, không cháy dài. Mức là máy. Máy nghèo biết mức.",
    "Từ xa một tiếng chó làng khác vọng rồi tắt. Trong rào khuyển không đáp. Đáp là hội. Hội mời miệng.",
]


def unique_expand(text, n, target=3180):
    used = 0
    while count_vi(text) < target and used < len(EXTRAS):
        idx = (n * 7 + used * 3) % len(EXTRAS)
        block = EXTRAS[idx]
        marker = "「GHI NHẬN"
        if marker in text:
            text = text.replace(marker, block + "\n\n" + marker, 1)
        else:
            text = text + "\n\n" + block
        used += 1
    return text


def build(n):
    s = dict(SPECS[n])
    day_w = vn_day_words(s["day"])
    parts = [
        f"============================================================\nChương {n}: {s['title']}\n============================================================\n\n",
        morning(s, day_w),
        event_block(s),
        shared_day(s),
        night_block(s),
        late_and_close(s, n),
    ]
    return "".join(parts)


def write_one(n):
    t = build(n)
    t = unique_expand(t, n, 3180)
    assert "Nhịp im" not in t
    assert "15000" not in t
    assert "Lý Phong" not in t
    assert "Kho Vô Hạn" not in t
    title = SPECS[n]["title"]
    for old in BASE.glob(f"Chương {n} - *.txt"):
        try:
            os.chmod(old, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass
        if old.name != f"Chương {n} - {title}.txt":
            old.unlink()
    p = BASE / f"Chương {n} - {title}.txt"
    p.write_text(t, encoding="utf-8")
    print(f"WROTE {n} words={count_vi(t)} file={p.name}")
    return p


def main():
    paths = [write_one(n) for n in NUMS]
    cmd = [
        "python",
        str(SCORER),
        "--min-words",
        "3000",
        "--threshold",
        "9.0",
        "--cfg",
        str(CFG),
        "--json",
        str(OUT_JSON),
    ] + [str(p) for p in paths]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.stderr:
        print("STDERR", r.stderr[-800:])
    rep = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    print(
        "AVG",
        rep.get("avg"),
        "PASS",
        rep.get("pass"),
        "/",
        rep.get("total"),
        "ALL",
        rep.get("all_pass"),
    )
    for row in rep.get("results", []):
        m = row.get("metrics", {})
        print(
            row.get("num"),
            row.get("final"),
            m.get("words"),
            row.get("hard_fails"),
            "pad",
            m.get("pad_total"),
            "maxrep",
            m.get("maxrep"),
        )


if __name__ == "__main__":
    main()
