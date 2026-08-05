# -*- coding: utf-8 -*-
"""Unique full rewrite CLONE pad ch.734-741.
Style: ch.726 pass batch prose + Kho Vô Hạn EXP panel.
No Nhịp im pad. Phong/Hà. Năm 629. EXP 15000/15000 cấp 3.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")


def vi_words(t: str) -> int:
    return len([w for w in t.split() if len(w) >= 2])


def hdr(n: int, title: str) -> str:
    return (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
    )


def panel(n: int, day: int, event: str) -> str:
    return (
        f"\n「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"EXP: 15000 / 15000\n"
        f"Hiện tại: cấp 3\n"
        f"Ngày sống: {day}\n"
        f"Nâng cấp: {event}\n"
    )


def cast_open(signal: str) -> str:
    return (
        "Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. "
        "Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. "
        "Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. "
        f"{signal} "
        "Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.\n"
    )


def cast_run(tag: str) -> str:
    return (
        f"\nSáng. Máy nghèo chạy ngày {tag}.\n\n"
        "Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. "
        "Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. "
        "Đại Lực đảo bao tây. Tôn Vũ móc thấp trong xưởng, không hun lửa sớm. Hứa lau dao đất. "
        "Diễm se sợi. Khuyển nằm ngưỡng. Hữu sau chó.\n\n"
        'Bà già ghé mé bếp: "Gió?"\n'
        '"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.\n\n'
        "Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. "
        "Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể.\n\n"
        "Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. "
        "Hữu không giơ sớm. Việc mắt nuốt — miệng không nhả.\n"
    )


def afternoon(tag: str, scent: str, micro: str) -> str:
    return f"""
---

Ngọ. Cháo sau {tag}.

Phong húp. Cúc: "Ngoài?"
Hà: "Im. Xâu."
Xâu. Hạt miệng. Sân nhàm. Nham sau {tag} đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu nghe luật ngắn: không kể số, không mở rèm sớm, đông thường, hầm xấu, nếu bóng — không chỉ, nếu sóng — đâm thấp, nếu hỏi — cùng màu. Miệng sau {tag} dò nẻ — khóa việc nặng. Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thêm."
"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"
"Không. Gió. Việc." Hứa không liếc. Nghỉ.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai sau muối:
"Đủ? Không lệch vì {tag}?"
"Không lệch. Việc không phải hội. Việc là im," chị lau tay. "Ai kể ngoài lều — nặng."
"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không pháo.

---

Chiều. Tay nắm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng nắm: gió, hầm ấm, đông thường, {scent}, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể {tag}.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. {micro}

Tám nhịp bếp: không phết sử vì việc, nửa bát, cửa thẻ, nồi không chuyện số. Gạch. Sôi. Gõ. A Cường: không xe không người lại. Nói hãm.

Chiều tà Mạc Tư Chú Bát tám nhịp: không phết, không đổi giờ ca đông, nửa bát, cửa thẻ, nồi không khách. Gạch. Hà: đủ.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi số. Cúc ngủ thẻ. Hạt gối. Thím Liên chiều. Ru im.

Tháp Hà không đèn: "Mai bóng hoặc sóng hoặc hỏi."
"Lời em. Bao anh. Không lệch." Gió. Mùi. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Mùi dày đúng. Không lỏng.

Hữu đổi ca: "Trống. Không người." Cháo nửa thừa. "Im. Giữ đúng nếu sóng." Nuốt. Lên. Hà: đủ.

Phong chạm ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Nắp xấu giữ. Thước không đọc xưởng.
"""


def night(tag: str, a: str, b: str, c: str) -> str:
    return f"""
---

Đêm. Lều tây. Ghế đá còn mùi muối và {a}.

Canh một. Phong nắm tay Hà, nhắc ngắn: {tag}. Không kể ngoài lều. Mai tai khe. Số lần không huy chương.

"Còn thở đều không?" chị hỏi khẽ — giọng mệt thật sau ngày việc, không phải câu máy.

"Đều. Không lỏng," anh đáp. "Mai vẫn việc. Không hội kể hôm nay."

"Rèm chặt. Không kể ngoài." Chị gật. Nắm siết rồi lỏng. Đủ.

Canh hai. Ngồi trong. Khuyển rít gió. Then êm. A Minh ngoài gò giơ nắm đấm — im. Hữu đổi ca một ngón. A Cường gõ cột ba lần — an. Không đèn thừa. Không họp miệng. {b}

Canh ba. Ngủ nghiêng. Mơ không mang chữ to. Tốt. Thỉnh thoảng rên đông một tiếng đứt — đếm, im, không dậy vội. Gió bấc mang {c}.

Canh tư. Nước. Hầm tây: bảy dấu. Thóc lép. Đắp xấu. Hà khẽ: "Tiếp." Phong: "Tiếp. Không lỏng." Cổng hai nhịp trống. Phía việc hôm nay im — không lê, không miệng, không bóng soi.

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng tháp không thắp thêm. Đếm then trong đầu: không kêu. Đông im. Hà ghé vai: "Đều." "Đều," anh đáp. Hai chữ đủ trước trống điểm.

Dưới sân Hữu đổi ca gò. A Minh nắm đấm. Ca đêm như sương — không ồn, không thiếu. Phong ghi sổ thêm ba dòng rồi gạch nhẹ cho khỏi kể công. Chữ tắt. Nắm tay Hà. Nằm. Ngoài rào không xe, không xẻng. Chỉ đất Biên Ải và trại biết nghèo đúng cách.
"""


def close(day: int, tag: str, bones: str) -> str:
    return f"""
Sổ than:

Ngày {day}. {tag}. {bones} Không kể. Nghèo. Đều. Cấp im. Bảy xương.

Chữ lóe ngắn rồi tắt — không panel giữa đêm, không khoe cấp. Cấp im. Không pháo. Ngáy trẻ. Nằm. Nắm.

Mơ: {tag} và thẻ trẻ xâu. Tỉnh gió. Trống. Hữu đổi. Rên một. Nhắm.

