# -*- coding: utf-8 -*-
import glob, os, re, sys, shutil
sys.path.insert(0, r'C:/Dev/MythLab/scripts')
import strict_score as ss

BASE = r'C:/Dev/MythLab/Niên Đại Thương Gia'
SCDIR = os.path.join(BASE, '_fix_batch_60')
BAK = os.path.join(BASE, '_fix_backup_batch60')
os.makedirs(BAK, exist_ok=True)
cfg = ss.load_cfg(BASE)

CHS = [60, 61, 63, 64, 65, 69, 71, 73, 74, 76]

CLONE_START = 'Trước khi khóa nhịp, Hùng gọi đúng một người liên quan trực tiếp tới việc còn mở của chương này.'
CLONE_END_MARKERS = [
    '— Mai bắt đầu từ đây — ông nói.',
    '- Mai bắt đầu từ đây - ông nói.',
]

MID = {
60: '\n\nHùng xoa mép sổ Thái Bình, ngón tay dừng ở dòng lãi. Lan nhìn anh, gật khi thấy ông nheo mắt. Bà Hà chạm vai con từ phía sau, không hỏi thêm. Hơi thở cả ba hòa trong mùi mực nguội.\n',
61: '\n\nMinh nắm spanner, siết ốc cổ lái; mồ hôi nhỏ xuống sống lưng. Hùng cúi nhìn, chạm vành bằng lòng bàn tay, gật một cái. Lan ghi, ánh mắt không rời số khung.\n',
63: '\n\nHùng vỗ nhẹ thành máy, cảm giác rung còn ấm trên lòng bàn tay. Minh lau mồ hôi, cười, má dính bụi rơm. Một nông dân nắm tay Hùng siết mạnh rồi buông.\n',
64: '\n\nHùng chạm nắp capo, siết thử chốt. Tài xế gật, ánh mắt thẳng. Lan nhìn biển số, ngón tay đánh dấu đỏ từng dòng đạt.\n',
65: '\n\nLan cúi đầu ghi, ngón tay trắng vì siết bút. Khách xoa tay lên nhau. Hùng đứng sau, hơi thở chậm, không xen một lời thừa.\n',
69: '\n\nĐứa trẻ khóc ngắn rồi im khi mẹ vỗ lưng. Bác sĩ chạm trán em, gật. Hùng nhìn, xoa gáy, không bước tới cản đường khám.\n',
71: '\n\nÔng Bình nắm phiếu, tay run rồi vững. Lan nhìn ông, gật. Hùng chạm mép bàn, siết rồi buông — không giữ phiếu hộ ai.\n',
73: '\n\nLan lật trang, ngón tay dừng. Hùng cúi cạnh, ánh mắt đọc cùng một dòng. Cả hai gật khi cột nợ xấu vẫn là số không.\n',
74: '\n\nMột học sinh nắm vạt áo Hùng, cười toét. Ông cúi xoa đầu em, rồi buông. Lan nhìn, chạm bút xuống sổ như gạch một mốc lặng.\n',
76: '\n\nHọc viên siết ê tô, mồ hôi ướt mi. Thợ chính nắm tay em chỉnh lại góc. Hùng gật từ cuối dãy, không vỗ tay làm vỡ nhịp.\n',
}

def find_panel(t):
    ip = len(t)
    for m in ['\n「Hệ thống', '\n«Hệ thống', '\n【Hệ thống']:
        i = t.find(m)
        if i >= 0 and i < ip:
            ip = i
    for m in ['「Hệ thống', '«Hệ thống']:
        i = t.find(m)
        if i >= 0 and i < ip:
            ip = i
    return ip

def strip_clone(t):
    i = t.find(CLONE_START)
    if i < 0:
        return t, False
    pre = t.rfind('============================================================', 0, i)
    start = pre if pre >= 0 and i - pre < 80 else i
    end = -1
    for mk in CLONE_END_MARKERS:
        j = t.find(mk, i)
        if j >= 0:
            end = j + len(mk)
            break
    if end < 0:
        end = find_panel(t)
    while end < len(t) and t[end] in '\r\n':
        end += 1
    return t[:start].rstrip() + '\n\n' + t[end:].lstrip('\r\n'), True

