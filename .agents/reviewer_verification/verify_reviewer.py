# -*- coding: utf-8 -*-
import os, glob, re, json, unicodedata, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)
from audit_all import audit_chapter

PAD_MARKERS = [
    r'### Lớp sâu', r'### Nhịp', r'### Thử nhỏ', r'### Thoại', r'### Khép',
    r'Trong nhật ký riêng số', r'Chốt ý nghĩa chương này',
    r'không chờ khẩu hiệu', r'chi tiết số \d+ gắn với', r'Nhịp \d+\.\d+ của',
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

def norm(s):
    return unicodedata.normalize('NFC', s)

def body_of(raw):
    parts = raw.split('=' * 60)
    if len(parts) >= 3:
        return ('=' * 60).join(parts[2:]).strip()
    return raw

def check_ch(n):
    files = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
    if not files:
        files = glob.glob(os.path.join(ROOT, f'Chương {n:02d} - *.txt'))
    if not files:
        return None, 'File not found'
    p = files[0]
    raw = norm(open(p, encoding='utf-8').read())
    body = body_of(raw)
    
    toks = len(body.split())
    chars = len(body)
    hdr_ok = raw.lstrip().startswith('=' * 60)
    hm = re.search(r'Chương\s+(\d+)\s*:\s*(.+)', raw[:400])
    hdr_num_ok = bool(hm) and int(hm.group(1)) == n
    
    pad_hits = sum(len(re.findall(pat, body)) for pat in PAD_MARKERS)
    tic_hits = sum(body.count(t) for t in AI_TICS)
    
    lines = [l.strip() for l in body.split('\n') if len(l.strip()) > 40 and set(l.strip()) != {'='}]
    cnt = Counter(lines)
    maxrep = max(cnt.values()) if cnt else 0
    
    panel_count = body.count('GHI NHẬN') + body.count('Hệ thống ghi nhận')
    
    low = body.lower()
    sens = sum(low.count(w) for w in SENSORY)
    charw = sum(low.count(w) for w in CHAR_WORDS)
    per_k = max(chars / 1000.0, 0.001)
    sens_d = round(sens / per_k, 2)
    char_d = round(charw / per_k, 2)
    
    dlg_lines = len([l for l in body.split('\n') if l.strip().startswith(('"', '“', '—', '–'))])
    
    res = {
        'n': n,
        'file': os.path.basename(p),
        'toks': toks,
        'hdr_ok': hdr_ok and hdr_num_ok,
        'panel_count': panel_count,
        'dlg_lines': dlg_lines,
        'sens_d': sens_d,
        'char_d': char_d,
        'pad_hits': pad_hits,
        'tic_hits': tic_hits,
        'maxrep': maxrep
    }
    return res, None

if __name__ == '__main__':
    sample_nums = [1, 50, 100, 150, 200, 250, 300, 360]
    print('=== SAMPLE VERIFICATION ===')
    for n in sample_nums:
        r, err = check_ch(n)
        print(f"Ch {n:03d} | Toks={r['toks']} | Hdr={r['hdr_ok']} | Panel={r['panel_count']} | Dlg={r['dlg_lines']} | SensD={r['sens_d']} | CharD={r['char_d']} | Pad={r['pad_hits']} | Tic={r['tic_hits']} | Rep={r['maxrep']} | File={r['file']}")

    print('\n=== ALL 360 VERIFICATION ===')
    issues = []
    for n in range(1, 361):
        r, err = check_ch(n)
        if err:
            issues.append((n, err))
            continue
        if not (3000 <= r['toks'] <= 4200):
            issues.append((n, f"toks={r['toks']}"))
        if not r['hdr_ok']:
            issues.append((n, "hdr_bad"))
        if r['panel_count'] != 1:
            issues.append((n, f"panel={r['panel_count']}"))
        if r['dlg_lines'] < 10:
            issues.append((n, f"dlg={r['dlg_lines']}"))
        if r['sens_d'] < 3.5:
            issues.append((n, f"sens_d={r['sens_d']}"))
        if r['char_d'] < 5.0:
            issues.append((n, f"char_d={r['char_d']}"))
        if r['pad_hits'] > 0:
            issues.append((n, f"pad_hits={r['pad_hits']}"))
        if r['tic_hits'] > 0:
            issues.append((n, f"tic_hits={r['tic_hits']}"))
        if r['maxrep'] > 1:
            issues.append((n, f"maxrep={r['maxrep']}"))

    print('Total issues across all 360 chapters:', len(issues))

    print('\n=== CROSS-CHECK WITH SCORE95_FINAL.JSON ===')
    score_json_path = os.path.join(ROOT, 'score95_final.json')
    score_data = json.load(open(score_json_path, encoding='utf-8'))
    json_ch = {c['n']: c for c in score_data.get('chapters', [])}
    
    diffs = []
    for n in range(1, 361):
        live = audit_chapter(n)
        cached = json_ch.get(n)
        if not cached:
            diffs.append((n, "missing in json"))
            continue
        if abs(live['score'] - cached['score']) > 0.01:
            diffs.append((n, f"live={live['score']} json={cached['score']}"))
    
    print("Diffs count between live audit and score95_final.json:", len(diffs))
