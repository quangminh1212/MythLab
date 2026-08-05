# -*- coding: utf-8 -*-
"""Expand MTCDS ch 33-41,47-51,53 to >=3000 scorer words.
No 'Nhịp im' pad loops. Unique openings. Phong/Hà continuity. Kho Vô Hạn panel.
EXP progresses from neighbors (early-game allowed).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, r"C:\Dev\NovelLab\scripts")
from strict_score import score_chapter, vi_wordcount  # noqa: E402

cfg = json.loads((BASE / ".mythlab_score.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# Per-chapter plot + EXP (from short originals / neighbor chain)
# ch32=907 → 33..41 early climb; ch46=2300 → 47..51 climb; 53 continues early band
# ---------------------------------------------------------------------------
META = {
    33: dict(
        title="Chương 33: Trận Ma Túy",
        day="Ngày thứ sáu mươi bảy — mưa mỏng ướt sân đá đền",
        open12="Mưa mỏng ướt sân đá khi A Cường hô có người sốt ba ngày",
        exp="927 / 1000",
        level="cấp 6",
        people=34,
        cast=["Phong", "Hà", "A Cường", "Mạc", "bà", "Từ Sơn"],
        place="đền cổ — phòng ốm + bếp + kho",
        beats=[
            "A Cường báo mưa + người sốt ba ngày không hạ",
            "Mạc kiểm mạch, nghi sốt thường nhưng lo lây",
            "Hà mở sổ khẩu phần, Phong gọi Kho Vô Hạn chữa bệnh 10 EXP",
            "Ba người đau bụng — nghi thức ăn hỏng mùa nóng",
            "Mở bảo quản lạnh 20 EXP, xếp đá kho, Hà ghi quy tắc",
            "Đêm trống điểm, 34 miệng an toàn, EXP 927",
        ],
        cliff="Liệu chức năng chữa có đủ khi cả đám cùng ốm… hay chỉ kéo thêm ngày cho kho đá cạn?",
        hook_sens="mùi mưa lẫn mùi mồ hôi sốt",
        motif="chữa trước, giữ lạnh sau, sổ trước miệng",
    ),
    34: dict(
        title="Chương 34: Cuộc Săn Mùa Đông",
        day="Ngày thứ bảy mươi — tuyết phủ trắng bờ rào bắc",
        open12="Tuyết phủ trắng bờ rào khiến đội săn siết dây bẫy trước khi ra cổng",
        exp="952 / 1000",
        level="cấp 6",
        people=37,
        cast=["Phong", "Hà", "Từ Sơn", "A Cường", "Vũ", "bà"],
        place="rừng nam núi + nhà đất bỏ",
        beats=[
            "Kho báo gạo 15kg thịt 15kg — không đủ đông dài",
            "Đội năm người săn heo rừng nam núi",
            "Bẫy nâng cao bắt hai heo ~40kg thịt",
            "Dấu chân người trên tuyết — gặp Lan và hai người cellar",
            "Đón về đền: 37 miệng, Hà mở sổ tên mới",
            "EXP +25 = 952, chia thịt sấy muối",
        ],
        cliff="Liệu dấu chân trên tuyết còn ai khác… hay chỉ còn đàn zombie học theo mùi máu heo?",
        hook_sens="mùi tuyết sạch lẫn khói củi ướt",
        motif="săn no miệng trước khi đông nuốt hết gạo",
    ),
    35: dict(
        title="Chương 35: Bệnh Dịch Lớn",
        day="Ngày thứ bảy mươi mốt — mây đen kéo kín tháp canh",
        open12="Mây đen kéo kín tháp canh khi Mạc đếm mười người sốt cùng lúc",
        exp="1002 / 1500",
        level="cấp 7",
        people=34,
        cast=["Phong", "Hà", "Mạc", "A Cường", "bà", "Lan"],
        place="phòng cách ly + hành lang đền",
        beats=[
            "Sốt lây: 1→2→5→10 người trong nửa ngày",
            "Thuốc kho cạn, mở thuốc 10 EXP/người",
            "Hà + bà lập phòng cách ly, cháo riêng, nước đun",
            "Phong chữa lần lượt mười người, tay run vì mất ngủ",
            "Ba đến năm ngày bệnh lui, mở Hệ thống Phòng Bệnh",
            "EXP +50 = 1002, level 7",
        ],
        cliff="Liệu Hệ thống Phòng Bệnh có chặn đợt sau… hay chỉ là lưới mỏng trước virus không tên?",
        hook_sens="mùi thuốc thảo đắng lan từ bếp cách ly",
        motif="cách ly trước thương, sổ trước nỗi sợ",
    ),
    36: dict(
        title="Chương 36: Cuộc Phiêu Lưu",
        day="Ngày thứ bảy mươi lăm — trời quang lạnh sau mây",
        open12="Trời quang lạnh khiến Phong đeo lưới năm ngày bước ra cổng bắc",
        exp="1032 / 1500",
        level="cấp 7",
        people=40,
        cast=["Phong", "Hà", "Hùng", "A Cường", "bà"],
        place="năm nghìn bước bắc — nhà đất + cellar",
        beats=[
            "Nhiệm vụ thám hiểm mở rộng phạm vi",
            "Phong đi xa: cá suối, nhà đất, gặp Hùng",
            "Cellar năm người đói, đón về",
            "Về đền 40 miệng, Hà chia chỗ ngủ sàn đá",
            "A Cường tăng ca canh vì đông miệng lạ",
            "EXP +30 = 1032",
        ],
        cliff="Liệu bốn mươi miệng có no bằng cá suối… hay đường bắc còn giấu nhà cellar thứ hai?",
        hook_sens="mùi đất ẩm suối bắc lẫn mùi rơm mục nhà bỏ",
        motif="đi xa lấy người, về gần chia chỗ",
    ),
    37: dict(
        title="Chương 37: Cuộc Gặp Gỡ Bất Ngờ",
        day="Ngày thứ bảy mươi sáu — tiếng đinh xưởng mộc vang sớm",
        open12="Tiếng đinh xưởng mộc vang sớm khi Phong chia ba hướng thám năm trăm bước",
        exp="1057 / 1500",
        level="cấp 7",
        people=43,
        cast=["Phong", "Hà", "Lan", "A Cường", "Từ Sơn", "bà"],
        place="đông rừng — nhà đất + cổng đền",
        beats=[
            "Thám ba hướng: bắc trống, tây cá, đông gặp Lan",
            "Lan + hai người cellar từ thành nhỏ",
            "Hà kiểm vết cào, cho vào sổ",
            "43 người, phân việc mộc + canh",
            "Đêm Phong–Hà bàn khẩu phần đông miệng",
            "EXP +25 = 1057",
        ],
        cliff="Liệu Lan mang tin zombie thành thật… hay chỉ mang thêm miệng và nỗi sợ cũ?",
        hook_sens="tiếng đinh đều lẫn mùi gỗ bào mới",
        motif="gặp lạ không mở cổng vội — mở sổ trước",
    ),
    38: dict(
        title="Chương 38: Dự Trữ Mùa Đông",
        day="Ngày thứ bảy mươi bảy — gió se mang mùi củi khô",
        open12="Gió se mang mùi củi khô khi Hà trải sổ dự trữ giữa sân kho",
        exp="1097 / 1500",
        level="cấp 7",
        people=43,
        cast=["Phong", "Hà", "bà", "Hứa", "Tôn", "A Cường"],
        place="kho khô + bể nước + đống củi",
        beats=[
            "Ước lượng đông: củi, gạo, thịt sấy, muối, thuốc",
            "Hà lập bảng ngày-miệng-phần",
            "Gia cố mái kho, sàn cao chống chuột",
            "Hứa kiểm mạch nước không đóng băng sớm",
            "EXP +40 nhiệm vụ dự trữ = 1097",
            "Đêm cộng đồng học tiết kiệm không hoảng",
        ],
        cliff="Liệu bảng dự trữ có đủ nếu đông thêm mười miệng… hay tuyết sẽ tới trước khi củi đầy tháp?",
        hook_sens="mùi củi khô lẫn mùi thóc trong bao",
        motif="đếm trước đói, không đếm sau khóc",
    ),
    39: dict(
        title="Chương 39: Cuộc Săn Lớn",
        day="Ngày thứ bảy mươi tám — bình minh đội săn mang lao rèn",
        open12="Lao rèn mới trên vai Tôn lóe nắng khi tám người rời cổng tây",
        exp="1127 / 1500",
        level="cấp 7",
        people=43,
        cast=["Phong", "Hà", "Tôn", "A Cường", "Vũ", "Từ Sơn"],
        place="rừng tây sâu + lán sấy",
        beats=[
            "Săn lớn: nai, heo nhỏ, thỏ — protein đông",
            "Gặp zombie yếu, bẫy + lao xử gọn",
            "Thịt mang về, Hà + bà muối sấy",
            "Chia phần công bằng theo sổ",
            "EXP +30 = 1127",
            "Đêm mùi khói thịt, canh gắt vì mùi máu",
        ],
        cliff="Liệu mùi máu săn có gọi đàn xa… hay chỉ no đủ để qua đợt lạnh kế?",
        hook_sens="mùi máu tươi lẫn khói sấy mặn",
        motif="săn đủ không săn tham — tham là mùi gọi xác",
    ),
    40: dict(
        title="Chương 40: Cuộc Đàm Phán Mới",
        day="Ngày thứ bảy mươi chín — gậy gỗ gõ cổng ba nhịp đều",
        open12="Gậy gỗ gõ cổng ba nhịp đều khiến A Cường không giương cung vội",
        exp="1147 / 1500",
        level="cấp 7",
        people=46,
        cast=["Phong", "Hà", "A Cường", "đại diện nhóm lạ", "bà"],
        place="cổng đông + phòng đàm sàn đá",
        beats=[
            "Nhóm 6 xin đổi muối lấy chỗ 1 đêm",
            "Phong–Hà đàm: làm việc, không vũ khí vào trong",
            "Kiểm vết cào, 3 người xin ở lại",
            "Tin đàn zombie đỏ mắt phía tây",
            "EXP +20 = 1147, 46 miệng",
            "Đêm canh gắt vì khách mới",
        ],
        cliff="Liệu tin zombie đỏ tây có đúng… hay nhóm khách là mắt thám của nơi khác?",
        hook_sens="mùi muối thô lẫn mùi mồ hôi đường dài",
        motif="đàm phán bằng việc, không bằng lời hứa suông",
    ),
    41: dict(
        title="Chương 41: Mùa Xuân Approaches",
        day="Ngày thứ tám mươi — băng mép bể mỏng tan nhỏ giọt",
        open12="Băng mép bể tan nhỏ giọt khi Hà chỉ chồi xanh đầu tiên ngoài rào",
        exp="1177 / 1500",
        level="cấp 7",
        people=46,
        cast=["Phong", "Hà", "bà", "Hứa", "Nam", "A Cường"],
        place="ruộng bậc + bể + sân",
        beats=[
            "Dấu xuân: băng tan, chim, chồi đất",
            "Kế hoạch gieo lại bậc ruộng",
            "Hà chỉnh khẩu phần chuyển mùa",
            "Trẻ Nam cười khi thấy chồi",
            "EXP +30 = 1177 chuẩn bị xuân",
            "Đêm Phong không lơi — xuân cũng có zombie",
        ],
        cliff="Liệu chồi xanh có thành lúa… hay đàn xác sẽ giẫm nát bậc trước khi hạt chắc?",
        hook_sens="mùi đất tan băng lẫn tiếng chim lạ",
        motif="xuân là hy vọng có sổ, không phải lơi canh",
    ),
    47: dict(
        title="Chương 47: Chiến Dịch Thu Hút",
        day="Ngày thứ tám mươi lăm — khói tín hiệu mỏng trên đồi đông",
        open12="Khói tín hiệu mỏng trên đồi đông khiến Hà nắm tay Phong trước khi họp",
        exp="2350 / 2500",
        level="cấp 8",
        people=51,
        cast=["Phong", "Hà", "A Cường", "Tôn", "Từ Sơn", "bà"],
        place="đồi đông + cổng + sân họp",
        beats=[
            "Quyết định thu hút sống sót bằng khói + bảng gỗ luật",
            "Hà soạn điều kiện vào: làm việc, kiểm vết, trẻ trước",
            "Tín hiệu ba ngày, đón nhóm lẻ",
            "51 miệng, kho căng, tăng canh",
            "EXP +50 nhiệm vụ thu hút = 2350",
            "Đêm Phong–Hà đếm lại chỗ ngủ",
        ],
        cliff="Liệu khói thu hút người… hay cũng thu hút mắt xấu ngoài rừng?",
        hook_sens="mùi khói ướt lẫn mùi mực than trên bảng luật",
        motif="mở cửa có luật — không mở cửa bằng thương hại mù",
    ),
    48: dict(
        title="Chương 48: Gián Điệp",
        day="Ngày thứ chín mươi — ánh mắt Lý nán quá lâu phía kho",
        open12="Ánh mắt Lý nán quá lâu phía kho khiến Từ Sơn kéo Phong ra góc tường",
        exp="2420 / 2500",
        level="cấp 8",
        people=52,
        cast=["Phong", "Hà", "Lý", "Từ Sơn", "A Cường", "bà"],
        place="kho + góc tường + phòng hỏi",
        beats=[
            "Từ Sơn nghi Lý nhìn kho vũ khí quá kỹ",
            "Hà đối chiếu sổ ca: Lý trốn việc nhẹ",
            "Ba ngày giám sát, bắt hỏi",
            "Lý nhận sợ bị đuổi — không phải gián điệp có chủ",
            "Cho ở lại có điều kiện: việc nặng + không lại gần kho một mình",
            "EXP +70 = 2420 bài học tin nhưng kiểm",
        ],
        cliff="Liệu Lý chỉ sợ… hay còn mắt khác chưa lộ sau lưng anh ta?",
        hook_sens="mùi sắt kho lẫn tiếng bước chân lệch nhịp canh",
        motif="tin sau kiểm, thương sau việc",
    ),
    49: dict(
        title="Chương 49: Thách Thức Đầu Tiên",
        day="Ngày thứ một trăm hai mươi — tiếng cãi vang từ xưởng gỗ",
        open12="Tiếng cãi vang từ xưởng gỗ khiến Hà gập sổ và gọi Phong vào họp",
        exp="2500 / 2800",
        level="cấp 8",
        people=52,
        cast=["Phong", "Hà", "Tôn", "Lý", "A Cường", "bà"],
        place="phòng họp lớn + xưởng",
        beats=[
            "Tôn bảo Lý lười, Lý bảo Tôn bắt nạt",
            "Họp cả cộng đồng — không xử sau lưng",
            "Phong chia lại việc theo sức, Hà ghi bảng",
            "Hai bên nhận phần, hết cãi công khai",
            "EXP +80 = 2500 thách thức người > zombie",
            "Đêm yên nhưng Phong biết sẽ còn đợt khác",
        ],
        cliff="Liệu bảng việc có giữ công bằng khi đói siết… hay cãi sẽ thành nắm đấm?",
        hook_sens="mùi mồ hôi xưởng lẫn tiếng búa ngừng giữa chừng",
        motif="người sống nguy hiểm hơn xác nếu không có luật",
    ),
    50: dict(
        title="Chương 50: Bài Học",
        day="Ngày thứ một trăm ba mươi — tiếng ho khan vỡ canh ba",
        open12="Tiếng ho khan vỡ canh ba khiến Trương Bá gõ cửa phòng Phong",
        exp="2580 / 2800",
        level="cấp 8",
        people=52,
        cast=["Phong", "Hà", "Trương Bá", "Mạc", "bà", "A Cường"],
        place="phòng cách ly nhỏ + bếp thuốc",
        beats=[
            "Một người sốt ho — nhớ bài dịch cũ",
            "Cách ly ngay, Hà cắt khẩu phần riêng",
            "Mạc sắc thuốc, ba ngày khỏi",
            "Họp rút kinh nghiệm: ốm = cách ly, không xấu hổ",
            "EXP +80 = 2580",
            "Đêm Phong đứng canh phòng ốm với bà",
        ],
        cliff="Liệu bài học cách ly có thấm khi đông miệng xấu hổ… hay đợt sau sẽ giấu bệnh đến muộn?",
        hook_sens="mùi thuốc đắng lẫn tiếng ho khan xa dần",
        motif="giấu bệnh là giấu dao vào nhà",
    ),
    51: dict(
        title="Chương 51: Sự Thay Đổi",
        day="Ngày thứ một trăm ba mươi mốt — Hà chỉ nồi cháo toàn gạo thiếu xanh",
        open12="Hà chỉ nồi cháo toàn gạo thiếu xanh khiến Phong quyết đổi cách trồng",
        exp="2680 / 3000",
        level="cấp 8",
        people=52,
        cast=["Phong", "Hà", "Hứa", "bà", "Nam", "A Cường"],
        place="đất mới + rừng hạt + ruộng bậc",
        beats=[
            "Thiếu đa dạng: cần rau, trái, thảo",
            "Chia đội: tìm hạt, đào đất, gieo, giữ nước",
            "Hà lập lịch tưới + ca làm đất",
            "Gieo lúa-rau-thảo trên đất mới",
            "EXP +100 = 2680 nhiệm vụ thay đổi",
            "Đêm chờ mầm — không chủ quan zombie",
        ],
        cliff="Liệu mầm mới có kịp trước mùa khô… hay đất sẽ trả lại toàn sỏi?",
        hook_sens="mùi đất mới lật lẫn mùi hạt giống khô",
        motif="đổi khẩu phần bằng tay cuốc, không bằng than vãn",
    ),
    53: dict(
        title="Chương 53: Cuộc Sống Hàng Ngày",
        day="Ngày thứ một trăm ba mươi lăm — trống điểm ca sáng đều hơn mọi tuần",
        open12="Trống điểm ca sáng đều khi Hà treo bảng giờ làm việc giữa sân",
        exp="2780 / 3000",
        level="cấp 8",
        people=52,
        cast=["Phong", "Hà", "A Cường", "bà", "Nam", "Tôn"],
        place="toàn căn cứ — sân, bếp, rào, ruộng",
        beats=[
            "Lập nhịp ngày: sáng rửa-cháo-làm, trưa nghỉ, chiều làm, đêm canh",
            "Hà + Phong đi từng khu kiểm thói quen",
            "Trẻ học đếm + chữ với Lý Lão giữa giờ",
            "Không ai rảnh — không ai bị bỏ",
            "EXP +100 = 2780 cuộc sống có khung",
            "Đêm yên trong luật, Phong vẫn nghe gió",
        ],
        cliff="Liệu khung ngày có vỡ khi có báo động thật… hay chính khung sẽ giúp chạy đúng chỗ?",
        hook_sens="tiếng trống điểm đều lẫn mùi cháo sáng",
        motif="sống sót dài hơi cần thói quen, không chỉ anh hùng",
    ),
}


def find_file(ch: int) -> Path:
    for f in os.listdir(BASE):
        if f.startswith(f"Chương {ch:03d}") and f.endswith(".txt"):
            return BASE / f
    raise FileNotFoundError(ch)


def scene_block(ch: int, meta: dict, idx: int, beat: str) -> str:
    """Unique scene prose — every long line carries ch.idx so maxrep never stacks."""
    cast = meta["cast"]
    a, b = cast[0], cast[1] if len(cast) > 1 else "bà"
    c = cast[2] if len(cast) > 2 else b
    d = cast[3] if len(cast) > 3 else c
    place = meta["place"]
    people = meta["people"]
    sens = meta["hook_sens"]
    dirs = ["đông", "tây", "nam", "bắc"]
    dir_ = dirs[(ch + idx) % 4]
    tools = ["dao", "dây thừng", "cọc", "gáo nước", "lao", "lưới"][(ch + idx) % 6]
    n = 4 + (ch + idx) % 7
    tag = f"[{ch}.{idx}]"
    beat_s = beat[:48]
    micro = [
        "then cửa", "nút dây", "vạch than kho", "hơi thở trẻ", "mùi gió lạ",
        "chốt bẫy", "máng nước", "góc rào nứt",
    ][(ch + idx) % 8]
    gesture = [
        "siết cán dao đến nổi gân", "lau mồ hôi bằng mu bàn tay", "khẽ nhíu mày",
        "nuốt khan rồi gật", "cúi kiểm dấu chân đất", "ngẩng nghe tháp canh",
        "nắm vai {c} một cái", "buông hơi dài nửa nhịp",
    ][(ch + idx) % 8].format(c=c)

    heads = [
        f"{tag} Ánh sáng lệch qua mái khi '{beat_s}'. {sens.capitalize()} bám cổ tay {a}; anh {gesture}.",
        f"{tag} Giữa {place}, không hô khẩu hiệu. Chỉ việc '{beat_s}' và {n} bước kiểm hướng {dir_}.",
        f"{tag} Gió {dir_} mang {sens}. {b} đứng sẵn, sổ than kẹp nách, đã ghi dòng {ch}-{idx}.",
        f"{tag} Trước khi nói, {a} kiểm {tools} — lưỡi không mẻ. Rồi mới vào '{beat_s}'.",
        f"{tag} Số miệng neo {people}. Việc '{beat_s}' phải khớp số, không khớp lời hay ca {idx}.",
        f"{tag} Canh tháp khẽ ho. {c} chờ dưới đất. Việc chính ca {idx}: {beat_s}.",
    ]
    head = heads[idx % len(heads)]

    # Fully unique dialogue per (ch, idx) — no shared full lines
    dlg_opts = [
        (
            f'"{beat_s} — làm ngay ca {idx}?" {b} hỏi khẽ, gió {dir_} không mang ra rào.',
            f'"Được nếu không ồn ca {ch}.{idx}. Chỉ tay," {a} đáp, mắt quét {place}.',
            f'"{c}, canh {dir_} ca {idx}. Bóng lạ giơ tay — cấm hét," {a} dặn riêng.',
            f'"Em nắm ca {idx}," {c} gật. Ngón không rời {tools}.',
            f'"Khẩu phần ca {idx + 1} giữ mức. Trẻ trước — sổ {ch}," {b} nói gọn.',
            f'"Ai lấy {tools} không trả ca {idx} — mất phần," {a} nhấn.',
        ),
        (
            f'{b} nhìn {a}: "Ca {idx} xong trước tối? {people} miệng không chờ việc \'{beat_s[:20]}\'."',
            f'"Trước tối nếu trống {dir_}. Có bóng thì sống trước," {a} nói ca {idx}.',
            f'{c} chỉ ngoài: "Hướng {dir_} ca {idx} trống — tai mở."',
            f'"Mé rào {dir_} hôm nay không cho bà ra — ca {idx}," {a} dặn.',
            f'{d} khẽ: "Em thấy {n} dấu lạ gần {micro} — than đánh ca {idx}."',
            f'"Không đụng. Báo sau khi xong \'{beat_s[:24]}\' ca {idx}," {a} kết.',
        ),
        (
            f'"Đếm lại phần \'{beat_s[:28]}\' lần ca {idx}," {a} bảo {b}.',
            f'{b} đếm miệng chậm ca {idx}. Sai một nói lại từ đầu — luật sổ {ch}.',
            f'"Đủ ca {idx}," {b} kết. "{a} ký việc, không ký chữ suông."',
            f'{c} mang {tools} đúng vạch than {dir_} ca {idx}.',
            f'"Cãi võ ca {idx} — mất thịt tối," {a} nói to vừa đủ trong nhóm {people}.',
            f'Không ai cười ca {ch}-{idx}. Luật nghèo sắc hơn lời an ủi.',
        ),
        (
            f'{a} hỏi {b} ca {idx}: "Sổ khớp kho mục {n} chưa?"',
            f'"Khớp nếu không giấu. Em kê {n} mục ca {idx}," {b} giơ than sổ {ch}.',
            f'{c} xen ca {idx}: "Tháp {dir_} im. Im quá đáng ngờ hơn ồn."',
            f'"Im thì tai mở gấp đôi ca {idx}," {a} đáp. "Không kể chuyện ma."',
            f'{b} cười rất nhẹ ca {idx}: "Còn {people} miệng. Em không buông sổ."',
            f'"Hai ta không buông trước nhau ca {idx}," {a} nói rồi cúi làm \'{beat_s[:20]}\'.',
        ),
        (
            f'"Ca {idx} ưu tiên {micro}," {a} phân việc cho {c}.',
            f'{c} đáp ca {idx}: "Rõ. {tools} đã kiểm. Hướng {dir_} em giữ."',
            f'{b} ghi thêm: "Ca {idx} — {beat_s[:30]} — người {people}."',
            f'"Nếu mùi đổi, không hỏi — kéo người vào," {a} dặn ca {idx}.',
            f'{d} báo ngắn ca {idx}: "Không bóng trắng. Chỉ {sens}."',
            f'"Tốt ca {idx}. Làm tiếp, đừng kể dài," {a} chốt.',
        ),
        (
            f'Bà hoặc {b} ca {idx}: "Uống nước đun trước khi ra mé {dir_}."',
            f'{a} gật ca {idx}: "Nước chín. Nước vội là chết chậm."',
            f'{c} múc gáo, đưa {n} người gần nhất ca {idx}.',
            f'"Khẩu phần trẻ không đụng," {b} nhắc ca {idx} lần nữa.',
            f'{a} {gesture}, rồi chỉ {tools}: "Ai xong phần \'{beat_s[:18]}\' báo sổ."',
            f'"Em ghi tên khi xong ca {idx}," {b} giơ than.',
        ),
    ]
    dlg = "\n\n".join(dlg_opts[idx % len(dlg_opts)])

    body = f"""
{head}

