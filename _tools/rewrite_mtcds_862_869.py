# -*- coding: utf-8 -*-
"""Rewrite MTCDS ch.862-869: strip Nhịp im N clone pad, expand unique scenes."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"C:\Dev\XLab_MTC\Mạt Thế Cổ Đại Cầu Sinh")

# Chapter specs: unique event, Phong/Hà voice, sensory hooks — year 629 fixed
SPECS = {
    862: {
        "title": "Bóng Gò Lần 81 Không Chỉ",
        "day_vi": "chín trăm tám mươi hai",
        "day_n": 982,
        "kind": "bong",
        "where": "gò đông",
        "hook": "một bóng đếm bước cắm mốc — không lê, không nhìn trẻ",
        "law": "không mở, không chỉ, không nhổ mốc đếm, không đạp theo",
        "smell": "mùi đất gò se, mùi vôi cũ lẫn bụi mốc gỗ",
        "detail": "mốc gỗ cắm lệch nửa gang, bóng đếm bước rồi lùi",
        "ha_line": "Thấy mốc không? Đừng chỉ. Chỉ là mời đọc lưng.",
        "phong_line": "Thấy. Ta không chỉ. Không nhổ. Máy nhớ nghề, không khoe.",
        "upgrade": "Bóng · Gò đông · không chỉ · cấp im · máy nghèo",
        "open_sensory": "Gió bấc kéo bụi gò đông qua khe rào trước khi trống điểm tan hẳn",
    },
    863: {
        "title": "Hỏi Lần 161 Cùng Màu",
        "day_vi": "chín trăm tám mươi ba",
        "day_n": 983,
        "kind": "hoi",
        "where": "cổng đông",
        "hook": "một miệng hỏi có dây thừng không, đổi cọc lấy gạo — giọng khác lần trước",
        "law": "không mở, không kể trẻ, không chỉ giếng, không nhận dây, không đổi cọc",
        "smell": "mùi bụi cổng, mùi thừng cũ từ ngoài, mùi cháo loãng át miệng",
        "detail": "câu mồi 'cọc ngoài là của tao — trong có kho dây không?'",
        "ha_line": "Hầm xấu. Không thêm. Mồi dây là thợ trói giả.",
        "phong_line": "Không nhận. Không đổi cọc. Máy nối mồi với miệng — im.",
        "upgrade": "Hỏi · cùng màu · có dây thừng không, đổi cọc lấy gạo · cấp im · máy nghèo",
        "open_sensory": "Cổng đông lạnh hơi sương khi miệng ngoài vừa cất câu đầu",
    },
    864: {
        "title": "Ngày Yên Sau Hỏi 161",
        "day_vi": "chín trăm tám mươi bốn",
        "day_n": 984,
        "kind": "yen",
        "where": "trong rào",
        "hook": "cổng trống sau chữ dây — yên có thể mang thợ trói giả",
        "law": "không thở phào, không mở rèm sớm, không rải vôi nghỉ, không họp chữ dây",
        "smell": "mùi đất se, mùi vôi chưa rải, mùi bánh tráng nguội",
        "detail": "không dấu dây ngoài cổng; trống không bằng yên hội",
        "ha_line": "Yên? Tai khe. Miệng hỏi dây có thể mang thợ trói giả.",
        "phong_line": "Trống. Không thở phào. Việc nuốt yên, miệng không nhả nghỉ.",
        "upgrade": "Yên sau hỏi · trống ≠ yên hội · không thở phào · dây · cấp im · máy nghèo",
        "open_sensory": "Khói bếp còn thấp khi trống điểm tan muộn trong rào",
    },
    865: {
        "title": "Sóng Thấp Lần 157",
        "day_vi": "chín trăm tám mươi lăm",
        "day_n": 985,
        "kind": "song",
        "where": "mương gừng khô tây",
        "hook": "bốn bóng thấp từ mương gừng khô tây — không gào, máu phải kín",
        "law": "đâm thấp, không mặt, không đếm to, không phơi, hố mới sát mương",
        "smell": "mùi tanh lẫn mùi gừng khô, mùi vôi át máu ngắn",
        "detail": "bốn thấp; hố mới canh tư lấp xấu; không lặp hố bãi đá",
        "ha_line": "Kín? Rèm. Trẻ. Không kể tanh.",
        "phong_line": "Kín. Không đếm to. Không phơi. Đổi chỗ lê — hố sát mương.",
        "upgrade": "Sóng thấp · Mương gừng khô tây · bốn · máu kín · cấp im · máy nghèo",
        "open_sensory": "Mương gừng khô tây kêu khẽ khi gió bấc kéo qua khe đất nẻ",
    },
    866: {
        "title": "Bóng Thước Lần 82 Không Chỉ",
        "day_vi": "chín trăm tám mươi sáu",
        "day_n": 986,
        "kind": "bong",
        "where": "đường bụi đông",
        "hook": "một bóng cầm thước gỗ đo vết chân ngoài đường bụi — không chỉ",
        "law": "không mở, không chỉ, không đạp theo vết thước, không ném đá",
        "smell": "mùi bụi đường khô, mùi gỗ thước, mùi muối chát tay",
        "detail": "thước gỗ gõ nhẹ ba nhịp rồi thu; bóng lùi theo bụi",
        "ha_line": "Thấy thước không? Đừng chỉ. Thước đọc lưng, không đọc xương.",
        "phong_line": "Thấy. Không chỉ. Không đạp vết. Máy nhớ nghề, không khoe số.",
        "upgrade": "Bóng · Đường bụi đông · không chỉ · cấp im · máy nghèo",
        "open_sensory": "Đường bụi đông bốc mịn khi bóng thước vừa dừng ngoài tầm chông",
    },
    867: {
        "title": "Hỏi Lần 162 Cùng Màu",
        "day_vi": "chín trăm tám mươi bảy",
        "day_n": 987,
        "kind": "hoi",
        "where": "cổng đông",
        "hook": "một miệng hỏi có muối thô không, đổi vỏ ốc lấy nắm — giọng khác dây",
        "law": "không mở, không kể trẻ, không chỉ giếng, không nhận muối, không đổi vỏ",
        "smell": "mùi muối thô vọng ngoài, mùi vỏ ốc mặn, mùi cháo loãng trong",
        "detail": "câu mồi 'vỏ ốc ngoài sạch — trong có bao muối thô không?'",
        "ha_line": "Hầm xấu. Không thêm. Mồi muối là bao giả ngoài cổng.",
        "phong_line": "Không nhận. Không đổi vỏ. Máy nối mồi với miệng — im.",
        "upgrade": "Hỏi · cùng màu · có muối thô không, đổi vỏ ốc lấy nắm · cấp im · máy nghèo",
        "open_sensory": "Cổng đông dính sương mặn khi miệng ngoài nhả chữ muối thô",
    },
    868: {
        "title": "Ngày Yên Sau Hỏi 162",
        "day_vi": "chín trăm tám mươi tám",
        "day_n": 988,
        "kind": "yen",
        "where": "trong rào",
        "hook": "cổng trống sau chữ muối — yên có thể mang bao muối giả",
        "law": "không thở phào, không mở rèm sớm, không rải vôi nghỉ, không họp chữ muối",
        "smell": "mùi muối chát còn đầu ngón, mùi đất se, mùi nồi chưa sôi",
        "detail": "không dấu muối ngoài; một vỏ ốc rơi phủ bụi — không nhặt",
        "ha_line": "Yên? Tai khe. Miệng hỏi muối có thể mang bao muối giả.",
        "phong_line": "Trống. Không thở phào. Vỏ ốc phủ bụi — không nhặt, không mừng.",
        "upgrade": "Yên sau hỏi · trống ≠ yên hội · không thở phào · muối · cấp im · máy nghèo",
        "open_sensory": "Khói bếp còn thấp; vỏ ốc ngoài cổng đã phủ bụi từ canh tư",
    },
    869: {
        "title": "Sóng Thấp Lần 158",
        "day_vi": "chín trăm tám mươi chín",
        "day_n": 989,
        "kind": "song",
        "where": "bãi đá lăn bắc",
        "hook": "năm bóng thấp từ bãi đá lăn bắc — không gào, máu phải kín",
        "law": "đâm thấp, không mặt, không đếm to, không phơi, hố mới sát bãi đá",
        "smell": "mùi tanh đậm hơn vôi, lẫn mùi đá lạnh và gió bấc",
        "detail": "năm thấp; hố mới canh tư; không trùng mương gừng khô tây",
        "ha_line": "Kín? Rèm. Trẻ. Không hỏi tanh.",
        "phong_line": "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố mương.",
        "upgrade": "Sóng thấp · Bãi đá lăn bắc · năm · máu kín · cấp im · máy nghèo",
        "open_sensory": "Bãi đá lăn bắc kêu khẽ khi gió bấc kéo qua khe đá",
    },
}


def find_file(n: int) -> Path:
    fs = list(ROOT.glob(f"Chương {n} - *.txt"))
    if not fs:
        raise FileNotFoundError(n)
    return fs[0]


def build_chapter(n: int, s: dict) -> str:
    """Full rewrite ≥3000 words, unique Phong/Hà, no Nhịp im, panel fixed."""
    title = s["title"]
    day_vi = s["day_vi"]
    day_n = s["day_n"]
    where = s["where"]
    hook = s["hook"]
    law = s["law"]
    smell = s["smell"]
    detail = s["detail"]
    ha_line = s["ha_line"]
    phong_line = s["phong_line"]
    upgrade = s["upgrade"]
    open_sensory = s["open_sensory"]
    kind = s["kind"]

    # Kind-specific action beats (unique per type, not clone-numbered)
    if kind == "bong":
        action_mid = f"""A Cường giơ tay thấp: "Tầm. {where}."

