# -*- coding: utf-8 -*-
"""
STRICT AUDIT — Niên Đại Thương Gia (360 ch)
Chấm điểm khó tính nhất theo 5 tiêu chí có weight:
  Văn chương (1.0), Cấu trúc/Plot (1.0), Nhân vật (1.0), Continuity (1.5), Filler/Pad (2.0)
Output: _strict_audit_report.json + bảng console
"""
import os, re, json, glob, unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------- helpers ----------
def vi_tokens(text):
    return len([t for t in text.split() if len(t) >= 2])

def norm(s):
    return unicodedata.normalize('NFC', s)

CH_RE = re.compile(r'^Chương\s+(\d+)\s*-\s*(.+)\.txt$')

def load_chapters():
    out = {}
    for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
        base = os.path.basename(p)
        m = CH_RE.match(norm(base))
        if not m:
            continue
        n = int(m.group(1))
        try:
            raw = open(p, encoding='utf-8').read()
        except UnicodeDecodeError:
            raw = open(p, encoding='utf-8', errors='replace').read()
        out[n] = {'path': p, 'file': base, 'title_file': m.group(2), 'raw': norm(raw)}
    return out

# ---------- filler / pad markers ----------
PAD_MARKERS = [
    r'### Lớp sâu', r'### Nhịp', r'### Thử nhỏ', r'### Thoại', r'### Khép',
    r'Trong nhật ký riêng số', r'Chốt ý nghĩa chương này',
    r'không chờ khẩu hiệu — chờ người dám chịu khi hỏng',
    r'Hùng tới sớm, Lan mở sổ, hiện trường nói trước phòng họp',
    r'chi tiết số \d+ gắn với', r'Nhịp \d+\.\d+ của',
    r'Bổ sung hiện trường ch\.', r'Thêm một lớp rà soát',
    r'sổ cái khớp system_ledger', r'hàng chuyển nội bộ khớp',
]
# Câu/khung sáo AI thường gặp — khó tính: tính là filler nhẹ
AI_TICS = [
    'se lạnh lúc tờ mờ', 'sổ trong túi vải', 'Ráp ngứa lòng bàn tay chai sạn',
    'Cót két cổng sắt mở mỗi sớm mai', 'Ve kêu rả rích trưa hè',
    'Lộp bộp thớt thái hành buổi sớm', 'Khói rơm ẩm mốc buổi sáng',
    'Gỗ mít ẩm trong tủ áo cũ', 'Nặng trĩu bả vai khiêng hàng quá sức',
    'Dầu máy trộn mồ hôi', 'Ghi chú: sổ cái',
]

STRUCT_TITLES = ['Mở rộng', 'Hoàn thành nhiệm vụ', 'Tổng kết', 'Bắt đầu Phần']

SENSORY = ['mùi','tiếng','ánh','nắng','mưa','gió','ấm','lạnh','khói','vị','chát','mặn','ẩm','rít','thơm']
CHAR_WORDS = ['mắt','tay','cười','khóc','gật','thở','nhìn','môi','vai','giọng']

def body_of(raw):
    # Header = first two '='*60 rules around "Chương N: Title".
    # Body = everything after the 2nd rule. Rejoin so internal '='*60
    # dividers (e.g. GHI NHẬN panels) don't truncate the body.
    parts = raw.split('=' * 60)
    if len(parts) >= 3:
        return ('=' * 60).join(parts[2:]).strip()
    return raw

def opening_sig(body, nwords=12):
    for line in body.split('\n'):
        line = line.strip()
        if len(line) > 20:
            return ' '.join(line.split()[:nwords])
    return ''