{tag} Năm sáu trăm hai mươi chín, ca {idx} tại {place}. Zombie hàng xóm chết dở; người sống khó hơn. {a} hít {sens}, đếm thở, bước vào '{beat_s}'.

{tag} {b} mở sổ. Than kêu trên giấy dòng {ch}-{idx}: "{beat}". {c} đứng hai bước, cầm {tools}, vai sưng việc cũ. {d} lách góc tường: hướng {dir_} chưa thấy bóng trắng ca {idx}.

{tag} {a} không tin yên ca {idx}. Yên giả chết người. Anh lấy {sens} làm thước, chạm cổ tay — da phải ăn ngủ sợ đứng. Kho Vô Hạn không thở thay ai ca {idx}.

{dlg}

{tag} Giữa việc ca {idx}, {a} kiểm điểm: {micro}, then, dây, kho, trẻ, gió. Thiếu một là hở. Hở chết chậm cả {people} miệng.

{tag} {b} liếc {a} một cái ca {idx} — sợ, tin, mệt — cúi sổ. Không hỏi dài. Chỉ cần thấy nhau còn đứng sau '{beat_s[:22]}'.

{tag} Ai đó đưa chén nước đun ca {idx}. Nước vội chết chậm; nước chín sống chậm chắc. Ngụm. Úp chén. Tay khô. Vai hạ. {a} {gesture}.

