#!/usr/bin/env python3
"""
PASS 1: Restore every file to its original state.
Find ALL "Ghi chú: sổ cái khớp" occurrences, keep only the first one,
remove any extra text inserted above it.
"""
import os, re

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia/"

files = sorted([
    os.path.join(BASE, f) for f in os.listdir(BASE) 
    if f.endswith('.txt') and 'sổ cái khớp' in open(os.path.join(BASE, f), encoding='utf-8').read()
], key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1)) if re.search(r'(\d+)', os.path.basename(x)) else 9999)

print(f"Files to process: {len(files)}")

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    content = ''.join(lines)
    
    # Count occurrences
    count_occurrences = content.count('sổ cái khớp')
    if count_occurrences > 1:
        print(f"  {fname}: {count_occurrences} occurrences — cleaning")
    
    # Find the FIRST note line
    note_idx = -1
    note_line = ""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('Ghi chú') and 'sổ cái khớp' in stripped:
            if note_idx < 0:
                note_idx = i
                note_line = line.rstrip()
            break  # Only take first match
    
    if note_idx < 0:
        print(f"  WARNING: No note found in {fname}")
        continue
    
    # Walk backward from note_idx to find where real content ends
    # The real content before the note should be something like:
    # "Kỹ năng trọng yếu: ..." or "Tổng EXP: ..." or "Không gian kho: ..."
    # or maybe a "Teaser:" line
    # Between these and the note there should just be a blank line
    
    # Find the last non-empty, non-separator line that belongs to the body
    body_end = note_idx - 1
    while body_end >= 0:
        stripped = lines[body_end].strip()
        if stripped.startswith('====') or stripped.startswith('<!--') or stripped == '':
            body_end -= 1
        else:
            break
    
    if body_end < 0:
        body_end = 0
    
    # body_end now points to the last content line before the note area
    # (e.g., "Teaser: ..." or "Kỹ năng trọng yếu: ...")
    
    # The lines between note and body_end might have extra scene text inserted
    # We want to keep: body content up to body_end, then a blank, then the note
    # So: lines[0:body_end+1] + [''] + [note_line] + lines[note_idx+1:]
    
    clean = []
    for i in range(body_end + 1):
        clean.append(lines[i].rstrip())
    clean.append('')  # blank line before note
    clean.append(note_line)
    for i in range(note_idx + 1, len(lines)):
        clean.append(lines[i].rstrip())
    
    new_content = '\n'.join(clean) + '\n'
    
    # Verify only one sổ cái khớp
    if new_content.count('sổ cái khớp') != 1:
        print(f"  ERROR: {fname} still has {new_content.count('sổ cái khớp')} after clean!")
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("PASS 1 complete - all files restored to original")
