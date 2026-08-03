# -*- coding: utf-8 -*-
"""
INDEPENDENT chapter auditor - reads each chapter RAW, scores from scratch.
Placed inside the story folder to avoid Unicode path issues.
"""
import os, re, json, glob, unicodedata, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

def norm(s):
    return unicodedata.normalize('NFC', s)

# Read chapter outline
with open(os.path.join(ROOT, "chapter_outline.json"), 'r', encoding='utf-8') as f:
    outline = json.load(f)

PAD_MARKERS = [
    r'### Lớp sâu', r'### Nhịp', r'### Thử nhỏ', r'### Thoại', r'### Khép',
    r'Trong nhật ký riêng số', r'Chốt ý nghĩa chương này',
    r'không chờ khẩu hiệu', r'chi tiết số \d+ gắn với', r'Nhịp \d+\.?\d+ của',
    r'Bổ sung hiện trường ch\.', r'Thêm một lớp rà soát',
    r'sổ cái khớp system_ledger', r'hàng chuyển nội bộ khớp',
]
AI_TICS = [
    'se lạnh lúc tờ mờ', 'sổ trong túi vải', 'Ráp ngứa lòng bàn tay chai sạn',
    'Cót két cổng sắt mở mỗi sớm mai', 'Ve kêu rả rích trưa hè',
    'Lộp bộp thớt thái hành buổi sớm', 'Khói rơm ẩm mốc buổi sáng',
    'Gỗ mít ẩm trong tủ áo cũ', 'Nặng trĩu bả vai khiêng hàng quá sức',
    'Dầu máy trộn mồ hôi', 'Ghi chú: sổ cái',
]
SENSORY = ['mùi','tiếng','ánh','nắng','mưa','gió','ấm','lạnh','khói','vị','chát','mặn','ẩm','rít','thơm']
CHAR_WORDS = ['mắt','tay','cười','khóc','gật','thở','nhìn','môi','vai','giọng']

def body_of(raw):
    lines = raw.split('\n')
    sep_count = 0
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('=' * 40) and line.strip().endswith('='):
            sep_count += 1
            if sep_count == 2:
                start_idx = i + 1
                break
    body_lines = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.startswith('GHI NHẬN:') or stripped.startswith('-' * 40):
            break
        body_lines.append(line)
    return '\n'.join(body_lines).strip()