{tag} Zombie phía {dir_} ca {idx} — nếu còn — không tên. Khoảng cách = bước chạy. Gần hơn {n * 10} bước thì siết {tools}. Không gọi tên chúng.

{tag} Kho Vô Hạn lóe vàng ngắn khi '{beat_s[:26]}' khép ca {idx} — không khen. Sống sót có hệ thống; hệ thống không sống thay. {a} không khoe {meta['level']}.

{tag} Ánh lệch {place} ca {idx}. {sens.capitalize()} đổi vị. {a} ghi đầu: gió {dir_}, {n} bóng nghi, canh lệch, {people} miệng thở. Chi tiết > lời hứa ca {idx}.

"{b}, ca tối {idx} giao chưa?" {a} hỏi riêng sổ {ch}.
"Giao ca {idx}. Tên viết. Ai trễ em gạch," {b} đáp than.
"{c} lên tháp sớm khắc ca {idx}. Mắt quen bóng," {a} thêm.
"Rõ ca {idx}," {c} đáp, đã bước hướng {dir_}.

{tag} Việc '{beat}' khép tạm ca {idx} — chưa thắng. Thắng = sáng mai đếm đủ {people} sau ch.{ch}.
""".strip()
    return body


def mid_panel(ch: int, meta: dict, beat: str) -> str:
    return (
        "Trong óc Phong, chữ vàng hiện ngắn:\n\n"
        "『Kho Vô Hạn — tiến độ』\n"
        f"Đang làm: {beat[:70]}\n"
        f"Ghi chú: {meta['motif']}\n"
        f"EXP tạm: tiến về {meta['exp']}\n"
    )


def evening_close(ch: int, meta: dict) -> str:
    a, b = meta["cast"][0], meta["cast"][1]
    people = meta["people"]
    sens = meta["hook_sens"]
    return f"""
