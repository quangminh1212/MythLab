#!/usr/bin/env python3
import os, re, json

base = "C:/Dev/MythLab/Niên Đại Thương Gia/"
result = os.popen(f'grep -rln "s\\u1ed5 c\\u00e1i kh\\u1edbp" --include="*.txt" "{base}"').read()
files = [f.strip() for f in result.strip().split('\n') if f.strip()]

def sort_key(f):
    m = re.search(r'(\d+)', os.path.basename(f))
    return int(m.group(1)) if m else 9999

files_sorted = sorted(files, key=sort_key)
print(f"FILES_FOUND: {len(files_sorted)}")

chapters = []
for f in files_sorted:
    with open(f, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    
    # Get chapter title
    title_line = ""
    for i, line in enumerate(lines):
        if line.startswith('Chương') and ':' in line:
            title_line = line.strip()
            break
    
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('Chương') and ':' in line:
            body_start = i + 2
            break
    
    first_3 = []
    for i in range(body_start, len(lines)):
        s = lines[i].strip()
        if s and len(first_3) < 3:
            first_3.append(s)
        if len(first_3) == 3:
            break
    
    # Last 3 meaningful lines before the footer/ledger note
    last_3 = []
    for i in range(len(lines)-1, -1, -1):
        s = lines[i].strip()
        if not s:
            continue
        if s.startswith('===='):
            continue
        if s.startswith('<!--'):
            continue
        if 'sổ cái khớp' in s:
            continue
        if 'Ghi chú' in s:
            continue
        if s not in last_3:
            last_3.insert(0, s)
        if len(last_3) == 3:
            break
    
    base_name = os.path.basename(f)
    m = re.search(r'(\d+)', base_name)
    chap_num = int(m.group(1)) if m else 0
    
    chapters.append({
        'num': chap_num,
        'file': f.replace(base, ''),
        'name': base_name.replace('.txt', ''),
        'title': title_line,
        'first_3': first_3,
        'last_3': last_3
    })

chapters.sort(key=lambda x: x['num'])
print(json.dumps(chapters, ensure_ascii=False, indent=2))
