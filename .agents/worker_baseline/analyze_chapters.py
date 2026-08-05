# -*- coding: utf-8 -*-
import os, sys, json
sys.path.append(r'c:\Dev\XLab_MTC\Niên Đại Thương Gia')
import audit_all

os.chdir(r'c:\Dev\XLab_MTC\Niên Đại Thương Gia')

results = [audit_all.audit_chapter(n) for n in range(1, 361)]

pad_cnt = 0
tic_cnt = 0
panel_fail = 0
hdr_fail = 0
dlg_fail = 0

failing_details = []

for n in range(1, 361):
    res = audit_all.audit_chapter(n)
    p = res['path']
    raw = audit_all.norm(open(p, encoding='utf-8').read())
    body = audit_all.body_of(raw)
    
    pad_hits = sum(len(audit_all.re.findall(pat, body)) for pat in audit_all.PAD_MARKERS)
    tic_hits = sum(body.count(t) for t in audit_all.AI_TICS)
    panel = body.count('GHI NHẬN') + body.count('Hệ thống ghi nhận')
    dlg_lines = len([l for l in body.split('\n') if l.strip().startswith(('"', '“', '—', '–'))])
    hdr_ok = raw.lstrip().startswith('=' * 60)
    hm = audit_all.re.search(r'Chương\s+(\d+)\s*:\s*(.+)', raw[:400])
    hdr_num_ok = bool(hm) and int(hm.group(1)) == n
    
    issues = []
    if res['score'] < 9.5: issues.append(f"score={res['score']}")
    if res['words'] < 3000: issues.append(f"words_low={res['words']}")
    if res['words'] > 4200: issues.append(f"words_high={res['words']}")
    if res['sens_d'] < 3.5: issues.append(f"sens_d={res['sens_d']}")
    if res['char_d'] < 5.0: issues.append(f"char_d={res['char_d']}")
    if res['maxrep'] > 1: issues.append(f"maxrep={res['maxrep']}")
    if pad_hits > 0:
        pad_cnt += 1
        issues.append(f"pad_hits={pad_hits}")
    if tic_hits > 0:
        tic_cnt += 1
        issues.append(f"tic_hits={tic_hits}")
    if panel != 1:
        panel_fail += 1
        issues.append(f"panel_cnt={panel}")
    if not (hdr_ok and hdr_num_ok):
        hdr_fail += 1
        issues.append(f"hdr_ok={hdr_ok},hdr_num_ok={hdr_num_ok}")
    if dlg_lines < 10:
        dlg_fail += 1
        issues.append(f"dlg_lines={dlg_lines}")

    if issues:
        failing_details.append({
            'n': n,
            'file': res['file'],
            'score': res['score'],
            'issues': issues
        })

print(f"Total chapters: {len(results)}")
print(f"Score < 9.5: {sum(1 for r in results if r['score'] < 9.5)}")
print(f"Words < 3000: {sum(1 for r in results if r['words'] < 3000)}")
print(f"Words > 4200: {sum(1 for r in results if r['words'] > 4200)}")
print(f"Sens_d < 3.5: {sum(1 for r in results if r['sens_d'] < 3.5)}")
print(f"Char_d < 5.0: {sum(1 for r in results if r['char_d'] < 5.0)}")
print(f"Maxrep > 1: {sum(1 for r in results if r['maxrep'] > 1)}")
print(f"Pad hits > 0: {pad_cnt}")
print(f"Tic hits > 0: {tic_cnt}")
print(f"Panel != 1: {panel_fail}")
print(f"Header fail: {hdr_fail}")
print(f"Dialogue lines < 10: {dlg_fail}")
print(f"Total chapters with ANY issue: {len(failing_details)}")

with open(r'c:\Dev\XLab_MTC\.agents\worker_baseline\failing_details.json', 'w', encoding='utf-8') as f:
    json.dump(failing_details, f, ensure_ascii=False, indent=2)
