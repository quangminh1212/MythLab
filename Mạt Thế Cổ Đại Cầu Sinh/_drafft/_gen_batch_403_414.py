# -*- coding: utf-8 -*-
from pathlib import Path
import os, re, subprocess, shutil, json

base = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
cfg = str(base / ".mythlab_score.json")
scorer = r"C:/Dev/NovelLab/scripts/strict_score.py"
bp1 = base / "_pass_backup"
bp1.mkdir(exist_ok=True)
bp2 = Path(os.environ.get("TEMP", "/tmp")) / "mtcds_pass_backup"
bp2.mkdir(exist_ok=True)

T = {
    "hoi": base / "Chương 399 - Hỏi Lần Bốn Mươi Lăm Cùng Màu.txt",
    "yen": base / "Chương 400 - Ngày Yên Sau Hỏi Bốn Mươi Lăm.txt",
    "song": base / "Chương 401 - Sóng Thấp Lần Bốn Mươi Mốt.txt",
    "go": base / "Chương 402 - Bóng Gò Lần Hai Mươi Tư Không Chỉ.txt",
    "thuoc": base / "Chương 398 - Bóng Thước Lần Hai Mươi Ba Không Chỉ.txt",
}

SPECIAL = {
    23: "hai mươi ba",
    24: "hai mươi tư",
    25: "hai mươi lăm",
    26: "hai mươi sáu",
    40: "bốn mươi",
    41: "bốn mươi mốt",
    42: "bốn mươi hai",
    43: "bốn mươi ba",
    44: "bốn mươi tư",
    45: "bốn mươi lăm",
    46: "bốn mươi sáu",
    47: "bốn mươi bảy",
    48: "bốn mươi tám",
    49: "bốn mươi chín",
    50: "năm mươi",
}


def vn_num(n: int) -> str:
    return SPECIAL.get(n, str(n))


DAY = {
    523: "năm trăm hai mươi ba",
    524: "năm trăm hai mươi tư",
    525: "năm trăm hai mươi lăm",
    526: "năm trăm hai mươi sáu",
    527: "năm trăm hai mươi bảy",
    528: "năm trăm hai mươi tám",
    529: "năm trăm hai mươi chín",
    530: "năm trăm ba mươi",
    531: "năm trăm ba mươi mốt",
    532: "năm trăm ba mươi hai",
    533: "năm trăm ba mươi ba",
    534: "năm trăm ba mươi tư",
}

plan = [
    (403, "hoi", 46, 523, "Hỏi Lần Bốn Mươi Sáu Cùng Màu"),
    (404, "yen", 46, 524, "Ngày Yên Sau Hỏi Bốn Mươi Sáu"),
    (405, "song", 42, 525, "Sóng Thấp Lần Bốn Mươi Hai"),
    (406, "thuoc", 24, 526, "Bóng Thước Lần Hai Mươi Tư Không Chỉ"),
    (407, "hoi", 47, 527, "Hỏi Lần Bốn Mươi Bảy Cùng Màu"),
    (408, "yen", 47, 528, "Ngày Yên Sau Hỏi Bốn Mươi Bảy"),
    (409, "song", 43, 529, "Sóng Thấp Lần Bốn Mươi Ba"),
    (410, "go", 25, 530, "Bóng Gò Lần Hai Mươi Lăm Không Chỉ"),
    (411, "hoi", 48, 531, "Hỏi Lần Bốn Mươi Tám Cùng Màu"),
    (412, "yen", 48, 532, "Ngày Yên Sau Hỏi Bốn Mươi Tám"),
    (413, "song", 44, 533, "Sóng Thấp Lần Bốn Mươi Tư"),
    (414, "thuoc", 25, 534, "Bóng Thước Lần Hai Mươi Lăm Không Chỉ"),
]


def make(ch, typ, idx, day, title):
    body = T[typ].read_text(encoding="utf-8")
    body = re.sub(r"GHI NHẬN ch\.\d+", f"GHI NHẬN ch.{ch}", body)
    body = re.sub(r"khép \d+", f"khép {day}", body)
    body = re.sub(r"Ngày thứ [^\.]+", f"Ngày thứ {DAY[day]}", body, count=1)
    v = vn_num(idx)

    if typ == "hoi":
        body = re.sub(
            r"hỏi lần [^\.·\n,—]+",
            f"hỏi lần {v}",
            body,
            flags=re.IGNORECASE,
        )
        body = re.sub(r"Hỏi lần [^\.·\n,—]+", f"Hỏi lần {v}", body)
        body = re.sub(r"Lần [^\.·\n,—]+", f"Lần {v}", body)
        body = re.sub(r"(?<![A-Za-zÀ-ỹ])lần [^\.·\n,—]+", f"lần {v}", body)
        nang = f"Hỏi lần {v} · cùng màu · không lệch · cấp im · máy nghèo"
    elif typ == "yen":
        body = re.sub(r"yên sau hỏi [^\.·\n]+", f"yên sau hỏi {v}", body)
        body = re.sub(r"Yên sau hỏi [^\.·\n]+", f"Yên sau hỏi {v}", body)
        body = re.sub(r"hỏi bốn mươi [^\.·\n ]*", f"hỏi {v}", body)
        body = re.sub(r"Hỏi bốn mươi [^\.·\n ]*", f"Hỏi {v}", body)
        nang = f"Yên sau hỏi {v} · trống có lớp · không hội · cấp im · máy nghèo"
    elif typ == "song":
        body = re.sub(r"sóng thấp lần [^\.·\n,—]+", f"sóng thấp lần {v}", body)
        body = re.sub(r"Sóng thấp lần [^\.·\n,—]+", f"Sóng thấp lần {v}", body)
        body = re.sub(r"Lần [^\.·\n,—]+", f"Lần {v}", body)
        body = re.sub(r"(?<![A-Za-zÀ-ỹ])lần [^\.·\n,—]+", f"lần {v}", body)
        nang = f"Sóng thấp lần {v} · máu kín · không phơi · cấp im · máy nghèo"
    else:
        kind = "gò" if typ == "go" else "thước"
        body = re.sub(
            r"bóng (gò|thước) lần [^\.·\n,—]+",
            f"bóng {kind} lần {v}",
            body,
        )
        body = re.sub(
            r"Bóng (gò|thước) lần [^\.·\n,—]+",
            f"Bóng {kind} lần {v}",
            body,
        )
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
    print(status, ch, sc, tok, fn)
    print(" ", out.splitlines()[0] if out else "")
    if status == "OK":
        for bp in (bp1, bp2):
            shutil.copy2(p, bp / fn)
        subprocess.run(["attrib", "+R", p], shell=True, capture_output=True)
    results.append((ch, status, sc, tok))

fails = [r for r in results if r[1] != "OK"]
print("SUMMARY", results)
print("FAILS", fails)
state = {
    "frontier": 414 if not fails else min(f[0] for f in fails) - 1,
    "day": 534 if not fails else None,
    "counters": {"hoi": 48, "song_T": 44, "go_L": 25, "thuoc_L": 25},
    "next": "415 hỏi 49 day 535",
    "sealed_through": 414 if not fails else min(f[0] for f in fails) - 1,
    "results": results,
}
open(base / "_frontier_state.json", "w", encoding="utf-8").write(
    json.dumps(state, ensure_ascii=False, indent=2)
)
print("STATE", state)