def audit_chapter(n):
    files = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
    if not files:
        files = glob.glob(os.path.join(ROOT, f'Chương {n:02d} - *.txt'))
    if not files:
        return None

    p = files[0]
    base = os.path.basename(p)
    raw = norm(open(p, encoding='utf-8').read())
    body = body_of(raw)
    toks = len(body.split())
    chars = len(body)

    ch_outline = outline.get('chapters', {}).get(str(n), {})
    expected_year = ch_outline.get('year', None)

    has_panel = bool(re.search(r'GHI NHẬN|Hệ thống ghi nhận', body))

    year_pattern = re.findall(r'\b(19\d{2}|20\d{2})\b', body)

    dateline_match = re.search(r'Vào năm (\d{4})', body[:500])
    if not dateline_match:
        dateline_match = re.search(r'Năm (\d{4})\.', body[:500])
    panel_year = int(dateline_match.group(1)) if dateline_match else None

    year_mismatch = False
    year_diff = 0
    if panel_year and expected_year:
        year_diff = abs(panel_year - expected_year)
        year_mismatch = year_diff > 0

    low = body.lower()
    sens = sum(low.count(w) for w in SENSORY)
    charw = sum(low.count(w) for w in CHAR_WORDS)
    per_k = max(chars / 1000.0, 0.001)
    sens_d = sens / per_k
    char_d = charw / per_k

    dlg_lines = len([l for l in body.split('\n') if l.strip().startswith(('\u201c', '\u2018', '\u2014', '\u2013'))])
    names_found = sum(1 for nm in ['Hùng', 'Lan', 'bà Hà', 'Mai', 'Hạnh', 'Minh'] if nm in body)

    pad_hits = sum(len(re.findall(pat, body)) for pat in PAD_MARKERS)
    tic_hits = sum(body.count(t) for t in AI_TICS)

    long_lines = [l.strip() for l in body.split('\n') if len(l.strip()) > 60]
    cnt = Counter(long_lines)
    maxrep = max(cnt.values()) if cnt else 0

    c = 10.0
    if year_mismatch:
        c -= 5.0
    if not has_panel:
        c -= 1.5
    cont = max(0.0, c)

    p_score = 10.0
    if toks < 3000:
        p_score -= min(3.0, (3000 - toks) / 300.0)
    elif toks > 4200:
        p_score -= min(3.0, (toks - 4200) / 100.0)
    if sens_d < 3.5:
        p_score -= min(3.0, (3.5 - sens_d) * 1.4)
    if char_d < 5.0:
        p_score -= min(2.0, (5.0 - char_d) * 0.6)
    if dlg_lines < 10:
        p_score -= min(2.0, (10 - dlg_lines) * 0.25)
    p_score -= min(2.0, tic_hits * 0.35)
    prose = max(0.0, p_score)

    s = 10.0
    if toks < 3000:
        s -= 1.0
    elif toks > 4200:
        s -= 1.0
    plot = max(0.0, s)

    h = 10.0
    if dlg_lines < 10:
        h -= min(3.0, (10 - dlg_lines) * 0.3)
    if char_d < 5.0:
        h -= min(3.0, (5.0 - char_d) * 0.7)
    if names_found < 2:
        h -= (2 - names_found) * 1.0
    char_score = max(0.0, h)

    f = 10.0
    f -= min(6.0, pad_hits * 2.0)
    f -= min(3.0, tic_hits * 0.5)
    f -= min(3.0, max(0, maxrep - 1) * 1.0)
    filler = max(0.0, f)

    final = (prose * 1.0 + plot * 1.0 + char_score * 1.0 + cont * 1.5 + filler * 2.0) / 6.5

    hard_fails = []
    if year_mismatch and year_diff > 0:
        hard_fails.append(f"year_mismatch panel={panel_year} outline={expected_year}")
    if toks < 3000:
        hard_fails.append(f"short<3000({toks})")

    return {
        'num': n, 'file': base, 'final': round(final, 2),
        'prose': round(prose, 2), 'plot': round(plot, 2),
        'char': round(char_score, 2), 'cont': round(cont, 2), 'filler': round(filler, 2),
        'words': toks, 'sensory_d': round(sens_d, 2), 'char_d': round(char_d, 2),
        'dialogue': dlg_lines, 'maxrep': maxrep, 'pad_hits': pad_hits, 'tic_hits': tic_hits,
        'hard_fails': hard_fails, 'panel_year': panel_year, 'expected_year': expected_year,
        'has_panel': has_panel, 'names_found': names_found, 'path': p,
        'pass': round(final, 2) >= 9.5 and not hard_fails
    }

if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if target:
        res = audit_chapter(target)
        if res:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print("Chapter %d not found" % target)
    else:
        results = []
        passes = 0
        fails = 0
        for n in range(1, 361):
            res = audit_chapter(n)
            if res:
                results.append(res)
                if res['pass']:
                    passes += 1
                else:
                    fails += 1
                    print("FAIL Ch %03d: final=%.2f words=%d sens=%.1f char_d=%.1f dlg=%d hard=%s ey=%s py=%s" % (
                        n, res['final'], res['words'], res['sensory_d'], res['char_d'],
                        res['dialogue'], res['hard_fails'], res['expected_year'], res['panel_year']))

        avg = sum(r['final'] for r in results) / len(results) if results else 0
        print("\n===== INDEPENDENT AUDIT RESULT =====")
        print("Total: %d | Pass: %d | Fail: %d | Avg: %.3f" % (len(results), passes, fails, avg))

        with open(os.path.join(ROOT, 'independent_audit.json'), 'w', encoding='utf-8') as f:
            json.dump({'total': len(results), 'pass': passes, 'fail': fails, 'avg': round(avg, 3), 'chapters': results}, f, ensure_ascii=False, indent=2)
