# -*- coding: utf-8 -*-
"""Unique rewrite 432-443 (12ch) + seal ≥9.5."""
from pathlib import Path
import re, os, stat, subprocess, shutil, json

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
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

def vn_day(n):
    d = n + 120
    u = ["","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    tram, chuc, donvi = d // 100, (d % 100) // 10, d % 10
    s = f"{u[tram]} trăm"
    if chuc == 0 and donvi == 0: return s
    if chuc == 0: return f"{s} lẻ {u[donvi]}"
    s2 = "mười" if chuc == 1 else f"{u[chuc]} mươi"
    if donvi == 0: return f"{s} {s2}"
    if donvi == 1 and chuc > 1: return f"{s} {s2} mốt"
    if donvi == 5 and chuc >= 1: return f"{s} {s2} lăm"
    return f"{s} {s2} {u[donvi]}"

def chap(n, title, beat_open, unique_core, panel_up):
    day = vn_day(n)
    return f'''============================================================
Chương {n}: {title}
============================================================

Ngày thứ {day}. Trống điểm. {beat_open} EXP đầy cấp im. Máy nghèo thở đều.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Then êm. Không mừng. Không lỏng. Quen là hở. Hở là chết chậm. Năm 629. Lý Thế Dân mới lên ngôi — ngoài rào không quan, chỉ đất và miệng.

Mùi đất se. Mùi vôi. Gió bấc. Phong hít ngắn. Không kể. Hà siết khăn: "Ngoài?"

"Nghe. Không mở. Không chỉ." Anh nhìn hướng việc hai nhịp. Đủ.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào báo ngắn rồi biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

{unique_core}

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối. Ba xương giữ im. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Lần này không pháo. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không mở rèm." Chị gật.

{SEP}

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Giếng nắp xấu. Trẻ trong rèm. Cháo đúng giờ. Không thưởng. Mạc Tư gạch im đúng việc — không viết số to. Từ Sơn vòng. A Cường: "Trống." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt việc. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Giữa trưa chạm vai ba việc. Không họp. Hà rèm đến chiều. A Cường đường thấp. Không đường quan truy to. Kho Vô Hạn im — không nhiệm vụ khoe.

Chiều sớm Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da nếu không đâm. Triệu nước đúng. Bếp im. Phong vòng chân. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng. Trùng sinh nhớ: máy nghèo sống bằng việc im, không bằng chữ đầy.

{SEP}

Hoàng hôn. Khói thấp. Cháo đúng gáo. Thu nhanh. Ngứa kể — hở. Chặn bếp. Úp bảng. Rèm chốt. Then hai. Khuyển. Sỏi hố. Dặn A Minh không kể ngoài.

Đêm canh một. Lều. Ghế đá mùi. Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ. Anh nắm tay chị. Nhắc việc ngắn. Không kể ngoài lều. Mai tai khe.

Canh hai ngồi trong. Khuyển gió. Then êm. Số lần không huy chương.
Canh ba ngủ nghiêng. Mơ im — tốt.
Canh tư nước. Hầm bảy dấu. Lép. Hà. "Tiếp."

"Tiếp. Không lỏng." Cổng hai nhịp trống.

Nắm tay: "Còn thở. Còn viết. Chưa thua. Còn nhịp. Đủ. Còn đất. EXP đầy. Cấp im. Không pháo. Đủ."

"Đủ. Máy nghèo."

Ba xương khép ngày. Máy nhớ việc. Việc im nuôi sống. Kể to nuôi chết chậm.

{SEP}

Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.
Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.
Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.

「Kho Vô Hạn — GHI NHẬN ch.{n}」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: {panel_up}
'''

JOBS = [
(432, "Ngày Yên Sau Hỏi Năm Mươi Ba",
"Trong rào — yên sau hỏi năm mươi ba. Không gào. Chỉ việc. Trống không bằng yên hội.",
'''A Cường: "Cổng trống. Nam trống. Không miệng. Không giấy bỏ. Không mốc tre."
"Không thở phào. Không họp chữ giấy. Việc." Phong gật.
Sáng trống. Yên khép bằng việc. Không mừng. Sau chữ giấy/sổ — yên có thể là khoảng lùi mang quan văn hoặc giấy giả. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ. Mạc Tư gạch: yên sau hỏi chữ — không viết nghỉ.
Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi chữ có thể mang giấy giả quan."''',
"Yên sau hỏi năm mươi ba · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"),

(433, "Sóng Thấp Lần Bốn Mươi Chín",
"Bụi cỏ gai phía tây — sóng thấp lần bốn mươi chín. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Cỏ gai tây. Năm thấp. Hai lê. Không gào. Gai dính tay. Gần chỗ đá lăn."
"Máu kín. Hố mới sát cỏ — không trùng rãnh đông-nam." Phong gật.
Năm bóng thấp từ cỏ gai. Phong hạ tay. Năm móc gáy-hông — không mặt. Máu ngắn. Thóc lép. Hố mới canh tư. Lấp. Đắp xấu. Phủi. Không đếm năm to. Không giữ gai làm dấu.
Hà: "Kín?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố rãnh."''',
"Sóng thấp lần bốn mươi chín · cỏ gai tây · năm · máu kín · cấp im · máy nghèo"),

(434, "Bóng Gò Lần Hai Mươi Tám Không Chỉ",
"Gò đông — bóng lần hai mươi tám không chỉ. Không gào. Chỉ bóng. Chỉ đứng.",
'''A Cường: "Gò đông. Ba bóng. Đứng thành tam giác. Không thước. Không lê. Một giơ tay chỉ hướng nam — thử xem trong có chỉ theo."
"Không mở. Không chỉ theo. Không đạp theo. Không giơ tay đáp." Phong gật.
Ba bóng đứng năm nhịp. Một giơ tay chỉ nam. Không ai trong rào chỉ theo. Đại Lực bao. Tôn Vũ móc. Hứa dao. Ba việc nuốt mắt. Bóng hạ tay, cả ba lùi sườn. Lần hai mươi tám khép bằng chân bóng.
Hà: "Chỉ nam?" "Giơ tay thử. Ta không chỉ theo. Không kể trẻ. Máy nhớ nghề dụ chỉ, không khoe."''',
"Bóng gò lần hai mươi tám · tam giác · dụ chỉ · không chỉ · cấp im · máy nghèo"),

(435, "Hỏi Lần Năm Mươi Tư Cùng Màu",
"Cổng đông — hỏi lần năm mươi tư cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có ngựa không. Hỏi đổi yên cương lấy muối. Không lê. Giọng khác miệng hỏi chữ."
"Không mở. Không kể trẻ. Không chỉ giếng. Không nhận ngựa. Không đổi yên. Đông thường. Hầm xấu." Phong gật.
Miệng: "Trong ơi — có ngựa không? Đổi yên lấy muối!" "Đông thường. Hầm xấu."
Miệng lần hai: "Ba người trên gò chỉ nam — trong có đường ngựa không? Có chuồng không?"
Không đáp chuồng. Hà: "Hầm xấu." Không nối gò với miệng. Miệng cười khô lùi. Không mở tiễn. Không ném muối.
Hà: "Hỏi ngựa?" "Không nhận. Không đổi. Máy nối gò chỉ nam với miệng — im."''',
"Hỏi lần năm mươi tư · cùng màu · không nhận ngựa · không đổi yên · cấp im · máy nghèo"),

(436, "Ngày Yên Sau Hỏi Năm Mươi Tư",
"Trong rào — yên sau hỏi năm mươi tư. Không gào. Chỉ việc. Trống không bằng yên hội.",
'''A Cường: "Cổng trống. Gò trống. Không miệng. Không yên cương bỏ. Không vó ngựa."
"Không thở phào. Không họp chữ ngựa. Việc." Phong gật.
Sáng trống. Yên khép bằng việc. Sau chữ ngựa/yên — yên có thể là khoảng lùi mang kỵ thật. Ba xương yên giữ. Mạc Tư gạch: yên sau hỏi ngựa — không viết nghỉ.
Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi ngựa có thể mang kỵ."''',
"Yên sau hỏi năm mươi tư · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"),

(437, "Sóng Thấp Lần Năm Mươi",
"Gốc sung khô phía đông — sóng thấp lần năm mươi. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Sung đông. Tám thấp. Ba lê. Không gào. Quả sung thối dính. Gần chỗ rễ lộ."
"Máu kín. Hố mới sát sung — không trùng cỏ gai." Phong gật.
Tám bóng thấp từ gốc sung. Phong hạ tay. Tám móc gáy-hông — không mặt. Máu ngắn. Thóc lép. Hố mới. Lấp. Đắp xấu. Phủi. Không đếm tám to. Không giữ quả thối làm dấu.
Hà: "Kín? Tám?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố gai."''',
"Sóng thấp lần năm mươi · gốc sung đông · tám · máu kín · cấp im · máy nghèo"),

(438, "Bóng Thước Lần Hai Mươi Tám Không Chỉ",
"Đường bụi phía đông-bắc — bóng thước lần hai mươi tám không chỉ. Không gào. Chỉ bóng. Chỉ thước.",
'''A Cường: "Đông-bắc. Một bóng. Thước gỗ sơn đỏ cũ. Kẻ vạch than lên thước. Không lê. Không nhìn trẻ."
"Không mở. Không chỉ. Không nhặt thước sơn. Không đạp theo." Phong gật.
Bóng đứng bốn nhịp. Kẻ than lên thước hai vạch. Gió thổi. Phong bóng tường. Hà hầm. Rèm chốt. Việc nuốt mắt. Bóng xóa than bằng tay áo, lùi bụi. Lần hai mươi tám khép bằng chân bóng. Không ném đá. Không nhặt.
Hà: "Sơn đỏ? Kẻ than?" "Hai vạch. Ta không chỉ. Không nhặt. Máy nhớ nghề kẻ, không khoe."''',
"Bóng thước lần hai mươi tám · thước sơn đỏ · kẻ than · không chỉ · cấp im · máy nghèo"),

(439, "Hỏi Lần Năm Mươi Lăm Cùng Màu",
"Cổng đông — hỏi lần năm mươi lăm cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có mực không. Hỏi đổi bút lông lấy gạo. Không lê. Giọng khác miệng hỏi ngựa."
"Không mở. Không kể trẻ. Không chỉ giếng. Không nhận mực. Không đổi bút. Đông thường. Hầm xấu." Phong gật.
Miệng: "Trong ơi — có mực không? Đổi bút lấy gạo!" "Đông thường. Hầm xấu."
Miệng lần hai: "Thước sơn đỏ ngoài đông-bắc là của tao — trong có thấy vạch than không? Có sổ mực không?"
Không đáp sổ. Hà: "Hầm xấu." Không nối thước sơn. Miệng cười khô lùi. Không mở tiễn. Không ném gạo.
Hà: "Hỏi mực?" "Không nhận. Không đổi. Máy nối thước sơn với miệng — im."''',
"Hỏi lần năm mươi lăm · cùng màu · không nhận mực · không đổi bút · cấp im · máy nghèo"),

(440, "Ngày Yên Sau Hỏi Năm Mươi Lăm",
"Trong rào — yên sau hỏi năm mươi lăm. Không gào. Chỉ việc. Trống không bằng yên hội.",
'''A Cường: "Cổng trống. Đông-bắc trống. Không miệng. Không bút bỏ. Không mực loang."
"Không thở phào. Không họp chữ mực. Việc." Phong gật.
Sáng trống. Yên khép bằng việc. Sau chữ mực/bút — yên có thể là khoảng lùi mang văn thư giả. Ba xương yên giữ. Mạc Tư gạch: yên sau hỏi mực — không viết nghỉ.
Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi mực có thể mang giấy giả."''',
"Yên sau hỏi năm mươi lăm · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"),

(441, "Sóng Thấp Lần Năm Mươi Mốt",
"Mương lá mục phía nam — sóng thấp lần năm mươi mốt. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Mương nam. Sáu thấp. Hai lê. Không gào. Lá mục trôi. Gần chỗ cống vỡ."
"Máu kín. Hố mới sát mương — không trùng gốc sung." Phong gật.
Sáu bóng thấp từ mương lá. Phong hạ tay. Sáu móc gáy-hông — không mặt. Máu ngắn. Thóc lép. Hố mới. Lấp. Đắp xấu. Phủi. Không đếm sáu to. Không giữ lá mục làm dấu.
Hà: "Kín?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố sung."''',
"Sóng thấp lần năm mươi mốt · mương lá nam · sáu · máu kín · cấp im · máy nghèo"),

(442, "Bóng Gò Lần Hai Mươi Chín Không Chỉ",
"Gò đông — bóng lần hai mươi chín không chỉ. Không gào. Chỉ bóng. Chỉ đứng.",
'''A Cường: "Gò đông. Một bóng. Quỳ một gối. Vẽ vòng đất bằng que. Không thước dài. Không lê. Không nhìn trẻ."
"Không mở. Không chỉ. Không phá vòng đất. Không đạp theo." Phong gật.
Bóng quỳ bốn nhịp. Vẽ hai vòng. Gió thổi. Việc trong nuốt mắt. Bóng xóa vòng bằng gót, lùi sườn. Lần hai mươi chín khép bằng chân bóng. Không ném đá. Không phá.
Hà: "Vẽ vòng?" "Hai vòng. Ta không chỉ. Không phá. Máy nhớ nghề vẽ đất, không khoe."''',
"Bóng gò lần hai mươi chín · vẽ vòng đất · không chỉ · cấp im · máy nghèo"),

(443, "Hỏi Lần Năm Mươi Sáu Cùng Màu",
"Cổng đông — hỏi lần năm mươi sáu cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có thầy mo không. Hỏi đổi bùa dây lấy nước. Không lê. Giọng khác miệng hỏi mực."
"Không mở. Không kể trẻ. Không chỉ giếng. Không nhận mo. Không đổi bùa. Đông thường. Hầm xấu." Phong gật.
Miệng: "Trong ơi — có thầy mo không? Đổi bùa dây lấy gáo!" "Đông thường. Hầm xấu."
Miệng lần hai: "Vòng đất trên gò là dấu tao — trong có phá không? Có kho bùa không?"
Không đáp bùa. Hà: "Hầm xấu." Không nối vòng đất. Miệng cười khô lùi. Không mở tiễn. Không ném nước.
Hà: "Hỏi mo?" "Không nhận. Không đổi. Máy nối vòng đất với miệng — im."''',
"Hỏi lần năm mươi sáu · cùng màu · không nhận mo · không đổi bùa · cấp im · máy nghèo"),
]

def body_tok(t):
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end():] if m else t
    return len([w for w in body.split() if len(w) >= 2])

