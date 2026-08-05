#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shipped-path inventory + score gate for Mạt Thế Cổ Đại Cầu Sinh (1–1000)."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

SERIES = Path(__file__).resolve().parents[1]
CH_RE = re.compile(r"^Chương\s+(\d+)\s*[-–—]", re.I)


class TestMTCDSInventory1000(unittest.TestCase):
    def test_chapters_1_through_1000_present_no_dupes(self):
        by: dict[int, list[str]] = {}
        for p in SERIES.glob("Chương *.txt"):
            m = CH_RE.match(p.name)
            if not m:
                continue
            n = int(m.group(1))
            if 1 <= n <= 1000:
                by.setdefault(n, []).append(p.name)
        missing = [i for i in range(1, 1001) if i not in by]
        dupes = {k: v for k, v in by.items() if len(v) > 1}
        total_files = sum(len(v) for v in by.values())
        self.assertEqual(missing, [], f"missing chapters: {missing[:20]}")
        self.assertEqual(dupes, {}, f"duplicate chapter files: {dupes}")
        self.assertEqual(len(by), 1000)
        self.assertEqual(total_files, 1000, "exactly one root file per chapter 1..1000")

    def test_strict_report_all_pass_at_95(self):
        rep_path = SERIES / "strict_report.json"
        self.assertTrue(rep_path.exists(), "strict_report.json missing — run autopilot_loop")
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
        self.assertTrue(rep.get("all_pass"), rep)
        self.assertEqual(rep.get("below"), 0)
        self.assertEqual(rep.get("total"), 1000)
        self.assertGreaterEqual(float(rep.get("min_final") or 0), 9.5)
        # report filenames must exist on disk (no stale paths after rename)
        for r in rep.get("results") or []:
            fp = Path(r.get("path") or "")
            if not fp.is_file():
                fp = SERIES / (r.get("file") or "")
            self.assertTrue(fp.is_file(), f"stale report path: {r.get('file')}")
        wl = SERIES / "worklist.json"
        if wl.exists():
            data = json.loads(wl.read_text(encoding="utf-8"))
            self.assertEqual(data.get("total_below", data.get("count", 0)), 0)

    def test_no_literal_backslash_n_in_headers(self):
        """Regression: ch152–204 once had 'Chương N: \\nChương N: Title\\n'."""
        bad = []
        for p in SERIES.glob("Chương *.txt"):
            head = p.read_text(encoding="utf-8", errors="replace")[:400]
            if "\\n" in head:  # literal backslash + n
                bad.append(p.name)
        self.assertEqual(bad, [], f"literal \\\\n in headers: {bad[:10]}")


if __name__ == "__main__":
    unittest.main()
