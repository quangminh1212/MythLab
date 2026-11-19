# -*- coding: utf-8 -*-
import glob, os, sys, re
sys.path.insert(0, r'c:\Dev\MythLab\Niên Đại Thương Gia')
from audit_all import audit_chapter, body_of

ROOT = r'c:\Dev\MythLab\Niên Đại Thương Gia'

repeated_dialogues = {}
repeated_sensory = {}
inline_injections = {}

for n in range(1, 361):
    res = audit_chapter(n)
    if not res: continue
    raw = open(res['path'], encoding='utf-8').read()
    body = body_of(raw)
    
    for line in body.splitlines():
        l = line.strip()
        if not l: continue
        if l.startswith(('—', '–', '"', '“')):
            repeated_dialogues[l] = repeated_dialogues.get(l, 0) + 1
        elif any(w in l for w in ['Mùi khói rơm', 'Ánh nắng mờ nhạt', 'Vị chát thanh', 'Mùi keo dán', 'Tiếng gió lùa', 'Tiếng bước chân', 'Cái lạnh hanh khô', 'Mùi thơm dịu']):
            repeated_sensory[l] = repeated_sensory.get(l, 0) + 1
        elif 'đôi mắt đăm chiêu' in l or 'đôi tay chai sạn' in l or 'mỉm cười dịu dàng' in l:
            inline_injections[l] = inline_injections.get(l, 0) + 1

top_dlg = sorted([(c, text) for text, c in repeated_dialogues.items() if c > 5], reverse=True)
top_sens = sorted([(c, text) for text, c in repeated_sensory.items() if c > 5], reverse=True)
top_inline = sorted([(c, text) for text, c in inline_injections.items() if c > 5], reverse=True)

print(f"=== TOP REPEATED DIALOGUE LINES (Occurrences > 5) ===")
print(f"Total distinct template dialogue lines found: {len(top_dlg)}")
for c, txt in top_dlg[:20]:
    print(f"  [{c:3d} chs] {txt}")

print(f"\n=== TOP REPEATED SENSORY LINES (Occurrences > 5) ===")
print(f"Total distinct template sensory lines found: {len(top_sens)}")
for c, txt in top_sens[:15]:
    print(f"  [{c:3d} chs] {txt}")

print(f"\n=== TOP INLINE INJECTIONS / PHRASES (Occurrences > 5) ===")
print(f"Total distinct inline template phrases found: {len(top_inline)}")
for c, txt in top_inline[:15]:
    print(f"  [{c:3d} chs] {txt}")
