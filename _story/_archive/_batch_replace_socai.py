#!/usr/bin/env python3
"""
Batch process 103 files with system_ledger notes.
Read endings, determine chapter theme, replace Ghi chú with unique scene.
"""
import re
import os
import subprocess
import json

BASE = "C:/Dev/MythLab/Niên Đại Thương Gia"

# Use a simpler approach - get file list first
result = subprocess.run(
    ["grep", "-rl", "system_ledger", BASE, "--include=*.txt"],
    capture_output=True, text=True
)
paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
paths.sort()
print(f"Total files with system_ledger: {len(paths)}")

# For each file, get the exact Ghi chú line number and content
file_data = []
for p in paths:
    r = subprocess.run(
        ["grep", "-n", "system_ledger", p],
        capture_output=True, text=True
    )
    match_line = r.stdout.strip()
    if match_line:
        # Format: lineno:content
        parts = match_line.split(':', 1)
        lineno = int(parts[0])
        content = parts[1] if len(parts) > 1 else ""
        fname = os.path.basename(p)
        file_data.append((p, fname, lineno, content))

print(f"Parsed: {len(file_data)} files")

# Save for reference
with open(os.path.join(BASE, "_socai_file_index.json"), "w", encoding="utf-8") as f:
    json.dump(file_data, f, ensure_ascii=False, indent=2)
print("Saved index")

# Batch 1: first 35
batch1 = file_data[:35]
batch2 = file_data[35:70]
batch3 = file_data[70:]

print(f"\nBatch 1: {len(batch1)} files")
for p, fname, ln, _ in batch1:
    print(f"  {fname} (line {ln})")

print(f"\nBatch 2: {len(batch2)} files")
for p, fname, ln, _ in batch2:
    print(f"  {fname} (line {ln})")

print(f"\nBatch 3: {len(batch3)} files")
for p, fname, ln, _ in batch3:
    print(f"  {fname} (line {ln})")
