"""Auto-fix panel year after subagent batches.
Run: python _auto_fix_year.py
Fixes: panel year, EXP, space to match system_ledger.json
"""
import re, json, glob, os
ROOT = r'C:/Dev/MythLab/Niên Đại Thương Gia'
led = json.load(open(os.path.join(ROOT, 'system_ledger.json'), encoding='utf-8'))['chapters']
BAD = ['Liệu ngày mai còn lỗ hổng', 'Vì có em', 'nhìn vợ', 'Teaser:', 'chốt mục',
       'hermes_tools', 'HẾT CHƯƠNG', 'system_ledger', '[CHARFIX]']
yr_fix = bad_fix = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'Chương *.txt'))):
    n = int(re.match(r'Chương (\d+)', os.path.basename(f)).group(1))
    t = open(f, encoding='utf-8').read()
    L = led.get(str(n), {})
    if not L:
        continue
    changed = False
    m = re.search(r'Năm:\s*(\d{4})', t)
    if m and int(m.group(1)) != int(L['year']):
        t = t.replace(f'Năm: {m.group(1)}', f'Năm: {L["year"]}', 1)
        pe = f'{L["exp_total"]:,}'
        ps = f'{L["space_m2"]:,}'
        t = re.sub(r'Tổng EXP:\s*[^\n]+',
                   f'Tổng EXP: {pe} (+{L.get("exp_delta", 0)})', t, count=1)
        t = re.sub(r'Không gian kho:\s*[^\n]+',
                   f'Không gian kho: {ps}m² (+{L.get("space_delta", 0)}m²)', t, count=1)
        changed = True
        yr_fix += 1
    for b in BAD:
        if b in t:
            changed = True
            bad_fix += 1
            if b == 'Teaser:':
                t = re.sub(r'(?m)^.*Teaser:.*\n?', '', t)
            elif b == 'nhìn vợ':
                t = t.replace('nhìn vợ', 'nhìn mẹ')
            elif b == 'Vì có em':
                t = re.sub(r'(?m)^.*Vì có em.*\n?', '', t)
            elif b == 'HẾT CHƯƠNG':
                t = re.sub(r'(?m)^.*HẾT CHƯƠNG.*\n?', '', t)
            elif b == 'system_ledger':
                t = re.sub(r'(?m)^Ghi chú:.*system_ledger.*\n?', '', t)
            elif b == '[CHARFIX]':
                t = re.sub(r'(?m)^.*\[CHARFIX\].*\n?', '', t)
            elif b == 'chốt mục':
                t = re.sub(r'(?m)^.*chốt mục\s*\d+.*\n?', '', t)
            elif b == 'hermes_tools':
                t = re.sub(r'(?m)^.*hermes_tools.*\n?', '', t)
            elif b == 'Liệu ngày mai còn lỗ hổng':
                t = re.sub(r'(?m)^.*Liệu ngày mai.*\n?', '', t)
    if changed:
        t = re.sub(r'\n{4,}', '\n\n\n', t)
        open(f, 'w', encoding='utf-8').write(t if t.endswith('\n') else t + '\n')
# verify
yr2 = bad2 = 0
for f in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
    n = int(re.match(r'Chương (\d+)', os.path.basename(f)).group(1))
    t = open(f, encoding='utf-8').read()
    L = led.get(str(n), {})
    m = re.search(r'Năm:\s*(\d{4})', t)
    if L and m and int(m.group(1)) != int(L['year']):
        yr2 += 1
    if any(b in t for b in BAD):
        bad2 += 1
print(f'FIXED yr={yr_fix} bad={bad_fix} | AFTER year={yr2} bad={bad2}')
