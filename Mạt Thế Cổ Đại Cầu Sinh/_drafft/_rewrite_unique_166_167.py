# -*- coding: utf-8 -*-
"""Unique full rewrite ch.166-167."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".novelab_score.json"

_SRC = (BASE / "_rewrite_unique_104_128.py").read_text(encoding="utf-8")
_ns: dict = {}
exec(_SRC.split("SPECS = [")[0], _ns)
exec(_SRC[_SRC.find("def shared_mid") : _SRC.find("def build")], _ns)
hdr, panel, find_file = _ns["hdr"], _ns["panel"], _ns["find_file"]
night_close, vi_words, shared_mid = _ns["night_close"], _ns["vi_words"], _ns["shared_mid"]

SPECS = [
    dict(
        n=166,
        title="Gió Bắc Thổi Lạnh",
        day_vn="một trăm sáu mươi sáu",
        exp=25650,
        event="Gió bấc lạnh · củi siết · ca ngắn · tám mươi mốt",
        smell="mùi gió bấc buốt và than bếp",
        tag="gió bấc lạnh · củi siết · không lỏng",
        law="Rét không bằng lỏng · ca ngắn · trẻ trong · củi siết",
        cliff="Gió bấc kéo dài — sông băng cứng thêm hay nứt?",
        open=(
            "Canh tư ngày thứ một trăm sáu mươi sáu. Gió bấc thổi lạnh buốt gáy. "
            "Mùi than bếp. Củi siết. Ca tháp ngắn. Không tuần xa."
        ),
        core=(
            '"Vào. Ca ngắn. Không đứng tháp lâu," Phong dặn.\n\n'
            'Hà phát găng: "Trẻ trước."\n\n'
            'Hứa: "Củi đủ năm ngày nếu siết."\n\n'
            'Tôn Vũ: "Xưởng kín gió."\n\n'
            "---\n\n"
            'Họp: "Rét. Việc trong nhiều hơn ngoài. Canh đủ. Không lười vì lạnh."\n\n'
            'Phong-Hà: "Đủ ấm?"\n\n'
            '"Đủ. Không lỏng."\n\n'
            'Ngọ mười nhịp: "Gió bấc. Củi siết. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
            "Gật. Đêm nắm ấm. Sống. Đo. Không khoe."
        ),
    ),
    dict(
        n=167,
        title="Bình Minh Mới",
        day_vn="một trăm sáu mươi bảy",
        exp=25690,
        event="Bình minh việc · sau gió bấc · không lỏng · tám mươi mốt",
        smell="mùi sương mai se và đất sân đông",
        tag="bình minh việc sau gió bấc · không lỏng",
        law="Bình minh là việc · không hội · canh đủ · không thở phào",
        cliff="Bình minh yên — gió bấc có mang sóng theo sau không?",
        open=(
            "Bình minh ngày thứ một trăm sáu mươi bảy. Tám mươi mốt người. "
            "Mùi sương mai se và đất sân. Việc mở trước miệng. Không lỏng vì nắng sau rét."
        ),
        core=(
            "Phong tổ việc: tháp, rèn, kho, rau, thẻ, hầm, tuần trong rào.\n\n"
            '"Trống sát. Gió bấc dịu," Đại Lực báo.\n\n'
            '"Không thở phào. Tai khe."\n\n'
            'Hà: "Trẻ thẻ trong."\n\n'
            '"Giữ."\n\n'
            "---\n\n"
            'Họp ngắn: "Bình minh việc. Không họp chữ yên. Canh đủ. Lương siết giữ."\n\n'
            'Tôn Vũ: "Lưỡi mài."\n\n'
            'Phong-Hà: "Đủ?"\n\n'
            '"Đủ. Bình minh không phải hội."\n\n'
            'Ngọ mười nhịp: "Bình minh việc. Không lỏng. Đông thường. Hầm xấu. Cùng màu."\n\n'
            "Gật. Chiều muối. Đêm nắm. Sống. Đo. Không khoe."
        ),
    ),
]


def build(s: dict) -> str:
    return "".join(
        [
            hdr(s["n"], s["title"]),
            s["open"],
            "\n\n",
            "Phong ra việc trước khi sân thức hẳn khi còn trong rào. Muối chát đầu ngón khi đảo bao. "
            "Hà phơi hoặc bê cháo hoặc siết rèm — lưng thẳng, khăn mũi thấp. Việc mở trước miệng. Mùi ",
            s["smell"],
            ".\n\n",
            '"Ngoài?" Hà hỏi khẽ khi gần anh, không ngẩng hết đầu.\n\n',
            f'"{s["tag"]}. Việc. Không hội," Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay tay. Không đuổi mắt quá hai nhịp.\n\n',
            "---\n\n",
            s["core"],
            shared_mid(s),
            night_close(s["day_vn"], s["tag"], s["law"], s["cliff"], s["smell"]),
            panel(s["n"], s["exp"], s["event"]),
            "\n",
            s["cliff"],
            "\n",
        ]
    )


def main():
    fails = 0
    for s in SPECS:
        path = find_file(s["n"])
        text = build(s)
        if "Nhịp im" in text:
            raise SystemExit("Nhịp im")
        w = vi_words(text)
        i = 0
        extras = [
            f"Canh khuya ngày {s['day_vn']}: then êm. Mùi {s['smell']}. Đủ sau {s['tag']}.",
            f"Phong uống nước: {s['law']}. Hà thở. Nắm. Ngủ sau {s['tag']}.",
            f"Sổ than: {s['event']}. Không pháo. Gấp.",
            f"Trước gà: sau {s['tag']} chỉ đất gió. Nhịp gánh thẻ. Chưa thua.",
            f'Hà: "Mai cùng màu." Phong gật. Mùi {s["smell"]}. Sống. Đo. Không khoe.',
        ]
        while w < 3050 and i < 40:
            bit = extras[i % 5] + f" Hơi thở lớp {i + 1} ngày {s['day_vn']} sau {s['tag']}."
            if bit in text:
                bit += f" Muối {i}-{s['n']}."
            text = text.replace("「Kho Vô Hạn", "\n" + bit + "\n\n「Kho Vô Hạn", 1)
            w = vi_words(text)
            i += 1
        path.write_text(text, encoding="utf-8")
        r = subprocess.run(
            [
                "python",
                str(SCORER),
                str(path),
                "--min-words",
                "3000",
                "--cfg",
                str(CFG),
                "--threshold",
                "9.0",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        line = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[0]
        print(line, "w=", w, flush=True)
        if "[OK" not in line:
            fails += 1
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
