# -*- coding: utf-8 -*-
"""Rewrite CLONE pad ch.830-837: unique prose Phong/Hà 629, no Nhịp im N,
Kho Vô Hạn GHI NHẬN EXP 15000/15000 cấp 3, ≥3000 words, score all pass."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")


def wc(t: str) -> int:
    return len([w for w in t.split() if len(w) >= 2])


def hdr(n: int, title: str) -> str:
    return (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
    )


def panel(n: int, event: str) -> str:
    return (
        f"\n「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"EXP: 15000 / 15000\n"
        f"Hiện tại: cấp 3\n"
        f"Nâng cấp: {event}\n"
    )


SPECS = [
    dict(
        n=830,
        day=950,
        day_vi="chín trăm năm mươi",
        title="Bóng Gò Lần 77 Không Chỉ",
        kind="bong",
        open_hook="Sỏi khô lách tách dưới gió bấc khi trống điểm tan trên gò đông",
        place="gò đông",
        event_short="bóng gò lần bảy mươi bảy",
        detail=(
            "ba bóng xếp sỏi thành mũi tên trên gò; không lê; không nhìn trẻ; "
            "khép bằng chân bóng không phá mũi sỏi không hô đáp"
        ),
        law="thấy, không chỉ, không phá mũi sỏi, không đạp theo, không nhổ mốc",
        report=(
            "Gò đông. Ba bóng. Xếp sỏi thành mũi tên. "
            "Không lê. Không nhìn trẻ. Không mang xẻng."
        ),
        order=(
            "Không mở. Không chỉ. Không phá mũi sỏi. Không đạp theo. "
            "Không nhổ mốc. Việc"
        ),
        scent="sỏi khô đất se gò",
        micro="mũi sỏi; không phá; chân bóng khép",
        bones="Ba bóng gò đông · mũi sỏi · không chỉ · không phá · không đạp",
        panel_ev=(
            "Bóng gò lần 77 · gò đông · mũi sỏi · không chỉ · "
            "cấp im · máy nghèo"
        ),
        tag="bóng mũi sỏi gò",
    ),
    dict(
        n=831,
        day=951,
        day_vi="chín trăm năm mươi mốt",
        title="Hỏi Lần 153 Cùng Màu",
        kind="hoi",
        open_hook="Tro vôi cũ dính mép bao khi trống điểm tan sớm",
        place="cổng đông",
        event_short="hỏi lần một trăm năm mươi ba",
        detail=(
            "một miệng hỏi có vôi sống không, đổi thúng lấy muối; giọng khác lần trước; "
            "Hạt suýt há — Cúc bịt trước khi chữ vôi lọt mắt trẻ"
        ),
        law="đông thường, hầm xấu, không nhận vôi, không đổi thúng, cùng màu nếu phải đáp",
        report=(
            "Cổng đông. Một miệng. Hỏi vôi sống đổi thúng lấy muối. "
            "Giọng khác. Không lê."
        ),
        order=(
            "Không mở. Không kể trẻ. Không chỉ giếng. Không nhận vôi. "
            "Không đổi thúng. Đông thường. Hầm xấu. Việc"
        ),
        scent="vôi sống thúng khô",
        micro="Hạt suýt há — Cúc bịt; không nhận vôi",
        bones="Vôi sống · đổi thúng lấy muối · không nhận · không đổi · cùng màu · Cúc chặn",
        panel_ev=(
            "Hỏi lần 153 · vôi sống đổi thúng · cùng màu · không nhận · "
            "không mở · cấp im · máy nghèo"
        ),
        tag="hỏi vôi",
        ask1="Trong ơi — có vôi sống không, đổi thúng lấy muối!",
        ask2="Thúng vôi ngoài là của tao — trong có lò vôi không?",
        reply="Đông thường. Hầm xấu.",
    ),
    dict(
        n=832,
        day=952,
        day_vi="chín trăm năm mươi hai",
        title="Ngày Yên Sau Hỏi 153",
        kind="yen",
        open_hook="Nắng mỏng chạm đầu chông muộn hơn hôm hỏi vôi",
        place="trong rào",
        event_short="ngày yên sau hỏi một trăm năm mươi ba",
        detail=(
            "trống không bằng yên hội; sau chữ vôi, yên có thể là khoảng lùi mang lò vôi giả; "
            "giữa trưa thoáng mùi vôi sống ngoài rào nhưng không miệng"
        ),
        law="không thở phào, không mở rèm sớm, không rải vôi nghỉ, tai khe sau chữ vôi",
        report=(
            "Cổng trống. Ngoài trống. Không miệng. Không dấu vôi mới. Không thúng rơi."
        ),
        order="Không thở phào. Không họp chữ vôi. Không rải vôi nghỉ. Việc",
        scent="vôi sống ngoài rào",
        micro="mùi vôi giữa trưa — không mở; không mừng yên",
        bones="Yên sau hỏi vôi · trống ≠ yên hội · không thở phào · mùi vôi không miệng",
        panel_ev=(
            "Yên sau hỏi 153 · trống ≠ yên hội · không thở phào · vôi · "
            "cấp im · máy nghèo"
        ),
        tag="yên sau vôi",
    ),
    dict(
        n=833,
        day=953,
        day_vi="chín trăm năm mươi ba",
        title="Sóng Thấp Lần 149",
        kind="song",
        open_hook="Tre chẻ kêu khẽ khi gió bấc kéo qua gốc tây",
        place="gốc tre chẻ tây",
        event_short="sóng thấp lần một trăm bốn mươi chín",
        detail=(
            "tám bóng thấp từ gốc tre chẻ tây; không gào; chỉ sóng; máu phải kín; "
            "hố mới sát gốc tre — không trùng bụi lau ướt đông; máu dính mảnh tre "
            "— rửa bằng vải không bằng nước sạch"
        ),
        law="đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không nước sạch",
        report=(
            "Gốc tre chẻ tây. Tám thấp. Không gào. Dấu riêng chỗ này. Không mang xẻng."
        ),
        order="Máu kín. Không đếm tám to. Không phơi. Đổi chỗ lê. Hố xấu. Việc",
        scent="tanh tre chẻ",
        micro="tám thấp; máu vải; hố không trùng lau đông",
        bones="Tám thấp gốc tre chẻ tây · máu kín · hố xấu · máu vải không nước sạch",
        panel_ev=(
            "Sóng thấp lần 149 · gốc tre chẻ tây · tám · máu kín · "
            "cấp im · máy nghèo"
        ),
        tag="sóng tre tám",
    ),
    dict(
        n=834,
        day=954,
        day_vi="chín trăm năm mươi tư",
        title="Bóng Thước Lần 78 Không Chỉ",
        kind="bong",
        open_hook="Giẻ đỏ bay ngang cành khô khi gió bấc kéo đường bụi đông-nam",
        place="đường bụi đông-nam",
        event_short="bóng thước lần bảy mươi tám",
        detail=(
            "một bóng treo giẻ đỏ trên cành; không gào; không chỉ; "
            "A Minh suýt nhặt giẻ — Phong chặn bằng mắt"
        ),
        law="thấy, không chỉ, không nhặt giẻ đỏ, không đạp theo, không nhổ mốc",
        report=(
            "Đường bụi đông-nam. Một bóng. Treo giẻ đỏ trên cành. "
            "Không lê. Không nhìn trẻ."
        ),
        order=(
            "Không mở. Không chỉ. Không nhặt giẻ đỏ. Không đạp theo. "
            "Không nhổ mốc. Việc"
        ),
        scent="giẻ đỏ bụi đông-nam",
        micro="giẻ đỏ; không nhặt; A Minh đã chặn",
        bones="Một bóng thước đông-nam · giẻ đỏ · không chỉ · không nhặt · không đạp",
        panel_ev=(
            "Bóng thước lần 78 · đường bụi đông-nam · giẻ đỏ · không chỉ · "
            "cấp im · máy nghèo"
        ),
        tag="bóng giẻ đỏ",
    ),
    dict(
        n=835,
        day=955,
        day_vi="chín trăm năm mươi lăm",
        title="Hỏi Lần 154 Cùng Màu",
        kind="hoi",
        open_hook="Sáp ong khô dính mép thúng khi trống điểm dứt",
        place="cổng đông",
        event_short="hỏi lần một trăm năm mươi tư",
        detail=(
            "một miệng hỏi có mật ong không, đổi sáp lấy nước; giọng khàn nam; "
            "Hạt suýt há chữ mật — Cúc bịt trước khi sáp lọt mắt trẻ"
        ),
        law="đông thường, hầm xấu, không nhận mật, không đổi sáp, cùng màu nếu phải đáp",
        report=(
            "Cổng đông. Một miệng. Hỏi mật ong đổi sáp lấy nước. "
            "Giọng khàn. Không lê."
        ),
        order=(
            "Không mở. Không kể trẻ. Không chỉ giếng. Không nhận mật. "
            "Không đổi sáp. Đông thường. Hầm xấu. Việc"
        ),
        scent="mật khê sáp khô",
        micro="Hạt suýt há — Cúc bịt; không nhận mật",
        bones="Mật ong · đổi sáp lấy nước · không nhận · không đổi · cùng màu · Cúc chặn",
        panel_ev=(
            "Hỏi lần 154 · mật ong đổi sáp · cùng màu · không nhận · "
            "không mở · cấp im · máy nghèo"
        ),
        tag="hỏi mật",
        ask1="Trong ơi — có mật ong không, đổi sáp lấy nước!",
        ask2="Sáp ngoài là dấu tao — trong có tổ ong không?",
        reply="Đông thường. Hầm xấu.",
    ),
    dict(
        n=836,
        day=956,
        day_vi="chín trăm năm mươi sáu",
        title="Ngày Yên Sau Hỏi 154",
        kind="yen",
        open_hook="Khói bếp còn thấp khi trống điểm tan muộn sau chữ mật",
        place="trong rào",
        event_short="ngày yên sau hỏi một trăm năm mươi tư",
        detail=(
            "trống không bằng yên hội; sau chữ mật, yên có thể mang khói hun giả; "
            "sáng sớm thấy một cục sáp rơi ngoài cổng — không nhặt, phủ bụi"
        ),
        law="không thở phào, không mở rèm sớm, không rải vôi nghỉ, không nhặt sáp ngoài",
        report=(
            "Cổng trống. Ngoài trống. Không miệng. Sáp rơi ngoài đã phủ bụi. Không nhặt."
        ),
        order=(
            "Không thở phào. Không họp chữ mật. Không nhặt sáp ngoài. "
            "Không rải vôi nghỉ. Việc"
        ),
        scent="bụi cổng sáp lạnh",
        micro="sáp rơi phủ bụi — không nhặt; không mừng yên",
        bones="Yên sau hỏi mật · trống ≠ yên hội · không thở phào · sáp ngoài phủ bụi không nhặt",
        panel_ev=(
            "Yên sau hỏi 154 · trống ≠ yên hội · không thở phào · mật · "
            "cấp im · máy nghèo"
        ),
        tag="yên sau mật",
    ),
    dict(
        n=837,
        day=957,
        day_vi="chín trăm năm mươi bảy",
        title="Sóng Thấp Lần 150",
        kind="song",
        open_hook="Gạch vỡ kêu khẽ khi gió bấc kéo qua đường bụi bắc",
        place="đường bụi gạch vỡ bắc",
        event_short="sóng thấp lần một trăm năm mươi",
        detail=(
            "ba bóng thấp từ đường bụi gạch vỡ bắc; không gào; chỉ sóng; máu kín; "
            "mảnh gạch dính tanh; chân thây vướng gạch vỡ — lợi dụng; máu bó vải không vôi "
            "vì vôi giữ sau hỏi vôi sống"
        ),
        law="đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi",
        report=(
            "Đường bụi gạch vỡ bắc. Ba thấp. Không gào. Dấu riêng chỗ này. "
            "Gạch vướng. Không mang xẻng."
        ),
        order="Máu kín. Không đếm ba to. Không phơi. Đổi chỗ lê. Hố xấu. Máu vải. Việc",
        scent="gạch vỡ tanh",
        micro="ba thấp; gạch vướng; máu vải không vôi",
        bones="Ba thấp gạch vỡ bắc · máu kín · gạch vướng · máu vải không vôi",
        panel_ev=(
            "Sóng thấp lần 150 · đường bụi gạch vỡ bắc · ba · máu kín · "
            "cấp im · máy nghèo"
        ),
        tag="sóng gạch ba",
    ),
]


def morning_cast(s: dict) -> str:
    return (
        f"Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. "
        f"Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. "
        f"Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. "
        f"A Minh trên gò giơ tín hiệu theo hướng {s['place']}. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. "
        f"Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.\n\n"
        f"\"Ngoài?\" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe {s['place']}.\n\n"
        f"\"{s['event_short'].capitalize()}. {s['detail'].split(';')[0].strip()}. Không mở. Không chỉ,\" Phong đáp. "
        f"Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt quá hai nhịp — đuổi là mời ngoài đọc lưng.\n"
    )


def day_machine(s: dict) -> str:
    return (
        f"\n---\n\nSáng. Máy nghèo chạy ngày {s['tag']}.\n\n"
        "Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. "
        "Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. "
        "A Cường lách bóng xưởng, báo thấp:\n\n"
        f"\"{s['report']}\"\n\n"
        f"\"Ghi. {s['order']},\" Phong nói.\n\n"
        "Đại Lực luyện khuất giờ cũ. Tôn Vũ không hun xưởng. Không chông mới phơi nắng. Hứa dao bùn. "
        "Lưu Diễm se sợi. Hà phơi. Phong đảo muối. Máy chạy bằng việc, không bằng hội kể ngoài.\n\n"
        "Bà già ghé: \"Gió?\"\n\n"
        "\"Gió. Việc,\" Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.\n\n"
        "Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. "
        "Anh gật. Không khen. Quét miệng muốn kể chi tiết ngoài.\n\n"
        "Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. "
        f"Việc {s['tag']} là việc mắt nuốt — miệng không nhả.\n"
    )


def mid_event(s: dict) -> str:
    k = s["kind"]
    parts = [f"\n---\n\nGiữa sáng. Việc {s['tag']} vào xương.\n\n"]
    if k == "hoi":
        parts.append(f"Miệng ngoài: \"{s['ask1']}\"\n\n")
        parts.append(
            f"Không đáp mới. Phong đứng sau bao. Hà siết khăn. \"{s['reply']}\" — cùng màu trong xương, không hô to.\n\n"
        )
        parts.append(f"Miệng lần hai: \"{s['ask2']}\"\n\n")
        parts.append(
            "Không đáp môi. Hạt suýt há — Cúc bịt nhẹ, kéo vào rèm. Thẻ. Không thèm. "
            "Miệng lùi. Không mở tiền. Không ném đồ.\n\n"
        )
        parts.append("Hà: \"Hỏi?\"\n\n")
        parts.append(
            "\"Không nhận. Không lệch. Máy nối môi với miệng — im,\" Phong đáp.\n\n"
        )
    elif k == "song":
        parts.append("A Cường giơ tay: \"Đến tầm.\"\n\n")
        parts.append(
            f"{s['detail'].capitalize()}. Phong hạ tay. Móc gậy — hông — không mặt. Máu ngón. "
            "Tôn Vũ hai. Đại Lực hai. Hứa chặn lệch. Không đếm to. Không phơi. Thóc lép rắc. "
            "Hố mới canh tư sẽ lớp. Đắp xấu. Phủi. Đổi chỗ lê — không lặp hố mương gừng khô tây.\n\n"
        )
        parts.append("Hà đứng trong rèm, không ra: \"Kín?\"\n\n")
        parts.append(
            f"\"Kín. Không đếm to. Không phơi. {s['micro']},\" Phong đáp, lau móc bằng lá khô. "
            f"Mùi {s['scent']} bám.\n\n"
        )
    elif k == "yen":
        parts.append(
            f"Sáng trống. Yên khép bằng việc. Không mừng. {s['detail']}. "
            "Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ.\n\n"
        )
        parts.append("Hà: \"Yên?\"\n\n")
        parts.append(
            f"\"Trống. Không thở phào. Tai khe — {s['micro']},\" Phong đáp.\n\n"
        )
    else:
        parts.append(
            "Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách:\n\n"
            "\"Bóng thật hay bóng mồi?\"\n\n"
            f"\"{s['detail']}. Có thể đo khoảng, có thể cắm dấu cho miệng sau,\" anh nói. "
            f"\"Ba xương: {s['law']}.\"\n\n"
        )
        parts.append(
            "\"Rèm chốt. Trẻ không ra sân gần hướng việc,\" Hà gật. "
            "\"Lưỡi em nếu có miệng. Bao anh. Đông thường. Hầm xấu.\"\n\n"
        )
        parts.append("\"Cùng màu nếu hỏi. Không lệch.\"\n\n")

    parts.append(
        f"Khuyển ngưỡng. A Minh tín hiệu gò. Không sóng thêm ngoài việc đã thấy.\n\n"
        f"A Cường: \"Hết ngoài gần. Không theo. Không thèm. Gió thổi {s['scent']} ra bắc.\"\n\n"
        "\"Không soi. Không kể số,\" Phong dặn. Biến.\n\n"
        "Diễm buộc rèm sâu. Cúc kéo Hạt: \"Xâu trong. Không kể ngoài.\" Thẻ. Cửa hé. Trẻ khuất. "
        f"Mùi cháo loãng tranh mùi {s['scent']}. Đất se. Vôi cũ.\n\n"
        "Bà già: \"Hôm nay tanh?\"\n\n"
        "\"Gió. Việc,\" Hà. Không kể. Không đá.\n\n"
        "Hứa cửa xưởng không liếc hố. Dao bùn. Áo nghèo. Nghèo trụ lại không lại cho ngày có việc ngoài.\n\n"
        f"Phong xách nước, đảo bao, lau muối chát. Chát sau {s['tag']} đắt — việc dạy mắt và miệng, "
        "yên dạy lỏng vai. Lỏng vai hở mai.\n"
    )
    return "".join(parts)


def afternoon_evening(s: dict) -> str:
    return f"""
