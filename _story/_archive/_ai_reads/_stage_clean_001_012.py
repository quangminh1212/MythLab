# -*- coding: utf-8 -*-
import re, glob, os
base = r'C:/Dev/XLab_MTC/Niên Đại Thương Gia'
out = os.path.join(base, '_ai_reads', '_clean_staging')
os.makedirs(out, exist_ok=True)

ledger = {
4:(90,30,1150,50,['Thương mại lv1','Ngôn ngữ lv1'],'Bán hàng có cam kết sửa lỗi; đếm tiền hai lần; hẹn nhà Khanh.'),
5:(120,30,1200,50,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2'],'Hoàn thành no đủ tháng; Thương mại lv2; điểm bán thứ hai.'),
6:(166,46,1200,0,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2'],'Gặp ông Tâm; hợp tác thử; chuẩn bị Hà Nội.'),
7:(212,46,1200,0,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2'],'Sửa nhà; mưa thử mái; giữ vốn chuyến Hà Nội.'),
8:(258,46,1200,0,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2'],'Mở rộng hàng thiết yếu; sổ với ông Tâm; ngưỡng nhập.'),
9:(304,46,1200,0,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2','Y tế lv1'],'Bán thuốc có ranh giới; hoàn tiền; Y tế lv1.'),
10:(350,46,1200,0,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2','Y tế lv1'],'Chuyến Hà Nội — hóa đơn, phiếu, sạp cố định.'),
11:(405,55,1240,40,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2','Y tế lv1'],'Mở tuyến Hà Nam; lịch giao; đọc sổ ngược.'),
12:(460,55,1280,40,['Thương mại lv1','Ngôn ngữ lv1','Thương mại lv2','Y tế lv1'],'Hải Dương — chữ tín; sổ xé đôi; trả đủ.'),
}

DUMP_MARKERS = [
'Liệu ngày mai còn lỗ hổng',
'Hùng nhíu mày, siết ngón tay sổ',
'Teaser:',
'Teaser :',
'Hai người ăn cơm tối. Mùi cơm mới thơm',
'Buổi chiều, Hùng ngồi ngoài hiên nhà, nhìn ra đường phố',
'Đêm xuống, Hùng nằm trên giường, mắt mở',
'Mưa rơi trên mái ngói, tiếng mưa rì rào. Hùng và',
'Trên bàn làm việc, sổ sách chất cao',
'Trong nhà bếp, Hùng nhặt rau',
'Minh đến sau lưng',
'Lan dựa đầu',
'Canh chua cá lóc',
'Bữa tối ấm cúng bắt đầu',
'「Hệ thống — CỘT MỐC',
'============================================================ Teaser',
'============================================================\n\n\nLan cúi',
'Lan cúi xuống nhặt chiếc bát rơi',
'Lan ngồi bên bàn, đếm lại số tiền lẻ',
'Bà Hà ngồi ở hiên, tay vuốt ve chiếc lá',
'Ông Lân gõ búa lên tấm tôn cuối cùng',
'Trên đường về từ Phủ Lý, Hùng dừng xe đạp bên bờ sông',
]

unique_closes = {
5: "Đêm đó Hùng ghi ba việc: hỏi Khanh mẫu đơn; giao đúng bộ đã đo; kiểm hai áo gửi chợ làng. Từ một sạp thành hai điểm bán — lần đầu hàng rời tầm mắt vẫn còn tên người nhận. Ông tắt đèn. Ngày mai còn phải chứng minh điểm thứ hai không biến thành nợ xấu.",
6: "Trước khi ngủ Hùng ghi ba điều: không lấy lòng tin thay hợp đồng; không lấy lý lịch Tâm che hàng mờ; không để bà đau đầu mà không đi trạm. Ngoài hiên lá bàng khô xào. Ông nắm mép chiếu. Mai còn phải chờ ông Tâm — chờ mà không đứng yên.",
7: "Sáng ra chậu vẫn khô. Lan úp chậu cạnh chum như cất dấu vết năm cũ. Bà Hà chống gậy ra hiên nhìn mái sau mưa thật, bảo giữ lá cọ lành che chuồng gà. Hùng ghi chi phí vượt vào sổ, gạch khoản xe đạp tuần này. Nhà đứng được qua một trận — đủ để nghĩ chuyến Hà Nội.",
8: "Khi gấp sổ Lan đã có bốn đầu mối: Khanh thủ tục, Tâm mặt bằng, Phượng bán lại, chị Hồng kiểm. Hùng chốt ngưỡng phiên sau: thiết yếu đủ hai phiên, hàng mới chỉ mười đơn vị, thuốc nguyên hộp. Ông siết then cửa. Phiên sau sẽ biết ngưỡng nào đúng.",
9: "Sổ cuối ngày không chỉ doanh thu. Có hai hộp loại bỏ, một lần hoàn tiền, ba khách chuyển bác sĩ. Hùng gói hóa đơn và hộp lỗi vào túi vải cho chuyến Hà Nội. Ông cần nguồn thật, dấu thật — không bán cái mình không dám uống.",
10: "Về nhà Lan hỏi kiếm được gì. Hùng: không mua vội, biết được chỗ có thể mua. Ông viết danh sách đầu mối dưới đèn dầu, mực chua nhẹ. Sáng mai còn phải đối chiếu giá với sổ nhà — chuyến Hà Nội chỉ xong khi số viết ra khớp với việc dám làm.",
11: "Trước khi khóa sổ tuần Hùng bắt Lan đọc ngược từ dòng cuối. Trời làng không đèn cao áp, chỉ sao và ếch. Trong cái tối ấy mắt xích phía nam còn nhỏ, nhưng đã có lịch ba ngày và cách báo khi mưa. Ông lau xích xe. Việc nhỏ trước việc xa.",
12: "Trên đường về trời tối, gió đồng mát. Tờ sổ thanh toán xé đôi — bà Uyên một nửa, Hùng một nửa. Chữ tín bắt đầu bằng trả đủ khi người kia không đòi. Ông không hát. Ông chỉ đạp đều, nghĩ đến dòng sổ nhà sẽ ghi: Hải Dương — đủ — không thiếu một xu.",
}

titles = {
4:'Bán hàng đầu tiên',5:'Mở rộng kinh doanh',6:'Tìm đối tác mới',7:'Sửa nhà',
8:'Mở rộng hàng hóa',9:'Bán thuốc men',10:'Đi Hà Nội',11:'Đi Hà Nam',12:'Đi Hải Dương'
}

inject_exact = {
'Lạch cạch xe đạp cũ.','Tõm tõm gầu nước giếng.','Đì đùng máy nổ xa.','Rạ khô thơm nắng.',
'Lạnh buốt sờ gầu nước đầu đông.','Cót két cổng sắt.','Than tổ ong.','Lộp bộp thớt thái hành.',
'Tõm tõm gầu nước giếng.'
}

def find_cut(t):
    gi = max(t.find('「Hệ thống'), t.find('「Hệ thống'), t.find('Hệ thống — GHI'))
    # find last GHI style
    for m in ['「Hệ thống — GHI NHẬN', '「Hệ thống', 'Teaser:']:
        i = t.rfind(m)
        if i > 0:
            gi = i if gi < 0 else min(gi, i) if m != 'Teaser:' else gi
    # prefer first teaser or dump in last third
    body = t
    cut = len(t)
    # panel start
    for m in ['「Hệ thống — GHI NHẬN', '「Hệ thống — CỘT MỐC', '\nTeaser:', '\nTeaser :']:
        i = t.find(m)
        if i > 3000:
            cut = min(cut, i)
    body = t[:cut]
    for m in DUMP_MARKERS:
        i = body.find(m)
        if i > 2500 and i < len(body):
            body = body[:i]
            break
    body2 = body.rstrip()
    while body2.endswith('=') or body2.endswith('='):
        body2 = body2.rstrip('=').rstrip()
    lines = body2.splitlines()
    clean = []
    for L in lines:
        s = L.strip()
        if s in inject_exact:
            continue
        if s.startswith('### '):
            continue
        if 'ôm eo' in L:
            L = L.replace('hai tay ôm eo anh', 'tay nắm yên sau').replace('ôm eo anh', 'nắm yên sau')
        if 'tay ôm nhẹ Lan' in L or 'ôm nhẹ Lan' in L:
            continue
        if 'Lan dựa đầu vào vai' in L or 'dựa đầu vào vai anh' in L:
            continue
        if 'tình yêu lặng lẽ' in L:
            continue
        clean.append(L)
    body2 = '\n'.join(clean).rstrip()
    body2 = re.sub(r'\n{3,}', '\n\n', body2)
    # strip header
    parts = body2.split('\n')
    i = 0
    while i < len(parts) and (parts[i].startswith('=') or parts[i].startswith('Chương') or not parts[i].strip()):
        i += 1
    return '\n'.join(parts[i:]).strip()

def panel(n):
    e, ed, s, sd, sk, note = ledger[n]
    def f(x):
        return f'{x:,}'
    sks = ', '.join(sk)
    delta_e = f'(+{ed})' if ed else '(+0)'
    if n in (3, 4, 12):
        delta_e = f'(+{ed} nhịp này)' if ed else '(+0)'
    delta_s = f'(+{sd}m²)' if sd else '(+0m²)'
    return (
        '============================================================\n'
        f'「Hệ thống — GHI NHẬN ch.{n}」\n'
        'Năm: 1983\n'
        f'Tổng EXP: {f(e)} {delta_e}\n'
        f'Không gian kho: {f(s)}m² {delta_s}\n'
        f'Kỹ năng trọng yếu: {sks}\n'
        f'Ghi chú: {note}\n'
        '============================================================\n'
    )

# Prefer backup originals for ch5-12 if live was partially rewritten short
backup_roots = [
    os.path.join(base, '_fix_backup_p0_20260729'),
    os.path.join(base, '_phase1_backup'),
]

def load_best(n):
    live = glob.glob(os.path.join(base, f'Chương {n} - *.txt'))[0]
    live_t = open(live, encoding='utf-8-sig').read()
    best = live_t
    best_w = len(live_t.split())
    # if live short or clearly cleaned stub, try backup longer core
    for br in backup_roots:
        if not os.path.isdir(br):
            continue
        cands = glob.glob(os.path.join(br, f'Chương {n} - *.txt')) + glob.glob(os.path.join(br, f'*Chương {n}*'))
        for c in cands:
            try:
                t = open(c, encoding='utf-8-sig').read()
            except Exception:
                continue
            w = len(t.split())
            if w > best_w and w > 2500:
                best = t
                best_w = w
    return best, live

results = []
for n in range(5, 13):
    raw, live_path = load_best(n)
    body = find_cut(raw)
    if n in unique_closes:
        # avoid double close
        if unique_closes[n][:40] not in body:
            body = body.rstrip() + '\n\n' + unique_closes[n]
    header = (
        '============================================================\n'
        f'Chương {n}: {titles[n]}\n'
        '============================================================\n\n'
    )
    text = header + body + '\n\n' + panel(n)
    w = len(text.split())
    # if still short, keep more of original before dumps by less aggressive cut
    if w < 3000:
        # retry with later cut
        gi = raw.find('「Hệ thống — GHI NHẬN')
        if gi < 0:
            gi = raw.find('Teaser:')
        if gi < 0:
            gi = len(raw)
        body = raw[:gi]
        # only strip inject lines and romance blocks
        lines = []
        skip_block = 0
        for L in body.splitlines():
            if L.startswith('=') and 'Chương' not in L and len(L) > 20:
                continue
            if L.strip().startswith('Chương '):
                continue
            if L.strip() in inject_exact or L.strip().startswith('### '):
                continue
            if any(x in L for x in ['ôm eo anh', 'ôm nhẹ Lan', 'Lan dựa đầu', 'Minh đến sau lưng', 'tình yêu lặng lẽ']):
                continue
            if 'Liệu ngày mai còn lỗ hổng' in L or 'Hùng nhíu mày, siết ngón tay sổ' in L:
                continue
            if L.strip().startswith('Teaser'):
                continue
            lines.append(L)
        body = '\n'.join(lines).strip()
        parts = body.split('\n')
        i = 0
        while i < len(parts) and (parts[i].startswith('=') or parts[i].startswith('Chương') or not parts[i].strip()):
            i += 1
        body = '\n'.join(parts[i:]).strip()
        if n in unique_closes and unique_closes[n][:40] not in body:
            body = body.rstrip() + '\n\n' + unique_closes[n]
        text = header + body + '\n\n' + panel(n)
        w = len(text.split())
    dest = os.path.join(out, f'ch{n}.txt')
    open(dest, 'w', encoding='utf-8').write(text)
    flags = {
        'w': w,
        'teaser': 'Teaser' in text,
        'cliff': 'Liệu ngày mai còn lỗ hổng' in text,
        'rom': any(x in text for x in ['ôm eo', 'Lan dựa', 'Minh đến sau', 'ôm nhẹ Lan']),
        'exp1250': '1,250' in text or 'Tổng EXP: 1,250' in text,
        'sp100': '100m²' in text and '1,000' not in text,
        'panels': text.count('GHI NHẬN'),
    }
    results.append((n, flags, dest, live_path))
    print(n, flags)

# Also build expanded ch4 from live short + backup core
n = 4
raw, live_path = load_best(4)
body = find_cut(raw)
if len(body.split()) < 2500:
    # merge: use backup core cut
    raw2 = raw
    for br in backup_roots:
        cands = glob.glob(os.path.join(br, f'Chương 4*'))
        for c in cands:
            t = open(c, encoding='utf-8-sig').read()
            if len(t.split()) > len(raw2.split()):
                raw2 = t
    body = find_cut(raw2)
header = (
    '============================================================\n'
    f'Chương 4: {titles[4]}\n'
    '============================================================\n\n'
)
text = header + body + '\n\n' + panel(4)
open(os.path.join(out, 'ch4.txt'), 'w', encoding='utf-8').write(text)
print(4, len(text.split()), 'words staged')
print('DONE', out)
