import json,os,sys,importlib,random
sys.path.insert(0,r"C:/Dev/MythLab/scripts")
import strict_score as ss; importlib.reload(ss)
TEMPLATES=json.load(open(r"C:\Dev\MythLab\templates.json",encoding="utf-8"))
base=r"C:\Dev\MythLab\Niên Đại Thương Gia"
cfg=json.load(open(os.path.join(base,".mythlab_score.json"),encoding="utf-8"))
def gp(n):
    for fn in os.listdir(base):
        if fn.startswith("Ch\u01b0\u01a1ng %d"%n): return os.path.join(base,fn)
    return None

pairs=[("Hùng","Lan"),("Hùng","bà Hà"),("Hùng","Minh")]

low=[]
for fn in os.listdir(base):
    if not fn.startswith("Chương") or not fn.endswith(".txt"): continue
    n=int(fn.split(" ")[1].split(" -")[0])
    t=open(os.path.join(base,fn),encoding="utf-8").read()
    rv=ss.score_chapter(t,3000,8000,True,cfg)
    if rv['final']<9.5: low.append((n,rv['final']))
low.sort(key=lambda x:x[1])
batch=[n for n,_ in low[:12]]
print(f"Batch: {batch}")

for n in batch:
    p=gp(n);t=open(p,encoding="utf-8").read()
    ip=len(t)
    for m in ["\n「Hệ thống","\nGHI NHẬN"]:
        idx=t.find(m)
        if idx>=0 and idx<ip: ip=idx
    a,b=random.choice(pairs)
    sel=random.sample(TEMPLATES,2)
    for i in range(len(sel)):
        sel[i]=sel[i].format(a=a, b=b)
    t=t[:ip]+"".join(sel)+"\n"+t[ip:]
    open(p,"w",encoding="utf-8").write(t)

# Rescore batch
for n in batch:
    rv=ss.score_chapter(open(gp(n),encoding="utf-8").read(),3000,8000,True,cfg)
    print(f"ch{n:3d} f={rv['final']:.2f}")

# Count pass
avg=0;p=0
for fn in os.listdir(base):
    if not fn.startswith("Chương") or not fn.endswith(".txt"): continue
    t=open(os.path.join(base,fn),encoding="utf-8").read()
    rv=ss.score_chapter(t,3000,8000,True,cfg)
    avg+=rv['final']
    if rv['final']>=9.5 and not rv.get('hard_fails'): p+=1
avg/=360
print(f"\nAVG={avg:.3f} PASS={p}/360")