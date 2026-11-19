# -*- coding: utf-8 -*-
"""Rewrite clone-pad chapters 640,641,643-648 as unique prose (ch622 style)."""
from pathlib import Path

BASE = Path(r"C:\Dev\MythLab\Mạt Thế Cổ Đại Cầu Sinh")

def header(n, title):
    return (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
    )

def panel(n, day, event):
    return (
        f"\n「GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"Ngày sống: {day}\n"
        f"Sự kiện: {event}\n"
        f"Cấp: im · không pháo\n"
        f"』\n"
    )

def wcount(t):
    return len([x for x in t.split() if len(x) >= 2])

# ---------- CHAPTER BODIES (unique) ----------

CH = {}

CH[640] = {
"title": "Ngày Yên Sau Hỏi 105",
"day": 760,
"event": "yên sau hỏi 105 — sau chữ vôi · không thở phào · lò vôi giả có thể mang · cấp im",
"body": r'''Sương còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm sáu mươi dưới đất Biên Ải. Trong rào — ngày yên sau hỏi một trăm lẻ năm. Không gào. Không miệng. Chỉ việc. Trống không bằng yên hội. Máy nghèo thở đều.

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ hai ngón mở — trống cả bốn hướng. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe cổng.

"Trống. Không miệng. Không dấu vôi mới," Phong đáp. Anh nhìn hướng cổng đông hai nhịp rồi quay muối. Không đuổi mắt theo quá hai nhịp — đuổi là mời khoảng lùi đọc lưng.

---

Sáng. Máy nghèo chạy ngày yên sau hỏi.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn: yên. Không viết số to. Không viết nghỉ. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. A Cường lách bóng xưởng, báo thấp:

"Cổng trống. Ngoài trống. Không miệng. Không dấu vôi. Không lò. Không xe."

"Ghi. Không thở phào. Không họp chữ vôi. Không rải vôi nghỉ. Việc," Phong nói.

Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. Lưu Diễm se xước. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể yên.

Bà già ghé: "Gió?"

"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Chân kho. Thớt không phơi. Dây không kêu. Quét miệng muốn kể trống thành chuyện sân.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu ho trống gò phía bắc. Không giơ sớm. Yên sau hỏi là việc khác — việc mắt nuốt, miệng không nhả phào.

---

Giữa sáng. Ba xương yên.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, mắt không lỏng:

"Yên thật hay yên mồi?"

"Trống. Không miệng. Không dấu vôi. Sau chữ vôi — yên có thể là khoảng lùi mang lò vôi giả," anh nói. "Ba xương: không thở phào, không mở rèm sớm, không rải vôi nghỉ."

"Rèm chặt. Trẻ không ra sân gần đông," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch."

Khuyển kéo bóng gần ngưỡng nửa bước rồi đứng. A Minh: hai ngón mở — trống. Gò không sóng. Không thước. Không bóng.

A Cường lách lại: "Vẫn trống. Gió thổi. Không mùi vôi mới ngoài."

"Không soi. Không kể," Phong dặn. A Cường biến.

Diễm buộc rèm sâu hơn một nấc. Cúc kéo Hạt vào: "Xâu trong. Không ra gần cổng." Thẻ. Cửa hờ. Trẻ khuất. Sân nhẹ. Mùi cháo loãng át mùi vôi một nhịp rồi trả lại đất se.

Bà già lại ghé, thấp hơn: "Hôm qua ồn?"

"Gió. Việc," Hà đáp. Không thêm. Không vôi. Không hỏi.

Hứa đứng cửa xưởng không liếc cổng. Dao bùn. Bùn áo. Áo nghèo. Nghèo đúng là trả lời không lời cho ngày yên dễ lỏng vai.

Phong xách thêm một thùng nước, đảo thêm hai bao lép phía tây, lau muối đến chát. Chát sau yên đắt hơn chát sau sóng — vì yên dạy lỏng, sóng dạy siết. Lỏng vai là hở mai.

---

Ngọ. Cháo sau yên.

Phong húp. Cúc: "Ngoài?"

Hà: "Trống. Xâu."

Xâu. Hạt miệng. Sân nhàm. Nham sau yên đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"Yên sau hỏi một trăm lẻ năm. Không thở phào. Không mở rèm sớm. Không rải vôi nghỉ. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau yên dễ nở — khóa việc nặng."

Gật. Máy che. Không khe đá. Không phình.

Phong đảo tây nhiều hơn đông. Hà phơi nắng xấu. A Cường: "Trống. Không xe. Không người."

"Không kể trống thành chuyện sân," Phong nói. Biến.

Bà già: "Khách?"

"Không. Gió. Việc." Hứa không liếc. Nghề.

Chú Bát không hỏi hôm qua cổng mang chữ gì. Nồi sôi. Giờ đúng. Mạc Tư không đọc to vạch yên. Ghi im. Từ Sơn bước đều. Diễm buộc rèm. Cúc Hạt xâu. Lỗ vá rèm và xâu.

Phong gặp Hà lần hai sau muối:

"Đủ? Không lệch vì trống?"

"Không lệch. Yên không phải hội. Yên là việc im," chị lau tay. "Ai thở phào ngoài lều — nặng."

"Ghi. Ai rải vôi nghỉ — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò: hai ngón mở. Trống sau yên. Không phào.

---

Chiều. Tay năm dấu nhắc. Trẻ thuốc củ thẻ. Mười hơi chân kho — còn. Hà miệng năm hay nói: gió, hầm ẩm, đông thường, trống, không bảy hố cửa đồi kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xế. Gánh gác. Không hội kể yên.

Xế. Ca đổi. Xước se. Vòng then tây bao vai. Gật đủ. Thỏ bếp tro miệng khớp trống đêm. Thở. Mùi. Đều.

Tám nhịp bếp: không phát mừng vì trống, nửa bát, củ thẻ, nồi không chuyện vôi. Gạch. Sôi. Gỗ. A Cường: không xe không người lại. Nới hàm. Nghèo không cứng.

Chiều tà Mạc Tư chú Bát bóng bếp tám nhịp: không phát vì yên, không đổi giờ ca đông, nửa bát, củ thẻ, nồi không khách. Gạch. A Cường ngắn. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi vôi. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im. Im đắt truyện.

Tháp Hà không đèn: "Yên có lớp. Mai bóng hoặc sóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Cổng trống. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Không vôi mới. Không rải nghỉ. Yên rào — không người xe, mùi dày đứng. Đứng được. Không lỏng.

Hữu đổi ca: "Trống gần. Không người." Cháo nửa thìa. "Im. Giơ người đúng. Không sóng nhầm." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc giữa chiều: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Thước đọc lưng; xương không cho đọc.

---

Tối. Lớp ba. Đèn một. Cửa đóng.

Phong xương: "Yên sau hỏi một trăm lẻ năm. Không thở phào. Không mở rèm sớm. Không rải vôi nghỉ. Đông thường. Hầm xấu. Luật. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca bù."

Khuyển: "Kể yên cộng bảy — nặng."

A Cường: "Tay. Xe tìm ta."

Mạc Tư: "Cháo. Nửa bát. Không viết số to."

Diễm: "Xước. Trẻ. Máu kín."

Tôn Vũ: "Móc. Không hun."

Hữu: "Im. Yên — giơ đúng nếu sóng."

Tan. Ngáy. Kiểm tay. Máy ngủ.

Hà tháp: "Yên có lớp. Chưa xông. Mai bóng hoặc sóng."

"Lời em. Bao anh. Cùng màu." Nắm. Muối. Mùi.

Xưởng móc mài lá khô. A Minh trống. Hữu không giơ. Đúng.

---

Canh một. Tuần tây.

Hầm đông chông vôi then hố vết. Rên thưa. Không sóng. Gò: trống. Bảy im. Chọn im.

Canh hai. Ca mới. Thuốc ngủ. "Mùi. Thỏ. Trống. Tạm yên."

"Ngủ ca. Mai bóng, sóng, hoặc hỏi."

"Máu kín nếu sóng."

Ra. Gió. Muối. Không xe. Vết nguyên. Góc sân mảnh: hầm đông trẻ tay miệng thỏ hố không kể cấp im lời Hà cùng màu yên sau hỏi không phào. Cầm thở.

Canh ba. "Cổng?"

"Trống. Dày. Không xe. Không người. Không dấu vôi."

"Ngủ."

Sổ than:

Ngày 760. Yên sau hỏi 105 — trống sau chữ vôi. Ba xương: không thở phào, không mở rèm sớm, không rải vôi nghỉ. Trống ≠ yên hội. Không kể. Nghèo. Đều. Cấp im. Bảy xương.

Chữ lóe ngắn:

『Ghi nhận: yên sau hỏi · trống · không thở phào · không rải vôi nghỉ.』
『Cảnh báo: lò vôi giả có thể mang sau khoảng lùi · miệng sau yên dễ nở.』
『Nhiệm vụ: việc im · không kể · đâm thấp nếu sóng · máy nghèo.』

Cấp im. Không pháo. Ngáy. Nằm. Nắm. "Im." "Im…"

Mơ: miệng hỏi vôi ngoài rào và thẻ. Xâu. Lò mờ. Tỉnh gió. Trống. Hữu đổi. Rên một. Nhắm.

Gà nhất. Không vội. Hà thở. Then. Mùi. Im. Bảy gối. Yên không hội miệng sân mai.

Tây xấu. Đông chông hố vết. Cổng trống. Trẻ. Người đều. Lớn thầm. Đo. Sống.

Ngày 761 chờ bóng, sóng, hỏi, mùi, mặt không biết, miệng ngậm, chông thấp. Trống bao mũi tai miệng tay. Không sống theo đã thấy trống một ngày. Sống theo đều khi mắt dễ phào.

Ngủ muối hết. Tai khe. Chưa. Tốt. Nghèo sau yên. Không phào. Củ thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ.

Yên không pháo. Cháo bao vải tay trẻ im lời cùng màu. Đủ trống. Đủ hắn đọc lưng mà không đọc được xương. Đủ bảy xương. Mai đảo đông. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe. Đất người cháo thẻ đều còn.

Gà hai. Nước. Bảy im. Nằm. Tay Hà. Mùi. Thở. Cấp im. Chông. Gió. Nghi. Ta sống. Yên khép im — im đắt nở miệng dưới trời này.

Gió dài. Mắt: chông thẻ Hà cửa vết cổng trống lời ba xương yên. Giữ. Không kể bảy. Không rải vôi. Không pháo. Đất lưng. Ngủ sau yên. Mai chủ nghèo — không bia mồi miệng.

Rên tắt. Không dậy. Tai khe. Im. Hà nắm. Ngủ. Sau yên không cột đêm. Sức trống kế chông mặt không biết mang bảy hố xương sân gió bao.

Mai trống cháo bao mùi. Máy nghèo. Then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm.

---

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng trên tháp không thắp đèn thêm, đếm then cổng trong đầu: không kêu. Đông rên một tiếng đứt quãng rồi im. Cổng trống. Không dấu vôi mới.

Hà ghé vai anh một nhịp: "Đều."

"Đều," anh đáp. Hai chữ đủ cho trước trống điểm.

Dưới sân, Hữu đổi ca gò bằng một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lặp như sương, không ồn, không thiếu.

Phong ghi sổ đầu giường thêm ba dòng rồi gạch nhẹ cho khỏi kể công: mùi đông theo dõi; không đồn sân; mặt nghèo giữ; yên sau hỏi không phào. Chữ lóe ngắn rồi tắt. Anh gấp sổ, nắm tay Hà, nằm. Ngoài rào không xe, không xẻng, không sóng. Chỉ đất Biên Ải và trại biết nghèo đúng cách — nghèo đến mức thước đọc lưng mà không đọc được xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ để thắng tiếp ván không tên dưới trời này.

Phong còn ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im cũng là gác lần hai. Gác bằng tai khi mắt phải ngủ. Yên sau hỏi một trăm lẻ năm khép bằng tai khe — không bằng thở phào.

Trống điểm kế sẽ mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm. Nhưng hôm nay đã viết việc đủ — thấy trống, nuốt mắt, không phào, không rải, không họp. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm sẽ chạm cổng. Ai phào — hở. Ai rải vôi nghỉ — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
'''
}

# Continue building remaining chapters in next write...
print('ch640 body words', wcount(CH[640]['body']))
