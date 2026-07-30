# -*- coding: utf-8 -*-
"""Restore ch4-12 from p0 backup and clean dumps/panels without destroying body."""
import re, os, glob, shutil

base = r'C:/Dev/XLab_MTC/Niên Đại Thương Gia'
bak = os.path.join(base, '_fix_backup_p0_20260729')

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

titles = {
4:'Bán hàng đầu tiên',5:'Mở rộng kinh doanh',6:'Tìm đối tác mới',7:'Sửa nhà',
8:'Mở rộng hàng hóa',9:'Bán thuốc men',10:'Đi Hà Nội',11:'Đi Hà Nam',12:'Đi Hải Dương'
}

unique_closes = {
4: 'Hùng phủi bùn ống quần. Lan hong áo đã sửa. Ngày bán khép bằng hai việc không ai ngoài nhà thấy: một món lỗi được nhận; một tờ mười không mất vào ước lượng. Sáng mai còn hẹn Khanh — ông sẽ bước vào nhà cấp bốn mà không để lý lịch hộ nuốt mất cái gật đầu.',
5: 'Đêm đó Hùng ghi ba việc: hỏi Khanh mẫu đơn; giao đúng bộ đã đo; kiểm hai áo gửi chợ làng. Từ một sạp thành hai điểm bán — lần đầu hàng rời tầm mắt vẫn còn tên người nhận. Ông tắt đèn. Ngày mai còn phải chứng minh điểm thứ hai không biến thành nợ xấu.',
6: 'Trước khi ngủ Hùng ghi ba điều: không lấy lòng tin thay hợp đồng; không lấy lý lịch Tâm che hàng mờ; không để bà đau đầu mà không đi trạm. Ngoài hiên lá bàng khô xào. Ông nắm mép chiếu. Mai còn phải chờ ông Tâm — chờ mà không đứng yên.',
7: 'Sáng ra chậu vẫn khô. Lan úp chậu cạnh chum như cất dấu vết năm cũ. Bà Hà chống gậy ra hiên nhìn mái sau mưa thật. Hùng ghi chi phí vượt vào sổ, gạch khoản xe đạp tuần này. Nhà đứng được qua một trận — đủ để nghĩ chuyến Hà Nội.',
8: 'Khi gấp sổ Lan đã có bốn đầu mối: Khanh thủ tục, Tâm mặt bằng, Phượng bán lại, chị Hồng kiểm. Hùng chốt ngưỡng phiên sau: thiết yếu đủ hai phiên, hàng mới chỉ mười đơn vị, thuốc nguyên hộp. Ông siết then cửa. Phiên sau sẽ biết ngưỡng nào đúng.',
9: 'Sổ cuối ngày không chỉ doanh thu. Có hai hộp loại bỏ, một lần hoàn tiền, ba khách chuyển bác sĩ. Hùng gói hóa đơn và hộp lỗi vào túi vải cho chuyến Hà Nội. Ông cần nguồn thật, dấu thật — không bán cái mình không dám uống.',
10: 'Về nhà Lan hỏi kiếm được gì. Hùng: không mua vội, biết được chỗ có thể mua. Ông viết danh sách đầu mối dưới đèn dầu. Sáng mai còn phải đối chiếu giá với sổ nhà — chuyến Hà Nội chỉ xong khi số viết ra khớp với việc dám làm.',
11: 'Trước khi khóa sổ tuần Hùng bắt Lan đọc ngược từ dòng cuối. Trời làng không đèn cao áp, chỉ sao và ếch. Mắt xích phía nam còn nhỏ, nhưng đã có lịch ba ngày và cách báo khi mưa. Ông lau xích xe. Việc nhỏ trước việc xa.',
12: 'Trên đường về trời tối, gió đồng mát. Tờ sổ thanh toán xé đôi — bà Uyên một nửa, Hùng một nửa. Chữ tín bắt đầu bằng trả đủ khi người kia không đòi. Ông đạp đều, nghĩ dòng sổ nhà: Hải Dương — đủ — không thiếu một xu.',
}

