#!/usr/bin/env python3
"""
Clean ALL files: remove any scene text between the main body and the 'Ghi chú:' line.
Restore to original state (note line directly after footer content).
"""
import os, re

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia/"

files = sorted([
    os.path.join(BASE, f) for f in os.listdir(BASE) 
    if f.endswith('.txt')
], key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1)) if re.search(r'(\d+)', os.path.basename(x)) else 9999)

count = 0
for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'sổ cái khớp' not in content:
        continue
    
    lines = content.split('\n')
    
    # Find the FIRST occurrence of the note line
    note_idx = -1
    for i, line in enumerate(lines):
        # Check if it starts with "Ghi chú:" and contains "sổ cái khớp"
        stripped = line.strip()
        if stripped.startswith('Ghi chú') and 'sổ cái khớp' in stripped:
            note_idx = i
            break
    
    if note_idx < 0:
        continue
    
    note_line = lines[note_idx]
    
    # Now walk backwards from note_idx to find a non-empty line that looks like body content
    # That would be something like "Kỹ năng trọng yếu: ..." or "Tổng EXP: ..." or "Hùng cười..."
    # Stop at the first such line, then delete everything between it and the note
    
    # Actually simpler: just look for a line that starts with '====' or is empty
    # before the note, and keep everything up to that blank/separator line
    
    # Find the line BEFORE the note that is part of the body
    scene_insertion_point = note_idx
    prev_content = note_idx - 1
    
    # Skip empty lines going backwards
    while prev_content >= 0 and lines[prev_content].strip() == '':
        prev_content -= 1
    
    # That prev_content points to a non-empty line (either scene text or original content)
    # Walk further back to find where the scene/extra text starts
    # We keep scanning backwards:
    # - If we hit a '====' line, scene starts right after it
    # - If we hit an empty line, scene starts right after it
    # - If we hit a line that looks like system footer (Kỹ năng, Tổng EXP, Không gian), scene starts after it
    
    scan = prev_content
    while scan >= 0:
        line = lines[scan].strip()
        if line == '':
            scene_insertion_point = scan
            scan -= 1
            # Don't break - keep scanning for the real body end
        elif line.startswith('===='):
            scene_insertion_point = scan
            break
        else:
            # Content - keep going back to find the start
            scene_insertion_point = scan
            scan -= 1
    
    # scene_insertion_point now points to a line that is either:
    # - The blank line before the scene
    # - The ==== line
    # - The first line of the scene/extra text
    
    # But we actually want to KEEP the original content (like "Kỹ năng trọng yếu...")
    # and REMOVE just the scene text
    
    # Re-scan from scene_insertion_point forward, keeping lines that 
    # look like original content (EXP, Không gian, Kỹ năng) or ====
    
    restored_lines = lines[:note_idx]  # everything before note
    
    # Find what the original pre-note lines should be
    # by looking back from note_idx for system-styled lines
    original_pre_lines = []
    scan = note_idx - 1
    while scan >= 0:
        line = lines[scan].strip()
        if not line:
            if original_pre_lines:
                # We hit an empty line AFTER finding system lines - stop
                break
            # Empty line before all system lines - skip
            scan -= 1
            continue
        if line.startswith('====') or line.startswith('Tổng EXP') or line.startswith('Không gian') or line.startswith('Kỹ năng') or line.startswith('Teaser') or line.startswith('<!--'):
            original_pre_lines.insert(0, lines[scan].rstrip())
            scan -= 1
        else:
            # Found a non-system line (scene text)
            # But if we already have system lines, this scene text is between system lines and note
            if original_pre_lines:
                break
            # Otherwise, keep going - this could be old scene text
            scan -= 1
    
    # Keep: all system lines before note + blank line + note
    keep = [l.rstrip() for l in original_pre_lines]
    keep.append('')  # blank line
    keep.append(note_line)
    
    # Rest: lines after note
    rest = [l.rstrip() for l in lines[note_idx+1:]]
    
    new_content = '\n'.join(keep + rest) + '\n'
    
    # Verify sổ cái appears exactly once
    if new_content.count('sổ cái khớp') != 1:
        print(f"WARNING: {os.path.basename(fpath)} has {new_content.count('sổ cái khớp')} occurrences")
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    count += 1
    print(f"✓ {os.path.basename(fpath)} — kept {original_pre_lines}")

print(f"\nCleaned {count} files")
