# -*- coding: utf-8 -*-
"""
deterministic_scorer_v2.py — MythLab DETERMINISTIC chapter scorer v2.0.

Hệ thống chấm điểm HOÀN TOÀN DETERMINISTIC:
  - Mọi tiêu chí là CÓ/KHÔNG (YES/NO), không subjective
  - Cùng 1 file → cùng 1 kết quả, 1000 lần cũng vậy
  - Không dùng LLM judgment — chỉ regex/count/threshold
  - Tham khảo: textstat, TextDescriptives, LexicalRichness, py-readability-metrics, TAALED

32 binary criteria across 8 axes (weighted):
  van_chuong  (20): prose quality (sensory, char, sentence_var, vocab_diversity, hapax, no_monotone)
  cau_truc    (15): structure (words, scene, teaser, paragraph_var)
  nhan_vat    (15): character (dialogue, char_action, dialogue_variety, no_name_leak)
  continuity  (20): timeline (year, anachronism, timeline_anchor)
  fillers     (15): quality (pad, maxrep, no_cliche, no_template_open, no_filler_phrases, no_redundancy)
  he_thong    (10): system panel (panel, year)
  pacing      (5):  rhythm (sent_len_var, pacing_consistent)
  nang_cao    (5):  advanced (emotional_arc, sensory_variety)

HARD-FAIL caps still apply from v1.
"""

import re, os, sys, json, glob, hashlib
from collections import Counter

VERSION = "2.0.0"

# ═══════════════════════════════════════════════════════════════
# WORD LISTS (deterministic — no LLM)
# ═══════════════════════════════════════════════════════════════

SENSORY_WORDS = [
    "mùi", "tiếng", "ánh", "nắng", "gió", "mưa", "sương", "khói",
    "mùi", "âm thanh", "vang", "rền", "lặng", "thanh", "sắc",
    "nồng", "ngạt", "mát", "lạnh", "nóng", "ấm", "se", "hơi",
    "màu", "trắng", "đen", "vàng", "đỏ", "xanh", "tím", "nâu",
    "chạm", "cứng", "mềm", "nhám", "mịn", "thô", "nhẵn",
    "ngọt", "chua", "cay", "mặn", "nhạt",
]

CHAR_WORDS = [
    "mắt", "tay", "cười", "khóc", "gật", "cau", "nhíu", "run",
    "thở", "nuốt", "liếc", "cúi", "ngẩng", "nắm", "buông", "siết",
    "nhìn", "cười", "bước", "lắc", "chạm", "mỉm", "gật đầu",
    "lắc đầu", "cười lớn", "cười nhẹ", "thở dài", "cúi đầu",
    "ngẩng đầu", "nhíu mày", "cau mày", "nheo mắt", "liếm môi",
    "xoa tay", "vuốt tóc", "vỗ vai", "đánh rơi", "rung mình",
]

PAD_MARKERS = [
    "### lớp sâu", "lớp sâu", "sâu thẳm", "vô cực", "hư không",
    "bản chất sâu", "nền tảng sâu", "bản chất", "vô hạn",
    "### hidden layer", "### deep layer", "deep layer",
]

FILLER_PHRASES = [
    "tiếng gió thổi nhẹ", "không khí mát lành",
    "nắng xuyên qua", "hơi hướng về phía trước",
    "dường như dường như", "rất là rất",
    "như thế nào đó", "ở một mức độ nào đó",
    "trong thời điểm hiện tại", "ở thời điểm hiện tại",
    "có thể nói rằng", "điều này khiến cho",
]

CLICHE_OPENINGS = [
    "ánh nắng xuyên qua", "mùi cà phê thoang thoảng",
    "mặt trời mọc", "bình minh lên",
    "ánh bình minh", "sương sớm",
    "hoàng hôn buông",
]

TEMPLATE_TRANSITIONS = [
    "thời gian trôi qua", "ngày tháng trôi qua", "năm tháng qua đi",
    "một thời gian sau", "vài ngày sau", "vài tuần sau",
    "đến một ngày", "rồi cũng đến ngày", "cuối cùng cũng",
    "không ngờ rằng", "thật không ngờ", "điều không ngờ",
]

ANACHRONISM = [
    "smartphone", "iphone", "internet", "facebook", "google", "wifi",
    "laptop", "app ", "online", "startup", "email",
]

