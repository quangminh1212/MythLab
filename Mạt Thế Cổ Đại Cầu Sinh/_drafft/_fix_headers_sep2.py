# -*- coding: utf-8 -*-
"""Ensure every chapter has SEP / Chương N: Title / SEP at top. Safe."""
import re, os, stat
from pathlib import Path

base = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
pat = re.compile(r"Chương\s*0*(\d+)\s*-\s*(.+)\.txt$", re.I)
CH = re.compile(r"^Chương\s*0*(\d+)\s*[:：]\s*(.+)$")
SEP = "=" * 60
fixed = 0
still = []

for f in sorted(base.glob("Chương *.txt")):
    m = pat.match(f.name)
    if not m:
        continue
    n = int(m.group(1))
    title_name = m.group(2).strip()
    raw = f.read_text(encoding="utf-8", errors="replace")
    lines = raw.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        still.append((n, "empty"))
        continue
    # detect current top
    i = 0
    has_top_sep = bool(re.match(r"^={6,}$", lines[0].strip()))
    if has_top_sep:
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    title = title_name
    if i < len(lines):
        hm = CH.match(lines[i].strip())
        if hm:
            title = hm.group(2).strip()
            # strip accidental ===== in title
            if "====" in title or title.startswith("="):
                title = title_name
            i += 1
        else:
            # no chapter header line
            pass
    # skip blank and bottom sep if present
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and re.match(r"^={6,}$", lines[i].strip()):
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    body = lines[i:]
    new_lines = [SEP, f"Chương {n}: {title}", SEP, ""] + body
    new = "\n".join(new_lines)
    # only write if header block differs or title had equals
    old_head = "\n".join(lines[: min(6, len(lines))])
    new_head = "\n".join(new_lines[:6])
    if old_head != new_head or "====" in (lines[1] if len(lines) > 1 else ""):
        os.chmod(f, stat.S_IWRITE | stat.S_IREAD)
        f.write_text(new, encoding="utf-8")
        fixed += 1

# verify
bad = []
for f in sorted(base.glob("Chương *.txt")):
    m = pat.match(f.name)
    if not m:
        continue
    n = int(m.group(1))
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    ok = (
        len(lines) >= 4
        and re.match(r"^={6,}$", lines[0].strip())
        and CH.match(lines[1].strip())
        and "====" not in lines[1]
        and re.match(r"^={6,}$", lines[2].strip())
    )
    if not ok:
        bad.append((n, lines[:3]))

print("fixed_headers", fixed)
print("still_bad", len(bad))
for b in bad[:15]:
    print(b)
