# -*- coding: utf-8 -*-
"""
Deterministic clone-strip for target chapters.
- Rebuild global clone set (line in >=5 chapters).
- Keep header + unique body lines (in original order, dedup intra-chapter).
- Drop clone-set lines AND intra-chapter duplicate long-line blocks.
- Preserve exactly ONE system panel (「Hệ thống ... 」 block) at the end.
- Report tokens before/after so caller can expand shorts.
"""
import os, re, glob, sys, json, unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
def norm(s): return unicodedata.normalize('NFC', s)
def vi(t): return len([x for x in t.split() if len(x) >= 2])
SEP = '=' * 60

# ---- FROZEN global clone set (from git baseline; never recompute from live disk) ----
_cs = json.load(open(os.path.join(ROOT, '_cloneset.json'), encoding='utf-8'))
CLONE = {norm(l) for l in _cs['clone_lines']}

PANEL_START = re.compile(r'^[「【«]?\s*Hệ thống')

def strip_file(n, dry=True):
    fl = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
    if not fl:
        return (n, None, None, 'NOFILE')
    path = fl[0]
    raw = norm(open(path, encoding='utf-8', errors='replace').read())
    pr = raw.split(SEP)
    if len(pr) < 3:
        return (n, None, None, 'NOHEADER')
    header = SEP + pr[1] + SEP  # ==== Chương N: Title ====
    body_full = SEP.join(pr[2:])

    # Isolate panel: find first line starting a panel marker
    lines = body_full.split('\n')
    panel_idx = None
    for i, l in enumerate(lines):
        if PANEL_START.match(l.strip()):
            panel_idx = i
            break
    if panel_idx is not None:
        body_lines = lines[:panel_idx]
        panel_lines = lines[panel_idx:]
    else:
        body_lines = lines
        panel_lines = []

    # Rebuild body: drop clone-set long lines + intra-chapter dup long lines
    seen = set()
    out = []
    for l in body_lines:
        s = l.strip()
        if len(s) >= 40:
            if s in CLONE:
                continue
            if s in seen:
                continue
            seen.add(s)
        out.append(l)

    # collapse >2 blank lines
    new_body = '\n'.join(out).strip()
    new_body = re.sub(r'\n{3,}', '\n\n', new_body)

    # clean panel: strip trailing separator lines, rebuild one clean panel
    panel_txt = '\n'.join(panel_lines).strip()
    panel_txt = panel_txt.replace(SEP, '').strip()

    toks = vi(new_body)
    assembled = f"{header}\n\n{new_body}\n\n{panel_txt}\n{SEP}\n"

    if not dry:
        open(path, 'w', encoding='utf-8').write(assembled)
    return (n, toks, os.path.basename(path), 'OK')

if __name__ == '__main__':
    dry = '--write' not in sys.argv
    nums = [int(x) for x in sys.argv[1:] if x.isdigit()]
    for n in nums:
        r = strip_file(n, dry=dry)
        print(f"ch{r[0]}: toks_after={r[1]} status={r[3]} {'(DRY)' if dry else '(WROTE)'}")
