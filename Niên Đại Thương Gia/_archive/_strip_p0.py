# -*- coding: utf-8 -*-
"""
P0 strip for Niên Đại Thương Gia — mechanical pad only.
Does NOT rewrite creative body. Backup before write.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")
BACKUP = ROOT / "_fix_backup_p0_20260729"
DRY = False

# --- romance / domestic template anchors (start of dump blocks) ---
ROMANCE_START = re.compile(
    r"(?m)^(?:"
    r"Hai ly nước ấm trên bàn"
    r"|Bên ly rượu nếp"
    r"|Đêm khuya, hai người nằm trên giường"
    r"|Sáng chủ nhật, Hùng gấp chăn màn"
    r"|Buổi trưa, Hùng nằm võng"
    r"|Ngoài vườn, hoa hồng nở đỏ"
    r"|Mưa rơi trên mái ngói, tiếng mưa rì rào"
    r"|Hùng mở cửa sổ, đón ánh nắng sớm"
    r"|Sau bữa ăn, hai người ngồi trước hiên nhà"
    r"|Trên bàn làm việc, sổ sách chất cao"
    r"|Trong nhà bếp, Hùng nhặt rau"
    r"|Một buổi sáng, \{a\} thức dậy"
    r"|Hai người ăn cơm tối\. Mùi cơm mới thơm"
    r"|Trong phòng khách, \{a\} mở tủ sách"
    r"|Một người khách đến, mắt đỏ hoe"
    r"|Hùng nhìn Lan mắt âu yếm"
    r"|Buổi chiều, Hùng ngồi ngoài hiên nhà, nhìn ra đường phố"
    r"|Đêm xuống, Hùng ngồi trước hiên nhà, nhìn lên bầu trời đầy sao"
    r"|a bà Hà đi dạo"
    r"|a Lan đi dạo"
    r"|Tình yêu trong những điều nhỏ bé"
    r")"
)

PLACEHOLDER_BLOCK = re.compile(
    r"(?ms)(?:^|\n)[^\n]*\{[ab]\}[^\n]*(?:\n[^\n]*\{[ab]\}[^\n]*)*"
)

# isolated sensory spam lines (full line only)
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

# unaccent-heavy short lines (heuristic: many ascii letters, no vietnamese diacritics, long)
UNACCENT_LINE = re.compile(
    r"(?m)^(?=[A-Za-z0-9 ,\.\'\"\-]{40,}$)(?!.*[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐÀ-ỹ]).+$"
)

PANEL_RE = re.compile(
    r"「Hệ thống[^\n]*」[\s\S]*?(?=(?:\n「Hệ thống)|(?:\n={10,})|$)",
    re.M,
)
SEP = re.compile(r"(?m)^={10,}\s*$")
TEASER_EMPTY = re.compile(r"(?m)^Teaser:\s*\n+", re.M)


def vi_words(text: str) -> int:
    return len([t for t in text.split() if len(t) >= 2])


def strip_romance_before_panel(text: str) -> tuple[str, int]:
    """Cut from first romance dump start to panel (or end), if dump is in last 35% of file."""
    m = ROMANCE_START.search(text)
    if not m:
        return text, 0
    # only strip if marker is in latter part of file (avoid false positive in body)
    if m.start() < int(len(text) * 0.55):
        # still allow if many romance hits after this point
        rest = text[m.start() :]
        hits = len(ROMANCE_START.findall(rest))
        if hits < 2 and "{a}" not in rest and "{b}" not in rest:
            return text, 0

    panel = text.find("「Hệ thống", m.start())
    if panel == -1:
        # cut to last separator or end
        cut_end = len(text)
        # keep trailing separators+panel if any before end without panel
        new = text[: m.start()].rstrip() + "\n\n"
        return new, 1

    head = text[: m.start()].rstrip()
    tail = text[panel:]  # keep panels from here
    return head + "\n\n" + tail, 1


def strip_placeholders(text: str) -> tuple[str, int]:
    new, n = PLACEHOLDER_BLOCK.subn("\n", text)
    # also single-line leftovers
    new2, n2 = re.subn(r"(?m)^.*\{[ab]\}.*$\n?", "", new)
    return new2, n + n2


def strip_spam_lines(text: str) -> tuple[str, int]:
    new, n = SPAM_LINE.subn("", text)
    # collapse 3+ blank lines
    new = re.sub(r"\n{3,}", "\n\n", new)
    return new, n


def strip_unaccent_blocks(text: str) -> tuple[str, int]:
    """Remove consecutive unaccent lines near end (before panel)."""
    panel = text.find("「Hệ thống")
    if panel == -1:
        region_end = len(text)
    else:
        region_end = panel
    region = text[:region_end]
    lines = region.splitlines(keepends=True)
    out = []
    removed = 0
    i = 0
    while i < len(lines):
        ln = lines[i]
        if UNACCENT_LINE.match(ln.rstrip("\n")) and len(ln.strip()) > 50:
            # remove run of unaccent lines
            while i < len(lines) and (
                UNACCENT_LINE.match(lines[i].rstrip("\n"))
                or lines[i].strip() == ""
                or re.match(r"^[a-z] [A-Za-z]", lines[i])
            ):
                if lines[i].strip():
                    removed += 1
                i += 1
            continue
        # broken 'a bà Hà' / 'a Lan'
        if re.match(r"^a (bà Hà|Lan) ", ln):
            removed += 1
            i += 1
            continue
        out.append(ln)
        i += 1
    new_head = "".join(out)
    return new_head + text[region_end:], removed


def dedupe_adjacent_paragraphs(text: str) -> tuple[str, int]:
    parts = re.split(r"(\n\n+)", text)
    out = []
    removed = 0
    prev_para = None
    for p in parts:
        if p.startswith("\n") or not p.strip():
            out.append(p)
            continue
        # only dedupe long paras
        norm = re.sub(r"\s+", " ", p.strip())
        if prev_para and len(norm) > 80 and norm == prev_para:
            removed += 1
            continue
        # near-duplicate: first 100 chars
        if prev_para and len(norm) > 120 and norm[:100] == prev_para[:100]:
            removed += 1
            continue
        out.append(p)
        prev_para = norm
    return "".join(out), removed


def consolidate_panels(text: str) -> tuple[str, int]:
    panels = list(PANEL_RE.finditer(text))
    if len(panels) <= 1:
        return text, 0
    # keep last GHI NHẬN-ish panel preferably
    keep = None
    for p in reversed(panels):
        if "GHI NHẬN" in p.group(0) or "CỘT MỐC" in p.group(0):
            keep = p
            break
    if keep is None:
        keep = panels[-1]
    # remove all panels from text then append keep at end (after cleaning teaser empties)
    body = PANEL_RE.sub("", text)
    body = TEASER_EMPTY.sub("\n", body)
    body = body.rstrip()
    # remove trailing seps
    body = re.sub(r"(?:\n={10,}\s*)+$", "", body).rstrip()
    panel_txt = keep.group(0).strip()
    # strip skill dump lines that list every unlock
    panel_txt = re.sub(
        r"(?m)^Kỹ năng hiện có:.*$",
        "Kỹ năng trọng yếu: (xem ledger)",
        panel_txt,
    )
    new = (
        body
        + "\n\n============================================================\n"
        + panel_txt
        + "\n============================================================\n"
    )
    return new, len(panels) - 1


def strip_post_panel_garbage(text: str) -> tuple[str, int]:
    """Anything after last panel that isn't separator."""
    panels = list(PANEL_RE.finditer(text))
    if not panels:
        return text, 0
    last = panels[-1]
    after = text[last.end() :]
    # keep only seps and whitespace
    cleaned = re.sub(r"[^=\s\n].*", "", after, flags=re.S)
    # if after had real prose
    if re.search(r"[A-Za-zÀ-ỹ]{10,}", after):
        return text[: last.end()] + "\n============================================================\n", 1
    return text, 0


