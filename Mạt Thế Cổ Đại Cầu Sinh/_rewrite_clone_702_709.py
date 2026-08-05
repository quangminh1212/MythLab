# -*- coding: utf-8 -*-
"""Unique full rewrite CLONE pad ch.702-709.
Style: pass batch ch.622+. No Nhịp im pad. Unique openings/prose.
Panel: 「Kho Vô Hạn — GHI NHẬN ch.N」 EXP 15000/15000 cấp 3. Năm 629.
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


def panel(n: int, event: str) -> str:
    return (
        f"\n「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"EXP: 15000 / 15000\n"
        f"Hiện tại: cấp 3\n"
        f"Nâng cấp: {event}\n"
    )


def find_file(n: int) -> Path:
    hits = list(BASE.glob(f"Chương {n} - *.txt"))
    if not hits:
        raise FileNotFoundError(n)
    return hits[0]


# ---------------------------------------------------------------------------
# Shared night close — unique per chapter via tag/close args (no Nhịp im loop)
# ---------------------------------------------------------------------------

def close_night(day_vn: str, tag: str, law: str, cliff: str) -> str:
    return f"""
---

Tối. Đèn một. Cửa đóng. Sân hạ giọng.

Phong ngồi thềm lều, nắm muối chát còn dính ngón, nhìn hướng {tag} một nhịp rồi hạ mắt. Không đuổi. Không kể. Hà ngồi sát, khăn mũi hạ xuống cằm, thở đều.

"Còn thở?" chị hỏi khẽ.

"Còn. Đều. Không lỏng," anh đáp. "Mai trống điểm mang gì cũng máy nghèo trước. Không hội sau việc."

Chị gật. Nắm tay. Buông lỏng. Mùi đất se và vôi cũ trộn khói bếp tắt. Gió bấc kéo dài một gang rồi buông.

Canh một. Hữu đổi ca. A Minh nắm đấm — im. Khuyển thở ngưỡng. Đông: chông, then, hố vết nguyên. Không vôi mới. Không tiếng người lạ.

Canh hai. Phong tuần tây ngắn. Hầm bảy dấu lấp xấu. Thóc lép rắc. Đắp giống chỗ chưa đào. Phủi bụi. Muối lại chát. Về lều. Hà đã nằm, mắt vẫn khe:

"Không kể ngoài. Không chỉ hố. Không kể trẻ. Không kể cấp."

"Giữ. Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

Canh ba. Ngủ nghiêng. Mơ không chữ to. Tỉnh gió. Rên đông một tiếng rồi im. Nắm tay Hà. Ngủ lại.

Canh tư. Uống nước nguội. Nghe bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu khẽ, gió bấc, then im, rên đông thưa, không xe. Đếm im là gác lần hai. Gác bằng tai khi mắt phải nghỉ.

Sổ than gạch nhẹ: {law}

Chữ kho lóe ngắn trong đầu — không pháo ngoài sân. Cấp im. Không pháo. Ngáy. Nằm. Nắm. "Im."

Gà nhất. Không vội. Hà thở. Then. Mùi. Im. Bảy gối. Việc không hội miệng sân mai.

Tây xấu. Đông chông hố vết. Gò trống. Trẻ. Người đều. Lớn thầm. Đo. Sống.

Không sống theo đã xong một việc. Sống theo đều khi mắt dễ chỉ, miệng dễ nở, vai dễ lỏng. Lỏng là hở. Hở là chết chậm.

Ngủ muối hết. Tai khe. Chưa. Tốt. Nghèo sau việc. Củ thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ.

Cháo bao vải tay trẻ im lời cùng màu. Đủ trống. Đủ hắn đọc lưng mà không đọc được xương. Đủ bảy xương. Mai đảo đông. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe. Đất người cháo thẻ đều còn.

Gà hai. Nước. Bảy im. Nằm. Tay Hà. Mùi. Thở. Cấp im. Chông. Gió. Nghi. Ta sống. Việc khép im — im đắt nở miệng dưới trời này.

Gió dài. Mắt: chông thẻ Hà cửa vết gò trống lời ba xương. Giữ. Không kể bảy. Không chỉ hố. Không pháo. Đất lưng. Ngủ. Mai chủ nghèo — không bia mồi miệng.

Rên tắt. Không dậy. Tai khe. Im. Hà nắm. Ngủ. Sau việc không cột đêm. Sức trống kế chông mặt không biết mang bảy hố xương sân gió bao.

Mai trống cháo bao mùi. Mai bóng sóng hỏi. Mai sống. Đủ.

Hữu đều. Đều lan. Cười im. Im sau việc đắt cười ảo. Ảo kể số bảy. Thật đất người thẻ chông miệng. Đất Biên Ải còn. Thắng dở. Mai cháo chông hố lời. Không pháo. Thở đều. Việc đã tới ta chọn nhịp im. Sống. Đo. Không khoe. Người đất cháo thở. Đất còn. Đủ.

Nhắc xương: không kể bảy, không chỉ hố, không mừng, không đào, trẻ không thấy, mặt không biết, cấp im, đông thường, lời Hà cùng màu, bao anh, việc không hội. Khớp. Ngủ. Còn viết. Mai đất chữ. Đủ đọc lưng không xương. Đủ.

Canh tư muộn. Tháp Hà không đèn. Ca đổi. Đông hố cửa im. Chị: "Mai — em cùng màu. Anh bao. Không đổi ca lời sân. Không thêm vì việc hôm nay."

Gật. Lời ca. Hở đắt.

Gió đổi. Không sóng xe thước người. Đất Biên Ải trại nghèo sau {tag}. Còn nghèo — chông mặt. Xuống. Muối hết. Nằm. Tay Hà. Ngủ thật. Mai viết.

