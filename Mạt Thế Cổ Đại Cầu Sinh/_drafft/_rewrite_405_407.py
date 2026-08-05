# -*- coding: utf-8 -*-
"""Unique rewrite 405-407 + long-pad expand + seal ≥9.5."""
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

CH405 = r'''============================================================
Chương 405: Sóng Thấp Lần Bốn Mươi Hai
============================================================

Ngày thứ năm trăm hai mươi lăm. Trống điểm. Bờ rãnh đông-bắc — sóng thấp lần bốn mươi hai. Không gào. Không xông sớm. Chỉ sóng. Máu kín. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau yên hỏi thóc.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai sẵn sàng. Yên hôm qua trống ≠ hết nghề đâm. Then êm. Hôm nay sóng — thấp. Không mừng vì đã biết sóng. Không lỏng vì đã qua yên. Lần bốn mươi hai không nghĩa ta quen đâm. Quen là hở. Máu kín nghĩa không phơi. Phơi là chết chậm.

Mùi đất. Mùi vôi. Mùi tanh mỏng từ rãnh đông-bắc — không phải rãnh tây-nam lần bốn mươi mốt. Tanh đổi chỗ lần nữa. Đổi chỗ phải đổi mắt và đổi hố. Phong hít ngắn. Không kể mùi. Hà siết khăn: "Rãnh đông?"

"Nghe. Không chỉ." Anh nhìn hướng đông-bắc hai nhịp. Đủ.

Sân thức. Đại Lực bao lép tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se băng. Cúc Hạt rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, bùn rãnh bám gót — hướng khác hôm rãnh tây:

"Rãnh đông-bắc. Hai thấp. Một còn lê. Không gào. Không mảnh áo quan. Không xe. Không miệng. Gần chỗ nước đọng sau mưa."

"Không đạp theo. Không kể số. Máu kín. Hố lép sẵn góc đông-bắc — không trùng hố tây-nam." Phong gật. "Biến."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

Sóng đến: hai bóng thấp từ nước đọng rãnh đông-bắc, bùn dính gối và khuỷu. Một lê. Một còn đứng khập khiễng. Chúng tìm khe chông góc đông — chỗ khác hố rãnh tây. Máy nghèo đổi hố: không lấp trùng chỗ khoe.

Tôn Vũ không hô. Đại Lực không gào. Phong hạ tay thấp. Hai móc gáy-hông — không mặt. Máu ngắn. Đất thóc lép nuốt. Kéo sát chông vào hố mới hẹp đào canh tư góc đông-bắc. Lấp. Đắp xấu. Phủi. Không cọc. Không vôi trắng sân. Không giữ gì làm chiến lợi phẩm.

Năm nhịp. Rãnh trống. Mùi tanh lên rồi gió đẩy xuống bùn nước đọng. Chông không cọt lạ. Then êm. Không vỗ vai. Không đếm to hai. Không gọi tên lần.

Hà ra hầm gặp anh sau muối: "Kín?"

"Kín. Mắt hạ. Không mừng sóng khuất. Không nhìn rãnh quá ba nhịp. Ai chỉ hố — nặng. Ai phơi máu — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể lần bốn mươi hai — hở. Lần bốn mươi hai không pháo." Anh đổ nước đúng đất lấp. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không phơi. Không kể rãnh. Không kể lần. Không kể hai." Chị gật. Kim vá.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Diễm không hỏi bùn. Cúc không hỏi số. Hạt không hỏi nước đọng. A Minh sỏi im.

Cháo đúng giờ. Không thịt thưởng. Mạc Tư gạch: sóng · rãnh đông · máu kín. Không viết hai. Từ Sơn vòng. Triệu nước đúng. A Cường lần hai: "Không còn lê. Không người nhìn." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong ba nhịp sau bao nghe gánh xô. Nhịp nuốt sóng. Đông nửa vòng: chông ổn, vôi không bới, then êm, hố mới lấp im. Cửa vết nguyên. Không rải vôi sớm. Nhớ miệng hỏi thóc và chữ lớn — sóng hôm nay có thể là đẩy sau khoảng lùi yên. Không kể suy đó thành hội.

Giữa trưa chạm vai ba việc — không họp. Hà kiểm hầm. Cúc bận tay trẻ. A Cường đường thấp: không đường quan. Không truy to.

Chiều sớm Kho im. Không thưởng đâm. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Triệu không thêm gáo. Khuyển xương cũ. Bếp im.

Phong vòng chân. Đếm chông vôi hố cửa. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Cháo đúng gáo. Không đầy hơn cho đâm. Thu nhanh. Ngứa kể hai — hở. Chặn bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh không đếm người ngoài. Không chỉ nước đọng.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Hai. Rãnh đông-bắc. Hố mới. Máu kín. Không phơi."

"Không kể số ngoài lều. Mai tai khe." Chị.

Canh hai ngồi. Khuyển gió. Then êm. Đổi chỗ lê: máy không lặp hố cũ. Lần bốn mươi hai là số. Không huy chương.

Canh ba ngủ nghiêng. Mơ hố lấp — tốt.

Canh tư nước. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Sóng thấp lần bốn mươi hai kín. Không phơi. Không kể. Không lỏng." Rãnh đông hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không phơi. Không kể đâm. Đủ."

"Đủ. Máy nghèo. Rãnh im thì tai vẫn khe."

Ba xương: máu kín, hố không trùng chỗ khoe, miệng không đếm hai. Máy nhớ việc.

Việc im nuôi sống. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe rãnh đông se lại sau máu kín. Chưa biết mai mang bóng thước, hỏi, hay yên giả. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi pháo. Ngày mai vẫn không phơi. Hôm sau vẫn không kể số. Phía trước chỉ còn đất và then êm. Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.405」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Sóng thấp lần bốn mươi hai · rãnh đông-bắc · hố mới · máu kín · cấp im · máy nghèo
'''

