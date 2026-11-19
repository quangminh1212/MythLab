#!/usr/bin/env python3
import os, re, json

base = "C:/Dev/MythLab/Niên Đại Thương Gia/"
files = []

for root, dirs, fnames in os.walk(base):
    for f in fnames:
        if f.endswith('.txt'):
            fpath = os.path.join(root, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                if 'sổ cái khớp' in content:
                    files.append(fpath)
            except:
                pass

print(f"FILES_FOUND: {len(files)}")

def sort_key(f):
    m = re.search(r'(\d+)', os.path.basename(f))
    return int(m.group(1)) if m else 9999

files_sorted = sorted(files, key=sort_key)

chapters = []
for f in files_sorted:
    with open(f, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    
    title_line = ""
    for line in lines:
        if line.strip().startswith('Chương') and ':' in line:
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
        'file': base_name,
        'name': base_name.replace('.txt', ''),
        'title': title_line,
        'first_3': first_3,
        'last_3': last_3
    })

chapters.sort(key=lambda x: x['num'])
print(json.dumps(chapters, ensure_ascii=False, indent=2))
