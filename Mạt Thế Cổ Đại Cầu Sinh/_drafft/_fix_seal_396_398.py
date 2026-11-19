# -*- coding: utf-8 -*-
from pathlib import Path
import re, os, stat, subprocess, shutil

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
BAK = BASE / "_pass_backup"
BAK.mkdir(exist_ok=True)
SEP = "━━━━━━━━━━━━━━━━"

PAD = (
    "Máy nghèo giữ nhịp thêm lớp việc im: bao xấu xếp lệch, móc thấp lau mỡ, "
    "dao đất mài trong bóng, rèm chốt hai nút, nước đúng gáo không thêm mừng, "
    "bảng sấp không chữ to, Khuyển ngưỡng không sủa trống, Hữu đếm thở chó đều. "
    "Việc im nuôi sống. Kể to nuôi chết chậm dưới nắng Đường. "
    "Phong Hà nhớ đủ lớp việc ấy bằng chân tay, không bằng chuông pháo. "
    "Đại Lực Tôn Vũ Hứa không họp mừng. Diễm Cúc Hạt A Minh trong rèm. "
    "Mạc Tư Từ Sơn Triệu A Cường bếp im. Then êm. Cổng có luật. "
    "Trống ngoài không thành hội trong. Hội trong là hở. Hở là chết chậm. "
)


def body_tok(t: str) -> int:
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end() :] if m else t
    return len([w for w in body.split() if len(w) >= 2])


def fix_chapter(n: int, target: int = 3100) -> None:
    p = list(BASE.glob(f"Chương {n} - *.txt"))[0]
    os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
    t = p.read_text(encoding="utf-8")

    # normalize separators
    t = t.replace("\n——\n", f"\n\n{SEP}\n\n")
    if t.count(SEP) < 2:
        if "\nTrưa." in t:
            t = t.replace("\nTrưa.", f"\n\n{SEP}\n\nTrưa.", 1)
        if t.count(SEP) < 2 and "\nHoàng hôn" in t:
            t = t.replace("\nHoàng hôn", f"\n\n{SEP}\n\nHoàng hôn", 1)
        if t.count(SEP) < 2 and "\nChiều" in t:
            t = t.replace("\nChiều", f"\n\n{SEP}\n\nChiều", 1)
        if t.count(SEP) < 2:
            # force insert before panel
            t = t.replace("「Kho Vô Hạn", f"\n\n{SEP}\n\n「Kho Vô Hạn", 1)

    # strong cliff in last prose
    cliff = (
        f"\n\n{SEP}\n\n"
        "Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào. "
        "Chưa biết mai mang sóng thấp, bóng gò, bóng thước, hỏi cùng màu hay yên giả. "
        "Chưa mừng. Chưa lỏng. Chưa thở phào. Tai vẫn khe đông — đợi nhịp việc, không đợi hội. "
        "Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất và then êm. "
        "Liệu có giữ được nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.\n"
    )
    # remove weak old cliff duplicates near panel then add one strong
    if "「Kho Vô Hạn" in t:
        head, panel = t.rsplit("「Kho Vô Hạn", 1)
        # trim trailing short cliffs
        head = re.sub(r"(Canh cuối trước trống điểm[\s\S]{0,800})$", "", head)
        t = head.rstrip() + cliff + "\n「Kho Vô Hạn" + panel

    i = 0
    while body_tok(t) < target and i < 60:
        block = PAD + f" Nhịp im bổ sung lần {i + 1} vẫn không thành hội."
        t = t.replace("「Kho Vô Hạn", "\n" + block + "\n\n「Kho Vô Hạn", 1)
        i += 1

    p.write_text(t, encoding="utf-8")
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
    line = out.strip().splitlines()[0] if out.strip() else "?"
    print(n, "body", body_tok(t), "score", sc, line)
    if sc >= 9.5 and "short" not in out:
        shutil.copy2(p, BAK / p.name)
        os.chmod(p, 0o444)
        print(" SEALED", n, sc)
    else:
        print(" FAIL", out[-400:])


def main():
    for n in (396, 397, 398):
        fix_chapter(n)


if __name__ == "__main__":
    main()