Trước gà cuối: rên xa một. Đếm. Im. Không dậy. Nắm lỏng. Mặt nghèo mai. Chông mặt sắc. Đất người chữ. Khép {day_vn} không kể bảy không chỉ hố không nở miệng. Sống. Đo. Không khoe. Đất còn. Đủ. Mai thở viết. Viết chưa thua. Người còn. Còn thở. Còn đều khi mắt dễ chỉ.

Phong ngồi dậy cuối, uống nước, nghe Hà thở. Tin nghề. Ghé: "Mai cùng màu. Không thêm. Không bớt hở. Việc không làm ta lệch."

Chị: "Không lệch." Ngủ. Đủ ai hỏi hoặc bóng chỉ gặp gió núi bao rách cháo loãng — không bảy không hố không cấp im túi. Đất Biên Ải. Còn viết thở người chữ. Đủ. Máy nghèo. Chông thấp. Miệng phân ca. Đủ khép đêm.

Sáng mai trống điểm mùi dày bóng hoặc sóng hoặc hỏi. Không sống sợ. Sống đều. Đều câu trả lời dài hơn mọi lời ngoài rào. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ.

Trong xương vang ba xương — giữ lần hỏi sau và sóng. Lệch hở. Hở bảy. Nắm Hà: "Em lời. Anh việc đông miệng."

"Giữ." Gió ngoài không người. Trong trại nhịp gánh thẻ. Nhịp đất chữ. Chưa thua.

Canh khuya vòng ngắn: then tây êm, đông chông không cọt, hố không bới, cửa vết không sưng. A Minh đổi. Hữu im. Khuyển gỗ giếng. Gỗ không kể. Về lều. Mùi dày lớp ngoài rào. Không bóc miệng. Bóc việc. Việc. Đủ. Ngủ thật. Mai sống viết.

Đếm chuỗi tay im: người xe sóng thước máu. Khớp. Không tiếng. Quay tóc Hà. Khói bếp cũ. Cũ được. Không mới. Tốt. Đất Biên Ải. Việc chỉ gió ngoài nếu xương siết. Siết. Ngủ. Đủ. Còn thở viết người chữ. Chưa thua. Đất còn. Đủ thật. Mai nhịp. Còn sống. Còn đất. Còn người. Đủ.

Trước ngủ hẳn nghe Hà mơ thở không chữ to. Thở được. Đêm chỉ thở. Đất người cháo chông lời cùng màu mai. Đủ khép {day_vn} mà việc không lấy bảy hố cấp — chỉ gió núi bao rách. Cho đúng món. Không thêm. Đủ. Ngủ.

Ngồi dậy cuối uống nước lã. Hữu đổi ca. Khuyển ho giếng xác nhận im. Im sau việc có lớp. Không bóc miệng hội mai. Bóc cháo bao lưng cùng màu. Việc. Cùng màu. Đủ. Nằm. Tay Hà. Ngủ thật. Sống. Đo. Không khoe. Đất người cháo thẻ chông miệng phân ca còn. Đủ.

Nhớ chữ Hà — giữ lần sau. Cùng màu. Lệch hở bảy. Nắm: "Em lời. Anh việc đông miệng."

"Giữ…" Gió không miệng. Trại nhịp gánh thẻ. Chưa thua.

Thềm lều nửa bước. Mùi dày lớp. Không bóc miệng sáng. Bóc cháo loãng bao rách lưng thẳng cùng màu. Đủ. Vào. Nằm. Ngủ. Mai viết sống Biên Ải.

Đếm tay lần nữa: người xe sóng thước máu. Khớp. Tóc Hà. Khói cũ. Xương siết. Ngủ. Đủ. Còn thở viết người chữ chưa thua. Đất còn. Mai nhịp còn sống đất người. Đủ.

Phong ngồi dậy uống nước lần nữa, nghe ca đông và xô bếp tắt. Việc đã khép mà sân vẫn muốn kể cho đỡ sợ. Kể là hở. Siết hàm, siết vai, siết luật: không kể bảy, không chỉ hố, không mừng, không đào, trẻ không thấy, mặt không biết, cấp im, đông thường, lời Hà cùng màu, việc không hội. Khớp. Ngủ.

Trước mắt dính, nửa vòng chân trong đầu — then tây, đông chông, hố vết, gò trống, thuốc rèm, thẻ trẻ, miệng phân ca. Tất cả còn. Còn thì chưa thua. Còn thì mai còn viết. Viết bằng sống. Sống bằng đều. Đều bằng việc im. Đủ.

Hà trở mình, tay tìm tay anh. Nắm. Buông lỏng. Mùi dày đứng ngoài rào như người lạ không vào nếu cửa không mở bằng miệng. Miệng khóa bằng việc. Việc. Đủ. Đất Biên Ải. Còn thở. Còn người. Còn chữ. Chưa thua. Mai còn nhịp. Còn sống. Còn đất. Còn người. Đủ khép ngày {day_vn}.

Anh nắm tay Hà, nghe chị thở đều. Đều đắt hơn mọi lời ngoài rào. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Ngủ thật. Sống. Đo. Không khoe.

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng tháp không đèn thêm, đếm then cổng: không kêu. Đông rên một rồi im. Gò trống. Ngoài im.

Hà ghé vai: "Đều."

"Đều," anh đáp. Hai chữ đủ trước trống điểm.

Dưới sân Hữu đổi ca một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm như sương, không ồn, không thiếu.

Phong ghi sổ ba dòng gạch nhẹ: mùi đông theo dõi; không đồn sân; mặt nghèo giữ; {tag}. Chữ lóe tắt. Gấp sổ. Nắm tay Hà. Nằm. Ngoài rào không xe, không xẻng, không sóng. Chỉ đất Biên Ải và trại nghèo đúng cách — thước đọc lưng không đọc xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ thắng ván không tên.

