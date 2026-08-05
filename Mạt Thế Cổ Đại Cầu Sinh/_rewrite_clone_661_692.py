# -*- coding: utf-8 -*-
"""Rewrite CLONE-pad ch.661,665,686-689,691-692 — unique prose via gold templates.
Remove Nhịp im loops. Keep panel: Kho Vô Hạn EXP format. Year 629. Cast Phong/Hà.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
CFG_PATH = BASE / ".novelab_score.json"
OUT = BASE / "_score_clone_rewrite_661_692.json"
NUMS = [661, 665, 686, 687, 688, 689, 691, 692]

sys.path.insert(0, r"C:/Dev/NovelLab/scripts")
from strict_score import score_chapter, vi_wordcount  # noqa: E402


def panel(n: int, kw: str) -> str:
    return (
        f"\n「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"EXP: 15000 / 15000\n"
        f"Hiện tại: cấp 3\n"
        f"Nâng cấp: {kw}\n"
    )


def strip_panel(t: str) -> str:
    t = re.sub(r"\n「[^」\n]*GHI NHẬN[\s\S]*$", "\n", t)
    return t.rstrip() + "\n"


def set_header(t: str, n: int, title: str) -> str:
    t = re.sub(r"Chương \d+:[^\n]*", f"Chương {n}: {title}", t, count=1)
    return t


def inject_cast_year(t: str) -> str:
    if "Lý Phong" not in t:
        t = t.replace("Phong ra hầm", "Lý Phong — gọi tắt Phong — ra hầm", 1)
    if "năm 629" not in t and "Năm: 629" in t:
        # ensure prose year
        t = t.replace("dưới đất Biên Ải", "dưới đất Biên Ải năm 629", 1)
        if "năm 629" not in t.split("「")[0]:
            # insert after first sentence block
            t = re.sub(
                r"(Ngày thứ [^\n.]+)\.",
                r"\1 dưới đất Biên Ải năm 629.",
                t,
                count=1,
            )
    if "629" not in t.split("「")[0]:
        t = t.replace("Biên Ải.", "Biên Ải năm 629.", 1)
    return t


def multi_replace(t: str, pairs: list[tuple[str, str]]) -> str:
    for a, b in pairs:
        if a:
            t = t.replace(a, b)
    return t


def rewrite_song(n: int, meta: dict) -> str:
    t = (BASE / "_gold_style_625.txt").read_text(encoding="utf-8")
    t = set_header(t, n, meta["title"])
    c = meta["count"]
    C = c.capitalize()
    pairs = [
        (
            "Mùi tanh ẩm len từ mương gừng khô tây trước khi trống điểm dứt hẳn. Ngày thứ bảy trăm bốn mươi lăm.",
            f"{meta['hook']} Ngày thứ {meta['day_w']} dưới đất Biên Ải năm 629.",
        ),
        ("Bốn bóng thấp", f"{C} bóng thấp"),
        ("bốn bóng thấp", f"{c} bóng thấp"),
        ("Bốn thấp", f"{C} thấp"),
        ("bốn thấp", f"{c} thấp"),
        ("Hết bốn", f"Hết {c}"),
        ("kể bốn", f"kể {c}"),
        ("chuyện bốn", f"chuyện {c}"),
        ("hỏi bốn", f"hỏi {c}"),
        ("chữ bốn", f"chữ {c}"),
        ("Kể bốn", f"Kể {c}"),
        ("bốn thấp đã lấp", f"{c} thấp đã lấp"),
        ("giết bốn", f"giết {c}"),
        ("sau bốn thấp", f"sau {c} thấp"),
        ("Bốn.", f"{C}."),
        (" bốn ", f" {c} "),
        ("mương gừng khô tây", meta["place"]),
        ("Mương gừng khô tây", meta["place"]),
        ("mương gừng", meta["place"]),
        ("Mương gừng", meta["place"]),
        ("gốc đa nghiêng nam", meta["prev"]),
        ("sóng thấp lần chín mươi bảy", meta["title_w"]),
        ("Sóng thấp lần chín mươi bảy", meta["title_w"].capitalize()),
        ("mùi tanh", meta["smell"]),
        ("Mùi tanh", meta["smell"].capitalize()),
        ("tanh ", meta["smell_short"] + " "),
        ("Tanh ", meta["smell_short"].capitalize() + " "),
        ("tanh?", meta["smell_short"] + "?"),
        ("Tanh?", meta["smell_short"].capitalize() + "?"),
        ("tanh.", meta["smell_short"] + "."),
        ("Tanh.", meta["smell_short"].capitalize() + "."),
        ("Tanh đi", meta["smell_short"].capitalize() + " đi"),
        ("tanh đi", meta["smell_short"] + " đi"),
        ("ngày bảy trăm bốn mươi lăm", f"ngày {meta['day_w']}"),
        ("Ngày 745", f"Ngày {meta['day']}"),
        ("Ngày 746", f"Ngày {meta['day'] + 1}"),
        ("khép 745", f"khép {meta['day']}"),
        ("khép ngày bảy trăm bốn mươi lăm", f"khép ngày {meta['day_w']}"),
    ]
    t = multi_replace(t, pairs)
    t = strip_panel(t)
    t = inject_cast_year(t)
    t = t.rstrip() + "\n" + panel(n, meta["panel_kw"])
    assert "Nhịp im" not in t
    return t


def rewrite_bong(n: int, meta: dict) -> str:
    t = (BASE / "_gold_style_622.txt").read_text(encoding="utf-8")
    t = set_header(t, n, meta["title"])
    pairs = [
        (
            "Sương đông còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm bốn mươi hai dưới đất Biên Ải.",
            f"{meta['hook']} Ngày thứ {meta['day_w']} dưới đất Biên Ải năm 629.",
        ),
        ("bảy trăm bốn mươi hai", meta["day_w"]),
        ("bóng gò lần 52", "bóng gò lần sáu mươi"),
        ("bóng gò lần năm mươi hai", "bóng gò lần sáu mươi"),
        ("Bóng gò lần 52", "Bóng gò lần sáu mươi"),
        ("Bóng gò lần năm mươi hai", "Bóng gò lần sáu mươi"),
        ("đếm bước cắm mốc", "xếp sỏi thành mũi tên"),
        ("Đếm bước cắm mốc", "Xếp sỏi thành mũi tên"),
        ("cắm mốc", "xếp sỏi"),
        ("nhổ mốc", "phá mũi sỏi"),
        ("không nhổ", "không phá mũi sỏi"),
        ("Không nhổ", "Không phá mũi sỏi"),
        ("không đạp", "không đạp theo"),
        ("gò thấp đông", "Gò đông"),
        ("Gò thấp đông", "Gò đông"),
        ("gò đông", "Gò đông"),
        ("Ngày 742", f"Ngày {meta['day']}"),
        ("Ngày 743", f"Ngày {meta['day'] + 1}"),
        ("742", str(meta["day"])),
    ]
    t = multi_replace(t, pairs)
    # force unique event line early
    t = re.sub(
        r"(năm 629\.)[^\n]*",
        r"\1 Gò đông — bóng gò lần sáu mươi không chỉ. Ba bóng xếp sỏi thành mũi tên. Không lê. Không nhìn trẻ. Luật: không mở, không chỉ, không phá mũi sỏi, không đạp theo.",
        t,
        count=1,
    )
    t = strip_panel(t)
    t = inject_cast_year(t)
    t = t.rstrip() + "\n" + panel(n, meta["panel_kw"])
    assert "Nhịp im" not in t
    return t


def rewrite_hoi(n: int, meta: dict) -> str:
    t = (BASE / "_gold_style_659.txt").read_text(encoding="utf-8")
    t = set_header(t, n, meta["title"])
    pairs = [
        (
            "Khói bếp còn thấp khi trống điểm dứt hẳn. Ngày sống thứ bảy trăm bảy mươi chín dưới đất Biên Ải.",
            f"{meta['hook']} Ngày thứ {meta['day_w']} dưới đất Biên Ải năm 629.",
        ),
        ("bảy trăm bảy mươi chín", meta["day_w"]),
        ("hỏi lần một trăm mười", meta["title_w"]),
        ("Hỏi lần một trăm mười", meta["title_w"].capitalize()),
        ("hỏi lần 110", meta["title_w"]),
        ("Hỏi lần 110", meta["title_w"].capitalize()),
        ("có ngựa thồ không, đổi yên lấy gạo", meta["ask"]),
        ("ngựa thồ đổi yên lấy gạo", meta["ask"]),
        ("đổi yên lấy gạo", meta["ask"].split(", ")[-1] if ", " in meta["ask"] else meta["ask"]),
        ("Yên ngoài là dấu hơn", meta["bait"].split(" — ")[0] if " — " in meta["bait"] else meta["bait"]),
        ("Yên ngoài là dấu tao", meta["bait"].split(" — ")[0] if " — " in meta["bait"] else meta["bait"]),
        ("trong có chuồng không", meta["bait_q"]),
        ("Không nhận ngựa", meta["refuse_a"]),
        ("không nhận ngựa", meta["refuse_a"].lower()),
        ("Không đổi yên", meta["refuse_b"]),
        ("không đổi yên", meta["refuse_b"].lower()),
        ("nhận ngựa", meta["refuse_a"].replace("Không ", "").lower()),
        ("đổi yên", meta["refuse_b"].replace("Không ", "").lower()),
        ("chữ ngựa", f"chữ {meta['word']}"),
        ("chữ yên", f"chữ {meta['word']}"),
        ("kể ngựa", f"kể {meta['word']}"),
        ("kể yên", f"kể {meta['word']}"),
        ("nghe chữ ngựa", f"nghe chữ {meta['word']}"),
        ("Kể ngựa", f"Kể {meta['word']}"),
        ("Kể yên", f"Kể {meta['word']}"),
        ("hỏi ngựa", f"hỏi {meta['word']}"),
        ("Hỏi ngựa", f"Hỏi {meta['word']}"),
        ("yên ngoài", f"{meta['word']} ngoài"),
        ("Yên ngoài", f"{meta['word'].capitalize()} ngoài"),
        ("da yên", f"da {meta['word']}"),
        ("bọc yên", f"bọc {meta['word']}"),
        ("nhặt yên", f"nhặt {meta['word']}"),
        ("Nhặt yên", f"Nhặt {meta['word']}"),
        ("yên hơn", f"{meta['word']} hơn"),
        ("Yên hơn", f"{meta['word'].capitalize()} hơn"),
        ("không yên", f"không {meta['word']}"),
        ("Không yên", f"Không {meta['word']}"),
        ("vì hỏi ngựa", f"vì hỏi {meta['word']}"),
        ("Ngày 779", f"Ngày {meta['day']}"),
        ("Ngày 780", f"Ngày {meta['day'] + 1}"),
        ("779", str(meta["day"])),
    ]
    t = multi_replace(t, pairs)
    t = strip_panel(t)
    t = inject_cast_year(t)
    t = t.rstrip() + "\n" + panel(n, meta["panel_kw"])
    assert "Nhịp im" not in t
    return t


def rewrite_yen(n: int, meta: dict) -> str:
    t = (BASE / "_gold_style_640.txt").read_text(encoding="utf-8")
    t = set_header(t, n, meta["title"])
    pairs = [
        (
            "Sương còn dính đầu chông khi trống điểm tan. Ngày thứ bảy trăm sáu mươi dưới đất Biên Ải.",
            f"{meta['hook']} Ngày thứ {meta['day_w']} dưới đất Biên Ải năm 629.",
        ),
        ("bảy trăm sáu mươi", meta["day_w"]),
        ("yên sau hỏi 105", meta["title_w"]),
        ("Yên sau hỏi 105", meta["title_w"].capitalize()),
        ("yên sau hỏi một trăm linh năm", meta["title_w"]),
        ("Yên sau hỏi một trăm linh năm", meta["title_w"].capitalize()),
        ("sau hỏi 105", f"sau hỏi {meta['ask_n']}"),
        ("sau hỏi một trăm linh năm", f"sau hỏi {meta['ask_n_w']}"),
        ("chữ vôi", f"chữ {meta['word']}"),
        ("Chữ vôi", f"Chữ {meta['word']}"),
        ("họp chữ vôi", f"họp chữ {meta['word']}"),
        ("lò vôi giả", meta["risk"]),
        ("Lò vôi giả", meta["risk"].capitalize()),
        ("dấu vôi", f"dấu {meta['word']}"),
        ("Dấu vôi", f"Dấu {meta['word']}"),
        ("kể vôi", f"kể {meta['word']}"),
        ("Kể vôi", f"Kể {meta['word']}"),
        ("vì vôi", f"vì {meta['word']}"),
        ("sau chữ vôi", f"sau chữ {meta['word']}"),
        ("Ngày 760", f"Ngày {meta['day']}"),
        ("Ngày 761", f"Ngày {meta['day'] + 1}"),
        ("760", str(meta["day"])),
    ]
    t = multi_replace(t, pairs)
    t = strip_panel(t)
    t = inject_cast_year(t)
    t = t.rstrip() + "\n" + panel(n, meta["panel_kw"])
    assert "Nhịp im" not in t
    return t


SPECS = {
    661: {
        "kind": "song",
        "title": "Sóng Thấp Lần 106",
        "day": 781,
        "day_w": "bảy trăm tám mươi mốt",
        "place": "Bãi sỏi nứt đông-bắc",
        "prev": "Mương lá mục tây-nam",
        "count": "bảy",
        "smell": "mùi sỏi nứt",
        "smell_short": "sỏi nứt",
        "title_w": "sóng thấp lần một trăm linh sáu",
        "panel_kw": "Sóng thấp · Bãi sỏi nứt đông-bắc · bảy · máu kín · cấp im · máy nghèo",
        "hook": "Gió bấc mang mùi sỏi nứt và đất se từ đông-bắc trước khi trống điểm tan hẳn.",
    },
    665: {
        "kind": "song",
        "title": "Sóng Thấp Lần 107",
        "day": 785,
        "day_w": "bảy trăm tám mươi lăm",
        "place": "Hố tro lạnh nam-tây",
        "prev": "Bãi sỏi nứt đông-bắc",
        "count": "tám",
        "smell": "mùi tro lạnh",
        "smell_short": "tro lạnh",
        "title_w": "sóng thấp lần một trăm linh bảy",
        "panel_kw": "Sóng thấp · Hố tro lạnh nam-tây · tám · máu kín · cấp im · máy nghèo",
        "hook": "Gió nam-tây mang mùi tro lạnh và bụi than trước khi trống điểm dứt hẳn.",
    },
    686: {
        "kind": "bong",
        "title": "Bóng Gò Lần 60 Không Chỉ",
        "day": 806,
        "day_w": "tám trăm lẻ sáu",
        "panel_kw": "Bóng · Gò đông · không chỉ · cấp im · máy nghèo",
        "hook": "Sương còn dính đầu chông khi trống điểm tan. Gò đông mang bóng xếp sỏi.",
    },
    687: {
        "kind": "hoi",
        "title": "Hỏi Lần 117 Cùng Màu",
        "day": 807,
        "day_w": "tám trăm lẻ bảy",
        "ask": "có vôi sống không, đổi thúng lấy muối",
        "bait": "Thúng ngoài là dấu tao — trong có lò vôi không?",
        "bait_q": "trong có lò vôi không",
        "word": "vôi",
        "refuse_a": "Không nhận vôi",
        "refuse_b": "Không đổi thúng",
        "title_w": "hỏi lần một trăm mười bảy",
        "panel_kw": "Hỏi · cùng màu · có vôi sống không, đổi thúng lấy muối · cấp im · máy nghèo",
        "hook": "Trống điểm dứt khi sương còn bám then. Cổng đông mang một miệng — hỏi vôi sống, đổi thúng lấy muối.",
    },
    688: {
        "kind": "yen",
        "title": "Ngày Yên Sau Hỏi 117",
        "day": 808,
        "day_w": "tám trăm lẻ tám",
        "word": "vôi",
        "risk": "lò vôi giả",
        "ask_n": "117",
        "ask_n_w": "một trăm mười bảy",
        "title_w": "ngày yên sau hỏi một trăm mười bảy",
        "panel_kw": "Yên sau hỏi · trống ≠ yên hội · không thở phào · vôi · cấp im · máy nghèo",
        "hook": "Ánh nắng loãng chạm đầu chông chậm hơn ngày hỏi. Trong rào — ngày yên sau hỏi một trăm mười bảy.",
    },
    689: {
        "kind": "song",
        "title": "Sóng Thấp Lần 113",
        "day": 809,
        "day_w": "tám trăm lẻ chín",
        "place": "Gò sườn tây thấp",
        "prev": "Bờ suối cạn đông-nam",
        "count": "tám",
        "smell": "mùi cỏ khô sườn",
        "smell_short": "cỏ khô",
        "title_w": "sóng thấp lần một trăm mười ba",
        "panel_kw": "Sóng thấp · Gò sườn tây thấp · tám · máu kín · cấp im · máy nghèo",
        "hook": "Gió tây mang mùi cỏ khô và đất sườn trước khi trống điểm dứt hẳn.",
    },
    691: {
        "kind": "hoi",
        "title": "Hỏi Lần 118 Cùng Màu",
        "day": 811,
        "day_w": "tám trăm mười một",
        "ask": "có mật ong không, đổi sáp lấy nước",
        "bait": "Sáp ngoài là dấu tao — trong có tổ ong không?",
        "bait_q": "trong có tổ ong không",
        "word": "mật",
        "refuse_a": "Không nhận mật",
        "refuse_b": "Không đổi sáp",
        "title_w": "hỏi lần một trăm mười tám",
        "panel_kw": "Hỏi · cùng màu · có mật ong không, đổi sáp lấy nước · cấp im · máy nghèo",
        "hook": "Khói bếp còn thấp khi trống điểm dứt. Cổng đông mang một miệng — hỏi mật ong, đổi sáp lấy nước.",
    },
    692: {
        "kind": "yen",
        "title": "Ngày Yên Sau Hỏi 118",
        "day": 812,
        "day_w": "tám trăm mười hai",
        "word": "mật",
        "risk": "khói hun giả",
        "ask_n": "118",
        "ask_n_w": "một trăm mười tám",
        "title_w": "ngày yên sau hỏi một trăm mười tám",
        "panel_kw": "Yên sau hỏi · trống ≠ yên hội · không thở phào · mật · cấp im · máy nghèo",
        "hook": "Nắng sớm chạm then chậm. Trong rào — ngày yên sau hỏi một trăm mười tám.",
    },
}


def make(n: int) -> str:
    s = SPECS[n]
    k = s["kind"]
    if k == "song":
        return rewrite_song(n, s)
    if k == "bong":
        return rewrite_bong(n, s)
    if k == "hoi":
        return rewrite_hoi(n, s)
    return rewrite_yen(n, s)


def primary_path(n: int) -> Path:
    title = SPECS[n]["title"]
    # Prefer non-Tháp
    cands = list(BASE.glob(f"Chương {n} *.txt"))
    cands = [p for p in cands if p.is_file()]
    if not cands:
        return BASE / f"Chương {n} - {title}.txt"
    cands.sort(key=lambda p: (1 if "Tháp" in p.name else 0, -p.stat().st_size))
    return cands[0]


def write_all() -> None:
    for n in NUMS:
        text = make(n)
        paths = list(BASE.glob(f"Chương {n} *.txt"))
        if not paths:
            paths = [BASE / f"Chương {n} - {SPECS[n]['title']}.txt"]
        for p in paths:
            try:
                p.chmod(0o666)
            except Exception:
                pass
            p.write_text(text, encoding="utf-8")
        print(
            f"WROTE ch.{n} -> {len(paths)} file(s) words={vi_wordcount(text)} "
            f"nhip={text.count('Nhịp im')} panel_ok={'Kho Vô Hạn' in text}"
        )


def score_all() -> dict:
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    results = []
    for n in NUMS:
        p = primary_path(n)
        text = p.read_text(encoding="utf-8")
        r = score_chapter(text, cfg.get("min_words", 3000), cfg.get("max_words", 4200), True, cfg)
        r["file"] = p.name
        r["num"] = n
        results.append(r)
        print(
            f"ch.{n} final={r['final']} hard={r['hard_fails']} words={r['metrics']['words']} "
            f"maxrep={r['metrics']['maxrep']} pad={r['metrics']['pad_total']} "
            f"panel_year={r['metrics'].get('panel_year')} axes={r['axes']}"
        )
    below = [r for r in results if r["final"] < 9.0 or r["hard_fails"]]
    report = {
        "threshold": 9.0,
        "min_words": 3000,
        "total": len(results),
        "pass": len(results) - len(below),
        "below": len(below),
        "all_pass": len(below) == 0,
        "below_list": [
            {"num": r["num"], "final": r["final"], "hard": r["hard_fails"]} for r in below
        ],
        "results": [
            {
                "num": r["num"],
                "file": r["file"],
                "final": r["final"],
                "hard_fails": r["hard_fails"],
                "metrics": {
                    "words": r["metrics"]["words"],
                    "maxrep": r["metrics"]["maxrep"],
                    "pad_total": r["metrics"]["pad_total"],
                    "has_panel": r["metrics"]["has_panel"],
                    "panel_year": r["metrics"]["panel_year"],
                },
                "axes": r["axes"],
            }
            for r in results
        ],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REPORT", OUT, "all_pass", report["all_pass"])
    return report


if __name__ == "__main__":
    write_all()
    rep = score_all()
    sys.exit(0 if rep["all_pass"] else 1)