def insert_before_panel(t, scene):
    ip = find_panel(t)
    if ip <= 0:
        return t + '\n\n' + scene + '\n'
    return t[:ip].rstrip() + '\n\n' + scene.strip() + '\n\n' + t[ip:].lstrip('\r\n')

def insert_mid(t, beat):
    ip = find_panel(t)
    body = t[:ip]
    target = int(len(body) * 0.38)
    lo = max(0, target - 400)
    hi = min(len(body), target + 800)
    window = body[lo:hi]
    rel = window.find('\n\n')
    if rel < 0:
        return t
    abs_pos = lo + rel
    return t[:abs_pos] + beat + t[abs_pos:]

def trim_words(t, need_cut):
    if need_cut <= 0:
        return t
    ip = find_panel(t)
    body, tail = t[:ip], t[ip:]
    lines = body.split('\n')
    out = []
    removed = 0
    skip_frags = [
        'Mùi mực và nước chè nguội',
        'Tiếng cửa sắt khép ngắn',
        'Gió lùa khe cửa mang mùi bụi kho',
        'Ngón tay Hùng chạm mép giấy đã sờn',
    ]
    for ln in lines:
        if removed < need_cut and any(f in ln for f in skip_frags):
            removed += max(1, len(ln.split()))
            continue
        out.append(ln)
    return '\n'.join(out) + tail

results = []
for n in CHS:
    fps = glob.glob(os.path.join(BASE, f'Chương {n} - *.txt'))
    if not fps:
        print('MISSING', n)
        continue
    fp = fps[0]
    raw = open(fp, encoding='utf-8').read()
    shutil.copy2(fp, os.path.join(BAK, os.path.basename(fp)))
    sc = open(os.path.join(SCDIR, f'sc{n}.txt'), encoding='utf-8').read().strip()

    t, did = strip_clone(raw)
    t = insert_mid(t, MID[n])
    t = insert_before_panel(t, sc)

    rv = ss.score_chapter(t, 3000, 4200, True, cfg)
    w = rv['metrics']['words']
    if w > 4200:
        t = trim_words(t, w - 4150)
        rv2 = ss.score_chapter(t, 3000, 4200, True, cfg)
        if rv2['metrics']['words'] > 4200 and MID[n].strip() in t:
            t = t.replace(MID[n], '\n\n', 1)
        rv = ss.score_chapter(t, 3000, 4200, True, cfg)
        w = rv['metrics']['words']
        if w > 4200:
            paras = sc.split('\n\n')
            if len(paras) > 1:
                sc2 = '\n\n'.join(paras[1:]) if len(paras) > 2 else sc
                t0, _ = strip_clone(raw)
                # keep mid only if room
                t0 = insert_before_panel(t0, sc2)
                t = t0
                rv = ss.score_chapter(t, 3000, 4200, True, cfg)
                if rv['metrics']['words'] <= 4100:
                    t = insert_mid(t, MID[n])
                    rv = ss.score_chapter(t, 3000, 4200, True, cfg)

    # final safety: if still over, drop mid
    if rv['metrics']['words'] > 4200 and MID[n].strip() in t:
        t = t.replace(MID[n], '\n\n', 1)
        rv = ss.score_chapter(t, 3000, 4200, True, cfg)

    open(fp, 'w', encoding='utf-8').write(t)
    rv = ss.score_chapter(open(fp, encoding='utf-8').read(), 3000, 4200, True, cfg)
    a = rv['axes']
    m = rv['metrics']
    print(
        f"Ch{n}|final={rv['final']:.2f}|van={a['van_chuong']}|cau={a['cau_truc']}|"
        f"nv={a['nhan_vat']}|w={m['words']}|cd={m['char_density']:.2f}|"
        f"sd={m['sensory_density']:.2f}|dlg={m['dialogue']}|clone_rm={did}|hf={rv['hard_fails']}"
    )
    results.append((n, rv['final'], m['words'], m['char_density']))

print('PASS', sum(1 for r in results if r[1] >= 9.5), '/', len(results))
