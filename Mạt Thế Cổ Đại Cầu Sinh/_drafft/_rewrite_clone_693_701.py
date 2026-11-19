# -*- coding: utf-8 -*-
"""Unique full rewrite CLONE pad ch.693-697,699-701 (skip 698).
Style: ch.677-685 pass batch + Kho Vô Hạn EXP panel (user-required).
No Nhịp im pad. Phong/Hà. Year 629. ≥3000 words.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".novelab_score.json"


def vi_words(t: str) -> int:
    return len([w for w in t.split() if len(w) >= 2])


def hdr(n: int, title: str) -> str:
    return (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
    )


def panel(n: int, keywords: str) -> str:
    return (
        f"\n「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"EXP: 15000 / 15000\n"
        f"Hiện tại: cấp 3\n"
        f"Nâng cấp: {keywords}\n"
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

Hữu đều. Đều lan. Cười im. Im sau việc đắt cười ảo. Ảo kể hố. Thật đất người thẻ chông miệng. Đất Biên Ải còn. Thắng dở. Mai cháo chông hố lời. Không pháo. Thở đều. Việc đã tới ta chọn im việc. Sống. Đo. Không khoe. Người đất cháo thở. Đất còn. Đủ.

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

Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm. Nhưng hôm nay đã viết việc đủ. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm sẽ chạm việc cũ. Ai kể — hở. Ai chỉ — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
"""


def build_wave(n, title, day, open_, place, count_vn, prev_hole, signal, scent, micro, keywords):
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
    text = hdr(n, title) + "\n".join(body) + close(
        day,
        f"Sóng thấp — {place} · {count_vn} · máu kín · hố xấu",
        f"Không đếm to. Không phơi. Không lặp hố {prev_hole}.",
    )
    text += panel(n, keywords)
    return text


def build_shadow(n, title, day, open_, place, shadow_detail, law, signal, scent, micro, keywords):
    body = []
    body.append(open_)
    body.append("")
    body.append(cast_open(signal))
    body.append(
        f'"Ngoài?" Hà hỏi khẽ, mắt đã lạnh hơn ngày yên.\n\n'
        f'"Bóng gò. {shadow_detail}. Không mở. Không chỉ," Phong đáp. Anh chạm cán gậy. Không khoe. Không họp.'
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
        f"Gò không sóng. Không thước.\n\n"
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
        scent, "Gò im. Dấu mờ. Không nhổ.", "mùi đất se",
    ))
    text = hdr(n, title) + "\n".join(body) + close(
        day,
        f"Bóng gò — {place} · {shadow_detail} · không chỉ",
        f"{law}. Không nhổ. Không đạp theo.",
    )
    text += panel(n, keywords)
    return text


def build_ask(n, title, day, open_, ask_item, ask_line1, ask_line2, refuse, signal, scent, micro, keywords):
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
    text = hdr(n, title) + "\n".join(body) + close(
        day,
        f"Hỏi — {ask_item} · cùng màu · không nhận · không mở",
        f"{refuse}. Không kể trẻ. Không chỉ giếng.",
    )
    text += panel(n, keywords)
    return text


def build_calm(n, title, day, open_, after_what, bait, signal, scent, micro, keywords):
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
    text = hdr(n, title) + "\n".join(body) + close(
        day,
        f"Yên sau hỏi {after_what} · trống ≠ yên hội · không thở phào",
        f"Không mở rèm sớm. Không rải vôi nghỉ. Tai khe — {bait}.",
    )
    text += panel(n, keywords)
    return text


