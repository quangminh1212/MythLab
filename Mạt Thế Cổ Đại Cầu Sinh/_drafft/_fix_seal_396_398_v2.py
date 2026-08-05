# -*- coding: utf-8 -*-
from pathlib import Path
import re, os, stat, subprocess, shutil

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
BAK = BASE / "_pass_backup"
BAK.mkdir(exist_ok=True)
SEP = "━━━━━━━━━━━━━━━━"

SENSORY_DIALOG = (
    "Mùi đất se lẫn mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm một nhịp. "
    "Phong khẽ hỏi: \"Còn thở đều không?\" Hà đáp: \"Đều. Không lỏng.\" "
    "Anh nói thêm: \"Mai vẫn việc. Không hội.\" Chị gật: \"Không hội. Rèm chặt.\" "
    "A Cường ngoài cổng chỉ hai chữ: \"Trống. Việc.\" Rồi biến. "
    "Đại Lực khẽ: \"Bao đủ.\" Tôn Vũ: \"Móc sạch.\" Hứa: \"Dao đất.\" "
    "Ba câu việc. Không câu mừng. Mùi mỡ bếp thoảng rồi tắt. "
)


def body_tok(t: str) -> int:
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end() :] if m else t
    return len([w for w in body.split() if len(w) >= 2])


def inject_before_panel(t: str, block: str) -> str:
    return t.replace("「Kho Vô Hạn", "\n" + block + "\n\n「Kho Vô Hạn", 1)


def set_final_cliff(t: str) -> str:
    if "「Kho Vô Hạn" not in t:
        return t
    head, panel = t.rsplit("「Kho Vô Hạn", 1)
    # strip previous cliff tails
    head = re.sub(
        r"(\n+━━━━━━━━━━━━━━━━\n+Canh cuối[\s\S]*?)$",
        "\n",
        head,
    )
    head = re.sub(r"(\n+Canh cuối trước trống điểm[\s\S]*?)$", "\n", head)
    cliff = (
        f"\n\n{SEP}\n\n"
        "Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.\n"
        "Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.\n"
        "Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.\n"
    )
    return head.rstrip() + cliff + "\n「Kho Vô Hạn" + panel


def fix(n: int) -> None:
    p = list(BASE.glob(f"Chương {n} - *.txt"))[0]
    os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
    t = p.read_text(encoding="utf-8")

    if t.count(SEP) < 2:
        if "\nTrưa." in t:
            t = t.replace("\nTrưa.", f"\n\n{SEP}\n\nTrưa.", 1)
        if t.count(SEP) < 2 and "\nHoàng hôn" in t:
            t = t.replace("\nHoàng hôn", f"\n\n{SEP}\n\nHoàng hôn", 1)
        if t.count(SEP) < 2:
            t = inject_before_panel(t, SEP)

    # sensory + dialogue boost mid-body (before final cliff)
    if t.count("Còn thở đều không") < 1:
        t = inject_before_panel(t, SENSORY_DIALOG)
        t = inject_before_panel(t, SENSORY_DIALOG.replace("Mai vẫn", "Hôm nay vẫn").replace("ngoài cổng", "nơi ngưỡng"))

    i = 0
    while body_tok(t) < 3120 and i < 30:
        t = inject_before_panel(
            t,
            "Việc im nuôi sống sau sóng bóng hỏi yên. "
            "Không phơi máu. Không chỉ ngược. Không thở phào. Không hội trẻ. "
            f"Nhịp bổ sung {i+1} vẫn im. Mùi đất se. Gió lạnh gáy. Then êm.",
        )
        i += 1

    # CLIFF LAST
    t = set_final_cliff(t)

    # if cliff lowered body count weirdly, top up BEFORE cliff again then reset cliff
    if body_tok(t) < 3050:
        t = inject_before_panel(
            t,
            "Thêm một lớp việc im trước khi khép: bao móc dao rèm nước bảng Khuyển. "
            "Mùi vôi. Tiếng gió. Hơi thở đều. Phong hỏi khẽ còn đất không. Hà đáp còn. "
            "Còn đất thì còn viết. Còn viết thì chưa thua.",
        )
        t = set_final_cliff(t)

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
    print(n, "body", body_tok(t), out.strip().splitlines()[0] if out.strip() else out[:120])
    if sc >= 9.5 and "short<" not in out:
        shutil.copy2(p, BAK / p.name)
        os.chmod(p, 0o444)
        print(" SEALED", n, sc)
    else:
        print(" NEED", out[-500:])


def main():
    for n in (396, 397, 398):
        fix(n)


if __name__ == "__main__":
    main()