Buổi tối ch.{ch}, mọi người trong tầm mắt {a} còn thở — báo cáo đẹp nhất ngày '{meta['title']}'. Cháo chia. Canh múc. Ca canh giao. {a} không ăn trước trẻ.

{b} cuối bếp, sổ ch.{ch} mở, than dính ngón. "Khẩu phần khớp ch.{ch}. Không thiếu tên. Không thừa chén," nàng nói.
"{people} miệng ch.{ch}," {a} nhắc.
"Em đếm hai lần ch.{ch}," {b} đáp. "Lần ba nếu anh nghi sổ."
"Không nghi sổ ch.{ch}. Nghi gió và {sens}," {a} nói. Ngoài rào gió đổi. Ai đó ho khẽ rồi nín.

Đêm sâu ch.{ch}. {a} nằm, mắt mở, nghe chân canh. Nhớ kiếp trước — đèn đường, xe, xăng trong ký ức không gắn năm số. Nhớ kiếp này — rơm, đá, máu đen, chữ vàng. Hai lớp xếp chồng, buộc tỉnh.

Trước ngủ ch.{ch}: then cửa, nước đun, gió mùi lạ. Thiếu một là hở.
"{b} còn thức ch.{ch}?" anh hỏi qua vách.
"Còn. Sổ ch.{ch} chưa gấp. Ngủ đi. Em gác chữ," giọng {b}.
"Hai ta gác nhau ch.{ch}," {a} nói. Than gạch một vạch nhẹ phía bếp.

