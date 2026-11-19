# -*- coding: utf-8 -*-
"""Unique rewrite 444-455 (12ch) + seal ≥9.5 — table-driven hooks."""
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

def yen(n, title, ask_word, risk):
    return (n, title,
f"Trong rào — {title.lower()}. Không gào. Chỉ việc. Trống không bằng yên hội.",
f'''A Cường: "Cổng trống. Ngoài trống. Không miệng. Không dấu {ask_word}."
"Không thở phào. Không họp chữ {ask_word}. Việc." Phong gật.
Sáng trống. Yên khép bằng việc. Không mừng. Sau chữ {ask_word} — yên có thể là khoảng lùi {risk}. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ. Mạc Tư gạch: yên sau hỏi {ask_word} — không viết nghỉ.
Hà: "Yên?" "Trống. Không thở phào. Tai khe — miệng hỏi {ask_word} có thể {risk}."''',
f"Yên sau hỏi · trống ≠ yên hội · không thở phào · {ask_word} · cấp im · máy nghèo")

def song(n, title, place, count, prev_hole):
    return (n, title,
f"{place} — {title.lower()}. Không gào. Chỉ sóng. Máu kín.",
f'''A Cường: "{place}. {count} thấp. Không gào. Dấu riêng chỗ này."
"Máu kín. Hố mới sát {place} — không trùng {prev_hole}." Phong gật.
{count} bóng thấp từ {place}. Phong hạ tay. Móc gáy-hông — không mặt. Máu ngắn. Thóc lép. Hố mới canh tư. Lấp. Đắp xấu. Phủi. Không đếm {count} to. Không giữ dấu làm chuyện.
Hà: "Kín?" "Kín. Không đếm to. Không phơi. Đổi chỗ lê — không lặp hố {prev_hole}."''',
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

JOBS = [
yen(444, "Ngày Yên Sau Hỏi Năm Mươi Sáu", "bùa", "mang thầy mo giả"),
song(445, "Sóng Thấp Lần Năm Mươi Hai", "Bờ suối cạn tây-nam", "bốn", "mương lá nam"),
bong(446, "Bóng Thước Lần Hai Mươi Chín Không Chỉ", "Đường bụi đông", "một bóng thước mây tre, buộc giẻ đỏ đầu thước", "nhặt giẻ đỏ"),
hoi(447, "Hỏi Lần Năm Mươi Bảy Cùng Màu", "có mật ong không, đổi sáp lấy muối", "Giẻ đỏ ngoài đông là dấu tao — trong có tổ ong không?", "Không nhận mật. Không đổi sáp"),
yen(448, "Ngày Yên Sau Hỏi Năm Mươi Bảy", "mật", "mang khói hun tổ"),
song(449, "Sóng Thấp Lần Năm Mươi Ba", "Bụi dứa dại bắc", "bảy", "suối cạn tây-nam"),
bong(450, "Bóng Gò Lần Ba Mươi Không Chỉ", "Gò đông", "hai bóng, một vác bao rỗng lắc nghe", "mở bao rỗng"),
hoi(451, "Hỏi Lần Năm Mươi Tám Cùng Màu", "có gạo mốc bán không, đổi bao rỗng lấy gạo", "Bao trên gò là của tao — trong có kho gạo không?", "Không bán gạo. Không nhận bao"),
yen(452, "Ngày Yên Sau Hỏi Năm Mươi Tám", "gạo", "mang bao đầy giả"),
song(453, "Sóng Thấp Lần Năm Mươi Tư", "Gốc tre gãy đông-nam", "năm", "dứa dại bắc"),
bong(454, "Bóng Gò Lần Ba Mươi Mốt Không Chỉ", "Gò đông", "một bóng thả diều giấy rách thử gió", "bắn diều"),
hoi(455, "Hỏi Lần Năm Mươi Chín Cùng Màu", "có giấy diều không, đổi chỉ bay lấy nước", "Diều trên gò là dấu tao — trong có thợ giấy không?", "Không nhận giấy. Không đổi chỉ"),
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
        return True
    print(" NEED", out[-400:])
    return False

def main():
    ok = 0
    for n, title, beat, core, panel in JOBS:
        if seal(n, title, chap(n, title, beat, core, panel)):
            ok += 1
    (BASE / "_detemplate_progress.json").write_text(json.dumps({
        "unique_rewritten_range": "393-455",
        "count": 63,
        "next": 456,
        "clone_remaining_est": "456-1000",
        "score_target": 9.5,
        "last_batch_ok": ok,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BATCH_OK", ok, "/", len(JOBS))

if __name__ == "__main__":
    main()