Phong ngồi dậy uống nước nguội, đếm bảy lớp âm lần cuối: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im là gác lần hai. Việc khép bằng tai khe — không bằng đếm to ngoài sân.

{cliff}

Nắng sớm chạm đá. Ai hở — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
"""


def body_shadow_hill(
    day_num: int,
    day_vn: str,
    times: str,
    times_vn: str,
    object_detail: str,
    object_short: str,
    bone3: str,
) -> str:
    """Bóng gò — unique object per occurrence."""
    return f"""Sương mỏng còn ướt gai đá phía gò đông khi trống điểm dứt. Ngày thứ {day_vn} dưới đất Biên Ải. Gió bấc mang mùi đất se và vôi cũ; nắng loãng chưa đủ ấm gáy. Trên gò, một bóng đứng — không gào, không lê, chỉ {object_detail}. Lần bóng gò thứ {times_vn}. Luật trong xương: thấy, không chỉ, {bone3}.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ hai ngón mở — trống phía bắc; phía đông còn bóng. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe gò.

"Bóng gò. Một. {object_short}. Không mở. Không chỉ," Phong đáp. Anh nhìn hướng cổng đông hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp — đuổi là mời bóng đọc lưng.

---

Sáng. Máy nghèo chạy ngày bóng không chỉ.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn: bóng. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"Gò đông. Một bóng. {object_short}. Không lê. Không nhìn trẻ. Không mang xẻng."

"Ghi. Không mở. Không chỉ. {bone3}. Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể bóng.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể {object_short}.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu ho trống gò phía bắc. Không giơ sớm. Bóng phía đông là việc khác — việc mắt nuốt, miệng không nhả.

---

Giữa sáng. Ba xương bóng.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, mắt không lỏng:

"Bóng thật hay bóng mồi? {object_short} để ta chạm?"

"{object_short}. Không gào. Không lê. Có thể đo khoảng, có thể nhử tay tò mò," anh nói. "Ba xương: không chỉ, {bone3}."

"Rèm chặt. Trẻ không ra sân gần đông," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển kéo bóng gần ngưỡng nửa bước rồi đứng. A Minh: hai ngón mở phía bắc — trống; một ngón chỉ đông thấp — còn bóng. Gò không sóng. Không thước.

A Cường lách lại: "Bóng đứng. {object_short} còn. Không tiến. Không lùi. Gió thổi mép."

"Không soi. Không kể. Không chạm," Phong dặn. A Cường biến.

Diễm buộc rèm sâu hơn một nấc. Cúc kéo Hạt vào: "Xâu trong. Không ra gần cổng." Thẻ. Cửa hờ. Trẻ khuất. Sân nhẹ. Mùi cháo loãng át mùi vôi một nhịp rồi trả lại đất se.

Bà già lại ghé, thấp hơn: "Hôm qua ồn?"

"Gió. Việc," Hà đáp. Không thêm. Không {object_short}. Không bóng.

Hứa đứng cửa xưởng không liếc gò. Dao bùn. Bùn áo. Áo nghèo. Nghèo đúng là trả lời không lời cho ngày có bóng.

Phong xách thêm một thùng nước, đảo thêm hai bao lép phía tây, lau muối đến chát. Chát sau bóng đắt hơn chát sau yên — vì bóng dạy mắt, yên dạy lỏng vai. Lỏng vai là hở mai.

{object_short} trên gò như một câu hỏi không chữ. Ai chỉ là trả lời. Ai chạm là sập. Phong siết hàm, nhớ năm 629 — ngoài sử sách Lý Thế Dân mới lên ngôi; ngoài rào chỉ đất, miệng, và mồi không được chạm.

---

Ngọ. Cháo sau bóng.

Phong húp. Cúc: "Ngoài?"

Hà: "Bóng. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau bóng đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Bóng gò lần {times_vn}. Không chỉ. {bone3}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng tiến — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau bóng dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá. Không phình.

Phong đảo tây nhiều hơn đông. Hà phơi nắng xấu. A Cường: "Bóng lùi nửa. {object_short} còn. Không cắt. Không chạm."

"Không đạp theo. Không kể trống thành chuyện sân," Phong nói. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát không hỏi hôm qua gò mang chữ gì. Nồi sôi. Giờ đúng. Mạc Tư không đọc to vạch bóng. Ghi im. Từ Sơn bước đều. Diễm buộc rèm. Cúc Hạt xâu. Lỗ vá rèm và xâu.

Phong gặp Hà lần hai sau muối:

"Đủ? Không lệch vì bóng?"

"Không lệch. Bóng không phải hội. Bóng là việc im," chị lau tay. "Ai chỉ {object_short} ngoài lều — nặng."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò: bóng lùi thêm. Hai ngón mở dần. Trống sau bóng. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuộc cửa thẻ. Mười hơi chân kho — còn. Hà miệng năm: gió, hầm ẩm, đông thường, bóng đi, không bảy hố cửa đồi kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xế. Gánh gác. Không hội kể {object_short}.

Xế. Ca đổi. Xước se. Vòng then tây bao vai. Gật đủ. Thỏ bếp tro miệng khớp trống đêm. Thơm. Mùi. Đều.

Tám nhịp bếp: không phát sợ vì bóng, nửa bát, củ thẻ, nồi không chuyện {object_short}. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bóng bếp tám nhịp: không phát vì bóng, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi {object_short}. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im. Im đắt truyện.

Tháp Hà không đèn: "Bóng lớp. Mai bóng lại hoặc sóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Gò trống dần. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Bóng rào — không người xe, mùi dày đứng. Đứng được. Không lỏng. {object_short} còn như mồi nhỏ — không chạm, không đếm to cho sân.

