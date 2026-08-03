# -*- coding: utf-8 -*-
import audit_all, json

below = []
for n in range(1, 71):
    res = audit_all.audit_chapter(n)
    if res and res['score'] < 9.5:
        below.append(res)

print(f"Total below 9.5: {len(below)}\n")
for r in below:
    print(f"Ch {r['n']:02d}: Score={r['score']} | Words={r['words']} | Prose={r['prose']} | Plot={r['plot']} | Char={r['char']} | Sens={r['sens_d']} | CharD={r['char_d']}")