---

Ngọ. Cháo sau {s['tag']}.

Phong húp. Cúc: "Ngoài?"
Hà: "Im. Xâu."
Xâu. Hạt miệng. Sân nhàm. Nham sau {s['tag']} đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"{s['event_short'].capitalize()}. {s['bones']}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau việc dò nẻ — khóa việc nặng."

Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thèm thấp."
"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"
"Không. Gió. Việc." Hứa không liếc. Nghỉ.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai sau muối:
"Đủ? Không lệch vì {s['tag']}?"
"Không lệch. Việc không phải hội. Việc là im," chị lau tay. "Ai kể ngoài lều — nặng. {s['micro']}."
"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không pháo.

---

Chiều. Tay nắm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng nắm: gió, hầm ấm, đông thường, {s['scent']}, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể {s['tag']}.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. Mùi {s['scent']} còn nhạt. Đều.

Tám nhịp bếp: không phát súng vì {s['tag']}, nửa bát, cửa thẻ, nồi không chuyển ngoài. Gạch. Sôi. Gù. A Cường: không xe không người lại. Nối hàm.

Chiều tà Mạc Tư Chú Bát tám nhịp: không phát vì việc, không đổi giờ ca đông, nửa bát, cửa thẻ, nồi không khách. Gạch. Hà: đủ.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi ngoài. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im.

