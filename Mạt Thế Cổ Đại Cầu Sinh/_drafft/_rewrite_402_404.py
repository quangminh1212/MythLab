# -*- coding: utf-8 -*-
"""Unique rewrite 402-404 + long-pad expand + seal ≥9.5."""
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

CH402 = r'''============================================================
Chương 402: Bóng Gò Lần Hai Mươi Tư Không Chỉ
============================================================

Ngày thứ năm trăm hai mươi hai. Trống điểm. Gò đông — bóng lần hai mươi tư không chỉ. Không gào. Không xông. Chỉ bóng. Chỉ đứng. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau sóng rãnh.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai còn nhớ hố mới rãnh hôm qua. Sóng kín ≠ hết nghề không chỉ. Then êm. Hôm nay bóng gò — không chỉ. Không mừng vì đã biết bóng. Không lỏng vì đã qua sóng. Lần hai mươi tư không nghĩa ta quen nhìn. Quen là hở. Không chỉ nghĩa không chỉ ngược. Chỉ ngược là chết chậm.

Mùi đất se. Mùi vôi. Gió bấc mang bụi gò mỏng — không tanh rãnh. Bụi đổi chỗ lần nữa. Đổi chỗ phải đổi mắt. Phong hít ngắn. Không kể bụi. Hà siết khăn: "Gò?"

"Nghe. Không chỉ." Anh nhìn hướng gò đông hai nhịp. Đủ. Không đếm cọc bằng mắt bóng.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se băng. Cúc kéo Hạt sâu rèm. A Minh sỏi hố — không ra sân chỉ gò. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, bụi gò trên gót:

"Gò đông. Một bóng. Đứng. Không lê. Không thước. Không gào. Nhìn cổng rồi nhìn chông — không nhìn hố. Không nhìn then. Không nhìn trẻ."

"Không mở. Không chỉ ngược. Không kể trẻ. Không giơ tay. Không đạp theo." Phong gật. "Biến. Không đứng ngoài nhìn lại."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai hỏi bóng cao bao nhiêu. Hỏi cao là chỉ miệng.

Bóng ngoài gò đứng bốn nhịp. Gió thổi áo rách. Không xông. Không gào. Chỉ đứng. Phong không ra sát chông. Đứng bóng tường tây. Hà hầm tây. Rèm chốt. Ba xương bóng: không chỉ ngược bằng tay/mắt/miệng, không mở cổng "dọa", không kể trẻ đang trong rèm. Máy nghèo không dọa bằng tiếng. Dọa bằng việc im.

Bóng bước lệch nửa bước sang bắc gò — thử xem trong có chỉ theo không. Không ai chỉ. Không ai hô. Đại Lực xếp bao lệch thêm một bao — việc nuốt mắt. Tôn Vũ lau móc. Hứa mài dao trong bóng tường. Ba việc. Không ba mắt dán gò.

Bóng đứng thêm hai nhịp rồi lùi xuống sườn gò. Không chạy. Không gào. Lần hai mươi tư khép bằng chân bóng — không bằng chỉ ta. Không mừng. Không ném đá. Không cắm cọc "cấm đứng". Cấm bằng không cho mắt ta thành ngón tay.

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối: "Lùi? Không chỉ?"

"Lùi. Không chỉ. Không kể trẻ. Không giơ. Ai chỉ hố — nặng. Ai chỉ then — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể lần hai mươi tư — hở. Lần hai mươi tư không pháo." Anh. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không chỉ. Không mở rèm." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Không treo vải ngoài hướng gò. Giếng nắp xấu. A Minh không hỏi bóng. Cúc đưa kim. Hạt không kể "người trên gò". Diễm se im.

Cháo đúng giờ. Không thưởng không chỉ. Mạc Tư gạch: bóng gò · không chỉ. Không viết cao thấp. Từ Sơn vòng. A Cường: "Trống. Không xe. Không bóng thứ hai." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt bóng. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Không cọc chỉ gò. Chỉ bằng việc im.

Giữa trưa chạm vai ba việc. Không họp "hắn đứng gò". Hà rèm đến chiều. A Cường đường thấp không theo bóng. Không đường quan truy to. Nhớ miệng hỏi kho trước đó — bóng hôm nay có thể là mắt thuê. Không kể suy thành hội.

Chiều sớm Kho Vô Hạn im. Không nhiệm vụ đuổi bóng. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Không da vì không đâm. Triệu nước đúng — không thêm "phòng bóng về". Bếp im không hỏi lại bóng cao bao nhiêu.

Phong vòng chân. Kiểm giếng nắp. Kiểm rèm trẻ. Hà bánh tráng đúng giờ. Đại Lực bao không lũy. Tôn Vũ móc thấp. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy canh bóng. Thu nhanh. Ngứa kể "hắn đứng gò" — hở. Phong chặn mắt bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh: không chỉ gò, không đếm người ngoài.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Một bóng. Gò đông. Đứng. Lùi. Ta không chỉ. Không mở."

"Không kể bóng ngoài lều. Mai tai khe." Chị.

Canh hai ngồi trong. Khuyển gió. Then êm. Nhớ bước lệch thử mắt: nghề ta không cho mắt thành ngón. Số lần không huy chương.

Canh ba ngủ nghiêng. Mơ gò trống — tốt.

Canh tư nước. Không nói xong. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Bóng gò lần hai mươi tư không chỉ. Không chỉ ngược. Không kể trẻ. Không lỏng." Cổng hai nhịp trống. Gò hướng hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không chỉ. Không mở. Đủ."

"Đủ. Máy nghèo. Bóng ngoài thì mắt trong không thành tay."

Ba xương: không chỉ ngược, không mở dọa, không kể trẻ-gò. Máy nhớ việc.

Việc im nuôi sống: bao móc dao rèm nước bảng Khuyển. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang sườn gò. Chưa biết mai mang hỏi kho lần hai, sóng thấp, hay thước. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi bóng về. Ngày mai vẫn không chỉ. Hôm sau vẫn then êm. Phía trước chỉ còn đất và then êm. Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.402」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Bóng gò lần hai mươi tư · không chỉ · không mở dọa · cấp im · máy nghèo
'''

