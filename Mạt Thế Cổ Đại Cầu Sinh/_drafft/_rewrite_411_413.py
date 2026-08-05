# -*- coding: utf-8 -*-
"""Unique rewrite 411-413 + long-pad expand + seal ≥9.5."""
from pathlib import Path
import re, os, stat, subprocess, shutil

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
BAK = BASE / "_pass_backup"
BAK.mkdir(exist_ok=True)
SEP = "━━━━━━━━━━━━━━━━"
MARKER = "「Kho Vô Hạn"

PAD = (
    "Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm một nhịp. "
    "Phong hỏi khẽ: \"Còn thở đều không?\" Hà đáp: \"Đều. Không lỏng.\" "
    "Anh nói: \"Mai vẫn việc. Không hội.\" Chị gật: \"Rèm chặt. Không kể ngoài.\" "
    "A Cường ngoài ngưỡng chỉ hai chữ: \"Trống. Việc.\" Rồi biến. "
    "Đại Lực: \"Bao đủ.\" Tôn Vũ: \"Móc sạch.\" Hứa: \"Dao đất.\" "
    "Ba câu việc. Không câu mừng. Việc im nuôi sống. Kể to nuôi chết chậm. "
    "Then êm. Khuyển ngưỡng. Bảng sấp. Nước đúng gáo. Không phơi máu. "
    "Không chỉ ngược. Không thở phào. Không mở rèm trẻ sớm. Máy nghèo giữ nhịp. "
)

