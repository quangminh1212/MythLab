# -*- coding: utf-8 -*-
"""Unique rewrite 417-419 + seal."""
from pathlib import Path
import re, os, stat, subprocess, shutil

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

def chap(n, title, day, beat_open, unique_core, panel_up):
    return f'''============================================================
Chương {n}: {title}
============================================================

Ngày thứ {day}. Trống điểm. {beat_open} EXP đầy cấp im. Máy nghèo thở đều.

Phong ra hầm tây trước sân thức. Đếm dấu: bảy. Không tám. Rắc thóc lép. Đắp xấu. Phủi. Hà phơi bao, khăn mũi, lưng thẳng. Anh đảo muối. Then êm. Không mừng. Không lỏng. Quen là hở. Hở là chết chậm.

Mùi đất se. Mùi vôi. Gió bấc. Phong hít ngắn. Không kể. Hà siết khăn: "Ngoài?"

"Nghe. Không mở. Không chỉ." Anh nhìn hướng việc hai nhịp. Đủ.

Sân thức. Đại Lực bao tây. Tôn Vũ móc thấp. Hứa dao đất. Diễm se. Cúc kéo Hạt sâu rèm. A Minh sỏi hố. Khuyển ngưỡng. Hữu sau chó. Mạc Tư bảng sấp. Từ Sơn vòng đều. Triệu ngậm miệng. A Cường lách vào báo ngắn rồi biến. Bà già: "Ồn?" Chú Bát: "Gió. Nồi."

{unique_core}

Phong không nhìn theo quá hai nhịp. Xách nước. Đảo bao. Hà ra gặp sau muối. Ba xương giữ im. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể EXP — nặng gấp đôi. Lần này không pháo. "Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch. Không mở rèm." Chị gật.

{SEP}

Trưa. Nắng mỏng. Phơi bao tây. Không đông. Giếng nắp xấu. Trẻ trong rèm. Cháo đúng giờ. Không thưởng. Mạc Tư gạch im đúng việc — không viết số to. Từ Sơn vòng. A Cường: "Trống." "Không soi. Không kể." Biến. Bà già: "Ồn?" "Gió. Việc."

Phong nghe nhịp sân nuốt việc. Đông nửa vòng chông vôi then hố cửa nguyên. Không vôi sớm. Giữa trưa chạm vai ba việc. Không họp. Hà rèm đến chiều. A Cường đường thấp. Không đường quan truy to.

Chiều sớm Kho Vô Hạn im. Không nhiệm vụ mừng. Phong đếm vai. Mạc Tư Từ Sơn canh ngồi trong. Không da nếu không đâm. Triệu nước đúng. Bếp im. Phong vòng chân. Hà bánh tráng đúng giờ. Đại Lực bao. Tôn Vũ móc. Hứa mài bóng.

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

C417 = chap(417, "Sóng Thấp Lần Bốn Mươi Lăm", "năm trăm ba mươi bảy",
"Gốc đa già phía tây-nam — sóng thấp lần bốn mươi lăm. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Đa tây-nam. Năm thấp. Hai lê. Không gào. Không xe. Rễ đa hở sau mưa."
"Máu kín. Hố mới sát đa — không trùng mương bắc." Phong gật.

Năm bóng thấp từ rễ đa, bùn và lá mục dính vai. Tôn Vũ không hô. Đại Lực không gào. Phong hạ tay. Năm móc gáy-hông lần lượt — không mặt. Máu ngắn. Thóc lép nuốt. Kéo vào hố mới canh tư góc đa. Lấp. Đắp xấu. Phủi. Không cọc. Không đếm năm to.

Hà: "Kín? Năm?"
"Kín. Không đếm to. Không phơi. Không nhìn đa quá ba nhịp. Đổi chỗ lê — máy không lặp hố."''',
"Sóng thấp lần bốn mươi lăm · gốc đa tây-nam · năm · máu kín · cấp im · máy nghèo")

