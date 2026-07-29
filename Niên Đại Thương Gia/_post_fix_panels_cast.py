# -*- coding: utf-8 -*-
"""Fix split panels (70/75/82) + wife-frame cast (82/83/89) + ch89 typo."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"C:/Dev/XLab_MTC/Niên Đại Thương Gia")


def merge_orphan_panel(t: str, ch: int) -> str:
    """Move orphan stats block into proper 「Hệ thống — GHI NHẬN」 panel."""
    header = f"「Hệ thống — GHI NHẬN ch.{ch}」"
    hi = t.rfind(header)
    if hi < 0:
        return t

    # Find orphan "Năm: YYYY\nTổng EXP:" in last 1500 chars before header
    pre = t[:hi]
    # Prefer last occurrence of Năm: 19xx before panel
    matches = list(re.finditer(r"(?m)^Năm:\s*19\d\d\s*$", pre))
    if not matches:
        return t
    start = matches[-1].start()
    # include preceding separator if close
    sep = pre.rfind("\n====", 0, start)
    if sep > 0 and start - sep < 80:
        cut_start = sep
    else:
        # maybe blank lines only
        cut_start = start
        while cut_start > 0 and pre[cut_start - 1] in "\n\r":
            cut_start -= 1
        # keep one blank
        cut_start = max(0, cut_start)

    orphan = pre[start:hi].strip()
    # strip trailing seps from orphan
    orphan = re.sub(r"(?:\n={10,}\s*)+$", "", orphan).strip()
    # remove orphan from body
    body = pre[:cut_start].rstrip()
    # after header: drop empty seps and rebuild
    after = t[hi + len(header) :]
    after = re.sub(r"^(?:\s|\n|={10,})+", "\n", after)
    # if after is just seps, empty it for rebuild
    after_clean = after.strip()
    if after_clean.startswith("=") or not after_clean:
        after_clean = ""

    # If orphan already has content, use it as panel body
    # Ensure ends with sep
    panel = (
        f"\n\n{'=' * 60}\n"
        f"{header}\n"
        f"{orphan}\n"
        f"{'=' * 60}\n"
    )
    # Don't duplicate after_clean if it was empty panel
    return body + panel


def fix_cast(t: str, ch: int) -> tuple[str, list[str]]:
    notes = []
    if ch == 82:
        old = "Ông nhìn bát cơm, nhìn mâm thức ăn đơn giản, nhìn người vợ đã ở với mình qua bao nhiêu ngày khó."
        new = "Ông nhìn bát cơm, nhìn mâm thức ăn đơn giản, nhìn bà Hà — người mẹ đã ở với mình qua bao nhiêu ngày khó."
        if old in t:
            t = t.replace(old, new)
            notes.append("82-wife->me")
    if ch == 83:
        old = "bao lần nhìn chồng về trong bóng tối"
        new = "bao lần nhìn con trai về trong bóng tối"
        if old in t:
            t = t.replace(old, new)
            notes.append("83-chong->con")
    if ch == 89:
        # typo
        if "củbà Hà" in t:
            t = t.replace("củbà Hà", "của bà Hà")
            notes.append("89-typo")
        # Lan wife frame
        old = "Cô nhìn chồng sổ, nhìn ngọn đèn dầu, nhìn bóng tối ngoài cửa sổ, và biết rằng đêm nay cô cần"
        # try broader
        t2, n = re.subn(
            r"Cô nhìn chồng sổ",
            "Cô nhìn chồng sổ sách",
            t,
            count=1,
        )
        # Actually "chồng sổ sách" = stack of ledgers is OK for sister Lan
        # But "đêm nay cô cần" + looking at husband is wife frame. Check full sentence.
        if "Cô nhìn chồng sổ" in t or "Cô nhìn chồng sổ sách" in t2:
            t = re.sub(
                r"Cô nhìn chồng sổ(?: sách)?, nhìn ngọn đèn dầu, nhìn bóng tối ngoài cửa sổ, và biết rằng đêm nay cô cần[^\n]*",
                "Cô nhìn chồng sổ sách trên bàn, nhìn ngọn đèn dầu, nhìn bóng tối ngoài cửa sổ — em gái biết anh còn việc chưa khép, và đêm nay không cần hỏi thêm.",
                t,
                count=1,
            )
            notes.append("89-lan-frame")
        # also fix if only typo path
        if "củbà" in t:
            t = t.replace("củbà", "của bà")
    return t, notes


def main() -> None:
    for n in [70, 75, 82, 83, 89]:
        fp = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
        t0 = fp.read_text(encoding="utf-8")
        t = t0
        notes = []
        if n in (70, 75, 82):
            t2 = merge_orphan_panel(t, n)
            if t2 != t:
                notes.append("merge-panel")
            t = t2
        t, cn = fix_cast(t, n)
        notes.extend(cn)
        t = re.sub(r"\n{3,}", "\n\n", t)
        if not t.endswith("\n"):
            t += "\n"
        if t != t0:
            fp.write_text(t, encoding="utf-8", newline="\n")
        # verify
        m = re.search(
            rf"「Hệ thống — GHI NHẬN ch\.{n}」\s*\n([\s\S]*?)(?:\n={{10,}}|\Z)", t
        )
        ok = bool(m and "Năm:" in m.group(1) and "EXP" in m.group(1))
        wife = any(x in t for x in ["người vợ đã ở", "nhìn chồng về", "Cô nhìn chồng sổ,"])
        print(f"Ch{n}: notes={notes} panel_ok={ok} wife_left={wife}")
        if m:
            print("  panel head:", m.group(1)[:180].replace("\n", " | "))


if __name__ == "__main__":
    main()
