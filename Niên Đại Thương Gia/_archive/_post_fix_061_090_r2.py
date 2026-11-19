# -*- coding: utf-8 -*-
"""Round 2 post-fix 61-90: inline spam, hard trim 77/86, expand 87."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")

INLINE_SPAM = [
    r"Chiếc cân bàn đĩa đồng đã mờ vạch số\.\s*",
    r"Tờ tiền giấy bạc mòn góc đếm qua nhiều tay\.\s*",
    r"Đì đùng máy nổ xa mờ cuối làng\.\s*",
    r"Mảnh nilon gói hàng buộc dây chuối khô\.\s*",
    r"Tõm tõm gầu nước xuống giếng sâu\.\s*",
    r"Tõm tõm gầu nước giếng\.\s*",
    r"Hăng hắc khói than làm cay mè mắt\.\s*",
    r"Rè rè loa phường phát tin sáng\.\s*",
    r"Lạch cạch khung xe đạp cũ trên đường đất\.\s*",
    r"Lạch cạch xe đạp cũ\.\s*",
    r"Loẹt xoẹt giấy tờ bóc biên lai thu tiền\.\s*",
    r"Nước mắm cá cơm đặc quánh từ chum\.\s*",
    r"Xăng pha dầu nhờn từ xưởng sửa xe\.\s*",
    r"Cây thước gỗ dấu đỏ kiểm định của ty thương nghiệp\.\s*",
    r"Than tổ ong lúc nửa đêm\.\s*",
    r"Vải mới cắt thơm mùi hồ\.\s*",
    r"Bùn non dưới ruộng lúa mới cày\.\s*",
    r"Rạ khô vừa gặt còn thơm nắng\.\s*",
    r"Nóng rát gáy dưới nắng hè đứng bán hàng\.\s*",
    r"Lạnh buốt ngón tay sờ gầu nước đầu đông\.\s*",
    r"Lạnh buốt sờ gầu nước đầu đông\.\s*",
    r"Tê nhức ngón tay sau giờ viết sổ liên tục\.\s*",
    r"Cuốn sổ gáy chỉ may vải có giá vài xu\.\s*",
    r"Ướt sũng mồ hôi lưng áo sau một ngày dài\.\s*",
]
INLINE_RE = re.compile("|".join(f"(?:{p})" for p in INLINE_SPAM))


def vi_words_body(text: str) -> int:
    best = -1
    for m in ["「Hệ thống", "«Hệ thống", "【Hệ thống"]:
        i = text.rfind(m)
        if i > best:
            best = i
    body = text[:best] if best > 0 else text
    return len([t for t in body.split() if len(t) >= 2])


def collapse(t: str) -> str:
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def split_body_panel(t: str) -> tuple[str, str]:
    panel_idx = -1
    for m in ["「Hệ thống", "«Hệ thống", "【Hệ thống"]:
        i = t.rfind(m)
        if i > panel_idx:
            panel_idx = i
    if panel_idx <= 0:
        return t, ""
    sep = t.rfind("\n====", 0, panel_idx)
    if sep > 0 and panel_idx - sep < 100:
        return t[:sep], t[sep:]
    return t[:panel_idx], t[panel_idx:]


def hard_trim(t: str, target: int = 4100) -> tuple[str, int]:
    body, panel = split_body_panel(t)
    paras = [p.strip() for p in re.split(r"\n\n+", body) if p.strip()]
    removed = 0
    # drop middle non-dialogue paras until under target
    while vi_words_body("\n\n".join(paras) + "\n") > target and len(paras) > 16:
        mid_s = max(4, len(paras) // 4)
        mid_e = min(len(paras) - 4, (3 * len(paras)) // 4)
        best_i = None
        best_sc = 10**9
        for i in range(mid_s, mid_e):
            pr = paras[i]
            if any(x in pr for x in ["—", '"', "“", "”", "「"]):
                continue
            if len(pr) < 40:
                continue
            sc = len(pr)
            if sc < best_sc:
                best_sc = sc
                best_i = i
        if best_i is None:
            # allow removing shorter dialogue-light paras
            for i in range(mid_s, mid_e):
                pr = paras[i]
                dlg = pr.count("—") + pr.count('"')
                if dlg >= 3:
                    continue
                sc = len(pr) + dlg * 200
                if sc < best_sc:
                    best_sc = sc
                    best_i = i
        if best_i is None:
            break
        del paras[best_i]
        removed += 1
    body = "\n\n".join(paras) + "\n"
    out = collapse(body + (panel if panel.startswith("\n") else "\n" + panel))
    return out, removed


def expand_ch87(t: str) -> str:
    """Add ~200-250 words of scene before panel; fix bà Hà as mother not wife."""
    body, panel = split_body_panel(t)
    # Fix wife framing
    body = body.replace(
        "Bà nhìn chồng — áo sơ-mi vẫn còn mùi dầu máy",
        "Bà nhìn con — áo sơ-mi vẫn còn mùi dầu máy",
    )
    body = body.replace('Bà Hà gắp cho ông miếng cá', "Bà Hà gắp cho con miếng cá")

    insert = """