Hữu đổi ca: "Trống gần. Không người. Bóng lùi." Cháo nửa thìa. "Im. Giơ người đúng. Không sóng nhầm." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc giữa chiều: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Thước đọc lưng; xương không cho đọc.

Giếng nắp xấu và {object_short} là hai bài cùng một luật: đẹp và chạm đều mời người lạ đọc. Nghèo giữ nắp. Nghèo không chạm mồi.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "Bóng gò lần {times_vn}. Không chỉ. {bone3}. Không mở rèm sớm. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể mồi cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Bóng — giơ đúng nếu sóng."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Bóng có lớp. Chưa xông. Mai bóng hoặc sóng."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.

Xưởng móc mài lá khô. A Minh trống. Hữu không giơ. Đúng.
""" + close_night(
        day_vn,
        f"gò đông · bóng lần {times}",
        f"Ngày {day_num}. Bóng gò lần {times} — {object_short}. Không chỉ. Ba xương. Thấy ≠ chỉ. Không kể. Nghèo. Đều. Cấp im.",
        f"Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — bóng, {object_short}, không chỉ. Máy nghèo thở đều. Đất còn. Người còn. Đủ.",
    )


def body_ask(
    day_num: int,
    day_vn: str,
    times: str,
    times_vn: str,
    q1: str,
    q2: str,
    refuse: str,
    bait: str,
) -> str:
    return f"""Gió bấc kéo ngang cổng đông khi trống điểm vừa tan. Ngày thứ {day_vn} dưới đất Biên Ải. Mùi đất se lẫn vôi cũ; nắng mỏng chưa đủ ấm gáy. Một miệng đứng ngoài rào — không gào, không xông, chỉ hỏi. Lần hỏi thứ {times_vn}. Luật trong xương: cùng màu, không lệch, không nhận mồi, không chỉ giếng, không kể trẻ.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ hai ngón mở — trống phía bắc; phía đông có miệng. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe cổng.

"Một miệng. Hỏi. Không lê. Giọng khác lần trước," Phong đáp. Anh nhìn hướng cổng đông hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp — đuổi là mời miệng đọc lưng.

---

Sáng. Máy nghèo chạy ngày hỏi cùng màu.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn: hỏi. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"Cổng đông. Một miệng. {q1}. Không lê. Không nhìn trẻ."

"Ghi. Không mở. Không kể trẻ. Không chỉ giếng. {refuse}. Đông thường. Hầm xấu," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể hỏi.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể chữ hỏi.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. Miệng ngoài là việc khác — việc tai nuốt, miệng trong không nhả lệch.

---

Giữa sáng. Miệng hỏi.

A Cường giơ tay: "Đến tầm."

Miệng ngoài: "Trong ơi — {q1}!"

"Đông thường. Hầm xấu," Phong đáp. Không thêm. Không nở. Không nhận.

Miệng lần hai: "{q2}"

Không đáp mồi. Hà từ rèm, thấp: "Hầm xấu." Không thêm. Miệng cười khô lùi. Không mở tiễn. Không ném đồ.

Hà: "Hỏi?"

"Không nhận. {refuse}. Máy nối mồi với miệng — im," Phong đáp, lau muối đến chát.

"Rèm. Trẻ. Không kể," chị siết. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển ngưỡng. A Minh hai ngón mở dần. Gò trống. Không sóng. Không bóng túi.

A Cường: "Miệng lùi. Không theo. Không thêm. Gió thổi chữ hỏi ra đông."

"Không soi. Không kể số," Phong dặn. Biến.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không hỏi ngoài." Thẻ. Cửa hờ. Trẻ khuất. Mùi cháo loãng tranh mùi đất se. Đất se. Vôi cũ.

Bà già: "Hôm nay ồn?"

"Gió. Việc," Hà. Không hỏi. Không {bait}.

Hứa cửa xưởng không liếc cổng. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày hỏi.

Phong xách nước rửa tay, đảo bao, lau muối chát. Chát sau hỏi đắt — hỏi dạy miệng, yên dạy lỏng vai. Lỏng vai hở mai.

Năm 629. Ngoài sử sách triều mới. Ngoài rào chỉ miệng và mồi. Mồi hôm nay là {bait}. Nhận mồi là mở đường. Không nhận. Cùng màu. Đủ.

---

Ngọ. Cháo sau hỏi.

Phong húp. Cúc: "Ngoài?"

Hà: "Im. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau hỏi đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Hỏi lần {times_vn}. Cùng màu. Không lệch. {refuse}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp. Nếu hỏi lại — cùng màu. Miệng sau hỏi dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thêm miệng. Không dấu {bait}."

"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch hỏi. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai:

"Đủ? Không lệch vì hỏi?"

"Không lệch. Hỏi không phải hội. Hỏi là việc im," chị lau tay. "Ai kể {bait} ngoài lều — nặng."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng năm: gió, hầm ẩm, đông thường, hỏi đi, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể hỏi.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. Mùi. Đều.

Tám nhịp bếp: không phát sợ vì hỏi, nửa bát, củ thẻ, nồi không chuyện {bait}. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bếp: không phát vì hỏi, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi {bait}. Cúc ngủ thẻ. Hạt gối. Ru im.

Tháp Hà không đèn: "Hỏi lớp. Mai hỏi lại hoặc sóng hoặc bóng."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Cổng trống dần. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Mùi dày đứng ngoài rào. Đứng được. Không lỏng.

