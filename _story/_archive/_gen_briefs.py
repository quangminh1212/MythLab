# -*- coding: utf-8 -*-
"""
Unified clone-map + brief generator for Niên Đại Thương Gia.
Single source of truth: compute the global clone-line set ONCE, split body
identically, then emit a brief per chapter >= THRESHOLD clone%.
Brief = title, ledger year/EXP/space, exact clone lines to DELETE,
unique core lines to PRESERVE.
"""
import os, re, json, glob, unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
BRIEF_DIR = os.path.join(ROOT, '_briefs')
THRESHOLD = 15.0          # emit brief for chapters with >= this clone%
MIN_CH_FOR_CLONE = 5      # a line is "clone" if it appears in >= this many chapters
MIN_LINE_LEN = 40

def norm(s):
    return unicodedata.normalize('NFC', s)

CH_RE = re.compile(r'^Chương\s+(\d+)\s*-\s*(.+)\.txt$')

def vi_tokens(text):
    return len([t for t in text.split() if len(t) >= 2])

def body_of(raw):
    parts = raw.split('=' * 60)
    return (('=' * 60).join(parts[2:]).strip() if len(parts) >= 3 else raw)

def long_lines(body):
    return [l.strip() for l in body.split('\n') if len(l.strip()) >= MIN_LINE_LEN]

def load():
    out = {}
    for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
        base = norm(os.path.basename(p))
        m = CH_RE.match(base)
        if not m:
            continue
        raw = norm(open(p, encoding='utf-8', errors='replace').read())
        out[int(m.group(1))] = dict(path=p, file=base, title=m.group(2),
                                    raw=raw, body=body_of(raw))
    return out

def main():
    chs = load()
    nums = sorted(chs)

    ledger = {}
    lp = os.path.join(ROOT, 'system_ledger.json')
    if os.path.exists(lp):
        try:
            ledger = json.load(open(lp, encoding='utf-8')).get('milestones', {})
        except Exception:
            ledger = {}

    def led_for(n):
        # nearest milestone <= n
        best = None
        for k in sorted(ledger, key=lambda x: int(x)):
            if int(k) <= n:
                best = ledger[k]
        return best or {}

    # ---- global clone set (line -> set of chapters) ----
    line_chs = {}
    for n in nums:
        for l in set(long_lines(chs[n]['body'])):
            line_chs.setdefault(l, set()).add(n)
    clone_set = {l for l, s in line_chs.items() if len(s) >= MIN_CH_FOR_CLONE}

    # ---- per-chapter clone% ----
    rows = []
    for n in nums:
        ll = long_lines(chs[n]['body'])
        if not ll:
            continue
        clone_hits = [l for l in ll if l in clone_set]
        pct = round(100.0 * len(clone_hits) / len(ll), 1)
        rows.append((n, vi_tokens(chs[n]['body']), pct, len(set(clone_hits)),
                     len(set(ll)) - len(set(clone_hits))))

    targets = sorted([r for r in rows if r[2] >= THRESHOLD], key=lambda x: -x[2])

    os.makedirs(BRIEF_DIR, exist_ok=True)
    # clear stale briefs
    for f in glob.glob(os.path.join(BRIEF_DIR, 'brief_*.txt')):
        os.remove(f)
    for f in glob.glob(os.path.join(BRIEF_DIR, 'ch*.md')):
        os.remove(f)

    def year_of(body):
        ys = [int(y) for y in re.findall(r'\b(19[7-9]\d|20[0-2]\d)\b', body)]
        return Counter(ys).most_common(1)[0][0] if ys else None

    for n, toks, pct, cl, uq in targets:
        c = chs[n]
        led = led_for(n)
        body = c['body']
        seen_clone, seen_uniq = set(), set()
        clone_lines, uniq_lines = [], []
        for l in long_lines(body):
            if l in clone_set:
                if l not in seen_clone:
                    seen_clone.add(l); clone_lines.append(l)
            else:
                if l not in seen_uniq:
                    seen_uniq.add(l); uniq_lines.append(l)
        yr = year_of(body)
        out = []
        out.append(f"# BRIEF — Chương {n}: {c['title']}")
        out.append("")
        out.append(f"FILE (exact): {c['file']}")
        out.append(f"Ledger: EXP={led.get('exp','?')}, space={led.get('space','?')}m²")
        out.append(f"Năm chủ đạo hiện tại trong prose: {yr}")
        out.append(f"Token hiện tại: {toks} | Clone: {pct}% ({cl} câu lặp)")
        out.append("")
        out.append("## NHIỆM VỤ")
        out.append("Viết lại chương này thành CẢNH MỚI nguyên bản. Giữ đúng: tiêu đề, "
                   "sự kiện lõi, năm, nhân vật, số liệu hệ thống. XÓA HẾT các câu clone "
                   "bên dưới (lặp nguyên văn ở nhiều chương khác) — thay bằng văn tả "
                   "cảnh/đối thoại/nội tâm RIÊNG của chương này. Không để BẤT KỲ câu "
                   "clone nào còn nguyên văn. >=3200 token tiếng Việt. Giữ đúng 1 panel "
                   "hệ thống ở cuối (giữ số liệu EXP/space/năm đúng ledger).")
        out.append("")
        out.append("## CÂU CLONE — PHẢI XÓA / VIẾT LẠI HOÀN TOÀN")
        for l in clone_lines:
            out.append(f"- {l[:300]}")
        out.append("")
        out.append("## LÕI UNIQUE — GIỮ Ý (sự kiện thật, trau chuốt lại câu chữ được)")
        for l in uniq_lines:
            out.append(f"- {l[:300]}")
        open(os.path.join(BRIEF_DIR, f'brief_{n}.md'), 'w',
             encoding='utf-8').write('\n'.join(out))

    # summary
    print(f"clone_set_lines(>= {MIN_CH_FOR_CLONE}ch): {len(clone_set)}")
    print(f"targets(>= {THRESHOLD}% clone): {len(targets)}")
    print("target list:", ' '.join(str(r[0]) for r in sorted(targets)))
    json.dump({'threshold': THRESHOLD,
               'targets': [{'n': r[0], 'toks': r[1], 'clone_pct': r[2]} for r in sorted(targets)]},
              open(os.path.join(ROOT, '_brief_targets.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