Trước khi về, Hùng còn ở lại xưởng nửa giờ. Ông Bảy Thìn lau lại cần số chiếc MC-01 thứ ba — chiếc đã cày thử ba vòng trên thửa đất cạnh cổng. Bùn non dính dưới lưỡi cày còn ướt, mùi đất lẫn dầu diesel bốc lên khi gió chiều lùa qua khe cửa xưởng.

— Phụ tùng thay nhanh được không? — một hợp tác xã hỏi lại lần cuối.

— Bu-lông, má phanh, lọc dầu — kho Cầu Diễn giữ sẵn. Máy hỏng một buổi là mang ra, không để nằm ruộng ba ngày — Hùng đáp.

Lan ghi tên bảy người bỏ cọc vào sổ đỏ. Cạnh mỗi tên là xã, diện tích ruộng, và câu họ hỏi nhiều nhất. Không ai hỏi màu sơn. Cả bảy đều hỏi một thứ: nếu gãy răng cày giữa vụ, ai chịu.

Hùng viết thêm một dòng dưới danh sách:

"Trả lời bằng phụ tùng trong một ngày. Không trả lời bằng lời hứa."

Ông gập sổ. Tiếng động cơ đã tắt. Trên nền xưởng còn vệt bánh lốp in bùn. MC-01 không còn là bản vẽ — nó đã cày đất thật, trước mắt người sẽ trả tiền.
"""
    # Only insert if not already present
    if "Trả lời bằng phụ tùng trong một ngày" not in body:
        body = body.rstrip() + insert + "\n"
    # de-indent body lines that have leading 4 spaces (template artifact)
    lines = []
    for ln in body.splitlines():
        if ln.startswith("    ") and not ln.startswith("        "):
            lines.append(ln[4:])
        else:
            lines.append(ln)
    body = "\n".join(lines)
    return collapse(body + (panel if panel.startswith("\n") else "\n" + panel))


def main() -> None:
    # 1) inline spam all 61-90
    for n in range(61, 91):
        fps = list(ROOT.glob(f"Chương {n} - *.txt"))
        if not fps:
            continue
        fp = fps[0]
        t = fp.read_text(encoding="utf-8")
        t2, c = INLINE_RE.subn("", t)
        t2 = collapse(t2)
        # cleanup double spaces left
        t2 = re.sub(r"  +", " ", t2)
        t2 = re.sub(r" \n", "\n", t2)
        if c or t2 != t:
            fp.write_text(t2 if t2.endswith("\n") else t2 + "\n", encoding="utf-8", newline="\n")
            print(f"Ch{n} inline-spam removed {c}, w={vi_words_body(t2)}")

    # 2) hard trim 77, 86
    for n, target in [(77, 4100), (86, 4100)]:
        fp = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
        t = fp.read_text(encoding="utf-8")
        w0 = vi_words_body(t)
        t2, rm = hard_trim(t, target=target)
        w1 = vi_words_body(t2)
        # if still long, more aggressive
        rounds = 1
        while w1 > 4200 and rounds < 5:
            t2, rm2 = hard_trim(t2, target=target - 50 * rounds)
            rm += rm2
            w1 = vi_words_body(t2)
            rounds += 1
        fp.write_text(t2 if t2.endswith("\n") else t2 + "\n", encoding="utf-8", newline="\n")
        print(f"Ch{n} hardtrim {w0}->{w1} rm={rm} rounds={rounds}")

    # 3) expand/fix 87
    fp = list(ROOT.glob("Chương 87 - *.txt"))[0]
    t = fp.read_text(encoding="utf-8")
    w0 = vi_words_body(t)
    t2 = expand_ch87(t)
    w1 = vi_words_body(t2)
    fp.write_text(t2 if t2.endswith("\n") else t2 + "\n", encoding="utf-8", newline="\n")
    print(f"Ch87 expand {w0}->{w1}")

    # final scan
    print("\n=== FINAL 61-90 ===")
    for n in range(61, 91):
        fp = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
        t = fp.read_text(encoding="utf-8")
        w = vi_words_body(t)
        flags = []
        if w < 3000:
            flags.append(f"SHORT{w}")
        if w > 4200:
            flags.append(f"LONG{w}")
        if "GHI NHẬN" not in t:
            flags.append("NOGHI")
        p = len(re.findall(r"「Hệ thống", t))
        if p != 1:
            flags.append(f"P{p}")
        if INLINE_RE.search(t):
            flags.append("SPAM")
        if "{a}" in t or "{b}" in t:
            flags.append("PH")
        if "Hai ly nước ấm" in t:
            flags.append("ROM")
        if "a bà Hà" in t:
            flags.append("aBA")
        print(f"Ch{n:02d} w={w:4d} {flags or ['OK']}")


if __name__ == "__main__":
    main()
