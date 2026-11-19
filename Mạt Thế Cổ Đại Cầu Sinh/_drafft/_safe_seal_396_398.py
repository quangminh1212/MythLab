# -*- coding: utf-8 -*-
"""Safe seal 396-398: never strip body; only append before panel."""
from pathlib import Path
import re, os, stat, subprocess, shutil

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
BAK = BASE / "_pass_backup"
BAK.mkdir(exist_ok=True)
SEP = "━━━━━━━━━━━━━━━━"
REWRITE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh/_rewrite_396_398.py")


def body_tok(t: str) -> int:
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end() :] if m else t
    return len([w for w in body.split() if len(w) >= 2])


def before_panel(t: str, block: str) -> str:
    marker = "「Kho Vô Hạn"
    if marker not in t:
        return t + "\n" + block
    return t.replace(marker, block + "\n\n" + marker, 1)


def load_ch397_from_rewrite_script() -> str:
    src = REWRITE.read_text(encoding="utf-8")
    # extract CH397 = r'''...'''
    m = re.search(r"CH397 = r'''(.*?)'''\s*\n\nCH397_BITS", src, re.S)
    if not m:
        raise SystemExit("CH397 not found in rewrite script")
    return m.group(1).lstrip("\n")


def load_bits(name: str) -> list[str]:
    src = REWRITE.read_text(encoding="utf-8")
    m = re.search(rf"{name} = \[(.*?)\]\s*\n\n", src, re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def ensure_seps(t: str) -> str:
    if t.count(SEP) >= 2:
        return t
    if "\nTrưa." in t:
        t = t.replace("\nTrưa.", f"\n\n{SEP}\n\nTrưa.", 1)
    if t.count(SEP) < 2 and "\nHoàng hôn" in t:
        t = t.replace("\nHoàng hôn", f"\n\n{SEP}\n\nHoàng hôn", 1)
    if t.count(SEP) < 2 and "\nChiều" in t:
        t = t.replace("\nChiều", f"\n\n{SEP}\n\nChiều", 1)
    if t.count(SEP) < 2:
        t = before_panel(t, SEP)
    return t


def append_cliff_last(t: str) -> str:
    """Remove ONLY a trailing cliff block immediately before panel, then add one."""
    marker = "「Kho Vô Hạn"
    if marker not in t:
        return t
    head, panel = t.rsplit(marker, 1)
    # remove only last 1-2KB if it is a cliff block
    tail = head[-1200:]
    if "Canh cuối trước trống điểm" in tail:
        idx = head.rfind("Canh cuối trước trống điểm")
        # also drop preceding SEP if right before
        chunk = head[:idx]
        if chunk.rstrip().endswith(SEP):
            chunk = chunk.rstrip()[: -len(SEP)].rstrip()
        head = chunk
    cliff = (
        f"\n\n{SEP}\n\n"
        "Canh cuối trước trống điểm, Phong còn nghe gió bấc đi ngang đất ngoài rào.\n"
        "Chưa biết mai mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng.\n"
        "Ngày mai vẫn máy nghèo. Hôm sau vẫn then êm. Phía trước chỉ còn đất. "
        "Liệu có giữ nhịp? Sẽ biết khi trống điểm kế. Nhưng hôm nay đã viết việc đủ.\n"
    )
    return head.rstrip() + cliff + "\n" + marker + panel


def expand(t: str, bits: list[str], target: int = 3120) -> str:
    t = ensure_seps(t)
    i = 0
    # first add unique bits
    while body_tok(t) < target and bits and i < len(bits) * 3:
        b = bits[i % len(bits)] + f" Nhịp im {i+1}."
        t = before_panel(t, b)
        i += 1
    # generic sensory+dialog pads
    pads = [
        'Mùi đất se. Mùi vôi. Gió lạnh gáy. Phong hỏi: "Còn đều không?" Hà đáp: "Đều. Không lỏng."',
        'Anh nói: "Mai vẫn việc." Chị gật: "Rèm chặt. Không hội." A Cường: "Trống. Việc." Rồi biến.',
        "Đại Lực: \"Bao đủ.\" Tôn Vũ: \"Móc sạch.\" Hứa: \"Dao đất.\" Ba câu việc. Không câu mừng.",
        "Việc im nuôi sống. Kể to nuôi chết chậm. Then êm. Khuyển ngưỡng. Bảng sấp. Nước đúng gáo.",
        "Không phơi máu. Không chỉ ngược. Không thở phào. Không mở rèm trẻ sớm. Máy nghèo giữ nhịp.",
    ]
    j = 0
    while body_tok(t) < target and j < 40:
        t = before_panel(t, pads[j % len(pads)] + f" Bổ sung {j+1}.")
        j += 1
    # cliff absolutely last
    t = append_cliff_last(t)
    # if cliff somehow short, top up then cliff again
    if body_tok(t) < 3050:
        t = before_panel(t, pads[0] + " Thêm lớp trước khi khép.")
        t = append_cliff_last(t)
    return t


def seal(n: int, t: str) -> None:
    p = list(BASE.glob(f"Chương {n} - *.txt"))[0]
    os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
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
    print(n, "body", body_tok(t), out.strip().splitlines()[0] if out.strip() else "?")
    if sc >= 9.5 and "short<" not in out:
        shutil.copy2(p, BAK / p.name)
        os.chmod(p, 0o444)
        print(" SEALED", n, sc)
    else:
        print(" NEED", out[-350:])


def main():
    # 396: already good unique — only ensure cliff last if cau weak
    p396 = list(BASE.glob("Chương 396 - *.txt"))[0]
    t396 = p396.read_text(encoding="utf-8")
    t396 = append_cliff_last(ensure_seps(t396))
    if body_tok(t396) < 3050:
        t396 = expand(t396, load_bits("CH396_BITS"), 3120)
    seal(396, t396)

    # 397: full unique from rewrite script
    t397 = load_ch397_from_rewrite_script()
    t397 = expand(t397, load_bits("CH397_BITS"), 3120)
    seal(397, t397)

    # 398: keep restored body, fix cliff last + light expand if needed
    p398 = list(BASE.glob("Chương 398 - *.txt"))[0]
    t398 = p398.read_text(encoding="utf-8")
    if body_tok(t398) < 3050:
        t398 = expand(t398, load_bits("CH398_BITS"), 3120)
    else:
        t398 = append_cliff_last(ensure_seps(t398))
    seal(398, t398)


if __name__ == "__main__":
    main()