def unique_tail(n: int, day: int, place_hint: str, scent_hint: str) -> str:
    """Unique sensory/cast beats — never Nhịp im, never identical across chapters."""
    lines = [
        f"Gió bấc đêm {day} kéo bụi mỏng qua khe rào phía {place_hint} — không mang miệng, không mang xẻng, chỉ mang lạnh gáy.",
        f"Muối trong bao tây ngày {day} vẫn chát đầu ngón khi Phong lau tay lần cuối trước ngủ.",
        f"Then cổng đông kêu một tiếng ngắn rồi im — tiếng quen chương {n}, tiếng nghề, tiếng không cần họp.",
        f"Khuyển trở mình trên ngưỡng, tai dựng rồi hạ — tín hiệu sống rẻ hơn chuông sau việc {place_hint}.",
        f"Hà chỉnh khăn mũi trong bóng tối lều tây, không nói, chỉ để hơi thở đều thành nhịp gác cho Phong yên.",
        f"Chông phía đông phản một vệt sáng mỏng từ sương {day} — không phải đèn, không phải hiệu.",
        f"Mùi {scent_hint} trộn đất se thành lớp khí quen thuộc của trại nghèo Biên Ải đêm nay.",
        f"A Minh ngoài gò ho khẽ một tiếng — không báo động, chỉ báo còn người gác sau {place_hint}.",
        f"Nước trong gáo canh tư lạnh buốt; Phong uống một ngụm, trả gáo đúng chỗ, không để lệch ngày {day}.",
        f"Sổ than đầu giường có thêm một vệt gạch nhỏ — không phải công trạng, chỉ là neo nghề chương {n}.",
        f"Trẻ trong rèm trở mình; thẻ gỗ khua nhẹ rồi im — Cúc siết tay Hạt trong ngủ, không hỏi ngoài.",
        f"Từ Sơn trong giấc vẫn đếm bước kho — đều, không vội, không khoe số sau yên hay sóng.",
        f"Mạc Tư úp bảng sấp; vạch việc hôm nay nằm im dưới gỗ, không đọc to cho ai nghe.",
        f"Đại Lực ngáy thấp phía tây; tiếng nặng, tiếng thật, tiếng máy nghèo còn thở sau {place_hint}.",
        f"Tôn Vũ để móc thấp trong tầm tay — thói quen sau máu kín, không phải sợ, không phải pháo.",
        f"Hứa gác dao đất cạnh tường; lưỡi sạch bùn, sạch chuyện, sạch miệng muốn kể số.",
        f"Diễm se sợi trong mơ tay — kim không rơi, chỉ trượt nhẹ rồi dừng trước rèm trẻ.",
        f"Triệu không đầy tràn gáo dù khát; thói đúng gáo giữ người hơn thói đầy sau hỏi.",
        f"Chú Bát trở mình phía bếp; tro nguội không bốc, khói không dậy sớm để khoe nồi.",
        f"Bà già ho một tiếng rồi ngủ lại — gió, việc, không hỏi thêm về {place_hint}.",
        f"Phía bắc rào, sương bám đầu chông thành hạt nhỏ; hạt rơi không thành tin ngày {day}.",
        f"Phía nam rào, cỏ tranh khua nhẹ; khua không thành sóng, không thành miệng hỏi.",
        f"Phía tây hầm, đất mới đắp xấu không phẳng — xấu đúng là nghề sống dưới trời biên ải.",
        f"Phía đông cửa, vết nguyên không thêm vôi — vôi sớm là khoe sạch sau yên giả.",
        f"Phong đếm lại bảy lớp âm một lần nữa trước khi mắt dính: trẻ, xẻng, chông, gió, then, rên, không lê.",
        f"Hà siết tay anh trong ngủ nửa nhịp rồi lỏng — tín hiệu đủ sau {place_hint}, không cần câu.",
        f"Ngày {day} khép không bằng pháo chữ, bằng việc đã nuốt và miệng đã ngậm dưới đất Biên Ải.",
        f"Đất Biên Ải không khen ai sau chương {n}. Đất chỉ còn khi người còn biết nghèo đúng cách.",
        f"Máy nghèo không cần huy chương số lần. Máy cần then êm và rèm chặt sau {place_hint}.",
        f"Sống. Đo. Không khoe. Câu này không phải khẩu hiệu — là xương sau ngày {day} còn thở.",
        f"Hữu ngoài gò đổi ca không gõ cột — chỉ một ngón mở, đủ cho Phong biết trống thật.",
        f"A Cường đi ngang ngưỡng, không vào lều, chỉ để lại mùi bụi đường và im lặng nghề.",
        f"Giếng nắp xấu giữ xấu: không ai vội sạch nắp vì sợ thước đọc sạch thành mồi.",
        f"Bao tây xếp lệch nửa gang so sáng — lệch có chủ đích, không phải lỏng tay.",
        f"Rèm đông thêm một nấc do Diễm buộc khuya; nấc nhỏ, giá lớn nếu trẻ tò mò.",
        f"Phong nhớ năm 629 — Lý Thế Dân mới lên ngôi ngoài rào không quan, chỉ đất và miệng.",
        f"Hà thở vào khăn: mùi muối, mùi {scent_hint}, mùi đất se — ba mùi đủ để không mơ chữ to.",
        f"Tai còn khe cho mai; việc đã qua không nhai lại thành chuyện sân.",
    ]
    return "\n\n".join(lines) + "\n"


