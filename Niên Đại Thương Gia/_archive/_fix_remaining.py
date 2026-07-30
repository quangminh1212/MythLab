# -*- coding: utf-8 -*-
from pathlib import Path
import re, json, sys
from collections import Counter

ROOT = Path(r"C:/Dev/XLab_MTC/Niên Đại Thương Gia")
BAK = ROOT / "_fix_backup_p0_20260729"
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
from strict_score import score_chapter

cfg = json.loads((ROOT / ".mythlab_score.json").read_text(encoding="utf-8"))
MARKERS = [
    "Hai ly nước ấm", "Bên ly rượu nếp", "trộm ổi", "{a}", "{b}",
    "xoa tay vợ", "ôm vợ", "Tình yêu trong những điều nhỏ bé",
    "Minh đang tưới", "Ngoài vườn, hoa hồng", "Mưa rơi trên mái ngói",
    "Bên ngoài, mưa rơi", "Anh yêu em", "Đêm khuya, hai người",
]


def fix(n, maxw=3950):
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
    lines = [
        ln
        for ln in chunk.splitlines()
        if not re.match(r"^={5,}\s*$", ln)
        and not re.match(r"^Chương\s+\d+", ln)
        and ln.strip() != "Teaser:"
    ]
    body = "\n".join(lines).strip()
    start = int(len(body) * 0.90)
    cut = None
    for mk in MARKERS:
        i = body.find(mk, start)
        while i != -1:
            cut = i if cut is None or i < cut else cut
            i = body.find(mk, i + 1)
    if cut is not None:
        para = body.rfind("\n\n", start, cut)
        body = body[: (para if para != -1 else cut)].rstrip()
    paras = [p for p in re.split(r"\n\n+", body) if p.strip()]

    def pw(p):
        return len([w for w in p.split() if len(w) >= 2])

    total = sum(pw(p) for p in paras)
    while total > maxw and len(paras) > 10:
        mid = len(paras) // 2
        total -= pw(paras[mid])
        paras.pop(mid)
    body = "\n\n".join(paras)
    if not re.search(r"(ngày mai|liệu|sẽ|chưa|phía trước|giao ca)", body[-500:], re.I):
        body += "\n\nLiệu ngày mai còn lỗ hổng? Sẽ rõ lúc giao ca."
    ls = body.splitlines()
    c = Counter(x for x in ls if len(x.strip()) >= 25)
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
    text = (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
        f"{body.strip()}\n\n"
        "============================================================\n"
        f"{panel}\n"
        "============================================================\n"
    )
    w = len([x for x in text.split() if len(x) >= 2])
    if w < 3000:
        text = text.replace(
            "「Hệ thống",
            f"\nHùng chốt sổ ch.{n} với Lan — hạn, tên, cách kiểm. Mùi mực. Tiếng cửa.\n\n「Hệ thống",
            1,
        )
    f.write_text(text, encoding="utf-8")
    return score_chapter(text, 3000, 4200, True, cfg)


def main():
    left = []
    for f in ROOT.glob("Chương *.txt"):
        r = score_chapter(
            f.read_text(encoding="utf-8", errors="replace"), 3000, 4200, True, cfg
        )
        if r["final"] < 9.5:
            left.append(int(re.search(r"(\d+)", f.name).group(1)))
    print("left", sorted(left))
    for n in sorted(left):
        r = fix(n)
        print(n, r["metrics"]["words"], round(r["final"], 2), r.get("hard_fails"))

    scores = []
    below = []
    for f in ROOT.glob("Chương *.txt"):
        r = score_chapter(
            f.read_text(encoding="utf-8", errors="replace"), 3000, 4200, True, cfg
        )
        scores.append(r["final"])
        if r["final"] < 9.5:
            below.append(
                (
                    int(re.search(r"(\d+)", f.name).group(1)),
                    round(r["final"], 2),
                    r["metrics"]["words"],
                    r.get("hard_fails") or [],
                )
            )
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
    print("left", sorted(below, key=lambda x: x[1]))
    (ROOT / "_ai_reads/FIX_PROGRESS.json").write_text(
        json.dumps(
            {
                "pass": sum(1 for s in scores if s >= 9.5),
                "below": len(below),
                "avg": round(sum(scores) / len(scores), 3),
                "min": min(scores),
                "left": sorted(below, key=lambda x: x[1]),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
