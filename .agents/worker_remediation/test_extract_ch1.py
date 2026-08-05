# -*- coding: utf-8 -*-
import sys, os, glob, re, json, random

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)

from audit_all import audit_chapter, body_of, SENSORY, CHAR_WORDS

# Load outline & ledger
with open(os.path.join(ROOT, 'chapter_outline.json'), encoding='utf-8') as f:
    OUTLINE = json.load(f)['chapters']
with open(os.path.join(ROOT, 'system_ledger.json'), encoding='utf-8') as f:
    LEDGER = json.load(f)['chapters']

# Load duplicate set
line_counts = {}
for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
    with open(p, encoding='utf-8') as f:
        for l in f:
            line = l.strip()
            if len(line) > 15 and not line.startswith('=' * 10) and not line.startswith('-' * 10) and not line.startswith('Chương ') and not line.startswith('GHI NHẬN'):
                line_counts[line] = line_counts.get(line, 0) + 1

DUP_SET = set(k for k, v in line_counts.items() if v > 1)

def get_clean_base_body(raw_text):
    lines = raw_text.splitlines()
    clean = []
    in_body = False
    for l in lines:
        s = l.strip()
        if s.startswith('=' * 10):
            in_body = True
            continue
        if s.startswith('-' * 10) or 'GHI NHẬN:' in s:
            break
        if s in DUP_SET:
            continue
        if 'Hùng nhìn thẳng vào đối phương' in s or 'Khánh đứng tựa ban công' in s:
            continue
        if s.startswith('— Hùng nhìn Lan') or s.startswith('— Lan gật đầu') or s.startswith('— Bà Hà nhìn'):
            continue
        if s:
            clean.append(l)
    return clean

# Test on chapter 1
p = os.path.join(ROOT, 'Chương 1 - Tỉnh lại.txt')
raw_text = open(p, encoding='utf-8').read()
clean_lines = get_clean_base_body(raw_text)
print("Original clean lines count:", len(clean_lines))
print("Original clean words:", len(' '.join(clean_lines).split()))