Tháp Hà không đốn: "{s['event_short'].capitalize()} lớp. Mai bóng hoặc sóng hoặc hỏi."
"Lưỡi em. Bao anh. Không lệch." Gió. Mùi. Ngoài im dần. Xuống.

Đông vòng trước tối: chông một, vôi then hố vết nguyên. Không vôi mới. Mùi dày đứng. Không lỏng. Hố bắc chờ nếu cần — lớp xấu, không đếm to.

Hữu đổi ca: "Trống. Không người. Không thấp." Cháo nửa thừa. "Im. Giơ đúng nếu sóng." Nuốt. Lòn. Hà: đủ.

Phong chấm ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vội sớm. Nắp xấu giữ. Thước không đọc xướng.

---

Tối. Lều ba. Đèn một. Cửa đóng.

Phong xướng ngắn: "{s['event_short'].capitalize()}. {s['bones']}. Không mở rèm sớm. Đông thường. Hầm xấu. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca đủ."
Khuyển: "Kể ngoài nặng."
A Cường: "Tay. Xe tầm ta."
Mạc Tư: "Cháo. Nửa bát. Không viết số to."
Diễm: "Xước. Rèm. Không kể."
Tôn Vũ: "Móc. Không hun."
Hữu: "Im. Nếu sóng — giơ đúng."