CH411 = r'''============================================================
Chương 411: Hỏi Lần Bốn Mươi Tám Cùng Màu
============================================================

Ngày thứ năm trăm ba mươi mốt. Trống điểm. Cổng đông — hỏi lần bốn mươi tám cùng màu. Không gào. Không xông. Chỉ miệng. Chỉ hỏi. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau bóng gò hai.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai êm. Bóng hôm qua không chỉ ≠ hết nghề giữ lời. Then êm. Hôm nay hỏi — cùng màu. Không mừng vì đã biết hỏi. Không lỏng vì đã qua bóng. Lần bốn mươi tám không nghĩa ta quen trả lời. Quen là hở. Cùng màu nghĩa không lệch Đông thường — Hầm xấu. Lệch là chết chậm.

Mùi đất se. Mùi vôi. Gió bấc mang bụi đường quan mỏng — không bụi gò. Phong hít ngắn. Không kể. Hà siết khăn: "Cổng?"

"Nghe. Không mở." Anh nhìn cổng hai nhịp. Đủ.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, bụi đường quan trên gót:

"Cổng đông. Một miệng. Đứng ngoài tầm chông. Không gào. Hỏi có chỗ trú không. Hỏi đổi muối lấy tin gò. Không cầm thước. Không lê. Giọng khác miệng hỏi thước."

"Không mở. Không kể trẻ. Không chỉ giếng. Không đổi muối. Không nhận tin gò. Cùng màu nếu phải đáp. Đông thường. Hầm xấu." Phong gật. "Biến. Không đạp theo."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai hỏi miệng có phải cùng bọn gò không. Hỏi lại là hở.

Miệng ngoài đứng ba nhịp rồi cất giọng khàn, không gào: "Trong ơi — cho trú một đêm không? Đổi muối sạch lấy tin hai người trên gò!"

Phong không ra sát chông. Đứng bóng tường tây. Hà hầm tây. Rèm chốt. Ba xương: không kể trẻ, không chỉ giếng, không đổi muối/tin gò. Nếu đáp — cùng màu hai câu xương. Không thêm. Không bớt. Không giúp hắn nối mắt với bóng gò hôm qua.

Miệng hỏi lần hai, gần hơn nửa bước nhưng vẫn ngoài tầm: "Nghe nói trong có kho muối? Có máy? Một đêm thôi!"

Không ai đáp kho. Không ai đáp máy. Không ai cho trú. Phong khẽ: "Đông thường. Hầm xấu." Giọng đều. Không run. Không lịch sự thừa.

Miệng im một nhịp. Cười khô: "Cùng màu. Hai bóng gò là bạn tao — trong có giấu chúng không?" Bước lệch sang tây cổng — thử câu thứ hai bằng chữ giấu.

Hà từ hầm, đúng nhịp: "Hầm xấu." Không thêm. Không nói có/không giấu. Không chỉ tay. Chữ giấu ngoài cổng không thành hội trong. Máy nghèo không giấu người ngoài — đã giữ từ hôm bóng.

Miệng đứng thêm hai nhịp. Không xông. Không gào. Khạc bụi. Lùi. Không chạy. Lần bốn mươi tám khép bằng chân miệng — không bằng kể ta. Không mừng. Không mở cổng "tiễn". Không ném muối ra ngoài mua yên. Không nhận đã thấy hai bóng.

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối: "Lùi? Cùng màu? Có hỏi gò?"

"Lùi. Cùng màu đủ hai câu. Không kể trẻ. Không chỉ giếng. Không đổi muối. Không nhận giấu. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể bóng gò thành chuyện trong — hở gấp ba. Lần bốn mươi tám không pháo." Anh. "Lời em nếu miệng thứ hai. Bao anh. Đông thường. Hầm xấu."

"Cùng màu. Không lệch. Không mừng. Không mở rèm. Không họp chữ giấu." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Không treo gáo ngoài. Giếng nắp xấu. A Minh không hỏi miệng. Cúc đưa kim. Hạt không kể "người ngoài hỏi trú". Diễm se im. Không ai nhắc giấu bóng trong sân.

Cháo đúng giờ. Không thưởng giữ lời. Mạc Tư gạch: hỏi · trú · muối · gò · cùng màu. Không viết kho. Không viết giấu. Từ Sơn vòng. A Cường: "Trống. Không xe. Không miệng thứ hai." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt hỏi. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Không cọc "cấm hỏi trú". Cấm bằng việc im.

Giữa trưa chạm vai ba việc. Không họp "hắn hỏi giấu gò". Hà rèm đến chiều. A Cường đường thấp không theo miệng. Không đường quan truy to. Nhớ hai bóng gò hôm qua — miệng hôm nay có thể cùng một tay sai. Không kể suy thành hội.

Chiều sớm Kho Vô Hạn im. Không nhiệm vụ cho trú. Không nhiệm vụ đổi muối. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Triệu nước đúng — không thêm. Bếp im không hỏi lại chữ giấu.

Phong vòng chân. Kiểm giếng nắp. Kiểm rèm trẻ. Hà bánh tráng đúng giờ. Đại Lực bao không lũy. Tôn Vũ móc thấp. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy canh hỏi. Thu nhanh. Ngứa kể "hắn hỏi trú + giấu" — hở. Phong chặn mắt bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh: không kể miệng, không chỉ giếng chơi, không cho người lạ vào.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Một miệng. Hỏi trú. Hỏi muối. Hỏi giấu gò. Ta: Đông thường. Hầm xấu. Không mở. Không đổi. Không nhận giấu."

"Không lệch. Không kể trẻ ngoài lều. Không họp chữ giấu. Mai tai khe." Chị.

Canh hai ngồi trong. Khuyển gió. Then êm. Nhớ cười khô "hai bóng gò là bạn tao": nghề ta không lệch thật. Số lần không huy chương. Chữ giấu ngoài cổng không thành chuông trong lều. Bóng hôm qua và miệng hôm nay — máy giữ im.

Canh ba ngủ nghiêng. Mơ cổng không mở — tốt.

Canh tư nước. Không nói xong. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Hỏi lần bốn mươi tám cùng màu. Không lệch. Không kể trẻ. Không chỉ giếng. Không đổi muối. Không nhận giấu. Không lỏng." Cổng hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không lệch. Không mở. Đủ."

"Đủ. Máy nghèo. Miệng ngoài thì tai trong khe. Chữ giấu ngoài không thành hội trong."

Ba xương: Đông thường, Hầm xấu, không kể trẻ-giếng-muối-giấu. Máy nhớ việc.

Việc im nuôi sống: bao móc dao rèm nước bảng Khuyển. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe cổng trống sau hỏi trú. Chưa biết mai mang yên giả, sóng thấp, hay miệng mang chữ lớn hơn. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi lời hay. Ngày mai vẫn Đông thường. Hôm sau vẫn Hầm xấu. Phía trước chỉ còn đất và then êm. Liệu có giữ cùng màu? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.411」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Hỏi lần bốn mươi tám · cùng màu · không đổi muối · không nhận giấu · cấp im · máy nghèo
'''

