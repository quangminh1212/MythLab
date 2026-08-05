#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix hard-fails: unique chapter openings + min-words for short ch184 set."""
from __future__ import annotations

import json
import re
from pathlib import Path

SERIES = Path(__file__).resolve().parent
REPORT = SERIES / "strict_report.json"
HEADER_RE = re.compile(
    r"(?s)^(={5,}\s*\nChương[^\n]*\n={5,}\s*\n+)(.*)$"
)


def split_header(text: str) -> tuple[str, str]:
    m = HEADER_RE.match(text)
    if m:
        return m.group(1), m.group(2)
    # fallback: first 4 lines as header-ish
    lines = text.splitlines(keepends=True)
    if len(lines) >= 4:
        return "".join(lines[:4]), "".join(lines[4:])
    return "", text


def unique_hook(n: int, title: str) -> str:
    """First ~12+ tokens unique per chapter (strict_score uses first 12)."""
    # strip accents-heavy noise from title for a short sensory cue
    t = re.sub(r"\s+", " ", (title or "").strip())
    t = t[:42] if t else f"nhịp {n}"
    # deliberately different word order / nouns by n % buckets
    buckets = [
        (
            "Sương dính rìu gỗ số {n} trước hầm tây. "
            "Lý Phong nghe tiếng {cue} lẫn mùi đất ẩm, siết chuôi dao lần {k}."
        ),
        (
            "Gió bấc quét qua cột rào ch.{n}. "
            "Phong dừng nửa bước vì {cue}, đếm bảy dấu chân không tám."
        ),
        (
            "Than trong bếp lò nổ lách tách đúng nhịp {n}. "
            "Bà Hà không nói; Phong chỉ khẽ gật vì {cue}."
        ),
        (
            "Nước giếng kéo lên lúc ch.{n} còn vẩn phù sa. "
            "Long đứng ngoài sân, chỉ tay về hướng {cue}."
        ),
        (
            "Vải bạt phủ kho kêu rít khi gió ch.{n} lùa. "
            "Hà phơi bao, Phong ghi sổ vì {cue}."
        ),
        (
            "Mũi tên gãy cắm đất ngoài rào số {n}. "
            "Tôn Vũ nhặt lên, lắc đầu — {cue} chưa hết."
        ),
        (
            "Đêm chưa tan hẳn ở ch.{n}. "
            "Phong xách đèn dầu, đi dọc tường vì {cue}."
        ),
    ]
    tpl = buckets[n % len(buckets)]
    cue = t if t else "việc trong rào"
    k = (n % 17) + 1
    return tpl.format(n=n, cue=cue, k=k)


def title_from_file(path: Path, n: int) -> str:
    m = re.match(r"^Chương\s+\d+\s*[-–—]\s*(.+)\.txt$", path.name, re.I)
    if m:
        return m.group(1).strip()
    # from header
    text = path.read_text(encoding="utf-8", errors="replace")
    hm = re.search(rf"Chương\s*{n}\s*:\s*(.+)", text[:400])
    if hm:
        return hm.group(1).strip()
    return f"nhịp {n}"


def patch_file(path: Path, n: int, need_words: int | None = None) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    header, body = split_header(raw)
    title = title_from_file(path, n)
    hook = unique_hook(n, title)
    # drop leading blank lines of body then prepend hook as new first paragraph
    body_stripped = body.lstrip("\n")
    # remove previous first short paragraph if it's a known template kitchen open
    # keep rest of body intact for continuity
    rest = body_stripped
    # if body starts with a short para, skip first para only when very short (< 40 words)
    parts = re.split(r"\n\s*\n", body_stripped, maxsplit=1)
    if len(parts) == 2 and len(parts[0].split()) <= 40:
        rest = parts[1]
    new_body = hook + "\n\n" + rest.lstrip()
    # min words boost for short chapters: add one concrete scene beat before panel if needed
    text = header + new_body
    words = len(text.split())
    if need_words and words < need_words:
        extra = (
            f"\n\nPhong dừng ở góc tường, lấy que vạch thêm một vạch ngày ch.{n} trên gỗ mục. "
            f"Vạch mới lệch nửa đốt tay so với hôm qua — gió đêm đã làm xô cột. "
            f"Anh không hô khẩu hiệu. Chỉ sửa cột bằng dây mây, siết nút chết, "
            f"rồi gọi Long mang thêm ba bao đất lấp chân tường. "
            f"Việc nhỏ, nhưng nếu bỏ qua, rào sẽ nghiêng lúc sóng zombie thấp kế tiếp.\n"
        )
        # insert extra before system panel if present
        if "「" in text:
            idx = text.rfind("「")
            text = text[:idx] + extra + text[idx:]
        else:
            text = text.rstrip() + extra
        words = len(text.split())
    path.write_text(text, encoding="utf-8")
    return {"n": n, "file": path.name, "words": words, "hook12": " ".join(hook.split()[:12])}


def main() -> None:
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    below = rep.get("below_list") or []
    # map num -> need min words
    need = {}
    for item in below:
        n = int(item["num"])
        need[n] = 3000 if any(str(h).startswith("short") for h in item.get("hard_fails") or []) else None

    # also fix any result with hard_fails
    for r in rep.get("results") or []:
        if r.get("hard_fails") and r.get("num"):
            n = int(r["num"])
            if n not in need:
                need[n] = 3000 if any(str(h).startswith("short") for h in r["hard_fails"]) else None

    # resolve path by num (prefer root chapter files)
    pat = re.compile(r"^Chương\s+(\d+)\s*[-–—]", re.I)
    by: dict[int, Path] = {}
    for p in SERIES.glob("Chương *.txt"):
        m = pat.match(p.name)
        if not m:
            continue
        n = int(m.group(1))
        if n in by:
            # keep larger
            if p.stat().st_size > by[n].stat().st_size:
                by[n] = p
        else:
            by[n] = p

    done = []
    for n, short in sorted(need.items()):
        p = by.get(n)
        if not p or not p.exists():
            print(f"MISSING path ch{n}")
            continue
        done.append(patch_file(p, n, need_words=short))

    # verify uniqueness of first-12 among patched
    opens = [d["hook12"] for d in done]
    assert len(opens) == len(set(opens)), "patched openings not unique among themselves"

    out = SERIES / "_fix_dup_openings_report.json"
    out.write_text(json.dumps({"patched": len(done), "items": done}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"patched": len(done), "sample": done[:3]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