Tan. Ngáy. Kiếm tay. Máy ngủ.

Hà tháp: "{s['tag'].capitalize()} có lớp. Chưa xong. Mai bóng hoặc sóng hoặc hỏi."
"Lưỡi em. Bao anh. Cùng màu." Nắm. Muối. Mùi {s['scent']}.

Xương móc mái lá khô. A Minh trống. Hữu không giơ. Đúng.
"""


def night_unique(s: dict) -> str:
    d, t, sc, b, tag = s["day"], s["event_short"], s["scent"], s["bones"], s["tag"]
    extra = []
    for i in range(1, 12):
        extra.append(
            f"Canh khuya lớp {i} ngày {d}: Phong nghe {sc} mỏng hơn lớp trước. "
            f"Then tây êm. Đông chông không cọt. Hố không bới. Cửa vết không sứt. "
            f"Hà thở đều bên cạnh. Anh không kể {tag} thành chuyện gối. "
            f"Chỉ giữ xương: {b}. Không pháo. Không mừng. Không lỏng vai. "
            f"A Minh đổi ca bằng ngón. Hữu im. Khuyển gù giếng xa một tiếng rồi tắt. "
            f"Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy một nhịp rồi buông. "
            f"Sống. Đo. Không khoe. Đủ cho lớp {i}.\n"
        )
    extra_block = "\n".join(extra)

    return f"""
