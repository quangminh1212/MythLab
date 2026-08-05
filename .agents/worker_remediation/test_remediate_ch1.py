# -*- coding: utf-8 -*-
import sys, os, re, json, glob

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)

from audit_all import audit_chapter, body_of, SENSORY, CHAR_WORDS

# Load outline and ledger
with open(os.path.join(ROOT, 'chapter_outline.json'), encoding='utf-8') as f:
    outline = json.load(f)['chapters']
with open(os.path.join(ROOT, 'system_ledger.json'), encoding='utf-8') as f:
    ledger = json.load(f)['chapters']

ch1_outline = outline['1']
ch1_ledger = ledger['1']

print("Ch 1 Outline:", json.dumps(ch1_outline, ensure_ascii=False, indent=2))
print("Ch 1 Ledger:", json.dumps(ch1_ledger, ensure_ascii=False, indent=2))
