#!/usr/bin/env python3
import re, os, subprocess, json

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia"

result = subprocess.run(
    ["grep", "-rn", "system_ledger", BASE, "--include=*.txt"],
    capture_output=True, text=True
)
lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]

file_data = []
for l in lines:
    # grep output: C:/.../file.txt:lineno:Ghi chú: ...
    # Find the line number by looking at the pattern
    parts = l.split(':', 3)
    if len(parts) >= 3:
        path = parts[0]
        try:
            lineno = int(parts[1])
        except ValueError:
            continue
        content = parts[2] if len(parts) == 3 else ':'.join(parts[2:])
        fname = os.path.basename(path)
        file_data.append((path, fname, lineno, content))

file_data.sort(key=lambda x: x[1])
print(f"Total files: {len(file_data)}")

# Read endings
endings = {}
for path, fname, ln, content in file_data:
    start = max(1, ln - 20)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        end_text = ''.join(all_lines[start-1:ln-1])
        endings[fname] = {
            'path': path, 'line': ln, 'ghichu': content.strip(),
            'end_text': end_text.strip()
        }
    except Exception as e:
        print(f"Error {fname}: {e}")

with open(os.path.join(BASE, '_socai_all.json'), 'w', encoding='utf-8') as f:
    json.dump(endings, f, ensure_ascii=False, indent=2)

print(f"Saved {len(endings)} endings")

# PRINT all filenames and last meaningful lines
for i, (fname, d) in enumerate(endings.items(), 1):
    lines = d['end_text'].split('\n')
    # Skip empty lines at end, get last 3 non-empty lines
    non_empty = [l for l in lines if l.strip()]
    last_3 = non_empty[-3:] if len(non_empty) >= 3 else non_empty
    print(f"\n=== [{i}] {fname} ===")
    for nl in last_3:
        print(f"  {nl[:150]}")
