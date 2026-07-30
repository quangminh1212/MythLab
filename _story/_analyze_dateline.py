# -*- coding: utf-8 -*-
import json, glob, re

DIR = "C:/Dev/XLab_MTC/Niên Đại Thương Gia"
with open(f"{DIR}/_fix_year_targets.json", encoding="utf-8") as f:
    ym_map = json.load(f)

results = []
for ch_str, pair in sorted(ym_map.items(), key=lambda x: int(x[0])):
    panel_y, prose_y = pair
    ch = int(ch_str)
    files = glob.glob(f"{DIR}/Chương {ch} -*.txt")
    if not files:
        results.append({"ch": ch, "error": "file not found"})
        continue
    fname = files[0]
    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()

    body_start = 0
    eq = 0
    for i, l in enumerate(lines):
        if "====" in l:
            eq += 1
            if eq == 2:
                body_start = i + 1
                break

    first_yr_line_num = None
    first_yr = None
    for i in range(body_start, min(body_start + 15, len(lines))):
        l = lines[i]
        m = re.search(r"(19[3-9]\d|20[0-4]\d)", l)
        if m:
            first_yr_line_num = i
            first_yr = m.group()
            break

    results.append({
        "ch": ch, "file": fname, "panel": panel_y, "prose": prose_y,
        "body_start": body_start,
        "first_yr_line_num": first_yr_line_num,
        "first_yr": first_yr,
        "line_text": lines[first_yr_line_num].strip()[:120] if first_yr_line_num is not None else None,
    })

with open(f"{DIR}/_dateline_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for r in results:
    if "error" in r:
        print(f"Ch{r['ch']}: ERROR {r['error']}")
    else:
        print(f"Ch{r['ch']}: panel={r['panel']} prose={r['prose']} L{r['first_yr_line_num']} yr={r['first_yr']} :: {r['line_text']}")