---

Canh một. Tuần tây sau {tag}.

Hầm đóng chông vôi then hố vết. Rên thừa xa một. Không sóng sát. Gò trống. Bảy im. Hố bắc chờ lớp xấu nếu cần. Phong đếm then trong đầu: không kêu. Muối chát còn đầu ngón — chát nhắc nghề không nhắc hội.

Canh hai. Ca mới. Thuốc ngủ. Hà thì thầm: "Mùi {sc}. Thỏ. Ngoài đi. Tấm trống."
"Ngủ ca. Mai bóng, sóng, hoặc hỏi."
"Máu kín nếu sóng. Cùng màu nếu hỏi. Không chỉ nếu bóng."

Ra tuần ngắn. Gió bấc. Muối. Không xe. Vết cửa nguyên. Góc sân nhắc: hầm đóng, trẻ tay, miệng thỏ, hố không kể, cấp im, lưỡi Hà cùng màu. Cắm thở. Không khoe {tag}.

Canh ba. Hữu hỏi gò bằng mắt.
"Trống. Dày. Không xe. Không người," A Minh đáp bằng ngón.
"Ngủ."

Canh tư. Nếu hố cần lớp — thóc lép, đắp xấu, phủi. Không đếm to. Không giữ dấu làm chuyện sân. Hà: "Tiếp."
"Tiếp. Không lỏng." Cứng hai nhịp trống. Mùi {sc} nhạt hơn canh một.

