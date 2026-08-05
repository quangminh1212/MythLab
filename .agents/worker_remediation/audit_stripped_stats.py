# -*- coding: utf-8 -*-
import sys, os, glob, re, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)
from audit_all import audit_chapter, body_of, SENSORY, CHAR_WORDS

# Collect all duplicate lines across chapters
line_counts = {}
for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
    with open(p, encoding='utf-8') as f:
        for l in f:
            line = l.strip()
            if len(line) > 15 and not line.startswith('=' * 10) and not line.startswith('-' * 10) and not line.startswith('Chương ') and not line.startswith('GHI NHẬN'):
                line_counts[line] = line_counts.get(line, 0) + 1

dup_set = set(k for k, v in line_counts.items() if v > 1)
print(f"Total duplicate lines identified: {len(dup_set)}")

low_dlg = []
low_words = []
low_sens = []
low_char = []

for n in range(1, 361):
    files = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
    if not files: files = glob.glob(os.path.join(ROOT, f'Chương {n:02d} - *.txt'))
    if not files: continue
    
    raw = open(files[0], encoding='utf-8').read()
    lines = raw.splitlines()
    clean = []
    for l in lines:
        s = l.strip()
        if s in dup_set: continue
        if 'Hùng nhìn thẳng vào đối phương' in s or 'Khánh đứng tựa ban công' in s: continue
        clean.append(l)
    
    clean_raw = '\n'.join(clean)
    body = body_of(clean_raw)
    toks = len(body.split())
    chars = len(body)
    low = body.lower()
    sens = sum(low.count(w) for w in SENSORY)
    charw = sum(low.count(w) for w in CHAR_WORDS)
    per_k = max(chars / 1000.0, 0.001)
    sens_d = sens / per_k
    char_d = charw / per_k
    dlg_lines = len([l for l in body.split('\n') if l.strip().startswith(('"', '“', '—', '–'))])
    
    if toks < 3000: low_words.append((n, toks))
    if dlg_lines < 10: low_dlg.append((n, dlg_lines))
    if sens_d < 3.5: low_sens.append((n, sens_d))
    if char_d < 5.0: low_char.append((n, char_d))

print(f"Chapters under 3000 words: {len(low_words)}")
print(f"Chapters with < 10 dialogue lines: {len(low_dlg)}")
print(f"Chapters with sens_d < 3.5: {len(low_sens)}")
print(f"Chapters with char_d < 5.0: {len(low_char)}")
