# -*- coding: utf-8 -*-
"""P0 strip pass 2 — residual romance variants, post-panel spill, skill dumps."""
from __future__ import annotations
import re
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")

# Additional romance starts (Lan=vợ bedroom etc.)
ROM2 = re.compile(
    r"(?m)^(?:"
    r".*xoa tay vợ.*"
    r"|.*=vợ.*"
    r"|.*tay vợ.*"
    r"|Hùng dắt Lan lên phòng"
    r"|anh nằm cạnh\. Anh ôm cô"
    r"|'Nịnh\.' Lan cười"
    r"|Hai người ngồi bên nhau, tay trong tay"
    r"|Hùng thì thầm\. 'Ngủ ngon\.'"
    r"|Đừng lo\.' Lan nói, tay vuốt nhẹ tay Hùng"
    r")"
)

# Broader: cut from bedroom/romance cluster near end
ROM_CLUSTER = re.compile(
    r"(?ms)(?:\nBên ngoài, mưa rơi\..*?Hạnh phúc\.\s*)"
    r"|(?:\nRồi Hùng đứng dậy, kéo Lan đứng lên\..*?Hạnh phúc\.\s*)"
    r"|(?:\n'Sáng mai em nấu cháo gì\?'.*?Hạnh phúc\.\s*)"
)

SPAM2 = re.compile(
    r"(?m)^(?:"
    r"Đì đùng máy nổ xa mờ cuối làng\."
    r"|Xăng pha dầu nhờn từ xưởng sửa xe\."
    r"|Tê nhức ngón tay sau giờ viết sổ liên tục\."
    r"|Cây thước gỗ dấu đỏ kiểm định của ty thương nghiệp\."
    r").*\n?"
)

def vi_words(t):
    return len([w for w in t.split() if len(w) >= 2])

def keep_last_panel_only(text: str) -> str:
    # find all panels
    parts = list(re.finditer(r"「Hệ thống[\s\S]*?============================================================\s*", text))
    if not parts:
        # try without trailing sep
        panels = list(re.finditer(r"「Hệ thống[\s\S]*?(?=\n「Hệ thống|\Z)", text))
        if len(panels) <= 1:
            return text
        body = text[: panels[0].start()]
        # remove all panels
        for p in panels:
            body = body  # rebuild
        body = re.sub(r"「Hệ thống[\s\S]*", "", text)
        last = panels[-1].group(0)
        # clean skill dump
        last = re.sub(r"(?m)^Kỹ năng hiện có:.*\n?", "Kỹ năng trọng yếu: (xem ledger)\n", last)
        body = body.rstrip()
        body = re.sub(r"(?:\n={10,}\s*)+$", "", body).rstrip()
        return body + "\n\n============================================================\n" + last.strip() + "\n============================================================\n"

    # Simpler approach: split at first panel marker
    idx = text.find("「Hệ thống")
    if idx < 0:
        return text
    body = text[:idx]
    rest = text[idx:]
    # get last panel block
    all_p = list(re.finditer(r"「Hệ thống[\s\S]*?(?=\n「Hệ thống|\Z)", rest))
    if not all_p:
        return text
    last = all_p[-1].group(0).strip()
    last = re.sub(r"(?m)^Kỹ năng hiện có:.*$", "Kỹ năng trọng yếu: (xem ledger)", last)
    # strip overclaim line
    last = re.sub(r"(?m)^.*không còn cảnh gặt tay.*\n?", "", last)
    last = re.sub(r"(?m)^.*mỗi tỉnh hai chiếc.*\n?", "", last)
    body = body.rstrip()
    body = re.sub(r"(?:\n={10,}\s*)+$", "", body).rstrip()
    # remove post-panel prose that was after last panel in original - already discarded by taking last panel only from rest
    # But rest may have prose BETWEEN panels and AFTER last - strip after last in rest
    return (
        body
        + "\n\n============================================================\n"
        + last
        + "\n============================================================\n"
    )


