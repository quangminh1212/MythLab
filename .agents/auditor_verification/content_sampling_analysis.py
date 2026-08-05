# -*- coding: utf-8 -*-
import os, glob, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
target_dir = r"c:\Dev\XLab_MTC\Niên Đại Thương Gia"

# Sample 20 chapters across the range
sample_chapters = [1, 15, 30, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 360]

boost_phrases = [
    "Hùng nhìn thẳng, đôi mắt đăm chiêu",
    "Lan mỉm cười rạng rỡ, đôi mắt lấp lánh",
    "Thợ Tư chau mày nhìn, đôi tay chai sạn",
    "Ông Khánh gật đầu kiên định",
    "Bà Hà ngước đôi mắt dịu dàng",
    "Minh nheo đôi mắt suy nghĩ",
    "Trong không gian gian phòng ẩm mốc, mùi khói rơm",
    "Bên ngoài hiên, tiếng mưa rơi lộp bộp hòa cùng gió lạnh",
    "Bụi đường bám trên áo, mùi nắng ấm và vị mặn",
    "Mùi gỗ mới thơm nồng hòa quyện khói bếp",
    "Gian bếp nhỏ đượm mùi cơm mới thơm phức"
]

print("=== Content Authenticity Sampling Analysis ===")

boost_hits_total = 0
chapter_details = []

for ch in range(1, 361):
    files = glob.glob(os.path.join(target_dir, f"Chương {ch} - *.txt"))
    if not files:
        files = glob.glob(os.path.join(target_dir, f"Chương {ch:02d} - *.txt"))
    if not files:
        print(f"Missing chapter {ch}!")
        continue
    
    p = files[0]
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    
    hits = 0
    matched_phrases = []
    for phrase in boost_phrases:
        cnt = text.count(phrase)
        if cnt > 0:
            hits += cnt
            matched_phrases.append((phrase, cnt))
    
    boost_hits_total += hits
    if ch in sample_chapters:
        chapter_details.append((ch, os.path.basename(p), hits, matched_phrases, len(text.split())))

print(f"\nTotal template boost hits across ALL 360 chapters: {boost_hits_total}")
print("\nSampled Chapters Detail:")
for ch, fname, hits, matched, wcnt in chapter_details:
    print(f"\nChapter {ch:03d} ({fname}) | Words: {wcnt} | Template Injections: {hits}")
    for phrase, count in matched:
        print(f"   -> [{count}x]: {phrase}")
