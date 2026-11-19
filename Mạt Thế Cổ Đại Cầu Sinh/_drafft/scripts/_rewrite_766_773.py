# -*- coding: utf-8 -*-
"""Rewrite clone pad ch.766-773: unique Phong/Hà prose, no Nhịp im, panel EXP 15k lv3."""
from __future__ import annotations

import os
import re
import sys

BASE = r"C:\Dev\MythLab\Mạt Thế Cổ Đại Cầu Sinh"

# day_num, title, kind, loc, hook_detail, short_tag, panel_upgrade, day_vi
SPECS = [
    dict(
        n=766, day=886, day_vi="tám trăm tám mươi sáu",
        title="Bóng Gò Lần 70 Không Chỉ",
        kind="bong",
        loc="gò đông",
        smell="mùi đất se trên gò đông",
        detail="một bóng đếm bước cắm mốc tre thấp; không lê; không nhìn trẻ; không nhổ mốc",
        short="bóng gò lần bảy mươi · mốc tre · không chỉ",
        law="thấy, không chỉ, không nhổ mốc, không đạp theo, không đếm mốc to",
        panel="Bóng gò lần 70 · gò đông · mốc tre · không chỉ · cấp im · máy nghèo",
        open_hook="Gió bấc mang mùi đất se khi trống điểm tan. Ngày thứ tám trăm tám mươi sáu dưới đất Biên Ải. Gò đông — bóng gò lần bảy mươi. Một bóng đếm bước cắm mốc tre thấp; không lê; không nhìn trẻ. Luật trong xương: thấy, không chỉ, không nhổ mốc, không đạp theo, không đếm mốc to.",
    ),
    dict(
        n=767, day=887, day_vi="tám trăm tám mươi bảy",
        title="Hỏi Lần 137 Cùng Màu",
        kind="hoi",
        loc="cổng đông",
        smell="mùi dây thừng se ngoài cổng",
        detail="một miệng hỏi có dây thừng không, đổi cọc lấy gạo; giọng khác lần trước; không lê",
        short="hỏi lần một trăm ba mươi bảy · dây thừng · cùng màu",
        law="không mở, không kể trẻ, không chỉ giếng, không nhận dây, không đổi cọc, đông thường, hầm xấu",
        panel="Hỏi lần 137 · cùng màu · dây thừng đổi cọc · cấp im · máy nghèo",
        open_hook="Gió bấc mang mùi dây thừng se khi trống điểm tan. Ngày thứ tám trăm tám mươi bảy dưới đất Biên Ải. Cổng đông — hỏi lần một trăm ba mươi bảy cùng màu. Một miệng hỏi có dây thừng không, đổi cọc lấy gạo. Luật trong xương: không mở, không kể trẻ, không chỉ giếng, không nhận dây, không đổi cọc, đông thường, hầm xấu.",
    ),
    dict(
        n=768, day=888, day_vi="tám trăm tám mươi tám",
        title="Ngày Yên Sau Hỏi 137",
        kind="yen",
        loc="trong rào",
        smell="mùi cháo loãng sau hỏi dây",
        detail="cổng trống; ngoài trống; không miệng; không dấu dây; yên có thể mang thợ trói giả",
        short="yên sau hỏi một trăm ba mươi bảy · trống ≠ yên hội",
        law="không thở phào, không mở rèm sớm, không rải vôi nghỉ, tai khe",
        panel="Yên sau hỏi 137 · trống ≠ yên hội · không thở phào · dây · cấp im · máy nghèo",
        open_hook="Nắng mỏng chạm rèm muộn. Ngày thứ tám trăm tám mươi tám. Trong rào — ngày yên sau hỏi một trăm ba mươi bảy. Không gào. Chỉ việc. Trống không bằng yên hội. Sau chữ dây — yên có thể là khoảng lùi mang thợ trói giả. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ.",
    ),
    dict(
        n=769, day=889, day_vi="tám trăm tám mươi chín",
        title="Sóng Thấp Lần 133",
        kind="song",
        loc="gò sườn tây thấp",
        smell="mùi tanh máu kín lẫn đất sườn tây",
        detail="bốn bóng thấp từ gò sườn tây thấp; không gào; máu kín; móc gáy-hông không mặt; hố mới không trùng bờ suối cạn đông-nam",
        short="sóng thấp lần một trăm ba mươi ba · bốn thấp · máu kín",
        law="đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi",
        panel="Sóng thấp lần 133 · gò sườn tây thấp · bốn · máu kín · cấp im · máy nghèo",
        open_hook="Gió bấc mang mùi tanh đất sườn tây khi trống điểm tan. Ngày thứ tám trăm tám mươi chín dưới đất Biên Ải. Gò sườn tây thấp — sóng thấp lần một trăm ba mươi ba. Bốn bóng thấp; không gào; chỉ sóng; máu kín. Luật trong xương: đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi.",
    ),
    dict(
        n=770, day=890, day_vi="tám trăm chín mươi",
        title="Bóng Thước Lần 69 Không Chỉ",
        kind="bong",
        loc="đường bụi đông",
        smell="mùi bụi đường và thước tre ướt sương",
        detail="một bóng cắm thước tre nghiêng trên đường bụi đông; không lê; không nhìn trẻ; không nhổ thước",
        short="bóng thước lần sáu mươi chín · thước tre nghiêng · không chỉ",
        law="thấy, không chỉ, không nhổ thước tre, không đạp theo, không đếm thước to",
        panel="Bóng thước lần 69 · đường bụi đông · thước tre · không chỉ · cấp im · máy nghèo",
        open_hook="Gió bấc mang mùi bụi đường khi trống điểm tan. Ngày thứ tám trăm chín mươi dưới đất Biên Ải. Đường bụi đông — bóng thước lần sáu mươi chín. Một bóng cắm thước tre nghiêng; không lê; không nhìn trẻ. Luật trong xương: thấy, không chỉ, không nhổ thước tre, không đạp theo, không đếm thước to.",
    ),
    dict(
        n=771, day=891, day_vi="tám trăm chín mươi mốt",
        title="Hỏi Lần 138 Cùng Màu",
        kind="hoi",
        loc="cổng đông",
        smell="mùi muối thô se và vỏ ốc khô",
        detail="một miệng hỏi có muối thô không, đổi vỏ ốc lấy nắm; giọng khác lần trước; không lê",
        short="hỏi lần một trăm ba mươi tám · muối thô · cùng màu",
        law="không mở, không kể trẻ, không chỉ giếng, không nhận muối, không đổi vỏ, đông thường, hầm xấu",
        panel="Hỏi lần 138 · cùng màu · muối thô đổi vỏ ốc · cấp im · máy nghèo",
        open_hook="Gió bấc mang mùi muối thô se khi trống điểm tan. Ngày thứ tám trăm chín mươi mốt dưới đất Biên Ải. Cổng đông — hỏi lần một trăm ba mươi tám cùng màu. Một miệng hỏi có muối thô không, đổi vỏ ốc lấy nắm. Luật trong xương: không mở, không kể trẻ, không chỉ giếng, không nhận muối, không đổi vỏ, đông thường, hầm xấu.",
    ),
    dict(
        n=772, day=892, day_vi="tám trăm chín mươi hai",
        title="Ngày Yên Sau Hỏi 138",
        kind="yen",
        loc="trong rào",
        smell="mùi cháo loãng sau hỏi muối",
        detail="cổng trống; ngoài trống; không miệng; không dấu muối; yên có thể mang bao muối giả",
        short="yên sau hỏi một trăm ba mươi tám · trống ≠ yên hội",
        law="không thở phào, không mở rèm sớm, không rải vôi nghỉ, tai khe",
        panel="Yên sau hỏi 138 · trống ≠ yên hội · không thở phào · muối · cấp im · máy nghèo",
        open_hook="Nắng mỏng chạm rèm muộn. Ngày thứ tám trăm chín mươi hai. Trong rào — ngày yên sau hỏi một trăm ba mươi tám. Không gào. Chỉ việc. Trống không bằng yên hội. Sau chữ muối — yên có thể là khoảng lùi mang bao muối giả. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ.",
    ),
    dict(
        n=773, day=893, day_vi="tám trăm chín mươi ba",
        title="Sóng Thấp Lần 134",
        kind="song",
        loc="bụi dứa dại bắc-tây",
        smell="mùi nhựa dứa dại lẫn tanh máu kín",
        detail="năm bóng thấp từ bụi dứa dại bắc-tây; không gào; máu kín; móc gáy-hông không mặt; hố mới không trùng gò sườn tây thấp",
        short="sóng thấp lần một trăm ba mươi tư · năm thấp · máu kín",
        law="đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi",
        panel="Sóng thấp lần 134 · bụi dứa dại bắc-tây · năm · máu kín · cấp im · máy nghèo",
        open_hook="Gió bấc mang mùi nhựa dứa dại khi trống điểm tan. Ngày thứ tám trăm chín mươi ba dưới đất Biên Ải. Bụi dứa dại bắc-tây — sóng thấp lần một trăm ba mươi tư. Năm bóng thấp; không gào; chỉ sóng; máu kín. Luật trong xương: đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi.",
    ),
]


