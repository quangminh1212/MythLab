# Surgical fix: drop appended machine-filler paragraphs, keep original panel untouched.
import glob, re
from pathlib import Path

fails = [158,162,163,166,167,168,169,171,172,173,174,175,177,179]

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
    "Hùng cảm thấy bình yên. Ông nhai chậm",
    "Hai người đọc cùng nhau",
    "Hùng mở cửa sổ, đón ánh nắng sớm",
    "Mùi hoa sữa thoang thoảng",
    "[ch.177 CHARFIX]",
    "Hùng siết hàm ch.",
    "Hùng nhíu mày, siết tay",
    "Trên bàn làm việc, sổ sách chất cao",
    "xoa bóp vai anh",
    "Buổi chiều, Hùng ngồi ngoài hiên nhà, nhìn ra đường phố",
    "tay chạm tay Lan",
    "Mưa rơi trên mái ngói",
    "nắm tay nhau, im lặng, bình yên",
    "Ngồi ngoài hiên nhà, nhìn ra đường phố",
    "Họ nắm tay nhau",
    "mỏ mệt nhưng lòng nhẹ",
]

for n in fails:
    p = glob.glob(f'Chương {n} - *.txt')[0]
    t = Path(p).read_text(encoding='utf-8')
    pi = t.rfind('「Hệ thống')
    if pi < 0:
        print(f"Ch{n}: NO PANEL FOUND - SKIP")
        continue
    body = t[:pi]
    panel = t[pi:]  # untouched, preserves exact Unicode
    paras = re.split(r'\n\s*\n', body)
    kept, dropped = [], 0
    for para in paras:
        s = para.strip()
        if not s:
            continue
        if any(sig in s for sig in FILLER_SIGS):
            dropped += 1
        else:
            kept.append(para.rstrip())
    kept_body = '\n\n'.join(kept)
    wc = len(kept_body.split())
    if wc < 3000:
        print(f"Ch{n}: WOULD DROP BELOW 3000 ({wc}w) - SKIP, needs manual")
        continue
    new = kept_body.rstrip() + '\n\n' + panel.lstrip()
    Path(p).write_text(new, encoding='utf-8')
    print(f"Ch{n}: dropped {dropped} filler paras, body {wc}w -> WROTE")

print("=== DONE ===")