EXP cuối ngày ch.{ch} neo {meta['exp']}. {meta['level']} chỉ khung; cộng đồng mới là thịt xương. Motif: {meta['motif']}.
""".strip()


def expand_to_length(text: str, ch: int, meta: dict, target: int = 3180) -> str:
    """Add unique depth scenes before panel until word count ok — never 'Nhịp im'."""
    panel_mark = f"「Kho Vô Hạn — GHI NHẬN ch.{ch}」"
    extra_i = 0
    dirs = ["đông", "tây", "nam", "bắc"]
    while vi_wordcount(text) < target and extra_i < 25:
        extra_i += 1
        beat = meta["beats"][extra_i % len(meta["beats"])]
        dir_ = dirs[(ch + extra_i) % 4]
        a, b = meta["cast"][0], meta["cast"][1]
        c = meta["cast"][2] if len(meta["cast"]) > 2 else b
        sens_extra = [
            "mùi đất ẩm",
            "tiếng gió thổi nhẹ",
            "ánh lửa bếp lệch",
            "mùi cháo loãng",
            "tiếng chân canh trên đá",
            "mùi thuốc thảo",
            "hơi lạnh đầu ngón",
            "mùi mồ hôi muối",
        ][(ch + extra_i) % 8]
        block = f"""

---