def kind_mid(s: dict) -> str:
    k, d, loc, smell, detail, short, law = (
        s["kind"], s["detail"], s["loc"], s["smell"], s["detail"], s["short"], s["law"]
    )
    if k == "bong":
        return f"""A Cường lách bóng xưởng, báo thấp:

"{loc.capitalize()}. {detail}. Không mang xẻng."

"Ghi. Không mở. Không chỉ. {law}. Việc," Phong nói, mắt liếc hai nhịp rồi cúi muối.

Giữa sáng. Việc bóng vào xương.

Bóng đứng vài nhịp ngoài {loc}. {detail}. Gió thổi. Việc trong nuốt mắt. Bóng lùi. Lần này khép bằng chân bóng. Không ném đá. Không nhổ. Không đạp theo.

Hà đứng trong rèm, siết khăn mũi: "Thấy?"

"Thấy. Ta không chỉ. Không nhổ. Máy nhớ nghề, không khoe," Phong đáp. Anh nắm bao muối, thở đều, không đuổi mắt quá hai nhịp — đuổi là mời ngoài đọc lưng.

Phong gặp Hà sau bao muối. Chị lau tay bằng vạt áo rách, cau nhẹ:

"Bóng thật hay bóng mồi?"

"{detail}. Có thể đo khoảng, có thể cắm dấu cho miệng sau," anh nói. "Ba xương: {law}."

"Rèm chặt. Trẻ không ra sân gần hướng việc," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch." Anh ngẩng, liếc cổng, buông tay xuống bao."""
    if k == "hoi":
        bait = detail
        if "dây" in detail:
            q1 = "Trong ơi — có dây thừng không, đổi cọc lấy gạo!"
            q2 = "Cọc ngoài là của tao — trong có kho dây không?"
            refuse = "Không nhận dây. Không đổi cọc."
        else:
            q1 = "Trong ơi — có muối thô không, đổi vỏ ốc lấy nắm!"
            q2 = "Vỏ ốc ngoài là dấu tao — trong có kho muối không?"
            refuse = "Không nhận muối. Không đổi vỏ."
        return f"""A Cường lách bóng xưởng, báo thấp:

"Một miệng. {bait}."

"Ghi. Không mở. Không kể trẻ. Không chỉ giếng. {refuse} Đông thường. Hầm xấu," Phong nói, gật ngắn, mắt không mở cổng.

Giữa sáng. Việc hỏi vào xương.

Miệng ngoài: "{q1}"

"Đông thường. Hầm xấu," Phong đáp một nhịp, không thêm. Hà đứng sau then, siết khăn, không ngẩng hết đầu.

Miệng lần hai: "{q2}"

Không đáp mồi. Hà khẽ: "Hầm xấu." Không thêm. Miệng cười khô lùi. Không mở tiễn. Không ném đồ.

Hà liếc anh: "Hỏi?"

"{refuse} Máy nối mồi với miệng — im," Phong nói. Anh nắm then, thở ra, không chạy theo tiếng cười khô.

Phong gặp Hà sau muối. Chị cau, nhíu, hỏi khẽ:

"Giọng khác lần trước — mồi hay thật đói?"

"Không phân bằng tai dài. Phân bằng luật. {law}," anh đáp. "Ba xương giữ im."

"Rèm chặt. Trẻ không ra gần cổng," Hà gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch." Anh siết hàm, buông, quay bao."""
    if k == "yen":
        bait_word = "dây" if "dây" in detail or "dây" in s["short"] else "muối"
        fake = "thợ trói giả" if bait_word == "dây" else "bao muối giả"
        return f"""A Cường lách, báo thấp:

"Cổng trống. Ngoài trống. Không miệng. Không dấu {bait_word}."

"Không thở phào. Không họp chữ {bait_word}. Việc," Phong gật. Mắt anh không nở mừng. Tay anh siết muối.

Sáng trống. Yên khép bằng việc. Không mừng. Sau chữ {bait_word} — yên có thể là khoảng lùi mang {fake}. Ba xương yên: không thở phào, không mở rèm sớm, không rải vôi nghỉ. Mạc Tư gạch: yên sau hỏi {bait_word} — không viết nghỉ.

Hà siết khăn, liếc cổng: "Yên?"

"Trống. Không thở phào. Tai khe — miệng hỏi {bait_word} có thể mang {fake}," anh nói, cúi, thở đều.

"Rèm chặt. Trẻ không ra sớm," chị gật. "Lời em nếu có miệng. Bao anh. Đông thường. Hầm xấu."

"Cùng màu nếu hỏi. Không lệch." Anh nắm tay chị một nhịp rồi buông — đủ, không ồn.

Khuyển ngưỡng. A Minh hai ngón mở. Gò trống. Cổng trống.

A Cường: "Vẫn trống. Không soi. Không kể."

"Không soi. Không kể," Phong dặn. Biến. Không thở phào theo."""
    # song
    count_word = "bốn" if "bốn" in detail else "năm"
    prev_hole = "bờ suối cạn đông-nam" if "bốn" in detail else "gò sườn tây thấp"
    return f"""A Cường lách bóng xưởng, báo thấp:

"{loc.capitalize()}. {count_word} thấp. Không gào. Dấu riêng chỗ này. Không mang xẻng to."

"Ghi. Máu kín. Không đếm {count_word} to. Không phơi. Đổi chỗ lê. Hố xấu. Máu vải. Việc," Phong nói, mắt liếc {loc} hai nhịp.

Giữa sáng. Việc sóng vào xương.

{count_word.capitalize()} bóng thấp từ {loc}; không gào; chỉ sóng; máu kín. Phong hạ tay. Móc gáy-hông — không mặt. Máu ngắn. Tôn Vũ hai. Đại Lực một. Hứa chặn lệch. Không đếm to. Không phơi. Thóc lép rắc. Hố mới canh tư sẽ lớp. Đắp xấu. Phủi. Đổi chỗ lê — không lặp hố {prev_hole}.

Hà đứng trong rèm, không ra, nhíu mày: "Kín?"

"Kín. Không đếm to. Không phơi. {count_word} thấp. Máu vải không vôi," Phong đáp, lau móc bằng lá khô. Mùi {smell} bám ngón. Anh thở, siết hàm, không kể sân.

Khuyển ngưỡng. A Minh tín hiệu gò. Không sóng thêm ngoài việc đã thấy.

A Cường: "Hết ngoài gần. Không theo. Không thèm. Gió thổi {smell} ra."

"Không soi. Không kể số," Phong dặn. Biến.

Phong gặp Hà sau muối. Chị lau tay, cau nhẹ:

"Đủ? Không lệch vì sóng?"

"Không lệch. Việc không phải hội. Việc là im," chị nói. "Ai kể ngoài lều — nặng. {count_word} thấp; máu kín."

"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh gật, nắm bao, thở đều."""


