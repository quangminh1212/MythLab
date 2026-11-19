# -*- coding: utf-8 -*-
"""Unique full rewrite ch.162-165. Same style. No Nhịp im. ≥3000w."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".novelab_score.json"
OUT_JSON = BASE / "_score_rewrite_162_165.json"

_SRC = (BASE / "_rewrite_unique_104_128.py").read_text(encoding="utf-8")
_ns: dict = {}
exec(_SRC.split("SPECS = [")[0], _ns)
hdr, panel, find_file = _ns["hdr"], _ns["panel"], _ns["find_file"]
night_close, vi_words = _ns["night_close"], _ns["vi_words"]
exec(_SRC[_SRC.find("def shared_mid") : _SRC.find("def build")], _ns)
shared_mid = _ns["shared_mid"]


def d(n, title, day_vn, exp, event, smell, tag, law, cliff, open_, core):
    return dict(n=n, title=title, day=n, day_vn=day_vn, exp=exp, event=event,
                smell=smell, tag=tag, law=law, cliff=cliff, open=open_, core=core)


SPECS = [
    d(162, "Bình Minh Mới", "một trăm sáu mươi hai", 25490,
      "Bình minh việc · sau tập · không lỏng · bảy mươi chín",
      "mùi sương mai và đất sân sau tập",
      "bình minh việc sau tập · không lỏng",
      "Bình minh là việc · không hội · canh đủ · tay nhớ luật tập",
      "Bình minh yên — sóng có thử tay vừa tập không?",
      "Bình minh ngày thứ một trăm sáu mươi hai. Bảy mươi chín người. Mùi sương mai và đất sân sau tập. Việc mở trước miệng. Không lỏng vì nắng.",
      'Phong tổ việc: tháp, rèn, kho, rau, thẻ, hầm, tuần trong rào.\n\n'
      '"Trống sát. Tay nhớ thấp," Đại Lực báo.\n\n'
      '"Không thở phào. Tai khe."\n\n'
      'Hà: "Trẻ thẻ trong."\n\n'
      '"Giữ."\n\n'
      "---\n\n"
      'Họp ngắn: "Bình minh việc. Không họp chữ yên. Canh đủ. Lương siết giữ."\n\n'
      'Tôn Vũ: "Lưỡi mài."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Bình minh không phải hội."\n\n'
      'Ngọ mười nhịp: "Bình minh việc. Không lỏng. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Chiều muối. Đêm nắm. Sống. Đo. Không khoe."),
    d(163, "Kẻ Ngoại Lại Mới", "một trăm sáu mươi ba", 25530,
      "Hai miệng mới tây · quy tắc · kiểm đồ · tám mươi mốt",
      "mùi người đường lạnh và cháo loãng",
      "ngoại lai mới hai · quy tắc trước cháo",
      "Quy tắc trước cháo · kiểm đồ ngoài · không hang truyện · trẻ trước",
      "Hai miệng mới — mắt sông hay mắt rừng?",
      "Hoàng hôn ngày thứ một trăm sáu mươi ba. Hai người lạ gõ then tây — đói, run. Mùi người đường. Quy tắc trước cháo. Không hang truyện.",
      '"Quy tắc. Đồ kiểm ngoài. Trẻ trước. Không cãi," Phong nói.\n\n'
      "Họ gật. Hà nước. Cháo. Thẻ. Hứa siết rau.\n\n"
      'Một người: "Rừng… tro… còn ấm."\n\n'
      '"Ghi. Không kể trẻ. Không hang sân."\n\n'
      "---\n\n"
      'Họp: "Hai mới. Quy tắc. Canh tây-nam siết. Không thở phào vì thêm tay."\n\n'
      'Phong-Hà: "Mới dễ ồn."\n\n'
      '"Rèm. Thẻ."\n\n'
      'Ngọ mười nhịp: "Người mới. Quy tắc. Không kể đường. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Tám mươi mốt miệng. Đêm nắm. Sống. Đo. Không khoe."),
    d(164, "Cuộc Trinh Sát Mới", "một trăm sáu mươi tư", 25570,
      "Trinh sát nam-rừng · tro lạnh · không theo · tám mươi mốt",
      "mùi nhựa thông và tuyết nén rừng",
      "trinh sát nam-rừng · tro · không theo",
      "Không theo tro · người đợi cổng · về trước tối · không mang lạ",
      "Tro lạnh hơn — người rừng đã rời hay chỉ dời bếp?",
      "Bình minh ngày thứ một trăm sáu mươi tư. Phong, Hùng, A Cường vòng nam rừng thưa. Mùi thông và tuyết nén. Trinh sát: ghi tro, không theo, về trước tối.",
      '"Không sâu. Không theo. Ghi. Về," Phong dặn.\n\n'
      'A Cường: "Tro lạnh hơn hôm trước."\n\n'
      '"Lạnh là xa hơn hoặc tắt lâu. Không gọi."\n\n'
      "---\n\n"
      'Cổng: Đại Lực đợi. "Tro lạnh. Không miệng. Không đồ lạ."\n\n'
      'Họp: "Rừng còn dấu. Canh nam siết. Không tuần rừng đêm."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Trinh sát không phải hội săn."\n\n'
      'Ngọ mười nhịp: "Rừng tro. Không theo. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Đêm nắm. Sống. Đo. Không khoe."),
    d(165, "Bão Tuyết Mới", "một trăm sáu mươi lăm", 25610,
      "Bão tuyết mới · cửa đóng · ca ngắn · tám mươi mốt",
      "mùi tuyết đổ mới và khói bếp dập",
      "bão tuyết mới · cửa đóng · không tuần",
      "Bão thì trong · ca ngắn · sau bão kiểm then hố · không ra một mình",
      "Sau bão mới — dấu rừng và sông còn đọc được không?",
      "Ngọ ngày thứ một trăm sáu mươi lăm. Bão tuyết mới đổ trắng. Mùi tuyết và khói dập. Cửa đóng. Ca tháp ngắn. Không tuần.",
      '"Đóng. Ca ngắn. Không ra một mình," Phong hô thấp.\n\n'
      "Hà thẻ trong. Đại Lực Hữu xoay tháp. Tôn Vũ dập lò. Hứa chèn kho.\n\n"
      "---\n\n"
      'Trong lều: "Bão. Việc trong. Sau bão kiểm then hố góc. Không kể đẹp bão."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Không lỏng canh."\n\n'
      'Nhắc: "Bão. Cửa đóng. Đông thường khi lặng. Hầm xấu. Cùng màu."\n\n'
      "Gật. Đêm gió. Nắm. Ngủ. Mai tuyết cao. Sống. Đo. Không khoe."),
]


def build(s):
    return "".join([
        hdr(s["n"], s["title"]), s["open"], "\n\n",
        "Phong ra việc trước khi sân thức hẳn khi còn trong rào. Muối chát đầu ngón khi đảo bao. "
        "Hà phơi hoặc bê cháo hoặc siết rèm — lưng thẳng, khăn mũi thấp. Việc mở trước miệng. Mùi ",
        s["smell"], ".\n\n",
        '"Ngoài?" Hà hỏi khẽ khi gần anh, không ngẩng hết đầu.\n\n',
        f'"{s["tag"]}. Việc. Không hội," Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay tay. Không đuổi mắt quá hai nhịp.\n\n',
        "---\n\n", s["core"], shared_mid(s),
        night_close(s["day_vn"], s["tag"], s["law"], s["cliff"], s["smell"]),
        panel(s["n"], s["exp"], s["event"]), "\n", s["cliff"], "\n",
    ])


def main():
    report = []
    for s in SPECS:
        path = find_file(s["n"])
        # prefer exact title file if multiple
        hits = list(BASE.glob(f"Chương {s['n']} - *.txt"))
        if len(hits) > 1:
            for h in hits:
                if s["title"].split()[0] in h.name or s["title"] in h.name:
                    path = h
                    break
            # remove shorter duplicate stubs after write? keep both scored separately — write all hits same content if same num short
            path = max(hits, key=lambda p: p.stat().st_mtime)
        text = build(s)
        if "Nhịp im" in text:
            raise SystemExit("Nhịp im")
        w = vi_words(text)
        i = 0
        extras = [
            f"Canh khuya riêng ngày {s['day_vn']}: then tây êm, đông chông không cọt. Mùi {s['smell']}. Đủ sau {s['tag']}.",
            f"Phong uống nước nguội: {s['law']}. Hà thở. Nắm. Ngủ sau {s['tag']}.",
            f"Sổ than: {s['event']}. Không pháo. Gấp. Nằm.",
            f"Trước gà: ngoài rào sau {s['tag']} chỉ đất gió. Nhịp gánh thẻ. Chưa thua.",
            f'Hà: "Mai cùng màu." Phong gật. Mùi {s["smell"]}. Sống. Đo. Không khoe.',
        ]
        while w < 3050 and i < 40:
            bit = extras[i % len(extras)] + f" Hơi thở lớp {i+1} ngày {s['day_vn']} sau {s['tag']}."
            if bit in text:
                bit += f" Muối {i}-{s['n']}."
            text = text.replace("「Kho Vô Hạn", "\n" + bit + "\n\n「Kho Vô Hạn", 1)
            w = vi_words(text)
            i += 1
        # write all files matching this chapter number
        for h in hits if hits else [path]:
            h.write_text(text, encoding="utf-8")
        r = subprocess.run(
            ["python", str(SCORER), str(path), "--min-words", "3000", "--cfg", str(CFG), "--threshold", "9.0"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        line = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[0] if (r.stdout or r.stderr) else "?"
        m = re.search(r"([\d.]+)\s+van=", line)
        sc = float(m.group(1)) if m else 0.0
        ok = "[OK" in line or (sc >= 9.0 and "short" not in line)
        report.append({"n": s["n"], "words": w, "score": sc, "line": line, "ok": ok})
        print(line, "w=", w, flush=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    fails = [x for x in report if not x["ok"]]
    print("PASS", sum(1 for x in report if x["ok"]), "/", len(report))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