CLOSURE_WORDS = [
    "khép lại", "kết thúc", "hoàn thành", "xong xuôi",
    "tạm biệt", "chia tay", "rời đi", "bước tiếp",
    "hy vọng", "mong chờ", "tương lai", "điểm đến",
]

EMOTION_WORDS = [
    "vui", "buồn", "tức giận", "sợ hãi", "lo lắng", "hạnh phúc",
    "tự hào", "xúc động", "bàng hoàng", "choáng váng",
    "bình tĩnh", "yên tâm", "phấn khích", "thất vọng",
    "cay đắng", "đắng cay", "ngọt ngào", "ấm lòng",
]

TIMELINE_ANCHORS = [
    "năm ", "tháng ", "ngày ", "tuần ", "quý ",
    "đầu năm", "cuối năm", "giữa năm",
    "đầu tháng", "cuối tháng", "giữa tháng",
    "đầu tuần", "cuối tuần",
]

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")

def _body(text: str) -> str:
    t = _norm(text)
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    return t[m.end():] if m else t

def _is_separator(ln: str) -> bool:
    if len(ln) <= 2:
        return True
    if re.match(r"^[\\W_—\\-–*·•=…\\.\\s]{0,4}$", ln):
        return True
    return bool(re.match(r"^[\\s\\\\\\\\]*[—\\\\-–*·•=…━_~#>\\\\.\\\\s\\\\\\\\]+$", ln)) and not re.search(r"[0-9A-Za-zÀ-ỹ]", ln)

def vi_wordcount(text: str) -> int:
    return len([t for t in text.split() if len(t) >= 2])

def _panel(text: str):
    t = _norm(text)
    m = re.search(r"「Hệ thống[^」]*GHI NHẬN[^」]*」\s*\n", t)
    if not m:
        return False, None, None
    panel_text = t[m.start():m.start()+200]
    ym = re.search(r"Năm:\s*(\d{4})", panel_text)
    year = int(ym.group(1)) if ym else None
    return True, panel_text, year

def _prose_year(text: str, ymin, ymax):
    body = _body(_norm(text))
    if ymin is None or ymax is None:
        return None
    years = [int(m) for m in re.findall(rf"\\b({ymin}|{ymin+1}|{ymin+2}|{ymin+3}|{ymax-3}|{ymax-2}|{ymax-1}|{ymax})\\b", body)]
    if not years:
        years = [int(m) for m in re.findall(rf"\\b(\\d{{4}})\\b", body) if ymin <= int(m) <= ymax]
    if not years:
        return None
    return Counter(years).most_common(1)[0][0]

def _sentences(text: str) -> list:
    """Split text into sentences (deterministic)."""
    sents = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sents if len(s.strip()) > 5]