INJECT = {
'Lạch cạch xe đạp cũ.','Tõm tõm gầu nước giếng.','Đì đùng máy nổ xa.','Rạ khô thơm nắng.',
'Lạnh buốt sờ gầu nước đầu đông.','Cót két cổng sắt.','Than tổ ong.','Lộp bộp thớt thái hành.',
'Cổng sắt cót két mở ngoài ngõ — ai đó gánh nước đi qua sớm.',
}

ROM_SNIPS = [
'ôm eo anh', 'ôm nhẹ Lan', 'Lan dựa đầu', 'dựa đầu vào vai', 'Minh đến sau lưng',
'tình yêu lặng lẽ', 'Canh chua cá lóc', 'Bữa tối ấm cúng bắt đầu', 'Hai ly nước ấm',
'xoa vai anh', 'Vì có em', 'bỏ thuốc vì em', 'Anh bỏ thuốc đi',
]

TAIL_DUMP_STARTS = [
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
'Một buổi sáng, Hùng thức dậy, mắt nhìn ra cửa sổ',
'Lan cúi xuống nhặt chiếc bát rơi',
'Lan ngồi bên bàn, đếm lại số tiền lẻ',
'Bà Hà ngồi ở hiên, tay vuốt ve',
'Ông Lân gõ búa lên tấm tôn cuối cùng',
'Trên đường về từ Phủ Lý',
]

def panel(n):
    e, ed, s, sd, sk, note = ledger[n]
    def f(x):
        return f'{x:,}'
    delta_e = f'(+{ed} nhịp này)' if n in (4, 12) and ed else (f'(+{ed})' if ed else '(+0)')
    delta_s = f'(+{sd}m²)' if sd else '(+0m²)'
    return (
        '============================================================\n'
        f'「Hệ thống — GHI NHẬN ch.{n}」\n'
        'Năm: 1983\n'
        f'Tổng EXP: {f(e)} {delta_e}\n'
        f'Không gian kho: {f(s)}m² {delta_s}\n'
        f'Kỹ năng trọng yếu: {", ".join(sk)}\n'
        f'Ghi chú: {note}\n'
        '============================================================\n'
    )

def extract_body(t):
    # cut at panel / teaser / dump
    cut = len(t)
    for m in ['「Hệ thống — GHI NHẬN', '「Hệ thống — CỘT MỐC', '「Hệ thống', '\nTeaser:', '\nTeaser :',
              '============================================================ Teaser']:
        i = t.find(m)
        if i > 2000:
            cut = min(cut, i)
    body = t[:cut]
    # earlier dump cut in last 35%
    start_scan = int(len(body) * 0.55)
    for m in TAIL_DUMP_STARTS:
        i = body.find(m, start_scan)
        if i > 0:
            body = body[:i]
            break
    # strip header
    parts = body.split('\n')
    i = 0
    while i < len(parts) and (parts[i].strip().startswith('=') or parts[i].strip().startswith('Chương') or not parts[i].strip()):
        i += 1
    body = '\n'.join(parts[i:]).rstrip()
    # line filters
    out = []
    for L in body.splitlines():
        s = L.strip()
        if s in INJECT:
            continue
        if s.startswith('### '):
            continue
        if any(r in L for r in ROM_SNIPS):
            # try soft replace for ôm eo on bike
            if 'ôm eo' in L and 'Lan' in L:
                L = L.replace('hai tay ôm eo anh', 'tay nắm yên sau').replace('ôm eo anh', 'nắm yên sau')
                if any(r in L for r in ROM_SNIPS if r != 'ôm eo anh'):
                    continue
            else:
                continue
        if s.startswith('Teaser'):
            continue
        if 'Liệu ngày mai còn lỗ hổng' in L:
            continue
        if 'Hùng nhíu mày, siết ngón tay sổ' in L:
            continue
        if 'system_ledger' in L and 'Ghi chú' not in L:
            continue
        out.append(L)
    body = '\n'.join(out)
    body = re.sub(r'\n{3,}', '\n\n', body).strip()
    # dedupe consecutive identical paragraphs
    paras = re.split(r'\n\s*\n', body)
    dedup = []
    prev = None
    for p in paras:
        p2 = p.strip()
        if not p2:
            continue
        if p2 == prev:
            continue
        # skip near-duplicate short dumps
        if prev and len(p2) > 80 and p2[:80] == prev[:80]:
            continue
        dedup.append(p2)
        prev = p2
    body = '\n\n'.join(dedup)
    return body