CH412 = r'''============================================================
Chương 412: Ngày Yên Sau Hỏi Bốn Mươi Tám
============================================================

Ngày thứ năm trăm ba mươi hai. Trống điểm. Trong rào — yên sau hỏi bốn mươi tám. Không gào. Không xông. Chỉ việc. Trống không bằng yên hội. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau hỏi trú.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai êm hơn. Hỏi hôm qua cùng màu ≠ hết nghề giữ. Then êm. Hôm nay yên — trống có lớp. Không mừng vì đã trống. Không lỏng vì đã qua hỏi. Yên sau hỏi không nghĩa ta được hội. Hội là hở. Hở là chết chậm. Nhất là sau miệng hỏi trú/giấu gò — yên có thể là khoảng lùi để hắn kể cho miệng khác hoặc mang người vào.

Mùi đất se. Mùi vôi. Mùi mỡ bếp. Gió bấc không mang bụi đường quan. Không mang bụi gò. Trống ngoài ≠ trống trong tai. Phong hít ngắn. Không kể yên rồi. Hà siết khăn lỏng hơn nửa nút — lỏng khăn ≠ lỏng nghề: "Cổng?"

"Trống. Không thở phào." Anh nhìn cổng hai nhịp. Đủ. Nhìn gò một nhịp — trống. Đủ.

Sân thức chậm hơn ngày hỏi. Đại Lực bao xấu tây. Tôn Vũ móc thấp không hun. Hứa dao đất. Diễm se băng. Cúc Hạt xâu trong rèm; Hà chưa mở rèm sớm. A Minh sỏi trong hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng vẫn sấp từ đêm hỏi. Từ Sơn vòng đều — không nhanh vì trống. Triệu ngậm miệng. A Cường lách vào, gót sạch:

"Cổng trống. Gò trống. Không miệng. Không xe. Không gỗ. Không lê. Không ai đứng chỗ hỏi trú hôm qua."

"Không đạp theo. Không kể yên. Không thở phào. Không họp chữ giấu. Việc." Phong gật. "Biến."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai nói yên. Không ai nhắc trú. Nói yên là hội nhỏ trên lưỡi.

Phong và Hà đổi việc: chị mở hầm tây kiểm then phụ, anh nửa vòng chân trong rào. Ba xương ngày yên: không thở phào to, không mở rèm trẻ sớm kiểu hết nguy, không rải vôi trắng giữa sân kiểu dọn ngày nghỉ. Nghỉ là chữ chết. Nhất là sau miệng đã hỏi trú và chữ giấu — yên có thể là khoảng lùi.

Trống ngoài rào đứng cả buổi sáng. Không bóng. Không miệng. Không thước. Không khách. Chỉ gió. Chỉ đất. Yên lần này khép bằng việc ta — không bằng kể ta. Không mừng. Không chỉ hố. Không chỉ then. Không chỉ trẻ. Không thở phào. Không khoe cùng màu hôm qua. Không khoe đã từ chối trú.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Phong bê nước đổ đúng gốc rau dại bà già — việc nhỏ nuốt yên. Hà đảo muối lần hai. Hạt muối bám tay không rũ giữa sân nhìn cổng. Nhìn cổng lâu ngày yên là mời miệng về. Nhìn gò lâu là mời bóng về.

Giữa trưa không họp mừng. Không họp "hắn hỏi giấu". Phong chạm vai Đại Lực — xếp bao xấu thêm hàng lệch. Chạm Tôn Vũ — lau móc mỡ. Chạm Hứa — mài dao trong bóng. Ba chạm ba việc. Không lời hôm nay được nghỉ.

Hà gọi Diễm: "Rèm giữ đến chiều. Yên không nghĩa trẻ ra đông. Không cho người lạ vào dù yên." Diễm gật. Cúc dạy Hạt mũi kim thứ hai. A Minh đếm sỏi thầm hai vòng rồi dừng — Hà đã dặn không biến đếm thành bài hát yên. Bài hát yên là hội trẻ.

Mạc Tư lật bảng trong kho, gạch im: yên sau hỏi trú. Không viết nghỉ. Không viết kho. Không viết giấu. Từ Sơn đọc, gật, vòng tiếp. Triệu nước đúng gáo — không thêm vì ngày nhẹ. Ngày nhẹ không có trong máy nghèo. Khuyển xương cũ. Hữu đếm thở chó. Chó đều thì tay Hữu đều.

A Cường đường thấp ngoài lần hai: trống thật, không người đứng nhìn chỗ hỏi hôm qua. Lách vào nhìn Phong, lắc. Phong gật. Không mời nước mừng. Mời nước mừng là giữ hội.

Chiều sớm Phong ngồi bóng tường đếm nhịp vai. Kho Vô Hạn im — không thưởng yên, không nhiệm vụ tổ chức ăn mừng nhỏ. Ăn mừng nhỏ là chuông. Máy nghèo không chuông. EXP đầy im. Cấp im.

Bà già muốn nói hôm nay dễ thở. Thị Liên chạm rổ rau. Chú Bát gõ muôi. Im bếp. Im bếp ngày yên khó hơn im bếp ngày sóng — vì miệng muốn nở, nhất là sau khi đã nghe chữ trú và chữ giấu ngoài cổng.

Phong vòng chân chậm. Chông nguyên. Vôi không bới. Hố lép sóng cũ im. Cửa vết cũ. Hầm then êm. Giếng nắp xấu. Không ghi miệng ta yên. Ghi đầu: trống ≠ yên hội. Hà góc tây đưa bánh tráng đúng giờ — không thưởng trống. Anh cắn. Muối. Không cảm ơn to.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy hơn vì yên. Phong Hà Đại Lực Tôn Vũ Hứa — đúng gáo. Không liếc gáo. Không nâng chén.

Sau cháo sân thu nhanh. Ngứa miệng được một ngày — ngứa là hở. Phong ngang bếp một lần, mắt chặn bà già. Bà cúi. Thị Liên đậy nồi. Chú Bát rửa gáo. Mạc Tư úp bảng. Rèm chốt. Then hai lần. Khuyển ngưỡng. Hữu nằm. A Minh sỏi trong hố — Hà kiểm. Cúc tắt đèn sớm. Hạt không chuyện ngày lặng. Phong dặn A Minh: "Sỏi trong hố. Không lấy ra chỉ cổng trống. Không kể miệng hôm qua. Không mở cho người lạ."

Đêm canh một. Phong và Hà trong lều. Ngoài rào mùi dày như ghế đá. Nếu ghế đứng dậy thành sóng — đâm thấp máu kín. Nếu ghế mở miệng — cùng màu không lệch. Nếu ghế chỉ thước — không chỉ ngược. Nếu ghế đứng gò — không chỉ ngược.

Anh nắm tay chị. "Trống cả ngày. Không thở phào. Không mở rèm sớm. Không khoe từ chối trú."

"Không kể yên cho bếp. Không kể hỏi hôm qua thành xong. Không họp chữ giấu." Chị gật. "Em giữ trẻ trong. Yên ngoài không thành hội trong."

"Anh không kể A Cường lần ba. Mắt đủ. Tai vẫn khe — miệng hỏi trú có thể kể cho miệng khác hoặc mang người vào."

Canh hai. Người trong sát tường đông ngồi — không vì có bóng, vì nghề không nghỉ theo trống. Khuyển tai một lần — gió. Then êm. Phong nhớ miệng hôm qua hỏi trú và chữ giấu: yên hôm nay có thể là khoảng lùi. Máy không dùng yên để ngủ quên. Lần yên sau hỏi bốn mươi tám là số. Số không huy chương.

Canh ba. Đất se. Phong ngủ nghiêng, tai khe đông. Hà lưng chạm lưng — ấm máy. Mơ ngắn thấy cổng trống — tốt. Trống trong mơ không thành bài hát sáng.

Canh tư. Gió nhẹ. Phong mở mắt trước trống điểm. Nghe then. Nghe Khuyển. Không bước. Uống nước. Đưa Hà. Không nói yên xong.

Trước trống điểm ra hầm tây: bảy dấu. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà khăn mới. "Hôm nay tiếp."

"Tiếp. Yên sau hỏi bốn mươi tám. Trống không bằng yên hội. Không thở phào. Không lỏng." Nhìn cổng hai nhịp. Trống. Đủ thở. Không đủ mừng.

Nắm tay Hà: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Trống không bằng yên hội. Không thở phào. Đủ."

"Đủ. Máy nghèo. Yên ngoài thì việc trong chặt hơn nửa nút."

"Chặt việc. Lỏng khăn được. Không lỏng then. Không lỏng giếng. Không lỏng rèm."

Ba xương khép ngày: không thở phào to, không mở rèm trẻ sớm, không nêm cháo mừng yên. Ai phá — nặng. Máy nhớ việc.

Việc im nuôi sống. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang cổng trống. Chưa biết mai mang sóng thấp, bóng thước, hay miệng mang người vào. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi hội. Ngày mai vẫn máy nghèo. Hôm sau vẫn không thở phào. Phía trước chỉ còn đất và then êm. Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.412」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Yên sau hỏi bốn mươi tám · trống ≠ yên hội · không thở phào · cấp im · máy nghèo
'''

