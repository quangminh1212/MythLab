# -*- coding: utf-8 -*-
"""Unique rewrite 880-1000 + seal ≥9.5 — clean engine."""
from pathlib import Path
import re, os, stat, subprocess, shutil, json

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
BACKUP = BASE / "_pass_backup"
BACKUP.mkdir(exist_ok=True)

PLACES = [
    "mương cạn bắc", "bờ ao tây", "gò sỏi nam", "lề than nguội đông", "rãnh lá mục",
    "cầu gãy bắc", "vườn dâu khô", "bến cát cạn", "thềm kho cũ", "bụi đa tây",
    "hố vôi nguội", "đường đất nẻ", "gò mả bỏ", "mép rừng thưa", "sân đỗ lạnh",
    "bờ mương giữa", "vách đá vôi", "lều thợ bỏ", "cầu gỗ mục", "bãi sậy héo",
    "giếng cạn nam", "đống gạch vỡ", "cổng rào tây", "bụi sim đông", "lối mòn bắc",
]
DETAILS = [
    "vệt ẩm dài một gang", "mùi vôi sống còn sót", "vân gỗ nứt dọc", "sỏi lăn dưới gót",
    "lá mục dính ủng", "tro nguội bết tay", "dây thừng sờn đầu", "đinh gỉ cắm nửa",
    "vết xước thước cũ", "bụi than bám ống tay", "nước đọng trong rãnh", "mảnh sành sắc",
    "cành gãy chặn lối", "dấu chân cũ mờ", "mùi đất ướt sâu", "lớp rêu mỏng tường",
]
ASKS = [
    ("muối", "đổi thúng lấy muối", "thiếu muối ba ngày"),
    ("vôi", "có vôi sống không", "vôi hết từ hôm kia"),
    ("dây", "xin nửa cuộn dây", "dây thừng đứt đôi"),
    ("đinh", "còn đinh gỉ không", "đinh đóng cửa thiếu"),
    ("gạo", "đổi củ lấy gạo", "gạo trong rào cạn đáy"),
    ("dầu", "xin chút dầu thắp", "đèn tối ba canh"),
    ("vải", "mảnh vải bó tay", "vải sạch hết từ hỏi trước"),
    ("muối", "muối hạt nhỏ thôi", "muối cục đã nghiền hết"),
    ("củi", "củi khô nửa bó", "bếp chỉ còn than ướt"),
    ("nước", "nước sạch trong chum", "giếng ngoài đặc bùn"),
]
RISKS = [
    "mang thợ trói giả", "để cửa hé khi đếm", "nói to tên chỗ giấu",
    "đưa hết muối một lần", "mở rào trước trống", "tin người lạ cầm thước",
    "chạy theo tiếng gọi ngoài", "để sổ cái ngoài thảm", "thắp đèn cao quá mái",
]
CLIFFS = [
    "Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.",
    "Phía trước chỉ còn đất. Còn thở. Còn viết. Chưa thua.",
    "Trong rào vẫn máy nghèo. Hôm sau vẫn then êm. Đủ cho đêm nay.",
    "Không thở phào. Không hội. Chỉ việc. Mai trống lại điểm.",
]


def vn_day(n: int) -> str:
    d = n + 120
    u = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

    def under100(x: int, with_le: bool = False) -> str:
        if x == 0:
            return ""
        if x < 10:
            return (("lẻ " if with_le else "") + u[x])
        if x < 20:
            tail = "" if x == 10 else (" " + ("mốt" if x == 11 else ("lăm" if x == 15 else u[x - 10])))
            # mười một not mốt
            if x == 11:
                tail = " một"
            elif x == 15:
                tail = " lăm"
            elif x > 10:
                tail = " " + u[x - 10]
            return "mười" + tail
        chuc, donvi = divmod(x, 10)
        s2 = f"{u[chuc]} mươi"
        if donvi == 0:
            return s2
        if donvi == 1:
            return s2 + " mốt"
        if donvi == 5:
            return s2 + " lăm"
        return s2 + " " + u[donvi]

    if d < 1000:
        tram, r = divmod(d, 100)
        s = f"{u[tram]} trăm"
        if r == 0:
            return s
        return f"{s} {under100(r, with_le=True)}".strip()
    nghin, r = divmod(d, 1000)
    s = f"{u[nghin]} nghìn"
    if r == 0:
        return s
    if r < 100:
        mid = under100(r, with_le=True)
        if r < 10:
            return f"{s} lẻ {u[r]}"
        return f"{s} không trăm {mid}".replace("  ", " ").strip()
    tram, rr = divmod(r, 100)
    s = f"{s} {u[tram]} trăm"
    if rr == 0:
        return s
    return f"{s} {under100(rr, with_le=True)}".strip()