def _paragraphs(text: str) -> list:
    """Split into non-empty paragraphs."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paras

def _ttr(words: list) -> float:
    """Type-Token Ratio — lexical diversity."""
    if len(words) < 10:
        return 1.0
    return len(set(words)) / len(words)

def _hapax_ratio(words: list) -> float:
    """Hapax Legomena ratio — words appearing exactly once."""
    if len(words) < 10:
        return 0.0
    counts = Counter(words)
    hapax = sum(1 for w, c in counts.items() if c == 1)
    return hapax / len(words)

def _sent_len_variance(sentences: list) -> float:
    """Variance in sentence lengths (higher = more varied)."""
    if len(sentences) < 3:
        return 0.0
    lens = [len(s) for s in sentences]
    mean = sum(lens) / len(lens)
    return sum((l - mean) ** 2 for l in lens) / len(lens)

def _paragraph_len_variance(paragraphs: list) -> float:
    """Variance in paragraph lengths."""
    if len(paragraphs) < 3:
        return 0.0
    lens = [len(p) for p in paragraphs]
    mean = sum(lens) / len(lens)
    return sum((l - mean) ** 2 for l in lens) / len(lens)


# ═══════════════════════════════════════════════════════════════
# MAIN SCORING
# ═══════════════════════════════════════════════════════════════

def score_chapter(text: str, cfg: dict = None) -> dict:
    if cfg is None:
        cfg = {}

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

    # ─── Counting signals ───
    # Pad markers
    pad_hits = {m: low.count(m) for m in PAD_MARKERS if m in low and m not in motif_whitelist}
    pad_total = sum(pad_hits.values())
    has_pad = pad_total > 0

    # Maxrep
    content_lines = [ln for ln in lines if not _is_separator(ln) and ln.lower() not in motif_whitelist]
    long_lines = [ln for ln in content_lines if len(ln) >= 25]
    long_counter = Counter(long_lines)
    maxrep = max(long_counter.values()) if long_counter else 0

    # Dialogue
    dialogue_quotes = len(re.findall(r'["""\\u201c\\u201d]', body))
    dialogue = dialogue_quotes // 2 + body.count("—") // 3

    # Sensory
    sensory = sum(body_low.count(w) for w in SENSORY_WORDS)
    sensory_density = sensory / k

    # Char density
    charct = sum(body_low.count(w) for w in CHAR_WORDS)
    char_density = charct / k

    # Panel
    has_panel, panel, panel_year = _panel(t)
    pyear = _prose_year(t, ymin, ymax)

    # Year mismatch (dateline mode)
    year_check = cfg.get("year_check", "strict")
    year_mismatch = False
    if has_panel and panel_year:
        if year_check == "dateline":
            dl_gap_max = int(cfg.get("dateline_gap_max", 6))
            head = " ".join(body.split()[:60])
            dm = re.search(r"năm\\s+((?:19[3-9]\\d|20[0-4]\\d))", head, re.I)
            if not dm:
                dm = re.search(r"\\b((?:19[3-9]\\d|20[0-4]\\d))\\b", head)
            dl_year = int(dm.group(1)) if dm else None
            if dl_year and 0 < abs(dl_year - panel_year) <= dl_gap_max:
                year_mismatch = True
                pyear = dl_year
        else:
            if ymin is not None and ymax is not None and pyear:
                year_mismatch = (panel_year != pyear)
            elif pyear:
                year_mismatch = (panel_year != pyear)

    # Anachronism
    anach_terms = [a for a in ANACHRONISM if a not in extra_anach_ok]
    anach_hits = {a: body_low.count(a) for a in anach_terms if a in body_low}
    has_anach = len(anach_hits) > 0

    # Scene breaks (separator lines ≥3 chars between prose)
    scene_breaks = sum(1 for ln in lines if _is_separator(ln) and len(ln) >= 3)
    has_scene = scene_breaks > 0

    # Teaser/cliffhanger at end of chapter
    prose_lines = [ln.strip() for ln in lines
                   if not _is_separator(ln.strip())
                   and not re.search(r"GHI\s*NHẬN|HẾT\s*CHƯƠNG", ln, re.I)
                   and not re.match(r"^(Năm|Tổng\s*EXP|Không\s*gian)", ln.strip())]
    has_teaser = False
    if len(prose_lines) >= 3:
        tail = "\n".join(prose_lines[-3:]).lower()
        has_teaser = bool(re.search(
            r"[?…]|liệu|sẽ|nhưng|chưa|đợi|ngày mai|hôm sau|sáng hôm|"
            r"giá như|mai là|một ngày mới|chưa biết|rồi tính|phía trước",
            tail))

    # ─── NEW v2 signals ───

    # 1. Sentence length variation (sent_len_var)
    sentences = _sentences(body)
    sent_len_var = _sent_len_variance(sentences)

    # 2. Paragraph length variation
    paragraphs = _paragraphs(body)
    para_var = _paragraph_len_variance(paragraphs)

    # 3. Vocabulary diversity (TTR)
    all_words = [w.lower() for w in body.split() if len(w) >= 2]
    ttr = _ttr(all_words)

    # 4. Hapax Legomena ratio
    hapax_ratio = _hapax_ratio(all_words)

    # 5. Dialogue ratio
    total_chars_body = max(len(body), 1)
    dialogue_chars = sum(len(m.group()) for m in re.finditer(r'["""\\u201c\\u201d][^""\\u201c\\u201d]+["""\\u201c\\u201d]', body))
    dialogue_ratio = dialogue_chars / total_chars_body

    # 6. No cliche openings
    first_500 = body[:500].lower()
    cliche_open_count = sum(1 for c in CLICHE_OPENINGS if c in first_500)

    # 7. No template transitions
    template_trans_count = sum(body_low.count(t) for t in TEMPLATE_TRANSITIONS)

    # 8. No filler phrases
    filler_count = sum(body_low.count(f) for f in FILLER_PHRASES)

    # 9. No redundancy (same sentence patterns)
    sent_starts = [s[:30].lower() for s in sentences if len(s) > 10]
    start_counter = Counter(sent_starts)
    max_start_rep = max(start_counter.values()) if start_counter else 0

    # 10. Emotional arc (at least 2 different emotions)
    emotions_found = [e for e in EMOTION_WORDS if e in body_low]
    unique_emotions = len(set(emotions_found))

    # 11. Sensory variety (at least 3 different senses)
    sense_cats = {
        "smell": ["mùi", "thơm", "nồng", "ngạt"],
        "sound": ["tiếng", "âm thanh", "vang", "rền", "lặng"],
        "sight": ["ánh", "nắng", "màu", "sáng", "tối", "mờ"],
        "touch": ["chạm", "cứng", "mềm", "nhám", "mịn", "ấm", "lạnh"],
        "taste": ["ngọt", "chua", "cay", "mặn", "nhạt"],
    }
    senses_used = sum(1 for cat_words in sense_cats.values() if any(w in body_low for w in cat_words))

    # 12. Pacing consistency (no super-long paragraphs)
    para_lens = [len(p) for p in paragraphs]
    max_para_len = max(para_lens) if para_lens else 0
    avg_para_len = sum(para_lens) / len(para_lens) if para_lens else 0

    # 13. Dialogue variety (at least 2 speakers)
    dialogue_lines = re.findall(r'["""\\u201c\\u201d]([^""\\u201c\\u201d]{5,})["""\\u201c\\u201d]', body)
    speakers = set()
    for dl in dialogue_lines:
        if "Hùng" in dl or "hùng" in dl:
            speakers.add("Hùng")
        if "Lan" in dl or "lan" in dl:
            speakers.add("Lan")
        if "mẹ" in dl or "Mẹ" in dl or "mế" in dl or "Mế" in dl:
            speakers.add("Me")
    dialogue_variety = len(speakers) >= 2

    # 14. No name leak (character called wrong name)
    name_leak = False
    if "Minh" in body and "Gia Huy" in body:
        name_leak = True
    if "bà Hà" in body.lower() and "mế" not in body.lower() and cfg.get("baha_is_me"):
        name_leak = True

    # 15. Timeline anchor (chapter mentions time)
    has_timeline = any(a in body_low for a in TIMELINE_ANCHORS)

    # 16. Closure at end (last paragraph has closure words)
    last_para = paragraphs[-1].lower() if paragraphs else ""
    has_closure = any(c in last_para for c in CLOSURE_WORDS)

    # ─── Binary criteria ───
    criteria = {}

    # 1. Văn chương (20%)
    criteria["van_sensory_ok"] = sensory_density >= 3.0
    criteria["van_char_ok"] = char_density >= 2.0
    criteria["van_sent_var_ok"] = sent_len_var >= 1000.0  # sentences vary in length
    criteria["van_vocab_ok"] = ttr >= 0.28  # vocabulary not too repetitive
    criteria["van_hapax_ok"] = hapax_ratio >= 0.18  # enough unique words

    # 2. Cấu trúc (15%)
    criteria["cau_words_ok"] = words >= 3000
    criteria["cau_scene_ok"] = has_scene
    criteria["cau_teaser_ok"] = has_teaser
    criteria["cau_para_var_ok"] = para_var >= 8000.0  # paragraphs vary in length

    # 3. Nhân vật (15%)
    criteria["nv_dialogue_ok"] = dialogue >= 6
    criteria["nv_char_action_ok"] = char_density >= 2.0  # same as van_char_ok for simplicity
    criteria["nv_dialogue_var_ok"] = dialogue_variety  # at least 2 speakers
    criteria["nv_no_name_leak"] = not name_leak

    # 4. Continuity (20%)
    criteria["cont_year_ok"] = not year_mismatch if (has_panel and panel_year and pyear) else True
    criteria["cont_anach_ok"] = not has_anach
    criteria["cont_timeline_ok"] = has_timeline

    # 5. Fillers (15%)
    criteria["fill_pad_ok"] = not has_pad
    criteria["fill_maxrep_ok"] = maxrep < 3
    criteria["fill_no_cliche_open"] = cliche_open_count == 0
    criteria["fill_no_template_trans"] = template_trans_count == 0
    criteria["fill_no_filler_phrases"] = filler_count == 0
    criteria["fill_no_redundancy"] = max_start_rep <= 2

    # 6. Hệ thống (10%)
    criteria["sys_panel_ok"] = has_panel if genre_has_system else True
    criteria["sys_year_ok"] = (panel_year is not None) if genre_has_system else True

    # 7. Pacing (5%)
    criteria["pac_consistent_ok"] = max_para_len < avg_para_len * 8  # no super-long paragraphs
    criteria["pac_sent_var_ok"] = sent_len_var >= 1000.0

    # 8. Nâng cao (5%)
    criteria["adv_emotion_ok"] = unique_emotions >= 1
    criteria["adv_sensory_var_ok"] = senses_used >= 3

    # ─── Hard-fail caps ───
    hard_fails = []
    cap = 10.0

    if has_pad:
        hard_fails.append("pad_markers")
        cap = min(cap, 6.5)
    if maxrep >= 3:
        hard_fails.append(f"maxrep={maxrep}")
        cap = min(cap, 7.0)
    if year_mismatch:
        hard_fails.append(f"year_mismatch panel={panel_year} prose={pyear}")
        cap = min(cap, 6.0)
    if has_anach:
        hard_fails.append(f"anachronism={len(anach_hits)}")
        cap = min(cap, 6.5)
    if words < 3000:
        hard_fails.append(f"words={words}")
        cap = min(cap, 7.5)
    if sensory_density < 2.0:
        hard_fails.append(f"sensory_density={sensory_density:.1f}")
        cap = min(cap, 7.5)
    if not has_panel and genre_has_system:
        hard_fails.append("missing_system_panel")
        cap = min(cap, 7.5)
    if dialogue < 3:
        hard_fails.append(f"dialogue={dialogue}")
        cap = min(cap, 7.5)
    if cliche_open_count >= 3:
        hard_fails.append(f"cliche_open={cliche_open_count}")
        cap = min(cap, 7.0)
    if template_trans_count >= 3:
        hard_fails.append(f"template_trans={template_trans_count}")
        cap = min(cap, 7.0)
    if filler_count >= 3:
        hard_fails.append(f"filler_phrases={filler_count}")
        cap = min(cap, 7.0)

    # ─── Axis scoring ───
    def axis_score(criteria_names):
        pass_count = sum(1 for c in criteria_names if criteria.get(c, False))
        total = len(criteria_names)
        return pass_count, total

    van_pass, van_total = axis_score(["van_sensory_ok", "van_char_ok", "van_sent_var_ok", "van_vocab_ok", "van_hapax_ok"])
    cau_pass, cau_total = axis_score(["cau_words_ok", "cau_scene_ok", "cau_teaser_ok", "cau_para_var_ok"])
    nv_pass, nv_total = axis_score(["nv_dialogue_ok", "nv_char_action_ok", "nv_dialogue_var_ok", "nv_no_name_leak"])
    cont_pass, cont_total = axis_score(["cont_year_ok", "cont_anach_ok", "cont_timeline_ok"])
    fill_pass, fill_total = axis_score(["fill_pad_ok", "fill_maxrep_ok", "fill_no_cliche_open", "fill_no_template_trans", "fill_no_filler_phrases", "fill_no_redundancy"])
    sys_pass, sys_total = axis_score(["sys_panel_ok", "sys_year_ok"])
    pac_pass, pac_total = axis_score(["pac_consistent_ok", "pac_sent_var_ok"])
    adv_pass, adv_total = axis_score(["adv_emotion_ok", "adv_sensory_var_ok"])

    axes = {
        "van_chuong": f"{van_pass}/{van_total}={round(van_pass/van_total*100,1) if van_total else 0}",
        "cau_truc": f"{cau_pass}/{cau_total}={round(cau_pass/cau_total*100,1) if cau_total else 0}",
        "nhan_vat": f"{nv_pass}/{nv_total}={round(nv_pass/nv_total*100,1) if nv_total else 0}",
        "continuity": f"{cont_pass}/{cont_total}={round(cont_pass/cont_total*100,1) if cont_total else 0}",
        "fillers": f"{fill_pass}/{fill_total}={round(fill_pass/fill_total*100,1) if fill_total else 0}",
        "he_thong": f"{sys_pass}/{sys_total}={round(sys_pass/sys_total*100,1) if sys_total else 0}",
        "pacing": f"{pac_pass}/{pac_total}={round(pac_pass/pac_total*100,1) if pac_total else 0}",
        "nang_cao": f"{adv_pass}/{adv_total}={round(adv_pass/adv_total*100,1) if adv_total else 0}",
    }

    # Weighted average (same weights as v1 for backward compat, new axes get small weights)
    weighted = (
        (van_pass / van_total * 20) +
        (cau_pass / cau_total * 15) +
        (nv_pass / nv_total * 15) +
        (cont_pass / cont_total * 20) +
        (fill_pass / fill_total * 15) +
        (sys_pass / sys_total * 10) +
        (pac_pass / pac_total * 5) +
        (adv_pass / adv_total * 5)
    )

    final = min(weighted, cap)

    return {
        "final": round(final, 1),
        "weighted_raw": round(weighted, 1),
        "cap": cap,
        "passed": final >= 9.0,
        "criteria": criteria,
        "hard_fails": hard_fails,
        "axes": axes,
        "metrics": {
            "words": words,
            "chars": chars,
            "sentences": len(sentences),
            "paragraphs": len(paragraphs),
            "dialogue": dialogue,
            "sensory_density": round(sensory_density, 2),
            "char_density": round(char_density, 2),
            "ttr": round(ttr, 3),
            "hapax_ratio": round(hapax_ratio, 3),
            "sent_len_var": round(sent_len_var, 1),
            "para_var": round(para_var, 1),
            "dialogue_ratio": round(dialogue_ratio, 3),
            "cliche_open": cliche_open_count,
            "template_trans": template_trans_count,
            "filler_phrases": filler_count,
            "max_start_rep": max_start_rep,
            "unique_emotions": unique_emotions,
            "senses_used": senses_used,
            "max_para_len": max_para_len,
            "panel_year": panel_year,
            "prose_year": pyear,
            "maxrep": maxrep,
            "pad_total": pad_total,
        },
        "version": VERSION,
    }