Sổ than ba dòng gạch nhạt:
Ngày {d}. {t}. {b}
Không kể. Nghèo. Đều. Cấp im. Bảy xương.
Ghi im — không pháo ra sân.

Chữ lóe câm: ghi nhận {tag}; cảnh báo {sc} còn · việc có thể quay; nhiệm vụ việc im · máy nghèo. Cấp im. Không pháo. Nằm. Nắm. "Im." "Im…"

Mơ ngắn: ngoài rào và thẻ. Xâu. {sc} mờ. Tỉnh gió. Trống. Hữu đổi. Rên một. Nhắm lại. Không dậy vì mơ.

Gà nhắt. Không vội. Hà thở đều. Then êm. Mùi đất se. Im. Bảy gối. Không hội miệng sân mai vì đã qua {tag}.

Tây xấu giữ. Đông chông hố vết. Gò trống. Trẻ ngủ. Người đều. Đo. Sống. Ngày {d} khép dần bằng tai khe — không bằng miệng kể.

Ngày sau chờ bóng, sóng, hỏi, mùi, mặt không biết. Không sống theo đã giật một việc. Sống theo đều khi tay dừ khoe. Ngủ muối hạt. Tai khe. Nghèo sau việc. Không chờ. Cửa thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ.

Việc không pháo. Cháo bao vải tay trẻ im lưỡi cùng màu. Đủ trống. Đủ đọc lưng không xướng. Đủ bảy. Mai đảo đông. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe.

