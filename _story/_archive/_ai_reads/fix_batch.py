# Targeted AI-rewrite clean: wife/spam/header/panel for ch151-180 FAIL chapters
import glob, re, json, sys
from pathlib import Path

base = "C:/Dev/MythLab/Nien Dai Thuong Gia"
base = "."
fails = [158,162,163,166,167,168,169,171,172,173,174,175,177,179]

led = json.loads(Path(base + '/system_ledger.json' if base != '.' else 'system_ledger.json').read_text(encoding='utf-8'))
ch = led.get('chapters') or led

panel_data = {}
for n in fails:
    e = ch[str(n)]
    skills = e.get('skills', [])
    sk = ', '.join(skills[-4:]) if isinstance(skills, list) and len(skills) > 4 else (', '.join(skills) if isinstance(skills, list) else str(skills))
    year = e['year']
    # Override year for ch167 (body says 1993) and ch179 (body says 1994)
    if n == 167: year = 1993
    if n == 179: year = 1994
    panel_data[n] = {
        'year': year,
        'exp_t': e['exp_total'],
        'exp_d': e['exp_delta'],
        'sp_t': e['space_m2'],
        'sp_d': e['space_delta'],
        'skills': sk
    }

WIFE_PATTERNS = [
    (r'Hùng quay sang, nhìn vợ trong bóng tối\..*?(?:đều đặn|ngủ say).*?(?:\n|$)', ''),
    (r'Hùng khẽ vươn tay, vuốt(?: mái tóc| nhẹ).*?(?:đều đặn|ngủ say).*?(?:\n|$)', ''),
    (r'Hùng bước ra, tay ôm nhẹ Lan.*?(?:Cảm ơn|ấm áp|vui vẻ).*?(?:\n|$)', ''),
    (r'Lan dựa đầu vào vai anh.*?(?:cuốn sách|nhìn nhau).*?(?:\n|$)', ''),
    (r'Hùng nhận ly, tay chạm tay Lan.*?(?:Cảm ơn|ấm áp).*?(?:\n|$)', ''),
    (r'Mắt họ chạm nhau, ấm áp.*?(?:\n|$)', ''),
    (r'bà Hà mỉm cười, dựa vào Hùng\..*?(?:\n|$)', ''),
    (r'(?:Anh|Hùng) bỏ thuốc đi.*?(?:vì em|em này).*?(?:\n|$)', ''),
    (r'"Thôi, vì em\." bà Hà mỉm cười.*?(?:\n|$)', ''),
    (r'Hùng lắc đầu: "Có em ở đây, không mệt\.".*?(?:\n|$)', 'Hùng lắc đầu: "Khong sao, chi hoi met thoi."\n'),
    (r'sau hai tháng xa nhà.*?đọc được vợ như đọc một trang giấy.*?(?:\n|$)', 'sau hai tháng xa nha, ba Ha van vay, hien lanh, quen thuoc.\n'),
    (r'Bà không giống vợ doanh nhân.*?vợ của một người đàn ông.*?(?:\n|$)', 'Ba Ha khong giong vo mot doanh nhan giau co — ba gian di, tan tao.\n'),
    (r'thay vợ đi.*?kiếm vợ trẻ.*?(?:\n|$)', ''),
    (r'nhưng vợ của một người làm kinh doanh hỏi những.*?(?:\n|$)', 'nhung ba hoi nhung cau sac sao, khong ai day o truong kinh te.\n'),
    (r'Giống hệt bữa cơm tối đầu tiên hai đứa mình ăn khi mới cưới\.', 'Giong het nhung ngay dau con kho khan.'),
    (r'bữa cơm tối đầu tiên hai đứa mình ăn khi mới cưới', 'bua com nhung ngay dau'),
    (r'"Nào\. Chúc thằng bạn già một cái Tết có vợ có em có bạn\."', '"Nao. Chuc thang ban gia mot cai Tet co em co ban."'),
    (r'Có mệt không anh\?.*?Có em ở đây, không mệt', 'Co met khong anh?'),
    (r'đều đặn\. "Có mệt không anh\?" bà Hà hỏi\. Hùng lắc đầu: "Có em ở đây, không mệt\."', 'deu dan. "Co met khong anh?" ba Ha hoi. Hung lac dau.'),
]

