#!/usr/bin/env python3
"""
Generate unique closing scenes for all 103 chapters.
Saves to JSON, then applies to files.
"""
import os, re, subprocess, json

BASE = "C:/Dev/MythLab/Niên Đại Thương Gia"

# Read the list of files
result = subprocess.run(
    ["grep", "-rn", "system_ledger", BASE, "--include=*.txt"],
    capture_output=True, text=True
)
raw_lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]

entries = []
for l in raw_lines:
    m = re.match(r'^(.+\.txt):(\d+):(.+)$', l)
    if m:
        entries.append((m.group(1), m.group(3)))

entries.sort(key=lambda x: os.path.basename(x[0]))
print(f"Total entries: {len(entries)}")

# Define all 103 scenes as dict keyed by filename
all_scenes = {}

# We'll write scenes in batches to avoid one huge file
# Loading from individual text files

import sys
# Collect scene definitions from stdin or file
scenes_json_path = os.path.join(BASE, "_socai_scenes_final.json")

if os.path.exists(scenes_json_path):
    with open(scenes_json_path, 'r', encoding='utf-8') as f:
        all_scenes = json.load(f)
    print(f"Loaded {len(all_scenes)} existing scenes from JSON")
else:
    print("No existing scenes found. Will create inline.")
    all_scenes = {}

# Show which files are missing scenes
missing = [fname for path, fname, ghi_chu in entries if fname not in all_scenes]
print(f"Files with scenes: {len(all_scenes)}")
print(f"Missing scenes: {len(missing)}")
for m in missing[:10]:
    print(f"  - {m}")
if len(missing) > 10:
    print(f"  ... and {len(missing)-10} more")
