# -*- coding: utf-8 -*-
"""Safe header normalize for MTCDS. Never match ===== separators as === Title ===."""
import re, os, stat
from pathlib import Path

base = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
pat = re.compile(r"Chương\s*0*(\d+)\s*-\s*(.+)\.txt$", re.I)
SEP = "=" * 60
# Safe: exactly 3 equals each side, content MUST NOT contain '='
EQ_TITLE = re.compile(r"^===\s*([^=\n]+?)\s*===$")
CH_HDR = re.compile(r"^Chương\s*0*(\d+)\s*[:：]\s*(.+)$")
fixed = []
skipped = []

for f in sorted(base.glob("Chương *.txt")):
    m = pat.match(f.name)
    if not m:
        continue
    n = int(m.group(1))
    title_from_name = m.group(2).strip()
    t = f.read_text(encoding="utf-8", errors="replace")
    lines = t.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    if not lines:
        continue
    first = lines[0].strip()
    # Already good: starts with 6+ equals
    if re.match(r"^={6,}$", first):
        # Check second line is Chương N: Title (not another separator)
        if len(lines) > 1:
            second = lines[1].strip()
            if re.match(r"^={6,}$", second) or not CH_HDR.match(second):
                # try find real title line
                title = title_from_name
                for ln in lines[1:6]:
                    hm = CH_HDR.match(ln.strip())
                    if hm:
                        title = hm.group(2).strip()
                        break
                # rebuild top if broken
                body_start = 0
                for i, ln in enumerate(lines):
                    if CH_HDR.match(ln.strip()) or (i > 0 and ln.strip() and not ln.strip().startswith("=")):
                        # find first non-sep content after header block
                        pass
                # only rebuild if second is sep or missing ch header
                if re.match(r"^={6,}$", second) or not CH_HDR.match(second):
                    # drop leading seps and rebuild
                    rest = lines[:]
                    while rest and (rest[0].strip() == "" or re.match(r"^={3,}$", rest[0].strip())):
                        rest.pop(0)
                    if rest and CH_HDR.match(rest[0].strip()):
                        hm = CH_HDR.match(rest[0].strip())
                        title = hm.group(2).strip()
                        rest = rest[1:]
                        while rest and re.match(r"^={3,}$", rest[0].strip()):
                            rest.pop(0)
                    new = [SEP, f"Chương {n}: {title}", SEP, ""] + rest
                    body = "\n".join(new)
                    if body != t:
                        os.chmod(f, stat.S_IWRITE | stat.S_IREAD)
                        f.write_text(body, encoding="utf-8")
                        fixed.append((n, "rebuild-sep-block"))
                continue
        skipped.append((n, "ok-sep"))
        continue

    changed = False
    # Case A: duplicate first two identical lines
    if len(lines) > 1 and lines[0].strip() == lines[1].strip() and lines[0].strip():
        lines.pop(1)
        changed = True
        first = lines[0].strip()

    # Case B: bare === or === Title === (exactly 3 equals, no more)
    if first == "===":
        # next lines may be Chương N: Title then ===
        title = title_from_name
        # drop first ===
        lines.pop(0)
        while lines and lines[0].strip() == "":
            lines.pop(0)
        if lines:
            hm = CH_HDR.match(lines[0].strip())
            if hm:
                title = hm.group(2).strip()
                lines.pop(0)
            elif EQ_TITLE.match(lines[0].strip()):
                title = EQ_TITLE.match(lines[0].strip()).group(1).strip()
                lines.pop(0)
        while lines and (lines[0].strip() == "" or lines[0].strip() == "===" or re.match(r"^={3,}$", lines[0].strip())):
            lines.pop(0)
        lines = [SEP, f"Chương {n}: {title}", SEP, ""] + lines
        changed = True
    else:
        em = EQ_TITLE.match(first)
        if em:
            title = em.group(1).strip()
            lines[0] = f"Chương {n}: {title}"
            # drop following === line if present
            if len(lines) > 1 and (lines[1].strip() == "===" or re.match(r"^={3,5}$", lines[1].strip())):
                lines.pop(1)
            lines = [SEP, lines[0], SEP] + lines[1:]
            changed = True
        else:
            hm = CH_HDR.match(first)
            if hm:
                # Chương N: Title without separator
                title = hm.group(2).strip()
                lines[0] = f"Chương {n}: {title}"
                lines = [SEP, lines[0], SEP] + lines[1:]
                changed = True

    if changed:
        body = "\n".join(lines)
        # collapse accidental double SEP blocks at top
        body = re.sub(
            r"^(={60}\nChương \d+: [^\n]+\n={60}\n)+",
            lambda m: m.group(0).split("\nChương")[0] + "\nChương" + m.group(0).split("\nChương", 1)[1].split("\n" + SEP + "\n", 1)[0].split("\n", 1)[-1] if False else m.group(0),
            body,
            count=1,
        )
        # simpler: ensure single top header
        ls = body.split("\n")
        # if first three are SEP / Chương / SEP good
        if not (ls and re.match(r"^={6,}$", ls[0].strip()) and len(ls) > 2 and CH_HDR.match(ls[1].strip()) and re.match(r"^={6,}$", ls[2].strip())):
            # force rebuild
            title = title_from_name
            rest = ls[:]
            while rest and (not rest[0].strip() or rest[0].strip().startswith("=")):
                rest.pop(0)
            if rest and CH_HDR.match(rest[0].strip()):
                title = CH_HDR.match(rest[0].strip()).group(2).strip()
                rest = rest[1:]
                while rest and rest[0].strip().startswith("="):
                    rest.pop(0)
            ls = [SEP, f"Chương {n}: {title}", SEP, ""] + rest
            body = "\n".join(ls)
        os.chmod(f, stat.S_IWRITE | stat.S_IREAD)
        f.write_text(body, encoding="utf-8")
        fixed.append((n, "normalized"))

print("fixed", len(fixed))
print("sample", fixed[:20])
# verify
bad = []
for f in sorted(base.glob("Chương *.txt")):
    m = pat.match(f.name)
    if not m:
        continue
    n = int(m.group(1))
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) < 3:
        bad.append((n, "short", lines[:2]))
        continue
    if not re.match(r"^={6,}$", lines[0].strip()):
        bad.append((n, "no-sep0", lines[0][:40]))
        continue
    if not CH_HDR.match(lines[1].strip()):
        bad.append((n, "no-ch1", lines[1][:40]))
        continue
    if not re.match(r"^={6,}$", lines[2].strip()):
        bad.append((n, "no-sep2", lines[2][:40]))
        continue
    # broken title with =====
    if "====" in lines[1]:
        bad.append((n, "eq-in-title", lines[1][:50]))
print("still_bad", len(bad))
for b in bad[:30]:
    print(" ", b)