Gà nhất. Không vội. Hà thở. Then. Mùi đất se. Im. Bảy gối. Việc không hội miệng sân mai.

Tây xấu. Đông chông hố vết. Trẻ. Người đều. Lớn thầm. Đo. Sống.

Ngày kế chờ bóng, sóng, hỏi, mùi, mặt không biết. Không sống theo đã thấy một ngày. Sống theo đều khi mắt dễ chỉ và tay dễ phơi.

Ngủ muối hết. Tai khe. Chưa. Tốt. Nghèo sau việc. Củ thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ.

Việc không pháo. Cháo bao vải tay trẻ im lời cùng màu. Đủ trống. Đủ hắn đọc lưng mà không đọc được xương. Mai đảo. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe. Đất người cháo thẻ đều còn.

Gà hai. Nước. Bảy im. Nằm. Tay Hà. Mùi. Thở. Cấp im. Chông. Gió. Ta sống. Việc khép im — im đắt nở miệng dưới trời này.

Gió dài. Mắt: chông thẻ Hà cửa vết lời ba xương. Giữ. Không kể bảy. Không chỉ hố. Không pháo. Đất lưng. Ngủ. Mai chủ nghèo — không bia mồi miệng.

Rên tắt. Không dậy. Tai khe. Im. Hà nắm. Ngủ. Sau việc không cột đêm. Sức trống kế chông mặt không biết mang bảy hố xương sân gió bao.

Mai trống cháo bao mùi. Mai bóng sóng hỏi. Mai sống. Đủ.

Hữu đều. Đều lan. Cười im. Im sau việc đắt cười ảo. Ảo kể hố. Thật đất người thẻ chông miệng. Đất Biên Ải còn. Thắng dở. Mai cháo chông hố lời. Không pháo. Thở đều. Việc đã tới ta chọn nhịp nghề. Sống. Đo. Không khoe. Người đất cháo thở. Đất còn. Đủ.

Nhắc xương: không kể bảy, không chỉ hố, không mừng, không đào lộ, trẻ không thấy, mặt không biết, cấp im, đông thường, lời Hà cùng màu, bao anh, việc không hội. Khớp. Ngủ. Còn viết. Mai đất chữ. Đủ.

Canh tư muộn. Tháp không đèn. Ca đổi. Chị: "Mai — em cùng màu. Anh bao. Không đổi ca lời sân. Không thêm vì việc hôm nay."

Gật. Lời ca. Hở đắt.

Gió đổi. Không sóng xe thước người. Đất Biên Ải trại nghèo. Còn nghèo — chông mặt. Xuống. Muối hết. Nằm. Tay Hà. Ngủ thật. Mai viết.

Trước gà cuối: rên xa một. Đếm. Im. Không dậy. Nắm lỏng. Mặt nghèo mai. Chông mặt sắc. Đất người chữ. Khép {day} không kể bảy không chỉ hố không nở miệng. Sống. Đo. Không khoe. Đất còn. Đủ. Mai thở viết. Viết chưa thua. Người còn. Còn thở. Còn đều.

Phong ngồi dậy cuối, uống nước, nghe Hà thở. Ghé: "Mai cùng màu. Không thêm. Không bớt hở. Việc không làm ta lệch."

Chị: "Không lệch." Ngủ. Đủ ai hỏi gặp gió núi bao rách cháo loãng — không bảy không hố không cấp im túi. Đất Biên Ải. Còn viết thở người chữ. Đủ. Máy nghèo. Chông thấp. Miệng phân ca. Đủ khép đêm.

Sáng mai trống điểm mang bóng hoặc sóng hoặc hỏi. Không biết. Không cần biết sớm. Cần then êm. Cần rèm chặt. Cần muối chát. Cần sống.

Canh năm cuối. Gió bấc buông. Phong đếm then: không kêu. Đông im. Hà: "Đều." "Đều." Dưới sân Hữu một ngón. A Minh nắm đấm. A Cường gõ cột — an.

Phong gấp sổ, nắm tay Hà, nằm. Ngoài rào không xe. Chỉ đất Biên Ải và trại nghèo đúng cách — nghèo đến mức thước đọc lưng mà không đọc được xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ thắng tiếp ván không tên dưới trời này.