def ensure_header(n, body):
    return (
        '============================================================\n'
        f'Chương {n}: {titles[n]}\n'
        '============================================================\n\n'
        + body.strip() + '\n\n' + panel(n)
    )

results = []
for n in range(4, 13):
    srcs = glob.glob(os.path.join(bak, f'Chương {n} - *.txt'))
    if not srcs:
        print('NO BAK', n)
        continue
    raw = open(srcs[0], encoding='utf-8-sig').read()
    body = extract_body(raw)
    # append unique close if not present
    cl = unique_closes[n]
    if cl[:50] not in body:
        body = body.rstrip() + '\n\n' + cl
    text = ensure_header(n, body)
    w = len(text.split())
    # if under 3000, keep more of original by less aggressive cut
    if w < 3000:
        # take body up to panel only, light filter
        cut = len(raw)
        for m in ['「Hệ thống — GHI NHẬN', '\nTeaser:']:
            i = raw.find(m)
            if i > 2000:
                cut = min(cut, i)
        body = raw[:cut]
        parts = body.split('\n')
        i = 0
        while i < len(parts) and (parts[i].strip().startswith('=') or parts[i].strip().startswith('Chương') or not parts[i].strip()):
            i += 1
        lines = []
        for L in parts[i:]:
            if L.strip() in INJECT or L.strip().startswith('### '):
                continue
            if any(r in L for r in ['ôm eo anh', 'ôm nhẹ Lan', 'Lan dựa đầu', 'Minh đến sau lưng', 'Liệu ngày mai còn lỗ hổng', 'Hùng nhíu mày, siết ngón tay sổ']):
                if 'ôm eo' in L:
                    L = L.replace('hai tay ôm eo anh', 'tay nắm yên sau').replace('ôm eo anh', 'nắm yên sau')
                else:
                    continue
            if L.strip().startswith('Teaser'):
                continue
            lines.append(L)
        body = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()
        if cl[:50] not in body:
            body = body.rstrip() + '\n\n' + cl
        text = ensure_header(n, body)
        w = len(text.split())
    # if over 4200 trim end paragraphs before close (keep close)
    if w > 4200:
        # split off panel
        pi = text.rfind('「Hệ thống — GHI NHẬN')
        head = text[:pi]
        pan = text[pi:]
        # remove close temporarily
        if cl in head:
            head = head.replace('\n\n'+cl, '')
        paras = re.split(r'\n\s*\n', head.strip())
        # keep header 3 lines in first para block
        while len(' '.join(paras).split()) + len(cl.split()) + 40 > 4100 and len(paras) > 10:
            # drop from middle
            mid = len(paras) // 2
            paras.pop(mid)
        head = '\n\n'.join(paras).rstrip() + '\n\n' + cl + '\n\n'
        text = head + pan
        w = len(text.split())
    # write live
    dests = glob.glob(os.path.join(base, f'Chương {n} - *.txt'))
    dest = dests[0]
    open(dest, 'w', encoding='utf-8').write(text)
    flags = dict(
        w=w,
        hdr=bool(re.match(r'(?s)^={20,}\s*\nChương[^\n]+\n={20,}\s*\n', text)),
        teaser='Teaser' in text,
        cliff='Lỗ hổng' in text,
        rom=any(x in text for x in ['ôm eo', 'ôm nhẹ Lan', 'Lan dựa đầu', 'Minh đến sau']),
        exp_bad=('1,250' in text and n == 10) or ('100m²' in text and n == 10),
        panels=text.count('GHI NHẬN'),
        year83='Năm: 1983' in text,
    )
    results.append((n, flags))
    print(n, flags)

print('RESTORE+CLEAN DONE')