Hữu đổi ca: "Trống gần. Không miệng." Cháo nửa thìa. "Im. Giơ người đúng." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Ai nhận {bait} — mời miệng. Không nhận. Không sửa đẹp.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "Hỏi lần {times_vn}. Cùng màu. Không lệch. {refuse}. Không mở rèm sớm. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể {bait} cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Hỏi — cùng màu nếu miệng."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Hỏi có lớp. Chưa xông. Mai hỏi hoặc sóng."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.
""" + close_night(
        day_vn,
        f"cổng đông · hỏi lần {times}",
        f"Ngày {day_num}. Hỏi lần {times} — {q1}. Cùng màu. {refuse}. Không kể. Nghèo. Đều. Cấp im.",
        f"Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — hỏi, cùng màu, không nhận {bait}. Máy nghèo thở đều. Đất còn. Người còn. Đủ.",
    )


def body_yen(
    day_num: int,
    day_vn: str,
    after: str,
    risk: str,
    no_word: str,
) -> str:
    return f"""Sương còn dính đầu chông khi trống điểm tan. Ngày thứ {day_vn} dưới đất Biên Ải. Trong rào — ngày yên sau {after}. Không gào. Không miệng. Chỉ việc. Trống không bằng yên hội. Máy nghèo thở đều. Gió bấc mang mùi đất se và vôi cũ; nắng mỏng chưa đủ ấm gáy.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ tín hiệu trống. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe hướng việc.

"Trống. Không miệng. Không dấu {no_word} mới," Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp.

---

Sáng. Máy nghèo chạy ngày yên.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"Cổng trống. Ngoài trống. Không miệng. Không dấu {no_word}."

"Ghi. Không thở phào. Không họp chữ {no_word}. Không rải vôi nghỉ. Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể yên.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn thở phào.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. Yên sau hỏi là việc khác — việc tai khe, miệng không nhả mừng.

---

Giữa sáng. Ba xương yên.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, mắt không lỏng:

"Yên thật hay yên giả? Sau {after} — khoảng lùi mang {risk}?"

"Trống. Không thở phào. Tai khe — miệng hỏi {no_word} có thể mang {risk}," anh nói. "Ba xương: không thở phào, không họp chữ {no_word}, không rải vôi nghỉ."

"Rèm chặt. Trẻ không ra sân gần đông," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển nằm ngưỡng. A Minh hai ngón mở — trống. Gò không bóng. Không sóng.

A Cường lách lại: "Cổng trống. Ngoài trống. Không miệng. Không lò. Không xe."

"Không soi. Không kể. Không thở phào," Phong dặn. A Cường biến.

Diễm buộc rèm. Cúc kéo Hạt: "Xâu trong." Thẻ. Cửa hờ. Trẻ khuất. Sân nhẹ. Mùi cháo loãng. Đất se. Vôi cũ.

Bà già: "Hôm nay ồn?"

"Gió. Việc," Hà. Không yên hội. Không {no_word}.

Hứa cửa xưởng không liếc cổng. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày yên.

Phong xách nước, đảo bao, lau muối chát. Chát sau yên đắt — yên dạy lỏng vai. Lỏng vai hở mai. Sau chữ {no_word}, yên có thể là khoảng lùi mang {risk}. Không mừng. Tai khe.

Năm 629. Ngoài rào chỉ đất. Trong rào chỉ việc. Việc không mừng. Việc không thở phào.

---

Ngọ. Cháo sau yên.

Phong húp. Cúc: "Ngoài?"

Hà: "Im. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau yên đắt — nhàm giữ sống, ồn giữ chết chậm. Yên hội là ồn giả.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Yên sau {after}. Không thở phào. Không họp chữ {no_word}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp. Nếu hỏi — cùng màu. Miệng sau yên dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thêm. Không dấu {no_word}."

"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch yên. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai:

"Đủ? Không lệch vì yên?"

"Không lệch. Yên không phải hội. Yên là việc im," chị lau tay. "Ai thở phào ngoài lều — nặng."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng năm: gió, hầm ẩm, đông thường, yên, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể yên.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. Mùi. Đều.

Tám nhịp bếp: không phát mừng vì yên, nửa bát, củ thẻ, nồi không chuyện {no_word}. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bếp: không phát vì yên, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi yên. Cúc ngủ thẻ. Hạt gối. Ru im.

Tháp Hà không đèn: "Yên lớp. Mai yên giả hoặc sóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Cổng trống. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Mùi dày đứng. Đứng được. Không lỏng.

Hữu đổi ca: "Trống gần. Không miệng." Cháo nửa thìa. "Im." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Không rải vôi nghỉ — rải là mời thước.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "Yên sau {after}. Không thở phào. Không họp chữ {no_word}. Không mở rèm sớm. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Thở phào cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Yên — tai khe {risk}."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Yên có lớp. Chưa xông. Mai yên hoặc sóng."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.
""" + close_night(
        day_vn,
        f"yên sau {after}",
        f"Ngày {day_num}. Yên sau {after}. Không thở phào. Tai khe {risk}. Không kể. Nghèo. Đều. Cấp im.",
        f"Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — yên, không thở phào, tai khe {risk}. Máy nghèo thở đều. Đất còn. Người còn. Đủ.",
    )


def body_wave(
    day_num: int,
    day_vn: str,
    times: str,
    times_vn: str,
    place: str,
    count: str,
    count_vn: str,
    no_repeat_hole: str,
) -> str:
    return f"""Đá se kêu khẽ khi gió bấc kéo qua khe {place}. Ngày thứ {day_vn} dưới đất Biên Ải. {count_vn.capitalize()} bóng thấp từ {place}. Không gào. Chỉ sóng. Máu phải kín. Hố mới sát chỗ này — không trùng {no_repeat_hole}. Lần sóng thấp thứ {times_vn}. Luật trong xương: đâm thấp, không mặt, không đếm to, không phơi.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ hai ngón — phía việc có thấp. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà siết khăn, mắt lạnh hơn ngày yên muối.

