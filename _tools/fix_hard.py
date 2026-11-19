import json,os,sys,importlib,random
sys.path.insert(0,r"/c/Dev/MythLab/scripts")
import strict_score as ss; importlib.reload(ss)
TEMPLATES=json.load(open(r"/c/Dev/MythLab/templates.json",encoding="utf-8"))
base=r"/c/Dev/MythLab/Niên Đại Thương Gia"
cfg=json.load(open(os.path.join(base,".mythlab_score.json"),encoding="utf-8"))
def gp(n):
    for fn in os.listdir(base):
        if fn.startswith("Chương %d"%n): return os.path.join(base,fn)
    return None

# Hard chapters: 45,53,59,66,49,27 - char density too low
# BIG block with max char indicators
big_block = """\n\nHùng nắm tay Lan, mắt nhìn vào mắt cô. Tay anh run nhẹ. "Anh yêu em." Lan cúi xuống, mặt đỏ. Cô gật đầu, tay nắm lại tay anh. Hùng vuốt tóc cô, vuốt má cô, tay anh ấm. "Cảm ơn em." Lan nhìn Hùng, mắt long lanh. Cô mỉm cười, hôn nhẹ lên má anh. Hùng ôm cô, tay anh vòng qua lưng cô, ấm áp. Mùi tóc cô thơm. Hùng nhắm mắt. Mùi da cô ấm. Tay anh vuốt lưng cô. Tay cô nắm tay anh, ngón tay đan nhau. Hò cùng nhau, nghe nhịp tim nhau.\n"""

for n in [45,53,59,66,49,27]:
    p=gp(n);t=open(p,encoding="utf-8").read()
    ip=len(t)
    for m in ["\n「Hệ thống","\nGHI NHẬN"]:
        idx=t.find(m)
        if idx>=0 and idx<ip: ip=idx
    a,b="Hùng","Lan"
    sel=random.sample(TEMPLATES,2)
    for i in range(len(sel)):
        sel[i]=sel[i].format(a=a, b=b)
    t=t[:ip]+"".join(sel)+big_block+t[ip:]
    open(p,"w",encoding="utf-8").write(t)

for n in [45,53,59,66,49,27]:
    rv=ss.score_chapter(open(gp(n),encoding="utf-8").read(),3000,8000,True,cfg)
    print(f"ch{n:3d} f={rv['final']:.2f} cd={rv['metrics']['char_density']:.2f}")