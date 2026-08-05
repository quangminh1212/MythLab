# -*- coding: utf-8 -*-
import os, glob, sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
target_dir = r"c:\Dev\XLab_MTC\Niên Đại Thương Gia"

chapter_files = []
for ch in range(1, 361):
    files = glob.glob(os.path.join(target_dir, f"Chương {ch} - *.txt"))
    if not files:
        files = glob.glob(os.path.join(target_dir, f"Chương {ch:02d} - *.txt"))
    if files:
        chapter_files.append((ch, files[0]))

print(f"Total chapter files found: {len(chapter_files)}")

# Global paragraph count map
global_para_counts = Counter()
for ch, path in chapter_files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50 and not p.strip().startswith("=")]
    for para in set(paras):
        global_para_counts[para] += 1

# Identify template paragraphs that appear in >= 10 chapters
template_paras = {para: count for para, count in global_para_counts.items() if count >= 10}

print(f"\nFound {len(template_paras)} distinct TEMPLATE PARAGRAPHS that repeat across >= 10 chapters.")
print("\nTop 15 Most Repeated Template Paragraphs:")
for para, count in sorted(template_paras.items(), key=lambda x: x[1], reverse=True)[:15]:
    first_line = para.split("\n")[0]
    print(f"  [{count} chapters] (len {len(para)} chars): {first_line[:90]}...")

# Per-chapter analysis of template pollution
chapter_pollution = []
for ch, path in chapter_files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    total_words = len(text.split())
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50 and not p.strip().startswith("=")]
    template_words = 0
    template_count_in_ch = 0
    for p in paras:
        if p in template_paras:
            template_words += len(p.split())
            template_count_in_ch += 1
    pct = (template_words / total_words * 100) if total_words > 0 else 0
    chapter_pollution.append((ch, os.path.basename(path), total_words, template_words, template_count_in_ch, round(pct, 1)))

polluted_chapters = [c for c in chapter_pollution if c[3] > 0]
print(f"\nNumber of chapters polluted with copy-pasted template blocks: {len(polluted_chapters)} / 360 ({len(polluted_chapters)/360*100:.1f}%)")

high_pollution = [c for c in chapter_pollution if c[5] >= 20]
print(f"Chapters with >= 20% template filler content: {len(high_pollution)}")

print("\nSample polluted chapters:")
for c in chapter_pollution[:20]:
    print(f"  Ch {c[0]:03d} ({c[1]}): Total Words={c[2]}, Template Words={c[3]} ({c[5]}%), Template Blocks={c[4]}")