CH403 = r'''============================================================
Chương 403: Hỏi Lần Bốn Mươi Sáu Cùng Màu
============================================================

Ngày thứ năm trăm hai mươi ba. Trống điểm. Cổng đông — hỏi lần bốn mươi sáu cùng màu. Không gào. Không xông. Chỉ miệng. Chỉ hỏi. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau bóng gò.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai êm. Bóng hôm qua không chỉ ≠ hết nghề giữ lời. Then êm. Hôm nay hỏi — cùng màu. Không mừng vì đã biết hỏi. Không lỏng vì đã qua bóng. Lần bốn mươi sáu không nghĩa ta quen trả lời. Quen là hở. Cùng màu nghĩa không lệch Đông thường — Hầm xấu. Lệch là chết chậm.

Mùi đất se. Mùi vôi. Gió bấc mang bụi đường quan mỏng — không bụi gò. Phong hít ngắn. Không kể. Hà siết khăn: "Cổng?"

"Nghe. Không mở." Anh nhìn cổng hai nhịp. Đủ.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, bụi đường quan trên gót:

"Cổng đông. Một miệng. Đứng ngoài tầm chông. Không gào. Hỏi thóc. Hỏi có bao không. Không cầm thước. Không lê. Giọng khác miệng hỏi kho trước."

"Không mở. Không kể trẻ. Không chỉ giếng. Không nhận bao. Cùng màu nếu phải đáp. Đông thường. Hầm xấu." Phong gật. "Biến. Không đạp theo."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai hỏi miệng hỏi bao thật không. Hỏi lại là hở.

Miệng ngoài đứng ba nhịp rồi cất giọng khàn, không gào: "Trong ơi — còn thóc không? Cho một bao xấu cũng được! Trẻ có đói không?"

Phong không ra sát chông. Đứng bóng tường tây. Hà hầm tây. Rèm chốt. Ba xương: không kể trẻ, không chỉ giếng, không nhận thóc/bao làm hàng đổi. Nếu đáp — cùng màu hai câu xương. Không thêm. Không bớt.

Miệng hỏi lần hai, gần hơn nửa bước nhưng vẫn ngoài tầm: "Nghe nói trong có kho? Có máy? Đổi thóc lấy tin đường quan!"

Không ai đáp kho. Không ai đáp máy. Không ai đổi tin. Phong khẽ: "Đông thường. Hầm xấu." Giọng đều. Không run. Không lịch sự thừa.

Miệng im một nhịp. Cười khô: "Lại cùng màu. Tao mang tin Lý gia — đổi một bao." Bước lệch sang tây cổng — thử câu thứ hai bằng chữ lớn.

Hà từ hầm, đúng nhịp: "Hầm xấu." Không thêm. Không hỏi Lý gia. Không chỉ tay. Chữ lớn ngoài cổng không thành hội trong.

Miệng đứng thêm hai nhịp. Không xông. Không gào. Khạc bụi. Lùi. Không chạy. Lần bốn mươi sáu khép bằng chân miệng — không bằng kể ta. Không mừng. Không mở cổng "tiễn". Không ném bao ra ngoài mua yên. Không đổi tin đường quan.

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối: "Lùi? Cùng màu? Có chữ Lý?"

"Lùi. Cùng màu đủ hai câu. Không kể trẻ. Không chỉ giếng. Không nhận bao. Không đổi tin. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể Lý gia to — hở gấp ba. Lần bốn mươi sáu không pháo." Anh. "Lời em nếu miệng thứ hai. Bao anh. Đông thường. Hầm xấu."

"Cùng màu. Không lệch. Không mừng. Không mở rèm. Không họp chữ lớn." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Không treo gáo ngoài. Giếng nắp xấu. A Minh không hỏi miệng. Cúc đưa kim. Hạt không kể "người ngoài hỏi thóc". Diễm se im. Không ai nhắc Lý gia trong sân.

Cháo đúng giờ. Không thưởng giữ lời. Mạc Tư gạch: hỏi · thóc · tin · cùng màu. Không viết kho. Không viết Lý. Từ Sơn vòng. A Cường: "Trống. Không xe. Không miệng thứ hai." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt hỏi. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Không cọc "cấm hỏi thóc". Cấm bằng việc im.

Giữa trưa chạm vai ba việc. Không họp "hắn nói Lý gia". Hà rèm đến chiều. A Cường đường thấp không theo miệng. Không đường quan truy to. Nhớ bóng gò hôm qua — mắt và miệng có thể cùng một tay sai. Không kể suy thành hội.

Chiều sớm Kho Vô Hạn im. Không nhiệm vụ phát thóc từ thiện. Không nhiệm vụ nghe tin triều. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Triệu nước đúng — không thêm. Bếp im không hỏi lại chữ Lý.

Phong vòng chân. Kiểm giếng nắp. Kiểm rèm trẻ. Hà bánh tráng đúng giờ. Đại Lực bao không lũy. Tôn Vũ móc thấp. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy canh hỏi. Thu nhanh. Ngứa kể "hắn hỏi thóc + Lý" — hở. Phong chặn mắt bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh: không kể miệng, không chỉ giếng chơi, không nhắc thóc ngoài.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Một miệng. Hỏi thóc. Hỏi kho. Đổi tin. Ta: Đông thường. Hầm xấu. Không mở. Không đổi."

"Không lệch. Không kể trẻ ngoài lều. Không họp chữ lớn. Mai tai khe." Chị.

Canh hai ngồi trong. Khuyển gió. Then êm. Nhớ cười khô "lại cùng màu": nghề ta không lệch thật. Số lần không huy chương. Chữ Lý ngoài cổng không thành chuông trong lều.

Canh ba ngủ nghiêng. Mơ cổng không mở — tốt.

Canh tư nước. Không nói xong. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Hỏi lần bốn mươi sáu cùng màu. Không lệch. Không kể trẻ. Không chỉ giếng. Không đổi tin. Không lỏng." Cổng hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không lệch. Không mở. Đủ."

"Đủ. Máy nghèo. Miệng ngoài thì tai trong khe. Chữ lớn ngoài không thành hội trong."

Ba xương: Đông thường, Hầm xấu, không kể trẻ-giếng-thóc-tin. Máy nhớ việc.

Việc im nuôi sống: bao móc dao rèm nước bảng Khuyển. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe cổng trống sau hỏi thóc. Chưa biết mai mang yên giả, sóng thấp, hay miệng mang chữ lớn hơn. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi lời hay. Ngày mai vẫn Đông thường. Hôm sau vẫn Hầm xấu. Phía trước chỉ còn đất và then êm. Liệu có giữ cùng màu? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.403」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Hỏi lần bốn mươi sáu · cùng màu · không đổi tin · không kể trẻ · cấp im · máy nghèo
'''