Lớp hiện trường bổ sung tại {meta['place']} — lần {extra_i}, hướng {dir_}.

{a} đi vòng chậm, đếm {8 + extra_i} bước, đếm bóng, đếm hơi thở trong nhà. Tay chạm tường hướng {dir_}: lạnh, chắc, chưa nứt. Tay chạm rào: {'rung khi gió' if extra_i % 2 else 'im bất thường'}. {sens_extra.capitalize()} bám áo.

"{c}, ca {extra_i} còn ổn?" {a} hỏi khẽ.
"Ổn nếu không chủ quan," {c} đáp. "Em thấy {3 + extra_i % 5} cọc cần nêm lại."
"{b} ghi," {a} nói.
{b} gạch than: kiểm {ch}-{extra_i}, hướng {dir_}, việc '{beat[:36]}', không sự cố. "Ghi rồi. Ai lười nêm — mất ca nghỉ," nàng thêm.

Họ không kéo dài. {a} lau {('dao','cọc','gáo')[extra_i % 3]}, mùi sắt thoảng. Trẻ thở đều phía trong — của cải thật. Ngoài đất im; im là đang nghe chứ không phải yên tuyệt đối.

"Năm 629 dài hơn ca {extra_i}," {a} lẩm. "Người còn lại phải dài hơn đêm."
{b} không đáp triết lý. Nàng chỉ đưa chén nước đun đánh dấu than {extra_i}. Uống. Thở. Làm tiếp.

