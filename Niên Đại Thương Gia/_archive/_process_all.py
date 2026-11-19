#!/usr/bin/env python3
"""
Read all 103 chapter endings → generate unique scenes → replace Ghi chú lines
"""
import os, subprocess, re, json

BASE = "C:/Dev/MythLab/Niên Đại Thương Gia"

# Step 1: Get current file list with system_ledger
result = subprocess.run(
    ["grep", "-rn", "system_ledger", BASE, "--include=*.txt"],
    capture_output=True, text=True
)
raw_lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]

# Parse: /path/file.txt:LINENO:Ghi chú:...
entries = []
for l in raw_lines:
    m = re.match(r'^(.+\.txt):(\d+):(.+)$', l)
    if m:
        path = m.group(1)
        lineno = int(m.group(2))
        line_content = m.group(3)
        fname = os.path.basename(path)
        entries.append((path, fname, lineno, line_content))

entries.sort(key=lambda x: x[1])
print(f"Total entries: {len(entries)}")

# Step 2: Read the last section before system block for each file
chapter_info = {}
for path, fname, ln, ghi_chu in entries:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    total = len(lines)
    
    # Get lines from ~20 before the Ghi chú line up to the ===== header
    start = max(0, ln - 22)
    # Find where the ==== system header starts
    sys_header = None
    for i in range(start, min(ln, total)):
        if lines[i].strip().startswith('====') or '「Hệ thống' in lines[i]:
            sys_header = i
            break
    
    # Get the ending scene: from sys_header-1 backwards to previous ====
    scene_lines = []
    header_idx = sys_header if sys_header else ln - 1
    for i in range(header_idx - 1, -1, -1):
        if lines[i].strip().startswith('===='):
            break
        scene_lines.insert(0, lines[i].rstrip())
    
    # Preview: last 3 non-empty lines before the system header
    preview = [l.strip() for l in scene_lines if l.strip()][-3:] if scene_lines else []
    
    chapter_info[fname] = {
        'path': path, 'line': ln, 'total': total,
        'ghichu': ghi_chu,
        'scene_lines': scene_lines,
        'preview': preview,
        'sys_header_line': sys_header
    }

print(f"Read {len(chapter_info)} chapter endings")
print("\n=== CHAPTER PREVIEWS ===")
for i, (fname, info) in enumerate(sorted(chapter_info.items()), 1):
    print(f"\n[{i:3d}] {fname}")
    print(f"      Ghi chú: {info['ghichu'][:70]}...")
    for p in info['preview']:
        print(f"      > {p[:120]}")
