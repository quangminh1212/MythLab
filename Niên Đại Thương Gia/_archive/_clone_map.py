# -*- coding: utf-8 -*-
"""
CLONE MAP — Niên Đại Thương Gia
Xác định chính xác từng chương clone: câu nào là clone (xuất hiện >=5 chương),
câu nào unique, % clone, và trích core (unique lines) để subagent giữ lại.
Output: _clone_map.json + console table.
"""
import os, re, json, glob, unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
CH_RE = re.compile(r'^Chương\s+(\d+)\s*-\s*(.+)\.txt$')

def norm(s):
    return unicodedata.normalize('NFC', s)

def vi_tokens(text):
    return len([t for t in text.split() if len(t) >= 2])

def load():
    out = {}
    for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
        base = norm(os.path.basename(p))
        m = CH_RE.match(base)
        if not m:
            continue
        n = int(m.group(1))
        raw = norm(open(p, encoding='utf-8', errors='replace').read())
        out[n] = {'path': p, 'file': base, 'raw': raw}
    return out

def body_of(raw):
    parts = raw.split('=' * 60)
    if len(parts) >= 3:
        return ('=' * 60).join(parts[2:]).strip()
    return raw

def main():
    chs = load()
    nums = sorted(chs)

    # collect long lines per chapter
    line_to_chs = defaultdict(set)
    ch_lines = {}
    for n in nums:
        body = body_of(chs[n]['raw'])
        chs[n]['body'] = body
        lines = [l.strip() for l in body.split('\n') if len(l.strip()) >= 40]
        ch_lines[n] = lines
        for l in set(lines):
            line_to_chs[l].add(n)

    # clone line = appears in >=5 chapters
    CLONE_THRESHOLD = 5
    clone_lines = {l for l, s in line_to_chs.items() if len(s) >= CLONE_THRESHOLD}

    # per chapter: clone char ratio
    rows = []
    clone_ch = []
    for n in nums:
        body = chs[n]['body']
        lines = ch_lines[n]
        total_chars = sum(len(l) for l in lines) or 1
        clone_chars = sum(len(l) for l in lines if l in clone_lines)
        n_clone_lines = sum(1 for l in lines if l in clone_lines)
        ratio = clone_chars / total_chars
        toks = vi_tokens(body)
        rows.append(dict(n=n, file=chs[n]['file'], toks=toks,
                         clone_lines=n_clone_lines, total_lines=len(lines),
                         clone_ratio=round(ratio, 3)))
        if n_clone_lines >= 3 or ratio >= 0.15:
            clone_ch.append(n)

    # build detailed map for clone chapters
    detail = {}
    for n in clone_ch:
        lines = ch_lines[n]
        unique = [l for l in lines if l not in clone_lines]
        cloned = [l for l in lines if l in clone_lines]
        detail[n] = dict(
            file=chs[n]['file'],
            toks=next(r['toks'] for r in rows if r['n'] == n),
            clone_ratio=next(r['clone_ratio'] for r in rows if r['n'] == n),
            n_clone=len(cloned), n_unique=len(unique),
            unique_lines=unique,          # CORE to preserve
            clone_samples=cloned[:8],
        )

    out = dict(
        clone_threshold=CLONE_THRESHOLD,
        n_clone_lines_global=len(clone_lines),
        clone_chapters=sorted(clone_ch),
        n_clone_chapters=len(clone_ch),
        rows=rows,
        detail=detail,
    )
    json.dump(out, open(os.path.join(ROOT, '_clone_map.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('=== CLONE MAP ===')
    print('clone chapters:', len(clone_ch))
    print('global clone lines (>=5ch):', len(clone_lines))
    print()
    print(f"{'ch':>4} {'toks':>5} {'clone%':>7} {'cloneL':>7} {'uniqL':>6}")
    for n in sorted(clone_ch):
        d = detail[n]
        print(f"{n:>4} {d['toks']:>5} {d['clone_ratio']*100:>6.1f}% {d['n_clone']:>7} {d['n_unique']:>6}")

if __name__ == '__main__':
    main()
