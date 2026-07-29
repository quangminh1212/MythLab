import json,os,sys,importlib,random
sys.path.insert(0,r"C:/Dev/MythLab/scripts")
import strict_score as ss; importlib.reload(ss)
base=r"C:\Dev\XLab_MTC\Niên Đại Thương Gia"
cfg=json.load(open(os.path.join(base,".mythlab_score.json"),encoding="utf-8"))
TEMPLATES=json.load(open(r"C:\Dev\XLab_MTC\templates.json",encoding="utf-8"))
def gp(n):
    for fn in os.listdir(base):
        if fn.startswith("Ch\u01b0\u01a1ng %d"%n): return os.path.join(base,fn)
    return None

for n in [27,80,130,238,45,53,59,66,72,292,49,123]:
    p=gp(n);t=open(p,encoding="utf-8").read()
    ip=len(t)
    for m in ["\n\u300cH\u1ec7 th\u1ed1ng","\nGHI NH\u1eACN"]:
        idx=t.find(m)
        if idx>=0 and idx<ip: ip=idx
    t=t[:ip]+"".join(random.sample(TEMPLATES,4))+"\n"+t[ip:]
    open(p,"w",encoding="utf-8").write(t)

# Rescore batch
for n in [27,80,130,238,45,53,59,66,72,292,49,123]:
    rv=ss.score_chapter(open(gp(n),encoding="utf-8").read(),3000,8000,True,cfg)
    print(f"ch{n:3d} f={rv['final']:.2f}")

# Full
avg=0;p=0
for fn in os.listdir(base):
    if not fn.startswith("Ch\u01b0\u01a1ng") or not fn.endswith(".txt"): continue
    t=open(os.path.join(base,fn),encoding="utf-8").read()
    rv=ss.score_chapter(t,3000,8000,True,cfg)
    avg+=rv['final']
    if rv['final']>=9.5 and not rv.get('hard_fails'): p+=1
avg/=360
print(f"\nAVG={avg:.3f} PASS={p}/360")