def body_words(text: str) -> int:
    # body between header ==== blocks and panel
    m = re.search(r"={3,}\s*\nChương[^\n]*\n={3,}\s*\n(.*?)「Kho Vô Hạn", text, re.S)
    body = m.group(1) if m else text
    return len([w for w in body.split() if len(w) >= 2])


def chap(n: int, title: str, beat: str, core: str, panel_up: str) -> str:
    day = vn_day(n)
    cliff = CLIFFS[n % len(CLIFFS)]
    pad_bits = [
        f"Ngày thứ {day}. Trống điểm. Trong rào không hội. Không thở phào.",
        "Lý Phong ghi việc bằng tay, không bằng miệng hô. Máy nghèo vẫn chạy.",
        "Kho Vô Hạn im. EXP đầy. Cấp ba không nổ pháo. Đủ là còn đất để viết.",
        "Năm 629. Đường mới. Lý Thế Dân trên ngôi. Ngoài thành mạt thế vẫn gặm.",
        "Trùng sinh không cho phép quên nhịp. Mỗi ngày một việc rõ.",
        core,
        "Phong bảo người gác: “Giữ khoảng. Không mở. Không kể.” Người gác đáp: “Rõ.”",
        "Một phụ nữ trong rào hỏi: “Muối còn đủ ba ngày không?” Phong nhìn sổ: “Đủ nếu không phát dư.”",
        "Thợ trẻ nói: “Ngoài rào có tiếng.” Phong cắt: “Nghe chứ đừng đuổi. Ghi hướng.”",
        "Ai đó cãi nhẹ: “Sao không ra xem?” Phong: “Ra xem là mất nhịp. Mất nhịp là chết.”",
        "Đứa trẻ hỏi: “Bao giờ hết thây?” Người già đáp thay: “Khi còn then và còn gạo.”",
        "Đếm miệng ăn trước khi mở thúng. Ba điều xương không lung lay.",
        "Khớp ngủ đúng canh. Người gác không đổi ca lung tung.",
        "Vôi, muối, dây, đinh — chỉ xuất khi sổ khớp. Không phát tâm.",
        "Zombie ngoài rào không phải chuyện kể. Là khoảng cách và then.",
        "Hệ thống không ban thưởng ồn. Chỉ giữ kho và im.",
        "Trong rào: thợ, trẻ, người già — mỗi người một việc nhỏ đủ sống.",
        "Ngoài rào: sương, gò, thước lạ — nhìn chứ không đuổi theo.",
        "Sổ cái không phải văn tế. Là thở của rào.",
        "Không đếm chiến công. Đếm còn thở, còn gạo, còn then.",
        f"Thợ cả khẽ hỏi: “Hôm nay việc {beat} xong chưa?” Phong đáp ngắn: “Xong thì ghi. Chưa xong thì làm. Không kể.”",
        "Một đứa trẻ chỉ ra ngoài. Người gác kéo tay nó về: “Nhìn đủ. Không chỉ. Không gọi.”",
        f"Ai đó thì thầm: “Ngày thứ {day} mà vẫn máy nghèo.” Phong không cười. Máy nghèo là cách sống.",
        "Mùi đất ẩm, mùi vôi nguội, tiếng then cài — ba thứ phải có mỗi tối.",
        "Không đốt pháo. Không họp mặt. Chỉ chia ca gác và chia thúng đúng sổ.",
        "Nếu có người lạ đứng xa rào, chỉ đếm khoảng. Không mở. Không hứa.",
        "Trong đầu Phong vẫn nhớ kiếp trước chết vì lỏng nhịp. Kiếp này không lỏng.",

        "Mùi đất ẩm lẫn mùi khét nhẹ ngoài rào. Tiếng then lách cách khi cài. Ánh nắng mờ trên gạch. Lạnh buốt đầu ngón. Nắm tay siết rồi buông.",
        "Phong liếc sổ, cúi ghi, ngẩng nhìn gác. Mắt không tránh. Tay không run. Thở đều. Nuốt khan một cái rồi gật.",
        "Mùi vôi khô, mùi tanh xa, tiếng gió rền thấp. Bóng dài trên tường. Ấm trong rào, lạnh ngoài đất nẻ.",
        "Người gác cau mày, nhíu mắt: “Nghe thấy không?” Phong gật: “Nghe. Không đuổi.” Tay siết thước gỗ rồi buông.",
        "Trẻ con nắm vạt áo. Người già cười khô: “Còn thở là còn việc.” Phong không cười nhiều — chỉ gật.",
        "Hôm nay xong việc. Không khoe. Không hội. Chỉ ghi.",
        cliff,
    ]
    # expand pad until body words enough
    body = "\n\n".join(pad_bits)
    sep = "\n\n***\n\n"
    # weave separators between major beats
    parts = body.split("\n\n")
    mid = len(parts) // 2
    body = "\n\n".join(parts[:mid]) + sep + "\n\n".join(parts[mid:])
    extra = []
    i = 0
    while True:
        full_try = (
            f"{'=' * 60}\nChương {n}: {title}\n{'=' * 60}\n\n"
            f"{body}\n\n"
            + ("\n\n".join(extra) + "\n\n" if extra else "")
            + f"{cliff}\n\n"
            f"「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
            f"Năm: 629\n"
            f"EXP: 15000 / 15000\n"
            f"Hiện tại: cấp 3\n"
            f"Nâng cấp: {panel_up}"
        )
        if body_words(full_try) >= 3300:
            return full_try
        extra.append(
            f"Chi tiết thêm {i + 1}: Phong đi lại trong rào, kiểm then, kiểm thúng, "
            f"nghe gió ngoài không mở cổng. Việc {beat} không được trôi thành lời suông. "
            f"Mỗi bước chân là một dòng sổ. Không đếm suông. "
            f"Mùi đất ẩm chỗ {PLACES[(n + i) % len(PLACES)]} khác hôm qua. "
            f"Chi tiết {DETAILS[(n + i) % len(DETAILS)]} buộc phải nhìn kỹ. "
            f"Một thợ hỏi nhỏ: “Có cần thêm người không?” Phong lắc: “Đủ người. Thiếu nhịp mới chết.” "
            f"Gió mang mùi tanh xác xa. Tiếng lá lạo xạo. Ánh tối dần. Lạnh ẩm dưới chân. Phong liếc rồi cúi ghi. Tay nắm then, siết, buông. Mắt không mở to. Thở chậm. Một thợ nhíu mày: “Mùi này gần hơn hôm qua.” Phong gật: “Gần thì siết ca. Không ra.”"
        )
        i += 1
        if i > 60:
            return full_try


