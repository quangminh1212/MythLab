# -*- coding: utf-8 -*-
import os, glob, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
target_dir = r"c:\Dev\XLab_MTC\Niên Đại Thương Gia"

chapter_files = []
for ch in range(1, 361):
    files = glob.glob(os.path.join(target_dir, f"Chương {ch} - *.txt"))
    if not files:
        files = glob.glob(os.path.join(target_dir, f"Chương {ch:02d} - *.txt"))
    if files:
        chapter_files.append((ch, files[0]))

total_dataset_words = 0
total_template_words = 0

global_para_counts = Counter()

for ch, path in chapter_files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    total_dataset_words += len(text.split())
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50 and not p.strip().startswith("=")]
    for para in set(paras):
        global_para_counts[para] += 1

template_paras = {para: count for para, count in global_para_counts.items() if count >= 10}

block_14_dlg_count = 0
block_sensory_count = 0

for ch, path in chapter_files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if "Dây chuyền máy móc mới vận hành rất trơn tru" in text:
        block_14_dlg_count += 1
    if "Vị chát thanh của bát nước chè xanh tỏa khói ấm" in text:
        block_sensory_count += 1
    
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50 and not p.strip().startswith("=")]
    for p in paras:
        if p in template_paras:
            total_template_words += len(p.split())

print("=== DEEP EVIDENCE METRICS ===")
print(f"Total Dataset Word Count: {total_dataset_words:,} words")
print(f"Total Template Filler Word Count: {total_template_words:,} words")
print(f"Template Filler Percentage: {total_template_words / total_dataset_words * 100:.2f}%")
print(f"Chapters with 14-sentence dialogue block: {block_14_dlg_count} / 360 ({block_14_dlg_count/360*100:.1f}%)")
print(f"Chapters with sensory block: {block_sensory_count} / 360 ({block_sensory_count/360*100:.1f}%)")