SPAM_PATTERNS = [
    r'Liệu ngày mai còn lỗ hổng\?.*?(?:\n|$)',
    r'Liệu ngày mai.*?(?:\n|$)',
    r'Hùng nhíu mày, siết ngón tay.*?(?:\n|$)',
    r'Hùng siết hàm.*?Lan liếc sổ.*?(?:\n|$)',
    r'(?:Lan )?liếc, cúi, gật\..*?(?:\n|$)',
    r'Bữa tối ấm cúng bắt đầu.*?(?:\n|$)',
    r'Đêm xuống, Hùng nằm trên giường.*?nhìn lên trần nhà.*?(?:\n|$)',
    r'Hùng mở tủ sách, lấy một cuốn sách cũ\..*?phai mờ\..*?(?:\n|$)',
    r'Một buổi sáng, Hùng thức dậy, mắt nhìn ra cửa sổ\..*?(?:\n|$)',
    r'Hai người ăn cơm tối\. Mùi cơm mới thơm, mùi canh cá nóng hổi\..*?(?:\n|$)',
    r'Trong nhà bếp, Hùng nhặt rau.*?Mùi gừng.*?tỏi phi thơm\..*?(?:\n|$)',
    r'Trong phòng khách, Hùng mở tủ sách, lấy một cuốn sách cũ\..*?(?:\n|$)',
    r'Buổi chiều, Hùng ngồi ngoài hiên nhà.*?(?:\n|$)',
    r'Mưa rơi trên mái ngói.*?Hùng và Minh ngồi bên nhau.*?(?:\n|$)',
    r'Trên bàn làm việc, sổ sách chất cao\..*?(?:\n|$)',
    r'Ngồi ngoài hiên nhà, nhìn ra đường phố\..*?(?:\n|$)',
    r'Sau bữa ăn, hai người ngồi trước hiên nhà\..*?(?:\n|$)',
    r'tay thoăn thoắt.*?(?:\n|$)',
    r'Canh chua cá lóc, anh thích mà\..*?(?:\n|$)',
    r'Ngoài sân, gió thổi qua mái tôn, mát rượi\..*?(?:\n|$)',
    r'Hai người nhìn nhau cười vui vẻ.*?(?:\n|$)',
    r'Nắng vàng nhạt rải.*?(?:\n|$)',
    r'hai người đọc cùng nhau.*?(?:\n|$)',
    r'Họ nắm tay nhau, im lặng, bình yên.*?(?:\n|$)',
    r'Mưa rồi\. "Ừ, mưa\.".*?(?:\n|$)',
    r'Buổi trưa, Hùng nằm võng.*?(?:\n|$)',
    r'đều đặn, bình yên\..*?(?:\n|$)',
]

results = []
for n in fails:
    p = glob.glob(f'Chương {n} - *.txt')[0]
    t = Path(p).read_text(encoding='utf-8')
    original = t

    # Fix header - ensure double ====
    m = re.match(r'^(={20,})\s*\n(Chương.*?)(\n|$)', t)
    if m:
        bar = m.group(1)
        title_line = m.group(2).strip()
        rest = t[m.end():].lstrip()
        if not rest.startswith('===='):
            t = bar + '\n' + title_line + '\n' + bar + '\n' + rest

    # Split body/panel
    pi = max(t.rfind('`H thng'), t.rfind('`Hệ thống'), t.rfind('''H thng'''))
    # More robust panel find
    for marker in ['H thng', 'Hệ thống', 'PANEL', 'GHI NHA^N']:
        idx = t.rfind(marker)
        if idx >= 0 and (pi < 0 or idx < pi):
            pi = idx
    if pi < 0:
        # find last ==== which is likely panel boundary
        lines = t.split('\n')
        for i in range(len(lines)-1, -1, -1):
            if lines[i].startswith('====') and i < len(lines)-2:
                # Find the preceding `H thng` or panel marker
                for j in range(max(0, i-20), i):
                    if 'GHI' in lines[j] or 'NHAN' in lines[j] or 'H thng' in lines[j]:
                        pi = t.find('\n'.join(lines[j:j+3]))
                        break
                if pi >= 0:
                    break

    if pi < 0:
        pi = t.find('=====', max(0, len(t)-500))
    if pi < 0:
        pi = len(t)

    body = t[:pi]
    # Apply wife strip
    for pat, repl in WIFE_PATTERNS:
        body = re.sub(pat, repl, body, flags=re.DOTALL)
        body = re.sub(pat, repl, body, flags=0)  # try without DOTALL too

    # Apply spam strip
    for pat in SPAM_PATTERNS:
        body = re.sub(pat, '', body, flags=re.DOTALL)
        body = re.sub(pat, '', body, flags=0)

    # Strip unaccent paragraphs
    lines = body.split('\n')
    clean = []
    for line in lines:
        s = line.strip()
        if not s:
            clean.append(line)
            continue
        has_vn = bool(re.search(r'[àáâãèéêìíòóôõùúýăđĩũơêưỴ̣̂̃̉]', s, re.I))
        if not has_vn and len(s) > 30:
            latin = sum(1 for c in s if c.isascii() and c.isalpha())
            if latin > 20 and latin / max(len(s), 1) > 0.5:
                continue
        clean.append(line)
    body = '\n'.join(clean)
    body = re.sub(r'\n{4,}', '\n\n\n', body)

    # Build new panel
    pd = panel_data[n]
    new_panel = (
        '`H thng - GHI NHAN ch.' + str(n) + '"\n'
        'Nam: ' + str(pd['year']) + '\n'
        'Tong EXP: ' + f"{pd['exp_t']:,}" + ' (+' + str(pd['exp_d']) + ' nhịp này)\n'
        'Khong gian kho: ' + f"{pd['sp_t']:,}m²" + ' (+' + str(pd['sp_d']) + 'm²)\n'
        'Ky nang trong yeu: ' + pd['skills'] + '\n'
        'Ghi chu: chuong ' + str(n) + '\n'
        + '=' * 60 + '\n'
    )

    result = body.rstrip() + '\n\n' + new_panel
    wc = len(body.split())

    results.append({
        'n': n, 'file': p, 'wc': wc,
        'len_orig': len(original), 'len_new': len(result),
        'body': result
    })
    print(f"Ch{n:3d}: {wc:5d}w | {len(original):6d} -> {len(result):6d}c")

# Write all
for r in results:
    if r['wc'] > 500:
        Path(r['file']).write_text(r['body'], encoding='utf-8')
        print(f"  WROTE: {r['file']}")
    else:
        print(f"  SKIP (short): {r['file']} ({r['wc']}w)")

print("\n=== DONE ===")