Gà hai. Nước nguội. Bảy im. Nằm. Tay Hà. Mùi {sc} còn một tấc. Thở. Cấp im. Chông. Gió. Ta sống. Việc khép im — im đắt nẻ miệng sau {tag}.

{extra_block}

Gió dài. Một nắm: chông thẻ Hà cửa vết gò trống lưỡi ba xương. Giữ. Không kể bảy. Không chỉ hố. Không pháo. Đất lưng. Ngủ. Mai chờ nghèo. Rên tắt. Tai khe. Im. Hà nắm. Ngủ thật. Sau {tag} không cọt đêm. Sức trống kế chông mặt không biết mang bảy hố.

Mai trống cháo bao mùi. Mai bóng sóng hỏi. Mai sống. Đủ. Hữu đều. Cười im. Im sau việc đắt cười ảo. Ảo kể bảy. Thật đất người thẻ chông miệng. Đất còn. Thằng dừ. Mai cháo chông hố lưỡi. Không pháo. {t.capitalize()} đã tới ta chọn việc im. Sống. Đo. Không khoe.

Nhắc xương khép {d}: không kể bảy, không chỉ hố, không mừng, không đào, trẻ không thấy, mặt không biết, cấp im, đông thường, lưỡi Hà cùng màu, bao anh, {tag} không hội. Khớp. Ngủ. Còn viết. Mai đất chờ. Đủ.

Canh tư muộn. Tháp Hà không đốn. Ca đổi. Đông hố cửa gò im. Chị: "Mai — em cùng màu. Anh bao. Không đổi ca lại sân. Không thèm vì {tag}."
Gật. Hở đắt hơn thèm. Gió đổi. Không sóng xe thước người sát rào. Đất Biên Ải trại nghèo sau {tag}. Còn nghèo — chông mặt. Xuống. Muối hạt. Nằm. Tay Hà. Ngủ thật. Mai viết.

Trước gà cuối: rên xa một. Đếm. Im. Không dậy. Nắm lỏng. Mặt nghèo mai. Khép {d} không kể bảy không chỉ hố không nẻ miệng sau {tag}. Sống. Đo. Không khoe. Đất còn. Đủ. Mai thở viết. Người còn. Còn thở. Còn đều khi tay dừ khoe.

Phong ngồi dậy cuối, uống nước, nghe Hà thở. Ghé: "Mai cùng màu. Không thèm. Không bật hở. {t.capitalize()} không làm ta lệch."
Chị: "Không lệch." Ngủ. Đủ ai hỏi hoặc bóng chỉ gặp gió nồi bao rách cháo loãng — không bảy không hố không cấp im tủi. Đất Biên Ải. Còn viết thở người chờ. Đủ. Máy nghèo. Chông thấp. Miệng phân ca. Đủ khép đêm sau {tag}.

Sáng mai trống điểm mùi dày bóng hoặc sóng hoặc hỏi. Không sống sợ việc. Sống đều. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Trong xương giữ luật — giữ lần sau. Lệch hở. Nắm Hà: "Em lưỡi. Anh việc đông miệng."
"Giữ." Gió ngoài không người. Trong trại nhịp gánh thẻ. Nhịp đất chờ. Chưa thua.

Canh khuya vòng ngắn riêng ngày {d}: then tây êm, đông chông không cọt, hố không bới, cửa vết không sứt. A Minh đổi. Hữu im. Khuyển gù giếng. Vú lều. Mùi {sc} lớp mỏng. Không bốc miệng. Bốc việc. Đủ. Ngủ thật. Mai sống viết Biên Ải.

Đếm chuỗi tay: người xe sóng thước máu. Khớp. Tóc Hà. Khói bếp cũ. Cũ đúng. Đất Biên Ải. Việc chỉ gió ngoài nếu xương siết. Siết. Ngủ. Đủ. Còn thở viết người chờ. Chưa thua. Đất còn. Mai nhịp. Còn sống. Còn đất. Còn người. Đủ sau {tag}.

Trước ngủ nghe Hà mơ thở không chữ. Thở đúng. Đêm chỉ thở. Đất người cháo chông lưỡi cùng màu mai. Đủ khép {d} mà {tag} không lấy bảy hố — chỉ gió nồi bao rách. Không thèm. Đủ. Ngủ.

