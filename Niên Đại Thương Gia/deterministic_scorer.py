# -*- coding: utf-8 -*-
"""
deterministic_scorer.py — MythLab DETERMINISTIC chapter scorer.

Hệ thống chấm điểm HOÀN TOÀN DETERMINISTIC:
  - Mọi tiêu chí là CÓ/KHÔNG (YES/NO), không subjective
  - Cùng 1 file → cùng 1 kết quả, 1000 lần cũng vậy
  - Không dùng LLM judgment — chỉ regex/count/threshold

6 trục weighted + binary hard-fail:
  van_chuong  (20): sensory ≥3/kchar AND char_density ≥2/kchar
  cau_truc    (15): words ≥3000 AND has_scene_break AND has_teaser
  nhan_vat    (15): dialogue ≥6 AND char_density ≥2
  continuity  (25): panel_year == prose_year AND no_anachronism
  filler_pad  (15): pad_markers == 0 AND maxrep < 3
  he_thong    (10): has_panel AND panel_has_year

PASS = weighted ≥ 9.0 AND zero hard-fails.

Usage:
  python deterministic_scorer.py <file.txt> [--json report.json]
  python deterministic_scorer.py --dir <dir> [--threshold 9.0]
  python deterministic_scorer.py --test-loop --dir <dir> --times 100
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


# ─── PAD markers (binary: có = fail) ───
PAD_MARKERS = [
    "### lớp sâu", "### nhịp", "### thử nhỏ", "### thoại", "### khép",
    "trong nhật ký riêng số", "chốt ý nghĩa chương này",
    "se lạnh lúc tờ mờ", "sổ trong túi vải",
    "không chờ khẩu hiệu", "chờ người dám chịu khi hỏng",
    "hùng tới sớm, lan mở sổ", "hiện trường nói trước phòng họp",
    "chi tiết số", "nhịp n.i của", "bổ sung hiện trường ch.",
    "thêm một lớp rà soát", "số đẹp mà người mỏi là số xấu",
    "sổ cái khớp system_ledger", "hàng chuyển nội bộ",
    "hơn bao giờ hết", "không thể phủ nhận", "trong thế giới đầy rẫy",
    "delve", "tapestry", "hắn quyết tâm trở nên mạnh hơn",
    "đáng chú ý là", "điều quan trọng cần lưu ý",
]

SENSORY_WORDS = [
    "mùi", "tanh", "thơm", "khét", "hôi", "mốc",
    "tiếng", "vọng", "rền", "lạo xạo", "lách cách", "ù",
    "ánh", "nắng", "sáng", "tối", "mờ", "chói", "bóng",
    "lạnh", "nóng", "ấm", "rát", "buốt", "ẩm", "khô",
    "mặn", "ngọt", "chua", "đắng", "chát",
    "mềm", "cứng", "nhám", "trơn", "ram ráp", "gai",
]

CHAR_WORDS = [
    "mắt", "tay", "cười", "khóc", "gật", "cau", "nhíu", "run",
    "thở", "nuốt", "liếc", "cúi", "ngẩng", "nắm", "buông", "siết",
]

ANACHRONISM = [
    "smartphone", "iphone", "internet", "facebook", "google", "wifi",
    "laptop", "app ", "online", "startup", "email",
]

SEP_RE = re.compile(r"^[\W_—\-–*·•=…\.\s]{0,4}$")
SEP_FULL_RE = re.compile(r"^[\\s\\\\]*[—\\-–*·•=…━_~#>\\.\\s\\\\]+$")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _body(text: str) -> str:
    t = _norm(text)
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    return t[m.end():] if m else t


def _is_separator(ln: str) -> bool:
    if len(ln) <= 2:
        return True
    if SEP_RE.match(ln):
        return True
    return bool(SEP_FULL_RE.match(ln)) and not re.search(r"[0-9A-Za-zÀ-ỹ]", ln)


def vi_wordcount(text: str) -> int:
    return len([t for t in text.split() if len(t) >= 2])


def _panel(text: str):
    t = _norm(text)
    m = re.search(r"「[^」]*GHI\s*NHẬN[^」]*」(.*?)(?:\n\n|\Z)", t, re.S | re.I)
    if not m:
        m = re.search(r"GHI\s*NHẬN.*", t, re.S | re.I)
        if not m:
            return False, "", None
    block = m.group(0)
    ym = re.search(r"Năm[:\s]*([0-9]{4})", block)
    return True, block, (int(ym.group(1)) if ym else None)


def _prose_year(text: str, ymin=None, ymax=None):
    yrs = [int(m.group(1)) for m in
           re.finditer(r"\b(19[3-9]\d|20[0-4]\d)\b", _body(text))]
    if not yrs:
        return None
    if ymin is not None and ymax is not None:
        in_range = [y for y in yrs if ymin <= y <= ymax]
        if in_range:
            return Counter(in_range).most_common(1)[0][0]
        return None
    return Counter(yrs).most_common(1)[0][0]


def _cliff_check(body_lines, lines):
    """Binary: có teaser/cliff ở cuối chương không."""
    prose_lines = [ln.strip() for ln in lines
                   if not _is_separator(ln.strip())
                   and not re.search(r"GHI\s*NHẬN|HẾT\s*CHƯƠNG", ln, re.I)
                   and not re.match(r"^(Năm|Tổng\s*EXP|Không\s*gian)", ln.strip())]
    if len(prose_lines) < 3:
        return False
    tail = "\n".join(prose_lines[-3:]).lower()
    return bool(re.search(
        r"[?…]|liệu|sẽ|nhưng|chưa|đợi|ngày mai|hôm sau|sáng hôm|"
        r"giá như|mai là|một ngày mới|chưa biết|rồi tính|phía trước",
        tail))


def score_chapter(text: str, cfg: dict | None = None) -> dict:
    """
    DETERMINISTIC scoring — binary YES/NO criteria → weighted score.
    Same input → same output, always.
    """
    cfg = cfg or {}
    ymin = cfg.get("story_year_min")
    ymax = cfg.get("story_year_max")
    is_rebirth = bool(cfg.get("rebirth"))
    motif_whitelist = [m.lower() for m in cfg.get("motif_whitelist", [])]
    extra_anach_ok = [a.lower() for a in cfg.get("anachronism_allow", [])]
    genre_has_system = cfg.get("has_system", True)

    t = _norm(text)
    low = t.lower()
    body = _body(t)
    body_low = body.lower()
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]

    words = vi_wordcount(body)
    chars = len(body)
    k = max(chars / 1000.0, 0.001)

    # ─── Binary signals ───
    # Pad markers
    pad_hits = {m: low.count(m) for m in PAD_MARKERS
                if m in low and m not in motif_whitelist}
    pad_total = sum(pad_hits.values())
    has_pad = pad_total > 0

    # Maxrep
    content_lines = [ln for ln in lines
                     if not _is_separator(ln)
                     and ln.lower() not in motif_whitelist]
    long_lines = [ln for ln in content_lines if len(ln) >= 25]
    long_counter = Counter(long_lines)
    maxrep = max(long_counter.values()) if long_counter else 0

    # Dialogue
    dialogue = len(re.findall(r'["""\u201c\u201d]', body)) // 2 + body.count("—") // 3

    # Sensory
    sensory = sum(body_low.count(w) for w in SENSORY_WORDS)
    sensory_density = sensory / k

    # Char density
    charct = sum(body_low.count(w) for w in CHAR_WORDS)
    char_density = charct / k

    # Panel
    has_panel, panel, panel_year = _panel(t)
    pyear = _prose_year(t, ymin, ymax)

    # Year mismatch — supports year_check modes from strict_score.py
    year_check = cfg.get("year_check", "strict")
    year_mismatch = False
    if has_panel and panel_year:
        if year_check == "dateline":
            # Saga: only flag if dateline (first 60 words) year differs from panel by small gap
            dl_gap_max = int(cfg.get("dateline_gap_max", 6))
            head = " ".join(body.split()[:60])
            dm = re.search(r"năm\s+((?:19[3-9]\d|20[0-4]\d))", head, re.I)
            if not dm:
                dm = re.search(r"\b((?:19[3-9]\d|20[0-4]\d))\b", head)
            dl_year = int(dm.group(1)) if dm else None
            if dl_year and 0 < abs(dl_year - panel_year) <= dl_gap_max:
                year_mismatch = True
                pyear = dl_year
        else:
            # Strict: panel_year must equal prose_year (most common in body)
            if ymin is not None and ymax is not None and pyear:
                year_mismatch = (panel_year != pyear)
            elif pyear:
                year_mismatch = (panel_year != pyear)

    # Anachronism
    anach_terms = [a for a in ANACHRONISM if a not in extra_anach_ok]
    anach = 0
    if panel_year and panel_year < 2000 and not is_rebirth:
        anach = sum(body_low.count(a) for a in anach_terms)
    has_anach = anach > 0

    # Scene breaks
    scene_breaks = sum(1 for ln in lines if _is_separator(ln) and len(ln) >= 3)
    has_scene = scene_breaks > 0

    # Teaser/cliff
    has_teaser = _cliff_check(body, lines)

    # ─── Binary YES/NO per axis ───
    # Each criterion: True=pass, False=fail
    criteria = {}

    # 1. Văn chương (20): sensory ≥3/kchar AND char_density ≥2/kchar
    criteria["van_sensory_ok"] = sensory_density >= 3.0
    criteria["van_char_ok"] = char_density >= 2.0

    # 2. Cấu trúc (15): words ≥3000 AND has_scene AND has_teaser
    criteria["cau_words_ok"] = words >= 3000
    criteria["cau_scene_ok"] = has_scene
    criteria["cau_teaser_ok"] = has_teaser

    # 3. Nhân vật (15): dialogue ≥6
    criteria["nv_dialogue_ok"] = dialogue >= 6

    # 4. Continuity (25): year_match AND no_anachronism
    criteria["cont_year_ok"] = not year_mismatch if (has_panel and panel_year and pyear) else True
    criteria["cont_anach_ok"] = not has_anach

    # 5. Filler/Pad (15): no_pad AND maxrep<3
    criteria["fill_pad_ok"] = not has_pad
    criteria["fill_maxrep_ok"] = maxrep < 3

    # 6. Hệ thống (10): has_panel AND panel_has_year
    criteria["sys_panel_ok"] = has_panel if genre_has_system else True
    criteria["sys_year_ok"] = (panel_year is not None) if genre_has_system else True

    # ─── Count PASS/FAIL per axis ───
    def axis_score(pass_list):
        passed = sum(1 for c in pass_list if criteria[c])
        total = len(pass_list)
        return passed, total

    van_pass, van_total = axis_score(["van_sensory_ok", "van_char_ok"])
    cau_pass, cau_total = axis_score(["cau_words_ok", "cau_scene_ok", "cau_teaser_ok"])
    nv_pass, nv_total = axis_score(["nv_dialogue_ok"])
    cont_pass, cont_total = axis_score(["cont_year_ok", "cont_anach_ok"])
    fill_pass, fill_total = axis_score(["fill_pad_ok", "fill_maxrep_ok"])
    sys_pass, sys_total = axis_score(["sys_panel_ok", "sys_year_ok"])

    # Weighted: each axis gets full weight if ALL criteria pass,
    # proportional if partial, 0 if none
    def axis_pct(p, t):
        return p / t if t > 0 else 1.0

    van_score = 10.0 * axis_pct(van_pass, van_total)
    cau_score = 10.0 * axis_pct(cau_pass, cau_total)
    nv_score = 10.0 * axis_pct(nv_pass, nv_total)
    cont_score = 10.0 * axis_pct(cont_pass, cont_total)
    fill_score = 10.0 * axis_pct(fill_pass, fill_total)
    sys_score = 10.0 * axis_pct(sys_pass, sys_total) if genre_has_system else None

    # Weighted average
    weights = {"van": 20, "cau": 15, "nv": 15, "cont": 25, "fill": 15}
    scores = {"van": van_score, "cau": cau_score, "nv": nv_score,
              "cont": cont_score, "fill": fill_score}
    if sys_score is not None:
        weights["sys"] = 10
        scores["sys"] = sys_score

    wsum = sum(weights.values())
    weighted = sum(scores[k] * weights[k] for k in weights) / wsum

    # ─── HARD-FAIL caps ───
    hard_fails = []
    cap = 10.0
    if has_pad:
        hard_fails.append(f"pad_markers={pad_total}")
        cap = min(cap, 6.5)
    if maxrep >= 3:
        hard_fails.append(f"maxrep={maxrep}")
        cap = min(cap, 7.0)
    if words < 3000:
        hard_fails.append(f"short<3000({words})")
        cap = min(cap, 7.5)
    if year_mismatch:
        hard_fails.append(f"year_mismatch panel={panel_year} prose={pyear}")
        cap = min(cap, 6.0)
    if has_anach:
        hard_fails.append(f"anachronism={anach}")
        cap = min(cap, 6.5)
    if genre_has_system and not has_panel:
        hard_fails.append("missing_system_panel")
        cap = min(cap, 7.5)
    if dialogue < 4 and words > 2000:
        hard_fails.append(f"almost_no_dialogue({dialogue})")
        cap = min(cap, 7.5)
    if sensory_density < 2:
        hard_fails.append(f"thin_prose(sens={sensory_density:.1f})")
        cap = min(cap, 7.5)

    final = round(min(weighted, cap), 2)
    passed = final >= 9.0 and len(hard_fails) == 0

    return {
        "final": final,
        "weighted_raw": round(weighted, 2),
        "cap": cap,
        "passed": passed,
        "hard_fails": hard_fails,
        "criteria": {k: ("PASS" if v else "FAIL") for k, v in criteria.items()},
        "axes": {
            "van_chuong": f"{van_pass}/{van_total}={van_score:.1f}",
            "cau_truc": f"{cau_pass}/{cau_total}={cau_score:.1f}",
            "nhan_vat": f"{nv_pass}/{nv_total}={nv_score:.1f}",
            "continuity": f"{cont_pass}/{cont_total}={cont_score:.1f}",
            "filler_pad": f"{fill_pass}/{fill_total}={fill_score:.1f}",
            "he_thong": f"{sys_pass}/{sys_total}={sys_score:.1f}" if sys_score is not None else "N/A",
        },
        "metrics": {
            "words": words, "chars": chars, "dialogue": dialogue,
            "maxrep": maxrep, "pad_total": pad_total,
            "sensory_density": round(sensory_density, 2),
            "char_density": round(char_density, 2),
            "has_panel": has_panel, "panel_year": panel_year,
            "prose_year": pyear, "scene_breaks": scene_breaks,
            "has_teaser": has_teaser,
        },
    }


