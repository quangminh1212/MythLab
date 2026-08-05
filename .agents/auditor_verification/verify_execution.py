# -*- coding: utf-8 -*-
import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')

target_dir = r"c:\Dev\XLab_MTC\Niên Đại Thương Gia"
sys.path.insert(0, target_dir)

import audit_all

score_file = os.path.join(target_dir, "score95_final.json")
with open(score_file, "r", encoding="utf-8") as f:
    saved_data = json.load(f)

saved_chapters = saved_data["chapters"]
print(f"Total saved chapters in score95_final.json: {len(saved_chapters)}")
print(f"Saved min_score: {saved_data.get('min_score')}, max_score: {saved_data.get('max_score')}, avg_score: {saved_data.get('avg_score')}")

mismatches = []
calculated_scores = []

for i in range(1, 361):
    comp = audit_all.audit_chapter(i)
    if not comp:
        mismatches.append(f"Ch {i}: audit_chapter returned None")
        continue
    
    calculated_scores.append(comp["score"])
    sav = next((c for c in saved_chapters if c["n"] == i), None)
    if not sav:
        mismatches.append(f"Ch {i}: missing in score95_final.json")
        continue
    
    keys = ["score", "prose", "plot", "char", "cont", "filler", "words", "maxrep", "sens_d", "char_d"]
    for k in keys:
        if comp.get(k) != sav.get(k):
            mismatches.append(f"Ch {i} metric {k}: calculated {comp.get(k)} vs saved {sav.get(k)}")

print(f"\nAudit complete. Total mismatches found: {len(mismatches)}")
if mismatches:
    print("Mismatches summary (first 30):")
    for m in mismatches[:30]:
        print("  -", m)
else:
    print("SUCCESS: Every score and metric in score95_final.json perfectly matches the live recalculation from text files!")

calc_min = min(calculated_scores)
calc_max = max(calculated_scores)
calc_avg = round(sum(calculated_scores) / len(calculated_scores), 2)
print(f"\nLive calculated metrics across all 360 chapters:")
print(f"  Min score: {calc_min}")
print(f"  Max score: {calc_max}")
print(f"  Avg score: {calc_avg}")
