# -*- coding: utf-8 -*-
import sys, os, json, importlib
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\MythLab\Niên Đại Thương Gia'
sys.path.insert(0, r'c:\Dev\MythLab\.agents\worker_remediation')

import generate_remediated_chapters
importlib.reload(generate_remediated_chapters)

from audit_all import audit_chapter

test_chs = [1, 6, 8, 9, 55, 100, 200, 360]
for n in test_chs:
    text = generate_remediated_chapters.build_remediated_chapter_text(n)
    files = [f for f in os.listdir(ROOT) if f.startswith(f'Chương {n} - ') or f.startswith(f'Chương {n:02d} - ')]
    if files:
        p = os.path.join(ROOT, files[0])
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
        res = audit_chapter(n)
        print(f"Ch {n:3d}: Score={res['score']:4.2f} | Words={res['words']:4d} | Prose={res['prose']:4.2f} Plot={res['plot']:4.2f} Char={res['char']:4.2f} SensD={res['sens_d']:4.2f} CharD={res['char_d']:4.2f}")