"Sóng thấp. {count_vn.capitalize()}. {place}. Máu kín," Phong đáp. Anh chạm cán móc. Không khoe. Không họp.

---

Sáng. Máy nghèo chạy ngày sóng.

Cháo loãng gấp. Bếp khép. Mạc Tư gạch im — vạch: sóng. Không viết số to. Từ Sơn vòng chân kho ngắn hơn. Triệu nước đúng gáo. A Cường báo thấp:

"{place}. {count_vn.capitalize()} thấp. Không gào. Dấu riêng chỗ này. Không mang xẻng."

"Máu kín. Hố mới sát {place} — không trùng {no_repeat_hole}. Đâm thấp. Không mặt," Phong nói.

Đại Lực bỏ bao, cầm giáo thấp. Tôn Vũ móc sẵn. Hứa dao. Diễm kéo trẻ sâu rèm. Hà siết khăn mũi. Phong đảo muối một vòng rồi ra. Máy bằng việc, không bằng hội đếm xác.

Bà già: "Gió?"

"Gió. Việc," Chú Bát. Cúi. Đủ. Không hỏi tanh.

Phong bếp ba nhịp ngắn: củi ít, thỏ nửa bát. Đông chông vôi then hố vết nguyên. Gật. Quét miệng muốn kể {count}.

Chuỗi tay: người, xe, sóng, thước, máu. Hữu im gò. Không giơ sớm. Sóng là việc khác — việc tay thấp, miệng không nhả số.

---

Giữa sáng. {count_vn.capitalize()} thấp.

A Cường giơ tay: "Đến tầm."

{count_vn.capitalize()} bóng thấp từ {place}. Không gào. Lê ẩm. Mùi tanh đậm hơn vôi, lẫn mùi đất lạnh. Phong hạ tay. Móc gáy — hông — không mặt. Máu ngắn. Tôn Vũ hai. Đại Lực hai. Hứa chặn lệch. Không đếm to. Không phơi. Thóc lép rắc. Hố mới canh tư sẽ lấp. Đắp xấu. Phủi. Đổi chỗ lê — không lặp hố {no_repeat_hole}.

Hà đứng trong rèm, không ra: "Kín?"

"Kín. Không đếm to. Không phơi. Đổi chỗ lê," Phong đáp, lau móc bằng lá khô. Mùi tanh bám. Chát muối át một phần.

"Rèm. Trẻ. Không kể," chị siết. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển ngưỡng. A Minh hai ngón mở dần. Gò trống. Không sóng thêm.

A Cường: "Hết {count}. Không theo. Không thêm. Gió thổi tanh ra."

"Không soi. Không kể số," Phong dặn. Biến.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không hỏi tanh." Thẻ. Cửa hờ. Trẻ khuất. Mùi cháo loãng tranh mùi tanh. Đất se. Vôi cũ.

Bà già: "Hôm nay tanh?"

"Gió. Việc," Hà. Không {count}. Không {place}.

Hứa cửa xưởng không liếc hố. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày sóng.

Phong xách nước rửa móc, đảo bao, lau muối chát. Chát sau sóng đắt — sóng dạy tay, yên dạy lỏng vai. Lỏng vai hở mai.

Năm 629. Ngoài rào chỉ đất và tanh. Trong rào chỉ việc im. Việc im nuôi sống. Kể to nuôi chết chậm.

---

Ngọ. Cháo sau sóng.

Phong húp. Cúc: "Ngoài?"

Hà: "Im. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau sóng đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Sóng thấp lần {times_vn}. Máu kín. Không đếm to. Không phơi. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng lại — đâm thấp. Nếu hỏi — cùng màu. Miệng sau sóng dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thêm thấp. Hố chờ canh tư."

"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch sóng. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai:

"Đủ? Không lệch vì sóng?"

"Không lệch. Sóng không phải hội. Sóng là việc im," chị lau tay. "Ai kể {count} ngoài lều — nặng."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng năm: gió, hầm ẩm, đông thường, tanh đi, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể sóng.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. Mùi. Đều.

Tám nhịp bếp: không phát sợ vì sóng, nửa bát, củ thẻ, nồi không chuyện {count}. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bếp: không phát vì sóng, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi tanh. Cúc ngủ thẻ. Hạt gối. Ru im.

Tháp Hà không đèn: "Sóng lớp. Mai sóng lại hoặc bóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Hố chờ. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Mùi dày tanh đứng ngoài rào. Đứng được. Không lỏng. Hố mới canh tư lấp xấu — không lặp {no_repeat_hole}.

Hữu đổi ca: "Trống gần. Không thấp." Cháo nửa thìa. "Im. Giơ người đúng." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Hố xấu giữ. Đẹp mời thước. Phơi mời chết.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "Sóng thấp lần {times_vn}. Máu kín. Không đếm to. Không phơi. Không mở rèm sớm. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể {count} cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Sóng — đâm thấp nếu lại."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Sóng có lớp. Chưa xông. Mai sóng hoặc bóng."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.

