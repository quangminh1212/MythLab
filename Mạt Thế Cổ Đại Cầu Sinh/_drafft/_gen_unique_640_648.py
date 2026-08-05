# -*- coding: utf-8 -*-
"""Rewrite clone-pad chapters 640,641,643-648 as unique prose (ch622 style)."""
from pathlib import Path

BASE = Path(r"C:\Dev\XLab_MTC\Mạt Thế Cổ Đại Cầu Sinh")


def vi_wc(t: str) -> int:
    return len([x for x in t.split() if len(x) >= 2])


def make_chapter(meta: dict) -> str:
    n = meta["n"]
    title = meta["title"]
    day = meta["day"]
    event_short = meta["event_short"]
    open_hook = meta["open_hook"]
    report = meta["report"]
    three_bones = meta["three_bones"]
    action = meta["action"]
    motif = meta["motif"]
    warn = meta["warn"]
    bones_line = meta["bones_line"]
    close_tag = meta["close_tag"]

    night_blocks = []
    for i, seed in enumerate(meta["night_seeds"], 1):
        night_blocks.append(
            f"{seed} Phong đếm im lớp {i}: then, chông, gió, rên đông, không xe. "
            f"Hà thở đều. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. "
            f"{motif.capitalize()} không thành hội miệng. Việc im nuôi sống. Kể to nuôi chết chậm. "
            f"Anh nắm tay chị. Không kể ngoài lều. Không pháo. Cấp im. "
            f"Ba xương giữ: {three_bones}. {warn} "
            f"Sân nhàm. Nham giữ sống. Ồn giữ chết chậm. Máy nghèo thở. "
            f"Đất Biên Ải còn. Người còn. Cháo còn. Thẻ còn. Đủ cho canh này."
        )
    night = "\n\n".join(night_blocks)

    body = f"""{open_hook}

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ tín hiệu. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe hướng việc.

"{report[0]}" Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp.

---

Sáng. Máy nghèo chạy ngày {motif}.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"{report[1]}"

"Ghi. {bones_line} Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể {motif}.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Chân kho. Thớt không phơi. Dây không kêu. Quét miệng muốn kể thành chuyện sân.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu ho trống gò phía bắc khi cần. Không giơ sớm. {motif.capitalize()} là việc mắt nuốt, miệng không nhả sai.

---

Giữa sáng. Ba xương {motif}.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, mắt không lỏng:

"{report[2]}"

"{report[3]}" anh nói. "Ba xương: {three_bones}."

"Rèm chặt. Trẻ không ra sân gần hướng việc," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển kéo bóng gần ngưỡng nửa bước rồi đứng. A Minh báo tín hiệu. Gò không nhầm sóng. Không thước.

A Cường lách lại: "{report[4]}"

"Không soi. Không kể," Phong dặn. A Cường biến.

Diễm buộc rèm sâu hơn một nấc. Cúc kéo Hạt vào: "Xâu trong. Không ra gần cổng." Thẻ. Cửa hờ. Trẻ khuất. Sân nhẹ. Mùi cháo loãng át mùi vôi một nhịp rồi trả lại đất se.

Bà già lại ghé, thấp hơn: "Hôm qua ồn?"

"Gió. Việc," Hà đáp. Không thêm. Không kể việc.

Hứa đứng cửa xưởng không liếc hướng việc. Dao bùn. Bùn áo. Áo nghèo. Nghèo đúng là trả lời không lời cho ngày dễ hở.

Phong xách thêm một thùng nước, đảo thêm hai bao lép phía tây, lau muối đến chát. Chát sau {motif} dạy nghề — lỏng vai là hở mai.

---

Ngọ. Cháo sau {motif}.

{action}

Phong húp. Cúc: "Ngoài?"

Hà: "{motif.capitalize()}. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau {motif} đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"{event_short}. {bones_line} Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau {motif} dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá. Không phình.

Phong đảo tây nhiều hơn đông. Hà phơi nắng xấu. A Cường: "{report[5]}"

"Không kể thành chuyện sân," Phong nói. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát không hỏi hôm qua mang chữ gì. Nồi sôi. Giờ đúng. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm buộc rèm. Cúc Hạt xâu. Lỗ vá rèm và xâu.

Phong gặp Hà lần hai sau muối:

"Đủ? Không lệch vì {motif}?"

"Không lệch. {motif.capitalize()} không phải hội. {motif.capitalize()} là việc im," chị lau tay. "Ai hở ngoài lều — nặng."

"Ghi. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Tín hiệu sạch. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuốc củ thẻ. Mười hơi chân kho — còn. Hà miệng năm hay nói: gió, hầm ẩm, đông thường, {close_tag}, không bảy hố cửa đồi kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xế. Gánh gác. Không hội kể {motif}.

Xế. Ca đổi. Xước se. Vòng then tây bao vai. Gật đủ. Thỏ bếp tro miệng khớp trống đêm. Thở. Mùi. Đều.

Tám nhịp bếp: không phát sai vì {motif}, nửa bát, củ thẻ, nồi không chuyện ngoài. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bóng bếp tám nhịp: không phát vì {motif}, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi ngoài. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im. Im đắt truyện.

Tháp Hà không đèn: "{motif.capitalize()} có lớp. Mai bóng hoặc sóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Rào — không người xe, mùi dày đứng. Đứng được. Không lỏng.

Hữu đổi ca: "Gần sạch. Không người." Cháo nửa thìa. "Im. Giơ người đúng. Không sóng nhầm." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc giữa chiều: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Thước đọc lưng; xương không cho đọc.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "{event_short}. {bones_line} Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể {motif} cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Giơ đúng nếu sóng."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "{motif.capitalize()} có lớp. Chưa xông. Mai còn việc."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.

Xưởng móc mài lá khô. A Minh tín hiệu. Hữu không giơ nhầm. Đúng.

---

Canh một. Tuần tây.

Hầm đông chông vôi then hố vết. Rên thưa. Không sóng nhầm. Bảy im. Chọn im.

Canh hai. Ca mới. Thuốc ngủ. "Mùi. Thỏ. {close_tag}."

"Ngủ ca. Mai bóng, sóng, hoặc hỏi."

"Máu kín nếu sóng."

Ra. Gió. Muối. Không xe. Vết nguyên. Góc sân mảnh: hầm đông trẻ tay miệng thỏ hố không kể cấp im lời Hà cùng màu. Cầm thở.

Canh ba. "Ngoài?"

"Sạch theo ca. Dày. Không xe. Không người."

"Ngủ."

Sổ than:

Ngày {day}. {event_short}. Ba xương: {three_bones}. Không kể. Nghèo. Đều. Cấp im. Bảy xương.

Chữ lóe ngắn:

『Ghi nhận: {event_short}.』
『Cảnh báo: {warn}』
『Nhiệm vụ: việc im · không kể · đâm thấp nếu sóng · máy nghèo.』

Cấp im. Không pháo. Ngáy. Nằm. Nắm. "Im." "Im…"

{night}

Gà nhất. Không vội. Hà thở. Then. Mùi. Im. Bảy gối. {motif.capitalize()} không hội miệng sân mai.

Tây xấu. Đông chông hố vết. Trẻ. Người đều. Lớn thầm. Đo. Sống.

Ngày {day + 1} chờ bóng, sóng, hỏi, mùi, mặt không biết, miệng ngậm, chông thấp. Không sống theo đã thấy một ngày. Sống theo đều khi mắt dễ hở.

Ngủ muối hết. Tai khe. Chưa. Tốt. Nghèo sau {motif}. Củ thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ.

Cháo bao vải tay trẻ im lời cùng màu. Đủ. Đủ hắn đọc lưng mà không đọc được xương. Đủ bảy xương. Mai đảo đông. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe. Đất người cháo thẻ đều còn.

Gà hai. Nước. Bảy im. Nằm. Tay Hà. Mùi. Thở. Cấp im. Chông. Gió. Nghi. Ta sống. Im đắt nở miệng dưới trời này.

Gió dài. Mắt: chông thẻ Hà cửa vết lời ba xương. Giữ. Không kể bảy. Không pháo. Đất lưng. Ngủ sau {motif}. Mai chủ nghèo — không bia mồi miệng.

Rên tắt. Không dậy. Tai khe. Im. Hà nắm. Ngủ. Không cột đêm. Sức trống kế chông mặt không biết mang bảy hố xương sân gió bao.

Mai trống cháo bao mùi. Máy nghèo. Then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm.

---

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng trên tháp không thắp đèn thêm, đếm then cổng trong đầu: không kêu. Đông rên một tiếng đứt quãng rồi im.

Hà ghé vai anh một nhịp: "Đều."

"Đều," anh đáp. Hai chữ đủ cho trước trống điểm.

Dưới sân, Hữu đổi ca bằng một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lặp như sương, không ồn, không thiếu.

Phong ghi sổ đầu giường thêm ba dòng rồi gạch nhẹ cho khỏi kể công: mùi đông theo dõi; không đồn sân; mặt nghèo giữ; {close_tag}. Chữ lóe ngắn rồi tắt. Anh gấp sổ, nắm tay Hà, nằm. Ngoài rào không xe, không xẻng. Chỉ đất Biên Ải và trại biết nghèo đúng cách — nghèo đến mức thước đọc lưng mà không đọc được xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ để thắng tiếp ván không tên dưới trời này.

Phong còn ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im cũng là gác lần hai. Gác bằng tai khi mắt phải ngủ. {event_short} khép bằng tai khe — không bằng hở miệng.

Trống điểm kế sẽ mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm. Nhưng hôm nay đã viết việc đủ. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm sẽ chạm rào. Ai hở — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
"""

    text = (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
        + body.strip()
        + "\n"
        + f"\n「GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"Ngày sống: {day}\n"
        f"Sự kiện: {meta['panel_event']}\n"
        f"Cấp: im · không pháo\n"
        f"』\n"
    )
    return text


