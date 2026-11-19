# -*- coding: utf-8 -*-
import sys, os, glob, re, json

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\MythLab\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)

from audit_all import audit_chapter, body_of, SENSORY, CHAR_WORDS

# Load outline and ledger
with open(os.path.join(ROOT, 'chapter_outline.json'), encoding='utf-8') as f:
    OUTLINE = json.load(f)['chapters']
with open(os.path.join(ROOT, 'system_ledger.json'), encoding='utf-8') as f:
    LEDGER = json.load(f)['chapters']

# Duplicate lines to strip
line_counts = {}
for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
    with open(p, encoding='utf-8') as f:
        for l in f:
            line = l.strip()
            if len(line) > 15 and not line.startswith('=' * 10) and not line.startswith('-' * 10) and not line.startswith('Chương ') and not line.startswith('GHI NHẬN'):
                line_counts[line] = line_counts.get(line, 0) + 1

DUP_SET = set(k for k, v in line_counts.items() if v > 1)

print(f"Loaded {len(OUTLINE)} outlines, {len(LEDGER)} ledgers, {len(DUP_SET)} duplicate lines to purge.")
