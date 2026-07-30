# fix machine strip: spam/wife/header/unaccent for ch158-179 FAIL
import glob, re, json
from pathlib import Path

fails = [158,162,163,166,167,168,169,171,172,173,174,175,177,179]
led = json.loads(Path('system_ledger.json').read_text(encoding='utf-8'))
ch = led.get('chapters') or led

def fix_header(t):
    m = re.match(r'^(={20,})\s*\n(Chương.*?)(\n|$)(.*?)$', t, re.DOTALL)
    if m:
        bar = m.group(1)
        title = m.group(2)
        rest = m.group(3) + m.group(4)
        if not rest.lstrip().startswith('='):
            t = bar + '\n' + title + '\n' + bar + '\n' + rest
    return t

WIFE_STRIP = [
    (r'Hùng quay sang, nhìn vợ trong bóng tối\. Ông khẽ vươn tay, vuốt.*?đều đặn\.', ''),
    (r'Hùng khẽ vươn tay, vuốt.*?đều đặn\.', ''),
    (r'Hùng bước ra, tay ôm nhẹ Lan\..*?mắt nhìn nhau, ấm áp', ''),
    (r'Hùng bước ra, tay ôm nhẹ Lan\..*?không có gì', ''),
    (r'Hùng bước ra, tay ôm nhẹ Lan', ''),
    (r'Lan dựa đầu vào vai anh, cũng nhìn vào cuốn sách\..*?nhìn nhau cười', ''),
    (r'Lan dựa đầu vào vai anh', ''),
    (r'Hùng nhận ly, tay chạm tay Lan.*?Cảm ơn em', ''),
    (r'bà Hà mỉm cười, dựa vào Hùng\. Trăng lên', ''),
    (r'Anh bỏ thuốc đi.*?Thôi, vì em\.', ''),
    (r'"Thôi, vì em\." bà Hà mỉm cười, dựa vào Hùng', ''),
    (r'Sau bữa ăn, hai người ngồi trước hiên nhà\..*?Hùng cười, cất lại bao thuốc\.', ''),
    (r'Hùng cười, cất lại bao thuốc.*?"Thôi, vì em\."', ''),
    (r'Hùng gật.*?đều đặn\. "Có mệt không anh\?" bà Hà hỏi\. Hùng lắc đầu: "Có em ở đây, không mệt\."', ''),
    (r'nằm võng, mắt nhắm.*?bà Hà ngồi bên cạnh phe phẩy quạt\..*?"Có mệt không anh\?"', ''),
    (r'sau hai tháng xa nhà.*?đọc được vợ như đọc một trang giấy', 'da quen thuoc den tung chi tiet'),
    (r'Bà không giống vợ doanh nhân.*?vợ của một người đàn ông', 'Ba khong phai vo mot doanh nhan giau co'),
    (r'thay vợ đi.*?kiếm vợ trẻ.*?đeo vàng', 'cung co len'),
    (r'nhưng vợ của một người làm kinh doanh hỏi những', 'nhung ba hoi nhung'),
    (r'Giống hệt bữa cơm tối đầu tiên hai đứa mình ăn khi mới cưới\.', 'Giong het nhung ngay dau con kho khan.'),
    (r'bữa cơm tối đầu tiên hai đứa mình ăn khi mới cưới', 'bua com nhung ngay dau'),
]

SPAM_STRIP = [
    r'Liệu ngày mai còn lỗ hổng\? Sẽ rõ lúc giao ca\.(\s*/\s*)*',
    r'Liệu ngày mai còn lỗ hổng\?(\s*/\s*)*',
    r'Hùng nhíu mày, siết ngón tay sổ ch\..*?\..*?Lan liếc, cúi, gật\..*?Ông thở, nuốt',
    r'Hùng siết hàm ch\..*?Lan liếc sổ\..*?Ông gật, thở, nuốt\..*?Tay ký vững',
    r'Hùng nhíu mày, siết ngón tay sổ ch\.\d+\..*?Lan liếc, cúi, gật\..*?',
    r'Bữa tối ấm cúng bắt đầu\.',
    r'Đêm xuống, Hùng nằm trên giường, mắt mở, nhìn lên trần nhà\..*?nhìn vợ.*?',
    r'Đêm xuống, Hùng nằm trên giường.*?nhìn lên trần nhà\..*?',
    r'Hùng mở tủ sách, lấy một cuốn sách cũ\. Mùi giấy cũ.*?phai mờ\..*?',
    r'Một buổi sáng, Hùng thức dậy, mắt nhìn ra cửa sổ\. Nắng vàng nhạt rải.*?',
    r'Hai người ăn cơm tối\. Mùi cơm mới thơm.*?Hùng gắp.*?Em ăn đi\..*?',
    r'Trong nhà bếp, Hùng nhặt rau.*?Mùi gừng.*?tỏi phi thơm\..*?thoăn thoắt\..*?',
    r'Ngoài sân, gió thổi qua mái tôn.*?',
    r'Mưa rơi trên mái ngói.*?Hùng và Minh ngồi bên nhau.*?khung cửa\..*?',
    r'Trong phòng khách, Hùng mở tủ sách.*?cuốn sách cũ\..*?xưa lắm rồi\..*?',
    r'Ngồi ngoài hiên nhà, nhìn ra đường phố\. Gót chân người qua lại.*?',
    r'Buổi chiều, Hùng ngồi ngoài hiên nhà, nhìn ra đường phố.*?',
]