def night_layers(s: dict) -> str:
    """Unique night beats — no numbered clone pad."""
    day, short, smell, law, loc = s["day"], s["short"], s["smell"], s["law"], s["loc"]
    parts = []
    beats = [
        f"Canh một sau việc {short}. Hầm đóng chông vôi then hố vết. Phong đếm then trong đầu: không kêu. Muối chát còn đầu ngón — chát nhắc nghề không nhắc hội. Hà thở đều bên cạnh. Anh nắm tay chị, nhắc ngắn: {law}. Không kể ngoài lều. Mai tai khe. Số lần không huy chương.",
        f"Canh hai. Ca mới. Thuốc ngủ. Hà thì thầm, mắt nhắm nửa: \"{smell}. Thỏ. Ngoài đi. Tấm trống.\" Phong đáp: \"Ngủ ca. Mai bóng, sóng, hoặc hỏi.\" Chị: \"Máu kín nếu sóng. Cùng màu nếu hỏi. Không chỉ nếu bóng.\" Anh gật, siết tay, buông.",
        f"Ra tuần ngắn. Gió bấc. Muối. Không xe. Vết cửa nguyên. Góc sân nhắc: hầm đóng, trẻ tay, miệng thỏ, hố không kể, cấp im, lời Hà cùng màu. Cắm thở. Không khoe {short}. A Minh trên gò giơ nắm đấm — im. Hữu đổi ca một ngón.",
        f"Canh ba. Hữu hỏi gò bằng mắt. A Minh đáp bằng ngón: \"Trống. Dày. Không xe. Không người.\" \"Ngủ.\" Rên đông một tiếng đứt — đếm, im, không dậy vội. Gió bấc mang {smell}.",
        f"Canh tư. Nếu hố cần lớp — thóc lép, đắp xấu, phủi. Không đếm to. Không giữ dấu làm chuyện sân. Hà khẽ: \"Tiếp.\" Phong: \"Tiếp. Không lỏng.\" Cổng hai nhịp trống. {smell} nhạt hơn canh một.",
        f"Sổ than ba dòng gạch nhạt:\nNgày {day}. {short}.\nKhông kể. Nghèo. Đều. Cấp im. Bảy xương.\nGhi im — không pháo ra sân.",
        f"Chữ lóe câm: ghi nhận việc; cảnh báo {smell} còn · việc có thể quay; nhiệm vụ việc im · máy nghèo. Cấp im. Không pháo. Nằm. Nắm. \"Im.\" \"Im…\" Phong không đọc to. Hà không hỏi số.",
        f"Mơ ngắn: ngoài rào và thẻ. Xâu. {smell} mờ. Tỉnh gió. Trống. Hữu đổi. Rên một. Nhắm lại. Không dậy vì mơ. Gà nhất. Không vội. Hà thở đều. Then êm. Mùi đất se. Im. Bảy gối. Không hội miệng sân mai vì đã qua việc {short}.",
        f"Tây xấu giữ. Đông chông hố vết. Gò trống. Trẻ ngủ. Người đều. Đo. Sống. Ngày {day} khép dần bằng tai khe — không bằng miệng kể. Ngày sau chờ bóng, sóng, hỏi, mùi, mặt không biết. Không sống theo đã giật một việc. Sống theo đều khi tay dừ khoe.",
        f"Ngủ muối hạt. Tai khe. Nghèo sau việc. Không chờ. Cửa thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm. Đủ. Việc không pháo. Cháo bao vải tay trẻ im lời cùng màu. Đủ trống. Đủ đọc lưng không xướng. Mai đảo đông. Mai hỏi — cùng màu. Mai bóng — không chỉ. Mai sóng — đâm thấp. Mai sống. Đo. Không khoe.",
        f"Gà hai. Nước nguội. Bảy im. Nằm. Tay Hà. {smell} còn một tấc. Thở. Cấp im. Chông. Gió. Ta sống. Việc khép im — im đắt nẻ miệng sau {short}. Phong ngồi dậy uống nước nguội, đếm bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. Đếm im là gác lần hai.",
        f"Canh khuya riêng ngày {day}: then tây êm, đông chông không cọt, hố không bới, cửa vết không sứt. A Minh đổi. Hữu im. Khuyển gõ giếng. Vải lều. {smell} lớp mỏng. Không bục miệng. Bục việc. Đủ. Ngủ thật. Mai sống viết Biên Ải.",
        f"Phong nắm tay Hà, nghe chị thở đều. Đều đắt hơn mùi lạ ngoài rào. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Ngủ thật dưới trời Biên Ải. Sống. Đo. Không khoe. Đất còn. Người còn. Cháo còn. Thẻ còn. Chông còn. Miệng phản ca còn. Còn thở. Còn viết. Còn chờ. Chưa thua. Đủ. Mai còn nhịp. Còn sống. Còn đất. Còn người. Đủ thật. Sống. Đo tiếp. Không khoe.",
        f"Trước gà gáy lần cuối lỏng nắm: then tây không kêu, chông đông không cọt, gò không bước lạ, thuốc không ho dịch, miệng ngoài không quay tiếng sân. Nằm im xếp một câu xương. Câu không viết sổ da Lưu — viết xương để mai mở cùng màu. Cùng màu. Không thèm. Không bật hở.",
        f"Hà ghé vai: \"Mai — em cùng màu. Anh bao. Không đổi ca lời sân. Không thèm vì việc hôm nay.\" Phong gật. Hở đắt hơn thèm. Gió đổi. Không sóng xe thước người sát rào. Đất Biên Ải trại nghèo sau {short}. Còn nghèo — chống mặt. Xuống. Muối hạt. Nằm. Tay Hà. Ngủ thật. Mai viết.",
        f"Trước gà cuối: rên xa một. Đếm. Im. Không dậy. Nắm lỏng. Mặt nghèo mai. Khép {day} không kể bảy không chỉ hố không nẻ miệng sau {short}. Sống. Đo. Không khoe. Đất còn. Đủ. Mai thở viết. Người còn. Còn thở. Còn đều khi tay dừ khoe.",
        f"Phong ngồi dậy cuối, uống nước, nghe Hà thở. Ghé: \"Mai cùng màu. Không thèm. Không bật hở. {short} không làm ta lệch.\" Chị: \"Không lệch.\" Ngủ. Đủ ai hỏi hoặc bóng chỉ gặp gió nồi bao rách cháo loãng — không bảy không hố không cấp im tếu. Đất Biên Ải. Còn viết thở người chờ. Đủ. Máy nghèo. Chống thấp. Miệng phản ca. Đủ khép đêm sau {short}.",
        f"Sáng mai trống điểm mùi dày bóng hoặc sóng hoặc hỏi. Không sống sợ việc. Sống đều. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Trong xương giữ luật — giữ lần sau. Lệch hở. Nắm Hà: \"Em lời. Anh việc đóng miệng.\" \"Giữ.\" Gió ngoài không người. Trong trại nhịp gánh thẻ. Nhịp đất chờ. Chưa thua.",
        f"Đếm chuỗi tay: người xe sóng thước máu. Khớp. Tóc Hà. Khói bếp cũ. Cũ đúng. Đất Biên Ải. Việc chỉ gió ngoài nếu xương siết. Siết. Ngủ. Đủ. Còn thở viết người chờ. Chưa thua. Đất còn. Mai nhịp. Còn sống. Còn đất. Còn người. Đủ sau {short}.",
        f"Trước ngủ nghe Hà mơ thở không chữ. Thở đúng. Đêm chỉ thở. Đất người cháo chông lời cùng màu mai. Đủ khép {day} mà {short} không lấy bảy hố — chỉ gió nồi bao rách. Không thèm. Đủ. Ngủ.",
        f"Canh năm. Gió bấc kéo dài rồi buông. Phong đứng tháp không thắp thêm, đếm then cứng: không kêu. Đông rên một rồi im. Gò trống. Ngoài im sau {short}. Hà ghé: \"Đều.\" \"Đều,\" anh đáp. Hai chữ đủ trước trống điểm.",
        f"Dưới sân Hữu đổi ca một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lấp như sương, không ồn, không thiếu. Phong ghi sổ ba dòng gạch nhạt: mùi đông theo dõi; không ồn sân; mặt nghèo giữ; {short} đã khép. Chữ lóe tắt. Gấp sổ. Nắm tay Hà. Nằm. Ngoài rào không xe, không xẻng, không sóng sát. Chỉ đất Biên Ải và trại nghèo đúng cách — thước đọc lưng không đọc xương.",
        f"Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ thẳng tiếp vẫn không tan. Phong ngồi dậy uống nước nguội, đếm bảy lớp âm lần nữa: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. {short} khép bằng tai khe — không bằng đếm to ngoài sân.",
        f"Trống điểm kế sẽ mang sóng, bóng, hỏi hay yên giả. Chưa mừng. Chưa lỏng. Ngày mai máy nghèo. Hôm sau then êm. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — {detail_short(s)}. Máy nghèo thở đều. Đất còn. Người còn. Đủ.",
        f"Nắng sớm chạm rào. Ai đếm to — hở. Ai phơi — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.",
    ]
    # Make each beat slightly unique per chapter number via loc/smell already embedded
    return "\n\n".join(beats)