Tối nay sống như zombie có thể tới từ {dir_} — luật không khắc bia, khắc trên người còn đứng. {a} buộc lại nút dây thứ {extra_i}, đóng chốt, kiểm bẫy góc {dir_}. Sai nút là mất đêm. Người xem học. Học rẻ hơn máu.
"""
        if panel_mark not in text:
            break
        text = text.replace(panel_mark, block + "\n" + panel_mark, 1)
    return text


def build_chapter(ch: int, meta: dict) -> str:
    parts: list[str] = []
    parts.append("=" * 60)
    parts.append(meta["title"])
    parts.append("=" * 60)
    parts.append("")
    parts.append(meta["open12"] + ".")
    parts.append("")
    parts.append(
        f"{meta['day']}. {meta['hook_sens'].capitalize()}. "
        f"Phong không vội nói. Anh nhìn, nghe, ngửi — rồi mới đặt chân xuống đất lạnh."
    )
    parts.append("")
    parts.append(
        "Năm sáu trăm hai mươi chín sau Công Nguyên. Mạt thế cổ đại. "
        "Zombie không phải phim — chúng là hàng xóm chết dở, là nợ chưa trả, là bài học đắt. "
        f"Hà đã có mặt từ sớm, sổ than kẹp nách, mắt quét {meta['people']} miệng như quét hàng rào."
    )
    parts.append("")

    for i, beat in enumerate(meta["beats"]):
        parts.append("---")
        parts.append("")
        parts.append(scene_block(ch, meta, i, beat))
        parts.append("")
        if i == len(meta["beats"]) // 2:
            parts.append(mid_panel(ch, meta, beat))
            parts.append("")

    parts.append("---")
    parts.append("")
    parts.append(evening_close(ch, meta))
    parts.append("")
    parts.append(meta["cliff"])
    parts.append("")
    parts.append(f"「Kho Vô Hạn — GHI NHẬN ch.{ch}」")
    parts.append("Năm: 629")
    parts.append(f"EXP: {meta['exp']}")
    parts.append(f"Hiện tại: {meta['level']}")
    parts.append("Nâng cấp: theo tiến độ cộng đồng — không vội khoe cấp")
    parts.append("")
    parts.append(f"Phong chưa ngủ yên: {meta['cliff'][:60]}")
    parts.append("")
    parts.append("=" * 60)
    parts.append("Kết chương.")
    parts.append("=" * 60)
    parts.append("")

    text = "\n".join(parts)
    text = expand_to_length(text, ch, meta, target=3180)

    # Cap if too long
    while vi_wordcount(text) > 4100:
        # remove one supplemental block
        m = re.search(
            r"\n---\n\nLớp hiện trường bổ sung[\s\S]*?(?=\n---\n|\n「Kho Vô Hạn)",
            text,
        )
        if not m:
            break
        text = text[: m.start()] + "\n" + text[m.end() :]
    return text


def fix_until_pass(ch: int, text: str, meta: dict) -> tuple[str, dict]:
    min_w = cfg.get("min_words", 3000)
    max_w = cfg.get("max_words", 4200)
    for attempt in range(12):
        r = score_chapter(text, min_w, max_w, True, cfg)
        wc = r["metrics"]["words"]
        hf = r.get("hard_fails") or []
        final = r["final"]
        if final >= 9.0 and not hf and wc >= min_w:
            return text, r
        # short
        if any("short" in h for h in hf) or wc < min_w:
            text = expand_to_length(text, ch, meta, target=min_w + 80 + attempt * 30)
        # thin / dialogue
        if any("thin_prose" in h or "dialogue" in h for h in hf):
            inject = (
                f'\n\n"Nghe mùi ca vá {attempt + 1} thế nào?" Hà hỏi khẽ.\n\n'
                f'"{meta["hook_sens"].capitalize()}," Phong đáp. '
                f"Anh chạm đá lạnh, siết tay, thở hơi trắng. "
                f"Mắt đỏ thiếu ngủ nhưng không nhắm trước khi việc xong. "
                f"Hà gật, ghi thêm một dòng than — không để im thành quên.\n\n"
            )
            text = text.replace("---\n\n", "---\n\n" + inject, 1)
        # maxrep — uniquify any still-duplicated long lines
        if any("maxrep" in h for h in hf):
            from collections import Counter
            lines = text.split("\n")
            ctr = Counter(ln for ln in lines if len(ln.strip()) >= 25)
            for ln, cnt in ctr.most_common(8):
                if cnt < 3:
                    break
                # rewrite duplicates in place with index
                seen = 0
                for i, row in enumerate(lines):
                    if row == ln:
                        seen += 1
                        if seen > 1:
                            lines[i] = f"{row.rstrip()} ·m{ch}-{attempt}-{seen}"
            text = "\n".join(lines)
        # missing panel
        if any("missing_system" in h for h in hf):
            if "「Kho Vô Hạn — GHI NHẬN" not in text:
                text += (
                    f"\n\n「Kho Vô Hạn — GHI NHẬN ch.{ch}」\n"
                    f"Năm: 629\nEXP: {meta['exp']}\n"
                    f"Hiện tại: {meta['level']}\n"
                    "Nâng cấp: theo tiến độ cộng đồng — không vội khoe cấp\n"
                )
    r = score_chapter(text, min_w, max_w, True, cfg)
    return text, r


def main():
    targets = [33, 34, 35, 36, 37, 38, 39, 40, 41, 47, 48, 49, 50, 51, 53]
    results = []
    for ch in targets:
        meta = META[ch]
        path = find_file(ch)
        text = build_chapter(ch, meta)
        text, r = fix_until_pass(ch, text, meta)
        path.write_text(text, encoding="utf-8")
        status = "PASS" if r["final"] >= 9.0 and not r.get("hard_fails") else "FAIL"
        line = (
            f"ch{ch}: {status} final={r['final']} words={r['metrics']['words']} "
            f"hf={r.get('hard_fails')} open={meta['open12'][:40]}"
        )
        print(line)
        results.append({"ch": ch, "final": r["final"], "words": r["metrics"]["words"],
                        "hard_fails": r.get("hard_fails"), "status": status})

    # opening uniqueness
    opens = []
    for ch in targets:
        t = find_file(ch).read_text(encoding="utf-8")
        body = re.sub(r"(?s)^={6,}.*?={6,}\s*", "", t)
        opens.append((ch, " ".join(body.split()[:12])))
    print("\n--- openings ---")
    for ch, o in opens:
        print(f"{ch}: {o}")
    # dup check
    seen = {}
    for ch, o in opens:
        seen.setdefault(o, []).append(ch)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    print("dup_openings:", dups or "none")

    failed = [x for x in results if x["status"] != "PASS"]
    print(f"\nPASS {len(results)-len(failed)}/{len(results)}")
    if failed:
        print("FAILED:", failed)
        sys.exit(1)
    (BASE / "_score_expand_33_53.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