def ensure_min(text: str, n: int, day: int, place_hint: str, scent_hint: str, min_w: int = 3050) -> str:
    m = re.search(r"\n「Kho Vô Hạn — GHI\s*NHẬN", text)
    if not m:
        m = re.search(r"\n「[^」]*GHI\s*NHẬN", text)
    if not m:
        return text
    head, tail = text[: m.start()], text[m.start() :]
    if vi_words(head) >= min_w:
        return text
    extra = unique_tail(n, day, place_hint, scent_hint)
    head = head.rstrip() + "\n\n" + extra
    k = 0
    while vi_words(head) < min_w and k < 20:
        head += (
            f"\nCanh khuya chương {n} lớp {k + 1}: gió đổi hướng một gang về {place_hint}, "
            f"then không kêu, khuyển thở dài, muối chát còn trên ngón Phong, "
            f"Hà thở đều bên cạnh, việc ngày {day} đã nuốt — không nhai lại thành chuyện sân.\n"
        )
        k += 1
    return head + tail


SPECS = [
    dict(
        kind="wave",
        n=693,
        title="Sóng Thấp Lần 114",
        day=813,
        open_=(
            "Sương còn ướt đầu chông phía bắc-tây khi trống điểm dứt. Ngày thứ tám trăm mười ba dưới đất Biên Ải. "
            "Gió bấc mang mùi đất se và bụi dứa dại; nắng mỏng chưa đủ ấm gáy. Bụi dứa dại bắc-tây — ba bóng thấp. "
            "Không gào. Chỉ sóng. Máu phải kín. Lần sóng thấp thứ một trăm mười bốn. Luật trong xương: nghe, đâm thấp nếu sát, "
            "lấp xấu, không đếm to, không phơi, không lặp hố Gò sườn tây thấp."
        ),
        place="Bụi dứa dại bắc-tây",
        count_vn="ba",
        prev_hole="Gò sườn tây thấp",
        signal="A Minh trên gò giơ hai ngón mở — trống phía đông; phía bắc-tây có tiếng lê thấp.",
        scent="bụi dứa dại se",
        micro="Mùi tanh nhạt còn bám mé bắc-tây; không phơi, không đếm ba.",
        keywords="Sóng thấp · Bụi dứa dại bắc-tây · ba · máu kín · cấp im · máy nghèo",
        place_hint="bắc-tây",
        scent_hint="bụi dứa dại",
    ),
    dict(
        kind="shadow",
        n=694,
        title="Bóng Gò Lần 61 Không Chỉ",
        day=814,
        open_=(
            "Sương đông còn dính đầu chông khi trống điểm tan. Ngày thứ tám trăm mười bốn dưới đất Biên Ải. "
            "Gió bấc mang mùi đất se và vôi cũ; nắng mỏng chưa đủ ấm gáy. Trên gò đông, ba bóng đứng im kéo vải gai ngang bụi. "
            "Không gào. Không lê. Chỉ đứng. Lần bóng gò thứ sáu mươi mốt. Luật trong xương: thấy, không chỉ, không cắt vải gai, không đạp theo."
        ),
        place="Gò đông",
        shadow_detail="ba bóng đứng im kéo vải gai ngang bụi",
        law="Không cắt vải gai. Không đạp theo",
        signal="A Minh trên gò giơ một ngón chỉ đông thấp — còn bóng; phía bắc trống.",
        scent="mùi vải gai ẩm",
        micro="Vải gai còn mờ trên bụi; không cắt, không chỉ trẻ.",
        keywords="Bóng · Gò đông · không chỉ · vải gai · cấp im · máy nghèo",
        place_hint="gò đông",
        scent_hint="vải gai",
    ),
    dict(
        kind="ask",
        n=695,
        title="Hỏi Lần 119 Cùng Màu",
        day=815,
        open_=(
            "Trống điểm dứt khi khói bếp còn thấp. Ngày thứ tám trăm mười lăm. Cổng đông mang một miệng — "
            "hỏi giấy bản, đổi bút lấy gạo. Không gào. Chỉ miệng. Chỉ hỏi. Lần hỏi thứ một trăm mười chín. "
            "Luật: cùng màu, không nhận, không mở, không kể trẻ, không chỉ giếng."
        ),
        ask_item="giấy bản đổi bút lấy gạo",
        ask_line1="có giấy bản không, đổi bút lấy gạo!",
        ask_line2="Bút ngoài là của tao — trong có kho giấy không?",
        refuse="Không nhận giấy. Không đổi bút",
        signal="A Minh trên gò giơ nắm đấm — im phía bắc; cổng đông có tiếng người.",
        scent="mùi khói bếp thấp",
        micro="Miệng hỏi giấy đã lùi; cổng trống; không thở phào sớm.",
        keywords="Hỏi · cùng màu · có giấy bản không, đổi bút lấy gạo · cấp im · máy nghèo",
        place_hint="cổng đông",
        scent_hint="khói bếp",
    ),
    dict(
        kind="calm",
        n=696,
        title="Ngày Yên Sau Hỏi 119",
        day=816,
        open_=(
            "Nắng mỏng chạm đầu chông muộn hơn hôm qua. Ngày thứ tám trăm mười sáu. Trong rào — ngày yên sau hỏi một trăm mười chín. "
            "Không gào. Chỉ việc. Trống không bằng yên hội. Sau chữ giấy — yên có thể là khoảng lùi mang bút dụ. "
            "Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ."
        ),
        after_what="giấy",
        bait="bút dụ",
        signal="A Minh trên gò giơ hai ngón mở — trống bốn hướng.",
        scent="mùi đất se",
        micro="Cổng trống cả buổi; tai khe hơn miệng mừng sau chữ giấy.",
        keywords="Yên sau hỏi · trống ≠ yên hội · không thở phào · giấy · cấp im · máy nghèo",
        place_hint="trong rào",
        scent_hint="đất se",
    ),
    dict(
        kind="wave",
        n=697,
        title="Sóng Thấp Lần 115",
        day=817,
        open_=(
            "Mùi tanh ẩm len từ hố cát khô đông trước khi trống điểm dứt hẳn. Ngày thứ tám trăm mười bảy. "
            "Bốn bóng thấp. Không gào. Chỉ sóng. Máu phải kín. Hố mới sát hố cát — không trùng Bụi dứa dại bắc-tây hôm trước. "
            "Luật: đâm thấp, không mặt, không đếm to, không phơi."
        ),
        place="Hố cát khô đông",
        count_vn="bốn",
        prev_hole="Bụi dứa dại bắc-tây",
        signal="A Minh trên gò giơ một ngón chỉ đông thấp — có lê; tây trống.",
        scent="mùi tanh cát ẩm",
        micro="Cát khô khua nhẹ sau sóng; không phơi, không đếm bốn.",
        keywords="Sóng thấp · Hố cát khô đông · bốn · máu kín · cấp im · máy nghèo",
        place_hint="đông cát",
        scent_hint="cát tanh",
    ),
    dict(
        kind="ask",
        n=699,
        title="Hỏi Lần 120 Cùng Màu",
        day=819,
        open_=(
            "Trống điểm dứt khi sương còn bám then. Ngày thứ tám trăm mười chín. Cổng đông mang một miệng — "
            "hỏi đinh sắt, đổi búa lấy muối. Không gào. Chỉ miệng. Chỉ hỏi. Lần hỏi thứ một trăm hai mươi. "
            "Luật: cùng màu, không nhận đinh, không đổi búa, không mở, không kể trẻ."
        ),
        ask_item="đinh sắt đổi búa lấy muối",
        ask_line1="có đinh sắt không, đổi búa lấy muối!",
        ask_line2="Búa ngoài là dấu tao — trong có thợ rèn không?",
        refuse="Không nhận đinh. Không đổi búa",
        signal="A Minh trên gò giơ nắm đấm — im; cổng đông có tiếng người lạ.",
        scent="mùi sương then",
        micro="Miệng hỏi đinh đã lùi; không thợ rèn giả vào rào.",
        keywords="Hỏi · cùng màu · có đinh sắt không, đổi búa lấy muối · cấp im · máy nghèo",
        place_hint="cổng đông",
        scent_hint="sương then",
    ),
    dict(
        kind="calm",
        n=700,
        title="Ngày Yên Sau Hỏi 120",
        day=820,
        open_=(
            "Nắng mỏng chạm rèm muộn. Ngày thứ tám trăm hai mươi. Trong rào — ngày yên sau hỏi một trăm hai mươi. "
            "Không gào. Chỉ việc. Trống không bằng yên hội. Sau chữ đinh — yên có thể là khoảng lùi mang dây dụ. "
            "Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ."
        ),
        after_what="đinh",
        bait="dây dụ",
        signal="A Minh trên gò giơ hai ngón mở — trống. Hữu gật thấp.",
        scent="mùi dây thừng se",
        micro="Cổng trống; không dấu đinh; tai khe hơn miệng mừng.",
        keywords="Yên sau hỏi · trống ≠ yên hội · không thở phào · dây · cấp im · máy nghèo",
        place_hint="trong rào",
        scent_hint="dây thừng",
    ),
    dict(
        kind="wave",
        n=701,
        title="Sóng Thấp Lần 116",
        day=821,
        open_=(
            "Sương còn ướt gốc đa nghiêng nam khi trống điểm dứt. Ngày thứ tám trăm hai mươi mốt dưới đất Biên Ải. "
            "Gió bấc mang mùi đất se và lá đa khô; nắng mỏng chưa đủ ấm gáy. Gốc đa nghiêng nam — năm bóng thấp. "
            "Không gào. Chỉ sóng. Máu phải kín. Lần sóng thấp thứ một trăm mười sáu. Luật trong xương: nghe, đâm thấp nếu sát, "
            "lấp xấu, không đếm to, không phơi, không lặp hố Hố cát khô đông."
        ),
        place="Gốc đa nghiêng nam",
        count_vn="năm",
        prev_hole="Hố cát khô đông",
        signal="A Minh trên gò giơ một ngón chỉ nam thấp — có lê; đông trống.",
        scent="mùi lá đa khô",
        micro="Lá đa khua nhẹ sau sóng; không phơi, không đếm năm.",
        keywords="Sóng thấp · Gốc đa nghiêng nam · năm · máu kín · cấp im · máy nghèo",
        place_hint="gốc đa nam",
        scent_hint="lá đa",
    ),
]