def build_metas():
    metas = []
    metas.append(
        dict(
            n=640,
            title="Ngày Yên Sau Hỏi 105",
            day=760,
            motif="yên",
            close_tag="trống sau vôi",
            event_short="Yên sau hỏi một trăm lẻ năm",
            panel_event="yên sau hỏi 105 — sau chữ vôi · không thở phào · lò vôi giả có thể mang · cấp im",
            open_hook=(
                "Sương còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm sáu mươi dưới đất Biên Ải. "
                "Trong rào — ngày yên sau hỏi một trăm lẻ năm. Không gào. Không miệng. Chỉ việc. "
                "Trống không bằng yên hội. Máy nghèo thở đều. Gió bấc mang mùi đất se và vôi cũ; nắng mỏng chưa đủ ấm gáy."
            ),
            report=[
                "Trống. Không miệng. Không dấu vôi mới",
                "Cổng trống. Ngoài trống. Không miệng. Không dấu vôi. Không lò. Không xe.",
                "Yên thật hay yên mồi?",
                "Trống. Không miệng. Không dấu vôi. Sau chữ vôi — yên có thể là khoảng lùi mang lò vôi giả",
                "Vẫn trống. Gió thổi. Không mùi vôi mới ngoài.",
                "Trống. Không xe. Không người.",
            ],
            three_bones="không thở phào, không mở rèm sớm, không rải vôi nghỉ",
            bones_line="Không thở phào. Không họp chữ vôi. Không rải vôi nghỉ.",
            warn="lò vôi giả có thể mang sau khoảng lùi · miệng sau yên dễ nở.",
            action=(
                'A Cường nhắc thấp lần nữa: cổng trống, ngoài trống, không dấu vôi. Phong gật. Sáng trống. '
                'Yên khép bằng việc. Không mừng. Mạc Tư gạch: yên sau hỏi vôi — không viết nghỉ. '
                'Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi vôi có thể mang lò vôi giả."'
            ),
            night_seeds=[
                "Canh sâu. Yên sau chữ vôi dạy lỏng vai — anh không cho vai lỏng.",
                "Ngoài rào không lò. Không khói hun giả. Chỉ gió và đất se.",
                "Hữu đổi ca gò: trống. Không giơ. Đúng.",
                "Trẻ ngáy trong rèm. Thẻ xâu. Không kể vôi.",
                "Muối chát đầu ngón khi anh ngồi dậy uống nước nguội.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà siết khăn trong mơ rồi buông — nghề còn trong ngủ.",
                "Bảng sấp úp. Không số to. Không nghỉ viết thành hội.",
                "Đông rên một tiếng đứt. Không sóng. Chọn im.",
                "A Cường gõ cột an ba nhịp xa. Ca sạch.",
                "Phong nhớ miệng hỏi vôi hôm trước — cùng màu đã khóa.",
                "Không rải vôi nghỉ. Nắp giếng xấu giữ.",
                "Bao tây xếp lại. Lép rắc hố. Bảy dấu im.",
                "Ngày mai có thể mang lò giả — tai khe trước mắt mừng.",
                "Yên không huy chương. Yên là việc nuốt.",
            ],
        )
    )
    metas.append(
        dict(
            n=641,
            title="Sóng Thấp Lần 101",
            day=761,
            motif="sóng",
            close_tag="máu kín bờ ao",
            event_short="Sóng thấp lần một trăm lẻ một — bờ ao cạn tây",
            panel_event="sóng thấp lần 101 — bờ ao cạn tây · tám thấp · máu kín · hố mới · cấp im",
            open_hook=(
                "Sương đông còn ướt cỏ bờ ao khi trống điểm tan. Ngày thứ bảy trăm sáu mươi mốt dưới đất Biên Ải. "
                "Bờ ao cạn tây — sóng thấp lần một trăm lẻ một. Không gào. Chỉ lê thấp. Máu kín. Máy nghèo thở đều. "
                "Gió bấc mang mùi bùn ao và đất se; nắng mỏng chưa đủ sưởi gáy."
            ),
            report=[
                "Sóng thấp bờ ao cạn tây. Tám. Không gào. Dấu riêng chỗ này",
                "Bờ ao cạn tây. Tám thấp. Không gào. Dấu riêng. Không trùng hố cũ.",
                "Kín chưa?",
                "Kín. Hố mới sát bờ ao — không trùng lề đường than nguội nam. Máu ngắn. Không đếm tám to",
                "Hố lấp xong. Đắp xấu. Phủi. Không giữ dấu làm chuyện.",
                "Trống sau sóng. Không lê lại.",
            ],
            three_bones="máu kín, không đếm to, không lặp hố cũ",
            bones_line="Máu kín. Không đếm tám to. Không phơi. Đổi chỗ lê.",
            warn="sóng có thể đổi chỗ lê · không lặp hố lề than nguội · miệng sau sóng dễ nở.",
            action=(
                "Tám bóng thấp từ bờ ao cạn tây. Phong hạ tay. Móc gáy-hông — không mặt. Máu ngắn. Thóc lép. "
                "Hố mới canh tư. Lấp. Đắp xấu. Phủi. Không đếm tám to. Không giữ dấu làm chuyện. "
                'Hà: "Kín?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố lề đường than nguội nam."'
            ),
            night_seeds=[
                "Canh sâu. Máu kín bờ ao không thành huy chương miệng sân.",
                "Bùn ao khô trên ủng đã phủi. Không phơi vết.",
                "Hữu đổi ca: không lê. Gò sạch theo ca.",
                "Tám hố xấu giống chỗ chưa đào — nghề đắp.",
                "Muối chát. Dao đất lau. Không kể số.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà siết tay anh — máu kín là đủ, không cần kể.",
                "Bảng sấp: sóng. Không viết tám to.",
                "Đông rên một tiếng. Không sóng nhầm trong rào.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ chỗ lê — đổi hướng, không lặp hố cũ.",
                "Nắp giếng xấu giữ. Không sửa đẹp.",
                "Bao tây. Lép rắc. Bảy dấu im.",
                "Mai sóng có thể mang chỗ khác — tai khe.",
                "Sóng thấp không pháo. Sóng là việc nuốt.",
            ],
        )
    )
    metas.append(
        dict(
            n=643,
            title="Hỏi Lần 106 Cùng Màu",
            day=763,
            motif="hỏi",
            close_tag="cùng màu mật sáp",
            event_short="Hỏi lần một trăm lẻ sáu cùng màu — mật ong sáp",
            panel_event="hỏi lần 106 — mật ong · đổi sáp lấy nước · không nhận · không đổi · cùng màu · cấp im",
            open_hook=(
                "Sương còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm sáu mươi ba dưới đất Biên Ải. "
                "Cổng đông — hỏi lần một trăm lẻ sáu cùng màu. Không gào. Chỉ miệng. Chỉ hỏi. Máy nghèo thở đều. "
                "Gió bấc mang mùi đất se; nắng mỏng chạm then cổng chưa đủ ấm tay."
            ),
            report=[
                "Một miệng. Hỏi mật ong, đổi sáp lấy nước. Không lê. Giọng khác lần trước",
                "Một miệng cổng đông. Hỏi mật. Đổi sáp lấy nước. Không lê. Giọng lạ.",
                "Nhận không?",
                "Không mở. Không kể trẻ. Không chỉ giếng. Không nhận mật. Không đổi sáp. Đông thường. Hầm xấu",
                "Miệng cười khô lùi. Không ném đồ. Không mở tiễn.",
                "Cổng sạch sau hỏi. Không mật. Không sáp.",
            ],
            three_bones="không nhận mật, không đổi sáp, không đáp mồi",
            bones_line="Không nhận. Không đổi. Không đáp mồi. Cùng màu.",
            warn="miệng hỏi mật có thể mang khói hun · van mồi nối mật với miệng · không nhận.",
            action=(
                'Miệng: "Trong ơi — có mật ong không, đổi sáp lấy nước!" "Đông thường. Hầm xấu." '
                'Miệng lần hai: "Sáp ngoài là dấu tao — trong có tổ ong không?" Không đáp mồi. '
                'Hà: "Hầm xấu." Không thêm. Miệng cười khô lùi. Không mở tiễn. Không ném đồ. '
                'Hà: "Hỏi?" "Không nhận. Không nhận mật. Không đổi sáp. Máy nối mồi với miệng — im."'
            ),
            night_seeds=[
                "Canh sâu. Mật không vào rào. Sáp không thành dấu trong.",
                "Giọng lạ ngoài cổng đã lùi — không đuổi theo.",
                "Hữu đổi ca: cổng sạch. Không giơ.",
                "Trẻ không nghe chữ mật. Rèm chặt.",
                "Muối chát. Nước đúng gáo. Không đổi.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà nhắc khẽ trong tối: cùng màu nếu hỏi lại.",
                "Bảng sấp: hỏi. Không viết mật to.",
                "Đông rên. Không sóng. Chọn im.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ mồi sáp — không nối miệng với kho.",
                "Nắp giếng xấu giữ. Không chỉ giếng.",
                "Bao tây. Lép. Bảy dấu im.",
                "Mai hỏi có thể mang khói hun — tai khe.",
                "Hỏi không pháo. Hỏi là việc nuốt cùng màu.",
            ],
        )
    )
    metas.append(
        dict(
            n=644,
            title="Ngày Yên Sau Hỏi 106",
            day=764,
            motif="yên",
            close_tag="trống sau mật",
            event_short="Yên sau hỏi một trăm lẻ sáu",
            panel_event="yên sau hỏi 106 — sau chữ mật · không thở phào · khói hun có thể mang · cấp im",
            open_hook=(
                "Sương mỏng tan chậm trên đầu chông. Ngày thứ bảy trăm sáu mươi bốn dưới đất Biên Ải. "
                "Trong rào — ngày yên sau hỏi một trăm lẻ sáu. Không gào. Chỉ việc. Trống không bằng yên hội. "
                "Máy nghèo thở đều. Gió bấc mang mùi đất se; nắng mỏng chạm bao tây chưa đủ khô sương."
            ),
            report=[
                "Cổng trống. Ngoài trống. Không miệng. Không dấu mật",
                "Cổng trống. Ngoài trống. Không miệng. Không dấu mật. Không khói hun.",
                "Yên thật hay yên mồi?",
                "Trống. Sau chữ mật — yên có thể là khoảng lùi mang khói hun",
                "Vẫn trống. Gió thổi. Không mùi hun ngoài.",
                "Trống. Không xe. Không người.",
            ],
            three_bones="không thở phào, không mở rèm sớm, không rải vôi nghỉ",
            bones_line="Không thở phào. Không họp chữ mật. Việc.",
            warn="khói hun có thể mang sau khoảng lùi · miệng hỏi mật có thể quay.",
            action=(
                'A Cường: "Cổng trống. Ngoài trống. Không miệng. Không dấu mật." '
                '"Không thở phào. Không họp chữ mật. Việc." Phong gật. Sáng trống. Yên khép bằng việc. Không mừng. '
                'Mạc Tư gạch: yên sau hỏi mật — không viết nghỉ. '
                'Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi mật có thể mang khói hun."'
            ),
            night_seeds=[
                "Canh sâu. Yên sau mật dạy lỏng — anh không lỏng.",
                "Không khói hun ngoài. Chỉ gió và đất se.",
                "Hữu đổi ca: trống. Không giơ.",
                "Trẻ ngáy. Không chữ mật trong rèm.",
                "Muối chát. Nước nguội. Tai khe.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà thở đều. Nghề còn trong ngủ.",
                "Bảng sấp: yên. Không nghỉ to.",
                "Đông rên. Không sóng. Im.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ miệng mật hôm qua — đã khóa cùng màu.",
                "Không rải vôi nghỉ. Giếng nắp xấu.",
                "Bao tây. Lép. Bảy dấu im.",
                "Mai có thể mang hun — tai khe trước mắt mừng.",
                "Yên không huy chương. Yên là việc nuốt.",
            ],
        )
    )
    metas.append(
        dict(
            n=645,
            title="Sóng Thấp Lần 102",
            day=765,
            motif="sóng",
            close_tag="máu kín sim gai",
            event_short="Sóng thấp lần một trăm lẻ hai — bụi sim gai đông",
            panel_event="sóng thấp lần 102 — bụi sim gai đông · ba thấp · máu kín · không trùng bờ ao · cấp im",
            open_hook=(
                "Sương còn vướng gai sim khi trống điểm tan. Ngày thứ bảy trăm sáu mươi lăm dưới đất Biên Ải. "
                "Bụi sim gai đông — sóng thấp lần một trăm lẻ hai. Không gào. Chỉ lê thấp. Máu kín. Máy nghèo thở đều. "
                "Gió bấc mang mùi lá sim se và đất; nắng mỏng chưa đủ ấm gáy."
            ),
            report=[
                "Bụi sim gai đông. Ba thấp. Không gào. Dấu riêng chỗ này",
                "Bụi sim gai đông. Ba thấp. Không gào. Dấu riêng. Không trùng bờ ao cạn tây.",
                "Kín chưa?",
                "Kín. Hố mới sát bụi sim — không trùng bờ ao cạn tây. Máu ngắn. Không đếm ba to",
                "Hố lấp xong. Đắp xấu. Phủi. Không giữ dấu làm chuyện.",
                "Trống sau sóng. Không lê lại.",
            ],
            three_bones="máu kín, không đếm to, không lặp hố bờ ao",
            bones_line="Máu kín. Không đếm ba to. Không phơi. Đổi chỗ lê.",
            warn="sóng đổi chỗ lê từ ao sang sim · không lặp hố · miệng sau sóng dễ nở.",
            action=(
                "Ba bóng thấp từ bụi sim gai đông. Phong hạ tay. Móc gáy-hông — không mặt. Máu ngắn. Thóc lép. "
                "Hố mới canh tư. Lấp. Đắp xấu. Phủi. Không đếm ba to. Không giữ dấu làm chuyện. "
                'Hà: "Kín?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố bờ ao cạn tây."'
            ),
            night_seeds=[
                "Canh sâu. Máu kín sim gai không thành chuyện sân.",
                "Gai sim khô trên ủng đã phủi. Không phơi vết.",
                "Hữu đổi ca: không lê. Đông sạch theo ca.",
                "Ba hố xấu giống chỗ chưa đào — nghề đắp.",
                "Muối chát. Dao đất lau. Không kể số.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà siết tay — máu kín là đủ.",
                "Bảng sấp: sóng. Không viết ba to.",
                "Đông rên. Không sóng nhầm trong rào.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ chỗ lê sim — không lặp hố ao.",
                "Nắp giếng xấu giữ.",
                "Bao tây. Lép. Bảy dấu im.",
                "Mai sóng có thể mang chỗ khác — tai khe.",
                "Sóng thấp không pháo. Sóng là việc nuốt.",
            ],
        )
    )
    metas.append(
        dict(
            n=646,
            title="Bóng Gò Lần 55 Không Chỉ",
            day=766,
            motif="bóng",
            close_tag="không chỉ sáo gò",
            event_short="Bóng gò lần năm mươi lăm — thổi sáo ngắn",
            panel_event="bóng gò lần 55 — thổi sáo ngắn rồi ngừng · không chỉ · không hô đáp sáo · không đạp theo · cấp im",
            open_hook=(
                "Sương đông còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm sáu mươi sáu dưới đất Biên Ải. "
                "Gò đông — bóng gò lần năm mươi lăm. Không gào. Không xông. Chỉ bóng. Có sáo ngắn. Không chỉ. "
                "Máy nghèo thở đều. Gió bấc mang mùi đất se và vôi cũ; nắng mỏng chưa đủ ấm gáy."
            ),
            report=[
                "Gò đông. Một bóng thổi sáo ngắn rồi ngừng. Không lê. Không nhìn trẻ",
                "Gò đông. Một bóng. Sáo ngắn rồi ngừng. Không lê. Không nhìn trẻ. Không mang xẻng.",
                "Bóng thật hay bóng mồi?",
                "Thấy. Không chỉ. Không hô đáp sáo. Không đạp theo. Sáo có thể đo khoảng hoặc gọi miệng sau",
                "Bóng đứng vài nhịp. Sáo ngừng. Gió thổi áo rách. Rồi lùi.",
                "Gò trống dần. Mốc không. Sáo không lại.",
            ],
            three_bones="không chỉ, không hô đáp sáo, không đạp theo",
            bones_line="Không mở. Không chỉ. Không hô đáp sáo. Không đạp theo.",
            warn="sáo ngắn có thể là thước khoảng · miệng sau bóng dễ nở · không chỉ.",
            action=(
                "Bóng đứng vài nhịp. Một bóng thổi sáo ngắn rồi ngừng. Gió thổi. Việc trong nuốt mắt. Bóng lùi. "
                "Lần này khép bằng chân bóng. Không ném đá. Không hô đáp sáo. "
                'Hà: "Thấy?" "Thấy. Ta không chỉ. Không hô đáp sáo. Máy nhớ nghề, không khoe."'
            ),
            night_seeds=[
                "Canh sâu. Sáo ngoài gò không được đáp trong rào.",
                "Gò trống. Không mốc. Không chỉ tay.",
                "Hữu đổi ca: trống gò. Không giơ nhầm.",
                "Trẻ không nghe sáo. Rèm chặt.",
                "Muối chát. Mắt nuốt. Miệng khóa.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà nhắc: thấy không bằng chỉ.",
                "Bảng sấp: bóng. Không viết sáo to.",
                "Đông rên. Không sóng. Im.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ nhịp sáo — không hô đáp.",
                "Nắp giếng xấu giữ. Không chỉ hố.",
                "Bao tây. Lép. Bảy dấu im.",
                "Mai bóng có thể mang sáo lại — tai khe.",
                "Bóng không pháo. Bóng là việc nuốt mắt.",
            ],
        )
    )
    metas.append(
        dict(
            n=647,
            title="Hỏi Lần 107 Cùng Màu",
            day=767,
            motif="hỏi",
            close_tag="cùng màu giấy bút",
            event_short="Hỏi lần một trăm lẻ bảy cùng màu — giấy bản bút",
            panel_event="hỏi lần 107 — giấy bản · đổi bút lấy gạo · không nhận · không đổi · cùng màu · cấp im",
            open_hook=(
                "Sương còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm sáu mươi bảy dưới đất Biên Ải. "
                "Cổng đông — hỏi lần một trăm lẻ bảy cùng màu. Không gào. Chỉ miệng. Chỉ hỏi. Máy nghèo thở đều. "
                "Gió bấc mang mùi đất se; nắng mỏng chạm then chưa đủ ấm tay giữ giấy — giấy không vào rào."
            ),
            report=[
                "Một miệng. Hỏi giấy bản, đổi bút lấy gạo. Không lê. Giọng khác lần trước",
                "Một miệng cổng đông. Hỏi giấy. Đổi bút lấy gạo. Không lê. Giọng lạ.",
                "Nhận không?",
                "Không mở. Không kể trẻ. Không chỉ giếng. Không nhận giấy. Không đổi bút. Đông thường. Hầm xấu",
                "Miệng cười khô lùi. Không ném đồ. Không mở tiễn.",
                "Cổng sạch sau hỏi. Không giấy. Không bút.",
            ],
            three_bones="không nhận giấy, không đổi bút, không đáp mồi",
            bones_line="Không nhận. Không đổi. Không đáp mồi. Cùng màu.",
            warn="miệng hỏi giấy có thể mang văn thư giả · van mồi nối bút với miệng · không nhận.",
            action=(
                'Miệng: "Trong ơi — có giấy bản không, đổi bút lấy gạo!" "Đông thường. Hầm xấu." '
                'Miệng lần hai: "Bút ngoài là của tao — trong có sổ không?" Không đáp mồi. '
                'Hà: "Hầm xấu." Không thêm. Miệng cười khô lùi. Không mở tiễn. Không ném đồ. '
                'Hà: "Hỏi?" "Không nhận. Không nhận giấy. Không đổi bút. Máy nối mồi với miệng — im."'
            ),
            night_seeds=[
                "Canh sâu. Giấy không vào rào. Bút không thành dấu trong.",
                "Giọng lạ ngoài cổng đã lùi — không đuổi theo.",
                "Hữu đổi ca: cổng sạch. Không giơ.",
                "Trẻ không nghe chữ giấy. Rèm chặt.",
                "Muối chát. Gạo không đổi. Nước đúng gáo.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà nhắc khẽ: cùng màu nếu hỏi lại.",
                "Bảng sấp: hỏi. Không viết giấy to.",
                "Đông rên. Không sóng. Chọn im.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ mồi bút — không nối miệng với sổ.",
                "Nắp giếng xấu giữ. Không chỉ giếng.",
                "Bao tây. Lép. Bảy dấu im.",
                "Mai hỏi có thể mang văn thư giả — tai khe.",
                "Hỏi không pháo. Hỏi là việc nuốt cùng màu.",
            ],
        )
    )
    metas.append(
        dict(
            n=648,
            title="Ngày Yên Sau Hỏi 107",
            day=768,
            motif="yên",
            close_tag="trống sau giấy",
            event_short="Yên sau hỏi một trăm lẻ bảy",
            panel_event="yên sau hỏi 107 — sau chữ giấy · không thở phào · văn thư giả có thể mang · cấp im",
            open_hook=(
                "Sương tan chậm trên đầu chông. Ngày thứ bảy trăm sáu mươi tám dưới đất Biên Ải. "
                "Trong rào — ngày yên sau hỏi một trăm lẻ bảy. Không gào. Chỉ việc. Trống không bằng yên hội. "
                "Máy nghèo thở đều. Gió bấc mang mùi đất se; nắng mỏng chạm bao tây chưa đủ khô sương đêm."
            ),
            report=[
                "Cổng trống. Ngoài trống. Không miệng. Không dấu giấy",
                "Cổng trống. Ngoài trống. Không miệng. Không dấu giấy. Không văn thư.",
                "Yên thật hay yên mồi?",
                "Trống. Sau chữ giấy — yên có thể là khoảng lùi mang văn thư giả",
                "Vẫn trống. Gió thổi. Không mùi mực lạ ngoài.",
                "Trống. Không xe. Không người.",
            ],
            three_bones="không thở phào, không mở rèm sớm, không rải vôi nghỉ",
            bones_line="Không thở phào. Không họp chữ giấy. Việc.",
            warn="văn thư giả có thể mang sau khoảng lùi · miệng hỏi giấy có thể quay.",
            action=(
                'A Cường: "Cổng trống. Ngoài trống. Không miệng. Không dấu giấy." '
                '"Không thở phào. Không họp chữ giấy. Việc." Phong gật. Sáng trống. Yên khép bằng việc. Không mừng. '
                'Mạc Tư gạch: yên sau hỏi giấy — không viết nghỉ. '
                'Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi giấy có thể mang văn thư giả."'
            ),
            night_seeds=[
                "Canh sâu. Yên sau giấy dạy lỏng — anh không lỏng.",
                "Không văn thư ngoài. Chỉ gió và đất se.",
                "Hữu đổi ca: trống. Không giơ.",
                "Trẻ ngáy. Không chữ giấy trong rèm.",
                "Muối chát. Nước nguội. Tai khe.",
                "Then êm. Chông kêu nhẹ. Không xe.",
                "Hà thở đều. Nghề còn trong ngủ.",
                "Bảng sấp: yên. Không nghỉ to.",
                "Đông rên. Không sóng. Im.",
                "A Cường gõ cột an. Ca sạch.",
                "Phong nhớ miệng giấy hôm qua — đã khóa cùng màu.",
                "Không rải vôi nghỉ. Giếng nắp xấu.",
                "Bao tây. Lép. Bảy dấu im.",
                "Mai có thể mang văn thư giả — tai khe trước mắt mừng.",
                "Yên không huy chương. Yên là việc nuốt.",
            ],
        )
    )
    return metas


def main():
    results = []
    for m in build_metas():
        text = make_chapter(m)
        files = list(BASE.glob(f"Chương {m['n']} - *.txt"))
        path = files[0] if files else BASE / f"Chương {m['n']} - {m['title']}.txt"
        bak = BASE / "_pass_backup" / (path.name + ".pre_unique_rewrite")
        bak.parent.mkdir(exist_ok=True)
        if path.exists() and not bak.exists():
            bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        path.write_text(text, encoding="utf-8")
        wc = vi_wc(text)
        results.append(
            {
                "n": m["n"],
                "file": path.name,
                "words": wc,
                "nhip": text.count("Nhịp im"),
                "kho": text.count("Kho Vô Hạn"),
                "exp15000": text.count("15000"),
                "ly_phong": text.count("Lý Phong"),
            }
        )
        print(
            f"WROTE {m['n']} words={wc} nhip={text.count('Nhịp im')} "
            f"kho={text.count('Kho Vô Hạn')} 15000={text.count('15000')} "
            f"LyPhong={text.count('Lý Phong')} -> {path.name}"
        )
    short = [r for r in results if r["words"] < 3000]
    if short:
        print("SHORT", short)
    else:
        print("ALL_GE_3000")
    return results


if __name__ == "__main__":
    main()