def strip_romance_tail(text: str) -> tuple[str, int]:
    n = 0
    t2, c = ROM_CLUSTER.subn("\n", text)
    n += c
    text = t2
    # cut from cluster markers in last 40%
    m = None
    for pat in [
        r"(?m)^Bên ngoài, mưa rơi\.",
        r"(?m)^Rồi Hùng đứng dậy, kéo Lan đứng lên",
        r"(?m)^'Sáng mai em nấu cháo gì\?'",
        r"(?m)^Hùng dắt Lan lên phòng",
        r"(?m)^Hai người ngồi bên nhau, tay trong tay",
        r"(?m)^.*xoa tay vợ",
        r"(?m)^.*nhìn vợ,",
        r"(?m)^.*ôm vợ",
        r"(?m)^.*hôn trán",
        r"(?m)^.*mắt nhìn vào mắt vợ",
    ]:
        for mm in re.finditer(pat, text):
            if mm.start() > len(text) * 0.5:
                m = mm
                break
        if m:
            break
    if m:
        panel = text.find("「Hệ thống", m.start())
        if panel > m.start():
            text = text[: m.start()].rstrip() + "\n\n" + text[panel:]
            n += 1
        elif panel == -1 and m.start() > len(text) * 0.7:
            text = text[: m.start()].rstrip() + "\n"
            n += 1
    return text, n


def strip_post_panel_prose(text: str) -> tuple[str, int]:
    """Remove prose after the final panel block."""
    # Find last panel start
    starts = [m.start() for m in re.finditer(r"「Hệ thống", text)]
    if not starts:
        return text, 0
    start = starts[-1]
    # panel ends at closing ===== or end
    m = re.search(
        r"「Hệ thống[\s\S]*?(?:\n={10,}\s*\n?|$)",
        text[start:],
    )
    if not m:
        return text, 0
    end = start + m.end()
    after = text[end:]
    if re.search(r"[A-Za-zÀ-ỹ]{15,}", after):
        return text[:end].rstrip() + "\n", 1
    return text, 0


def process(text: str) -> tuple[str, Counter]:
    st = Counter()
    t = text.replace("\r\n", "\n")
    t, n = strip_romance_tail(t)
    st["rom2"] = n
    t = keep_last_panel_only(t)
    t, n = strip_post_panel_prose(t)
    st["post"] = n
    t2, n = SPAM2.subn("", t)
    st["spam2"] = n
    t = re.sub(r"\n{3,}", "\n\n", t2)
    if not t.endswith("\n"):
        t += "\n"
    st["words"] = vi_words(t)
    return t, st


def main():
    files = sorted(ROOT.glob("Chương *.txt"), key=lambda f: int(re.search(r"(\d+)", f.name).group(1)))
    changed = 0
    tot = Counter()
    short = []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="replace")
        new, st = process(raw)
        tot.update({k: v for k, v in st.items() if k != "words"})
        if new != raw:
            f.write_text(new, encoding="utf-8")
            changed += 1
        if st["words"] < 2800:
            short.append((f.name, st["words"]))
    print("CHANGED", changed)
    print("STATS", dict(tot))
    print("SHORT", short[:20], "n", len(short))
    # residual checks
    resid = Counter()
    for f in files:
        t = f.read_text(encoding="utf-8", errors="replace")
        for lab, pat in [
            ("vo_word_tail", r"vợ"),
            ("a_ph", r"\{a\}"),
            ("nuoc", r"Hai ly nước ấm"),
            ("oi", r"trộm ổi"),
            ("multi_ghi", None),
        ]:
            if lab == "multi_ghi":
                if t.count("GHI NHẬN") > 1:
                    resid[lab] += 1
            elif re.search(pat, t):
                # vợ only count if near end with Lan
                if lab == "vo_word_tail":
                    if re.search(r"(?s).{0,400}vợ.{0,200}「Hệ thống", t) or re.search(
                        r"xoa tay vợ|ôm vợ|nhìn vợ", t
                    ):
                        resid[lab] += 1
                else:
                    resid[lab] += 1
    print("RESID", dict(resid))


if __name__ == "__main__":
    main()