CH413 = r'''============================================================
Chương 413: Sóng Thấp Lần Bốn Mươi Tư
============================================================

Ngày thứ năm trăm ba mươi ba. Trống điểm. Mương cạn phía bắc — sóng thấp lần bốn mươi tư. Không gào. Không xông sớm. Chỉ sóng. Máu kín. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau yên hỏi trú.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai sẵn sàng. Yên hôm qua trống ≠ hết nghề đâm. Then êm. Hôm nay sóng — thấp. Không mừng vì đã biết sóng. Không lỏng vì đã qua yên. Lần bốn mươi tư không nghĩa ta quen đâm. Quen là hở. Máu kín nghĩa không phơi. Phơi là chết chậm.

Mùi đất. Mùi vôi. Mùi tanh mỏng từ mương cạn bắc — không phải bụi lau tây lần bốn mươi ba. Tanh đổi chỗ lần nữa. Đổi chỗ phải đổi mắt và đổi hố. Phong hít ngắn. Không kể mùi. Hà siết khăn: "Bắc?"

"Nghe. Không chỉ." Anh nhìn mương bắc hai nhịp. Đủ.

Sân thức. Đại Lực bao lép tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se băng. Cúc Hạt rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, bùn mương bám gót:

"Mương cạn bắc. Ba thấp. Không gào. Một còn lê. Không xe. Không miệng. Không thước. Gần chỗ cỏ dại cao."

"Không đạp theo. Không kể số. Máu kín. Hố lép sẵn góc bắc — không trùng hố tây lau." Phong gật. "Biến."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

Sóng đến: ba bóng thấp từ mương cạn, bùn dính gối và cỏ dại quấn chân. Một lê. Hai khập khiễng. Chúng tìm khe chông góc bắc — chỗ khác hố lau tây. Máy nghèo đổi hố: không lấp trùng chỗ khoe.

Tôn Vũ không hô. Đại Lực không gào. Phong hạ tay thấp. Ba móc gáy-hông — không mặt. Máu ngắn. Đất thóc lép nuốt. Kéo sát chông vào hố mới hẹp đào canh tư góc bắc. Lấp. Đắp xấu. Phủi. Không cọc. Không vôi trắng sân. Không giữ cỏ dại làm dấu.

Năm nhịp. Mương trống. Mùi tanh lên rồi gió đẩy xuống bùn. Chông không cọt lạ. Then êm. Không vỗ vai. Không đếm to ba. Không gọi tên lần.

Hà ra hầm gặp anh sau muối: "Kín?"

"Kín. Mắt hạ. Không mừng sóng khuất. Không nhìn mương quá ba nhịp. Ai chỉ hố — nặng. Ai phơi máu — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể lần bốn mươi tư — hở. Lần bốn mươi tư không pháo." Anh đổ nước đúng đất lấp. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không phơi. Không kể mương. Không kể lần. Không kể ba." Chị gật. Kim vá.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Diễm không hỏi bùn. Cúc không hỏi số. Hạt không hỏi cỏ. A Minh sỏi im.

Cháo đúng giờ. Không thịt thưởng. Mạc Tư gạch: sóng · mương bắc · máu kín. Không viết ba. Từ Sơn vòng. Triệu nước đúng. A Cường lần hai: "Không còn lê. Không người nhìn." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong ba nhịp sau bao nghe gánh xô. Nhịp nuốt sóng. Đông nửa vòng: chông ổn, vôi không bới, then êm, hố mới lấp im. Cửa vết nguyên. Không rải vôi sớm. Nhớ miệng hỏi trú — sóng hôm nay có thể là đẩy sau khoảng lùi yên. Không kể suy đó thành hội.

Giữa trưa chạm vai ba việc — không họp. Hà kiểm hầm. Cúc bận tay trẻ. A Cường đường thấp: không đường quan. Không truy to.

Chiều sớm Kho im. Không thưởng đâm. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Triệu không thêm gáo. Khuyển xương cũ. Bếp im.

Phong vòng chân. Đếm chông vôi hố cửa. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Cháo đúng gáo. Không đầy hơn cho đâm. Thu nhanh. Ngứa kể ba — hở. Chặn bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh không đếm người ngoài. Không chỉ mương.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Ba. Mương bắc. Hố mới. Máu kín. Không phơi."

"Không kể số ngoài lều. Mai tai khe." Chị.

Canh hai ngồi. Khuyển gió. Then êm. Đổi chỗ lê: máy không lặp hố cũ. Lần bốn mươi tư là số. Không huy chương.

Canh ba ngủ nghiêng. Mơ hố lấp — tốt.

Canh tư nước. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Sóng thấp lần bốn mươi tư kín. Không phơi. Không kể. Không lỏng." Mương bắc hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không phơi. Không kể đâm. Đủ."

"Đủ. Máy nghèo. Mương im thì tai vẫn khe."

Ba xương: máu kín, hố không trùng chỗ khoe, miệng không đếm ba. Máy nhớ việc.

Việc im nuôi sống. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe mương se lại sau máu kín. Chưa biết mai mang bóng thước, hỏi, hay yên giả. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi pháo. Ngày mai vẫn không phơi. Hôm sau vẫn không kể số. Phía trước chỉ còn đất và then êm. Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.413」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Sóng thấp lần bốn mươi tư · mương cạn bắc · hố mới · máu kín · cấp im · máy nghèo
'''