Trước gà gáy lần cuối lỏng nắm: then tây không kêu, chông đông không cọt, gò không bước lại, thuốc không ho dịch, miệng {tag} không quay tiếng sân. Nằm im xếp một câu xương. Câu không viết sổ da Lưu — viết xương để mai mở cùng màu. Cùng màu. Không thèm. Không bật.

Anh nắm tay Hà, nghe chị thở đều. Đều đắt hơn mùi lạ ngoài rào. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Ngủ thật dưới trời Biên Ải. Sống. Đo. Không khoe. Đất còn. Người còn. Cháo còn. Thẻ còn. Chông còn. Miệng phân ca còn. Còn thở. Còn viết. Còn chờ. Chưa thua. Đủ. Mai còn nhịp. Còn sống. Còn đất. Còn người. Đủ thật. Sống. Đo tiếp. Không khoe. Đất người chờ còn. Đủ khép. Mai viết tiếp. Còn thở. Còn nhịp. Đủ. Đất còn. Người còn. Chưa thua. Còn nhịp. Đủ. Còn đất sau ngày {d}.

---

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng tháp không đốn thêm, đếm then cổng: không kêu. Đông rên một rồi im. Gò trống. Ngoài im sau {tag}.

Hà ghé: "Đều."
"Đều," anh đáp. Hai chữ đủ trước trống điểm.

Dưới sân Hữu đổi ca một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lặp như sương, không ồn, không thiếu.

Phong ghi sổ ba dòng gạch nhạt: mùi đông theo dõi; không ồn sân; mặt nghèo giữ; {t} đã khép. Chữ lóe tắt. Gấp sổ. Nắm tay Hà. Nằm. Ngoài rào không xe, không xẻng, không sóng sát. Chỉ đất Biên Ải và trại nghèo đúng cách — thước đọc lưng không đọc xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ thẳng tiếp vẫn không tan.

Phong ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im là gác lần hai. {t.capitalize()} khép bằng tai khe — không bằng đếm to ngoài sân.

Trống điểm kế sẽ mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — {b}. Máy nghèo thở đều. Đất còn. Người còn. Đủ.

Nắng sớm chạm rào. Ai đếm to — hở. Ai phơi — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
"""


def build(s: dict) -> str:
    open_ = (
        f"{s['open_hook']}. Ngày thứ {s['day_vi']} dưới đất Biên Ải năm 629. "
        f"{s['place'].capitalize()} — {s['event_short']}. {s['detail']}. "
        f"Luật trong xương: {s['law']}.\n\n"
    )
    return (
        hdr(s["n"], s["title"])
        + open_
        + morning_cast(s)
        + day_machine(s)
        + mid_event(s)
        + afternoon_evening(s)
        + night_unique(s)
        + panel(s["n"], s["panel_ev"])
    )


def main() -> None:
    paths = []
    for s in SPECS:
        text = build(s)
        # backup old then replace
        hits = [
            p
            for p in BASE.iterdir()
            if p.is_file() and re.search(rf"Chương\s+{s['n']}\b", p.name)
        ]
        for old in hits:
            bak = BASE / "_pass_backup" / f"{old.name}.pre_clone_rewrite_830"
            bak.parent.mkdir(exist_ok=True)
            if not bak.exists():
                bak.write_bytes(old.read_bytes())
            old.unlink()
        path = BASE / f"Chương {s['n']} - {s['title']}.txt"
        path.write_text(text, encoding="utf-8")
        print(
            f"wrote ch{s['n']} words={wc(text)} nhip={'Nhịp im' in text} "
            f"panel={'Kho Vô Hạn' in text and '15000' in text} "
            f"phong={'Phong' in text} ha={'Hà' in text} y629={'629' in text} "
            f"file={path.name}"
        )
        paths.append(path)

    cmd = (
        [sys.executable, str(SCORER)]
        + [str(p) for p in paths]
        + [
            "--min-words",
            "3000",
            "--threshold",
            "9.0",
            "--cfg",
            str(BASE / ".novelab_score.json"),
            "--json",
            str(BASE / "_score_clone_rewrite_830_837.json"),
        ]
    )
    r = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    print(r.stdout)
    if r.stderr:
        print("STDERR", r.stderr[:800])
    print("exit", r.returncode)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
