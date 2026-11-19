# -*- coding: utf-8 -*-
"""Post-strip fix ch.61-90: residual spam, broken panels, overlength trim."""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")
BACKUP = ROOT / "_fix_backup_post_061_090"
BACKUP.mkdir(exist_ok=True)

SPAM_LINE = re.compile(
    r"(?m)^(?:"
    r"Tờ tiền giấy bạc mòn góc đếm qua nhiều tay\."
    r"|Chiếc cân bàn đĩa đồng đã mờ vạch số\."
    r"|Đì đùng máy nổ xa mờ cuối làng\."
    r"|Mảnh nilon gói hàng buộc dây chuối khô\."
    r"|Tõm tõm gầu nước xuống giếng sâu\."
    r"|Tõm tõm gầu nước giếng\."
    r"|Hăng hắc khói than làm cay mè mắt\."
    r"|Rè rè loa phường phát tin sáng\."
    r"|Lạch cạch khung xe đạp cũ trên đường đất\."
    r"|Lạch cạch xe đạp cũ\."
    r"|Nước mắm cá cơm đặc quánh từ chum\."
    r"|Xăng pha dầu nhờn từ xưởng sửa xe\."
    r"|Cây thước gỗ dấu đỏ kiểm định của ty thương nghiệp\."
    r"|Loẹt xoẹt giấy tờ bóc biên lai thu tiền\."
    r"|Than tổ ong lúc nửa đêm\."
    r"|Vải mới cắt thơm mùi hồ\."
    r"|Bùn non dưới ruộng lúa mới cày\."
    r"|Rạ khô vừa gặt còn thơm nắng\."
    r"|Nóng rát gáy dưới nắng hè đứng bán hàng\."
    r"|Lạnh buốt ngón tay sờ gầu nước đầu đông\."
    r"|Lạnh buốt sờ gầu nước đầu đông\."
    r"|Tê nhức ngón tay sau giờ viết sổ liên tục\."
    r"|Cuốn sổ gáy chỉ may vải có giá vài xu\."
    r"|Ướt sũng mồ hôi lưng áo sau một ngày dài\."
    r")\s*$"
)


def vi_words_body(text: str) -> int:
    best = -1
    for m in ["「Hệ thống", "«Hệ thống", "【Hệ thống", '"Hệ thống']:
        i = text.rfind(m)
        if i > best:
            best = i
    body = text[:best] if best > 0 else text
    return len([t for t in body.split() if len(t) >= 2])