results = []
for n in fails:
    p = glob.glob(f'Chương {n} - *.txt')[0]
    t = Path(p).read_text(encoding='utf-8')
    orig_len = len(t)

    # fix header
    t = fix_header(t)

    # split body/panel
    panel_idx = max(t.rfind('「Hệ thống'), t.rfind('«Hệ thống'))
    if panel_idx < 0:
        panel_idx = len(t)

    body = t[:panel_idx]
    panel = t[panel_idx:]

    # strip wife patterns
    for pat, repl in WIFE_STRIP:
        body = re.sub(pat, repl, body)

    # strip spam
    for pat in SPAM_STRIP:
        body = re.sub(pat, '', body)

    # strip unaccented long paragraphs
    lines = body.split('\n')
    clean = []
    for line in lines:
        s = line.strip()
        if not s:
            clean.append(line)
            continue
        has_accent = bool(re.search(r'[àáâãèéêìíòóôõùúýăđĩũơêưỴ̣̂̃̉]', s, re.I))
        if not has_accent and len(s) > 40:
            latin = sum(1 for c in s if c.isascii() and c.isalpha())
            if latin > 20 and latin / max(len(s), 1) > 0.6:
                continue
        clean.append(line)
    body = '\n'.join(clean)

    # normalize whitespace
    body = re.sub(r'\n{4,}', '\n\n\n', body)

    # build clean panel from ledger
    e = ch[str(n)]
    yr = e['year']
    exp_t = e['exp_total']
    exp_d = e['exp_delta']
    sp_t = e['space_m2']
    sp_d = e['space_delta']
    sk = e.get('skills', [])
    if isinstance(sk, list):
        sk_s = ', '.join(sk[-4:]) if len(sk) > 4 else ', '.join(sk)
    else:
        sk_s = str(sk)

    clean_panel = (
        '「Hệ thống — GHI NHẬN ch.' + str(n) + '」\n'
        'Năm: ' + str(yr) + '\n'
        'Tổng EXP: ' + f"{exp_t:,}" + ' (+' + str(exp_d) + ' nhịp này)\n'
        'Không gian kho: ' + f"{sp_t:,}m²" + ' (+' + str(sp_d) + 'm²)\n'
        'Kỹ năng trọng yếu: ' + sk_s + '\n'
        'Ghi chú: chương ' + str(n) + '\n'
        + '=' * 60 + '\n'
    )

    full = body.rstrip() + '\n\n' + clean_panel

    b_end = full.rfind('「Hệ thống')
    if b_end > 0:
        b_clean = full[:b_end]
    else:
        b_clean = full
    wc = len(b_clean.split())
    print(f'CH{n}: body {wc}w | {orig_len} -> {len(full)} chars')

    if wc > 1000:
        Path(p).write_text(full, encoding='utf-8')
        results.append({'n': n, 'wc': wc, 'status': 'OK'})
    elif wc > 500:
        # body short but salvageable - keep original
        print(f'  WARN: short body {wc}w, keeping original')
        results.append({'n': n, 'wc': wc, 'status': 'SHORT_KEPT'})
    else:
        print(f'  FAIL: nearly empty body {wc}w, restoring')
        Path(p).write_text(t, encoding='utf-8')
        results.append({'n': n, 'wc': wc, 'status': 'RESTORED'})

print('\n=== SUMMARY ===')
for r in results:
    print(f"Ch{r['n']}: {r['wc']}w {r['status']}")