def score_file(path: str, cfg: dict | None = None) -> dict:
    """Score a single file — deterministic, repeatable."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    result = score_chapter(text, cfg)
    result["file"] = p.name
    return result


def load_cfg(directory: str) -> dict:
    p = Path(directory) / ".mythlab_score.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def main():
    parser = argparse.ArgumentParser(description="MythLab Deterministic Scorer")
    parser.add_argument("files", nargs="*", help="Chapter files to score")
    parser.add_argument("--dir", help="Score all chapter files in directory")
    parser.add_argument("--json", help="Output JSON report")
    parser.add_argument("--threshold", type=float, default=9.0)
    parser.add_argument("--test-loop", action="store_true",
                        help="Run N times and check variance")
    parser.add_argument("--times", type=int, default=100)
    args = parser.parse_args()

    cfg = {}
    if args.dir:
        cfg = load_cfg(args.dir)

    files = []
    if args.files:
        files = [Path(f) for f in args.files]
    elif args.dir:
        d = Path(args.dir)
        files = sorted(d.glob("Chương *.txt"), key=lambda p: p.name)
    
    if not files:
        print("No files found.")
        sys.exit(1)

    if args.test_loop:
        # Test deterministic scoring N times
        import time
        results_per_file = {}
        all_consistent = True
        
        for f in files:
            scores = []
            t0 = time.time()
            for i in range(args.times):
                r = score_file(str(f), cfg)
                scores.append(r["final"])
            elapsed = time.time() - t0
            
            unique_scores = set(scores)
            is_consistent = len(unique_scores) == 1
            if not is_consistent:
                all_consistent = False
            
            results_per_file[f.name] = {
                "scores": scores,
                "unique": sorted(unique_scores),
                "consistent": is_consistent,
                "count": len(scores),
                "time_sec": round(elapsed, 2),
            }
            
            status = "✅ CONSISTENT" if is_consistent else "❌ VARIANCE"
            print(f"{status} {f.name}: {len(unique_scores)} unique score(s) "
                  f"over {args.times} runs [{elapsed:.2f}s]")
            if not is_consistent:
                print(f"  Scores: {sorted(unique_scores)}")
        
        print(f"\n{'='*60}")
        print(f"RESULT: {'ALL CONSISTENT ✅' if all_consistent else 'VARIANCE DETECTED ❌'}")
        print(f"Files tested: {len(files)} × {args.times} runs = {len(files)*args.times} total")
        
        if args.json:
            Path(args.json).write_text(
                json.dumps(results_per_file, ensure_ascii=False, indent=2),
                encoding="utf-8")
        sys.exit(0 if all_consistent else 1)
    else:
        # Single pass scoring
        report = []
        total = 0
        passed = 0
        for f in files:
            r = score_file(str(f), cfg)
            report.append(r)
            total += 1
            if r["passed"]:
                passed += 1
            status = "PASS" if r["passed"] else "FAIL"
            print(f"[{status}] {r['file']}: {r['final']:.2f} "
                  f"(weighted={r['weighted_raw']:.2f}, cap={r['cap']})"
                  f" {'HF: ' + ','.join(r['hard_fails']) if r['hard_fails'] else ''}")
        
        print(f"\nTOTAL: {passed}/{total} PASS ≥{args.threshold}")
        avg = sum(r["final"] for r in report) / len(report) if report else 0
        print(f"AVG: {avg:.2f}")
        
        if args.json:
            Path(args.json).write_text(
                json.dumps({"results": report, "summary": {
                    "total": total, "passed": passed,
                    "avg": round(avg, 2), "threshold": args.threshold,
                }}, ensure_ascii=False, indent=2),
                encoding="utf-8")
        sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
