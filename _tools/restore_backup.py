#!/usr/bin/env python3
"""
RESTORE: Remove any added scene text between previous content and 'Ghi chú: sổ cái khớp'
"""
import os, re

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia/"
files = []
for root, dirs, fnames in os.walk(BASE):
    for f in fnames:
        if f.endswith('.txt'):
            files.append(os.path.join(root, f))

count = 0
for fpath in sorted(files):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find the "Ghi chú: sổ cái khớp" line
    target_idx = -1
    for i, line in enumerate(lines):
        if 'Ghi chú' in line and 'sổ cái khớp' in line:
            target_idx = i
            break
    
    if target_idx < 0:
        continue
    
    # Walk backwards from the target line
    # Find the last content (non-empty, non-=====) before whatever scene was inserted
    # Then find the blank line immediately before the scene
    scene_start = target_idx
    prev_empty = -1
    
    for i in range(target_idx - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped == '':
            prev_empty = i
            continue
        elif stripped.startswith('===='):
            scene_start = i
            break
        else:
            # found content that isn't empty or ====
            # If we already passed an empty line, the scene starts after that empty line
            if prev_empty >= 0:
                scene_start = prev_empty
            break
    
    # Check if there's actually scene text to remove
    original_note = lines[target_idx]
    
    # Reconstruct: everything up to scene_start + the original note line
    new_lines = lines[:scene_start] + [original_note] + lines[target_idx+1:]
    new_content = '\n'.join(new_lines)
    
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1

print(f"Restored {count} files to original state")
