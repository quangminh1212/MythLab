import json,os,sys,importlib,random
sys.path.insert(0,'C:/Dev/MythLab/scripts')
import strict_score as ss; importlib.reload(ss)
base='Niên Đại Thương Gia'
cfg=json.load(open(os.path.join(base,'.mythlab_score.json'),encoding='utf-8'))

def gp(n):
    for fn in os.listdir(base):
        if fn.startswith('Ch\u01b0\u01a1ng %d'%n): return os.path.join(base,fn)
    return None

# Classify all <9.5 chapters by primary deficiency
low=[]
for fn in sorted(os.listdir(base)):
    if not fn.startswith('Ch\u01b0\u01a1ng') or not fn.endswith('.txt'): continue
    t=open(os.path.join(base,fn),encoding='utf-8').read()
    rv=ss.score_chapter(t,3000,8000,True,cfg)
    if rv['final']<9.5:
        n=int(fn.split(' ')[1].split(' -')[0])
        axes=rv['axes']
        low.append((n,rv['final'],axes['van_chuong'],axes['nhan_vat'],axes['cau_truc'],rv['metrics']['char_density']))

# Group by score tier
tier_918=[(n,f,van,nv,ct,cd) for n,f,van,nv,ct,cd in low if f<9.3]
tier_934=[(n,f,van,nv,ct,cd) for n,f,van,nv,ct,cd in low if 9.3<=f<9.4]
tier_940=[(n,f,van,nv,ct,cd) for n,f,van,nv,ct,cd in low if 9.4<=f<9.45]
tier_948=[(n,f,van,nv,ct,cd) for n,f,van,nv,ct,cd in low if f>=9.45]

print(f'9.18: {len(tier_918)} -> {[n for n,_,_,_,_,_ in tier_918]}')
print(f'9.34: {len(tier_934)} -> {[n for n,_,_,_,_,_ in tier_934]}')
print(f'9.40: {len(tier_940)} -> {len(tier_940)} chapters')
print(f'9.48: {len(tier_948)} -> {len(tier_948)} chapters')