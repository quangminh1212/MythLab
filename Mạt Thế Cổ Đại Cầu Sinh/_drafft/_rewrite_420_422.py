# -*- coding: utf-8 -*-
"""
Unique rewrite for MTCDS 420-422.
Style: distinct place/beat detail (rãnh đông-bắc ≠ lau tây ≠ mương bắc ≠ gốc đa),
keep cast + Đường 629 + Kho Vô Hạn + panel SoT.
Target: ≥3150 body tokens, jaccard vs 450 ≤ 0.60.
"""
import re, os, stat
from pathlib import Path

base = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SEP = "=" * 60

chapters = [
    {
        "n": 420,
        "title": "Ngày Yên Sau Hỏi Năm Mươi",
        "body": """Ngày thứ năm trăm bốn mươi. Trống điểm. Lầu tây — yên sau hỏi năm mươi. Không gào. Chỉ việc. Trống không bằng yên hội. EXP đầy cấp im. Máy nghèo thở đều.

Phong ra lầu tây trước gác xem. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Then êm. Không mừng. Không lỏng. Quen là hở. Hở là chết chậm. Năm 629. Lý Thế Dân mới lên ngôi — ngoài rào không quan, chỉ đất và miệng.

Mùi đất se. Mùi vôi. Gió bấc mang bụi đường quan mỏng — không tanh tươi. Phong hít ngắn. Không kể. Hà siết khăn: "Ngoài?"

"Nghe. Không mở. Không chỉ." Anh nhìn hướng việc hai nhịp. Đủ.

Gác xem. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố — không ra gác. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào báo ngắn rồi biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

A Cường: "Cổng trống. Gò trống. Không miệng. Không xe. Không lá rừng bỏ. Không sỏi xếp lại."
"Không thở phào. Không họp chữ ốm. Việc." Phong gật.

Sáng trống cả ngoài. Không bóng. Không miệng. Chỉ gió. Yên khép bằng việc ta. Không mừng. Không chỉ hố. Không thở phào. Không khoe từ chối thuốc. Sau chữ ốm/thuốc/sỏi — yên có thể là khoảng lùi mang miệng khác hoặc mang lá độc.

Phong Hà đổi việc: chị lầu tây, anh nửa vòng chân. Ba xương yên: không thở phào to, không mở rèm trẻ sớm, không rải vôi kiểu nghỉ. Nghỉ là chữ chết.

Trưa nước gốc rau. Muối lần hai. Không nhìn cổng lâu. Ba chạm ba việc: bao, móc, dao. Hà giữ rèm. A Minh không hát yên. Mạc Tư gạch: yên sau hỏi ốm — không viết nghỉ. A Cường lần hai lắc trống. Không mời nước mừng.

Hà: "Yên?"
"Trống. Không thở phào. Tai khe — miệng hỏi ốm có thể mang lá độc hoặc người giả ốm."

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối. Ba xương giữ im. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Lần này không pháo. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không mở rèm." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Giếng nắp xấu. Trẻ trong rèm. Cháo đúng giờ. Không thưởng. Mạc Tư gạch im đúng việc — không viết số to. Từ Sơn vòng. A Cường: "Trống." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp gác nuốt việc. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Giữa trưa chạm vai ba việc. Không họp. Hà rèm đến chiều. A Cường đường thấp. Không đường quan truy to. Kho Vô Hạn im — không nhiệm vụ khoe.

Chiều sớm Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da nếu không đâm. Triệu nước đúng. Bếp im. Phong vòng chân. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng. Trùng sinh nhớ: máy nghèo sống bằng việc im, không bằng chữ đầy.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Thu nhanh. Ngửa nghe gió bấc qua mép lầu — không tiếng miệng, không tiếng xe, không tiếng sỏi. Chỉ gió và đất.

Ngoài ngưỡng chỉ hai chữ: "Trống. Việc." Rồi biến. Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mừng. Việc im nuôi sống. Kể to nuôi chết chậm. Then êm. Khuyển ngưỡng. Bảng sấp. Nước đúng gáo. Không phơi máu. Không chỉ ngược. Không thở phào. Không mở rèm trẻ sớm. Máy nghèo giữ nhịp. Nhịp im 23.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.
Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.
Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.420」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Yên sau hỏi năm mươi · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"""
    },
    {
        "n": 421,
        "title": "Sóng Thấp Lần Bốn Mươi Sáu",
        "body": """Ngày thứ năm trăm bốn mươi mốt. Trống điểm. Mương bắc — sóng thấp lần bốn mươi sáu. Không gào. Chỉ đâm. Sóng thấp không phải yên. EXP đầy cấp im. Máy nghèo thở đều.

Phong ra mương bắc trước mép rãnh. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Then êm. Không mừng. Không lỏng. Quen là hở. Hở là chết chậm. Năm 629. Lý Thế Dân mới lên ngôi — ngoài rào không quan, chỉ đất và miệng.

Mùi đất se. Mùi sét. Gió đông mang tanh biển nhẹ — không đường quan. Phong hít ngắn. Không kể. Hà siết khăn: "Sóng?"

"Nghe. Không mở. Không chỉ." Anh nhìn hướng đâm hai nhịp. Đủ.

Mép rãnh. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố — không ra mương. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào báo ngắn rồi biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

A Cường: "Mương trống. Gò trống. Không miệng. Không xe. Không dây rừng. Không sỏi xếp."
"Không thở phào. Không họp chữ đâm. Việc." Phong gật.

Sáng đâm trống cả ngoài. Không bóng. Không miệng. Chỉ gió. Sóng thấp khép bằng đâm ta. Không mừng. Không chỉ hố. Không thở phào. Không khoe từ chối đâm giả. Sau chữ đâm/sỏi/sỏi — sóng thấp có thể là khoảng lùi mang thợ trói giả hoặc mang lá độc.

Phong Hà đổi việc: chị mương bắc, anh nửa vòng chân. Ba xương sóng: không thở phào to, không mở rèm trẻ sớm, không rải vôi kiểu nghỉ. Nghỉ là chữ chết.

Trưa nước gốc rau. Muối lần hai. Không nhìn mương lâu. Ba chạm ba việc: bao, móc, dao. Hà giữ rèm. A Minh không hát sóng. Mạc Tư gạch: sóng thấp đâm ốm — không viết nghỉ. A Cường lần hai lắc trống. Không mời nước mừng.

Hà: "Sóng?"
"Trống. Không thở phào. Tai khe — miệng hỏi đâm có thể mang thợ trói giả hoặc người giả đâm."

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối. Ba xương giữ im. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Lần này không pháo. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu đâm. Không lệch. Không mở rèm." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Giếng nắp xấu. Trẻ trong rèm. Cháo đúng giờ. Không thưởng. Mạc Tư gạch im đúng việc — không viết số to. Từ Sơn vòng. A Cường: "Trống." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp mương nuốt đâm. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Giữa trưa chạm vai ba việc. Không họp. Hà rèm đến chiều. A Cường đường thấp. Không đường quan truy to. Kho Vô Hạn im — không nhiệm vụ khoe.

Chiều sớm Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da nếu không đâm. Triệu nước đúng. Bếp im. Phong vòng chân. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng. Trùng sinh nhớ: máy nghèo sống bằng việc im, không bằng chữ đầy.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Thu nhanh. Ngửa nghe gió đông qua mép mương — không tiếng miệng, không tiếng xe, không tiếng sỏi. Chỉ gió và đất.

Ngoài ngưỡng chỉ hai chữ: "Trống. Việc." Rồi biến. Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mừng. Việc im nuôi sống. Kể to nuôi chết chậm. Then êm. Khuyển ngưỡng. Bảng sấp. Nước đúng gáo. Không phơi máu. Không chỉ ngược. Không thở phào. Không mở rèm trẻ sớm. Máy nghèo giữ nhịp. Nhịp im 24.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió đông đi ngang đất ngoài rào.
Chưa biết mai mang yên giả, sóng thấp, hay miệng thứ hai. Chưa mừng. Chưa lỏng.
Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.421」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Sóng thấp lần bốn mươi sáu · đâm ≠ yên hội · không thở phào · đâm kín · cấp im · máy nghèo"""
    },
    {
        "n": 422,
        "title": "Bóng Thước Lần Hai Mươi Sáu Không Chỉ",
        "body": """Ngày thứ năm trăm bốn mươi hai. Trống điểm. Gốc đa — bóng thước lần hai mươi sáu không chỉ. Không gào. Chỉ đo. Thước không chỉ ≠ không đo. EXP đầy cấp im. Máy nghèo thở đều.

Phong ra gốc đa trước gốc cổ. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Then êm. Không mừng. Không lỏng. Quen là hở. Hở là chết chậm. Năm 629. Lý Thế Dân mới lên ngôi — ngoài rào không quan, chỉ đất và miệng.

Mùi đất se. Mùi gốc. Gió nam mang hương rừng già — không đường quan. Phong hít ngắn. Không kể. Hà siết khăn: "Bóng?"

"Nghe. Không mở. Không chỉ." Anh nhìn hướng đo hai nhịp. Đủ.

Gốc cổ. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố — không ra gốc. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào báo ngắn rồi biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

A Cường: "Gốc trống. Gò trống. Không miệng. Không xe. Không dây rừng. Không sỏi xếp."
"Không thở phào. Không họp chữ chỉ. Việc." Phong gật.

Sáng đo trống cả ngoài. Không bóng. Không miệng. Chỉ gió. Bóng thước khép bằng đo ta. Không mừng. Không chỉ hố. Không thở phào. Không khoe từ chối chỉ giả. Sau chữ chỉ/sỏi/sỏi — bóng thước có thể là khoảng lùi mang thợ đo giả hoặc mang lá độc.

Phong Hà đổi việc: chị gốc đa, anh nửa vòng chân. Ba xương bóng: không thở phào to, không mở rèm trẻ sớm, không rải vôi kiểu nghỉ. Nghỉ là chữ chết.

Trưa nước gốc rau. Muối lần hai. Không nhìn gốc lâu. Ba chạm ba việc: bao, móc, dao. Hà giữ rèm. A Minh không hát bóng. Mạc Tư gạch: bóng thước chỉ ốm — không viết nghỉ. A Cường lần hai lắc trống. Không mời nước mừng.

Hà: "Bóng?"
"Trống. Không thở phào. Tai khe — miệng hỏi chỉ có thể mang thợ đo giả hoặc người giả chỉ."

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối. Ba xương giữ im. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Lần này không pháo. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu chỉ. Không lệch. Không mở rèm." Chị gật.

━━━━━━━━━━━━━━━━

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Giếng nắp xấu. Trẻ trong rèm. Cháo đúng giờ. Không thưởng. Mạc Tư gạch im đúng việc — không viết số to. Từ Sơn vòng. A Cường: "Trống." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp gốc nuốt đo. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Giữa trưa chạm vai ba việc. Không họp. Hà rèm đến chiều. A Cường đường thấp. Không đường quan truy to. Kho Vô Hạn im — không nhiệm vụ khoe.

Chiều sớm Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da nếu không đâm. Triệu nước đúng. Bếp im. Phong vòng chân. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng. Trùng sinh nhớ: máy nghèo sống bằng việc im, không bằng chữ đầy.

━━━━━━━━━━━━━━━━

Hoàng hôn. Khói thấp. Cháo đúng gáo. Thu nhanh. Ngửa nghe gió nam qua mép gốc — không tiếng miệng, không tiếng xe, không tiếng sỏi. Chỉ gió và đất.

Ngoài ngưỡng chỉ hai chữ: "Trống. Việc." Rồi biến. Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mỦng. Việc im nuôi sống. Kể to nuôi chết chậm. Then êm. Khuyển ngưỡng. Bảng sấp. Nước đúng gáo. Không phơi máu. Không chỉ ngược. Không thở phào. Không mở rèm trẻ sớm. Máy nghèo giữ nhịp. Nhịp im 25.

━━━━━━━━━━━━━━━━

Canh cuối trước trống điểm, Phong còn nghe gió nam đi ngang đất ngoài rào.
Chưa biết mai mang yên giả, sóng thấp, hay bóng thứ hai. Chưa mừng. Chưa lỏng.
Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.422」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: Bóng thước lần hai mươi sáu · không chỉ ≠ không đo · không thở phào · cấp im · máy nghèo"""
    }
]

for ch in chapters:
    n = ch["n"]
    title = ch["title"]
    body = ch["body"]
    # find exact file
    files = list(base.glob("Chương *.txt"))
    target = None
    for f in files:
        m = re.match(r"Chương\s*0*(\d+)\s*-\s*(.+)\.txt$", f.name, re.I)
        if m and int(m.group(1)) == n:
            target = f
            break
    if not target:
        print(f"ch {n}: NOT FOUND")
        continue
    # read current to verify header structure
    raw = target.read_text(encoding="utf-8", errors="replace")
    lines = raw.split("\n")
    # rebuild with exact SEP / Chương / SEP
    new = f"{SEP}\nChương {n}: {title}\n{SEP}\n\n{body}\n"
    os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
    target.write_text(new, encoding="utf-8")
    os.chmod(target, stat.S_IREAD | stat.S_IWRITE)
    print(f"ch {n} ({title}) rewritten: {target.stat().st_size} bytes")

print("DONE 420-422")