def main():
    chs = load_chapters()
    nums = sorted(chs)
    ledger = {}
    lp = os.path.join(ROOT, 'system_ledger.json')
    if os.path.exists(lp):
        try:
            ledger = json.load(open(lp, encoding='utf-8'))
        except Exception:
            ledger = {}

    outline = {}
    op = os.path.join(ROOT, 'chapter_outline.json')
    if os.path.exists(op):
        try:
            outline = json.load(open(op, encoding='utf-8'))
        except Exception:
            outline = {}

    # global passes
    openings = {}
    all_lines = defaultdict(list)   # line -> [ch...]
    recs = {}

    for n in nums:
        c = chs[n]
        raw = c['raw']
        body = body_of(raw)
        c['body'] = body
        toks = vi_tokens(body)
        chars = len(body)

        # header sanity
        hdr_ok = raw.lstrip().startswith('=' * 60)
        hm = re.search(r'Chương\s+(\d+)\s*:\s*(.+)', raw[:400])
        hdr_num_ok = bool(hm) and int(hm.group(1)) == n
        title_hdr = hm.group(2).strip() if hm else ''

        # content spill: text before header
        spill = 0
        idx = raw.find('=' * 60)
        if idx > 0:
            spill = len(raw[:idx].strip())

        # pad markers
        pad_hits = []
        for pat in PAD_MARKERS:
            k = len(re.findall(pat, body))
            if k:
                pad_hits.append((pat, k))
        pad_count = sum(k for _, k in pad_hits)

        tic_hits = []
        for t in AI_TICS:
            k = body.count(t)
            if k:
                tic_hits.append((t, k))
        tic_count = sum(k for _, k in tic_hits)

        # intra-chapter repetition
        # Exclude '='*N separator rules (header/panel dividers) — they are structural,
        # not prose repetition, and would falsely inflate maxrep/cross-dup on every chapter.
        lines = [l.strip() for l in body.split('\n')
                 if len(l.strip()) > 40 and set(l.strip()) != {'='}]
        cnt = Counter(lines)
        maxrep = max(cnt.values()) if cnt else 0
        dup_lines = sum(v - 1 for v in cnt.values() if v > 1)
        for l in set(lines):
            all_lines[l].append(n)

        # system panel
        panel = body.count('GHI NHẬN') + body.count('Hệ thống ghi nhận')
        has_panel = panel > 0
        double_panel = panel > 1

        # ledger check
        led = ledger.get('milestones', {}).get(str(n)) if isinstance(ledger, dict) else None
        exp_in = None
        me = re.findall(r'([\d\.]{2,})\s*EXP', body) + re.findall(r'EXP[:\s]+([\d\.]{2,})', body)
        if me:
            try:
                exp_in = int(me[-1].replace('.', ''))
            except Exception:
                exp_in = None

        # year check
        years = [int(y) for y in re.findall(r'\b(19[7-9]\d|20[0-2]\d)\b', body)]
        yr_main = Counter(years).most_common(1)[0][0] if years else None

        # anachronism (crude, by dominant year)
        # NOTE: case-sensitive whole-word match. Do NOT lowercase — "AI" (the tech)
        # must not collide with Vietnamese pronoun "ai" (who), which is ubiquitous.
        anach = []
        ANACH = {'Facebook': 2004, 'internet': 1997, 'điện thoại thông minh': 2008,
                 'smartphone': 2008, 'Mercedes': 1995, 'email': 1997, 'website': 1998,
                 'iPhone': 2007, 'trí tuệ nhân tạo': 2015, 'laptop': 1995}
        if yr_main:
            for w, y0 in ANACH.items():
                if re.search(r'\b' + re.escape(w) + r'\b', body) and yr_main < y0:
                    anach.append(f'{w.strip()}@{yr_main}')

        # prose density
        low = body.lower()
        sens = sum(low.count(w) for w in SENSORY)
        charw = sum(low.count(w) for w in CHAR_WORDS)
        per_k = max(chars / 1000.0, 0.001)
        sens_d = sens / per_k
        char_d = charw / per_k

        # dialogue
        dlg = len(re.findall(r'["\u201c\u2018]', body)) + body.count('“')
        dlg_lines = len([l for l in body.split('\n') if l.strip().startswith(('"', '“', '—', '–'))])

        # title-true: title keywords present in body
        tkeys = [w for w in re.split(r'[\s\-—–]+', c['title_file']) if len(w) >= 4]
        tkeys = [w for w in tkeys if w.lower() not in ('mở', 'rộng', 'hoàn', 'thành')]
        thit = sum(1 for w in tkeys if w.lower() in low)
        title_true = (thit / len(tkeys)) if tkeys else 1.0

        struct_title = any(s in c['title_file'] for s in STRUCT_TITLES)

        openings[n] = opening_sig(body)

        recs[n] = dict(
            n=n, file=c['file'], toks=toks, chars=chars,
            hdr_ok=hdr_ok, hdr_num_ok=hdr_num_ok, spill=spill,
            pad=pad_count, pad_hits=pad_hits[:5], tics=tic_count, tic_hits=tic_hits[:5],
            maxrep=maxrep, dup_lines=dup_lines,
            panel=panel, has_panel=has_panel, double_panel=double_panel,
            exp_in=exp_in, led=led, yr=yr_main, anach=anach,
            sens_d=round(sens_d, 2), char_d=round(char_d, 2),
            dlg=dlg, dlg_lines=dlg_lines,
            title_true=round(title_true, 2), struct_title=struct_title,
        )

    # cross-chapter duplicate lines
    cross = {l: v for l, v in all_lines.items() if len(v) >= 3}
    cross_by_ch = Counter()
    for l, v in cross.items():
        for n in v:
            cross_by_ch[n] += 1

    # duplicate openings
    open_cnt = Counter(openings.values())
    dup_open = {n: open_cnt[s] for n, s in openings.items() if s and open_cnt[s] >= 2}

    # ---------- scoring (strict) ----------
    rows = []
    for n in nums:
        r = recs[n]
        r['cross_dup'] = cross_by_ch.get(n, 0)
        r['dup_open'] = dup_open.get(n, 0)

        # --- Filler/Pad (weight 2.0) — khó tính nhất
        f = 10.0
        f -= min(6.0, r['pad'] * 2.0)
        f -= min(3.0, r['tics'] * 0.5)
        f -= min(3.0, max(0, r['maxrep'] - 1) * 1.0)
        f -= min(3.0, r['cross_dup'] * 0.25)
        f -= 1.5 if r['dup_open'] >= 2 else 0
        f -= 1.0 if r['double_panel'] else 0
        filler = max(0.0, f)

        # --- Continuity (weight 1.5)
        c = 10.0
        if not r['hdr_ok']: c -= 2.0
        if not r['hdr_num_ok']: c -= 1.5
        if r['spill'] > 0: c -= min(3.0, 1.0 + r['spill'] / 2000.0)
        if not r['has_panel']: c -= 1.5
        if r['double_panel']: c -= 1.0
        c -= min(2.5, len(r['anach']) * 1.25)
        if r['led'] and r['exp_in'] is not None:
            tgt = r['led'].get('exp')
            if tgt and abs(r['exp_in'] - tgt) > max(500, tgt * 0.1):
                c -= 1.5
        cont = max(0.0, c)

        # --- Văn chương (weight 1.0)
        # Calibrated to real VI-prose norms: hand-verified best chapter (ch1, 8.5/10)
        # has sens_d 3.47 / char_d 5.14 / dlg 41. Full credit at those floors; genuinely
        # thin chapters (sens_d<2, dlg<6) still lose points.
        p = 10.0
        if r['toks'] < 3200: p -= min(3.0, (3200 - r['toks']) / 350.0)
        if r['sens_d'] < 3.5: p -= min(3.0, (3.5 - r['sens_d']) * 1.4)
        if r['char_d'] < 5.0: p -= min(2.0, (5.0 - r['char_d']) * 0.6)
        if r['dlg_lines'] < 10: p -= min(2.0, (10 - r['dlg_lines']) * 0.25)
        p -= min(2.0, r['tics'] * 0.35)
        prose = max(0.0, p)

        # --- Cấu trúc / Plot (weight 1.0)
        s = 10.0
        if r['struct_title']: s -= 1.5          # tiêu đề kiểu báo cáo
        s -= (1 - r['title_true']) * 3.0        # title không hiện trường hóa
        if r['dup_open'] >= 2: s -= 1.5
        if r['toks'] < 3000: s -= 1.0
        if r['cross_dup'] >= 5: s -= 1.5
        plot = max(0.0, s)

        # --- Nhân vật (weight 1.0)
        # Calibrated: ch1 (8.5/10) has char_d 5.14, dlg 41. Full credit at char_d>=5, dlg>=10.
        h = 10.0
        if r['dlg_lines'] < 10: h -= min(3.0, (10 - r['dlg_lines']) * 0.3)
        if r['char_d'] < 5.0: h -= min(3.0, (5.0 - r['char_d']) * 0.7)
        names = sum(1 for nm in ['Lan', 'Hùng', 'bà Hà', 'Mai', 'Hạnh', 'Minh', 'Tâm'] if nm in r_body(chs, n))
        if names < 3: h -= (3 - names) * 0.8
        char = max(0.0, h)

        w = (prose * 1.0 + plot * 1.0 + char * 1.0 + cont * 1.5 + filler * 2.0) / 6.5
        r.update(prose=round(prose, 2), plot=round(plot, 2), char=round(char, 2),
                 cont=round(cont, 2), filler=round(filler, 2), score=round(w, 2))
        rows.append(r)

    avg = lambda k: round(sum(x[k] for x in rows) / len(rows), 2)
    summary = dict(
        chapters=len(rows),
        weighted=avg('score'),
        prose=avg('prose'), plot=avg('plot'), char=avg('char'),
        cont=avg('cont'), filler=avg('filler'),
        toks_avg=int(sum(x['toks'] for x in rows) / len(rows)),
        short_lt3000=sum(1 for x in rows if x['toks'] < 3000),
        pad_total=sum(x['pad'] for x in rows),
        pad_ch=sum(1 for x in rows if x['pad'] > 0),
        tics_total=sum(x['tics'] for x in rows),
        tics_ch=sum(1 for x in rows if x['tics'] > 0),
        spill_ch=sum(1 for x in rows if x['spill'] > 0),
        no_panel=sum(1 for x in rows if not x['has_panel']),
        double_panel=sum(1 for x in rows if x['double_panel']),
        anach_ch=sum(1 for x in rows if x['anach']),
        dup_open_ch=sum(1 for x in rows if x['dup_open'] >= 2),
        cross_dup_lines=len(cross),
        struct_titles=sum(1 for x in rows if x['struct_title']),
        sens_d_avg=avg('sens_d'), char_d_avg=avg('char_d'),
        maxrep_ge3=sum(1 for x in rows if x['maxrep'] >= 3),
        below9=sum(1 for x in rows if x['score'] < 9.0),
        below8=sum(1 for x in rows if x['score'] < 8.0),
        below7=sum(1 for x in rows if x['score'] < 7.0),
        below5=sum(1 for x in rows if x['score'] < 5.0),
    )

    worst = sorted(rows, key=lambda x: x['score'])[:40]
    out = dict(summary=summary, rows=rows, worst=[{k: w[k] for k in
               ('n','file','score','prose','plot','char','cont','filler','toks','pad','tics','spill','cross_dup','dup_open','anach')} for w in worst],
               cross_dup_top=sorted(({'line': l[:110], 'chs': len(v)} for l, v in cross.items()),
                                    key=lambda z: -z['chs'])[:30])
    json.dump(out, open(os.path.join(ROOT, '_strict_audit_report.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('=== STRICT AUDIT SUMMARY ===')
    for k, v in summary.items():
        print(f'{k:18} {v}')
    print('\n=== 25 CHƯƠNG TỆ NHẤT ===')
    print(f"{'ch':>4} {'score':>5} {'văn':>5} {'plot':>5} {'nv':>5} {'cont':>5} {'fill':>5} {'toks':>5} {'pad':>4} {'tic':>4} {'spill':>6}")
    for w in worst[:25]:
        print(f"{w['n']:>4} {w['score']:>5} {w['prose']:>5} {w['plot']:>5} {w['char']:>5} {w['cont']:>5} {w['filler']:>5} {w['toks']:>5} {w['pad']:>4} {w['tics']:>4} {w['spill']:>6}")
    print('\n=== TOP CROSS-CHAPTER DUPLICATE LINES ===')
    for d in out['cross_dup_top'][:12]:
        print(f"{d['chs']:>4} ch | {d['line']}")


_body_cache = {}
def r_body(chs, n):
    if n not in _body_cache:
        _body_cache[n] = chs[n]['body']
    return _body_cache[n]


if __name__ == '__main__':
    main()