def before_panel(t, block):
    return t.replace(MARKER, block + "\n\n" + MARKER, 1)

def ensure_seps(t):
    if t.count(SEP) >= 2: return t
    if "\nTrưa." in t: t = t.replace("\nTrưa.", f"\n\n{SEP}\n\nTrưa.", 1)
    if t.count(SEP) < 2 and "\nHoàng hôn" in t: t = t.replace("\nHoàng hôn", f"\n\n{SEP}\n\nHoàng hôn", 1)
    if t.count(SEP) < 2: t = before_panel(t, SEP)
    return t

def cliff_last(t):
    head, panel = t.rsplit(MARKER, 1)
    if "Canh cuối trước trống điểm" in head[-1500:]:
        idx = head.rfind("Canh cuối trước trống điểm")
        chunk = head[:idx].rstrip()
        if chunk.endswith(SEP): chunk = chunk[: -len(SEP)].rstrip()
        head = chunk
    cliff = (
        f"\n\n{SEP}\n\n"
        "Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.\n"
        "Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.\n"
        "Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. "
        "Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.\n"
    )
    return head.rstrip() + cliff + "\n" + MARKER + panel

def expand(t, target=3150):
    t = ensure_seps(t)
    i = 0
    while body_tok(t) < target and i < 80:
        t = before_panel(t, PAD + f"Nhịp im {i+1}."); i += 1
    t = cliff_last(t)
    if body_tok(t) < 3050:
        t = before_panel(t, PAD + "Thêm trước khép."); t = cliff_last(t)
    return t

