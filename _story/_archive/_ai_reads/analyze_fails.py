# Analyze FAIL chapters: panel location, filler paragraphs, word counts
import glob, re
from pathlib import Path

fails = [158,162,163,166,167,168,169,171,172,173,174,175,177,179]

# Signature substrings marking machine-generated filler paragraphs (romance/clone/cliff/CHAR-spam)
FILLER_SIGS = [
    "Liệu ngày mai còn lỗ hổng",
    "siết ngón tay sổ ch.",
    "Lan liếc, cúi, gật",
    "Lan liếc sổ",
    "nhìn vợ trong bóng tối",
    "vuốt tóc cô",
    "khẽ vươn tay, vuốt",
    "tay ôm nhẹ Lan",
    "Lan dựa đầu vào vai anh",
    "dựa đầu vào vai Hùng",
    "mở tủ sách, lấy một cuốn sách cũ",
    "Hai người ăn cơm tối. Mùi cơm mới thơm",
    "Trong nhà bếp, Hùng nhặt rau",
    "Canh chua cá lóc, anh thích mà",
    "Bữa tối ấm cúng bắt đầu",
    "Một người khách đến, mắt đỏ hoe",
    "Buổi trưa, Hùng nằm võng",
    "đang pha trà. Mùi trà xanh thơm",
    "Mắt họ chạm nhau, ấm áp",
    "Hai người nhìn nhau cười vui vẻ",
    "hai người ngồi trước hiên nhà. Hùng rút thuốc",
    "bà Hà mỉm cười, dựa vào Hùng",
    "Có em ở đây, không mệt",
    "Chiều tà, Hùng ngồi bậc thềm",
    "dựa đầu vào vai Hùng",
    "Hùng cảm thấy bình yên. Ông nhai chậm",
    "Hai người đọc cùng nhau",
    "Hùng mở cửa sổ, đón ánh nắng sớm",
    "Mùi hoa sữa thoang thoảng",
]

def find_panel(t):
    idx = t.rfind('「Hệ thống')
    return idx

for n in fails:
    p = glob.glob(f'Chương {n} - *.txt')[0]
    t = Path(p).read_text(encoding='utf-8')
    pi = find_panel(t)
    body = t[:pi] if pi >= 0 else t
    panel = t[pi:] if pi >= 0 else ""
    paras = re.split(r'\n\s*\n', body)
    kept, dropped = [], []
    for para in paras:
        s = para.strip()
        if not s:
            continue
        if any(sig in s for sig in FILLER_SIGS):
            dropped.append(s[:60])
        else:
            kept.append(para)
    kept_body = '\n\n'.join(kept)
    wc_before = len(body.split())
    wc_after = len(kept_body.split())
    # panel year
    ym = re.search(r'Năm:\s*(\d{4})', panel)
    py = ym.group(1) if ym else '?'
    # body year mentions
    body_years = re.findall(r'\b(199[0-9])\b', kept_body)
    from collections import Counter
    yc = Counter(body_years)
    print(f"Ch{n}: wc {wc_before}->{wc_after} (dropped {len(dropped)} paras) | panel_year={py} | body_years={dict(yc)}")
    for d in dropped:
        print(f"     DROP: {d}")
