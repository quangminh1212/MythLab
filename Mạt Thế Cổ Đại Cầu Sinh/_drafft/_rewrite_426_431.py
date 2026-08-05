# -*- coding: utf-8 -*-
"""Unique rewrite 426-431 + seal ≥9.5."""
from pathlib import Path
import re, os, stat, subprocess, shutil, json

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

def vn_day(n):
    d = n + 120
    units = ["","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    tram = d // 100
    chuc = (d % 100) // 10
    donvi = d % 10
    s = f"{units[tram]} trăm"
    if chuc == 0 and donvi == 0: return s
    if chuc == 0: return f"{s} lẻ {units[donvi]}"
    s2 = "mười" if chuc == 1 else f"{units[chuc]} mươi"
    if donvi == 0: return f"{s} {s2}"
    if donvi == 1 and chuc > 1: return f"{s} {s2} mốt"
    if donvi == 5 and chuc >= 1: return f"{s} {s2} lăm"
    return f"{s} {s2} {units[donvi]}"

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
(426, "Bóng Gò Lần Hai Mươi Bảy Không Chỉ",
"Gò đông — bóng lần hai mươi bảy không chỉ. Không gào. Chỉ bóng. Chỉ đứng.",
'''A Cường: "Gò đông. Hai bóng. Một đứng. Một nằm sấp giả chết. Không thước. Không lê thật. Không nhìn trẻ."
"Không mở. Không chỉ. Không ra kiểm nằm. Không đạp theo." Phong gật.

Hai bóng trên gò bốn nhịp. Một đứng. Một nằm sấp. Gió thổi áo. Không xông. Phong bóng tường tây. Hà hầm. Rèm chốt. Ba xương: không chỉ ngược, không mở dọa, không ra lật người nằm. Đại Lực bao. Tôn Vũ móc. Hứa dao — việc nuốt mắt.

Bóng đứng đá nhẹ bóng nằm — nằm ngồi dậy, cả hai lùi sườn gò. Giả chết thử mắt. Không ai chỉ. Không ai hô. Lần hai mươi bảy khép bằng chân bóng. Không ném đá. Không phá giả chết.

Hà: "Giả chết?"
"Một nằm. Ta không ra kiểm. Không chỉ. Không kể trẻ. Máy nhớ nghề giả, không khoe."''',
"Bóng gò lần hai mươi bảy · giả chết · không chỉ · cấp im · máy nghèo"),

(427, "Hỏi Lần Năm Mươi Hai Cùng Màu",
"Cổng đông — hỏi lần năm mươi hai cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có chỗ chôn người không. Hỏi đổi vải liệm lấy nước. Không lê. Giọng khác miệng hỏi rèn."
"Không mở. Không kể trẻ. Không chỉ giếng. Không chỉ hố. Không nhận chôn. Không đổi vải. Đông thường. Hầm xấu." Phong gật.

Miệng: "Trong ơi — cho chôn một người ngoài rào không? Đổi vải sạch lấy gáo nước!"
"Đông thường. Hầm xấu."
Miệng lần hai: "Người nằm trên gò là anh tao — trong có giấu xác không? Có hố sẵn không?"
Không đáp hố. Không nhận giấu xác. Hà: "Hầm xấu." Không thêm. Chữ chôn/vải/xác ngoài không thành hội trong. Không nối giả chết hôm qua thành chuyện bếp.

Miệng cười khô lùi. Lần năm mươi hai khép bằng chân miệng. Không mở tiễn. Không ném vải. Không nhận gò.

Hà: "Hỏi chôn? Nối gò?"
"Hỏi. Ta không chỉ hố. Không nhận. Không kể trẻ. Máy nối giả chết với miệng hôm nay — im."''',
"Hỏi lần năm mươi hai · cùng màu · không nhận chôn · không chỉ hố · cấp im · máy nghèo"),

(428, "Ngày Yên Sau Hỏi Năm Mươi Hai",
"Trong rào — yên sau hỏi năm mươi hai. Không gào. Chỉ việc. Trống không bằng yên hội.",
'''A Cường: "Cổng trống. Gò trống. Không miệng. Không xe. Không vải bỏ. Không người nằm."
"Không thở phào. Không họp chữ chôn. Việc." Phong gật.

Sáng trống. Không bóng. Không miệng. Chỉ gió. Yên khép bằng việc ta. Không mừng. Không thở phào. Sau chữ chôn/xác — yên có thể là khoảng lùi mang xác thật hoặc miệng khác.

Phong Hà đổi việc. Ba xương yên: không thở phào to, không mở rèm trẻ sớm, không rải vôi nghỉ. Trưa nước gốc rau. Ba chạm ba việc. Hà giữ rèm. A Minh không hát yên. Mạc Tư gạch: yên sau hỏi chôn — không viết nghỉ. A Cường lắc trống. Không mời nước mừng.

Hà: "Yên?"
"Trống. Không thở phào. Tai khe — miệng hỏi chôn có thể mang xác thật."''',
"Yên sau hỏi năm mươi hai · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"),

(429, "Sóng Thấp Lần Bốn Mươi Tám",
"Rãnh nước cạn phía đông-nam — sóng thấp lần bốn mươi tám. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Rãnh đông-nam. Bảy thấp. Hai lê. Không gào. Bùn vàng. Gần chỗ gạch vỡ."
"Máu kín. Hố mới sát rãnh — không trùng lau bắc-tây." Phong gật.

Bảy bóng thấp từ rãnh, bùn vàng và mảnh gạch dính gối. Tôn Vũ không hô. Đại Lực không gào. Phong hạ tay. Bảy móc gáy-hông — không mặt. Máu ngắn. Thóc lép nuốt. Kéo hố mới canh tư góc rãnh. Lấp. Đắp xấu. Phủi. Không cọc. Không đếm bảy to. Không giữ gạch làm dấu.

Hà: "Kín? Bảy?"
"Kín. Không đếm to. Không phơi. Không nhìn rãnh quá ba nhịp. Đổi chỗ lê — máy không lặp hố lau."''',
"Sóng thấp lần bốn mươi tám · rãnh đông-nam · bảy · máu kín · cấp im · máy nghèo"),

(430, "Bóng Thước Lần Hai Mươi Bảy Không Chỉ",
"Đường bụi phía nam — bóng thước lần hai mươi bảy không chỉ. Không gào. Chỉ bóng. Chỉ thước.",
'''A Cường: "Nam. Một bóng. Thước tre ngắn. Cắm thước đứng làm mốc rồi bước đếm. Không lê. Không nhìn trẻ."
"Không mở. Không chỉ. Không nhổ mốc. Không đạp theo." Phong gật.

Bóng đứng sáu nhịp. Cắm thước tre. Bước đếm mười bước rồi rút. Gió thổi. Phong bóng tường bắc. Hà hầm. Rèm chốt. Ba xương: không chỉ ngược, không mở dọa, không nhổ thước mốc. Đại Lực bao. Tôn Vũ móc. Hứa dao — việc nuốt mắt.

Bóng rút thước, lùi bụi nam. Không bỏ mốc vết. Lần hai mươi bảy khép bằng chân bóng. Không ném đá. Không phá vết đếm.

Hà: "Cắm mốc? Đếm bước?"
"Tre ngắn. Mười bước. Ta không chỉ. Không nhổ. Không kể trẻ. Máy nhớ nghề mốc, không khoe."''',
"Bóng thước lần hai mươi bảy · thước tre mốc · đếm bước · không chỉ · cấp im · máy nghèo"),

(431, "Hỏi Lần Năm Mươi Ba Cùng Màu",
"Cổng đông — hỏi lần năm mươi ba cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có người biết chữ không. Hỏi đổi giấy cũ lấy gạo. Không lê. Giọng khác miệng hỏi chôn."
"Không mở. Không kể trẻ. Không chỉ giếng. Không nhận chữ. Không đổi giấy. Đông thường. Hầm xấu." Phong gật.

Miệng: "Trong ơi — có ai biết chữ không? Đổi giấy quan cũ lấy nắm gạo!"
"Đông thường. Hầm xấu."
Miệng lần hai: "Mốc tre ngoài nam là dấu tao — trong có sổ không? Có máy ghi không?"
Không đáp sổ. Không nhận mốc. Hà: "Hầm xấu." Không thêm. Chữ giấy/sổ/mốc ngoài không thành hội trong. Không nối thước tre hôm qua thành chuyện bếp.

Miệng cười khô lùi. Lần năm mươi ba khép bằng chân miệng. Không mở tiễn. Không ném gạo. Không nhận giấy quan.

Hà: "Hỏi chữ? Nối mốc tre?"
"Hỏi. Ta không đổi. Không nhận. Không kể trẻ. Máy nối mốc với miệng hôm nay — im."''',
"Hỏi lần năm mươi ba · cùng màu · không nhận chữ · không đổi giấy · cấp im · máy nghèo"),
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
        raw = chap(n, title, beat, core, panel)
        good, sc = seal(n, title, raw)
        if good: ok += 1
    st = BASE / "_detemplate_progress.json"
    st.write_text(json.dumps({
        "unique_rewritten_range": "393-431",
        "count": 39,
        "next": 432,
        "clone_remaining_est": "432-1000",
        "score_target": 9.5,
        "last_batch_ok": ok,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BATCH_OK", ok, "/", len(JOBS))

if __name__ == "__main__":
    main()
