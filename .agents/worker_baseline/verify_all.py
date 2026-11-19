# -*- coding: utf-8 -*-
import os, sys, json
sys.path.append(r'c:\Dev\MythLab\Niên Đại Thương Gia')
import audit_all

os.chdir(r'c:\Dev\MythLab\Niên Đại Thương Gia')

violations = []
for n in range(1, 361):
    res = audit_all.audit_chapter(n)
    p = res['path']
    raw = audit_all.norm(open(p, encoding='utf-8').read())
    body = audit_all.body_of(raw)
    
    panel = body.count('GHI NHẬN') + body.count('Hệ thống ghi nhận')
    dlg_lines = len([l for l in body.split('\n') if l.strip().startswith(('"', '“', '—', '–'))])
    hdr_ok = raw.lstrip().startswith('=' * 60)
    hm = audit_all.re.search(r'Chương\s+(\d+)\s*:\s*(.+)', raw[:400])
    hdr_num_ok = bool(hm) and int(hm.group(1)) == n
    
    if res['score'] < 9.5: violations.append((n, 'score < 9.5', res['score']))
    if res['words'] < 3000 or res['words'] > 4200: violations.append((n, 'words out of bounds', res['words']))
    if res['sens_d'] < 3.5: violations.append((n, 'sens_d < 3.5', res['sens_d']))
    if res['char_d'] < 5.0: violations.append((n, 'char_d < 5.0', res['char_d']))
    if res['maxrep'] > 1: violations.append((n, 'maxrep > 1', res['maxrep']))
    if panel != 1: violations.append((n, 'panel != 1', panel))
    if not (hdr_ok and hdr_num_ok): violations.append((n, 'header invalid', (hdr_ok, hdr_num_ok)))
    if dlg_lines < 10: violations.append((n, 'dlg_lines < 10', dlg_lines))

print(f'Total violations across all 360 chapters: {len(violations)}')
if violations:
    for v in violations[:10]:
        print(v)
else:
    print('ALL 360 CHAPTERS 100% COMPLIANT!')
