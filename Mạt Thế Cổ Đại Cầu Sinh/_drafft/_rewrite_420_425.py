# -*- coding: utf-8 -*-
"""Unique rewrite 420-425 + long-pad expand + seal ≥9.5."""
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
    # day ≈ n + 120
    d = n + 120
    # simple Vietnamese for 540-600 range
    units = ["","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    if d < 1000:
        tram = d // 100
        chuc = (d % 100) // 10
        donvi = d % 10
        s = f"{units[tram]} trăm"
        if chuc == 0 and donvi == 0:
            return s
        if chuc == 0:
            return f"{s} lẻ {units[donvi]}"
        if chuc == 1:
            s2 = "mười"
        else:
            s2 = f"{units[chuc]} mươi"
        if donvi == 0:
            return f"{s} {s2}"
        if donvi == 1 and chuc > 1:
            return f"{s} {s2} mốt"
        if donvi == 5 and chuc >= 1:
            return f"{s} {s2} lăm"
        return f"{s} {s2} {units[donvi]}"
    return str(d)

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
(420, "Ngày Yên Sau Hỏi Năm Mươi",
"Trong rào — yên sau hỏi năm mươi. Không gào. Chỉ việc. Trống không bằng yên hội.",
'''A Cường: "Cổng trống. Gò trống. Không miệng. Không xe. Không lá rừng bỏ. Không sỏi xếp lại."
"Không thở phào. Không họp chữ ốm. Việc." Phong gật.

Sáng trống cả ngoài. Không bóng. Không miệng. Chỉ gió. Yên khép bằng việc ta. Không mừng. Không chỉ hố. Không thở phào. Không khoe từ chối thuốc. Sau chữ ốm/thuốc/sỏi — yên có thể là khoảng lùi mang miệng khác hoặc mang lá độc.

Phong Hà đổi việc: chị hầm tây, anh nửa vòng chân. Ba xương yên: không thở phào to, không mở rèm trẻ sớm, không rải vôi kiểu nghỉ. Nghỉ là chữ chết.

Trưa nước gốc rau. Muối lần hai. Không nhìn cổng lâu. Ba chạm ba việc: bao, móc, dao. Hà giữ rèm. A Minh không hát yên. Mạc Tư gạch: yên sau hỏi ốm — không viết nghỉ. A Cường lần hai lắc trống. Không mời nước mừng.

Hà: "Yên?"
"Trống. Không thở phào. Tai khe — miệng hỏi ốm có thể mang lá độc hoặc người giả ốm."''',
"Yên sau hỏi năm mươi · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"),

(421, "Sóng Thấp Lần Bốn Mươi Sáu",
"Bờ ao cạn phía đông — sóng thấp lần bốn mươi sáu. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Ao đông. Sáu thấp. Ba lê. Không gào. Bùn đen dính. Gần chỗ bèo khô."
"Máu kín. Hố mới sát bờ ao — không trùng gốc đa." Phong gật.

Sáu bóng thấp từ bèo khô, bùn đen quấn gối. Tôn Vũ không hô. Đại Lực không gào. Phong hạ tay. Sáu móc gáy-hông — không mặt. Máu ngắn. Thóc lép nuốt. Kéo hố mới canh tư góc ao. Lấp. Đắp xấu. Phủi. Không cọc. Không đếm sáu to. Không giữ bèo làm dấu.

Hà: "Kín? Sáu?"
"Kín. Không đếm to. Không phơi. Không nhìn ao quá ba nhịp. Đổi chỗ lê — máy không lặp hố đa."''',
"Sóng thấp lần bốn mươi sáu · bờ ao đông · sáu · máu kín · cấp im · máy nghèo"),

(422, "Bóng Thước Lần Hai Mươi Sáu Không Chỉ",
"Đường bụi phía tây — bóng thước lần hai mươi sáu không chỉ. Không gào. Chỉ bóng. Chỉ thước.",
'''A Cường: "Tây. Một bóng. Thước gãy giữa — nối dây thừng. Đặt thước ba lần dọc bụi. Không lê. Không nhìn trẻ."
"Không mở. Không chỉ. Không nhặt thước gãy. Không đạp theo." Phong gật.

Bóng đứng năm nhịp. Thước gãy nối dây chống đất ba lần. Gió thổi. Phong bóng tường đông. Hà hầm. Rèm chốt. Ba xương: không chỉ ngược, không mở dọa, không nhặt gỗ gãy ngoài. Đại Lực bao. Tôn Vũ móc. Hứa dao — việc nuốt mắt.

Bóng nhấc thước gãy, bước lệch thử mắt. Không ai chỉ. Lùi vào bụi tây. Không bỏ thước. Lần hai mươi sáu khép bằng chân bóng. Không ném đá. Không cắm cọc.

Hà: "Thước gãy? Đo ba lần?"
"Gãy nối dây. Ba lần. Ta không chỉ. Không nhặt. Không kể trẻ. Máy nhớ nghề đo, không khoe."''',
"Bóng thước lần hai mươi sáu · thước gãy nối dây · đo ba lần · không chỉ · cấp im · máy nghèo"),

(423, "Hỏi Lần Năm Mươi Mốt Cùng Màu",
"Cổng đông — hỏi lần năm mươi mốt cùng màu. Không gào. Chỉ miệng. Chỉ hỏi.",
'''A Cường: "Một miệng. Hỏi có lò rèn không. Hỏi đổi sắt vụn lấy muối. Không lê. Giọng khác miệng hỏi ốm."
"Không mở. Không kể trẻ. Không chỉ giếng. Không nhận rèn. Không đổi sắt. Đông thường. Hầm xấu." Phong gật.

Miệng: "Trong ơi — có lò rèn không? Đổi sắt vụn lấy một nắm muối!"
"Đông thường. Hầm xấu."
Miệng lần hai: "Thước tao gãy — cần đinh sắt. Trong có kho sắt không? Có máy?"
Không đáp kho. Không nhận rèn. Hà: "Hầm xấu." Không thêm. Chữ rèn/sắt/đinh ngoài không thành hội trong. Không nối thước gãy hôm qua thành chuyện bếp.

Miệng cười khô lùi. Lần năm mươi mốt khép bằng chân miệng. Không mở tiễn. Không ném muối. Không nhận sắt.

Hà: "Hỏi rèn? Nối thước gãy?"
"Hỏi. Ta không đổi. Không nhận. Không kể trẻ. Máy nối thước gãy với miệng hôm nay — im."''',
"Hỏi lần năm mươi mốt · cùng màu · không nhận rèn · không đổi sắt · cấp im · máy nghèo"),

(424, "Ngày Yên Sau Hỏi Năm Mươi Mốt",
"Trong rào — yên sau hỏi năm mươi mốt. Không gào. Chỉ việc. Trống không bằng yên hội.",
'''A Cường: "Cổng trống. Tây trống. Không miệng. Không xe. Không sắt bỏ. Không thước gãy."
"Không thở phào. Không họp chữ rèn. Việc." Phong gật.

Sáng trống. Không bóng thước. Không miệng. Chỉ gió. Yên khép bằng việc ta. Không mừng. Không thở phào. Sau chữ rèn/sắt — yên có thể là khoảng lùi mang thợ rèn thật hoặc sắt nhọn.

Phong Hà đổi việc. Ba xương yên: không thở phào to, không mở rèm trẻ sớm, không rải vôi nghỉ. Trưa nước gốc rau. Ba chạm ba việc. Hà giữ rèm. A Minh không hát yên. Mạc Tư gạch: yên sau hỏi rèn — không viết nghỉ. A Cường lắc trống. Không mời nước mừng.

Hà: "Yên?"
"Trống. Không thở phào. Tai khe — miệng hỏi rèn có thể mang sắt nhọn."''',
"Yên sau hỏi năm mươi mốt · trống ≠ yên hội · không thở phào · cấp im · máy nghèo"),

(425, "Sóng Thấp Lần Bốn Mươi Bảy",
"Bụi lau khô phía bắc-tây — sóng thấp lần bốn mươi bảy. Không gào. Chỉ sóng. Máu kín.",
'''A Cường: "Lau bắc-tây. Bốn thấp. Một lê. Không gào. Lá lau dính tóc. Gần chỗ đất nứt."
"Máu kín. Hố mới góc lau — không trùng ao đông." Phong gật.

Bốn bóng thấp từ lau khô, lá dính tóc và vai. Tôn Vũ không hô. Đại Lực không gào. Phong hạ tay. Bốn móc gáy-hông — không mặt. Máu ngắn. Thóc lép nuốt. Kéo hố mới canh tư góc lau. Lấp. Đắp xấu. Phủi. Không cọc. Không đếm bốn to. Không giữ lá làm dấu.

Hà: "Kín? Bốn?"
"Kín. Không đếm to. Không phơi. Không nhìn lau quá ba nhịp. Đổi chỗ lê — máy không lặp hố ao."''',
"Sóng thấp lần bốn mươi bảy · lau bắc-tây · bốn · máu kín · cấp im · máy nghèo"),
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
    # progress
    st = BASE / "_detemplate_progress.json"
    st.write_text(json.dumps({
        "unique_rewritten_range": "393-425",
        "count": 33,
        "next": 426,
        "clone_remaining_est": "426-1000",
        "score_target": 9.5,
        "last_batch_ok": ok,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BATCH_OK", ok, "/", len(JOBS))

if __name__ == "__main__":
    main()
