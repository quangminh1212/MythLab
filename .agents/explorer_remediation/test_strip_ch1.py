# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r'c:\Dev\MythLab\Niên Đại Thương Gia')
from audit_all import body_of, SENSORY, CHAR_WORDS

raw = open(r'c:\Dev\MythLab\Niên Đại Thương Gia\Chương 1 - Tỉnh lại.txt', encoding='utf-8').read()

# Strip template block
lines = raw.splitlines()
clean_lines = []
for line in lines:
    if '— Bà Hà nhìn hai con' in line or '— Hùng nhìn Lan' in line or 'Mùi khói rơm ẩm mốc' in line or line.startswith('— '):
        continue
    clean_lines.append(line)

clean_raw = '\n'.join(clean_lines)
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

print(f"Stripped Ch 1 Toks: {toks}, sens_d: {sens_d:.2f}, char_d: {char_d:.2f}, dlg_lines: {dlg_lines}")