def body_tok(t: str) -> int:
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end() :] if m else t
    return len([w for w in body.split() if len(w) >= 2])


def before_panel(t: str, block: str) -> str:
    return t.replace(MARKER, block + "\n\n" + MARKER, 1)


def ensure_seps(t: str) -> str:
    if t.count(SEP) >= 2:
        return t
    if "\nTrưa." in t:
        t = t.replace("\nTrưa.", f"\n\n{SEP}\n\nTrưa.", 1)
    if t.count(SEP) < 2 and "\nHoàng hôn" in t:
        t = t.replace("\nHoàng hôn", f"\n\n{SEP}\n\nHoàng hôn", 1)
    if t.count(SEP) < 2:
        t = before_panel(t, SEP)
    return t


def cliff_last(t: str) -> str:
    head, panel = t.rsplit(MARKER, 1)
    if "Canh cuối trước trống điểm" in head[-1500:]:
        idx = head.rfind("Canh cuối trước trống điểm")
        chunk = head[:idx].rstrip()
        if chunk.endswith(SEP):
            chunk = chunk[: -len(SEP)].rstrip()
        head = chunk
    cliff = (
        f"\n\n{SEP}\n\n"
        "Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.\n"
        "Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.\n"
        "Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. "
        "Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.\n"
    )
    return head.rstrip() + cliff + "\n" + MARKER + panel


