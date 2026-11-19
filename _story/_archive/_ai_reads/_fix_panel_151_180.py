# -*- coding: utf-8 -*-
from pathlib import Path
import re
import json

ROOT = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")
led = json.loads((ROOT / "system_ledger.json").read_text(encoding="utf-8"))["chapters"]


def skills_str(L):
    sk = L.get("skills") or []
    if not sk:
        return "(xem ledger)"
    return ", ".join(sk[-3:])


def ensure_header(t, n, title):
    t = t.replace("\r\n", "\n")
    if t.startswith("\ufeff"):
        t = t[1:]
    body = t
    body = re.sub(r"^(={5,}\s*\n)+", "", body)
    body = re.sub(r"^Chương\s+\d+\s*[:：][^\n]*\n", "", body)
    body = re.sub(r"^(={5,}\s*\n)+", "", body)
    body = body.lstrip("\n")
    return (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n" + body
    )


def fix_panel(t, n):
    L = led[str(n)]
    y = L["year"]
    exp = L["exp_total"]
    sp = L["space_m2"]
    de = L.get("exp_delta", 0)
    ds = L.get("space_delta", 0)
    pi = t.find("「Hệ thống")
    body = t[:pi].rstrip() if pi >= 0 else t.rstrip()
    body = re.sub(r"\n={5,}\s*$", "", body)
    pe = f"{exp:,}"
    ps = f"{sp:,}"
    panel = (
        "\n\n============================================================\n"
        f"「Hệ thống — GHI NHẬN ch.{n}」\n"
        f"Năm: {y}\n"
        f"Tổng EXP: {pe} (+{de})\n"
        f"Không gian kho: {ps}m² (+{ds}m²)\n"
        f"Kỹ năng trọng yếu: {skills_str(L)}\n"
        f"Ghi chú: khóa nhịp ch.{n}\n"
        "============================================================\n"
    )
    return body + panel


def fix_wife_frames(t):
    reps = [
        (r"vợ ông Hùng", "mẹ ông Hùng"),
        (r"vợ Hùng", "mẹ Hùng"),
        (r"nhìn vợ", "nhìn mẹ"),
        (r"ôm vợ", "nắm tay mẹ"),
        (r"vợ ơi", "mẹ ơi"),
        (r"vợ anh", "mẹ anh"),
    ]
    for a, b in reps:
        t = re.sub(a, b, t)
    return t


def main():
    for n in [158, 162, 163, 166, 167, 168, 169, 171, 172, 173, 174, 175, 177, 179]:
        f = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
        t = f.read_text(encoding="utf-8", errors="replace")
        if n == 177:
            t = t.replace("Mở rộngnhà máy", "Mở rộng nhà máy")
            t = t.replace("Mở rộngnhà", "Mở rộng nhà")
        t = fix_wife_frames(t)
        m = re.search(r"Chương\s+\d+\s*[:：]\s*([^\n]+)", t)
        title = m.group(1).strip() if m else re.sub(r"^Chương \d+ - |\.txt$", "", f.name)
        title = title.replace("Mở rộngnhà", "Mở rộng nhà")
        t = ensure_header(t, n, title)
        t = fix_panel(t, n)
        f.write_text(t if t.endswith("\n") else t + "\n", encoding="utf-8")
        t2 = f.read_text(encoding="utf-8")
        L = led[str(n)]
        exp_ok = str(L["exp_total"]) in t2.replace(",", "")
        print(
            n,
            "w",
            len([x for x in t2.split() if len(x) >= 2]),
            "year",
            L["year"],
            "exp_ok",
            exp_ok,
            "panels",
            t2.count("「Hệ thống"),
        )


if __name__ == "__main__":
    main()
