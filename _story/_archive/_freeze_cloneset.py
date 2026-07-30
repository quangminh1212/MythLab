# -*- coding: utf-8 -*-
"""Compute clone set ONCE from git baseline and freeze to JSON.
A long line (>=40 chars) is a clone if it appears in >=5 baseline chapters.
Both _strip_clones.py and _gate.py must load THIS frozen set, never recompute
from live disk (which shrinks as we strip)."""
import os, glob, json, unicodedata
BASE = r"C:\c\Dev\_ndtg_base\Niên Đại Thương Gia"
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cloneset.json")
SEP = "=" * 60
def norm(s): return unicodedata.normalize("NFC", s)

line_chs = {}
n_files = 0
for p in glob.glob(os.path.join(BASE, "Chương *.txt")):
    n_files += 1
    raw = norm(open(p, encoding="utf-8", errors="replace").read())
    pr = raw.split(SEP)
    body = (SEP.join(pr[2:]) if len(pr) >= 3 else raw)
    for l in set(l.strip() for l in body.split("\n") if len(l.strip()) >= 40):
        line_chs.setdefault(l, set()).add(p)

clone = sorted(l for l, s in line_chs.items() if len(s) >= 5)
json.dump({"clone_lines": clone, "n_baseline_files": n_files, "min_ch": 5},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"baseline_files={n_files} clone_lines={len(clone)} -> {OUT}")
