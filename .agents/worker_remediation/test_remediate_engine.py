# -*- coding: utf-8 -*-
import sys, os, glob, re, json, random
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)

from audit_all import audit_chapter, body_of, SENSORY, CHAR_WORDS

# Load outline and ledger
with open(os.path.join(ROOT, 'chapter_outline.json'), encoding='utf-8') as f:
    outline = json.load(f)['chapters']
with open(os.path.join(ROOT, 'system_ledger.json'), encoding='utf-8') as f:
    ledger = json.load(f)['chapters']

# Test chapter 1
ch_num = 1
ch_out = outline[str(ch_num)]
ch_led = ledger[str(ch_num)]

print("Testing remediation engine for Chapter", ch_num)
print("Cast:", ch_out['cast'])
print("Year:", ch_out['year'])
print("Plot:", ch_out['plot'])
print("Conflict:", ch_out['conflict'])