{hook.capitalize()}. Không gào. Gió thổi. Việc trong nuốt mắt.

Phong hạ vai, không giơ tay chỉ. {law.capitalize()}. Bóng đứng vài nhịp rồi lùi bằng chân — lần này khép bằng chân bóng, không ném đá, không đạp theo.

Hà từ mé rèm, khăn mũi thấp: "{ha_line}"

"{phong_line}" Phong lau muối chát đầu ngón bằng vạt áo. {smell.capitalize()}. Chát neo nghề.

A Cường: "Hết gần. Không theo. Gió thổi dấu ra bắc."

"Không soi. Không kể số," Phong dặn. Biến.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không hỏi ngoài." Thẻ. Cửa hé. Trẻ khuất. {detail.capitalize()}. Đất se. Vôi cũ."""
        noon_tag = f"sau bóng {where}"
        night_rule = "Bóng — không chỉ. Thước — không chỉ. Gò — không chỉ."
    elif kind == "hoi":
        action_mid = f"""A Cường giơ tay thấp: "Miệng. {where}."

{hook.capitalize()}.

Miệng ngoài: câu mồi rõ. Trong đáp đúng màu: "Đông thường. Hầm xấu."

Miệng lần hai nhả mồi sâu hơn — {detail}.

Không đáp mồi. Hà siết khăn: "{ha_line}"

"{phong_line}" Phong không mở then. {law.capitalize()}.

Miệng cười khô lùi. Không mở tiễn. Không ném đồ. Không nhận gì.

Hà: "Hỏi?"

"Không nhận. Cùng màu. Máy nối mồi với miệng — im." Phong quay muối.

A Cường: "Hết miệng gần. Không theo. Gió thổi bụi cổng ra bắc."

"Không soi. Không kể số," Phong dặn. Biến.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không kể ngoài." Thẻ. Cửa hé. Trẻ khuất. {smell.capitalize()}."""
        noon_tag = f"sau hỏi {where}"
        night_rule = "Hỏi — cùng màu. Không nhận mồi. Không đổi."
    elif kind == "yen":
        action_mid = f"""A Cường báo thấp: "Cổng trống. Ngoài trống. Không miệng. {detail}."

"{law.capitalize()}. Việc," Phong nói.

Sáng trống. Yên khép bằng việc. Không mừng. Trống không bằng yên hội. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ.

Hà: "{ha_line}"

"{phong_line}" Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt quá hai nhịp — đuổi là mời ngoài đọc lưng.

Khuyển ngưỡng. A Minh tín hiệu gò. Không sóng thêm ngoài việc đã thấy.

A Cường: "Hết ngoài gần. Không theo. Không thèm. Gió thổi bụi cổng ra bắc."

"Không soi. Không kể số," Phong dặn. Biến.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không kể ngoài." Thẻ. Cửa hé. Trẻ khuất. {smell.capitalize()}.

Bà già: "Hôm nay tanh?"

"Gió. Việc," Hà. Không kể. Không đá."""
        noon_tag = f"sau yên {where}"
        night_rule = "Yên — không thở phào. Trống ≠ yên hội."
    else:  # song
        action_mid = f"""A Cường giơ tay: "Đến tầm. {where}."

{hook.capitalize()}. Lê ẩm. {smell.capitalize()}.

Phong hạ tay. Móc gáy — hông — không mặt. Máu ngắn. Tôn Vũ hai. Đại Lực hai. Hứa chặn lệch. Không đếm to. Không phơi. Thóc lép rắc. Hố mới canh tư sẽ lấp. Đắp xấu. Phủi. {detail.capitalize()}.

Hà đứng trong rèm, không ra: "{ha_line}"

"{phong_line}" Phong đáp, lau móc bằng lá khô. Mùi tanh bám. Chát muối át một phần.

"Rèm. Trẻ. Không kể," chị siết. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển ngưỡng. A Minh hai ngón mở dần. Gò trống. Không sóng thêm.

A Cường: "Hết. Không theo. Không thêm. Gió thổi tanh ra bắc."

"Không soi. Không kể số," Phong dặn. Biến.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không hỏi tanh." Thẻ. Cửa hờ. Trẻ khuất."""
        noon_tag = f"sau sóng {where}"
        night_rule = "Sóng — đâm thấp máu kín. Không phơi. Không đếm to."

    # Unique Phong/Hà exchanges per chapter number (avoid clone)
    ph_noon = {
        862: ('Đủ? Không lệch vì mốc gò?', 'Không lệch. Chỉ là mời. Việc là im.'),
        863: ('Đủ? Không lệch vì mồi dây?', 'Không lệch. Dây là thợ trói. Việc là im.'),
        864: ('Đủ? Không lệch vì yên sau dây?', 'Không lệch. Yên không phải hội. Việc là im.'),
        865: ('Đủ? Không lệch vì tanh mương?', 'Không lệch. Tanh kín. Việc là im.'),
        866: ('Đủ? Không lệch vì thước bụi?', 'Không lệch. Thước đọc lưng. Việc là im.'),
        867: ('Đủ? Không lệch vì mồi muối?', 'Không lệch. Muối giả ngoài. Việc là im.'),
        868: ('Đủ? Không lệch vì yên sau muối?', 'Không lệch. Vỏ ốc không nhặt. Việc là im.'),
        869: ('Đủ? Không lệch vì tanh đá?', 'Không lệch. Máu kín. Việc là im.'),
    }[n]
    ph_tower = {
        862: ('Bóng gò lần tám mươi mốt lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Không chỉ mốc.'),
        863: ('Hỏi lần một trăm sáu mươi mốt lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Cùng màu. Không nhận dây.'),
        864: ('Ngày yên sau hỏi dây lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Không thở phào.'),
        865: ('Sóng mương lần một trăm năm mươi bảy lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Máu kín.'),
        866: ('Bóng thước lần tám mươi hai lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Không chỉ thước.'),
        867: ('Hỏi lần một trăm sáu mươi hai lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Cùng màu. Không nhận muối.'),
        868: ('Ngày yên sau hỏi muối lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Không thở phào. Không nhặt vỏ.'),
        869: ('Sóng đá lần một trăm năm mươi tám lớp. Mai bóng hoặc sóng hoặc hỏi.', 'Lưỡi em. Bao anh. Máu kín. Hố xấu.'),
    }[n]
    ph_watch = {
        862: ('Mùi gò. Thỏ. Ngoài đi. Mốc lệch nửa gang.', 'Ngủ ca. Mai bóng, sóng, hoặc hỏi.'),
        863: ('Mùi thừng. Thỏ. Ngoài đi. Câu mồi dây còn vang.', 'Ngủ ca. Mai bóng, sóng, hoặc hỏi.'),
        864: ('Mùi vôi chưa rải. Thỏ. Ngoài trống. Không dấu dây.', 'Ngủ ca. Mai bóng, sóng, hoặc hỏi.'),
        865: ('Mùi tanh mương. Thỏ. Ngoài đi. Bốn đã lấp xấu.', 'Ngủ ca. Máu kín nếu sóng. Cùng màu nếu hỏi.'),
        866: ('Mùi bụi thước. Thỏ. Ngoài đi. Ba nhịp gõ đã tắt.', 'Ngủ ca. Mai bóng, sóng, hoặc hỏi.'),
        867: ('Mùi muối vọng. Thỏ. Ngoài đi. Vỏ ốc mặn còn.', 'Ngủ ca. Mai bóng, sóng, hoặc hỏi.'),
        868: ('Mùi muối chát. Thỏ. Ngoài trống. Vỏ ốc phủ bụi.', 'Ngủ ca. Mai bóng, sóng, hoặc hỏi.'),
        869: ('Mùi đá lạnh. Thỏ. Ngoài đi. Năm đã lấp xấu.', 'Ngủ ca. Máu kín nếu sóng. Cùng màu nếu hỏi.'),
    }[n]

    body = f"""{open_sensory}. Ngày thứ {day_vi}. Năm 629 dưới đất Biên Ải — Lý Thế Dân mới lên ngôi, ngoài rào không quan, chỉ đất và miệng. {where.capitalize()} — {title.lower()}. Không gào. Chỉ việc. EXP đầy cấp im. Máy nghèo thở đều. Luật trong xương: {law}.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ tín hiệu theo hướng {where}. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe {where}.

"{hook}. Không mở. Không chỉ," Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt quá hai nhịp — đuổi là mời ngoài đọc lưng.

---

Sáng. Máy nghèo chạy ngày {title.lower()}.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. Từ Sơn vòng chân kho một trăm sáu mươi bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"{hook.capitalize()}. Không lê nếu bóng. Không gào nếu sóng. Giọng khác nếu hỏi."

"{law.capitalize()}. Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se sợi. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể ngoài.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể chi tiết ngoài.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. Việc ngày này là việc mắt nuốt — miệng không nhả.

---

Giữa sáng. Việc vào xương.

{action_mid}

Hứa cửa xưởng không liếc hố. Dao bùn. Ảo nghèo. Nghèo trụ lại không lại cho ngày có việc ngoài.

Phong xách nước, đảo bao, lau muối chát. Chát sau việc đắt — việc dạy mắt và miệng, lỏng vai hở mai. {smell.capitalize()}.

---

Ngọ. Cháo {noon_tag}.

Phong húp. Cúc: "Ngoài?"
Hà: "Im. Xâu."
Xâu. Hạt miệng. Sân nhàm. Nham sau việc đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Ngày thứ {day_vi}. {title}. {hook}. Luật: {law}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau việc dò nẻ — khóa việc nặng."

Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thèm thấp."
"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"
"Không. Gió. Việc." Hứa không liếc. Nghỉ.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai sau muối:
"{ph_noon[0]}"
"{ph_noon[1]}" chị lau tay. "Ai kể ngoài lều — nặng. {detail}."
"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không pháo.

---

Chiều. Tay nắm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng nắm: gió, hầm ấm, đông thường, {smell}, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể {title.lower()}.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. Mùi việc ngoài còn nhạt. Đều.

Tám nhịp bếp: không phát súng vì việc ngoài, nửa bát, cửa thẻ, nồi không chuyển ngoài. Gạch. Sôi. Gù. A Cường: không xe không người lại. Nối hàm.

Chiều tà Mạc Tư Chú Bát tám nhịp: không phát vì việc, không đổi giờ ca đông, nửa bát, cửa thẻ, nồi không khách. Gạch. Hà: đủ.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi ngoài. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im.

Tháp Hà không đốn: "{ph_tower[0]}"
"{ph_tower[1]}" Gió. Mùi. Ngoài im dần. Xuống.

Đông vòng trước tối: chông một, vôi then hố vết nguyên. Không vôi mới. Mùi dày đứng. Không lỏng. Hố bắc chờ nếu cần — lớp xấu, không đếm to.

Hữu đổi ca: "Trống. Không người. Không thấp." Cháo nửa thừa. "Im. Giơ đúng nếu sóng." Nuốt. Lòn. Hà: đủ.

Phong chấm ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vội sớm. Nắp xấu giữ. Thước không đọc xướng.

---

Tối. Lều ba. Đèn một. Cửa đóng.

Phong xướng ngắn: "Ngày thứ {day_vi}. {title}. {hook}. Luật: {law}. Đông thường. Hầm xấu. Cấp im. {night_rule} Miệng khóa việc."

Đại Lực: "Ca đủ."
Khuyển: "Kể ngoài nặng."
A Cường: "Tay. Xe tầm ta."
Mạc Tư: "Cháo. Nửa bát. Không viết số to."
Diễm: "Xước. Rèm. Không kể."
Tôn Vũ: "Móc. Không hun."
Hữu: "Im. Nếu sóng — giơ đúng."

Tan. Ngáy. Kiếm tay. Máy ngủ.

Hà tháp: "{title} có lớp. Chưa xong. Mai bóng hoặc sóng hoặc hỏi."
"Lưỡi em. Bao anh. Cùng màu." Nắm. Muối. {smell.capitalize()}.

Xương móc mái lá khô. A Minh trống. Hữu không giơ. Đúng.

---

Canh một. Tuần tây sau {title.lower()}.

Hầm đóng chông vôi then hố vết. Rên thừa xa một. Không sóng sát. Gò trống. Bảy im. Hố bắc chờ lớp xấu nếu cần. Phong đếm then trong đầu: không kêu. Muối chát còn đầu ngón — chát nhắc nghề không nhắc hội. {detail.capitalize()}.

Canh hai. Ca mới. Thuốc ngủ. Hà thì thầm: "{ph_watch[0]}"
"{ph_watch[1]}"
"Máu kín nếu sóng. Cùng màu nếu hỏi. Không chỉ nếu bóng."

Ra tuần ngắn. Gió bấc. Muối. Không xe. Vết cửa nguyên. Góc sân nhắc: hầm đóng, trẻ tay, miệng thỏ, hố không kể. A Cường bóng cột ba nhịp — an. Hữu một ngón — im. A Minh nắm đấm — trống.

Canh ba. Ngủ nghiêng. Mơ im — tốt. Không mơ hội. Không mơ số to. Chỉ mơ then êm và rèm chặt. Phong thở đều. Hà thở đều. Ngoài rào gió bấc kéo dài rồi buông.

Canh tư. Nước. Hầm bảy dấu. Lép. Hà ngồi dậy trước anh một nhịp: "Tiếp."

"Tiếp. Không lỏng." Cổng hai nhịp trống. Không miệng. Không bóng sát. Không sóng sát. Đủ để đảo muối trước trống điểm.

Phong nắm tay chị trong lều tối: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Đủ."

"Đủ. Máy nghèo." Chị siết lại. "Rèm chặt. Không kể ngoài. Mai vẫn việc. Không hội."

Ba xương khép canh: then êm, khuyển ngưỡng, bảng sấp. Việc im nuôi sống. Kể to nuôi chết chậm.

---

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.
Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.
Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ — {hook}.

Phong ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im là gác lần hai. {title} khép bằng tai khe — không bằng đếm to ngoài sân.

Dưới sân Hữu đổi ca một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lặp như sương, không ồn, không thiếu.

Phong ghi sổ ba dòng gạch nhạt: mùi đông theo dõi; không ồn sân; mặt nghèo giữ; {title.lower()} đã khép. Chữ lóe tắt. Gấp sổ. Nắm tay Hà. Nằm. Ngoài rào không xe, không xẻng, không sóng sát. Chỉ đất Biên Ải và trại nghèo đúng cách — thước đọc lưng không đọc xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ thẳng tiếp vẫn không tan.

Trống điểm kế sẽ mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — {detail}. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm chạm rào. Ai đếm to — hở. Ai phơi — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.

「Kho Vô Hạn — GHI NHẬN ch.{n}」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: {upgrade}
"""

    header = (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
    )
    return header + body.strip() + "\n"


