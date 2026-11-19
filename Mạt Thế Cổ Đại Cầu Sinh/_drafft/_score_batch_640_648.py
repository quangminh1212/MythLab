# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Dev\NovelLab\scripts")
import strict_score as ss

BASE = Path(r"C:\Dev\MythLab\Mạt Thế Cổ Đại Cầu Sinh")
cfg = json.loads((BASE / ".mythlab_score.json").read_text(encoding="utf-8"))
nums = [640, 641, 643, 644, 645, 646, 647, 648]
results = []
for n in nums:
    f = list(BASE.glob(f"Chương {n} - *.txt"))[0]
    t = f.read_text(encoding="utf-8")
    r = ss.score_chapter(t, cfg.get("min_words", 3000), cfg.get("max_words", 4200), True, cfg)
    row = {
        "num": n,
        "file": f.name,
        "final": r["final"],
        "axes": r["axes"],
        "hard_fails": r.get("hard_fails", []),
        "words": r["metrics"]["words"],
        "maxrep": r["metrics"]["maxrep"],
        "maxrep_short": r["metrics"]["maxrep_short"],
        "pad_total": r["metrics"]["pad_total"],
        "dialogue": r["metrics"]["dialogue"],
        "sensory_density": r["metrics"]["sensory_density"],
        "has_panel": r["metrics"]["has_panel"],
        "panel_year": r["metrics"]["panel_year"],
        "top_rep": r["metrics"]["top_rep"][:3],
        "pass": r["final"] >= 9.0 and not r.get("hard_fails"),
    }
    results.append(row)
    print(
        f"{n} final={row['final']} words={row['words']} maxrep={row['maxrep']} "
        f"pad={row['pad_total']} hf={row['hard_fails']} pass={row['pass']}"
    )
    if row["maxrep"] >= 2:
        print("  top:", row["top_rep"][:2])

out = {
    "threshold": 9.0,
    "min_words": 3000,
    "total": len(results),
    "pass": sum(1 for x in results if x["pass"]),
    "below": sum(1 for x in results if not x["pass"]),
    "avg": round(sum(x["final"] for x in results) / len(results), 2),
    "all_pass": all(x["pass"] for x in results),
    "results": results,
}
(BASE / "_score_clone_rewrite_640_648.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("ALL_PASS" if out["all_pass"] else "NEED_FIX", "avg", out["avg"])