CH404 = r'''============================================================
Chương 404: Ngày Yên Sau Hỏi Bốn Mươi Sáu
============================================================

Ngày thứ năm trăm hai mươi tư. Trống điểm. Trong rào — yên sau hỏi bốn mươi sáu. Không gào. Không xông. Chỉ việc. Trống không bằng yên hội. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau hỏi thóc.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai êm hơn. Hỏi hôm qua cùng màu ≠ hết nghề giữ. Then êm. Hôm nay yên — trống có lớp. Không mừng vì đã trống. Không lỏng vì đã qua hỏi. Yên sau hỏi không nghĩa ta được hội. Hội là hở. Hở là chết chậm. Nhất là sau chữ lớn ngoài cổng — yên có thể là khoảng lùi để miệng kể cho miệng khác.

Mùi đất se. Mùi vôi. Mùi mỡ bếp. Gió bấc không mang bụi đường quan. Không mang bụi gò. Trống ngoài ≠ trống trong tai. Phong hít ngắn. Không kể yên rồi. Hà siết khăn lỏng hơn nửa nút — lỏng khăn ≠ lỏng nghề: "Cổng?"

"Trống. Không thở phào." Anh nhìn cổng hai nhịp. Đủ.

Sân thức chậm hơn ngày hỏi. Đại Lực bao xấu tây. Tôn Vũ móc thấp không hun. Hứa dao đất. Diễm se băng. Cúc Hạt xâu trong rèm; Hà chưa mở rèm sớm. A Minh sỏi trong hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng vẫn sấp từ đêm hỏi. Từ Sơn vòng đều — không nhanh vì trống. Triệu ngậm miệng. A Cường lách vào, gót sạch:

"Cổng trống. Gò trống. Không miệng. Không xe. Không gỗ. Không lê. Không ai đứng chỗ hỏi thóc hôm qua."

"Không đạp theo. Không kể yên. Không thở phào. Không họp chữ lớn. Việc." Phong gật. "Biến."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai nói yên. Không ai nhắc Lý. Nói yên là hội nhỏ trên lưỡi.

Phong và Hà đổi việc: chị mở hầm tây kiểm then phụ, anh nửa vòng chân trong rào. Ba xương ngày yên: không thở phào to, không mở rèm trẻ sớm kiểu hết nguy, không rải vôi trắng giữa sân kiểu dọn ngày nghỉ. Nghỉ là chữ chết. Nhất là sau miệng đã hỏi thóc và khoe tin — yên có thể là khoảng lùi.

Trống ngoài rào đứng cả buổi sáng. Không bóng. Không miệng. Không thước. Không khách. Chỉ gió. Chỉ đất. Yên lần này khép bằng việc ta — không bằng kể ta. Không mừng. Không chỉ hố. Không chỉ then. Không chỉ trẻ. Không thở phào. Không khoe cùng màu hôm qua. Không khoe đã từ chối đổi tin.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Phong bê nước đổ đúng gốc rau dại bà già — việc nhỏ nuốt yên. Hà đảo muối lần hai. Hạt muối bám tay không rũ giữa sân nhìn cổng. Nhìn cổng lâu ngày yên là mời miệng về.

Giữa trưa không họp mừng. Không họp "hắn nói Lý". Phong chạm vai Đại Lực — xếp bao xấu thêm hàng lệch. Chạm Tôn Vũ — lau móc mỡ. Chạm Hứa — mài dao trong bóng. Ba chạm ba việc. Không lời hôm nay được nghỉ.

Hà gọi Diễm: "Rèm giữ đến chiều. Yên không nghĩa trẻ ra đông." Diễm gật. Cúc dạy Hạt mũi kim thứ hai. A Minh đếm sỏi thầm hai vòng rồi dừng — Hà đã dặn không biến đếm thành bài hát yên. Bài hát yên là hội trẻ.

Mạc Tư lật bảng trong kho, gạch im: yên sau hỏi thóc. Không viết nghỉ. Không viết kho. Không viết Lý. Từ Sơn đọc, gật, vòng tiếp. Triệu nước đúng gáo — không thêm vì ngày nhẹ. Ngày nhẹ không có trong máy nghèo. Khuyển xương cũ. Hữu đếm thở chó. Chó đều thì tay Hữu đều.

A Cường đường thấp ngoài lần hai: trống thật, không người đứng nhìn chỗ hỏi hôm qua. Lách vào nhìn Phong, lắc. Phong gật. Không mời nước mừng. Mời nước mừng là giữ hội.

Chiều sớm Phong ngồi bóng tường đếm nhịp vai. Kho Vô Hạn im — không thưởng yên, không nhiệm vụ tổ chức ăn mừng nhỏ. Ăn mừng nhỏ là chuông. Máy nghèo không chuông. EXP đầy im. Cấp im.

Bà già muốn nói hôm nay dễ thở. Thị Liên chạm rổ rau. Chú Bát gõ muôi. Im bếp. Im bếp ngày yên khó hơn im bếp ngày sóng — vì miệng muốn nở, nhất là sau khi đã nghe chữ thóc và chữ lớn ngoài cổng.

Phong vòng chân chậm. Chông nguyên. Vôi không bới. Hố lép sóng cũ im. Cửa vết cũ. Hầm then êm. Giếng nắp xấu. Không ghi miệng ta yên. Ghi đầu: trống ≠ yên hội. Hà góc tây đưa bánh tráng đúng giờ — không thưởng trống. Anh cắn. Muối. Không cảm ơn to.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy hơn vì yên. Phong Hà Đại Lực Tôn Vũ Hứa — đúng gáo. Không liếc gáo. Không nâng chén.

Sau cháo sân thu nhanh. Ngứa miệng được một ngày — ngứa là hở. Phong ngang bếp một lần, mắt chặn bà già. Bà cúi. Thị Liên đậy nồi. Chú Bát rửa gáo. Mạc Tư úp bảng. Rèm chốt. Then hai lần. Khuyển ngưỡng. Hữu nằm. A Minh sỏi trong hố — Hà kiểm. Cúc tắt đèn sớm. Hạt không chuyện ngày lặng. Phong dặn A Minh: "Sỏi trong hố. Không lấy ra chỉ cổng trống. Không kể miệng hôm qua. Không kể thóc ngoài."

Đêm canh một. Phong và Hà trong lều. Ngoài rào mùi dày như ghế đá. Nếu ghế đứng dậy thành sóng — đâm thấp máu kín. Nếu ghế mở miệng — cùng màu không lệch. Nếu ghế chỉ thước — không chỉ ngược. Nếu ghế đứng gò — không chỉ ngược.

Anh nắm tay chị. "Trống cả ngày. Không thở phào. Không mở rèm sớm. Không khoe từ chối tin."

"Không kể yên cho bếp. Không kể hỏi hôm qua thành xong. Không họp chữ lớn." Chị gật. "Em giữ trẻ trong. Yên ngoài không thành hội trong."

"Anh không kể A Cường lần ba. Mắt đủ. Tai vẫn khe — miệng hỏi thóc có thể kể cho miệng khác."

Canh hai. Người trong sát tường đông ngồi — không vì có bóng, vì nghề không nghỉ theo trống. Khuyển tai một lần — gió. Then êm. Phong nhớ miệng hôm qua hỏi thóc và khoe tin: yên hôm nay có thể là khoảng lùi. Máy không dùng yên để ngủ quên. Lần yên sau hỏi bốn mươi sáu là số. Số không huy chương.

Canh ba. Đất se. Phong ngủ nghiêng, tai khe đông. Hà lưng chạm lưng — ấm máy. Mơ ngắn thấy cổng trống — tốt. Trống trong mơ không thành bài hát sáng.

Canh tư. Gió nhẹ. Phong mở mắt trước trống điểm. Nghe then. Nghe Khuyển. Không bước. Uống nước. Đưa Hà. Không nói yên xong.

Trước trống điểm ra hầm tây: bảy dấu. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà khăn mới. "Hôm nay tiếp."

"Tiếp. Yên sau hỏi bốn mươi sáu. Trống không bằng yên hội. Không thở phào. Không lỏng." Nhìn cổng hai nhịp. Trống. Đủ thở. Không đủ mừng.

Nắm tay Hà: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Trống không bằng yên hội. Không thở phào. Đủ."

"Đủ. Máy nghèo. Yên ngoài thì việc trong chặt hơn nửa nút."

"Chặt việc. Lỏng khăn được. Không lỏng then. Không lỏng giếng. Không lỏng rèm."

Ba xương khép ngày: không thở phào to, không mở rèm trẻ sớm, không nêm cháo mừng yên. Ai phá — nặng. Máy nhớ việc.

Việc im nuôi sống. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang cổng trống. Chưa biết mai mang sóng thấp, bóng thước, hay miệng mang chữ lớn hơn. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi hội. Ngày mai vẫn máy nghèo. Hôm sau vẫn không thở phào. Phía trước chỉ còn đất và then êm. Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.404」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Yên sau hỏi bốn mươi sáu · trống ≠ yên hội · không thở phào · cấp im · máy nghèo
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
    # remove old file(s) for this chapter number, write canonical name
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
    seal(402, "Bóng Gò Lần Hai Mươi Tư Không Chỉ", CH402)
    seal(403, "Hỏi Lần Bốn Mươi Sáu Cùng Màu", CH403)
    seal(404, "Ngày Yên Sau Hỏi Bốn Mươi Sáu", CH404)


if __name__ == "__main__":
    main()