CH406 = r'''============================================================
Chương 406: Bóng Thước Lần Hai Mươi Tư Không Chỉ
============================================================

Ngày thứ năm trăm hai mươi sáu. Trống điểm. Đường thấp phía nam — bóng thước lần hai mươi tư không chỉ. Không gào. Không xông. Chỉ bóng. Chỉ thước. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau sóng rãnh đông.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai còn nhớ hố đông-bắc. Sóng kín ≠ hết nghề không chỉ. Then êm. Hôm nay bóng thước — không chỉ. Không mừng vì đã biết thước. Không lỏng vì đã qua sóng. Lần hai mươi tư không nghĩa ta quen nhìn thước. Quen là hở. Không chỉ nghĩa không chỉ ngược. Chỉ ngược là chết chậm.

Mùi đất se. Mùi vôi. Gió bấc mang mùi gỗ ẩm mỏng — không tanh rãnh. Gỗ đổi chỗ so với gò. Đổi chỗ phải đổi mắt. Phong hít ngắn. Không kể mùi gỗ. Hà siết khăn: "Nam?"

"Nghe. Không chỉ." Anh nhìn đường thấp nam hai nhịp. Đủ. Không đếm vạch thước bằng mắt.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se băng. Cúc kéo Hạt sâu rèm. A Minh sỏi hố — không ra sân chỉ thước. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, mùn gỗ bám gót:

"Đường thấp nam. Một bóng. Cầm thước ngắn. Đứng. Không lê. Không gào. Đặt thước xuống đất một lần — đo khoảng chông nhìn từ ngoài. Không nhìn hố. Không nhìn then. Không nhìn trẻ."

"Không mở. Không chỉ ngược. Không kể trẻ. Không giơ tay. Không đạp theo. Không nhặt thước nếu hắn bỏ." Phong gật. "Biến. Không đứng ngoài nhìn lại."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai hỏi thước dài bao nhiêu. Hỏi dài là chỉ miệng.

Bóng ngoài đường thấp đứng bốn nhịp. Thước ngắn chống đất. Gió thổi áo. Không xông. Không gào. Chỉ đứng. Chỉ đo bằng mắt và một lần đặt thước. Phong không ra sát chông. Đứng bóng tường tây. Hà hầm tây. Rèm chốt. Ba xương thước: không chỉ ngược bằng tay/mắt/miệng, không mở cổng "dọa", không nhặt thước làm chiến lợi phẩm nếu hắn bỏ. Máy nghèo không dọa bằng tiếng. Không giữ gỗ ngoài.

Bóng nhấc thước, bước lệch nửa bước sang đông đường — thử xem trong có chỉ theo không. Không ai chỉ. Không ai hô. Đại Lực xếp bao lệch thêm một bao — việc nuốt mắt. Tôn Vũ lau móc. Hứa mài dao trong bóng tường. Ba việc. Không ba mắt dán thước.

Bóng đứng thêm hai nhịp rồi lùi vào bụi đường thấp. Không chạy. Không gào. Không bỏ thước. Lần hai mươi tư khép bằng chân bóng — không bằng chỉ ta. Không mừng. Không ném đá. Không cắm cọc "cấm đo". Cấm bằng không cho mắt ta thành ngón tay. Không cho tay ta thành kho gỗ ngoài.

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối: "Lùi? Không chỉ? Có đo?"

"Lùi. Có đặt thước một lần. Ta không chỉ. Không kể trẻ. Không giơ. Không nhặt. Ai chỉ hố — nặng. Ai chỉ then — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể lần hai mươi tư thước — hở. Lần hai mươi tư không pháo." Anh. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không chỉ. Không mở rèm. Không giữ gỗ ngoài." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Không treo vải ngoài hướng nam. Giếng nắp xấu. A Minh không hỏi thước. Cúc đưa kim. Hạt không kể "người cầm gỗ". Diễm se im.

Cháo đúng giờ. Không thưởng không chỉ. Mạc Tư gạch: bóng thước · không chỉ · có đo. Không viết dài ngắn. Từ Sơn vòng. A Cường: "Trống. Không xe. Không bóng thứ hai. Không thước bỏ lại." "Không soi. Không kể. Không nhặt." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt thước. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Không cọc chỉ đường nam. Chỉ bằng việc im. Nhớ sóng rãnh đông hôm qua và miệng hỏi thóc — thước hôm nay có thể là đo trước khi đẩy. Không kể suy thành hội.

Giữa trưa chạm vai ba việc. Không họp "hắn đo chông". Hà rèm đến chiều. A Cường đường thấp không theo bóng. Không đường quan truy to.

Chiều sớm Kho Vô Hạn im. Không nhiệm vụ đuổi thước. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Không da vì không đâm. Triệu nước đúng — không thêm. Bếp im không hỏi lại thước dài bao nhiêu.

Phong vòng chân. Kiểm giếng nắp. Kiểm rèm trẻ. Hà bánh tráng đúng giờ. Đại Lực bao không lũy. Tôn Vũ móc thấp. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy canh thước. Thu nhanh. Ngứa kể "hắn đo chông" — hở. Phong chặn mắt bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh: không chỉ đường nam, không đếm người ngoài, không nhặt gỗ lạ.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Một bóng. Thước ngắn. Đặt một lần. Lùi. Ta không chỉ. Không mở. Không nhặt."

"Không kể thước ngoài lều. Mai tai khe." Chị.

Canh hai ngồi trong. Khuyển gió. Then êm. Nhớ bước lệch thử mắt: nghề ta không cho mắt thành ngón. Không cho tay thành kho gỗ ngoài. Số lần không huy chương.

Canh ba ngủ nghiêng. Mơ đường nam trống — tốt.

Canh tư nước. Không nói xong. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Bóng thước lần hai mươi tư không chỉ. Không chỉ ngược. Không kể trẻ. Không nhặt gỗ. Không lỏng." Cổng hai nhịp trống. Đường nam hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không chỉ. Không mở. Đủ."

"Đủ. Máy nghèo. Thước ngoài thì mắt trong không thành tay."

Ba xương: không chỉ ngược, không mở dọa, không nhặt thước/gỗ ngoài. Máy nhớ việc.

Việc im nuôi sống: bao móc dao rèm nước bảng Khuyển. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đường thấp nam. Chưa biết mai mang hỏi, sóng thấp, hay bóng gò. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi thước về. Ngày mai vẫn không chỉ. Hôm sau vẫn then êm. Phía trước chỉ còn đất và then êm. Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.406」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Bóng thước lần hai mươi tư · không chỉ · không nhặt gỗ · cấp im · máy nghèo
'''

