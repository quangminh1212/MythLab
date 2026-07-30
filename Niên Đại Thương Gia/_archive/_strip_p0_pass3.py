# -*- coding: utf-8 -*-
"""P0 pass3: hard-cut tail romance; sanitize single clean panel; remove post-panel."""
from __future__ import annotations
import re
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:/Dev/XLab_MTC/Niên Đại Thương Gia")

TAIL_STARTS = [
    r"Hai ly nước ấm",
    r"Bên ly rượu nếp",
    r"trộm ổi",
    r"xoa tay vợ",
    r"ôm vợ",
    r"nhìn vợ",
    r"hôn lên trán vợ",
    r"hôn trán",
    r"mắt nhìn vào mắt vợ",
    r"tay vợ",
    r"kéo Lan đứng lên",
    r"Hùng dắt Lan lên phòng",
    r"Ngủ ngon\.' Hùng thì thầm",
    r"Hạnh phúc\.",
    r"Anh yêu em\.",
    r"anh yeu em",
    r"mat long lanh",
    r"Lan nhin Hung",
    r"\{a\}",
    r"\{b\}",
    r"Tình yêu trong những điều nhỏ bé",
    r"Minh đang tưới cây",
    r"Đêm khuya, hai người nằm",
    r"Sáng chủ nhật, Hùng gấp chăn",
    r"Buổi trưa, Hùng nằm võng",
    r"Ngoài vườn, hoa hồng",
    r"Mưa rơi trên mái ngói",
    r"Bên ngoài, mưa rơi",
    r"'Chị Hoa ơi, thịt kho",
    r"'Anh nhìn kìa, con chim",
    r"Lan nhin Hung, mat am ap",
    r"Hùng nhìn lên trần nhà, mắt mở to",
    r"Cảm ơn vì đã ở bên anh",
]


def vi_words(t: str) -> int:
    return len([w for w in t.split() if len(w) >= 2])


def extract_clean_panel(text: str, ch_num: int) -> str | None:
    """Return cleaned single panel block or None."""
    m = re.search(r"「Hệ thống[^\n]*」", text)
    if not m:
        return None
    start = m.start()
    chunk = text[start:]
    # take lines until we hit a line that looks like restarted story OR second panel OR too many seps
    lines = chunk.splitlines()
    keep = [lines[0]]  # header
    for ln in lines[1:]:
        if re.match(r"^={10,}\s*$", ln):
            break
        if ln.startswith("「Hệ thống"):
            break
        # restarted narrative (common spill)
        if re.match(r"^(Cửa khẩu|Qua biên giới|Mang theo ba cuộn|Đường sang Lào)", ln):
            break
        if re.match(r"^(Hùng đứng|Hùng ngồi|Sáng |Chiều |Tối |Một |Lan |Bà )", ln) and len(keep) > 8:
            # likely spill if already have year/exp
            if any("Năm:" in x or "EXP" in x for x in keep):
                break
        keep.append(ln)
        if len(keep) > 25:
            break
    # clean skill dump
    out = []
    for ln in keep:
        if ln.startswith("Kỹ năng hiện có:"):
            out.append("Kỹ năng trọng yếu: (xem ledger)")
            continue
        if "không còn cảnh gặt tay" in ln:
            continue
        if "mỗi tỉnh hai chiếc" in ln:
            continue
        out.append(ln)
    body = "\n".join(out).strip()
    if "GHI NHẬN" not in body and "CỘT MỐC" not in body:
        # force label
        body = body.replace("「Hệ thống", "「Hệ thống — GHI NHẬN", 1)
    return body


def cut_tail_before_panel(text: str) -> tuple[str, int]:
    panel_i = text.find("「Hệ thống")
    if panel_i < 0:
        region = text
        panel_part = ""
    else:
        region = text[:panel_i]
        panel_part = text[panel_i:]

    cut_at = None
    for pat in TAIL_STARTS:
        for m in re.finditer(pat, region, flags=re.I):
            # only late in chapter
            if m.start() >= int(len(region) * 0.45):
                if cut_at is None or m.start() < cut_at:
                    cut_at = m.start()
    n = 0
    if cut_at is not None:
        # snap back to paragraph start
        para = region.rfind("\n\n", 0, cut_at)
        if para > int(len(region) * 0.4):
            cut_at = para
        region = region[:cut_at].rstrip() + "\n\n"
        n = 1
    return region + panel_part, n


def rebuild(text: str, ch_num: int) -> tuple[str, Counter]:
    st = Counter()
    t = text.replace("\r\n", "\n")
    t, n = cut_tail_before_panel(t)
    st["tail_cut"] = n
    panel = extract_clean_panel(t, ch_num)
    if panel:
        # body = everything before first panel marker
        idx = t.find("「Hệ thống")
        body = t[:idx].rstrip() if idx >= 0 else t.rstrip()
        body = re.sub(r"(?:\n={10,}\s*)+$", "", body).rstrip()
        # also remove empty Teaser:
        body = re.sub(r"(?m)^Teaser:\s*$", "", body)
        body = re.sub(r"\n{3,}", "\n\n", body).rstrip()
        t = (
            body
            + "\n\n============================================================\n"
            + panel
            + "\n============================================================\n"
        )
        st["panel_rebuild"] = 1
    t = re.sub(r"\n{3,}", "\n\n", t)
    if not t.endswith("\n"):
        t += "\n"
    st["words"] = vi_words(t)
    return t, st


def main():
    files = sorted(
        ROOT.glob("Chương *.txt"),
        key=lambda f: int(re.search(r"(\d+)", f.name).group(1)),
    )
    changed = 0
    tot = Counter()
    short = []
    vo_left = []
    for f in files:
        num = int(re.search(r"(\d+)", f.name).group(1))
        raw = f.read_text(encoding="utf-8", errors="replace")
        new, st = rebuild(raw, num)
        tot.update({k: v for k, v in st.items() if k != "words"})
        if new != raw:
            f.write_text(new, encoding="utf-8")
            changed += 1
        if st["words"] < 3000:
            short.append((num, st["words"]))
        # check wife near end
        if re.search(r"(?s).{0,800}(xoa tay vợ|ôm vợ|nhìn vợ|hôn.*vợ).{0,200}「Hệ thống", new):
            vo_left.append(num)
    print("CHANGED", changed)
    print("STATS", dict(tot))
    print("SHORT", short, "n", len(short))
    print("VO_LEFT", vo_left[:40], "n", len(vo_left))
    # ch27 check
    t = (ROOT / "Chương 27 - Đi Lào.txt").read_text(encoding="utf-8")
    print("ch27 words", vi_words(t))
    print("ch27 has vợ", "vợ" in t[-2000:])
    print("ch27 tail:\n", t[-900:])


if __name__ == "__main__":
    main()
