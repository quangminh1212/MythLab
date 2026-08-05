# -*- coding: utf-8 -*-
import os, glob, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
target_dir = r"c:\Dev\XLab_MTC\Niên Đại Thương Gia"

paragraph_map = defaultdict(list)
total_paras = 0

for ch in range(1, 361):
    files = glob.glob(os.path.join(target_dir, f"Chương {ch} - *.txt"))
    if not files:
        files = glob.glob(os.path.join(target_dir, f"Chương {ch:02d} - *.txt"))
    if not files: continue
    
    p = files[0]
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80 and not p.strip().startswith("=")]
    for para in paras:
        total_paras += 1
        paragraph_map[para].append(ch)

duplicate_paras = {para: chs for para, chs in paragraph_map.items() if len(chs) > 1}

print(f"Total paragraphs analyzed across 360 chapters: {total_paras}")
print(f"Unique paragraphs count: {len(paragraph_map)}")
print(f"Duplicate paragraphs count (appearing in >1 chapter): {len(duplicate_paras)}")

if duplicate_paras:
    print("\nSample of Duplicate Paragraphs found across chapters:")
    for para, chs in list(duplicate_paras.items())[:10]:
        print(f"  - Appears in chapters {chs}: '{para[:100]}...'")
else:
    print("Zero cross-chapter duplicate paragraphs found!")
