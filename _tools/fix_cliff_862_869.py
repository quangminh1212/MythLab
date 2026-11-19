# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(r"C:\Dev\MythLab\Mạt Thế Cổ Đại Cầu Sinh")

EXTRA = {
    862: " Mai bóng gò hay sóng mương — chưa biết.",
    863: " Mai miệng dây hay thước bụi — chưa biết.",
    864: " Mai yên giả sau dây hay sóng thấp — chưa biết.",
    865: " Mai bốn thấp lại hay hỏi mồi — chưa biết.",
    866: " Mai thước gõ hay miệng muối — chưa biết.",
    867: " Mai vỏ ốc mồi hay sóng đá — chưa biết.",
    868: " Mai yên giả sau muối hay bóng gò — chưa biết.",
    869: " Mai năm thấp lại hay hỏi cùng màu — chưa biết.",
}

BASE = (
    "Trống điểm kế mang sóng, bóng, hỏi hay yên giả. Chưa biết. Chưa mừng. "
    "Ngày mai máy nghèo. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm."
)

for n in range(862, 870):
    p = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
    t = p.read_text(encoding="utf-8")
    m = re.search(r"\n「Kho Vô Hạn", t)
    if not m:
        raise SystemExit(f"no panel {n}")
    head = t[: m.start()].rstrip()
    tail = t[m.start() :]
    # drop weak last line if present
    head = re.sub(
        r"\nPhong hít ngắn lần cuối\. Hà thở\. Gió bấc lạnh gáy\. Tiếng then êm một nhịp thật\. Đủ\.\s*$",
        "",
        head,
    )
    cliff = BASE + EXTRA[n]
    new = head + "\n\n" + cliff + "\n\n" + tail
    if re.search(r"Nhịp im\s*\d+", new):
        raise SystemExit(f"Nhịp im in {n}")
    p.write_text(new, encoding="utf-8")
    print(f"ch.{n} words={len(new.split())}")
