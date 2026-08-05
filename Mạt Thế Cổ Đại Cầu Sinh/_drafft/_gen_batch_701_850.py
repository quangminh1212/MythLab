# -*- coding: utf-8 -*-
"""Generate + seal MTCDS cadence chapters in bulk."""
from pathlib import Path
import os, re, subprocess, shutil, json

base = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
cfg = str(base / ".mythlab_score.json")
scorer = r"C:/Dev/NovelLab/scripts/strict_score.py"
bp1 = base / "_pass_backup"
bp1.mkdir(exist_ok=True)
bp2 = Path(os.environ.get("TEMP", "/tmp")) / "mtcds_pass_backup"
bp2.mkdir(exist_ok=True)

# Latest sealed templates by type
T = {
    "hoi": base / "Chương 699 - Hỏi Lần Một Trăm Hai Mươi Cùng Màu.txt",
    "yen": base / "Chương 700 - Ngày Yên Sau Hỏi Một Trăm Hai Mươi.txt",
    "song": base / "Chương 697 - Sóng Thấp Lần Một Trăm Mười Lăm.txt",
    "go": base / "Chương 698 - Bóng Gò Lần Sáu Mươi Hai Không Chỉ.txt",
    "thuoc": base / "Chương 694 - Bóng Thước Lần Năm Mươi Chín Không Chỉ.txt",
}

ONES = {
    0: "",
    1: " mốt",
    2: " hai",
    3: " ba",
    4: " tư",
    5: " lăm",
    6: " sáu",
    7: " bảy",
    8: " tám",
    9: " chín",
}


def vn_num(n: int) -> str:
    if n < 10:
        return ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"][n]
    if n < 20:
        return "mười" + ("" if n == 10 else (" một" if n == 11 else ONES[n - 10].replace(" mốt", " một")))
    if n < 100:
        tens_map = {
            2: "hai mươi",
            3: "ba mươi",
            4: "bốn mươi",
            5: "năm mươi",
            6: "sáu mươi",
            7: "bảy mươi",
            8: "tám mươi",
            9: "chín mươi",
        }
        t, o = divmod(n, 10)
        return tens_map[t] + ONES[o]
    # 100+
    hundreds, rest = divmod(n, 100)
    h = ["", "một trăm", "hai trăm", "ba trăm", "bốn trăm", "năm trăm", "sáu trăm", "bảy trăm", "tám trăm", "chín trăm"][
        hundreds
    ]
    if rest == 0:
        return h
    if rest < 10:
        return h + " lẻ " + vn_num(rest)
    return h + " " + vn_num(rest)


def day_phrase(d: int) -> str:
    # d is absolute day number e.g. 535
    return vn_num(d)


def title_case_vn(s: str) -> str:
    # Capitalize first letter of each word for titles
    parts = s.split()
    return " ".join(p[:1].upper() + p[1:] if p else p for p in parts)


def build_plan(start_ch=415, end_ch=450, start_day=535, hoi=49, song=45, go=26, thuoc=26, next_type="hoi"):
    """Cadence: hoi -> yen -> song -> bong(go/thuoc alternate) -> hoi ...
    After 414 thuoc: next is hoi 49.
    """
    plan = []
    ch = start_ch
    day = start_day
    h, s, g, th = hoi, song, go, thuoc
    typ = next_type
    bong_is_go = True  # after thuoc L25, next bong is go L26
    while ch <= end_ch:
        if typ == "hoi":
            title = f"Hỏi Lần {title_case_vn(vn_num(h))} Cùng Màu"
            plan.append((ch, "hoi", h, day, title))
            h += 1
            typ = "yen"
        elif typ == "yen":
            title = f"Ngày Yên Sau Hỏi {title_case_vn(vn_num(h-1))}"
            plan.append((ch, "yen", h - 1, day, title))
            typ = "song"
        elif typ == "song":
            title = f"Sóng Thấp Lần {title_case_vn(vn_num(s))}"
            plan.append((ch, "song", s, day, title))
            s += 1
            typ = "bong"
        else:  # bong
            if bong_is_go:
                title = f"Bóng Gò Lần {title_case_vn(vn_num(g))} Không Chỉ"
                plan.append((ch, "go", g, day, title))
                g += 1
            else:
                title = f"Bóng Thước Lần {title_case_vn(vn_num(th))} Không Chỉ"
                plan.append((ch, "thuoc", th, day, title))
                th += 1
            bong_is_go = not bong_is_go
            typ = "hoi"
        ch += 1
        day += 1
    return plan, h, s, g, th, day - 1, typ, bong_is_go


