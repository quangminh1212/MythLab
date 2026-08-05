#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Idempotent: one root file per chapter number 1..1000 (archive digit/VN-title twins)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SERIES = Path(__file__).resolve().parents[1]
ARCH = SERIES / "_dupe_archive"
PAT = re.compile(r"^Chương\s+(\d+)\s*[-–—]", re.I)


def scan() -> dict[int, list[Path]]:
    by: dict[int, list[Path]] = {}
    for p in SERIES.glob("Chương *.txt"):
        m = PAT.match(p.name)
        if not m:
            continue
        n = int(m.group(1))
        if 1 <= n <= 1000:
            by.setdefault(n, []).append(p)
    return by


def collapse() -> dict:
    ARCH.mkdir(exist_ok=True)
    by = scan()
    actions = []
    for n, files in sorted(by.items()):
        if len(files) < 2:
            continue
        scored = sorted(
            files,
            key=lambda p: (
                len(p.read_text(encoding="utf-8", errors="replace").split()),
                p.stat().st_size,
                p.stat().st_mtime,
            ),
            reverse=True,
        )
        for p in scored[1:]:
            dest = ARCH / p.name
            i = 2
            while dest.exists():
                dest = ARCH / f"{p.stem}__h{i}{p.suffix}"
                i += 1
            p.rename(dest)
            actions.append({"n": n, "archived": dest.name, "kept": scored[0].name})
    by2 = scan()
    missing = [i for i in range(1, 1001) if i not in by2]
    dupes = {k: [p.name for p in v] for k, v in by2.items() if len(v) > 1}
    total = sum(len(v) for v in by2.values())
    return {
        "archived": actions,
        "present": len(by2),
        "total_files": total,
        "missing": missing,
        "dupes": dupes,
        "ok": not missing and not dupes and len(by2) == 1000 and total == 1000,
    }


def main() -> int:
    rep = collapse()
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
