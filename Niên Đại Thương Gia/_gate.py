# -*- coding: utf-8 -*-
import os, re, glob, sys, json, unicodedata
from collections import Counter
ROOT = os.path.dirname(os.path.abspath(__file__))
def norm(s): return unicodedata.normalize('NFC', s)
def vi(t): return len([x for x in t.split() if len(x)>=2])
SEP='='*60
def body_of(raw):
    parts = raw.split(SEP)
    return (SEP.join(parts[2:]).strip() if len(parts)>=3 else raw)
def prose_of(body):
    # prose = body minus the final panel block (from first 「Hệ thống to end)
    pos = body.find('「Hệ thống')
    return body[:pos] if pos>0 else body
def plines(text):
    out=[]
    for l in text.split('\n'):
        s=l.strip()
        if len(s)>=40 and set(s)!={'='}:
            out.append(s)
    return out
# FROZEN global clone set (from git baseline; never recompute from live disk)
_cs = json.load(open(os.path.join(ROOT,'_cloneset.json'), encoding='utf-8'))
clone_set = {norm(l) for l in _cs['clone_lines']}
targets=[int(x) for x in sys.argv[1:]]
for n in targets:
    fl=glob.glob(os.path.join(ROOT,f'Chương {n} - *.txt'))
    if not fl: print(f'ch{n}: NOFILE'); continue
    raw=norm(open(fl[0],encoding='utf-8',errors='replace').read())
    b=body_of(raw); pr=prose_of(b)
    toks=vi(pr)
    ll=plines(pr)
    clone_lines=sum(1 for l in ll if l in clone_set)
    cnt=Counter(ll); intra=sum(v-1 for v in cnt.values() if v>1)
    panels=b.count('GHI NHẬN')
    ys=[int(y) for y in re.findall(r'\b(19[7-9]\d|20[0-2]\d)\b', b)]
    yr=Counter(ys).most_common(1)[0][0] if ys else None
    ok = toks>=3200 and clone_lines==0 and intra==0 and panels==1
    print(f'ch{n}: toks={toks} clone={clone_lines} intra={intra} panel={panels} yr={yr} {"PASS" if ok else "FAIL"}')