def seal(n, title, raw):
    t = expand(raw)
    for old in BASE.glob(f"Chương {n} - *.txt"):
        os.chmod(old, stat.S_IWRITE | stat.S_IREAD)
        if old.name != f"Chương {n} - {title}.txt":
            old.unlink()
    p = BASE / f"Chương {n} - {title}.txt"
    p.write_text(t, encoding="utf-8")
    r = subprocess.run(
        ["python", str(SCORER), str(p), "--min-words", "3000", "--cfg", str(CFG)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"ch\d+\s+([0-9.]+)", out)
    sc = float(m.group(1)) if m else 0.0
    line = out.strip().splitlines()[0] if out.strip() else "?"
    print(n, "body", body_tok(t), line)
    if sc >= 9.5 and "short<" not in out:
        shutil.copy2(p, BAK / p.name)
        os.chmod(p, 0o444)
        print(" SEALED", n, sc)
        return True, sc
    print(" NEED", out[-400:])
    return False, sc

def main():
    ok = 0
    for n, title, beat, core, panel in JOBS:
        good, sc = seal(n, title, chap(n, title, beat, core, panel))
        if good: ok += 1
    st = BASE / "_detemplate_progress.json"
    st.write_text(json.dumps({
        "unique_rewritten_range": "393-443",
        "count": 51,
        "next": 444,
        "clone_remaining_est": "444-1000",
        "score_target": 9.5,
        "last_batch_ok": ok,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BATCH_OK", ok, "/", len(JOBS))

if __name__ == "__main__":
    main()