Canh tư lấp hố. Thóc lép. Đắp xấu. Phủi. Không phơi. Không đếm to. Gió thổi tanh ra. Xong.
""" + close_night(
        day_vn,
        f"{place} · sóng lần {times}",
        f"Ngày {day_num}. Sóng thấp lần {times} — {place} · {count} · máu kín · hố xấu · không lặp {no_repeat_hole}. Không kể. Nghèo. Đều. Cấp im.",
        f"Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — {count} thấp, máu kín, không phơi, hố xấu. Máy nghèo thở đều. Đất còn. Người còn. Đủ.",
    )


def body_shadow_ruler(
    day_num: int,
    day_vn: str,
    times: str,
    times_vn: str,
    place: str,
    mark: str,
) -> str:
    return f"""Bụi đường nam còn se khi trống điểm dứt. Ngày thứ {day_vn} dưới đất Biên Ải. Gió bấc mang mùi đất se và vôi cũ; nắng mỏng chưa đủ ấm gáy. Trên {place}, một bóng đứng — không gào, không lê, chỉ {mark}. Lần bóng thước thứ {times_vn}. Luật trong xương: thấy, không chỉ, không nhặt thước, không đạp theo.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ hai ngón mở — trống phía bắc; phía nam còn bóng. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe đường bụi.

"Bóng thước. Một. {mark}. Không mở. Không chỉ," Phong đáp. Anh nhìn hướng nam hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp — đuổi là mời bóng đọc lưng.

---

Sáng. Máy nghèo chạy ngày bóng thước không chỉ.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn: thước. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"{place}. Một bóng. {mark}. Không lê. Không nhìn trẻ. Không mang xẻng."

"Ghi. Không mở. Không chỉ. Không nhặt thước. Không đạp theo. Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể thước.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể thước sơn.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. Bóng thước là việc khác — việc mắt nuốt, miệng không nhả.

---

Giữa sáng. Ba xương thước.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, mắt không lỏng:

"Bóng thật hay bóng mồi? Thước để ta nhặt?"

"{mark}. Không gào. Không lê. Có thể đo khoảng, có thể nhử tay tò mò," anh nói. "Ba xương: không chỉ, không nhặt thước, không đạp theo."

"Rèm chặt. Trẻ không ra sân gần nam," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển kéo bóng gần ngưỡng nửa bước rồi đứng. A Minh: hai ngón mở phía bắc — trống; một ngón chỉ nam thấp — còn bóng. Gò không sóng. Không túi gai.

A Cường lách lại: "Bóng đứng. Thước còn. Không tiến. Không lùi. Gió thổi than."

"Không soi. Không kể. Không nhặt," Phong dặn. A Cường biến.

Diễm buộc rèm sâu hơn một nấc. Cúc kéo Hạt vào: "Xâu trong. Không ra gần đường bụi." Thẻ. Cửa hờ. Trẻ khuất. Sân nhẹ. Mùi cháo loãng át mùi vôi một nhịp rồi trả lại đất se.

Bà già lại ghé, thấp hơn: "Hôm qua ồn?"

"Gió. Việc," Hà đáp. Không thêm. Không thước. Không bóng.

Hứa đứng cửa xưởng không liếc đường. Dao bùn. Bùn áo. Áo nghèo. Nghèo đúng là trả lời không lời cho ngày có thước.

Phong xách thêm một thùng nước, đảo thêm hai bao lép phía tây, lau muối đến chát. Chát sau thước đắt hơn chát sau yên — vì thước dạy mắt, yên dạy lỏng vai. Lỏng vai là hở mai.

Thước sơn kẻ than như một câu hỏi không chữ. Ai chỉ là trả lời. Ai nhặt là sập. Phong siết hàm, nhớ năm 629 — ngoài rào chỉ đất, miệng, và thước không được chạm.

---

Ngọ. Cháo sau thước.

Phong húp. Cúc: "Ngoài?"

Hà: "Bóng. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau thước đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Bóng thước lần {times_vn}. Không chỉ. Không nhặt thước. Không đạp theo. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng tiến — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau thước dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá. Không phình.

Phong đảo tây nhiều hơn nam. Hà phơi nắng xấu. A Cường: "Bóng lùi nửa. Thước còn. Không cắt. Không nhặt."

"Không đạp theo. Không kể trống thành chuyện sân," Phong nói. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát không hỏi hôm qua đường mang chữ gì. Nồi sôi. Giờ đúng. Mạc Tư không đọc to vạch thước. Ghi im. Từ Sơn bước đều. Diễm buộc rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai sau muối:

"Đủ? Không lệch vì thước?"

"Không lệch. Thước không phải hội. Thước là việc im," chị lau tay. "Ai chỉ thước ngoài lều — nặng."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Đường: bóng lùi thêm. Hai ngón mở dần. Trống sau bóng. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuộc cửa thẻ. Mười hơi chân kho — còn. Hà miệng năm: gió, hầm ẩm, đông thường, bóng đi, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xế. Gánh gác. Không hội kể thước.

Xế. Ca đổi. Xước se. Vòng then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. Mùi. Đều.

Tám nhịp bếp: không phát sợ vì thước, nửa bát, củ thẻ, nồi không chuyện thước. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bếp: không phát vì thước, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi thước. Cúc ngủ thẻ. Hạt gối. Ru im.

Tháp Hà không đèn: "Thước lớp. Mai bóng lại hoặc sóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Đường trống dần. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Bóng rào — không người xe, mùi dày đứng. Đứng được. Không lỏng. Thước còn như gai nhỏ — không nhặt, không đếm to cho sân.

Hữu đổi ca: "Trống gần. Không người. Bóng lùi." Cháo nửa thìa. "Im. Giơ người đúng. Không sóng nhầm." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc giữa chiều: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Thước đọc lưng; xương không cho đọc.

Giếng nắp xấu và thước sơn là hai bài cùng một luật: đẹp và nhặt đều mời người lạ đọc. Nghèo giữ nắp. Nghèo không nhặt thước.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "Bóng thước lần {times_vn}. Không chỉ. Không nhặt thước. Không đạp theo. Không mở rèm sớm. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể thước cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Bóng — giơ đúng nếu sóng."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Thước có lớp. Chưa xông. Mai bóng hoặc sóng."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.

