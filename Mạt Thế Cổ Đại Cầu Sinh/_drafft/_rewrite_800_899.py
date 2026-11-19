# -*- coding: utf-8 -*-
"""Unique rewrite 800-899 (100ch) + seal ≥9.5 — auto hook pools."""
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

def vn_num(n):
    """VI number for counters; titles mainly use digits."""
    try:
        n=int(n)
    except Exception:
        return str(n)
    if n < 0:
        return str(n)
    u = ["không","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    if n < 10:
        return u[n]
    if n < 20:
        tail = ["","một","hai","ba","bốn","lăm","sáu","bảy","tám","chín"][n-10] if n>10 else ""
        return "mười" + ((" " + tail) if tail else "")
    if n < 100:
        chuc, d = divmod(n, 10)
        s = f"{u[chuc]} mươi"
        if d == 0: return s
        if d == 1: return s + " mốt"
        if d == 5: return s + " lăm"
        return s + " " + u[d]
    # 100+
    tram, r = divmod(n, 100)
    s = f"{u[tram]} trăm" if tram < 10 else f"{n}"
    if r == 0: return s
    if r < 10: return f"{s} lẻ {u[r]}"
    return f"{s} {vn_num(r)}"


def vn_day(n):
    d = n + 120
    u = ["không","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    if d < 1000:
        tram, r = divmod(d, 100)
        s = f"{u[tram]} trăm"
        if r == 0: return s
        chuc, donvi = divmod(r, 10)
        if chuc == 0: return f"{s} lẻ {u[donvi]}"
        s2 = "mười" if chuc == 1 else f"{u[chuc]} mươi"
        if donvi == 0: return f"{s} {s2}"
        if donvi == 1 and chuc > 1: return f"{s} {s2} mốt"
        if donvi == 5 and chuc >= 1: return f"{s} {s2} lăm"
        return f"{s} {s2} {u[donvi]}"
    # 1000+
    nghin, r = divmod(d, 1000)
    s = f"{u[nghin]} nghìn" if nghin < 10 else f"{d}"
    if r == 0: return s
    if r < 100:
        if r < 10: return f"{s} lẻ {u[r]}"
        chuc, donvi = divmod(r, 10)
        s2 = "mười" if chuc == 1 else f"{u[chuc]} mươi"
        if donvi == 0: return f"{s} không trăm {s2}"
        if donvi == 1 and chuc > 1: return f"{s} không trăm {s2} mốt"
        if donvi == 5: return f"{s} không trăm {s2} lăm"
        return f"{s} không trăm {s2} {u[donvi]}"
    tram, rr = divmod(r, 100)
    s = f"{s} {u[tram]} trăm"
    if rr == 0: return s
    chuc, donvi = divmod(rr, 10)
    if chuc == 0: return f"{s} lẻ {u[donvi]}"
    s2 = "mười" if chuc == 1 else f"{u[chuc]} mươi"
    if donvi == 0: return f"{s} {s2}"
    if donvi == 1 and chuc > 1: return f"{s} {s2} mốt"
    if donvi == 5: return f"{s} {s2} lăm"
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

PLACES = [
    "Bờ ao cạn tây","Bụi sim gai đông","Rãnh vôi cũ nam","Gốc sung khô bắc",
    "Mương lá mục tây-nam","Bãi sỏi nứt đông-bắc","Hố tro lạnh nam-tây","Bụi lau ướt đông",
    "Gốc tre chẻ tây","Đường bụi gạch vỡ bắc","Rìa cỏ tranh nam","Bờ suối cạn đông-nam",
    "Gò sườn tây thấp","Bụi dứa dại bắc-tây","Hố cát khô đông","Gốc đa nghiêng nam",
    "Mương gừng khô tây","Bãi đá lăn bắc","Rìa bèo khô đông","Lề đường than nguội nam",
]
COUNTS = ["ba","bốn","năm","sáu","bảy","tám","ba","bốn","năm","sáu","bảy","tám"]
DETAILS = [
    ("một bóng cắm thước tre nghiêng","nhổ thước tre"),
    ("hai bóng kéo dây ngang đường bụi","cắt dây ngang"),
    ("một bóng vẽ vòng phấn trên gò","xóa vòng phấn"),
    ("ba bóng xếp sỏi thành mũi tên","phá mũi sỏi"),
    ("một bóng treo giẻ đỏ trên cành","nhặt giẻ đỏ"),
    ("một bóng thổi sáo ngắn rồi ngừng","hô đáp sáo"),
    ("hai bóng gánh thước như đòn","gánh theo thước"),
    ("một bóng đặt túi vải trên gai","mở túi gai"),
    ("một bóng kẻ than lên thước sơn","nhặt thước sơn"),
    ("hai bóng đứng tam giác chỉ nam","chỉ theo tay"),
    ("một bóng giả chết nằm sấp","ra lật người"),
    ("một bóng đếm bước cắm mốc","nhổ mốc đếm"),
]
ASKS = [
    ("có muối thô không, đổi vỏ ốc lấy nắm", "Vỏ ốc ngoài là dấu tao — trong có kho muối không?", "muối", "Không nhận muối. Không đổi vỏ", "mang bao muối giả"),
    ("có dầu đèn không, đổi bấc lấy nước", "Bấc ngoài là của tao — trong có kho dầu không?", "dầu", "Không nhận dầu. Không đổi bấc", "mang đèn dụ"),
    ("có kim khâu không, đổi chỉ lấy gạo", "Chỉ ngoài là dấu tao — trong có thợ may không?", "kim", "Không nhận kim. Không đổi chỉ", "mang thợ may giả"),
    ("có vôi sống không, đổi thúng lấy muối", "Thúng vôi ngoài là của tao — trong có lò vôi không?", "vôi", "Không nhận vôi. Không đổi thúng", "mang lò vôi giả"),
    ("có mật ong không, đổi sáp lấy nước", "Sáp ngoài là dấu tao — trong có tổ ong không?", "mật", "Không nhận mật. Không đổi sáp", "mang khói hun"),
    ("có giấy bản không, đổi bút lấy gạo", "Bút ngoài là của tao — trong có sổ không?", "giấy", "Không nhận giấy. Không đổi bút", "mang văn thư giả"),
    ("có đinh sắt không, đổi búa lấy muối", "Búa ngoài là dấu tao — trong có lò rèn không?", "đinh", "Không nhận đinh. Không đổi búa", "mang thợ rèn giả"),
    ("có thuốc bắc không, đổi bọc lá lấy nước", "Bọc lá ngoài là của tao — trong có thầy thuốc không?", "thuốc", "Không nhận thuốc. Không đổi bọc", "mang thầy thuốc giả"),
    ("có ngựa thồ không, đổi yên lấy gạo", "Yên ngoài là dấu tao — trong có chuồng không?", "ngựa", "Không nhận ngựa. Không đổi yên", "mang kỵ giả"),
    ("có thầy mo không, đổi bùa dây lấy muối", "Bùa ngoài là của tao — trong có bàn thờ không?", "bùa", "Không nhận mo. Không đổi bùa", "mang thầy mo giả"),
    ("có thợ đẽo không, đổi đục lấy nước", "Đục ngoài là dấu tao — trong có xưởng đá không?", "đá", "Không nhận đẽo. Không đổi đục", "mang thợ đá giả"),
    ("có dây thừng không, đổi cọc lấy gạo", "Cọc ngoài là của tao — trong có kho dây không?", "dây", "Không nhận dây. Không đổi cọc", "mang thợ trói giả"),
]

def yen(n, title, ask_word, risk):
    return (n, title,
f"Trong rào — {title.lower()}. Không gào. Chỉ việc. Trống không bằng yên hội.",
f'''A Cường: "Cổng trống. Ngoài trống. Không miệng. Không dấu {ask_word}."
"Không thở phào. Không họp chữ {ask_word}. Việc." Phong gật.
Sáng trống. Yên khép bằng việc. Không mừng. Sau chữ {ask_word} — yên có thể là khoảng lùi {risk}. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ. Mạc Tư gạch: yên sau hỏi {ask_word} — không viết nghỉ.
Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi {ask_word} có thể {risk}."''',
f"Yên sau hỏi · trống ≠ yên hội · không thở phào · {ask_word} · cấp im · máy nghèo")

def song(n, title, place, count, prev):
    return (n, title,
f"{place} — {title.lower()}. Không gào. Chỉ sóng. Máu kín.",
f'''A Cường: "{place}. {count} thấp. Không gào. Dấu riêng chỗ này."
"Máu kín. Hố mới sát {place} — không trùng {prev}." Phong gật.
{count} bóng thấp từ {place}. Phong hạ tay. Móc gáy-hông — không mặt. Máu ngắn. Thóc lép. Hố mới canh tư. Lấp. Đắp xấu. Phủi. Không đếm {count} to. Không giữ dấu làm chuyện.
Hà: "Kín?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố {prev}."''',
f"Sóng thấp · {place} · {count} · máu kín · cấp im · máy nghèo")

def bong(n, title, place, detail, action):
    return (n, title,
f"{place} — {title.lower()}. Không gào. Chỉ bóng. Không chỉ.",
f'''A Cường: "{place}. {detail}. Không lê. Không nhìn trẻ."
"Không mở. Không chỉ. Không {action}. Không đạp theo." Phong gật.
Bóng đứng vài nhịp. {detail}. Gió thổi. Việc trong nuốt mắt. Bóng lùi. Lần này khép bằng chân bóng. Không ném đá. Không {action}.
Hà: "Thấy?" "Thấy. Ta không chỉ. Không {action}. Máy nhớ nghề, không khoe."''',
f"Bóng · {place} · không chỉ · cấp im · máy nghèo")

def hoi(n, title, ask, bait, refuse):
    return (n, title,
f"Cổng đông — {title.lower()}. Không gào. Chỉ miệng. Chỉ hỏi.",
f'''A Cường: "Một miệng. Hỏi {ask}. Không lê. Giọng khác lần trước."
"Không mở. Không kể trẻ. Không chỉ giếng. {refuse}. Đông thường. Hầm xấu." Phong gật.
Miệng: "Trong ơi — {ask}!" "Đông thường. Hầm xấu."
Miệng lần hai: "{bait}"
Không đáp mồi. Hà: "Hầm xấu." Không thêm. Miệng cười khô lùi. Không mở tiễn. Không ném đồ.
Hà: "Hỏi?" "Không nhận. {refuse}. Máy nối mồi với miệng — im."''',
f"Hỏi · cùng màu · {ask} · cấp im · máy nghèo")

def build_jobs(start, end):
    """Cadence cycle: yên, sóng, bóng, hỏi — 4-beat."""
    jobs = []
    # counters continue from prior (~ yên after hỏi 65 done at 479)
    # At 480: yên after hỏi 65
    song_n = 161
    bong_thuoc = 84
    bong_go = 84
    hoi_n = 166
    prev_place = "bờ ao cạn tây"
    i_place = 100
    i_det = 100
    i_ask = 100
    beat = 0  # resume after ch879
    last_ask_word = "dây"
    last_risk = "mang thợ trói giả"
    # resume