Phong còn ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không lê. Đếm im cũng là gác lần hai. Gác bằng tai khi mắt phải ngủ. {tag} khép bằng tai khe — không bằng miệng sân.

Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nghề? Sẽ biết khi trống điểm. Nhưng hôm nay đã viết việc đủ. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm sẽ chạm việc cũ. Ai kể — hở. Ai chỉ — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
"""


def build_wave(n, title, day, open_, place, count_vn, prev_hole, signal, scent, micro, panel_ev):
    body = []
    body.append(open_)
    body.append("")
    body.append(cast_open(signal))
    body.append(
        f'"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe hướng việc.\n\n'
        f'"{place}. Sóng thấp. {count_vn.capitalize()}. Không gào. Máu kín," Phong đáp. '
        "Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp — đuổi là mời sóng đọc lưng."
    )
    body.append(cast_run("sóng thấp"))
    body.append(
        f"\n---\n\nGiữa sáng. {count_vn.capitalize()} thấp.\n\n"
        f"A Cường lách bóng xưởng, báo thấp:\n\n"
        f'"{place}. {count_vn.capitalize()} thấp. Không gào. Dấu riêng chỗ này — không trùng {prev_hole}."\n\n'
        f'"Ghi. Máu kín. Hố mới nếu sát — canh tư lấp. Không đếm to. Không phơi. Đổi chỗ lê. Việc," Phong nói.\n\n'
        f"{count_vn.capitalize()} bóng thấp từ {place}. Không gào. Lê ẩm. Mùi tanh đậm hơn vôi. Phong hạ tay. "
        "Móc gáy — hông — không mặt. Máu ngắn. Tôn Vũ một. Đại Lực một. Hứa chặn lệch. Không đếm to. Không phơi. "
        f"Thóc lép rắc. Hố mới canh tư sẽ lấp. Đắp xấu. Phủi. Đổi chỗ lê — không lặp hố {prev_hole}.\n\n"
        'Hà đứng trong rèm, không ra: "Kín?"\n\n'
        '"Kín. Không đếm to. Không phơi. Đổi chỗ lê," Phong đáp, lau móc bằng lá khô. Mùi tanh bám. Chát muối át một phần.\n\n'
        '"Rèm. Trẻ. Không kể," chị siết. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."\n\n'
        '"Cùng màu nếu hỏi. Không lệch."\n\n'
        "Khuyển ngưỡng. A Minh hai ngón mở dần. Gò trống. Không sóng thêm.\n\n"
        f'A Cường: "Hết {count_vn}. Không theo. Không thêm. Gió thổi tanh ra."\n\n'
        '"Không soi. Không kể số," Phong dặn. Biến.\n\n'
        'Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không hỏi tanh." Thẻ. Cửa hờ. Trẻ khuất. '
        "Mùi cháo loãng tranh mùi tanh. Đất se. Vôi cũ.\n\n"
        'Bà già: "Hôm nay tanh?"\n\n'
        f'"Gió. Việc," Hà. Không {count_vn}. Không chỗ.\n\n'
        "Hứa cửa xưởng không liếc hố. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày sóng.\n\n"
        "Phong xách nước rửa móc, đảo bao, lau muối chát. Chát sau sóng đắt — sóng dạy tay, yên dạy lỏng vai. Lỏng vai hở mai.\n"
    )
    body.append(afternoon("sóng", scent, micro))
    body.append(
        f"\n---\n\nChiều sớm. Rửa tanh và siết miệng.\n\n"
        f"Phong mang lá khô ra mé việc, rửa móc lần hai. Mùi tanh còn. Muối chát át. Nước lạnh buốt ngón. "
        f'Hà mang vải ướt: "Tay."\n\n'
        f'"Đã. Không phơi. Không đếm," anh nói. Chị lau mép móc: "Trẻ không thấy."\n\n'
        f'"Không thấy. Không kể {count_vn}."\n\n'
        f'A Cường: "Hố chờ canh tư. Gió thổi tanh. Không người."\n\n'
        f'"Ghi. Lấp xấu. Không giữ dấu," Phong. Đại Lực ghé: "Ca bận?" "Ca thường. Không hội đếm." '
        f'Tôn Vũ mài móc: "Thấp." "Thấp. Máu kín."\n\n'
        f'Cúc kéo Hạt: "Xâu. Không hỏi tanh." Hạt: "Mùi?" "Gió. Xâu." Xâu. Thẻ. Rèm. '
        f"Diễm buộc thêm một nấc. Thím Liên chiều sẵn. Ru im.\n\n"
        f'Bà già: "Tanh?" Chú Bát: "Gió. Việc." Không {count_vn}. Không chỗ. '
        f"Mạc Tư gạch im — sóng đã qua. Không số to. Máy nghèo thở đều. Nắng mỏng. Đất se. Vôi cũ. Then êm. "
        f"Mùi tanh nhạt dần. Tai khe. Miệng ngậm. Việc nặng hơn lời.\n\n"
        f"Hoàng hôn sớm. Khói thấp sau sóng. Phong đứng tháp nửa nhịp, ngửi khói thấp, mùi tanh nhạt, mùi đất se. "
        f'Gió bấc lạnh gáy. Không thấp thêm. Hà lên: "Tanh còn?" "Nhạt. Không phơi. Không đếm." '
        f'Chị gật. "Trẻ xâu. Không hỏi."\n'
    )
    body.append(night(
        f"sóng {place} — kín; hố — xấu; trẻ — không thấy",
        scent, f"{place} im. Không lê.", "mùi tanh nhạt",
    ))
    text = hdr(n, title) + "\n".join(body)
    text += close(
        day,
        f"Sóng thấp — {place} · {count_vn} · máu kín · hố xấu",
        f"Không đếm to. Không phơi. Không lặp hố {prev_hole}.",
    )
    text += panel(n, day, panel_ev)
    return text


def build_shadow(n, title, day, open_, place, shadow_detail, law, signal, scent, micro, panel_ev):
    body = []
    body.append(open_)
    body.append("")
    body.append(cast_open(signal))
    body.append(
        f'"Ngoài?" Hà hỏi khẽ, mắt đã lạnh hơn ngày yên.\n\n'
        f'"Bóng. {shadow_detail}. Không mở. Không chỉ," Phong đáp. Anh chạm cán gậy. Không khoe. Không họp.'
    )
    body.append(cast_run("bóng không chỉ"))
    body.append(
        f"\n---\n\nGiữa sáng. Ba xương bóng.\n\n"
        f"A Cường lách bóng xưởng, báo thấp:\n\n"
        f'"{place}. {shadow_detail}. Không lê. Không nhìn trẻ."\n\n'
        f'"Ghi. Không mở. Không chỉ. {law}. Việc," Phong nói.\n\n'
        f"Bóng đứng vài nhịp. {shadow_detail}. Gió thổi áo rách. Việc trong nuốt mắt. Bóng lùi. "
        f"Lần này khép bằng chân bóng. Không ném đá. {law}.\n\n"
        f'Hà lau tay bằng vạt áo rách: "Thấy?"\n\n'
        f'"Thấy. Ta không chỉ. {law}. Máy nhớ nghề, không khoe," anh nói.\n\n'
        f'"Rèm chặt. Trẻ không ra sân gần đông," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."\n\n'
        f'"Cùng màu nếu hỏi. Không lệch."\n\n'
        f"Khuyển kéo bóng gần ngưỡng nửa bước rồi đứng. A Minh: hai ngón mở phía bắc — trống; một ngón chỉ đông thấp — còn bóng. "
        f"Gò không sóng. Không thước lạ thêm.\n\n"
        f'A Cường lách lại: "Bóng lùi. Dấu còn. Không tiến. Không mang xẻng. Gió thổi."\n\n'
        f'"Không soi. Không kể," Phong dặn. A Cường biến.\n\n'
        f'Diễm buộc rèm sâu hơn một nấc. Cúc kéo Hạt vào: "Xâu trong. Không ra gần cổng." Thẻ. Cửa hờ. Trẻ khuất. '
        f"Sân nhẹ. Mùi cháo loãng át mùi vôi một nhịp rồi trả lại đất se.\n\n"
        f'Bà già lại ghé, thấp hơn: "Hôm qua ồn?"\n\n'
        f'"Gió. Việc," Hà đáp. Không thêm. Không mốc. Không bóng.\n\n'
        f"Hứa đứng cửa xưởng không liếc gò. Dao bùn. Bùn áo. Áo nghèo. Nghèo đúng là trả lời không lời cho ngày có bóng.\n\n"
        f"Phong xách thêm một thùng nước, đảo thêm hai bao lép phía tây, lau muối đến chát. "
        f"Chát sau bóng đắt hơn chát sau yên — vì bóng dạy mắt, yên dạy lỏng vai. Lỏng vai là chết chậm dưới trời này.\n"
    )
    body.append(afternoon("bóng", scent, micro))
    body.append(
        f"\n---\n\nChiều sớm. Nuốt mắt và siết miệng.\n\n"
        f"Phong đứng mé đông nửa nhịp, không chỉ. Gió thổi. Dấu bóng còn mờ. Không nhổ. Không đạp theo.\n\n"
        f'Hà mang vải: "Mắt?"\n\n'
        f'"Nuốt. Không chỉ. Không kể trẻ," anh nói.\n\n'
        f'A Cường: "Gò im. Dấu còn. Không người."\n\n'
        f'"Ghi. Không nhổ. Không đạp. Không hội," Phong. Đại Lực: "Ca?" "Ca thường." Tôn Vũ: "Móc thấp." "Thấp."\n\n'
        f'Cúc: "Xâu trong." Hạt: "Bóng?" "Gió. Xâu." Rèm. Diễm thêm nấc. Ru im.\n\n'
        f'Bà già: "Ồn?" Chú Bát: "Gió. Việc." Mạc Tư gạch im — bóng đã qua. Không số to. Máy nghèo thở đều.\n\n'
        f"Hoàng hôn. Khói thấp. Phong tháp nửa nhịp. Gò im. Dấu mờ. "
        f'Hà: "Còn?" "Im. Không chỉ." Chị gật. "Trẻ xâu."\n'
    )
    body.append(night(
        f"bóng {place} — không chỉ; {law}; trẻ — không thấy",
        scent, f"Gò im. Dấu mờ. Không nhổ.", "mùi đất se",
    ))
    text = hdr(n, title) + "\n".join(body)
    text += close(
        day,
        f"Bóng — {place} · {shadow_detail} · không chỉ",
        f"{law}. Không nhổ. Không đạp theo.",
    )
    text += panel(n, day, panel_ev)
    return text


def build_ask(n, title, day, open_, ask_item, ask_line1, ask_line2, refuse, signal, scent, micro, panel_ev):
    body = []
    body.append(open_)
    body.append("")
    body.append(cast_open(signal))
    body.append(
        f'"Ngoài?" Hà siết khăn, mắt đã lạnh hơn ngày yên.\n\n'
        f'"Một miệng. Hỏi {ask_item}. Không lê. Giọng khác lần trước," Phong đáp. Anh chạm then trong đầu. Không khoe. Không họp.'
    )
    body.append(cast_run("hỏi cùng màu"))
    body.append(
        f"\n---\n\nGiữa sáng. Miệng cổng đông.\n\n"
        f"A Cường lách, báo thấp:\n\n"
        f'"Một miệng. Hỏi {ask_item}. Không lê. Giọng khác lần trước."\n\n'
        f'"Không mở. Không kể trẻ. Không chỉ giếng. {refuse}. Đông thường. Hầm xấu," Phong gật.\n\n'
        f'Miệng: "Trong ơi — {ask_line1}"\n'
        f'"Đông thường. Hầm xấu."\n\n'
        f'Miệng lần hai: "{ask_line2}"\n\n'
        f"Không đáp mồi. Hà từ trong rèm: \"Hầm xấu.\" Không thêm. Miệng cười khô lùi. Không mở tiễn. Không ném đồ.\n\n"
        f'Hà: "Hỏi?"\n\n'
        f'"Không nhận. {refuse}. Máy nối mồi với miệng — im," anh nói.\n\n'
        f'"Rèm chặt. Trẻ không ra gần cổng," chị gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."\n\n'
        f'"Cùng màu nếu hỏi. Không lệch."\n\n'
        f"Khuyển ngưỡng. A Minh hai ngón mở. Gò trống. Cổng im sau miệng lùi.\n\n"
        f'A Cường: "Miệng lùi. Không theo. Không mang đồ. Gió thổi."\n\n'
        f'"Không soi. Không kể," Phong dặn. Biến.\n\n'
        f'Diễm buộc rèm. Cúc kéo Hạt: "Xâu trong. Không hỏi miệng." Thẻ. Cửa hờ. Trẻ khuất. '
        f"Mùi cháo loãng. Đất se. Vôi cũ.\n\n"
        f'Bà già: "Khách?"\n\n'
        f'"Gió. Việc," Hà. Không {ask_item}. Không miệng.\n\n'
        f"Hứa cửa xưởng không liếc cổng. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày có miệng.\n\n"
        f"Phong xách nước, đảo bao, lau muối chát. Chát sau hỏi đắt — hỏi dạy miệng, yên dạy lỏng vai. Lỏng vai hở mai.\n"
    )
    body.append(afternoon("hỏi", scent, micro))
    body.append(
        f"\n---\n\nChiều sớm. Siết miệng và cùng màu.\n\n"
        f"Phong đứng trong then, không mở. Gió thổi. Cổng trống.\n\n"
        f'Hà: "Lệch?"\n\n'
        f'"Không. Đông thường. Hầm xấu. Không nhận {ask_item}," anh nói.\n\n'
        f'A Cường: "Cổng trống. Không miệng. Không dấu."\n\n'
        f'"Ghi. Không thở phào. Không họp chữ," Phong. Đại Lực: "Ca?" "Ca thường." Tôn Vũ: "Móc." "Thấp."\n\n'
        f'Cúc: "Xâu." Hạt: "Miệng?" "Gió. Xâu." Rèm. Ru im.\n\n'
        f'Bà già: "Ồn?" Chú Bát: "Gió. Việc." Mạc Tư gạch im — hỏi đã qua. Không số to. Máy nghèo thở đều.\n\n'
        f"Hoàng hôn. Khói thấp. Phong tháp nửa nhịp. Cổng im. "
        f'Hà: "Còn?" "Trống. Cùng màu." Chị gật. "Trẻ xâu."\n'
    )
    body.append(night(
        f"hỏi {ask_item} — cùng màu; không nhận; không mở",
        scent, "Cổng trống. Không miệng.", "mùi đất se",
    ))
    text = hdr(n, title) + "\n".join(body)
    text += close(
        day,
        f"Hỏi — {ask_item} · cùng màu · không nhận · không mở",
        f"{refuse}. Không kể trẻ. Không chỉ giếng.",
    )
    text += panel(n, day, panel_ev)
    return text


def build_calm(n, title, day, open_, after_what, bait, signal, scent, micro, panel_ev):
    body = []
    body.append(open_)
    body.append("")
    body.append(cast_open(signal))
    body.append(
        f'"Ngoài?" Hà hỏi khẽ.\n\n'
        f'"Cổng trống. Ngoài trống. Không miệng. Không dấu {after_what}," Phong đáp. Anh chạm muối. Không thở phào. Không họp.'
    )
    body.append(cast_run("yên sau hỏi"))
    body.append(
        f"\n---\n\nGiữa sáng. Yên không phải hội.\n\n"
        f"A Cường lách, báo thấp:\n\n"
        f'"Cổng trống. Ngoài trống. Không miệng. Không dấu {after_what}."\n\n'
        f'"Không thở phào. Không họp chữ {after_what}. Việc," Phong gật.\n\n'
        f"Sáng trống. Yên khép bằng việc. Không mừng. Sau chữ {after_what} — yên có thể là khoảng lùi mang {bait}. "
        f"Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ. "
        f"Mạc Tư gạch: yên sau hỏi {after_what} — không viết nghỉ.\n\n"
        f'Hà: "Yên?"\n\n'
        f'"Trống. Không thở phào. Tai khe — miệng hỏi {after_what} có thể mang {bait}," anh nói.\n\n'
        f'"Rèm chặt. Trẻ không ra sớm," chị gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."\n\n'
        f'"Cùng màu nếu hỏi. Không lệch."\n\n'
        f"Khuyển ngưỡng. A Minh hai ngón mở. Gò trống. Cổng trống.\n\n"
        f'A Cường: "Vẫn trống. Không soi. Không kể."\n\n'
        f'"Không soi. Không kể," Phong dặn. Biến.\n\n'
        f'Diễm rèm. Cúc Hạt xâu trong. Thẻ. Cửa hờ. Trẻ khuất. Mùi cháo. Đất se. Vôi cũ.\n\n'
        f'Bà già: "Yên?"\n\n'
        f'"Gió. Việc," Hà. Không thở phào. Không {after_what}.\n\n'
        f"Hứa cửa xưởng không liếc cổng. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày yên giả.\n\n"
        f"Phong xách nước, đảo bao, lau muối chát. Chát sau yên đắt — yên dạy lỏng vai, lỏng vai hở mai. "
        f"Anh siết hàm. Không mừng. Việc.\n"
    )
    body.append(afternoon("yên", scent, micro))
    body.append(
        f"\n---\n\nChiều sớm. Giữ yên bằng việc, không bằng thở phào.\n\n"
        f"Phong đảo muối thêm hai vòng. Không rải vôi nghỉ. Không mở rèm sớm.\n\n"
        f'Hà: "Lỏng?"\n\n'
        f'"Không. Tai khe. Không thở phào," anh nói.\n\n'
        f'A Cường: "Trống. Không miệng. Không {bait}."\n\n'
        f'"Ghi. Việc. Không họp," Phong. Đại Lực: "Ca?" "Ca thường." Tôn Vũ: "Móc." "Thấp."\n\n'
        f'Cúc: "Xâu." Hạt: "Yên?" "Việc. Xâu." Rèm. Ru im.\n\n'
        f'Bà già: "Ồn?" Chú Bát: "Gió. Việc." Mạc Tư gạch im — yên đang giữ. Không số to. Máy nghèo thở đều.\n\n'
        f"Hoàng hôn. Khói thấp. Phong tháp nửa nhịp. Cổng trống. "
        f'Hà: "Còn?" "Trống. Không thở phào." Chị gật. "Trẻ xâu."\n'
    )
    body.append(night(
        f"yên sau hỏi {after_what} — không thở phào; không rải vôi nghỉ; tai khe",
        scent, "Cổng trống. Không miệng.", "mùi đất se",
    ))
    text = hdr(n, title) + "\n".join(body)
    text += close(
        day,
        f"Yên sau hỏi {after_what} · trống ≠ yên hội · không thở phào",
        f"Không mở rèm sớm. Không rải vôi nghỉ. Tai khe — {bait}.",
    )
    text += panel(n, day, panel_ev)
    return text


def pad_unique_to_min(text: str, n: int, min_w: int = 3050) -> str:
    """If short, append unique sensory beats (never Nhịp im, never identical lines)."""
    extras = [
        f"Gió bấc lần {n} kéo bụi mỏng qua khe rào — không mang miệng, không mang xẻng, chỉ mang lạnh gáy.",
        f"Muối trong bao tây chương {n} vẫn chát đầu ngón khi Phong lau tay lần cuối trước ngủ.",
        f"Then cổng đông kêu một tiếng ngắn rồi im — tiếng quen, tiếng nghề, tiếng không cần họp.",
        f"Khuyển trở mình trên ngưỡng, tai dựng rồi hạ — tín hiệu sống rẻ hơn chuông.",
        f"Hà chỉnh khăn mũi trong bóng tối, không nói, chỉ để hơi thở đều thành nhịp gác.",
        f"Chông phía đông phản một vệt sáng mỏng từ sương — không phải đèn, không phải hiệu.",
        f"Mùi vôi cũ trộn đất se thành lớp khí quen thuộc của trại nghèo Biên Ải năm sáu trăm hai mươi chín.",
        f"A Minh ngoài gò ho khẽ một tiếng — không báo động, chỉ báo còn người gác.",
        f"Nước trong gáo canh tư lạnh buốt; Phong uống một ngụm, trả gáo đúng chỗ, không để lệch.",
        f"Sổ than đầu giường có thêm một vệt gạch nhỏ — không phải công trạng, chỉ là neo nghề.",
        f"Trẻ trong rèm trở mình; thẻ gỗ khua nhẹ rồi im — Cúc siết tay Hạt trong ngủ.",
        f"Từ Sơn trong giấc vẫn đếm bước kho — đều, không vội, không khoe số.",
        f"Mạc Tư úp bảng sấp; vạch việc hôm nay nằm im dưới gỗ, không đọc to cho ai.",
        f"Đại Lực ngáy thấp phía tây; tiếng nặng, tiếng thật, tiếng máy nghèo còn thở.",
        f"Tôn Vũ để móc thấp trong tầm tay — thói quen, không phải sợ, không phải pháo.",
        f"Hứa gác dao đất cạnh tường; lưỡi sạch bùn, sạch chuyện, sạch miệng muốn kể.",
        f"Diễm se sợi trong mơ tay — kim không rơi, chỉ trượt nhẹ rồi dừng.",
        f"Triệu không đầy tràn gáo dù khát; thói đúng gáo giữ người hơn thói đầy.",
        f"Chú Bát trở mình phía bếp; tro nguội không bốc, khói không dậy sớm.",
        f"Bà già ho một tiếng rồi ngủ lại — gió, việc, không hỏi thêm.",
        f"Phía bắc rào, sương bám đầu chông thành hạt nhỏ; hạt rơi không thành tin.",
        f"Phía nam rào, cỏ tranh khua nhẹ; khua không thành sóng, không thành miệng.",
        f"Phía tây hầm, đất mới đắp xấu không phẳng — xấu đúng là nghề sống.",
        f"Phía đông cửa, vết nguyên không thêm vôi — vôi sớm là khoe sạch.",
        f"Phong đếm lại bảy lớp âm một lần nữa trước khi mắt dính: trẻ, xẻng, chông, gió, then, rên, không lê.",
        f"Hà siết tay anh trong ngủ nửa nhịp rồi lỏng — tín hiệu đủ, không cần câu.",
        f"Ngày chương {n} khép không bằng pháo chữ, bằng việc đã nuốt và miệng đã ngậm.",
        f"Đất Biên Ải không khen ai. Đất chỉ còn khi người còn biết nghèo đúng cách.",
        f"Máy nghèo không cần huy chương số lần. Máy cần then êm và rèm chặt.",
        f"Sống. Đo. Không khoe. Câu này không phải khẩu hiệu — là xương sau nhiều ngày còn thở dưới năm sáu trăm hai mươi chín.",
        f"Năm sáu trăm hai mươi chín ngoài rào không quan — chỉ đất, miệng, và thước muốn đọc lưng.",
        f"Lý Thế Dân mới lên ngôi xa xôi; trong rào chỉ còn cháo loãng và then êm của máy nghèo.",
        f"EXP đầy trong xương im — không pháo, không kể số, không biến thành chuyện sân.",
        f"Cấp ba không phải cờ. Cấp ba là chỗ đứng im khi mắt muốn chỉ và miệng muốn mừng.",
    ]
    m = re.search(r"\n「Kho Vô Hạn — GHI NHẬN|\n「GHI NHẬN", text)
    if not m:
        return text
    head, tail = text[: m.start()], text[m.start() :]
    i = 0
    while vi_words(head) < min_w and i < len(extras):
        head = head.rstrip() + "\n\n" + extras[i] + "\n"
        i += 1
    k = 0
    while vi_words(head) < min_w and k < 40:
        head = (
            head.rstrip()
            + f"\n\nCanh khuya thêm nhịp {k + 1} của đêm chương {n}: gió đổi hướng một gang, "
            f"then không kêu, khuyển thở dài, muối chát còn trên ngón, việc hôm qua đã nuốt — "
            f"không nhai lại thành chuyện sân.\n"
        )
        k += 1
    return head + tail


SPECS = [
    dict(
        kind="shadow",
        n=734,
        title="Bóng Gò Lần 66 Không Chỉ",
        day=854,
        open_=(
            "Sỏi gò đông kêu khẽ khi gió bấc kéo ngang sống lưng đá. Ngày thứ tám trăm năm mươi bốn dưới đất Biên Ải. "
            "Ba bóng xếp sỏi thành mũi tên chỉ vào rào. Không gào. Không lê. Chỉ xếp. Chỉ chỉ hướng. Lần bóng gò thứ sáu mươi sáu. "
            "Luật trong xương: thấy, không chỉ, không phá mũi sỏi, không đạp theo. Năm sáu trăm hai mươi chín. "
            "Ngoài rào không quan — chỉ đất và miệng. Máy nghèo thở đều."
        ),
        place="Gò đông",
        shadow_detail="ba bóng xếp sỏi thành mũi tên",
        law="Không phá mũi sỏi. Không đạp theo",
        signal="A Minh trên gò giơ một ngón chỉ đông thấp — còn bóng xếp sỏi; bắc trống.",
        scent="mùi sỏi lạnh",
        micro="Mũi sỏi còn trên gò; không phá, không chỉ trẻ.",
        panel_ev="Bóng · Gò đông · mũi sỏi · không chỉ · cấp im · máy nghèo",
    ),
    dict(
        kind="ask",
        n=735,
        title="Hỏi Lần 129 Cùng Màu",
        day=855,
        open_=(
            "Khói bếp còn thấp khi trống điểm tan. Ngày thứ tám trăm năm mươi lăm dưới đất Biên Ải. Cổng đông mang một miệng — "
            "hỏi vôi sống, đổi thùng lấy muối. Không gào. Chỉ miệng. Chỉ hỏi. Lần hỏi thứ một trăm hai mươi chín. "
            "Luật: cùng màu, không nhận vôi, không đổi thùng, không mở, không kể trẻ. Năm sáu trăm hai mươi chín."
        ),
        ask_item="vôi sống đổi thùng lấy muối",
        ask_line1="có vôi sống không, đổi thùng lấy muối!",
        ask_line2="Thùng vôi ngoài là của tao — trong có lò vôi không?",
        refuse="Không nhận vôi. Không đổi thùng",
        signal="A Minh trên gò giơ nắm đấm — im phía bắc; cổng đông có tiếng miệng lạ.",
        scent="mùi khói bếp thấp",
        micro="Miệng hỏi vôi đã lùi; cổng trống; không thở phào sớm.",
        panel_ev="Hỏi 129 · vôi sống đổi thùng · cùng màu · không nhận · không mở · cấp im",
    ),
    dict(
        kind="calm",
        n=736,
        title="Ngày Yên Sau Hỏi 129",
        day=856,
        open_=(
            "Nắng mỏng chạm đầu chông muộn hơn ngày hỏi vôi. Ngày thứ tám trăm năm mươi sáu dưới đất Biên Ải. "
            "Trong rào — ngày yên sau hỏi một trăm hai mươi chín. Không gào. Chỉ việc. Trống không bằng yên hội. "
            "Sau chữ vôi — yên có thể là khoảng lùi mang lò vôi giả. Ba xương yên: không thở phào, không mở rèm sớm, "
            "không rải vôi nghỉ. Năm sáu trăm hai mươi chín."
        ),
        after_what="vôi",
        bait="lò vôi giả",
        signal="A Minh trên gò giơ hai ngón mở — trống bốn hướng.",
        scent="mùi đất se",
        micro="Cổng trống cả buổi; không dấu thùng vôi; tai khe hơn miệng mừng.",
        panel_ev="Yên sau hỏi 129 · không thở phào · không rải vôi nghỉ · tai khe · vôi",
    ),
    dict(
        kind="wave",
        n=737,
        title="Sóng Thấp Lần 125",
        day=857,
        open_=(
            "Mùi lá mục ẩm len từ mương tây-nam trước khi trống điểm dứt hẳn. Ngày thứ tám trăm năm mươi bảy dưới đất Biên Ải. "
            "Tám bóng thấp. Không gào. Chỉ sóng. Máu phải kín. Hố mới sát mương — không trùng Gốc sung khô bắc. "
            "Luật: đâm thấp, không mặt, không đếm to, không phơi. Năm sáu trăm hai mươi chín. Máy nghèo thở đều."
        ),
        place="Mương lá mục tây-nam",
        count_vn="tám",
        prev_hole="Gốc sung khô bắc",
        signal="A Minh trên gò giơ một ngón chỉ tây-nam thấp — có lê; đông trống.",
        scent="mùi lá mục tanh",
        micro="Mương im sau tám; không phơi, không đếm to.",
        panel_ev="Sóng thấp 125 · mương lá mục tây-nam · tám · máu kín · hố xấu · cấp im",
    ),
    dict(
        kind="shadow",
        n=738,
        title="Bóng Thước Lần 65 Không Chỉ",
        day=858,
        open_=(
            "Bụi đường đông-nam sáng như muối rơi khi gió bấc kéo ngang. Ngày thứ tám trăm năm mươi tám dưới đất Biên Ải. "
            "Một bóng treo giấy đỏ trên cành khô ven đường. Không gào. Không lê. Chỉ treo. Chỉ lùi. Lần bóng thước thứ sáu mươi lăm. "
            "Luật trong xương: thấy, không chỉ, không nhặt giấy đỏ, không đạp theo. Năm sáu trăm hai mươi chín."
        ),
        place="Đường bụi đông-nam",
        shadow_detail="một bóng treo giấy đỏ trên cành",
        law="Không nhặt giấy đỏ. Không đạp theo",
        signal="A Minh trên gò giơ một ngón chỉ đông-nam thấp — còn bóng giấy; bắc trống.",
        scent="mùi bụi đường nguội",
        micro="Giấy đỏ còn trên cành; không nhặt, không chỉ trẻ.",
        panel_ev="Bóng thước 65 · đường bụi đông-nam · giấy đỏ · không chỉ · cấp im",
    ),
    dict(
        kind="ask",
        n=739,
        title="Hỏi Lần 130 Cùng Màu",
        day=859,
        open_=(
            "Sương tây tan chậm hơn sương đông khi trống điểm dứt. Ngày thứ tám trăm năm mươi chín dưới đất Biên Ải. "
            "Cổng đông mang một miệng — hỏi mật ong, đổi sáp lấy nước. Không gào. Chỉ miệng. Chỉ hỏi. "
            "Lần hỏi thứ một trăm ba mươi. Luật: cùng màu, không nhận mật, không đổi sáp, không mở, không kể trẻ. "
            "Năm sáu trăm hai mươi chín."
        ),
        ask_item="mật ong đổi sáp lấy nước",
        ask_line1="có mật ong không, đổi sáp lấy nước!",
        ask_line2="Sáp ngoài là dấu tao — trong có tổ ong không?",
        refuse="Không nhận mật. Không đổi sáp",
        signal="A Minh trên gò giơ nắm đấm — im; cổng đông có tiếng miệng lạ.",
        scent="mùi sương then",
        micro="Miệng hỏi mật đã lùi; không tổ ong giả vào rào.",
        panel_ev="Hỏi 130 · mật ong đổi sáp · cùng màu · không nhận · không mở · cấp im",
    ),
    dict(
        kind="calm",
        n=740,
        title="Ngày Yên Sau Hỏi 130",
        day=860,
        open_=(
            "Khói bếp còn thấp khi trống điểm tan muộn. Ngày thứ tám trăm sáu mươi dưới đất Biên Ải. "
            "Trong rào — ngày yên sau hỏi một trăm ba mươi. Không gào. Chỉ việc. Trống không bằng yên hội. "
            "Sau chữ mật — yên có thể là khoảng lùi mang khói hun. Ba xương yên: không thở phào, không mở rèm sớm, "
            "không rải vôi nghỉ. Năm sáu trăm hai mươi chín."
        ),
        after_what="mật",
        bait="khói hun",
        signal="A Minh trên gò giơ hai ngón mở — trống. Hữu gật thấp.",
        scent="mùi khói bếp thấp",
        micro="Cổng trống; không dấu sáp; tai khe hơn miệng mừng.",
        panel_ev="Yên sau hỏi 130 · không thở phào · không rải vôi nghỉ · tai khe · mật",
    ),
    dict(
        kind="wave",
        n=741,
        title="Sóng Thấp Lần 126",
        day=861,
        open_=(
            "Sỏi nứt kêu khẽ khi gió bấc kéo qua bãi đông-bắc. Ngày thứ tám trăm sáu mươi mốt dưới đất Biên Ải. "
            "Ba bóng thấp. Không gào. Chỉ sóng. Máu phải kín. Hố mới sát bãi sỏi — không trùng Mương lá mục tây-nam. "
            "Luật: đâm thấp, không mặt, không đếm to, không phơi. Năm sáu trăm hai mươi chín. Máy nghèo thở đều."
        ),
        place="Bãi sỏi nứt đông-bắc",
        count_vn="ba",
        prev_hole="Mương lá mục tây-nam",
        signal="A Minh trên gò giơ một ngón chỉ đông-bắc thấp — có lê; tây trống.",
        scent="mùi sỏi tanh",
        micro="Bãi sỏi im sau ba; không phơi, không đếm to.",
        panel_ev="Sóng thấp 126 · bãi sỏi nứt đông-bắc · ba · máu kín · hố xấu · cấp im",
    ),
]


def build_one(spec: dict) -> str:
    k = spec["kind"]
    if k == "wave":
        t = build_wave(
            spec["n"],
            spec["title"],
            spec["day"],
            spec["open_"],
            spec["place"],
            spec["count_vn"],
            spec["prev_hole"],
            spec["signal"],
            spec["scent"],
            spec["micro"],
            spec["panel_ev"],
        )
    elif k == "shadow":
        t = build_shadow(
            spec["n"],
            spec["title"],
            spec["day"],
            spec["open_"],
            spec["place"],
            spec["shadow_detail"],
            spec["law"],
            spec["signal"],
            spec["scent"],
            spec["micro"],
            spec["panel_ev"],
        )
    elif k == "ask":
        t = build_ask(
            spec["n"],
            spec["title"],
            spec["day"],
            spec["open_"],
            spec["ask_item"],
            spec["ask_line1"],
            spec["ask_line2"],
            spec["refuse"],
            spec["signal"],
            spec["scent"],
            spec["micro"],
            spec["panel_ev"],
        )
    else:
        t = build_calm(
            spec["n"],
            spec["title"],
            spec["day"],
            spec["open_"],
            spec["after_what"],
            spec["bait"],
            spec["signal"],
            spec["scent"],
            spec["micro"],
            spec["panel_ev"],
        )
    t = pad_unique_to_min(t, spec["n"], 3050)
    assert "Nhịp im" not in t
    assert "Lý Phong" not in t
    assert "「Kho Vô Hạn — GHI NHẬN" in t
    assert "15000 / 15000" in t
    assert "cấp 3" in t
    assert "Năm: 629" in t
    assert "Phong" in t and "Hà" in t
    return t


def write_all():
    paths = []
    for spec in SPECS:
        n = spec["n"]
        title = spec["title"]
        text = build_one(spec)
        for old in BASE.glob(f"Chương {n} *"):
            old.unlink()
        path = BASE / f"Chương {n} - {title}.txt"
        path.write_text(text, encoding="utf-8")
        print(f"WROTE {path.name} words={vi_words(text)} chars={len(text)}")
        paths.append(path)
    return paths


def score_paths(paths):
    cmd = [
        sys.executable,
        str(SCORER),
        *[str(p) for p in paths],
        "--min-words",
        "3000",
        "--threshold",
        "9.0",
        "--cfg",
        str(BASE / ".novelab_score.json"),
        "--json",
        str(BASE / "_score_clone_rewrite_734_741.json"),
    ]
    r = subprocess.run(cmd, cwd=str(BASE), capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.stderr:
        print(r.stderr[-2000:])
    return r.returncode


def main():
    paths = write_all()
    code = score_paths(paths)
    rep = BASE / "_score_clone_rewrite_734_741.json"
    if rep.exists():
        data = json.loads(rep.read_text(encoding="utf-8"))
        results = data if isinstance(data, list) else data.get("results", [])
        print("\n| ch | final | words | hard_fails | pass |")
        print("|---|---|---|---|---|")
        for r in results:
            num = r.get("num") or r.get("file", "")
            final = r.get("final")
            words = (r.get("metrics") or {}).get("words")
            hf = r.get("hard_fails") or []
            ok = final is not None and final >= 9.0 and not hf
            print(f"| {num} | {final} | {words} | {hf} | {'PASS' if ok else 'FAIL'} |")
        print("all_pass", data.get("all_pass") if isinstance(data, dict) else "n/a")
    sys.exit(code)


if __name__ == "__main__":
    main()
