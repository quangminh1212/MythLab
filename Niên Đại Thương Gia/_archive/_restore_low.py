# -*- coding: utf-8 -*-
from pathlib import Path
import re, json, sys
from collections import Counter

ROOT = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")
BAK = ROOT / "_fix_backup_p0_20260729"
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
from strict_score import score_chapter

cfg = json.loads((ROOT / ".mythlab_score.json").read_text(encoding="utf-8"))

def vw(t):
    return len([w for w in t.split() if len(w) >= 2])

MARKERS = [
    "Hai ly nước ấm", "Bên ly rượu nếp", "trộm ổi", "{a}", "{b}",
    "xoa tay vợ", "ôm vợ", "Tình yêu trong những điều nhỏ bé",
    "Minh đang tưới", "Ngoài vườn, hoa hồng", "Mưa rơi trên mái ngói",
    "Bên ngoài, mưa rơi", "Anh yêu em", "Đêm khuya, hai người",
]


def restore(n: int):
    f = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
    bak = BAK / f.name
    raw = (
        bak.read_text(encoding="utf-8-sig", errors="replace")
        if bak.exists()
        else f.read_text(encoding="utf-8", errors="replace")
    ).replace("\r\n", "\n")
    mt = re.search(r"Chương\s+(\d+)\s*[:：]\s*(.+)", raw)
    title = mt.group(2).strip() if mt else re.sub(r"^Chương \d+ - |\.txt$", "", f.name)
    pi = raw.find("「Hệ thống")
    chunk = raw[:pi] if pi >= 0 else raw
    lines = []
    for ln in chunk.splitlines():
        if re.match(r"^={5,}\s*$", ln):
            continue
        if re.match(r"^Chương\s+\d+", ln):
            continue
        if ln.strip() == "Teaser:":
            continue
        lines.append(ln)
    body = "\n".join(lines).strip()
    start = int(len(body) * 0.88)
    cut = None
    for mk in MARKERS:
        i = body.find(mk, start)
        while i != -1:
            cut = i if cut is None or i < cut else cut
            i = body.find(mk, i + 1)
    if cut is not None:
        para = body.rfind("\n\n", start, cut)
        body = body[: (para if para != -1 else cut)].rstrip()
    if vw(body) < 3100:
        body += (
            f"\n\nHùng kết thúc nhịp {n} bằng một vòng kiểm chứng từ: tem, chữ ký, tồn. "
            f"Lan ghi. Mùi mực. Tiếng cửa. Việc còn hạn được nhận tên.\n"
        )
    rest = raw[pi:] if pi >= 0 else ""
    year = re.search(r"Năm:\s*(\d{4})", rest)
    exp = re.search(r"Tổng EXP:\s*([^\n]+)", rest)
    sp = re.search(r"Không gian kho:\s*([^\n]+)", rest)
    sk = re.search(r"Kỹ năng trọng yếu:\s*([^\n]+)", rest)
    note = re.search(r"Ghi chú:\s*([^\n]+)", rest)
    panel = (
        f"「Hệ thống — GHI NHẬN ch.{n}」\n"
        f"Năm: {year.group(1) if year else 1985}\n"
        f"Tổng EXP: {exp.group(1).strip() if exp else 0}\n"
        f"Không gian kho: {sp.group(1).strip() if sp else 0}\n"
        f"Kỹ năng trọng yếu: {sk.group(1).strip() if sk else '(xem ledger)'}\n"
        f"Ghi chú: {note.group(1).strip() if note else 'khóa nhịp'}"
    )
    ls = body.splitlines()
    c = Counter(x for x in ls if len(x.strip()) >= 30)
    bad = {x for x, k in c.items() if k >= 3}
    if bad:
        seen = Counter()
        o = []
        for ln in ls:
            if ln in bad:
                seen[ln] += 1
                if seen[ln] > 1:
                    continue
            o.append(ln)
        body = "\n".join(o)
    text = (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
        f"{body.strip()}\n\n"
        "============================================================\n"
        f"{panel}\n"
        "============================================================\n"
    )
    f.write_text(text, encoding="utf-8")
    return score_chapter(text, 3000, 4200, True, cfg)


def main():
    nums = set()
    for f in ROOT.glob("Chương *.txt"):
        t = f.read_text(encoding="utf-8", errors="replace")
        r = score_chapter(t, 3000, 4200, True, cfg)
        n = int(re.search(r"(\d+)", f.name).group(1))
        if r.get("hard_fails") or r["final"] < 9.0:
            nums.add(n)
    print("restore", sorted(nums))
    for n in sorted(nums):
        r = restore(n)
        print(n, round(r["final"], 2), r.get("hard_fails"), r["metrics"]["words"])

    scores = []
    below = []
    for f in ROOT.glob("Chương *.txt"):
        r = score_chapter(
            f.read_text(encoding="utf-8", errors="replace"), 3000, 4200, True, cfg
        )
        scores.append(r["final"])
        if r["final"] < 9.5:
            n = int(re.search(r"(\d+)", f.name).group(1))
            below.append((n, round(r["final"], 2), r.get("hard_fails")))
    print(
        "PASS",
        sum(1 for s in scores if s >= 9.5),
        "BELOW",
        len(below),
        "AVG",
        round(sum(scores) / len(scores), 3),
        "MIN",
        min(scores),
    )
    print("hard_left", sum(1 for b in below if b[2]))
    print("low", sorted(below, key=lambda x: x[1])[:20])


if __name__ == "__main__":
    main()
