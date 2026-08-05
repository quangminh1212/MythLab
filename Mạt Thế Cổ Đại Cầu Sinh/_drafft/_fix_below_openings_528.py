# -*- coding: utf-8 -*-
"""Fix BELOW chapters: unique openings, ch528 >=3000, no Nhịp im, keep Kho Vô Hạn panel."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, r"C:\Dev\NovelLab\scripts")
from strict_score import score_chapter, vi_wordcount, _body  # noqa: E402

BASE = Path(__file__).resolve().parent
cfg = json.loads((BASE / ".novelab_score.json").read_text(encoding="utf-8-sig"))

TARGETS = [
    824, 825, 826, 827, 828, 829, 839, 842, 843, 844,
    855, 858, 859, 860, 872, 874, 875, 876, 878, 528,
]

# Unique openings: first 12 tokens must differ across whole series.
# Avoid "Nhịp im". Keep era/cast: Phong, Hà, 629, Biên Ải + plot cues.
OPENINGS = {
    528: (
        "Cột rào đông kêu rít nửa nhịp then khi gió bấc quét qua khe vải gai. "
        "Lý Phong đứng dưới mái hầm tây, đếm nhịp then cổng: một — hai. Không ba. Không gào. "
        "Ngày yên sau hỏi bảy mươi bảy. Anh không thở phào."
    ),
    824: (
        "Muối còn chát đầu ngón khi rèm gai hầm tây hé muộn hơn cả mùi dầu cũ. "
        "Ngày thứ chín trăm bốn mươi tư dưới đất Biên Ải năm 629. "
        "Trong rào — ngày yên sau hỏi một trăm năm mươi mốt. "
        "Trống không bằng yên hội; sau chữ dầu, yên có thể là khoảng lùi mang đèn dụ; "
        "giữa trưa thoáng mùi bấc cháy ngoài rào nhưng không miệng. "
        "Luật trong xương: không thở phào, không mở rèm sớm, không rải vôi nghỉ, tai khe sau chữ dầu."
    ),
    825: (
        "Hơi tro lạnh xộc lên gáy khi Phong quỳ sát mép hố nam-tây trước sóng. "
        "Ngày thứ chín trăm bốn mươi lăm dưới đất Biên Ải năm 629. "
        "Hố tro lạnh nam-tây — sóng thấp lần một trăm bốn mươi bảy. "
        "Sáu bóng thấp từ hố tro lạnh nam-tây; không gào; chỉ sóng; máu phải kín; "
        "hố mới sát hố tro — không trùng bãi sỏi cũ."
    ),
    826: (
        "Vòng phấn trắng còn mờ trên bụi nam khi gió bấc kéo ngang như muối rơi. "
        "Ngày thứ chín trăm bốn mươi sáu dưới đất Biên Ải năm 629. "
        "Đường bụi nam — bóng thước lần bảy mươi bảy. "
        "Một bóng vẽ vòng phấn trên gò; không gào; không chỉ; A Minh suýt xóa vòng — Phong chặn bằng mắt. "
        "Luật trong xương: thấy, không chỉ, không xóa, không hô."
    ),
    827: (
        "Kim khâu lạnh trong túi Diễm khi trống điểm dứt và sương tây còn dính cổng đông. "
        "Ngày thứ chín trăm bốn mươi bảy dưới đất Biên Ải năm 629. "
        "Cổng đông — hỏi lần một trăm năm mươi hai. "
        "Một miệng hỏi có kim khâu không, đổi chỉ lấy gạo; giọng khàn nữ; "
        "Diễm có kim trong túi may — Phong ra hiệu giấu trước khi miệng thấy. "
        "Luật trong xương: đông thường, hầm xấu, không nhận kim, không đổi chỉ, cùng màu nếu phải đáp."
    ),
    828: (
        "Sợi chỉ rơi ngoài cổng còn dính bụi khi khói bếp thấp tan sau trống muộn. "
        "Ngày thứ chín trăm bốn mươi tám dưới đất Biên Ải năm 629. "
        "Trong rào — ngày yên sau hỏi một trăm năm mươi hai. "
        "Trống không bằng yên hội; sau chữ kim, yên có thể mang thợ may giả; "
        "sáng sớm thấy một sợi chỉ rơi ngoài cổng — không nhặt, phủ bụi. "
        "Luật trong xương: không thở phào, không nhặt chỉ lạ, không mở rèm sớm."
    ),
    829: (
        "Lá lau ướt dính tanh vào ống quần khi bảy bóng thấp len qua bụi đông. "
        "Ngày thứ chín trăm bốn mươi chín dưới đất Biên Ải năm 629. "
        "Bụi lau ướt đông — sóng thấp lần một trăm bốn mươi tám. "
        "Bảy bóng thấp từ bụi lau ướt đông; không gào; chỉ sóng; máu kín; "
        "lá lau dính tanh; chân thây vướng gốc lau — lợi dụng; không hô to."
    ),
    839: (
        "Mồi khô còn nồng trong túi Hạt khi sương mỏng dính đầu chông tan sớm. "
        "Ngày thứ chín trăm năm mươi chín dưới đất Biên Ải năm 629. "
        "Cổng đông — hỏi lần một trăm năm mươi lăm. "
        "Một miệng hỏi có đá lửa không, đổi mồi khô lấy nắm gạo; giọng khác lần trước; "
        "Hạt suýt há — Cúc bịt trước khi mồi lọt mắt trẻ. "
        "Luật trong xương: đông thường, không nhận đá lửa, không đổi mồi, cùng màu nếu phải đáp."
    ),
    842: (
        "Que đo nghiêng cắm dọc bụi đông như dấu thước lạ trước khi gió bấc kéo ngang. "
        "Ngày thứ chín trăm sáu mươi hai dưới đất Biên Ải năm 629. "
        "Đường bụi đông — bóng thước lần bảy mươi chín. "
        "Hai bóng cắm que đo nghiêng dọc bụi; không gào; không chỉ; A Minh suýt nhổ que — Phong chặn bằng mắt. "
        "Luật trong xương: thấy que lạ, không nhổ, không chỉ, không hô."
    ),
    843: (
        "Vải bố gấp nhỏ trong túi Diễm khi sương tây tan chậm hơn sương đông. "
        "Ngày thứ chín trăm sáu mươi ba dưới đất Biên Ải năm 629. "
        "Cổng đông — hỏi lần một trăm năm mươi sáu. "
        "Một miệng hỏi có vải bố không, đổi cói đan lấy nắm; giọng khàn nam; "
        "Diễm có vải vá trong túi — Phong ra hiệu giấu trước khi miệng thấy. "
        "Luật trong xương: đông thường, không nhận vải, không đổi cói, cùng màu nếu phải đáp."
    ),
    844: (
        "Sợi cói rơi ngoài cổng còn se khi khói bếp thấp tan sau trống muộn. "
        "Ngày thứ chín trăm sáu mươi tư dưới đất Biên Ải năm 629. "
        "Trong rào — ngày yên sau hỏi một trăm năm mươi sáu. "
        "Trống không bằng yên hội; sau chữ vải, yên có thể mang thợ đan giả; "
        "sáng sớm thấy một sợi cói rơi ngoài cổng — không nhặt, phủ bụi. "
        "Luật trong xương: không thở phào, không nhặt cói lạ, không mở rèm sớm."
    ),
    855: (
        "Bùa dây khô kêu khẽ trong túi khi sương mỏng dính đầu chông tan sớm. "
        "Ngày thứ chín trăm bảy mươi lăm dưới đất Biên Ải năm 629. "
        "Cổng đông — hỏi lần một trăm năm mươi chín. "
        "Một miệng hỏi có thầy mo không, đổi bùa dây lấy muối; giọng khác lần trước; "
        "Hạt suýt há — Cúc bịt trước khi bùa lọt mắt trẻ. "
        "Luật trong xương: đông thường, không nhận thầy mo, không đổi bùa, cùng màu nếu phải đáp."
    ),
    858: (
        "Bóng giả chết nằm sấp trên bụi đông-nam trước khi gió bấc kéo ngang như muối. "
        "Ngày thứ chín trăm bảy mươi tám dưới đất Biên Ải năm 629. "
        "Đường bụi đông-nam — bóng thước lần tám mươi mốt. "
        "Một bóng giả chết nằm sấp trên bụi; không gào; không chỉ; A Minh suýt ra lật — Phong chặn bằng mắt. "
        "Luật trong xương: thấy giả chết, không lật, không chỉ, không hô."
    ),
    859: (
        "Đục gỗ còn dính mùn trong xưởng Hứa khi sương tây tan chậm hơn sương đông. "
        "Ngày thứ chín trăm bảy mươi chín dưới đất Biên Ải năm 629. "
        "Cổng đông — hỏi lần một trăm sáu mươi. "
        "Một miệng hỏi có thợ đẽo không, đổi đục lấy nước; giọng khàn nam; "
        "Hứa có đục trong xưởng — Phong ra hiệu giấu trước khi miệng thấy. "
        "Luật trong xương: đông thường, không nhận thợ đẽo, không đổi đục, cùng màu nếu phải đáp."
    ),
    860: (
        "Mảnh đá đẽo rơi ngoài cổng còn bám bụi khi khói bếp thấp tan sau trống. "
        "Ngày thứ chín trăm tám mươi dưới đất Biên Ải năm 629. "
        "Trong rào — ngày yên sau hỏi một trăm sáu mươi. "
        "Trống không bằng yên hội; sau chữ đá, yên có thể mang thợ đá giả; "
        "sáng sớm thấy một mảnh đá đẽo rơi ngoài cổng — không nhặt, phủ bụi. "
        "Luật trong xương: không thở phào, không nhặt đá lạ, không mở rèm sớm."
    ),
    872: (
        "Mùi bấc khét thoáng qua rào khi nắng mỏng chạm đầu chông muộn hơn hôm dầu. "
        "Ngày thứ chín trăm chín mươi hai dưới đất Biên Ải năm 629. "
        "Trong rào — ngày yên sau hỏi một trăm sáu mươi ba. "
        "Trống không bằng yên hội; sau chữ dầu, yên có thể là khoảng lùi mang đèn dụ; "
        "giữa trưa thoáng mùi bấc khét ngoài rào nhưng không miệng. "
        "Luật trong xương: không thở phào, không mở rèm sớm, tai khe sau chữ dầu."
    ),
    874: (
        "Vòng phấn mới vẽ sát đường bụi nam trước khi gió bấc kéo ngang. "
        "Ngày thứ chín trăm chín mươi tư dưới đất Biên Ải năm 629. "
        "Đường bụi nam — bóng thước lần tám mươi ba. "
        "Một bóng vẽ vòng phấn trên gò sát đường bụi nam; không gào; không chỉ; không xóa vòng phấn; "
        "A Minh suýt chỉ — Phong chặn bằng mắt. "
        "Luật trong xương: thấy vòng lạ, không xóa, không chỉ, không hô."
    ),
    875: (
        "Chỉ nứt giơ cao ngoài cổng đông khi sương tây tan chậm hơn sương đông. "
        "Ngày thứ chín trăm chín mươi lăm dưới đất Biên Ải năm 629. "
        "Cổng đông — hỏi lần một trăm sáu mươi tư. "
        "Một miệng hỏi có kim khâu không, đổi chỉ lấy gạo; giọng khàn nam; giơ chỉ nứt; "
        "Diễm có kim trong túi — Phong ra hiệu giấu trước khi miệng thấy. "
        "Luật trong xương: đông thường, không nhận kim, không đổi chỉ, cùng màu nếu phải đáp."
    ),
    876: (
        "Sợi chỉ lạ dính bụi ngoài cổng khi khói bếp còn thấp sau trống điểm tan muộn. "
        "Ngày thứ chín trăm chín mươi sáu dưới đất Biên Ải năm 629. "
        "Trong rào — ngày yên sau hỏi một trăm sáu mươi tư. "
        "Trống không bằng yên hội; sau chữ kim, yên có thể mang thợ may giả; "
        "sáng sớm thấy một sợi chỉ rơi ngoài cổng — không nhặt, phủ bụi. "
        "Luật trong xương: không thở phào, không nhặt chỉ lạ, không mở rèm sớm."
    ),
    878: (
        "Mũi sỏi xếp thành mũi tên trên gò đông trước khi gió bấc mang mùi sỏi ướt. "
        "Ngày thứ chín trăm chín mươi tám dưới đất Biên Ải năm 629. "
        "Gò đông — bóng gò lần tám mươi ba. "
        "Ba bóng xếp sỏi thành mũi tên trên gò đông; không gào; không chỉ; không phá mũi sỏi; "
        "khép bằng chân bóng không ném đá. "
        "Luật trong xương: thấy mũi sỏi, không phá, không chỉ, không hô."
    ),
}

HEADER_RE = re.compile(r"(?s)^(={5,}\s*\nChương[^\n]*\n={5,}\s*\n+)(.*)$")


def find_file(ch: int) -> Path:
    files = list(BASE.glob(f"Chương {ch:03d}*.txt")) or list(BASE.glob(f"Chương {ch} - *.txt"))
    if not files:
        raise FileNotFoundError(ch)
    return files[0]


def opening12(text: str) -> str:
    m = HEADER_RE.match(text)
    body = m.group(2) if m else text
    return " ".join(body.split()[:12])


def main() -> None:
    # Pre-check collisions within new openings
    batch_ops: dict[str, int] = {}
    for ch, op_text in OPENINGS.items():
        op = " ".join(op_text.split()[:12])
        if op in batch_ops:
            raise SystemExit(f"COLLIDE within batch: ch{ch} vs ch{batch_ops[op]}: {op}")
        batch_ops[op] = ch

    # Existing series openings (non-target)
    used: dict[str, list[int]] = {}
    for p in BASE.glob("Chương *.txt"):
        m = re.match(r"Chương\s+(\d+)", p.name)
        if not m:
            continue
        n = int(m.group(1))
        if n in TARGETS:
            continue
        op = opening12(p.read_text(encoding="utf-8"))
        used.setdefault(op, []).append(n)

    for ch, op_text in OPENINGS.items():
        op = " ".join(op_text.split()[:12])
        if op in used:
            raise SystemExit(f"COLLIDE with series: ch{ch} -> {op} vs {used[op]}")

    results = []
    for ch in TARGETS:
        path = find_file(ch)
        raw = path.read_text(encoding="utf-8")
        if "Nhịp im" in raw:
            raw = raw.replace("Nhịp im", "nhịp việc")
        m = HEADER_RE.match(raw)
        if not m:
            raise RuntimeError(f"bad header {path.name}")
        header, body = m.group(1), m.group(2)
        body_s = body.lstrip("\n")
        parts = re.split(r"\n\s*\n", body_s, maxsplit=1)
        rest = parts[1] if len(parts) == 2 else ""
        new_first = OPENINGS[ch].strip()
        new_body = new_first + "\n\n" + rest.lstrip()
        text = header + new_body

        if ch == 528:
            marker = "tám góc việc trong rào đang tự chạy bằng tay người"
            extra = (
                "\n\nPhong dừng thêm một nhịp ở góc tường đông, nghe gió bấc mang mùi đất se "
                "lẫn mùi vải gai khô từ bao muối Hà vừa siết. Anh không gọi đó là yên hội. "
                "Chỉ thấy then cổng còn khít, cột đông còn dấu dây cũ, và tám góc việc trong rào "
                "đang tự chạy bằng tay người — không bằng khẩu hiệu. A Cường lùi nửa bước, gật. "
                "Đủ để bắt đầu giờ mới bằng cuốc, không bằng thở phào.\n\n"
            )
            if marker not in text and "「Kho Vô Hạn" in text:
                idx = text.rfind("「Kho Vô Hạn")
                text = text[:idx] + extra + text[idx:]

        if "「Kho Vô Hạn" not in text:
            print(f"WARN missing panel ch{ch}")
        if "Nhịp im" in text:
            text = text.replace("Nhịp im", "nhịp việc")

        path.write_text(text, encoding="utf-8")
        op = opening12(text)
        wc = vi_wordcount(_body(text))
        results.append((ch, path.name, op, wc))
        print(f"OK ch{ch}: words={wc} open12={op}")

    print("\n--- uniqueness check ---")
    all_ops: dict[str, list[str]] = {}
    for p in BASE.glob("Chương *.txt"):
        op = opening12(p.read_text(encoding="utf-8"))
        all_ops.setdefault(op, []).append(p.name)

    bad = False
    for ch, name, op, wc in results:
        files = all_ops.get(op, [])
        if len(files) > 1:
            print(f"DUP ch{ch}: {files}")
            bad = True
        if ch == 528 and wc < 3000:
            print(f"SHORT ch528: {wc}")
            bad = True
        if "Nhịp im" in (BASE / name).read_text(encoding="utf-8"):
            print(f"NHIP IM still in {name}")
            bad = True
    if not bad:
        print("All targets unique openings + ch528 length OK")

    print("\n--- score with series-wide dup_opening ---")
    openings_counter: Counter[str] = Counter()
    scored = []
    for p in BASE.glob("Chương *.txt"):
        t = p.read_text(encoding="utf-8")
        r = score_chapter(t, 3000, 4200, genre_has_system=True, cfg=cfg)
        r["file"] = p.name
        r["num"] = int(re.match(r"Chương\s+(\d+)", p.name).group(1))
        openings_counter[r["opening"]] += 1
        scored.append(r)

    for r in scored:
        if openings_counter[r["opening"]] > 1 and r["opening"]:
            if "dup_opening" not in r["hard_fails"]:
                r["hard_fails"].append("dup_opening")
            r["final"] = round(min(r["final"], 8.0), 2)

    print("TARGET SCORES:")
    below = []
    for ch in TARGETS:
        r = next(x for x in scored if x["num"] == ch)
        print(
            f"  ch{ch}: final={r['final']} hard={r['hard_fails']} "
            f"words={r['metrics']['words']}"
        )
        if r["final"] < 9.0:
            below.append(r)

    print(f"\nBelow among targets: {len(below)}")
    for r in below:
        print(r["num"], r["final"], r["hard_fails"], r.get("axes"))

    out = {
        "targets": [
            {
                "num": r["num"],
                "final": r["final"],
                "hard_fails": r["hard_fails"],
                "words": r["metrics"]["words"],
                "opening": r["opening"],
            }
            for r in scored
            if r["num"] in TARGETS
        ],
        "below_count": len(below),
    }
    (BASE / "_score_below_fixed.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if below:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