def process_one(text: str) -> tuple[str, dict]:
    stats = Counter()
    t = text.replace("\r\n", "\n")
    t, n = strip_placeholders(t)
    stats["placeholder"] = n
    t, n = strip_romance_before_panel(t)
    stats["romance_cut"] = n
    t, n = strip_spam_lines(t)
    stats["spam_lines"] = n
    t, n = strip_unaccent_blocks(t)
    stats["unaccent"] = n
    t, n = dedupe_adjacent_paragraphs(t)
    stats["dedupe"] = n
    t, n = consolidate_panels(t)
    stats["panel_merge"] = n
    t, n = strip_post_panel_garbage(t)
    stats["post_panel"] = n
    # second pass romance (after other cleanups may expose)
    t, n = strip_romance_before_panel(t)
    stats["romance_cut"] += n
    t, n = strip_placeholders(t)
    stats["placeholder"] += n
    t = re.sub(r"\n{3,}", "\n\n", t)
    if not t.endswith("\n"):
        t += "\n"
    stats["words_after"] = vi_words(t)
    return t, stats


def main():
    files = sorted(
        ROOT.glob("Chương *.txt"),
        key=lambda f: int(re.search(r"Chương (\d+)", f.name).group(1)),
    )
    assert len(files) == 360, len(files)
    if not DRY:
        BACKUP.mkdir(parents=True, exist_ok=True)

    total = Counter()
    changed = 0
    short = []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="replace")
        w0 = vi_words(raw)
        new, st = process_one(raw)
        w1 = st["words_after"]
        total.update({k: v for k, v in st.items() if k != "words_after"})
        if new != raw:
            changed += 1
            if not DRY:
                dest = BACKUP / f.name
                if not dest.exists():
                    shutil.copy2(f, dest)
                f.write_text(new, encoding="utf-8")
        if w1 < 2800:
            short.append((f.name, w0, w1))
        num = int(re.search(r"Chương (\d+)", f.name).group(1))
        if num % 60 == 0:
            print(f"... ch{num} changed_so_far={changed}")

    print("CHANGED", changed, "/", len(files))
    print("STATS", dict(total))
    print("SHORT<2800", len(short))
    for row in short[:30]:
        print(" ", row)
    # residual markers
    resid = Counter()
    for f in files:
        t = f.read_text(encoding="utf-8", errors="replace")
        for m, lab in [
            ("Hai ly nước ấm", "nuoc_am"),
            ("trộm ổi", "oi"),
            ("{a}", "ph_a"),
            ("{b}", "ph_b"),
            ("Bên ly rượu nếp", "ruou"),
            ("Tình yêu trong những điều nhỏ bé", "tinhyeu"),
        ]:
            if m in t:
                resid[lab] += 1
    print("RESIDUAL_FILES", dict(resid))


if __name__ == "__main__":
    main()