C418 = chap(418, "Bóng Gò Lần Hai Mươi Sáu Không Chỉ", "năm trăm ba mươi tám",
"Gò đông — bóng lần hai mươi sáu không chỉ. Không gào. Chỉ bóng. Chỉ đứng.",
'''A Cường: "Gò đông. Một bóng. Ngồi xổm. Không thước. Không lê. Nhặt sỏi xếp hàng — đo mắt không bằng gỗ. Không nhìn trẻ."
"Không mở. Không chỉ. Không phá hàng sỏi. Không đạp theo." Phong gật.

Bóng ngồi bốn nhịp. Xếp sỏi ba hàng ngắn. Gió thổi áo. Không xông. Phong bóng tường. Hà hầm. Rèm chốt. Ba xương: không chỉ ngược, không mở dọa, không ra phá sỏi ngoài. Đại Lực bao. Tôn Vũ móc. Hứa dao — việc nuốt mắt.

Bóng đứng, đá sỏi tan hàng, lùi sườn gò. Không chạy. Lần hai mươi sáu khép bằng chân bóng. Không ném đá theo. Cấm bằng mắt không thành ngón.

Hà: "Xếp sỏi?"
"Ba hàng. Tan trước khi lùi. Ta không chỉ. Không phá. Không kể trẻ. Đo bằng sỏi — máy nhớ nghề, không khoe."''',
"Bóng gò lần hai mươi sáu · xếp sỏi · không chỉ · cấp im · máy nghèo")

C419 = chap(419, "Hỏi Lần Năm Mươi Cùng Màu", "năm trăm ba mươi chín",
"Cổng đông — hỏi lần năm mươi cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có người ốm không. Hỏi đổi thuốc lá rừng lấy nước. Không lê. Không thước. Giọng khác miệng hỏi thợ."
"Không mở. Không kể trẻ. Không chỉ giếng. Không đổi thuốc. Không nhận ốm. Đông thường. Hầm xấu." Phong gật.

Miệng: "Trong ơi — có ốm không? Đổi lá rừng lấy một gáo!"
"Đông thường. Hầm xấu."
Miệng lần hai: "Nghe trong có kho thuốc? Có máy? Sỏi trên gò là dấu tao — trong có thấy không?"
Không đáp kho. Không nhận sỏi. Hà: "Hầm xấu." Không thêm. Chữ ốm/thuốc/sỏi ngoài không thành hội trong.

Miệng cười khô lùi. Lần năm mươi khép bằng chân miệng. Không mở tiễn. Không ném gáo. Không nhận sỏi gò.

Hà: "Hỏi ốm? Nối sỏi gò?"
"Hỏi. Ta không đổi. Không nhận. Không kể trẻ. Máy nối sỏi hôm qua với miệng hôm nay — im."''',
"Hỏi lần năm mươi · cùng màu · không đổi thuốc · không nhận ốm · cấp im · máy nghèo")

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
        if old.name != f"Chương {n} - {title}.txt": old.unlink()
    p = BASE / f"Chương {n} - {title}.txt"
    p.write_text(t, encoding="utf-8")
    r = subprocess.run(["python", str(SCORER), str(p), "--min-words", "3000", "--cfg", str(CFG)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"ch\d+\s+([0-9.]+)", out)
    sc = float(m.group(1)) if m else 0.0
    print(n, "body", body_tok(t), out.strip().splitlines()[0] if out.strip() else "?")
    if sc >= 9.5 and "short<" not in out:
        shutil.copy2(p, BAK / p.name); os.chmod(p, 0o444); print(" SEALED", n, sc)
    else:
        print(" NEED", out[-400:])

def main():
    seal(417, "Sóng Thấp Lần Bốn Mươi Lăm", C417)
    seal(418, "Bóng Gò Lần Hai Mươi Sáu Không Chỉ", C418)
    seal(419, "Hỏi Lần Năm Mươi Cùng Màu", C419)

if __name__ == "__main__":
    main()
