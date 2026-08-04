# -*- coding: utf-8 -*-
"""Pre-score gate: fail if not exactly one Chương file per 1..1000 with body >= min_words.

Exit 0 = clean (safe to run full strict_score).
Exit 1 = offenders printed; do NOT score.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, r"C:/Dev/NovelLab/scripts")
import strict_score as ss

ROOT = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
MIN_WORDS = 3000
TARGET = 1000


def main() -> int:
    by: dict[int, list[Path]] = defaultdict(list)
    for f in ROOT.glob("Chương *.txt"):
        m = re.match(r"Chương\s+(\d+)", f.name)
        if not m:
            print(f"OFFENDER no_chapter_num: {f.name}")
            continue
        by[int(m.group(1))].append(f)

    offenders: list[str] = []
    total = sum(len(v) for v in by.values())
    if total != TARGET:
        offenders.append(f"total_files={total} expected={TARGET}")
    if len(by) != TARGET:
        offenders.append(f"unique_nums={len(by)} expected={TARGET}")

    missing = [i for i in range(1, TARGET + 1) if i not in by]
    if missing:
        offenders.append(f"missing={missing[:20]}{'...' if len(missing) > 20 else ''}")

    dups = {k: v for k, v in by.items() if len(v) > 1}
    for n, files in sorted(dups.items()):
        names = ", ".join(p.name for p in files)
        offenders.append(f"dup ch.{n}: {names}")

    short: list[str] = []
    for n in range(1, TARGET + 1):
        files = by.get(n) or []
        if len(files) != 1:
            continue
        p = files[0]
        text = p.read_text(encoding="utf-8", errors="replace")
        body_w = ss.vi_wordcount(ss._body(text))
        if body_w < MIN_WORDS:
            short.append(f"short ch.{n} words={body_w} file={p.name}")

    offenders.extend(short)

    if offenders:
        print("GATE_FAIL")
        for o in offenders:
            print(" ", o)
        print(f"summary: total={total} unique={len(by)} dups={len(dups)} short={len(short)}")
        return 1

    print(f"GATE_OK total={total} unique={len(by)} dups=0 short=0 min_words>={MIN_WORDS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