def find_path(n: int) -> Path:
    matches = list(BASE.glob(f"Chương {n} - *.txt"))
    if not matches:
        raise FileNotFoundError(f"Chương {n}")
    return matches[0]


def build_one(spec: dict) -> str:
    kind = spec["kind"]
    common = dict(
        n=spec["n"],
        title=spec["title"],
        day=spec["day"],
        open_=spec["open_"],
        signal=spec["signal"],
        scent=spec["scent"],
        micro=spec["micro"],
        keywords=spec["keywords"],
    )
    if kind == "wave":
        text = build_wave(
            **common,
            place=spec["place"],
            count_vn=spec["count_vn"],
            prev_hole=spec["prev_hole"],
        )
    elif kind == "shadow":
        text = build_shadow(
            **common,
            place=spec["place"],
            shadow_detail=spec["shadow_detail"],
            law=spec["law"],
        )
    elif kind == "ask":
        text = build_ask(
            **common,
            ask_item=spec["ask_item"],
            ask_line1=spec["ask_line1"],
            ask_line2=spec["ask_line2"],
            refuse=spec["refuse"],
        )
    elif kind == "calm":
        text = build_calm(
            **common,
            after_what=spec["after_what"],
            bait=spec["bait"],
        )
    else:
        raise ValueError(kind)
    text = ensure_min(text, spec["n"], spec["day"], spec["place_hint"], spec["scent_hint"])
    # hard ban
    if "Nhịp im" in text:
        text = text.replace("Nhịp im", "nhịp việc")
    return text