def collapse_blank(t: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", t)


def strip_spam(t: str) -> tuple[str, int]:
    new, n = SPAM_LINE.subn("", t)
    return collapse_blank(new), n


def fix_ch83(t: str) -> str:
    t = t.replace('"Hệ thống — GHI NHẬN ch.83」', "「Hệ thống — GHI NHẬN ch.83」")
    t = re.sub(r"\n+Teaser:\s*\n*\s*$", "\n", t)
    if "============================================================\n「Hệ thống — GHI NHẬN ch.83」" not in t:
        t = t.replace(
            "「Hệ thống — GHI NHẬN ch.83」",
            "============================================================\n「Hệ thống — GHI NHẬN ch.83」",
        )
    t = t.rstrip() + "\n============================================================\n"
    # dedupe trailing seps
    t = re.sub(r"(?:\n={60}\s*){2,}\s*$", "\n" + "=" * 60 + "\n", t)
    return t


def fix_ch89(t: str) -> str:
    t = re.sub(r"(?m)^a bà Hà", "Bà Hà", t)
    t = t.replace("a bà Hà", "bà Hà")

    ret = t.find("Rét chưa qua. Mai — Part 3.")
    if ret != -1:
        head = t[: ret + len("Rét chưa qua. Mai — Part 3.")].rstrip()
    else:
        cut_a = t.find("\nNăm: 1986 | Tổng EXP")
        if cut_a == -1:
            cut_a = t.rfind("「Hệ thống")
        head = t[:cut_a].rstrip() if cut_a > 0 else t

    head = re.sub(r"(?:\n={10,}\s*)+$", "", head).rstrip()
    head = re.sub(
        r"\nNăm: 1986 \| Tổng EXP:.*?(?=\n\n|\n={10,}|\Z)", "", head, flags=re.S
    )
    head = re.sub(r"\nGhi chú:\s*system_ledger\s*", "\n", head)
    head = re.sub(
        r"\nNăm: 1986\nTổng EXP: 14,500 \(\+250\).*?(?=\n={10,}|\n「|\Z)",
        "",
        head,
        flags=re.S,
    )
    # Drop orphan mid-summary blocks that look like bare stats
    head = re.sub(
        r"\nKỹ năng: Logistics lv1.*?(?=\n\n|\n={10,}|\Z)", "", head, flags=re.S
    )
    head = re.sub(
        r"\nĐội lõi: Trần Văn Hùng.*?(?=\n\n|\n={10,}|\Z)", "", head, flags=re.S
    )
    head = re.sub(
        r"\nThành quả: 30 trường.*?(?=\n\n|\n={10,}|\Z)", "", head, flags=re.S
    )
    head = re.sub(r"(?:\n={10,}\s*)+$", "", head).rstrip()
    head = collapse_blank(head)

    panel = (
        "\n\n============================================================\n"
        "「Hệ thống — GHI NHẬN ch.89」\n"
        "Năm: 1986\n"
        "Tổng EXP: 14,500 (+250 nhịp này)\n"
        "Không gian kho: 5,000m² (+57m²)\n"
        "Kỹ năng trọng yếu: Logistics lv2, Tài chính lv1, Thương mại lv2\n"
        "Ghi chú: Khóa Phần 2 — checklist 7 mũi đã xong; Part 3 mở cửa.\n"
        "============================================================\n"
    )
    return head + panel


def split_body_panel(t: str) -> tuple[str, str]:
    panel_idx = -1
    for m in ["「Hệ thống", "«Hệ thống", "【Hệ thống", '"Hệ thống']:
        i = t.rfind(m)
        if i > panel_idx:
            panel_idx = i
    if panel_idx <= 0:
        return t, ""
    sep = t.rfind("\n====", 0, panel_idx)
    if sep > 0 and panel_idx - sep < 100:
        return t[:sep], t[sep:]
    return t[:panel_idx], t[panel_idx:]


def trim_if_overlong(t: str, target_max: int = 4150, min_keep: int = 3000) -> tuple[str, int]:
    w = vi_words_body(t)
    if w <= target_max:
        return t, 0

    body, panel = split_body_panel(t)
    paras = [p.strip() for p in re.split(r"\n\n+", body) if p.strip()]
    new_paras = []
    removed = 0
    seen_norm: set[str] = set()
    for ps in paras:
        norm = re.sub(r"\s+", " ", ps)[:120]
        if norm in seen_norm and len(ps) < 400:
            removed += 1
            continue
        seen_norm.add(norm)
        if (
            len(ps) < 90
            and ps.count(".") <= 1
            and any(
                h in ps
                for h in [
                    "mòn góc",
                    "đĩa đồng",
                    "gầu nước",
                    "loa phường",
                    "nilon",
                    "khói than",
                ]
            )
        ):
            removed += 1
            continue
        new_paras.append(ps)

    body2 = "\n\n".join(new_paras) + "\n"
    t2 = collapse_blank(body2 + (panel if panel.startswith("\n") else "\n" + panel))
    w2 = vi_words_body(t2)

    if w2 > target_max + 100:
        body, panel = split_body_panel(t2)
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        while vi_words_body("\n\n".join(paras) + "\n") > target_max and len(paras) > 14:
            mid_start = len(paras) // 3
            mid_end = (2 * len(paras)) // 3
            candidates = []
            for i in range(mid_start, mid_end):
                pr = paras[i]
                has_dlg = ("—" in pr) or ('"' in pr) or ("“" in pr) or ("”" in pr)
                score = 100000 if has_dlg else len(pr)
                # protect opening / title-ish
                if i < 3:
                    score = 200000
                candidates.append((score, i))
            candidates.sort()
            to_rm = None
            for sc, i in candidates:
                if sc < 100000:
                    to_rm = i
                    break
            if to_rm is None:
                break
            del paras[to_rm]
            removed += 1
            if vi_words_body("\n\n".join(paras) + "\n") < min_keep + 150:
                break
        body = "\n\n".join(paras) + "\n"
        t2 = collapse_blank(body + (panel if panel.startswith("\n") else "\n" + panel))
    return t2, removed


def main() -> None:
    results = []
    for n in range(61, 91):
        fps = list(ROOT.glob(f"Chương {n} - *.txt"))
        if not fps:
            results.append((n, 0, 0, ["MISSING"], ["MISSING"]))
            continue
        fp = fps[0]
        raw = fp.read_text(encoding="utf-8")
        bak = BACKUP / fp.name
        if not bak.exists():
            shutil.copy2(fp, bak)

        t = raw
        notes: list[str] = []
        t, ns = strip_spam(t)
        if ns:
            notes.append(f"spam-{ns}")

        if n == 83:
            t2 = fix_ch83(t)
            if t2 != t:
                notes.append("fix-panel83")
            t = t2
        if n == 89:
            t2 = fix_ch89(t)
            if t2 != t:
                notes.append("fix-panel89")
            t = t2

        t = re.sub(r"(?:\n={60}\s*){2,}\s*$", "\n" + "=" * 60 + "\n", t)
        t2 = re.sub(r"\n+Teaser:\s*\n*\s*$", "\n", t)
        if t2 != t:
            notes.append("teaser")
            t = t2
        t2 = re.sub(r'(?m)^"Hệ thống — GHI NHẬN', "「Hệ thống — GHI NHẬN", t)
        if t2 != t:
            notes.append("panel-quote")
            t = t2

        w0 = vi_words_body(t)
        if w0 > 4200:
            t, nr = trim_if_overlong(t, target_max=4150)
            notes.append(f"trim-rm{nr}")
        t = collapse_blank(t)
        if not t.endswith("\n"):
            t += "\n"

        w1 = vi_words_body(t)
        flags = []
        if w1 < 3000:
            flags.append(f"SHORT{w1}")
        if w1 > 4200:
            flags.append(f"STILLLONG{w1}")
        if "GHI NHẬN" not in t:
            flags.append("NOGHI")
        panels = len(re.findall(r"「Hệ thống|【Hệ thống", t))
        if panels != 1:
            flags.append(f"P{panels}")
        head = t.find("=" * 10)
        if head < 0 or head > 400:
            flags.append(f"H{head}")
        if "{a}" in t or "{b}" in t:
            flags.append("PLACEHOLDER")
        if "Hai ly nước ấm" in t:
            flags.append("ROMANCE")
        if "a bà Hà" in t:
            flags.append("aBAHA")

        if t != raw:
            fp.write_text(t, encoding="utf-8", newline="\n")
            notes.append("WRITTEN")
        results.append((n, w0, w1, notes, flags))

    for n, w0, w1, notes, flags in results:
        print(f"Ch{n}: {w0}->{w1} | {','.join(notes) or '-'} | {flags or ['OK']}")
    print("done", datetime.now())


if __name__ == "__main__":
    main()