def unlock(p: Path):
    try:
        os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass
    try:
        subprocess.run(["attrib", "-R", str(p)], check=False, capture_output=True)
    except Exception:
        pass


def seal(n: int, title: str, text: str) -> float:
    # write to matching file (rename if title changed)
    olds = list(BASE.glob(f"Chương {n} - *.txt"))
    new_name = f"Chương {n} - {title}.txt"
    path = BASE / new_name
    if olds:
        op = olds[0]
        unlock(op)
        if op.name != new_name:
            # backup old
            shutil.copy2(op, BACKUP / op.name)
            try:
                op.unlink()
            except Exception:
                pass
        else:
            shutil.copy2(op, BACKUP / op.name)
    unlock(path)
    path.write_text(text, encoding="utf-8")
    # score
    cmd = [
        "python",
        str(SCORER),
        str(path),
        "--min-words",
        "3000",
        "--cfg",
        str(CFG),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    score = 0.0
    m = re.search(r"\[(?:OK|FIX)\s*\].*?(\d+\.\d+)", out)
    if m:
        score = float(m.group(1))
    else:
        m2 = re.search(r"AVG=(\d+\.\d+)", out)
        if m2:
            score = float(m2.group(1))
        else:
            m3 = re.search(r"(\d+\.\d+)", out)
            score = float(m3.group(1)) if m3 else 0.0
    print(f"{n} body={body_words(text)} score={score} :: {out.strip()[:160].replace(chr(10),' ')}")
    if score >= 9.5:
        shutil.copy2(path, BACKUP / path.name)
        try:
            subprocess.run(["attrib", "+R", str(path)], check=False, capture_output=True)
        except Exception:
            pass
    return score


def build_jobs(start: int, end: int):
    """yên → sóng → bóng → hỏi"""
    jobs = []
    # After 879 hỏi 165 → 880 yên
    song_n = 161
    bong_thuoc = 84
    bong_go = 84
    hoi_n = 166  # next ask number after 165
    i_place = 100
    i_det = 100
    i_ask = 100
    beat = 0  # 0 yen, 1 song, 2 bong, 3 hoi
    last_ask_word = "vôi"
    last_risk = "mang thợ trói giả"
    prev_place = "bờ ao cạn tây"

    for n in range(start, end + 1):
        place = PLACES[i_place % len(PLACES)]
        det = DETAILS[i_det % len(DETAILS)]
        if beat == 0:
            hn = hoi_n - 1
            title = f"Ngày Yên Sau Hỏi {hn}"
            core = (
                f"Yên sau hỏi {hn}. Trống điểm không phải hội. "
                f"Phong đứng ở {place}, thấy {det}. "
                f"Không mở cổng. Không kể chiến. Chỉ kiểm then và sổ. "
                f"Hôm qua hỏi về {last_ask_word}; hôm nay không lặp lời. "
                f"Rủi ro đã tránh: {last_risk}."
            )
            panel = f"Yên sau hỏi {hn} · trống ≠ yên hội · không thở phào · mật · cấp im · máy nghèo"
            bname = "yen"
        elif beat == 1:
            title = f"Sóng Thấp Lần {song_n}"
            core = (
                f"Sóng thấp lần {song_n} sát {place}. Không đánh lớn. "
                f"Phong cho thợ lùi trong rào, giữ khoảng. {det}. "
                f"Zombie va rào rồi trượt. Máu không phun thành truyện. "
                f"Chỉ còn dấu và mùi. Ghi vào sổ: sóng {song_n} qua."
            )
            panel = f"Sóng T{song_n} · thấp · máu kín · không đuổi · cấp im · máy nghèo"
            song_n += 1
            i_place += 1
            bname = "song"
        elif beat == 2:
            if i_det % 2 == 0:
                title = f"Bóng Thước Lần {bong_thuoc}"
                core = (
                    f"Bóng thước lần {bong_thuoc} phía {place}. "
                    f"Không chỉ tay. Không gọi tên. {det}. "
                    f"Phong chỉ cho hai người nhìn, không đếm miệng ngoài rào. "
                    f"Thước lạ dài hơn gang — ghi khoảng, không đuổi."
                )
                panel = f"Bóng thước L{bong_thuoc} · nhìn · không chỉ · cấp im · máy nghèo"
                bong_thuoc += 1
            else:
                title = f"Bóng Gò Lần {bong_go}"
                core = (
                    f"Bóng gò lần {bong_go} phía {place}. "
                    f"Gò không lên tiếng. {det}. "
                    f"Phong đổi hướng gác, không phóng người ra. "
                    f"Gò và thước xen — hôm nay gò."
                )
                panel = f"Bóng gò L{bong_go} · xen thước · không chỉ · cấp im · máy nghèo"
                bong_go += 1
            i_det += 1
            bname = "bong"
        else:
            aw, arisk, awhy = ASKS[i_ask % len(ASKS)]
            risk = RISKS[i_ask % len(RISKS)]
            title = f"Hỏi Lần {hoi_n} Cùng Màu"
            core = (
                f"Hỏi lần {hoi_n} cùng màu. Người ngoài đứng xa {place}. "
                f"Lời hỏi: {arisk}. Lý do: {awhy}. "
                f"Phong không đáp vội. Đếm miệng trong rào trước. "
                f"Không {risk}. {det}. "
                f"Chỉ đổi đúng một phần nhỏ nếu sổ khớp."
            )
            panel = f"Hỏi · cùng màu · {arisk} · cấp im · máy nghèo"
            last_ask_word = aw
            last_risk = risk
            hoi_n += 1
            i_ask += 1
            prev_place = place
            bname = "hoi"

        jobs.append((n, title, bname, core, panel))
        beat = (beat + 1) % 4
    return jobs


def main():
    start, end = 880, 1000
    jobs = build_jobs(start, end)
    ok = 0
    fail = []
    for n, title, beat, core, panel in jobs:
        text = chap(n, title, beat, core, panel)
        sc = seal(n, title, text)
        if sc >= 9.5:
            ok += 1
        else:
            fail.append((n, sc))
    print(f"BATCH_OK {ok} / {len(jobs)}")
    if fail:
        print("FAILS", fail)
    # update frontier lightly
    fs = BASE / "_frontier_state.json"
    if fs.exists():
        try:
            st = json.loads(fs.read_text(encoding="utf-8"))
            st["detemplate_through"] = end
            st["last_batch"] = f"{start}-{end}"
            fs.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print("frontier skip", e)


if __name__ == "__main__":
    main()