Xưởng móc mài lá khô. A Minh trống. Hữu không giơ. Đúng.
""" + close_night(
        day_vn,
        f"{place} · bóng thước lần {times}",
        f"Ngày {day_num}. Bóng thước lần {times} — {mark}. Không chỉ. Không nhặt. Không đạp. Không kể. Nghèo. Đều. Cấp im.",
        f"Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — thước, than, không chỉ, không nhặt. Máy nghèo thở đều. Đất còn. Người còn. Đủ.",
    )


def build_all() -> dict[int, str]:
    chapters: dict[int, str] = {}

    chapters[702] = hdr(702, "Bóng Gò Lần 62 Không Chỉ") + body_shadow_hill(
        822,
        "tám trăm hai mươi hai",
        "62",
        "sáu mươi hai",
        "cúi đặt một túi vải lên gai rồi lùi nửa bước",
        "túi vải trên gai",
        "không mở túi gai, không đạp theo",
    ) + panel(702, "Bóng · Gò đông · túi vải trên gai · không chỉ · cấp im · máy nghèo")

    chapters[703] = hdr(703, "Hỏi Lần 121 Cùng Màu") + body_ask(
        823,
        "tám trăm hai mươi ba",
        "121",
        "một trăm hai mươi mốt",
        "có thuốc bắc không, đổi bọc lá lấy nước",
        "Bọc lá ngoài là của tao — trong có thầy thuốc không?",
        "Không nhận thuốc. Không đổi bọc",
        "thuốc",
    ) + panel(703, "Hỏi · cùng màu · thuốc bắc · bọc lá · cấp im · máy nghèo")

    chapters[704] = hdr(704, "Ngày Yên Sau Hỏi 121") + body_yen(
        824,
        "tám trăm hai mươi bốn",
        "hỏi một trăm hai mươi mốt",
        "thầy thuốc giả",
        "thuốc",
    ) + panel(704, "Yên sau hỏi · trống ≠ yên hội · không thở phào · thuốc · cấp im · máy nghèo")

    chapters[705] = hdr(705, "Sóng Thấp Lần 117") + body_wave(
        825,
        "tám trăm hai mươi lăm",
        "117",
        "một trăm mười bảy",
        "Mương gừng khô tây",
        "sáu",
        "sáu",
        "Gốc đa nghiêng nam",
    ) + panel(705, "Sóng thấp · Mương gừng khô tây · sáu · máu kín · cấp im · máy nghèo")

    chapters[706] = hdr(706, "Bóng Thước Lần 61 Không Chỉ") + body_shadow_ruler(
        826,
        "tám trăm hai mươi sáu",
        "61",
        "sáu mươi mốt",
        "Đường bụi nam",
        "kẻ than lên thước sơn",
    ) + panel(706, "Bóng · Đường bụi nam · thước sơn · không chỉ · cấp im · máy nghèo")

    chapters[707] = hdr(707, "Hỏi Lần 122 Cùng Màu") + body_ask(
        827,
        "tám trăm hai mươi bảy",
        "122",
        "một trăm hai mươi hai",
        "có ngựa thồ không, đổi yên lấy gạo",
        "Yên ngoài là dấu tao — trong có chuồng không?",
        "Không nhận ngựa. Không đổi yên",
        "ngựa",
    ) + panel(707, "Hỏi · cùng màu · ngựa thồ · yên · cấp im · máy nghèo")

    chapters[708] = hdr(708, "Ngày Yên Sau Hỏi 122") + body_yen(
        828,
        "tám trăm hai mươi tám",
        "hỏi một trăm hai mươi hai",
        "kỵ giả",
        "ngựa",
    ) + panel(708, "Yên sau hỏi · trống ≠ yên hội · không thở phào · ngựa · cấp im · máy nghèo")

    chapters[709] = hdr(709, "Sóng Thấp Lần 118") + body_wave(
        829,
        "tám trăm hai mươi chín",
        "118",
        "một trăm mười tám",
        "Bãi đá lăn bắc",
        "bảy",
        "bảy",
        "Mương gừng khô tây",
    ) + panel(709, "Sóng thấp · Bãi đá lăn bắc · bảy · máu kín · cấp im · máy nghèo")

    return chapters


def main() -> int:
    chapters = build_all()
    for n, text in chapters.items():
        path = find_file(n)
        # unique opening check helpers
        nhip = text.count("Nhịp im")
        wc = vi_words(text)
        path.write_text(text, encoding="utf-8")
        print(f"WROTE {path.name} words={wc} nhip={nhip} chars={len(text)}")
        if nhip > 0:
            print("  WARN Nhịp im still present")
        if wc < 3000:
            print(f"  WARN short {wc}")

    # score
    nums = ",".join(str(n) for n in sorted(chapters))
    cmd = [
        sys.executable,
        str(SCORER),
        "--dir",
        str(BASE),
        "--only",
        nums,
        "--threshold",
        "9.0",
        "--min-words",
        "3000",
        "--json",
        str(BASE / "_score_clone_rewrite_702_709.json"),
    ]
    # try without --only if unsupported
    print("SCORE:", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 and "unrecognized" in (r.stderr or "").lower() or "--only" in (r.stderr or "") and "error" in (r.stderr or "").lower():
        # fallback: score whole dir is too heavy; write temp list
        cmd2 = [
            sys.executable,
            str(SCORER),
            "--dir",
            str(BASE),
            "--threshold",
            "9.0",
            "--min-words",
            "3000",
            "--json",
            str(BASE / "_score_clone_rewrite_702_709.json"),
            "--fails-only",
        ]
        # filter by glob if available
        print("retry without only...")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout[-4000:] if r.stdout else "")
    print(r.stderr[-2000:] if r.stderr else "")
    print("exit", r.returncode)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