def score_file(path: str, cfg: dict = None) -> dict:
    text = open(path, encoding="utf-8").read()
    result = score_chapter(text, cfg)
    result["file"] = os.path.basename(path)
    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MythLab Deterministic Scorer v2")
    parser.add_argument("files", nargs="*", help="Chapter files to score")
    parser.add_argument("--dir", help="Score all .txt files in directory")
    parser.add_argument("--threshold", type=float, default=9.0, help="PASS threshold")
    parser.add_argument("--json", help="Output JSON to file")
    parser.add_argument("--fails-only", action="store_true", help="Only show FAIL chapters")
    parser.add_argument("--test-loop", action="store_true", help="Determinism test")
    parser.add_argument("--times", type=int, default=100, help="Test loop count")
    args = parser.parse_args()

    # Load config
    cfg = {}
    cfg_path = ".mythlab_score.json"
    if os.path.exists(cfg_path):
        cfg = json.load(open(cfg_path, encoding="utf-8"))

    if args.test_loop:
        test_dir = args.dir or "."
        test_files = sorted(glob.glob(os.path.join(test_dir, "Chương *.txt")))[:3]
        print(f"Determinism test: {args.times} runs × {len(test_files)} files")
        all_pass = True
        for f in test_files:
            scores = set()
            for _ in range(args.times):
                r = score_file(f, cfg)
                scores.add(r["final"])
            status = "✅" if len(scores) == 1 else "❌"
            if len(scores) != 1:
                all_pass = False
            print(f"  {status} {os.path.basename(f)}: {sorted(scores)} ({args.times} runs)")
        print(f"\n{'ALL PASS ✅' if all_pass else 'FAILED ❌'}")
        sys.exit(0 if all_pass else 1)

    # Collect files
    file_list = []
    if args.files:
        file_list = args.files
    elif args.dir:
        file_list = sorted(glob.glob(os.path.join(args.dir, "Chương *.txt")))

    if not file_list:
        print("No files to score.")
        sys.exit(1)

    results = []
    pass_count = 0
    for f in file_list:
        r = score_file(f, cfg)
        results.append(r)
        if r["final"] >= args.threshold:
            pass_count += 1
            tag = "PASS"
        else:
            tag = "FAIL"
        if not args.fails_only or tag == "FAIL":
            hf_str = f" [HF: {', '.join(r['hard_fails'])}]" if r['hard_fails'] else ""
            print(f"[{tag}] {r['file']}: {r['final']:.2f} (weighted={r['weighted_raw']:.2f}, cap={r['cap']}){hf_str}")

    print(f"\nTOTAL: {pass_count}/{len(results)} PASS ≥{args.threshold}")
    avg = sum(r["final"] for r in results) / len(results) if results else 0
    print(f"AVG: {avg:.2f}")

    if args.json:
        output = {"version": VERSION, "threshold": args.threshold, "total": len(results), "pass": pass_count, "avg": round(avg, 2), "results": results}
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"JSON: {args.json}")
