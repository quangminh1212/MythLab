# -*- coding: utf-8 -*-
import glob, os, sys, re

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

DUP_SET = set(k for k, v in line_counts.items() if v > 1)

words_list = []
dlg_list = []
sens_list = []
char_list = []

for n in range(1, 361):
    files = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
    if not files: files = glob.glob(os.path.join(ROOT, f'Chương {n:02d} - *.txt'))
    if not files: continue
    raw = open(files[0], encoding='utf-8').read()
    
    # Strip template sentences
    lines = raw.splitlines()
    clean = []
    for l in lines:
        s = l.strip()
        if s in DUP_SET: continue
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
    
    words_list.append(toks)
    dlg_list.append(dlg_lines)
    sens_list.append(sens_d)
    char_list.append(char_d)

print(f"Post-stripping Metrics across 360 chapters:")
print(f"Words: min={min(words_list)}, max={max(words_list)}, avg={sum(words_list)/len(words_list):.1f}")
print(f"Under 3100 words: {sum(1 for w in words_list if w < 3100)}")
print(f"Under 3000 words: {sum(1 for w in words_list if w < 3000)}")
print(f"Dialogue lines < 10: {sum(1 for d in dlg_list if d < 10)}")
print(f"Sensory density < 3.5: {sum(1 for s in sens_list if s < 3.5)}")
print(f"Char action density < 5.0: {sum(1 for c in char_list if c < 5.0)}")