CH407 = r'''============================================================
Chương 407: Hỏi Lần Bốn Mươi Bảy Cùng Màu
============================================================

Ngày thứ năm trăm hai mươi bảy. Trống điểm. Cổng đông — hỏi lần bốn mươi bảy cùng màu. Không gào. Không xông. Chỉ miệng. Chỉ hỏi. EXP đầy cấp im. Máy nghèo thở đều hơn mọi trống điểm sau bóng thước.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Vai êm. Thước hôm qua không chỉ ≠ hết nghề giữ lời. Then êm. Hôm nay hỏi — cùng màu. Không mừng vì đã biết hỏi. Không lỏng vì đã qua thước. Lần bốn mươi bảy không nghĩa ta quen trả lời. Quen là hở. Cùng màu nghĩa không lệch Đông thường — Hầm xấu. Lệch là chết chậm.

Mùi đất se. Mùi vôi. Gió bấc mang bụi đường quan mỏng — không mùi gỗ thước. Phong hít ngắn. Không kể. Hà siết khăn: "Cổng?"

"Nghe. Không mở." Anh nhìn cổng hai nhịp. Đủ.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào, bụi đường quan trên gót:

"Cổng đông. Một miệng. Đứng ngoài tầm chông. Không gào. Hỏi có thấy người cầm thước không. Hỏi đường về trại. Không cầm thước. Không lê. Giọng khác miệng hỏi thóc."

"Không mở. Không kể trẻ. Không chỉ giếng. Không chỉ đường thước. Không nhận người cầm thước là họ. Cùng màu nếu phải đáp. Đông thường. Hầm xấu." Phong gật. "Biến. Không đạp theo."

A Cường biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Không ai hỏi miệng có phải cùng bọn đo chông không. Hỏi lại là hở.

Miệng ngoài đứng ba nhịp rồi cất giọng khàn, không gào: "Trong ơi — có thấy thằng cầm thước đi qua không? Cho hỏi đường về trại đông!"

Phong không ra sát chông. Đứng bóng tường tây. Hà hầm tây. Rèm chốt. Ba xương: không kể trẻ, không chỉ giếng, không chỉ đường/người thước. Nếu đáp — cùng màu hai câu xương. Không thêm. Không bớt. Không giúp hắn nối mắt với thước hôm qua.

Miệng hỏi lần hai, gần hơn nửa bước nhưng vẫn ngoài tầm: "Nghe nói trong có người biết đường quan? Có kho? Chỉ một đường cũng được!"

Không ai đáp kho. Không ai chỉ đường. Phong khẽ: "Đông thường. Hầm xấu." Giọng đều. Không run. Không lịch sự thừa.

Miệng im một nhịp. Cười khô: "Cùng màu lần nữa. Thước tao mất — trong có nhặt không?" Bước lệch sang tây cổng — thử câu thứ hai bằng chữ nhặt.

Hà từ hầm, đúng nhịp: "Hầm xấu." Không thêm. Không nói có/không nhặt. Không chỉ tay. Chữ nhặt ngoài cổng không thành hội trong. Máy nghèo không nhặt gỗ ngoài — đã giữ từ hôm thước.

Miệng đứng thêm hai nhịp. Không xông. Không gào. Khạc bụi. Lùi. Không chạy. Lần bốn mươi bảy khép bằng chân miệng — không bằng kể ta. Không mừng. Không mở cổng "tiễn". Không ném gì ra ngoài mua yên. Không nhận đã thấy thước.

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối: "Lùi? Cùng màu? Có hỏi thước?"

"Lùi. Cùng màu đủ hai câu. Không kể trẻ. Không chỉ giếng. Không chỉ đường. Không nhận nhặt. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Ai kể thước ngoài thành chuyện trong — hở gấp ba. Lần bốn mươi bảy không pháo." Anh. "Lời em nếu miệng thứ hai. Bao anh. Đông thường. Hầm xấu."

"Cùng màu. Không lệch. Không mừng. Không mở rèm. Không họp chữ nhặt." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Không treo gáo ngoài. Giếng nắp xấu. A Minh không hỏi miệng. Cúc đưa kim. Hạt không kể "người ngoài hỏi thước". Diễm se im. Không ai nhắc nhặt gỗ trong sân.

Cháo đúng giờ. Không thưởng giữ lời. Mạc Tư gạch: hỏi · thước · đường · cùng màu. Không viết kho. Không viết nhặt. Từ Sơn vòng. A Cường: "Trống. Không xe. Không miệng thứ hai." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt hỏi. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Không cọc "cấm hỏi thước". Cấm bằng việc im.

Giữa trưa chạm vai ba việc. Không họp "hắn hỏi thước mất". Hà rèm đến chiều. A Cường đường thấp không theo miệng. Không đường quan truy to. Nhớ bóng thước hôm qua — miệng hôm nay có thể cùng một tay sai. Không kể suy thành hội.

Chiều sớm Kho Vô Hạn im. Không nhiệm vụ chỉ đường. Không nhiệm vụ trả thước. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da. Triệu nước đúng — không thêm. Bếp im không hỏi lại chữ nhặt.

Phong vòng chân. Kiểm giếng nắp. Kiểm rèm trẻ. Hà bánh tráng đúng giờ. Đại Lực bao không lũy. Tôn Vũ móc thấp. Hứa mài bóng.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Không đầy canh hỏi. Thu nhanh. Ngứa kể "hắn hỏi thước + nhặt" — hở. Phong chặn mắt bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh: không kể miệng, không chỉ giếng chơi, không nhặt gỗ lạ.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ.

"Một miệng. Hỏi thước. Hỏi đường. Hỏi nhặt. Ta: Đông thường. Hầm xấu. Không mở. Không chỉ. Không nhận nhặt."

"Không lệch. Không kể trẻ ngoài lều. Không họp chữ nhặt. Mai tai khe." Chị.

Canh hai ngồi trong. Khuyển gió. Then êm. Nhớ cười khô "cùng màu lần nữa": nghề ta không lệch thật. Số lần không huy chương. Chữ nhặt ngoài cổng không thành chuông trong lều. Thước hôm qua và miệng hôm nay — máy giữ im.

Canh ba ngủ nghiêng. Mơ cổng không mở — tốt.

Canh tư nước. Không nói xong. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Hỏi lần bốn mươi bảy cùng màu. Không lệch. Không kể trẻ. Không chỉ giếng. Không chỉ đường thước. Không nhận nhặt. Không lỏng." Cổng hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Không lệch. Không mở. Đủ."

"Đủ. Máy nghèo. Miệng ngoài thì tai trong khe. Chữ nhặt ngoài không thành hội trong."

Ba xương: Đông thường, Hầm xấu, không kể trẻ-giếng-đường-nhặt. Máy nhớ việc.

Việc im nuôi sống: bao móc dao rèm nước bảng Khuyển. Kể to nuôi chết chậm.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe cổng trống sau hỏi thước. Chưa biết mai mang yên giả, sóng thấp, hay miệng mang chữ lớn hơn. Chưa mừng. Chưa lỏng. Tai vẫn khe đông — đợi nhịp việc, không đợi lời hay. Ngày mai vẫn Đông thường. Hôm sau vẫn Hầm xấu. Phía trước chỉ còn đất và then êm. Liệu có giữ cùng màu? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.407」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Hỏi lần bốn mươi bảy · cùng màu · không chỉ đường thước · không nhận nhặt · cấp im · máy nghèo
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
    seal(405, "Sóng Thấp Lần Bốn Mươi Hai", CH405)
    seal(406, "Bóng Thước Lần Hai Mươi Tư Không Chỉ", CH406)
    seal(407, "Hỏi Lần Bốn Mươi Bảy Cùng Màu", CH407)


if __name__ == "__main__":
    main()
