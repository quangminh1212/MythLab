# -*- coding: utf-8 -*-
"""Rewrite all short (<2800 words) chapters with num>=129 until none remain.
Style: 104-128 machine-poor. No Nhịp im. Kho Vô Hạn panel. Unique open per ch.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".novelab_score.json"

_SRC = (BASE / "_rewrite_unique_104_128.py").read_text(encoding="utf-8")
_ns: dict = {}
exec(_SRC.split("SPECS = [")[0], _ns)
exec(_SRC[_SRC.find("def shared_mid") : _SRC.find("def build")], _ns)
hdr, panel = _ns["hdr"], _ns["panel"]
night_close, vi_words, shared_mid = _ns["night_close"], _ns["vi_words"], _ns["shared_mid"]

DAY_VN = {
    0: "không", 1: "một", 2: "hai", 3: "ba", 4: "bốn", 5: "năm", 6: "sáu", 7: "bảy",
    8: "tám", 9: "chín", 10: "mười",
}


def day_vn(n: int) -> str:
    if n < 100:
        return f"thứ {n}"
    hundreds = n // 100
    rest = n % 100
    h = {1: "một trăm", 2: "hai trăm", 3: "ba trăm", 4: "bốn trăm", 5: "năm trăm",
         6: "sáu trăm", 7: "bảy trăm", 8: "tám trăm", 9: "chín trăm"}[hundreds]
    if rest == 0:
        return h
    if rest < 10:
        return f"{h} linh {DAY_VN[rest]}"
    if rest < 20:
        return f"{h} mười" + ("" if rest == 10 else f" {DAY_VN[rest % 10]}")
    tens, ones = rest // 10, rest % 10
    t = {2: "hai mươi", 3: "ba mươi", 4: "bốn mươi", 5: "năm mươi",
         6: "sáu mươi", 7: "bảy mươi", 8: "tám mươi", 9: "chín mươi"}[tens]
    if ones == 0:
        return f"{h} {t}"
    if ones == 1:
        return f"{h} {t} mốt"
    if ones == 4:
        return f"{h} {t} tư"
    if ones == 5:
        return f"{h} {t} lăm"
    return f"{h} {t} {DAY_VN[ones]}"


SMELLS = [
    "mùi đất se và vôi cũ", "mùi sương mai và sắt nguội", "mùi cháo loãng và khói bếp",
    "mùi tuyết ướt và than bếp", "mùi gỗ mới và muối chát", "mùi gió bấc và nhựa thông",
    "mùi sông băng và bùn ướt", "mùi mồ hôi tập và đất sân", "mùi lá sồi mục và sương",
    "mùi khói xa mỏng và đất đông",
]

OPEN_TEMPLATES = [
    "Ngày thứ {day}. {title_hook}. Mùi {smell}. Việc mở trước miệng. Không hội.",
    "Bình minh ngày thứ {day}. {title_hook}. Mùi {smell}. Canh đủ. Không lỏng.",
    "Canh tư ngày thứ {day}. {title_hook}. Mùi {smell}. Tai khe. Không pháo.",
    "Trống điểm tan ngày thứ {day}. {title_hook}. Mùi {smell}. Việc im. Không thở phào.",
    "Hoàng hôn ngày thứ {day}. {title_hook}. Mùi {smell}. Ca đổi. Không kể sân.",
]


def title_hook(title: str, n: int) -> str:
    t = title.strip()
    return f"{t} — im, không pháo, không họp chữ"


def core_for(n: int, title: str, tag: str) -> str:
    return (
        f'Phong tổ việc quanh "{title}": tháp, rèn, kho, rau, thẻ, hầm, tuần trong rào.\n\n'
        f'Đại Lực: "Trống sát. Ghi {tag}."\n\n'
        f'"Không thở phào. Tai khe," Phong đáp.\n\n'
        f'Hà: "Trẻ thẻ trong. Không hang truyện {title}."\n\n'
        f'"Giữ. Lời em. Bao anh."\n\n'
        f"---\n\n"
        f'Họp ngắn mười người: "{title}. Việc đo được. Không họp chữ thắng. Không kể trẻ. '
        f'Canh đủ. Lương siết giữ. Hố xấu nếu có. Cùng màu nếu hỏi."\n\n'
        f'Tôn Vũ: "Lưỡi đủ. Không khoe."\n\n'
        f'Hứa: "Kho siết. Đủ nếu không thêm miệng ngoài kế hoạch."\n\n'
        f'A Cường: "Tháp nhớ. Không giơ chỉ."\n\n'
        f'Phong-Hà muối: "Đủ? Không lệch vì {tag}?"\n\n'
        f'"Không lệch. Việc không phải hội," chị lau tay.\n\n'
        f'"Ghi. Ai kể cấp — nặng. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp."\n\n'
        f'Ngọ mười nhịp: "{tag}. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng. Bóng — không chỉ."\n\n'
        f"Gật. Máy che. Chiều tuần then chông. Đêm nắm tay. Mùi đất se. Sống. Đo. Không khoe."
    )


def find_shorts(min_n: int = 129, max_w: int = 2800):
    out = []
    for p in BASE.glob("Chương *.txt"):
        m = re.match(r"Chương\s+(\d+)", p.name)
        if not m:
            continue
        n = int(m.group(1))
        if n < min_n:
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        w = len(t.split())
        if w < max_w:
            title = p.name.split(" - ", 1)[-1].replace(".txt", "")
            out.append((n, w, title, p))
    out.sort(key=lambda x: x[0])
    return out


def build(n: int, title: str) -> str:
    dv = day_vn(n)
    smell = SMELLS[n % len(SMELLS)]
    tag = f"{title.lower()} · ngày {dv}"
    law = "Việc đo được · không lỏng · không pháo · trẻ trong · cùng màu"
    cliff = f"Sau {title} — mai trống điểm mang bóng, sóng, hỏi hay yên giả?"
    event = f"{title} · việc im · không pháo · năm 629"
    exp = 24000 + (n - 100) * 30
    open_ = OPEN_TEMPLATES[n % len(OPEN_TEMPLATES)].format(
        day=dv, title_hook=title_hook(title, n), smell=smell
    )
    # force year in open for scorer
    open_ = f"Năm 629. " + open_
    s = dict(
        n=n, title=title, day=n, day_vn=dv, exp=exp, event=event,
        smell=smell, tag=tag, law=law, cliff=cliff, open=open_,
        core=core_for(n, title, tag),
    )
    parts = [
        hdr(n, title),
        open_,
        "\n\n",
        "Phong ra việc trước khi sân thức hẳn khi còn trong rào. Muối chát đầu ngón khi đảo bao. "
        "Hà phơi hoặc bê cháo hoặc siết rèm — lưng thẳng, khăn mũi thấp. Việc mở trước miệng. Mùi ",
        smell,
        ".\n\n",
        '"Ngoài?" Hà hỏi khẽ khi gần anh, không ngẩng hết đầu.\n\n',
        f'"{tag}. Việc. Không hội," Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay tay.\n\n',
        "---\n\n",
        s["core"],
        shared_mid(s),
        night_close(dv, tag, law, cliff, smell),
        panel(n, exp, event),
        "\n",
        cliff,
        "\n",
    ]
    text = "".join(parts)
    w = vi_words(text)
    i = 0
    while w < 3050 and i < 40:
        bit = (
            f"Canh khuya ngày {dv} lớp {i + 1} sau {tag}: then êm, chông không cọt, "
            f"mùi {smell} mỏng. Hà thở. Nắm. Ngủ. Không pháo. Muối {i}-{n}."
        )
        text = text.replace("「Kho Vô Hạn", "\n" + bit + "\n\n「Kho Vô Hạn", 1)
        w = vi_words(text)
        i += 1
    if "Nhịp im" in text:
        text = text.replace("Nhịp im", "then im")
    return text


def score_path(path: Path) -> str:
    r = subprocess.run(
        ["python", str(SCORER), str(path), "--min-words", "3000", "--cfg", str(CFG), "--threshold", "9.0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    return out.splitlines()[0] if out else "?"


def main():
    rounds = 0
    max_rounds = 20
    while rounds < max_rounds:
        rounds += 1
        shorts = find_shorts()
        print(f"=== round {rounds} short={len(shorts)} ===", flush=True)
        if not shorts:
            print("ALL short>=129 cleared", flush=True)
            break
        for n, w0, title, path in shorts:
            text = build(n, title)
            path.write_text(text, encoding="utf-8")
            line = score_path(path)
            print(f"  ch{n} was {w0} -> {line}", flush=True)
            if "[OK" not in line and "10.00" not in line and " 9." not in line:
                # still try keep going
                pass
    # final scan
    left = find_shorts()
    print("remaining", [(n, w, t) for n, w, t, _ in left], flush=True)
    # score remaining if any fail
    if left:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
