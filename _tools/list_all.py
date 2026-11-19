#!/usr/bin/env python3
"""
Get the 103 exact chapter files from the original task list and verify the full set.
"""
import os, re, json

BASE = "C:/Dev/MythLab/Niên Đại Thương Gia/"
files = []
for f in os.listdir(BASE):
    if not f.endswith('.txt'):
        continue
    fpath = os.path.join(BASE, f)
    with open(fpath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if 'sổ cái khớp' in content:
        files.append(f)

def sort_key(f):
    m = re.search(r'(\d+)', f)
    return int(m.group(1)) if m else 9999

files_sorted = sorted(files, key=sort_key)
print(f"Total files with 'sổ cái khớp': {len(files_sorted)}")
for i, f in enumerate(files_sorted, 1):
    print(f"{i:3d}. {f}")