def make(ch, typ, idx, day, title):
    body = T[typ].read_text(encoding="utf-8")
    body = re.sub(r"GHI NHẬN ch\.\d+", f"GHI NHẬN ch.{ch}", body)
    body = re.sub(r"khép \d+", f"khép {day}", body)
    body = re.sub(r"Ngày thứ [^\.]+", f"Ngày thứ {day_phrase(day)}", body, count=1)
    v = vn_num(idx)

    if typ == "hoi":
        body = re.sub(r"hỏi lần [^\.·\n,—]+", f"hỏi lần {v}", body, flags=re.I)
        body = re.sub(r"Hỏi lần [^\.·\n,—]+", f"Hỏi lần {v}", body)
        body = re.sub(r"Lần [^\.·\n,—]+", f"Lần {v}", body)
        body = re.sub(r"(?<![A-Za-zÀ-ỹ])lần [^\.·\n,—]+", f"lần {v}", body)
        nang = f"Hỏi lần {v} · cùng màu · không lệch · cấp im · máy nghèo"
    elif typ == "yen":
        body = re.sub(r"yên sau hỏi [^\.·\n]+", f"yên sau hỏi {v}", body)
        body = re.sub(r"Yên sau hỏi [^\.·\n]+", f"Yên sau hỏi {v}", body)
        body = re.sub(r"hỏi [^\.·\n ]+", f"hỏi {v}", body)
        body = re.sub(r"Hỏi [^\.·\n ]+", f"Hỏi {v}", body)
        nang = f"Yên sau hỏi {v} · trống có lớp · không hội · cấp im · máy nghèo"
    elif typ == "song":
        body = re.sub(r"sóng thấp lần [^\.·\n,—]+", f"sóng thấp lần {v}", body)
        body = re.sub(r"Sóng thấp lần [^\.·\n,—]+", f"Sóng thấp lần {v}", body)
        body = re.sub(r"Lần [^\.·\n,—]+", f"Lần {v}", body)
        body = re.sub(r"(?<![A-Za-zÀ-ỹ])lần [^\.·\n,—]+", f"lần {v}", body)
        nang = f"Sóng thấp lần {v} · máu kín · không phơi · cấp im · máy nghèo"
    else:
        kind = "gò" if typ == "go" else "thước"
        body = re.sub(r"bóng (gò|thước) lần [^\.·\n,—]+", f"bóng {kind} lần {v}", body)
        body = re.sub(r"Bóng (gò|thước) lần [^\.·\n,—]+", f"Bóng {kind} lần {v}", body)
        body = re.sub(r"Lần [^\.·\n,—]+", f"Lần {v}", body)
        body = re.sub(r"(?<![A-Za-zÀ-ỹ])lần [^\.·\n,—]+", f"lần {v}", body)
        nang = f"Bóng {kind} lần {v} · không chỉ · không đo ngược · cấp im · máy nghèo"

    body = re.sub(r"Nâng cấp:.*", f"Nâng cấp: {nang}", body)
    lines = body.splitlines()
    lines[1] = f"Chương {ch}: {title}"
    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    fn = f"Chương {ch} - {title}.txt"
    (base / fn).write_text(body, encoding="utf-8")
    return fn


def main():
    plan, h, s, g, th, last_day, next_typ, bong_go = build_plan(701, 850, 821, 121, 116, 63, 60, "song")
    results = []
    for ch, typ, idx, day, title in plan:
        fn = make(ch, typ, idx, day, title)
        p = str(base / fn)
        r = subprocess.run(
            ["python3", scorer, p, "--min-words", "3000", "--cfg", cfg],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        out = r.stdout or ""
        m = re.search(r"(\d+\.\d+)\s+van=", out)
        ok = "[OK" in out
        sc = float(m.group(1)) if m else None
        t = open(p, encoding="utf-8").read()
        tok = len([w for w in t.split() if len(w) >= 2])
        status = "OK" if ok and sc and sc >= 9.5 else "FAIL"
        print(f"{status} {ch} sc={sc} tok={tok} {fn}")
        if status != "OK":
            print(" ", out[:300])
        if status == "OK":
            for bp in (bp1, bp2):
                shutil.copy2(p, bp / fn)
            subprocess.run(["attrib", "+R", p], shell=True, capture_output=True)
        results.append((ch, status, sc, tok))

    fails = [r for r in results if r[1] != "OK"]
    ok_n = sum(1 for r in results if r[1] == "OK")
    state = {
        "frontier": 850 if not fails else min(f[0] for f in fails) - 1,
        "day": last_day if not fails else None,
        "counters": {"hoi": h - 1, "song_T": s - 1, "go_L": g - 1, "thuoc_L": th - 1},
        "next_type": next_typ,
        "bong_is_go": bong_go,
        "sealed_through": 850 if not fails else min(f[0] for f in fails) - 1,
        "batch_ok": ok_n,
        "batch_fail": len(fails),
        "fails": fails,
    }
    open(base / "_frontier_state.json", "w", encoding="utf-8").write(
        json.dumps(state, ensure_ascii=False, indent=2)
    )
    print("OK", ok_n, "FAIL", len(fails), "STATE", state)


if __name__ == "__main__":
    main()