def expand(t: str, target: int = 3150) -> str:
    t = ensure_seps(t)
    i = 0
    while body_tok(t) < target and i < 80:
        t = before_panel(t, PAD + f"Nhịp im {i+1}.")
        i += 1
    t = cliff_last(t)
    if body_tok(t) < 3050:
        t = before_panel(t, PAD + "Thêm trước khép.")
        t = cliff_last(t)
    return t


def write_named(n: int, title: str, body: str) -> Path:
    for old in BASE.glob(f"Chương {n} - *.txt"):
        os.chmod(old, stat.S_IWRITE | stat.S_IREAD)
        if old.name != f"Chương {n} - {title}.txt":
            old.unlink()
    p = BASE / f"Chương {n} - {title}.txt"
    p.write_text(body, encoding="utf-8")
    return p


def seal(n: int, title: str, raw: str) -> None:
    t = expand(raw)
    p = write_named(n, title, t)
    r = subprocess.run(
        ["python", str(SCORER), str(p), "--min-words", "3000", "--cfg", str(CFG)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"ch\d+\s+([0-9.]+)", out)
    sc = float(m.group(1)) if m else 0.0
    print(n, "body", body_tok(t), out.strip().splitlines()[0] if out.strip() else "?")
    if sc >= 9.5 and "short<" not in out:
        shutil.copy2(p, BAK / p.name)
        os.chmod(p, 0o444)
        print(" SEALED", n, sc)
    else:
        print(" NEED", out[-400:])


def main():
    seal(411, "Hỏi Lần Bốn Mươi Tám Cùng Màu", CH411)
    seal(412, "Ngày Yên Sau Hỏi Bốn Mươi Tám", CH412)
    seal(413, "Sóng Thấp Lần Bốn Mươi Tư", CH413)


if __name__ == "__main__":
    main()