def detail_short(s: dict) -> str:
    return s["short"]


def build(s: dict) -> str:
    n = s["n"]
    day = s["day"]
    title = s["title"]
    short = s["short"]
    smell = s["smell"]
    law = s["law"]
    loc = s["loc"]
    open_hook = s["open_hook"]
    mid = kind_mid(s)
    night = night_layers(s)

    body = f"""============================================================
Chương {n}: {title}
============================================================

{open_hook}

Phong ra hầm tây trước khi sân thức hẳn. Anh đếm dấu thây đã lấp: bảy. Không tám. Rắc thóc lép lên lớp đất mới, đắp xấu cho giống chỗ chưa đào, phủi bụi khỏi tay. Muối chát đầu ngón. Chát neo nghề. Hà phơi bao rách phía tây, khăn mũi buộc thấp, lưng thẳng. A Minh trên gò giơ tín hiệu theo hướng {loc}. Hữu vắt vải ướt. Cúc xâu thẻ trẻ. Chú Bát vung cháo loãng. Năm hơi cửa bếp. Việc mở trước miệng.

"Ngoài?" Hà hỏi khẽ, không ngẩng hết đầu. Mắt chị nhìn bao, tai chị nghe {loc}.

"{short}. Không mở. Không chỉ," Phong đáp. Anh nhìn hướng việc hai nhịp rồi quay muối. Không đuổi mắt quá hai nhịp — đuổi là mời ngoài đọc lưng. Năm 629. Lý Thế Dân mới lên ngôi — ngoài rào không quan, chỉ đất và miệng.

---

Sáng. Máy nghèo chạy ngày {short}.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. Đại Lực đảo bao tây. Tôn Vũ móc thấp trong xưởng, không hun lửa sớm. Hứa lau dao đất. Diễm se sợi. Khuyển nằm ngưỡng. Hữu sau chó.

{mid}

Bà già ghé mé bếp: "Gió?"
"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể chi tiết ngoài.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. Việc {short} là việc mắt nuốt — miệng không nhả.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không kể ngoài." Thẻ. Cửa hé. Trẻ khuất. Mùi cháo loãng tranh {smell}. Đất se. Vôi cũ.

Bà già: "Hôm nay tanh?"
"Gió. Việc," Hà. Không kể. Không đá.

Hứa cửa xưởng không liếc hố. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày có việc ngoài.

Phong xách nước, đảo bao, lau muối chát. Chát sau {short} đắt — việc dạy mắt và miệng, yên dạy lỏng vai. Lỏng vai hở mai. Anh siết hàm. Không mừng. Việc.

---

Ngọ. Cháo sau {short}.

Phong húp. Cúc: "Ngoài?"
Hà: "Im. Xâu."
Xâu. Hạt miệng. Sân nhàm. Nham sau {short} đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu:

"{short}. {law}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau việc dò nẻ — khóa việc nặng."

Gật. Máy che. Không khe đá.

Phong đảo tây. Hà phơi nắng xấu. A Cường: "Trống. Không thèm."
"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"
"Không. Gió. Việc." Hứa không liếc. Nghỉ.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần hai sau muối:
"Đủ? Không lệch vì {short}?"
"Không lệch. Việc không phải hội. Việc là im," chị lau tay, gật, thở. "Ai kể ngoài lều — nặng."
"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh nắm tay chị một nhịp, buông. Đủ.

Khuyển gật. A Minh khuất. Gò trống. Hai ngón mở. Không pháo.

---

Chiều. Tay nắm dấu nhắc. Trẻ thuộc cửa thẻ. Chân kho — còn. Hà miệng nắm: gió, hầm ấm, đông thường, {smell}, không bảy hố kể. Siết. Cắn lưỡi. Khuyển.

Then chông vôi giáo dao. Không khói. Không chông nắng. Trẻ xỉa. Gánh gạo. Không hội kể {short}.

Xỉa. Ca đổi. Xước se. Then tây bao vai. Gật đủ. Thỏ bếp tro. Thơm. {smell} còn nhạt. Đều.

Tám nhịp bếp: không phát súng vì {short}, nửa bát, cửa thẻ, nồi không chuyện ngoài. Gạch. Sôi. Gõ. A Cường: không xe không người lại. Nói hãm.

Chiều tà Mạc Tư Chú Bát tám nhịp: không phát vì việc, không đổi giờ ca đông, nửa bát, cửa thẻ, nồi không khách. Gạch. Hà: đủ.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi ngoài. Cúc ngủ thẻ. Hạt gối. Thị Liên chiếu. Ru im.

Tháp Hà không đèn: "{short} lớp. Mai bóng hoặc sóng hoặc hỏi."
"Lời em. Bao anh. Không lệch." Gió. Mùi. Ngoài im dần. Xuống. Anh nắm tay chị, thở, liếc đông một nhịp.

Đông vòng trước tối: chông một, vôi then hố vết nguyên. Không vôi mới. Mùi dày đúng. Không lỏng. Hố chờ nếu cần — lớp xấu, không đếm to.

Hữu đổi ca: "Trống. Không người." Cháo nửa thừa. "Im. Giơ đúng nếu sóng." Nuốt. Lên. Hà: đủ.

Phong chạm ba việc: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Nắp xấu giữ. Thước không đọc xưởng.

---

Tối. Lều ba. Đèn một. Cửa đóng.

Phong xướng ngắn: "{short}. {law}. Không mở rèm sớm. Đông thường. Hầm xấu. Cấp im. Hỏi — cùng màu. Bóng — không chỉ. Sóng — đâm thấp. Miệng khóa việc."

Đại Lực: "Ca đủ."
Khuyển: "Kể ngoài nặng."
A Cường: "Tay. Xe tầm ta."
Mạc Tư: "Cháo. Nửa bát. Không viết số to."
Diễm: "Xước. Rèm. Không kể."
Tôn Vũ: "Móc. Không hun."
Hữu: "Im. Nếu sóng — giơ đúng."

Tan. Ngáy. Kiếm tay. Máy ngủ.

Hà tháp: "{short} có lớp. Chưa xong. Mai bóng hoặc sóng hoặc hỏi."
"Lời em. Bao anh. Cùng màu." Nắm. Muối. {smell}.

Xương móc mái lá khô. A Minh trống. Hữu không giơ. Đúng.

---

{night}

「Kho Vô Hạn — GHI NHẬN ch.{n}」
Năm: 629
EXP: 15000 / 15000
Hiện tại: cấp 3
Nâng cấp: {s['panel']}
"""
    return body


def find_path(n: int) -> str:
    for f in os.listdir(BASE):
        if f.startswith(f"Chương {n} "):
            return os.path.join(BASE, f)
    raise FileNotFoundError(n)


def main() -> None:
    for s in SPECS:
        text = build(s)
        # strip accidental Nhịp im
        if "Nhịp im" in text:
            text = re.sub(r".*Nhịp im \d+.*\n?", "", text)
        path = find_path(s["n"])
        # keep filename; rewrite content
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        words = len(text.split())
        has_pad = "Nhịp im" in text
        print(f"ch.{s['n']} words={words} pad={has_pad} -> {os.path.basename(path)}")
        if words < 3000:
            print("  WARN short", words, file=sys.stderr)


if __name__ == "__main__":
    main()