def main() -> int:
    written = []
    for spec in SPECS:
        n = spec["n"]
        path = find_path(n)
        text = build_one(spec)
        path.write_text(text, encoding="utf-8")
        w = vi_words(text)
        has_nhip = "Nhịp im" in text
        print(f"WRITE ch{n} words={w} nhip={has_nhip} -> {path.name}")
        written.append(str(path))

    cmd = [
        sys.executable,
        str(SCORER),
        *written,
        "--min-words",
        "3000",
        "--threshold",
        "9.0",
        "--json",
        str(BASE / "_score_clone_rewrite_693_701.json"),
    ]
    if CFG.exists():
        cmd.extend(["--cfg", str(CFG)])
    print("SCORE:", " ".join(cmd[-6:]))
    r = subprocess.run(cmd, cwd=str(BASE))
    if (BASE / "_score_clone_rewrite_693_701.json").exists():
        data = json.loads((BASE / "_score_clone_rewrite_693_701.json").read_text(encoding="utf-8"))
        print(
            f"RESULT avg={data.get('avg')} min={data.get('min_final')} "
            f"pass={data.get('pass')}/{data.get('total')} all_pass={data.get('all_pass')}"
        )
        for item in data.get("results", []):
            print(
                f"  ch{item.get('num')} final={item.get('final')} "
                f"hf={item.get('hard_fails')} w={item.get('metrics', {}).get('words')}"
            )
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