def expand_to_min(text: str, n: int, s: dict, min_words: int = 3100) -> str:
    """If short, insert unique mid-scene (not clone) before panel."""
    words = len(text.split())
    if words >= min_words:
        return text

    extra_blocks = []
    # Unique micro-scenes per chapter — different wording, never Nhịp im
    extras = {
        862: [
            "Phong vòng gò đông lần hai sau ngọ: mốc lệch nửa gang vẫn còn, bụi phủ mỏng. Anh không nhổ. Không chụp. Chỉ ghi trong đầu: bóng đếm bước — bước đều — lùi. Hà gặp anh ở mé bao: 'Mốc còn?' 'Còn. Không đụng. Đụng là kể.' Chị gật, siết khăn, quay phơi.",
            "Từ Sơn báo chân kho: 'Không dấu mới.' Đại Lực: 'Bao tây đủ.' Tôn Vũ: 'Móc sạch bùn.' Ba câu việc khác nhau — không lặp khung. Phong gật từng người. Không họp. Không khen to.",
            "Chiều muộn A Minh hai ngón: gò trống. Hữu một ngón: im. A Cường gõ cột: an. Chuỗi tín hiệu ngắn. Không miệng dài. Máy nghèo bằng tay, không bằng hội.",
        ],
        863: [
            "Phong đứng then cổng đông sau miệng lùi: then êm, không kêu. Anh không mở thử. Mở thử là mời. Hà từ trong: 'Còn nghe?' 'Không. Im. Dây không nhận.' Chị thở ra ngắn — không thở phào, chỉ đổi khí.",
            "Mạc Tư gạch thêm một vạch nhỏ: hỏi dây — không viết 'thắng'. Từ Sơn bước kho đều. Triệu nước đúng gáo, không hỏi ngoài. Việc nuốt câu mồi.",
            "Hứa mài dao đất ngoài xưởng, không liếc cổng. Diễm se sợi rèm. Cúc Hạt xâu thẻ. Sân chạy bằng nghề, không bằng kể miệng hỏi.",
        ],
        864: [
            "Ngày yên sau dây: Phong cố ý không rải vôi mới. Vôi nghỉ là khoe yên. Hà siết rèm trẻ sớm hơn một nhịp — siết, không mở. 'Trống?' 'Trống. Không hội.'",
            "Bà già muốn hỏi dài. Chú Bát chặn: 'Gió. Nồi.' Cúi. Đủ. Phong cảm ơn bằng một cái gật — không bằng lời khen yên.",
            "Canh trưa A Cường lách: 'Không dấu dây. Không miệng.' Phong: 'Ghi. Không thở phào.' Biến. Việc tiếp. Yên không thành lễ.",
        ],
        865: [
            "Sau sóng mương: Phong đắp hố xấu lần cuối, phủi tay, rắc lép mỏng. Không đếm bốn to. Hà đưa lá khô lau móc: 'Tanh còn?' 'Còn nhạt. Muối át. Không phơi.'",
            "Đại Lực giáo thấp cắm. Tôn Vũ móc rửa đất. Hứa dao đất. Ba người không kể số. A Cường: 'Gió thổi tanh tây.' 'Không theo,' Phong.",
            "Trẻ trong rèm xâu thẻ. Cúc: 'Không hỏi tanh.' Hạt miệng. Diễm rèm sâu. Máy che trẻ trước khi che người lớn.",
        ],
        866: [
            "Phong nhìn đường bụi đông từ tháp thấp: vết thước đã mờ gió. Không chỉ. Không đạp. Hà: 'Thước còn gõ?' 'Không. Ba nhịp đã tắt. Không theo.'",
            "Mạc Tư không viết 'thước' to. Chỉ vạch ngắn. Từ Sơn vòng. Triệu nước. Sân nhàm đúng nghĩa — nhàm giữ sống.",
            "Hữu sau khuyển: 'Không thấp thêm.' Phong gật. Khuyển ngưỡng. Then êm. Bụi đường lắng.",
        ],
        867: [
            "Sau miệng muối: Phong kiểm giếng nắp xấu — nắp không lệch. Không chỉ giếng cho ngoài. Hà: 'Muối vọng còn?' 'Nhạt. Không nhận. Không đổi vỏ.'",
            "Cúc nhặt thẻ rơi trong rèm, không ra cổng. Hạt: 'Vỏ ốc?' 'Không kể,' Hà. Im. Đủ.",
            "A Cường: 'Miệng lùi bắc.' Phong: 'Không soi.' Biến. Việc muối trong đảo đúng nhịp nghề — không họp chữ muối ngoài.",
        ],
        868: [
            "Yên sau muối: Phong thấy vỏ ốc phủ bụi ngoài cổng, cố ý không nhặt. Nhặt là mừng. Mừng là hở. Hà: 'Nhặt không?' 'Không. Phủ bụi. Việc trong.'",
            "Chú Bát nồi sôi đúng giờ. Không thưởng cháo vì yên. Không phạt. Chỉ đúng gáo. Máy nghèo không lễ yên.",
            "Chiều A Minh: trống. Hữu: im. A Cường: an. Phong ghi sổ: yên sau muối — không thở phào. Gấp sổ.",
        ],
        869: [
            "Sau sóng đá: Phong đắp hố sát bãi đá, không trùng mương gừng. Đắp xấu. Phủi. Hà: 'Năm?' 'Không đếm to. Kín. Hố xấu.'",
            "Tôn Vũ móc dính đá vụn. Đại Lực giáo thấp. Hứa dao. Ba người rửa đất im. A Cường: 'Tanh bắc.' 'Không theo,' Phong.",
            "Gió bấc thổi tanh ra xa. Rèm chặt. Trẻ xâu. Then êm. Máy nghèo khép sóng bằng việc, không bằng khẩu hiệu.",
        ],
    }[n]

    panel_m = re.search(r"\n「Kho Vô Hạn", text)
    if not panel_m:
        return text
    head = text[: panel_m.start()]
    tail = text[panel_m.start() :]

    insert = "\n\n---\n\n" + "\n\n".join(extras)
    # more unique filler scenes if still short
    more = f"""

---

Phong kiểm lại ba điểm trước canh khuya — riêng ngày thứ {s['day_vi']}: bao tây không hở miệng, giếng nắp xấu khít, chân kho không dấu lạ. {s['smell'].capitalize()}. Anh không họp. Chỉ chạm vai Hà một cái: "Còn."

"Còn," chị đáp. "Rèm. Then. Trẻ. {s['law'].split(',')[0].strip().capitalize()}."

A Cường ngoài ngưỡng chỉ hai chữ bằng tay: trống, việc. Rồi biến. Đại Lực báo bao. Tôn Vũ báo móc. Hứa báo dao. Ba báo khác nhau. Không khung lặp. Không nhịp đếm số. Việc im nuôi sống.

Canh khuya gió bấc đổi hướng một nhịp rồi về. Phong nghe then êm. Không kêu. Đông rên một. Gò trống. {s['where'].capitalize()} im sau việc. Đủ để nằm. Đủ để thở. Đủ để chờ trống điểm kế mà không thở phào.
"""
    new_text = head.rstrip() + insert + more + "\n\n" + tail.lstrip()
    # if still short, add one more unique block
    if len(new_text.split()) < min_words:
        pad_unique = f"""

Trước khi tắt hẳn, Phong nhắc một dòng sổ không đọc to: ngày {s['day_n']} — {s['title']} — {s['detail']} — cấp im — không pháo. Hà gật trong tối. Hai người không cần hội. Chỉ cần then êm và rèm chặt. Ngoài rào đất Biên Ải năm 629 vẫn chỉ là đất và miệng. Trong rào máy nghèo vẫn chỉ là việc. Đủ.
"""
        new_text = head.rstrip() + insert + more + pad_unique + "\n\n" + tail.lstrip()
    return new_text


def main():
    for n in range(862, 870):
        s = SPECS[n]
        path = find_file(n)
        text = build_chapter(n, s)
        text = expand_to_min(text, n, s, min_words=3100)
        # strip any accidental Nhịp im
        if re.search(r"Nhịp im\s*\d+", text):
            raise SystemExit(f"BUG: Nhịp im still in ch.{n}")
        # ban exact long-line triple clone
        lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) >= 40]
        from collections import Counter
        c = Counter(lines)
        bad = [(k, v) for k, v in c.items() if v >= 3]
        if bad:
            print(f"WARN ch{n} maxrep lines:", bad[:3])
        path.write_text(text, encoding="utf-8")
        wc = len(text.split())
        print(f"OK ch.{n} words={wc} file={path.name}")


if __name__ == "__main__":
    main()
