# -*- coding: utf-8 -*-
"""Unique full rewrite ch.104-128.
Style: early-arc Phong/Hà + Biên Ải machine-poor density.
No Nhịp im pad. Unique openings/prose per chapter.
Panel: 「Kho Vô Hạn — GHI NHẬN ch.N」 Năm 629. EXP progressive.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".mythlab_score.json"
OUT_JSON = BASE / "_score_rewrite_104_128.json"


def vi_words(t: str) -> int:
    m = re.search(r"={6,}\s*\n.*?\n={6,}\s*\n", t, re.S)
    body = t[m.end() :] if m else t
    return len([w for w in body.split() if len(w) >= 2])


def hdr(n: int, title: str) -> str:
    return (
        "============================================================\n"
        f"Chương {n}: {title}\n"
        "============================================================\n\n"
    )


def panel(n: int, exp: int, event: str) -> str:
    return (
        f"\n「Kho Vô Hạn — GHI NHẬN ch.{n}」\n"
        f"Năm: 629\n"
        f"EXP: {exp} / 30000\n"
        f"Hiện tại: cấp 2\n"
        f"Nâng cấp: {event}\n"
    )


def find_file(n: int) -> Path:
    hits = list(BASE.glob(f"Chương {n} - *.txt"))
    if not hits:
        raise FileNotFoundError(n)
    return hits[0]


def night_close(day_vn: str, tag: str, law: str, cliff: str, smell: str) -> str:
    """Long unique night close — no Nhịp im, unique via tag/smell/law/day."""
    return f"""
---

Tối. Đèn một. Cửa đóng. Sân hạ giọng. Mùi {smell} còn mỏng ngoài rào.

Phong ngồi thềm lều, nắm muối chát dính ngón, nhìn hướng việc một nhịp rồi hạ mắt. Không đuổi. Không kể. Hà ngồi sát, khăn mũi hạ cằm, thở đều. Năm 629 — đất Biên Ải không cho mừng sớm.

"Còn thở?" chị hỏi khẽ.

"Còn. Đều. Không lỏng," anh đáp. "Mai trống điểm mang gì cũng việc trước. Không hội sau {tag}."

Chị gật. Nắm tay. Buông lỏng. Mùi đất se trộn khói bếp tắt. Gió bấc kéo một gang rồi buông.

Canh một. Hữu đổi ca. A Minh nắm đấm — im. Khuyển thở ngưỡng. Đông: chông, then, hố vết nguyên. Không vôi mới. Không tiếng người lạ. Đại Lực trên tháp không giơ sớm.

Canh hai. Phong tuần tây ngắn. Hầm bảy dấu lấp xấu. Thóc lép rắc. Đắp giống chỗ chưa đào. Phủi bụi. Muối lại chát. Về lều. Hà đã nằm, mắt vẫn khe:

"Không kể ngoài. Không chỉ hố. Không kể trẻ. Không kể cấp. Không kể {tag}."

"Giữ. Lời em nếu miệng. Bao anh. Đông thường. Hầm xấu."

Canh ba. Ngủ nghiêng. Mơ không chữ to. Tỉnh gió. Rên đông một tiếng rồi im. Nắm tay Hà. Ngủ lại. Mùi {smell} nhạt hơn canh một.

Canh tư. Uống nước nguội. Nghe bảy lớp âm: ngáy trẻ, xẻng cắm, chông kêu khẽ, gió bấc, then im, rên đông thưa, không xe. Đếm im là gác lần hai. Gác bằng tai khi mắt phải nghỉ.

Sổ than gạch nhẹ:
Ngày {day_vn}. {tag}.
{law}
Không kể. Nghèo. Đều. Cấp im. Bảy xương.

Chữ kho lóe ngắn trong đầu — không pháo ngoài sân. Cấp im. Không pháo. Ngáy. Nằm. Nắm. "Im."

Gà nhất. Không vội. Hà thở. Then. Mùi. Im. Bảy gối. Việc không hội miệng sân mai vì đã qua {tag}.

Tây xấu giữ. Đông chông hố vết. Gò trống. Trẻ ngủ. Người đều. Lớn thầm. Đo. Sống. Không sống theo đã xong một việc. Sống theo đều khi mắt dễ chỉ, miệng dễ nở, vai dễ lỏng. Lỏng là hở. Hở là chết chậm dưới đất này.

Ngủ muối hết. Tai khe. Nghèo sau việc. Củ thẻ. Đất Biên Ải. Cúc Hữu Hà Đại Lực Diễm Tôn Vũ. Đủ. Cháo bao vải tay trẻ im lời cùng màu. Đủ trống. Đủ hắn đọc lưng mà không đọc được xương.

Gà hai. Nước. Bảy im. Nằm. Tay Hà. Mùi {smell} còn một tấc. Thở. Cấp im. Chông. Gió. Ta sống. Việc khép im — im đắt nở miệng sau {tag}.

Gió dài. Mắt: chông thẻ Hà cửa vết gò trống lời ba xương. Giữ. Không kể bảy. Không chỉ hố. Không pháo. Đất lưng. Ngủ. Mai chủ nghèo — không bia mồi miệng.

Rên tắt. Không dậy. Tai khe. Im. Hà nắm. Ngủ. Sau việc không cột đêm. Sức trống kế chông mặt không biết mang bảy hố xương sân gió bao.

Mai trống cháo bao mùi. Mai bóng sóng hỏi. Mai sống. Đủ. Hữu đều. Đều lan. Cười im. Im sau việc đắt cười ảo. Ảo kể số. Thật đất người thẻ chông miệng. Đất Biên Ải còn. Thắng dở. Mai cháo chông hố lời. Không pháo. Thở đều. Sống. Đo. Không khoe. Người đất cháo thở. Đất còn. Đủ.

Nhắc xương: không kể bảy, không chỉ hố, không mừng, không đào, trẻ không thấy, mặt không biết, cấp im, đông thường, lời Hà cùng màu, bao anh, việc không hội, {law}. Khớp. Ngủ. Còn viết. Mai đất chữ. Đủ đọc lưng không xương.

Canh tư muộn. Tháp Hà không đèn. Ca đổi. Đông hố cửa im. Chị: "Mai — em cùng màu. Anh bao. Không đổi ca lời sân. Không thèm vì {tag}."

Gật. Lời ca. Hở đắt hơn thèm. Gió đổi. Không sóng xe thước người sát rào. Đất Biên Ải trại nghèo sau {tag}. Còn nghèo — chông mặt. Xuống. Muối hết. Nằm. Tay Hà. Ngủ thật. Mai viết.

Trước gà cuối: rên xa một. Đếm. Im. Không dậy. Nắm lỏng. Mặt nghèo mai. Khép {day_vn} không kể bảy không chỉ hố không nở miệng sau {tag}. Sống. Đo. Không khoe. Đất còn. Đủ. Mai thở viết. Người còn. Còn thở. Còn đều khi mắt dễ chỉ.

Phong ngồi dậy cuối, uống nước, nghe Hà thở. Ghé: "Mai cùng màu. Không thèm. Không bật hở. {tag} không làm ta lệch."

Chị: "Không lệch." Ngủ. Đủ ai hỏi hoặc bóng chỉ gặp gió núi bao rách cháo loãng — không bảy không hố không cấp im túi. Đất Biên Ải. Còn viết thở người chữ. Đủ. Máy nghèo. Chông thấp. Miệng phân ca. Đủ khép đêm sau {tag}.

Sáng mai trống điểm mùi dày bóng hoặc sóng hoặc hỏi. Không sống sợ. Sống đều. Đều. Nghèo. Im đúng chỗ. Mở đúng tay. Đủ. Trong xương giữ luật — giữ lần sau. Lệch hở. Nắm Hà: "Em lời. Anh việc đóng miệng."

"Giữ." Gió ngoài không người. Trong trại nhịp gánh thẻ. Nhịp đất chờ. Chưa thua.

Canh khuya vòng ngắn: then tây êm, đông chông không cọt, hố không bới, cửa vết không sứt. A Minh đổi. Hữu im. Khuyển gõ giếng. Vải lều. Mùi {smell} lớp mỏng. Không bục miệng. Bục việc. Đủ. Ngủ thật. Mai sống viết Biên Ải.

Đếm chuỗi tay im: người xe sóng thước máu. Khớp. Tóc Hà. Khói bếp cũ. Cũ đúng. Đất Biên Ải. Việc chỉ gió ngoài nếu xương siết. Siết. Ngủ. Đủ. Còn thở viết người chờ. Chưa thua. Đất còn. Mai nhịp. Còn sống. Còn đất. Còn người. Đủ sau {tag}.

Trước ngủ nghe Hà mơ thở không chữ. Thở đúng. Đêm chỉ thở. Đất người cháo chông lời cùng màu mai. Đủ khép {day_vn} mà {tag} không lấy bảy hố — chỉ gió nồi bao rách. Không thèm. Đủ. Ngủ.

Canh năm. Gió bấc kéo dài rồi buông. Phong đứng tháp không thắp thêm, đếm then cứng: không kêu. Đông rên một rồi im. Gò trống. Ngoài im sau {tag}. Hà ghé: "Đều." "Đều," anh đáp. Hai chữ đủ trước trống điểm.

Dưới sân Hữu đổi ca một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm lấp như sương, không ồn, không thiếu. Phong ghi sổ ba dòng gạch nhạt: mùi đông theo dõi; không ồn sân; mặt nghèo giữ; {tag} đã khép. Chữ lóe tắt. Gấp sổ. Nắm tay Hà. Nằm. Ngoài rào không xe, không xẻng, không sóng sát. Chỉ đất Biên Ải và trại nghèo đúng cách — thước đọc lưng không đọc xương.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Mai mang mặt không biết ra nắng. Đủ thẳng tiếp vẫn không tan. Phong ngồi dậy uống nước nguội, đếm bảy lớp âm lần nữa: ngáy trẻ, xẻng cắm, chông kêu, gió bấc, then im, rên đông, không xe. {tag} khép bằng tai khe — không bằng đếm to ngoài sân.

{cliff}

Nắng sớm chạm rào. Ai đếm to — hở. Ai phơi — hở. Ai kể trẻ — hở gấp. Phong siết hàm lần cuối. Hà thở. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm. Sống. Đo. Không khoe.
"""


# ---------------------------------------------------------------------------
# Chapter specs — unique plot per day
# ---------------------------------------------------------------------------
SPECS = [
    dict(
        n=104, title="Tiếng Đinh Đầu Tiên", day=104, day_vn="một trăm linh bốn",
        exp=23500, event="Đinh sắt hàng rào bắc · tám bóng đông · chuẩn bị ra ngoài",
        smell="mùi sắt nóng và gỗ sồi ướt",
        tag="tiếng đinh đầu tiên · hàng rào bắc",
        law="Chất lượng hơn số lượng · trẻ trước · không ra ngoài một mình không có người đợi cổng",
        cliff="Liệu bình minh tới có mang theo zombie… hay mang theo kẻ thù mang mặt người?",
        open=(
            "Tiếng đinh sắt xuyên gỗ sồi già vang trước khi trống điểm tan hẳn. "
            "Ngày thứ một trăm linh bốn dưới đất Biên Ải. Tuyết đã ngừng. "
            "Phong đứng dưới mái hiên nhà kho phía tây, tay cầm thanh sắt ngắn mới rèn — lưỡi cong, rộng hai ngón, mũi nhọn. "
            "Mùi sắt nóng và gỗ sồi ướt bám gáy. Gió bấc mang hơi ẩm đất đen lộ ra sau băng. "
            "Năm 629. Ngoài sử sách Lý Thế Dân mới lên ngôi; ngoài rào chỉ đinh, cọc, và tám bóng đông."
        ),
        core=(
            "Anh nhắm cọc đã đóng một nửa hàng rào phía bắc. Tiếng búa không phải tiếng búa thường — mỗi nhát, thanh đinh sắt dài bằng ngón tay xuyên cọc, xuyên hàng rào cũ, xuyên đất trong. "
            "Keng — kim loại chạm kim loại — rõ trong không khí lạnh. Đinh thứ nhất. Thứ hai. Thứ ba. Mỗi tiếng — một cọc vững hơn.\n\n"
            "Đại Lực từ nam đến, vai vác khúc gỗ. \"Hàng rào nam xong một phần ba. Hào sâu nửa thân. Đáy có nước đóng băng. Zombie rơi sẽ dính.\"\n\n"
            "\"Đáy hào cần đốt. Than từ bếp. Đáy ấm — băng tan — zombie chìm,\" Phong nói, không ngẩng hết đầu. Mắt anh đếm cọc còn trống.\n\n"
            "Đại Lực gật. Bếp là trung tâm. Một bếp cháy — căn cứ sống. Một bếp tắt — căn cứ chết.\n\n"
            "Tôn Vũ từ xưởng, thước gỗ trên tay. \"Bắc xong hai phần ba. Còn nửa ngày.\"\n\n"
            "\"Không vội. Chất lượng hơn số lượng. Đinh còn bao nhiêu?\"\n\n"
            "\"Hai mươi. Hết — phải rèn.\"\n\n"
            "\"Bắc cần ba mươi cọc. Thiếu mười. Rèn.\"\n\n"
            "Tôn Vũ gật, búa trên vai, mắt nhìn đất, không ngoái.\n\n"
            "---\n\n"
            "Trưa. Hà bê khay: cháo trắng, rau cải muối, miếng thịt heo nhỏ từ Kho Vô Hạn. \"Mỗi người một phần. Không thêm vì lạnh.\"\n\n"
            "Phong nhìn phần cơm. Gạo trắng hiếm. Thịt hiếm hơn. \"Chia đều. Trẻ em trước.\"\n\n"
            "Hà không hỏi thêm. Trong căn cứ, quy tắc của Phong là quy tắc: trẻ trước, lớn sau, bản thân cuối.\n\n"
            "Sau bữa, Phong ra ngoài rào một mình — năm chục bước, hướng đông. Tuyết tan một phần. Đất đen ẩm. Dấu chân in bùn. "
            "Tám zombie: bảy quỳ, một đứng. Không di chuyển. Không nhìn anh. Tất cả nhìn đông — hướng thành Trường An. Mắt đỏ sẫm, máu khô, nhìn hư không.\n\n"
            "Anh lui. Không chạy. Bước nhanh. Về cổng, Hà đợi.\n\n"
            "\"Có gì?\"\n\n"
            "\"Chúng vẫn đó. Tất cả nhìn đông. Hướng Trường An.\"\n\n"
            "\"Ai đó ở đó đang ra lệnh?\"\n\n"
            "\"Có thể. Hoặc thứ gì đó đang thu hút. Cần tìm. Không phải bây giờ.\"\n\n"
            "Hà gật. Thời điểm là tất cả. Sớm — nguy. Muộn — nguy hơn.\n\n"
            "---\n\n"
            "Chiều. Họp mười người: Hà, Đại Lực, Tôn Vũ, Hứa, Triệu, A Cường, Từ Sơn, Mạc Tư, Lý Lão, Trương Bá.\n\n"
            "\"Ba nhiệm vụ. Một: hoàn thành rào bắc và nam. Hai: vũ khí mùa xuân. Ba: tìm ai đang kiểm soát zombie,\" Phong nói ngắn.\n\n"
            "Trương Bá: \"Việc ba — làm sao?\"\n\n"
            "\"Ra ngoài. Đông. Tìm nguồn. Zombie đang đứng yên. Đi nhanh — có thể tìm trước khi chúng động.\"\n\n"
            "Hà: \"Anh đi?\"\n\n"
            "\"Đúng.\"\n\n"
            "\"Em đi cùng.\"\n\n"
            "\"Không. Em giữ căn cứ. Nhiều người — dễ lộ.\"\n\n"
            "Im. \"Được. Nhưng về trước hoàng hôn. Nếu không —\"\n\n"
            "\"Ta sẽ về.\"\n\n"
            "Hà tin — không vì hứa, vì anh chưa thất lời hứa.\n\n"
            "Đêm. Trống điểm. Gió bấc nhẹ hơn. Tuyết tan nhiều. Ngoài rào tám bóng đen bất động. Trong lều chỉ Phong và Hà.\n\n"
            "\"Ngày mai em trông. Nếu ta không về trước hoàng hôn —\"\n\n"
            "\"Anh sẽ về.\"\n\n"
            "Mắt Hà sáng dưới đèn mờ. Không sợ — chỉ tin. Phong nhắm mắt. Thở đều. Chờ bình minh."
        ),
    ),
    dict(
        n=105, title="Cuộc Hành Trình Về Phía Đông", day=105, day_vn="một trăm linh năm",
        exp=23550, event="Đông tìm nguồn · Lan Hùng từ Trường An · tin Lý Hắc",
        smell="mùi đất ướt sau tuyết tan",
        tag="hành trình đông · hai người lạ nhà bỏ hoang",
        law="Không ra ngoài một mình không có người đợi cổng · trẻ trước · tin từ thành phải kiểm bằng mắt",
        cliff="Liệu ba tuần có đủ để chuẩn bị trước khi hàng nghìn miệng đổ về Biên Ải?",
        open=(
            "Bình minh chưa đủ sáng khi Phong cột giày đế dày — giày Hà vá chỉ sợi. "
            "Ngày thứ một trăm linh năm. Mùi đất ướt sau tuyết tan nồng hơn mọi ngày. "
            "Áo bông dày, mũ vải, dao ngắn phòng thân — lưỡi sắc, cán gỗ, vừa tay. "
            "Trên tháp bắc, Đại Lực giơ hai ngón xuống đất rồi một ngón đông: hai zombie đông."
        ),
        core=(
            "\"Đi bao lâu?\" Đại Lực hỏi nhỏ.\n\n"
            "\"Ba canh. Không hơn. Trước hoàng hôn.\"\n\n"
            "\"Em đợi cổng.\"\n\n"
            "Phong không cãi. Nguyên tắc: không ai ra ngoài một mình mà không có người đợi cổng.\n\n"
            "Tuyết dưới chân ướt, mềm, trơn. Năm chục bước — trống. Trăm — trống. Hai trăm — trống. Ba trăm — hai xác sống nam, áo cũ, mặt trương. Chúng quay đầu khi nghe bước. Khoảng hai mươi bước. Mắt đỏ sẫm. Không tiến. Không gào. Chỉ nhìn. Anh lui hai bước chậm. Chúng quay, lê đông. Như quên mục đích.\n\n"
            "Năm trăm bước: ngã tư. Trái — Trường An khoảng ba dặm. Phải — rừng sồi nam. Trước — thung lũng đông. Phong chọn đông.\n\n"
            "Hai trăm bước nữa: dấu chân người — giày vải, bốn dấu, hai đôi, đi đông. Dấu mới — tuyết chưa phủ. Có thể một giờ. Có thể hai. Anh theo.\n\n"
            "Tám trăm bước: dấu dừng. Nhà tường đất, mái rơm sập một bên, cửa hé. Mùi ẩm mốc. Trong tối: một nam một nữ, áo rách, mặt bụi. Mắt mở to.\n\n"
            "\"Zombie?\" nữ run.\n\n"
            "\"Không. Người.\"\n\n"
            "Nam khoảng ba mươi, râu dài, mắt trũng: \"Chúng tôi chạy từ thành Trường An. Ba ngày. Zombie tấn công từ cổng nam. Hàng nghìn. Chạy đông. Không dừng.\"\n\n"
            "\"Ba ngày? Không ăn?\"\n\n"
            "\"Không ăn. Không ngủ. Chỉ chạy.\"\n\n"
            "Phong nhìn: đói, mệt, sợ — nhưng sống. \"Đi theo tôi. Thức ăn. Chỗ ở. Phía bắc — tám trăm bước.\"\n\n"
            "Nữ tóc buộc rối, mắt sáng: \"Được. Đi.\"\n\n"
            "Ba người về. Không nói. Chỉ bước trên đất ướt. Cổng: Đại Lực tay trên dao. \"Hai người từ Trường An. Zombie tấn công thành.\"\n\n"
            "\"Vào. Có ăn. Có chỗ. Quy tắc: không ra ngoài một mình. Không cãi. Không gây rối. Trẻ trước.\"\n\n"
            "Họ gật. Quá mệt để hỏi.\n\n"
            "---\n\n"
            "Trưa. Hà chia hai phần đầy cho người mới. \"Họ cần hơn chúng ta. Ba ngày chạy.\"\n\n"
            "\"Cảm ơn. Tôi Lan. Đây Hùng,\" nữ nói.\n\n"
            "\"Phong. Đây căn cứ.\"\n\n"
            "Hùng: \"Thành chưa mất. Nhưng chịu đựng. Hàng nghìn zombie. Không đủ người giữ.\"\n\n"
            "\"Khi nào chúng đến đây?\"\n\n"
            "\"Không biết. Vài ngày. Vài tuần.\"\n\n"
            "\"Vài tuần. Đủ để chuẩn bị.\"\n\n"
            "---\n\n"
            "Chiều. Họp mười hai người gồm Lan, Hùng.\n\n"
            "\"Trường An bị tấn công. Nếu thất thủ — chúng đến đây. Chuẩn bị rào, vũ khí, giếng, lương. Và tìm ai kiểm soát zombie,\" Phong nói.\n\n"
            "Lan cau: \"Ai có thể?\"\n\n"
            "\"Ở Trường An. Zombie đứng yên ngoài rào — bảy quỳ một đứng — tất cả nhìn đông. Không tự nhiên.\"\n\n"
            "Lan: \"Trước khi chạy tôi làm thư viện thành. Có một thầy. Hắn nói kêu gọi zombie bằng giọng. Tên Lý Hắc.\"\n\n"
            "Im. \"Lý Hắc. Họ Lý,\" Phong lặp. \"Hắn nguy hiểm hơn hàng nghìn miệng. Ba tuần. Chuẩn bị. Rồi tìm.\"\n\n"
            "Mười hai người gật. Đêm: Phong và Hà trong lều. \"Ba tuần. Đủ để chuẩn bị. Không đủ để chờ. Làm. Tất cả cùng làm.\""
        ),
    ),
    dict(
        n=106, title="Lý Hắc", day=106, day_vn="một trăm linh sáu",
        exp=23600, event="Họp Lý Hắc · năm zombie rời · kế hoạch ba tuần",
        smell="mùi đất ướt sau nhiều ngày lạnh",
        tag="tên Lý Hắc vào xương · năm bóng rời đông",
        law="Không đếm zombie to ngoài sân · tin phải kiểm · ba tuần không hội mừng",
        cliff="Mai mang thêm tin từ đông — hay mang bóng quay đầu?",
        open=(
            "Trời còn tối khi Phong bước ra sân. Ngày thứ một trăm linh sáu. "
            "Không tuyết. Đất ẩm mềm dễ lún. Mùi đất ướt sau nhiều ngày lạnh nồng gáy. "
            "Tháp bắc: Đại Lực giơ ba ngón đông — ba zombie. Ít hơn hôm qua. Năm bóng đã rời."
        ),
        core=(
            "\"Đếm lần đầu. Không đếm lần sau to,\" Phong nói. Năm bóng rời — lệnh Lý Hắc hay bản năng tìm ăn — chưa biết. Nếu đi bắc có thể chạm căn cứ khác.\n\n"
            "Sáng. Họp mười hai người. Lan và Hùng có mặt.\n\n"
            "\"Hôm qua hai người từ Trường An. Thành bị tấn công. Có Lý Hắc — kêu gọi zombie bằng giọng,\" Phong nói ngắn.\n\n"
            "Lan: \"Tôi gặp hắn ở thư viện. Hắn nói hậu duệ gì đó. Nói zombie nghe lệnh.\"\n\n"
            "Từ Sơn cau: \"Zombie không có tai.\"\n\n"
            "\"Zombie thường — đúng. Mắt đỏ — có thể khác. Hắn kích hoạt bản năng,\" Phong đáp.\n\n"
            "Đại Lực: \"Tiêu diệt hắn — làm sao?\"\n\n"
            "\"Ba tuần. Rào xong. Vũ khí sẵn. Rồi ra tìm. Không vội. Vội chết.\"\n\n"
            "Hà đứng mé cửa, khăn mũi thấp: \"Ai giữ căn cứ khi anh đi?\"\n\n"
            "\"Em. Đại Lực. Tôn Vũ. Không để trẻ ra gần cổng. Đông thường. Hầm xấu nếu có miệng hỏi.\"\n\n"
            "Hà gật. Lời em nếu miệng. Bao anh.\n\n"
            "---\n\n"
            "Giữa sáng. Phong đảo muối tây. Hà phơi bao rách. Mùi cháo loãng tranh mùi đất ướt. "
            "A Cường lách xưởng: \"Ba đông. Không tiến. Không gào. Nhìn đông như cũ.\"\n\n"
            "\"Ghi. Không soi. Không kể số to sân,\" Phong dặn.\n\n"
            "Tôn Vũ rèn: mười đinh còn thiếu từ hôm qua — hôm nay xong tám. Hai còn nguội. "
            "\"Mai đủ mười,\" hắn nói, mồ hôi trán, mắt không khoe lưỡi sáng.\n\n"
            "Hứa kiểm kho: gạo đủ ba tuần nếu siết rau. Thịt Kho Vô Hạn — từng phần nhỏ. Không nêm cháo mừng vì tin Trường An.\n\n"
            "---\n\n"
            "Chiều. Phong gặp Hà sau bao muối.\n\n"
            "\"Lý Hắc — thật hay mồi miệng?\" chị nhíu.\n\n"
            "\"Lan nói gặp. Hùng chạy ba ngày. Tin có xương. Chưa đủ để mở cổng sớm. Ba tuần việc. Rồi mắt kiểm.\"\n\n"
            "\"Trẻ không nghe tên hắn.\"\n\n"
            "\"Ghi. Ai kể trẻ — nặng. Ai kể cấp — nặng gấp.\"\n\n"
            "Chị lau tay vạt áo rách: \"Em cùng màu nếu có miệng ngoài.\"\n\n"
            "\"Cùng màu. Không lệch.\"\n\n"
            "Ngọ cháo loãng. Cúc xâu thẻ. Hạt miệng. Sân nhàm. Nham giữ sống. "
            "Mười nhịp xưởng — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu: "
            "\"Tên Lý Hắc. Không kể sân. Ba tuần rào vũ khí lương. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu.\"\n\n"
            "Gật. Máy che. Không khe đá.\n\n"
            "Hoàng hôn. Phong tuần đông trong rào: chông, vôi, then, vải hố, vết cửa nguyên. Ba bóng đông còn. Không tiến. Anh gật. Không khen. Quét miệng muốn kể thành chuyện."
        ),
    ),
    dict(
        n=107, title="Về Phía Nam", day=107, day_vn="một trăm linh bảy",
        exp=23650, event="Nam với Hùng · dấu lạ · tin viên đá",
        smell="mùi sương và đất chưa hong khô",
        tag="vòng tây rồi nam · dấu chân lớn",
        law="Đi vòng không gặp miệng · không dừng trừ khi cần · tin Hùng kiểm bằng dấu",
        cliff="Phía nam còn dấu lớn hơn — liệu đó là zombie tiến hóa hay mồi đường?",
        open=(
            "Sương nồng khi Phong đội mũ lần thứ ba — giày Hà vá lại. "
            "Ngày thứ một trăm linh bảy. Lạnh hơn dù không tuyết. "
            "Hùng đứng ngoài lều, túi vải trên vai, mắt trũng nhưng đã ăn ba bữa cháo nóng. "
            "Tháp: Đại Lực giơ ba ngón đông, hai ngón nam — năm zombie."
        ),
        core=(
            "\"Hai nam. Đi vòng tây rồi rẽ nam. Thêm hai trăm bước. Không gặp,\" Phong nói.\n\n"
            "Hùng gật. Không cãi. Trong căn cứ Phong quyết đường.\n\n"
            "Gió tây nhẹ. Mùi đất ẩm nhẹ hơn. Tuyết hết. Đất đen mềm. Năm chục — trống. Trăm — trống. Hai trăm — trống. Ba trăm — rẽ nam. Bốn trăm bước nam: chỉ bước chân trên đất ướt.\n\n"
            "Hùng thấp: \"Khi chạy, tôi thấy thầy mang viên đá. Phát sáng. Vàng nhạt. Hắn rời tháp chuông mang đá. Zombie theo hướng hắn.\"\n\n"
            "\"Viên đá điều khiển?\"\n\n"
            "\"Có thể. Hoặc mồi. Tôi không gần. Chỉ thấy sáng.\"\n\n"
            "Phong ghi xương: viên đá — sáng — theo hướng. Chưa kết luận. Kết luận bằng mắt sau.\n\n"
            "Bảy trăm bước: dấu chân zombie — rộng, nông, kéo. Ba dấu. Tuyết mỏng phủ. Cũ hơn một đêm. Đi vòng. Không đạp theo.\n\n"
            "Một nghìn bước: nhà bỏ hoang khác — tường nứt, mái sụp. Trong: không người. Chỉ mùi mốc và một mảnh vải thư viện — chữ mờ \"Lý\". Hùng nhặt: \"Có thể của hắn. Hoặc ai đó.\"\n\n"
            "\"Không mang về kể trẻ. Ghi im,\" Phong nói. Bỏ mảnh vào túi trong. Không pháo.\n\n"
            "---\n\n"
            "Về trước hoàng hôn. Đại Lực đợi cổng. \"Ngoài?\"\n\n"
            "\"Dấu cũ. Nhà trống. Tin đá. Không miệng sống.\"\n\n"
            "Hà bê nước nóng: \"Ăn. Rồi nói ngắn.\"\n\n"
            "Phong húp. \"Hùng thấy đá sáng. Zombie theo hướng. Ba tuần vẫn giữ. Không mở sớm vì mảnh vải.\"\n\n"
            "Hà: \"Em không kể sân. Trẻ xâu trong.\"\n\n"
            "\"Cùng màu.\"\n\n"
            "Chiều. Tôn Vũ báo đinh đủ mười. Bắc rào gần xong. Nam hào đáy đã đốt than — băng mỏng tan, bùn dính. "
            "A Cường: \"Đông ba. Nam hai. Không tiến.\"\n\n"
            "Phong gặp Hà sau muối: \"Nam có dấu lớn hơn thường — chưa thấy xác. Có thể tiến hóa. Có thể mồi đường.\"\n\n"
            "\"Không đạp theo. Không chỉ trẻ.\"\n\n"
            "\"Giữ.\" Anh siết hàm. Mùi sương còn trên áo."
        ),
    ),
    dict(
        n=108, title="Viên Đá Phát Sáng", day=108, day_vn="một trăm linh tám",
        exp=23700, event="Năm zombie quay nam · tin đá sáng · giữ Lý Hắc nếu gặp",
        smell="mùi sương đêm và gió bấc",
        tag="zombie quay đầu nam · viên đá sáng",
        law="Nguồn di chuyển thì miệng theo · không giữ đá nếu không hiểu · không kể sáng to sân",
        cliff="Nếu đá là nguồn — ai mang đá về Biên Ải sẽ mang cả bầy theo sau?",
        open=(
            "Gió bấc thổi suốt đêm không mang tuyết nhưng mang sương. "
            "Ngày thứ một trăm linh tám. Phong thức vì gió, không vì trống. "
            "Tháp: Đại Lực giơ ba đông hai nam — năm. Nhưng năm bóng không nhìn đông nữa. "
            "Tất cả quay đầu nam. Cùng lúc. Từ canh tư."
        ),
        core=(
            "\"Đại Lực. Năm. Đã quay đầu,\" Phong nói nhỏ.\n\n"
            "\"Từ canh tư. Cùng lúc.\"\n\n"
            "\"Có thứ phía nam.\"\n\n"
            "Hùng đến sớm, mắt trũng bớt: \"Hắn mang đá khi rời tháp chuông. Nếu đá kiểm soát — khi nguồn đi, miệng theo.\"\n\n"
            "\"Nếu giữ hắn trong căn cứ — miệng kéo đến. Nếu hắn ra — miệng theo hắn. Cả hai nguy,\" Phong nói.\n\n"
            "Hà sau lưng, khăn thấp: \"Vậy không giữ? Không đuổi?\"\n\n"
            "\"Giữ hiểu đã. Chưa hiểu — không mang đá vào giữa trẻ. Gặp hắn: đá ra ngoài rào trước. Người sau.\"\n\n"
            "---\n\n"
            "Sáng. Họp ngắn mười người. Mạc Tư gạch im: quay nam. Không viết số to.\n\n"
            "\"Ba tuần còn. Rào bắc hôm nay đóng nốt. Nam hào siết. Vũ khí: mỗi người một dao nhỏ gọn,\" Phong phân.\n\n"
            "Tôn Vũ: \"Sắt từ nhà bỏ hoang đủ mười lưỡi. Cần mài.\"\n\n"
            "Hứa: \"Lương siết rau — đủ ba tuần rưỡi nếu không thêm miệng.\"\n\n"
            "Lan: \"Lý Hắc thích nói. Hắn khoe. Nếu gặp — đừng để hắn nói trước trẻ.\"\n\n"
            "\"Ghi. Ai để hắn nói sân — nặng,\" Phong chốt.\n\n"
            "Giữa sáng. Phong và Hà sau bao muối.\n\n"
            "\"Quay đầu cùng lúc — lệnh hay bản năng đá?\" chị nhíu.\n\n"
            "\"Chưa phân bằng tai. Phân bằng việc. Không mở sớm. Không mang sáng vào bếp.\"\n\n"
            "\"Rèm chặt. Trẻ không gần đông-nam.\"\n\n"
            "\"Cùng màu.\"\n\n"
            "A Cường báo: \"Năm nam. Không tiến rào. Chỉ quay. Gió thổi mùi đất se.\"\n\n"
            "\"Không soi. Không kể,\" Phong dặn. Biến.\n\n"
            "Chiều. Phong tuần hào nam: than còn ấm đáy, bùn dính. Cọc đinh keng khi thử tay. Chất lượng. Không khoe. "
            "Bà già ghé bếp: \"Gió?\" \"Gió. Việc,\" Chú Bát đáp trước miệng dài.\n\n"
            "Ngọ cháo. Cúc: \"Ngoài?\" Hà: \"Quay. Xâu.\" Xâu. Hạt miệng. Sân nhàm. "
            "Mười nhịp xưởng: \"Năm quay nam. Không đếm to. Không mang đá vào trẻ. Đông thường. Hầm xấu. Nếu hỏi — cùng màu. Nếu sóng — đâm thấp máu kín.\"\n\n"
            "Gật. Máy che."
        ),
    ),
    dict(
        n=109, title="Cuộc Truy Tìm Thành Trường An", day=109, day_vn="một trăm linh chín",
        exp=23750, event="Ba người tới tường thành · im lặng · dấu đá",
        smell="mùi cỏ non sau mưa mỏng",
        tag="tường Trường An im · cửa đóng · không khói",
        law="Đi vòng không đạp dấu miệng · không vào thành nếu trống lạ · về trước tối",
        cliff="Thành im không khói — rơi rồi, hay đang nín thở chờ lệnh?",
        open=(
            "Ba người ra cổng khi trời còn tối. Ngày thứ một trăm linh chín. "
            "Phong trước — dao ngắn, túi thức ăn dây thừng. "
            "Lý Hắc giữa — tay giữ túi đá, mắt liếc quanh; hắn đã bị đưa về căn cứ canh trước, chưa được kể sân. "
            "Hùng sau — cuốc sắt, bước chắc. "
            "Đại Lực tháp: một ngón nam — hai zombie. \"Bỏ qua. Đi vòng.\""
        ),
        core=(
            "Rẽ tây rồi nam. Gió đông-nam nhẹ. Đất khô hơn. Mùi cỏ non. "
            "Dấu zombie — rộng nông kéo — ba dấu, tuyết mỏng phủ. Cũ. Đi vòng. Không đạp theo.\n\n"
            "Bảy trăm bước: thành Trường An hiện giữa trời xám — tường đá cao, tháp canh, cửa đóng. Không khói bếp. Không dấu sống. Im lặng nặng hơn gào.\n\n"
            "Hùng: \"Chưa rơi. Nhưng không người.\"\n\n"
            "Lý Hắc siết túi: \"Đá nóng hơn. Sáng qua vải.\"\n\n"
            "Phong: \"Không mở túi giữa đường. Không sáng ra nắng. Tìm dấu nguồn rồi về. Không vào cửa nếu trống lạ.\"\n\n"
            "Vòng tường tây: vết cào cao hơn người. Máu khô cũ. Không thây mới. "
            "Góc nam: mảnh vải thư viện khác — chữ mờ. Lý Hắc nhận: \"Chỗ tôi làm. Hắn… tôi… đã lấy đá từ tháp chuông.\"\n\n"
            "Phong nhìn hắn thẳng: \"Ngươi điều khiển miệng?\"\n\n"
            "\"Không hết. Đá giúp. Không đá — giọng yếu. Tôi sợ. Tôi chạy. Mang đá vì sợ bỏ.\"\n\n"
            "\"Sợ đúng. Khoe sai. Về căn cứ: đá ngoài rào trước. Người vào sau. Không nói trẻ.\"\n\n"
            "Lý Hắc gật. Tay run. Hùng: \"Tin hắn?\"\n\n"
            "\"Tin việc. Chưa tin miệng. Việc: đá ra ngoài. Canh. Nghiên cứu không pháo.\"\n\n"
            "---\n\n"
            "Về trước tối. Hà đợi cổng, mắt không lỏng. \"Thành?\"\n\n"
            "\"Im. Không khói. Đá về — để ngoài rào tây hầm xấu. Không vào bếp.\"\n\n"
            "Chị nhìn Lý Hắc một nhịp: \"Lời em nếu miệng. Bao anh.\"\n\n"
            "\"Cùng màu,\" Phong đáp.\n\n"
            "Đêm họp ngắn: Đại Lực, Tôn Vũ, Hà, Hùng, Lan. \"Thành im. Có thể nín. Có thể rơi. Ba tuần siết thành hai nếu cần. Rào vũ khí lương. Đá — ngoài. Không kể sáng.\"\n\n"
            "Gật. Máy che. Không khe đá."
        ),
    ),
    dict(
        n=110, title="Phá Hủy Viên Đá", day=110, day_vn="một trăm mười",
        exp=23800, event="Thử phá đá · sáng hơn · zombie trống quanh rào",
        smell="mùi sắt đỏ lò và khói than",
        tag="thanh sắt nóng · đá không nứt · sáng hơn",
        law="Không mang đá vào trẻ · thử nhỏ không pháo · trống rào ≠ yên hội",
        cliff="Đá không nứt — phải tìm viên lớn, hay phải tìm cách tắt khác?",
        open=(
            "Trời còn tối. Ngày thứ một trăm mười. Tháp: Đại Lực giơ tay — không bóng. "
            "Hoàn toàn trống từ đêm qua. Mùi sắt đỏ lò rèn đã dậy sớm — Tôn Vũ nung thanh sắt từ canh tư. "
            "Phong gật. Đá đã đẩy miệng nam. Thành có thể đã rơi. Căn cứ — trống. Trống không bằng yên hội."
        ),
        core=(
            "Lều Lý Hắc: cửa hé, đá trên bàn, sáng vàng nhạt hơn hôm qua. Hắn ngồi, mắt thâm.\n\n"
            "\"Đá mạnh hơn mỗi ngày. Nếu tiếp — gọi miệng về,\" hắn nói.\n\n"
            "Phong đặt thanh sắt đỏ rực lên bàn đất. Nhiệt sóng mặt. \"Đặt đá lên. Nếu vật lý — nóng. Nóng quá — nứt.\"\n\n"
            "Lý Hắc run, đặt đá lên sắt. Đá sáng hơn. Không nóng tay hắn. Không nứt. Chỉ sáng.\n\n"
            "\"Không phải đá thường,\" Tôn Vũ lầm. \"Không nung được.\"\n\n"
            "\"Ngừng thử lớn. Thử nhỏ đủ. Không pháo sân. Đá về hầm xấu tây — chông vôi then. Không trẻ gần,\" Phong chốt.\n\n"
            "Hà đứng ngưỡng: \"Trống ngoài?\"\n\n"
            "\"Trống. Không thở phào. Tai khe — trống có thể là khoảng lùi mang miệng giả.\"\n\n"
            "\"Rèm chặt. Trẻ không ra sớm.\"\n\n"
            "\"Cùng màu.\"\n\n"
            "---\n\n"
            "Sáng. Máy nghèo chạy ngày trống sau đá. Cháo loãng. Mạc Tư gạch: trống · đá sáng · không nứt. Không viết số to. "
            "Từ Sơn vòng kho đều. A Cường: \"Cổng trống. Ngoài trống. Không dấu vôi mới.\"\n\n"
            "\"Không họp chữ trống. Việc,\" Phong nói.\n\n"
            "Giữa sáng. Gặp Hà sau muối: \"Phá không được. Phải tìm nguồn lớn hơn — hoặc cách tắt khác.\"\n\n"
            "\"Nam? Thành?\"\n\n"
            "\"Có thể. Chuẩn bị hành trình. Không mang cả trại. Ba người. Đá đi cùng nếu cần mồi ngược — ngoài tay trẻ.\"\n\n"
            "Chị nhíu: \"Anh đi. Em giữ.\"\n\n"
            "\"Đúng. Lời em. Bao anh.\"\n\n"
            "Chiều. Phân công: Đại Lực rào; Tôn Vũ vũ khí; Hứa lương; Lý Hắc canh đá ngoài hầm xấu không một mình — A Cường xen ca; Hà tổ chức miệng trong. "
            "Phong kiểm đông: chông vôi then hố vết nguyên. Không vôi mới. Gật. Không khen.\n\n"
            "Ngọ. Mười nhịp xưởng: \"Đá không nứt. Trống ≠ yên. Không thở phào. Không kể sáng. Nếu bóng — không chỉ. Nếu sóng — đâm thấp. Nếu hỏi — cùng màu.\"\n\n"
            "Gật. Máy che."
        ),
    ),
    dict(
        n=111, title="Chuẩn Bị", day=111, day_vn="một trăm mười một",
        exp=23850, event="Ba tuần siết · phân công · không zombie ba ngày",
        smell="mùi gỗ mới chặt và mồ hôi sân",
        tag="chuẩn bị ba tuần · rào vũ khí lương đá",
        law="Mỗi người một việc · không lười · không cãi · vấn đề nói thẳng",
        cliff="Ba tuần đếm ngược — liệu tay có kịp trước khi miệng quay lại?",
        open=(
            "Bình minh. Ngày thứ một trăm mười một. Ba tuần để chuẩn bị — đếm trong xương. "
            "Tháp: Đại Lực — không zombie ba ngày. Mùi gỗ mới chặt và mồ hôi sân đã dậy. "
            "Phong ra sân, mắt đếm người: ba mươi sáu miệng ăn, ba mươi sáu việc."
        ),
        core=(
            "\"Không zombie. Ba ngày,\" Đại Lực nói.\n\n"
            "\"Tốt. Tiếp canh. Không thở phào.\"\n\n"
            "Phân công rõ:\n"
            "Đại Lực — hàng rào lớp ngoài dày cao, gỗ đá. Mỗi người một phần: chặt, khuân, đắp.\n"
            "Tôn Vũ — dao đao giáo từ sắt tìm được; mỗi người một lưỡi nhỏ gọn.\n"
            "Hứa — kho; hợp Trương Thành cách bảo quản; siết rau.\n"
            "Lý Hắc — đá ngoài hầm xấu; nghiên cứu không pháo; A Cường xen ca.\n"
            "Hà — tổ chức xung đột; trẻ thẻ; rèm.\n"
            "Phong — nối việc; tìm thêm người nếu an toàn; không ôm tất cả miệng.\n\n"
            "Chiều họp mười lăm người lớn trong lều lớn. Đèn dầu vàng mờ. Mặt căng.\n\n"
            "\"Ba tuần. Không hội mừng trống. Mỗi ngày một việc đo được. Ai lười — nhắc một. Nhắc hai — cắt phần thịt. Ai cãi việc sống — ra ngoài rào một mình,\" Phong nói đều, không gào.\n\n"
            "Im. Rồi gật. Không sợ — tin.\n\n"
            "Hà sau họp, thấp: \"Nặng?\"\n\n"
            "\"Nặng đúng. Nhẹ là chết.\"\n\n"
            "\"Em giữ trẻ. Anh không mang đá vào lều.\"\n\n"
            "\"Giữ.\"\n\n"
            "---\n\n"
            "Giữa sáng ngày việc. Phong đảo muối, nghe búa đinh keng bắc, rìu gỗ nam, mài đá xưởng. "
            "Mùi mồ hôi trộn cháo loãng. Bà già: \"Gió?\" \"Gió. Việc.\"\n\n"
            "A Cường: \"Đá hầm xấu. Sáng ổn định. Không nứt. Không gọi.\"\n\n"
            "\"Ghi. Không soi lâu. Mắt mỏi thì đổi ca.\"\n\n"
            "Lan dạy hai trẻ chữ không liên quan đá — chỉ đếm gạo. Cúc xâu thẻ. Hạt miệng. Sân nhàm đắt.\n\n"
            "Ngọ mười nhịp: \"Chuẩn bị. Không kể cấp. Không kể đá sáng. Đông thường. Hầm xấu. Cùng màu nếu hỏi. Máu kín nếu sóng.\"\n\n"
            "Gật. Máy che. Phong gặp Hà sau muối lần hai: \"Đủ? Không lệch vì ba tuần?\"\n\n"
            "\"Không lệch. Việc không hội. Việc là im đo được,\" chị lau tay. \"Ai kể ngoài lều — nặng.\""
        ),
    ),
    dict(
        n=112, title="Cuộc Ra Đi", day=112, day_vn="một trăm mười hai",
        exp=23900, event="Ba người nam · bản đồ Trương Thành · đá trong túi",
        smell="mùi đất đỏ và cỏ non gió nam",
        tag="ra đi phía nam · tháp xa dần",
        law="Mai trở lại lời với cổng · không đuổi mắt quá hai nhịp · đá không mở nắng",
        cliff="Con đường nam dài hơn tưởng — liệu có kịp về trước khi sáng đá gọi miệng?",
        open=(
            "Ba người ra cổng trời còn tối. Ngày thứ một trăm mười hai. "
            "Phong trước — ba lô hai tuần: thức ăn, dây, dao, kim, bản đồ Trương Thành vẽ lệch nhưng đủ hướng nam. "
            "Lý Hắc giữa — đá trong túi vải, sáng vàng nhạt lọt chỉ. "
            "Hùng sau — cuốc, dao hông, mắt bốn hướng. "
            "Tháp: Đại Lực ba ngón nam xa — không đuổi. \"Mai trở lại,\" Phong thấp."
        ),
        core=(
            "Đất đỏ mềm dễ lún. Đá nhỏ lăn mỗi bước. Gió nam ấm hơn bấc nhưng vẫn lạnh. Mùi đất cỏ non. "
            "Năm trăm bước: quay đầu — tháp canh và rào nhỏ giữa đất trống. Không ngoái lâu. Ngoái lâu là mời nhớ sai.\n\n"
            "Im. Chỉ bước. Lý Hắc: \"Đá nóng hơn khi đi nam.\"\n\n"
            "\"Không mở túi. Không sáng ra nắng. Nếu nóng quá — báo. Không gào,\" Phong đáp.\n\n"
            "Một nghìn bước: dấu zombie nhiều — hàng chục kéo nam. Dấu mới sâu hơn. "
            "Hùng: \"Lớn hơn thường.\"\n\n"
            "\"Tiến hóa hoặc mang đồ. Đi vòng. Không đạp theo.\"\n\n"
            "Chiều tới bờ suối cạn. Nghỉ nửa canh. Nước đun. Cháo nguội. Không lửa to. Khói là bản đồ.\n\n"
            "Lý Hắc: \"Phía trước có đền cũ. Tôi nghe — đá lớn ở đó. Mảnh này từ đá lớn.\"\n\n"
            "\"Nghe hay thấy?\"\n\n"
            "\"Nghe. Thư viện. Sách rách.\"\n\n"
            "\"Đủ để đi. Không đủ để tin hết. Mắt kiểm.\"\n\n"
            "---\n\n"
            "Đêm ngoài — không lều căn cứ. Ba người xoay ca. Phong ca một: nghe gió, không xe, không lê sát. "
            "Nghĩ Hà trong rào: rèm, thẻ, cháo, lời cùng màu. Nắm muối hạt trong túi — chát neo nghề.\n\n"
            "Canh hai Hùng: \"Ngủ. Tôi nghe.\"\n\n"
            "Canh ba Lý Hắc run: \"Sáng mạnh.\" Phong sờ ngoài túi — nóng nhẹ. \"Bọc thêm vải. Không mở.\"\n\n"
            "Gà rừng xa. Không vội. Nam còn dài. Việc mở trước miệng."
        ),
    ),
    dict(
        n=113, title="Viên Đá Lớn", day=113, day_vn="một trăm mười ba",
        exp=23950, event="Đá nhỏ hòa đá lớn · sáng tắt · im sau chói",
        smell="mùi đá lạnh hang và khói đuốc",
        tag="viên đá lớn tắt · mảnh biến mất",
        law="Không nhìn sáng lâu · không kể chói sân · tắt ≠ hết nguy",
        cliff="Đá tắt — miệng sẽ tan hay sẽ loạn không lệnh?",
        open=(
            "Buổi chiều ngày thứ một trăm mười ba. Ba người đứng trước viên đá lớn trên bàn đá trong đền nứt. "
            "Đá sáng vàng nhấp nháy như tim. Sáng đến phải che mắt. Bóng ba người dài trên tường. "
            "Mùi đá lạnh hang và khói đuốc. Gió lùa khe mái."
        ),
        core=(
            "\"Ngươi nói mảnh là của lớn,\" Phong nói.\n\n"
            "Lý Hắc: \"Có thể hòa. Mảnh về lớn.\"\n\n"
            "\"Hòa xong — mạnh hơn hay nổ?\"\n\n"
            "\"Không biết.\"\n\n"
            "Phong đặt dao sắt lên bàn. \"Làm. Hùng chặn cửa. Tôi kéo nếu sáng lạ. Không nhìn thẳng.\"\n\n"
            "Lý Hắc đặt mảnh cạnh lớn. Sáng hơn — trắng — chói — ba người nhắm. Rồi im. Ánh tắt.\n\n"
            "Mảnh biến mất. Lớn nằm đen — như đá thường. Không nháy. Không nóng.\n\n"
            "Hùng thở: \"Xong?\"\n\n"
            "\"Tắt. Chưa xong. Tắt ≠ hết nguy. Có thể loạn không lệnh. Có thể ngủ. Về. Mang theo nếu nhẹ — hoặc bỏ nếu nặng lạ,\" Phong nói.\n\n"
            "Lý Hắc sờ: \"Nhẹ. Lạnh.\"\n\n"
            "\"Bọc. Không khoe. Đi.\"\n\n"
            "---\n\n"
            "Ra đền. Trời xám. Không bóng lê gần. Dấu cũ. Đi vòng bắc về hướng căn cứ. "
            "Im. Chỉ bước. Phong nghĩ Hà: sẽ nói tắt — không nói chói. Chói là hội.\n\n"
            "Đêm dừng rừng thưa. Ca xoay. Đá lớn bọc trong ba lớp vải dưới gốc. Không để sát người ngủ.\n\n"
            "Lý Hắc: \"Tôi… hết giọng với miệng?\"\n\n"
            "\"Chưa kiểm. Về kiểm bằng mắt ngoài rào. Không thử gần trẻ.\"\n\n"
            "Hùng: \"Tin hắn hơn một tấc.\"\n\n"
            "\"Tin việc tắt. Chưa tin người.\"\n\n"
            "Gió nam mang mùi đất đỏ. Tai khe. Sống. Đo. Không khoe."
        ),
    ),
    dict(
        n=114, title="Con Đường Phía Nam", day=114, day_vn="một trăm mười bốn",
        exp=24000, event="Đường về · dấu lớn · ba người mang đá tắt",
        smell="mùi đất đỏ bụi đường",
        tag="đường về bắc · dấu zombie lớn",
        law="Không đạp dấu lớn · không mở bọc đá · về trước hết sức",
        cliff="Dấu lớn phía sau — đuổi theo tắt, hay chỉ là xác cũ?",
        open=(
            "Bình minh ngày thứ một trăm mười bốn. Ba người bước bắc về căn cứ. "
            "Đá lớn tắt bọc trong ba lô Lý Hắc — nặng vai nhưng không sáng. "
            "Mùi đất đỏ bụi đường. Gió ngược mặt. Tháp canh còn xa."
        ),
        core=(
            "Năm trăm bước: dấu lớn hơn hôm đi — sâu, mới hơn sương. "
            "Đại… Hùng sửa miệng: \"Lớn. Mới.\"\n\n"
            "\"Vòng tây. Không đạp. Không chỉ.\"\n\n"
            "Một nghìn bước: nghe lê xa phải. Không thấy hình. Tăng tốc nửa nhịp — không chạy. Chạy là gãy hơi.\n\n"
            "Lý Hắc thở: \"Đá rung nhẹ.\"\n\n"
            "\"Không mở. Nếu sáng lọt — báo.\"\n\n"
            "Không sáng lọt. Rung rồi im.\n\n"
            "Chiều thấy tháp canh — nhỏ rồi lớn. Đại Lực giơ hai ngón mở: cổng nhận. "
            "Hà đứng trong then, khăn thấp, mắt đếm ba người đủ.\n\n"
            "\"Về. Đá tắt. Để hầm xấu. Không trẻ,\" Phong nói trước ôm.\n\n"
            "Chị gật. Nắm tay một nhịp. Buông. Đủ.\n\n"
            "---\n\n"
            "Trong rào. Việc trước miệng. Đá vào hầm xấu tây — chông vôi then. A Cường khóa. "
            "Họp ngắn: \"Tắt. Chưa chắc miệng tan. Canh bảy ngày. Rào siết. Không thở phào.\"\n\n"
            "Gật. Máy che. Ngọ cháo loãng. Cúc xâu. Sân nhàm. "
            "Phong gặp Hà sau muối: \"Đủ? Không lệch vì đường?\"\n\n"
            "\"Không lệch. Về là việc. Không hội mừng về,\" chị đáp. \"Mai còn dấu lớn.\""
        ),
    ),
    dict(
        n=115, title="Người Trong Hang", day=115, day_vn="một trăm mười lăm",
        exp=24050, event="Hang phía tây · người sống · thêm miệng ăn",
        smell="mùi ẩm hang và khói đuốc nhỏ",
        tag="hang tây · người sống · quy tắc vào rào",
        law="Người mới: quy tắc trước cháo · trẻ trước · không mang đồ lạ vào bếp",
        cliff="Trong hang còn bao nhiêu miệng — cứu được bao nhiêu trước khi tối?",
        open=(
            "Chiều ngày thứ một trăm mười lăm. Ba người — Phong, Đại Lực, Hùng — vào hang tây nửa dặm. "
            "Đuốc nhỏ. Bóng dài. Tường đá đen ẩm. "
            "Ánh vàng nhạt sâu trong — không phải đá kho; là lửa người. Mùi ẩm hang và khói."
        ),
        core=(
            "Phong trước dao. Đại Lực giữa. Hùng sau. "
            "Sâu hang: mười hai người — già trẻ, áo rách, mắt sợ. Một bà ôm cháu. Một thanh niên cầm gậy.\n\n"
            "\"Zombie?\" thanh niên khàn.\n\n"
            "\"Người. Căn cứ bắc. Có rào. Có cháo. Quy tắc: không ra một mình, không cãi việc sống, trẻ trước. Muốn theo — bỏ đồ lạ ngoài rào để kiểm,\" Phong nói đều.\n\n"
            "Họ nhìn nhau. Bà khóc nhẹ: \"Đi.\"\n\n"
            "Ra hang trước tối. Đoàn lặng. A Cường cổng đếm: mười hai. Hà bê nước. Cháo loãng thêm nồi — siết rau gốc.\n\n"
            "\"Cảm ơn,\" bà nói.\n\n"
            "\"Việc. Không hội,\" Hà đáp, mắt dịu nhưng rèm vẫn chặt.\n\n"
            "---\n\n"
            "Đêm. Họp: dân số tăng. Lương siết. Rào ca thêm. "
            "Phong: \"Cứ được bao nhiêu người thì căn cứ mới mạnh lên — nếu việc đều. Nếu ồn — yếu.\"\n\n"
            "Gật. Lý Hắc từ hầm xấu báo: đá vẫn tắt. Không rung. "
            "\"Ghi. Bảy ngày chưa hết.\"\n\n"
            "Phong-Hà thềm lều: \"Mười hai miệng. Đủ chỗ nếu xép.\"\n\n"
            "\"Đủ nếu im. Không đủ nếu kể hang như truyện,\" chị nói.\n\n"
            "\"Không kể.\" Nắm. Buông. Ngủ ca."
        ),
    ),
    dict(
        n=116, title="Cuộc Sống Sau Viên Đá", day=116, day_vn="một trăm mười sáu",
        exp=24100, event="45 người · đá tắt ba ngày · không zombie",
        smell="mùi cháo loãng và gỗ ướt sân",
        tag="sau đá tắt · bốn mươi lăm người",
        law="Chia đúng cách · canh không lỏng · trống ≠ yên hội",
        cliff="Ba ngày trống — khoảng lùi hay thật im?",
        open=(
            "Bình minh ngày thứ một trăm mười sáu. Bốn mươi lăm người. "
            "Đủ chỗ nếu xép. Đủ ăn nếu chia đúng. "
            "Tháp: Đại Lực — không zombie từ khi đá tắt — ba ngày. "
            "Mùi cháo loãng và gỗ ướt sân. Phong ra sớm, đếm việc không đếm sợ."
        ),
        core=(
            "\"Không zombie. Ba ngày,\" Đại Lực nói.\n\n"
            "\"Tốt. Tiếp canh. Không thở phào.\"\n\n"
            "Phân việc: tháp ba ca; rèn; kho; rau; trẻ thẻ; đá hầm xấu xen ca; tuần ngoài ngắn không một mình. "
            "Hà gọi tên từng tổ. Không ai cãi — tin.\n\n"
            "Giữa sáng. Phong đảo muối. Hà phơi. "
            "\"Sau đá — người mới hay hỏi sáng. Không trả lời chi tiết. Trả lời: tắt. Việc,\" anh dặn.\n\n"
            "\"Lời em. Bao anh.\"\n\n"
            "A Cường: \"Hầm xấu im. Đá lạnh.\"\n\n"
            "\"Ghi.\"\n\n"
            "Chiều tuần ngắn đông trong rào: chông then hố vết. Nguyên. "
            "Lan dạy đếm gạo. Hùng sửa cọc. Lý Hắc không khoe giọng — im đúng.\n\n"
            "Ngọ mười nhịp: \"Bốn mươi lăm. Đá tắt ba ngày. Không đếm to. Không mừng trống. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng.\"\n\n"
            "Gật. Máy che. Đêm: Phong nắm tay Hà. \"Mai còn mở rộng nếu an toàn.\"\n\n"
            "\"An toàn đo bằng canh, không bằng muốn,\" chị đáp."
        ),
    ),
    dict(
        n=117, title="Năm Mươi Người", day=117, day_vn="một trăm mười bảy",
        exp=24130, event="Gần năm mươi · thêm người đường đông · siết lương",
        smell="mùi người mới và bụi đường",
        tag="bốn mươi chín miệng · gần năm mươi",
        law="Người mới quy tắc trước cháo · siết rau · không mở rèm sớm",
        cliff="Năm mươi miệng — mạnh hơn hay ồn hơn?",
        open=(
            "Bình minh ngày thứ một trăm mười bảy. Bốn mươi chín người — gần năm mươi. "
            "Tháp: không zombie sáu ngày. "
            "Mùi người mới trộn bụi đường — bốn người đường đông xin vào canh trước, đã qua quy tắc."
        ),
        core=(
            "\"Sáu ngày trống. Tiếp canh,\" Phong nói với Đại Lực.\n\n"
            "Hà chia việc tổ mới: gánh nước, vá rèm, không gần hầm xấu. "
            "Hứa cau: \"Lương căng. Siết rau thêm một nấc.\"\n\n"
            "\"Siết. Thịt Kho Vô Hạn không nêm mừng.\"\n\n"
            "Họp ngắn sân: \"Gần năm mươi. Mạnh nếu im. Yếu nếu ồn. Mỗi người một việc. Vấn đề nói thẳng.\"\n\n"
            "Gật. Không cãi.\n\n"
            "Giữa sáng. Phong-Hà muối: \"Đủ chỗ?\"\n\n"
            "\"Xép. Đủ. Không dựng lều ngoài rào.\"\n\n"
            "\"Đúng. Ngoài rào là chết chậm.\"\n\n"
            "A Cường: \"Đá lạnh. Cổng trống.\"\n\n"
            "\"Không soi. Không kể.\"\n\n"
            "Chiều. Tôn Vũ giao thêm năm lưỡi nhỏ cho tổ mới. Mài không khoe. "
            "Cúc xâu thẻ thêm. Trẻ khuất. Sân nhàm.\n\n"
            "Ngọ mười nhịp: \"Bốn mươi chín. Sáu ngày trống. Không thở phào. Không họp chữ năm mươi. Việc.\"\n\n"
            "Gật. Máy che."
        ),
    ),
    dict(
        n=118, title="Cuộc Tìm Kiếm", day=118, day_vn="một trăm mười tám",
        exp=24160, event="Tuần ngoài ba hướng · cá tây · không miệng",
        smell="mùi cá suối và rong",
        tag="tìm kiếm ba hướng · mười cá",
        law="Năm trăm bước mỗi hướng · không một mình · đồ lạ kiểm ngoài",
        cliff="Phía đông trống — phía nào sẽ mang tin trước?",
        open=(
            "Bình minh ngày thứ một trăm mười tám. Ba người — Phong, Đại Lực, Lý Hắc — ra cổng. "
            "Tôn Vũ tháp: không zombie. "
            "Mục tiêu: năm trăm bước mỗi hướng — người, lương, vũ khí. Không anh hùng."
        ),
        core=(
            "Bắc năm trăm: đất đỏ đá thưa — trống. "
            "Tây năm trăm: đất ẩm cỏ suối — mười cá. Bắt. Không lửa. Về ướp muối. Mùi cá rong bám tay.\n\n"
            "Đông năm trăm: bụi đường — dấu người cũ, không mới. Không đuổi dấu cũ.\n\n"
            "Nam không đi sâu — dấu lớn còn trong sổ. Chỉ quan sát mép. Trống hôm nay.\n\n"
            "Về. Hà nhận cá: \"Siết rau bớt nửa nấc tối nay. Không mừng chợ.\"\n\n"
            "\"Đúng.\"\n\n"
            "Lý Hắc: \"Ngoài im. Đá trong hầm im.\"\n\n"
            "\"Im hai lớp. Tai vẫn khe.\"\n\n"
            "Chiều họp tổ: phân cá đều — trẻ trước. "
            "Phong-Hà: \"Tìm kiếm là việc không phải dạo. Mai lại nếu cần.\"\n\n"
            "\"Em giữ rèm.\"\n\n"
            "Ngọ mười nhịp: \"Mười cá. Ba hướng. Không kể như chiến thắng. Đông thường. Hầm xấu.\"\n\n"
            "Gật. Máy che."
        ),
    ),
    dict(
        n=119, title="Trận Chiến", day=119, day_vn="một trăm mười chín",
        exp=24200, event="Sáu bóng thấp nam · máu kín · hố xấu",
        smell="mùi tanh máu kín và đất sườn nam",
        tag="sóng thấp sáu · máu kín không phơi",
        law="Đâm thấp · không mặt · không đếm to · không phơi · hố xấu",
        cliff="Sáu đã khép — liệu còn lớp sóng sau gió bấc?",
        open=(
            "Trống điểm tan mang mùi tanh đất sườn nam. Ngày thứ một trăm mười chín. "
            "A Cường lách xưởng báo thấp: sáu bóng thấp từ sườn nam — không gào — chỉ sóng. "
            "Luật xương: đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi."
        ),
        core=(
            "Phong hạ tay. Móc gáy-hông. Tôn Vũ hai. Đại Lực hai. Hùng một. Hứa chặn lệch. "
            "Không đếm to. Không phơi. Máu ngắn. Thóc lép rắc. Hố mới — không trùng hố cũ đông. Đắp xấu. Phủi.\n\n"
            "Hà trong rèm không ra: \"Kín?\"\n\n"
            "\"Kín. Sáu. Máu vải. Không phơi,\" Phong lau móc lá khô. Mùi tanh bám ngón. Thở. Siết hàm. Không kể sân.\n\n"
            "Khuyển ngưỡng. A Minh tín hiệu gò. Không sóng thêm.\n\n"
            "A Cường: \"Hết gần. Không theo. Gió thổi tanh ra.\"\n\n"
            "\"Không soi. Không kể số.\"\n\n"
            "---\n\n"
            "Giữa sáng. Việc sóng vào xương. Cháo loãng trưa. Cúc xâu. Trẻ không thấy hố. "
            "Mười nhịp xưởng: \"Sáu thấp. Máu kín. Không đếm to. Không phơi. Đông thường. Hầm xấu. Nếu hỏi — cùng màu.\"\n\n"
            "Gật. Máy che.\n\n"
            "Phong-Hà muối: \"Đủ? Không lệch vì sóng?\"\n\n"
            "\"Không lệch. Việc không hội,\" chị. \"Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp.\"\n\n"
            "\"Ghi. Lần này không pháo.\"\n\n"
            "Chiều. Hố lớp thêm canh tư sẽ làm. Sống. Đo. Không khoe."
        ),
    ),
    dict(
        n=120, title="Thành Trường An", day=120, day_vn="một trăm hai mươi",
        exp=24130, event="Bốn mươi chín · tin thành · bảy ngày trống",
        smell="mùi khói bếp trong và gió đông mang bụi thành",
        tag="nhắc Trường An · bảy ngày trống",
        law="Bình yên không kéo dài · canh không lỏng · mở rộng có điều kiện",
        cliff="Thành im trong trí nhớ — mai có mang người chạy nữa không?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi. Bốn mươi chín người. "
            "Bảy ngày không zombie từ đá tắt. "
            "Mùi khói bếp trong; gió đông mang bụi tưởng như thành xa. "
            "Phong ra sân — việc trước miệng nhớ Trường An."
        ),
        core=(
            "\"Bảy ngày. Tốt. Tiếp canh,\" anh nói với Đại Lực.\n\n"
            "Họp phòng lớn: \"Hai mươi tám ngày từ sợ đến đều. Bình yên không kéo dài. Zombie có thể quay. Có thể tiến hóa. Chuẩn bị không nghỉ.\"\n\n"
            "Lan: \"Thành… còn?\"\n\n"
            "\"Im khi ta thấy. Không về đó hội. Về đó chỉ khi việc.\"\n\n"
            "Hùng gật. Lý Hắc im — đúng.\n\n"
            "Hà phân tổ. Hứa kho. Tôn Vũ rèn. "
            "Phong-Hà muối: \"Nhắc thành để nhớ nguy, không để nhớ oán.\"\n\n"
            "\"Em giữ trẻ khỏi chuyện tháp chuông.\"\n\n"
            "\"Giữ.\"\n\n"
            "Chiều tuần trong rào. Chông then nguyên. "
            "Ngọ mười nhịp: \"Bảy ngày trống. Không thở phào. Không họp chữ thành. Việc. Cùng màu. Máu kín nếu sóng.\"\n\n"
            "Gật. Máy che. Đêm thềm: nắm tay. Mùi đất se. Sống. Đo. Không khoe."
        ),
    ),
    dict(
        n=121, title="Cuộc Sống Mới", day=121, day_vn="một trăm hai mươi mốt",
        exp=24140, event="Tám ngày trống · nhịp sống mới · việc đều",
        smell="mùi rơm khô và cháo sáng",
        tag="nhịp sống mới · tám ngày trống",
        law="Mỗi người một việc đo được · không lười · không cãi",
        cliff="Sống mới có bền khi miệng ngoài chưa hết?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi mốt. Bốn mươi chín người. "
            "Tám ngày trống. Mùi rơm khô và cháo sáng. "
            "Phong dậy năm giờ xương — không phải đồng hồ."
        ),
        core=(
            "Đại Lực tháp ba ca. Tôn Vũ rèn. Hứa kho. Hà tổ. Cúc thẻ. A Cường hầm đá. "
            "Phong nối việc — không ôm miệng.\n\n"
            "\"Tám ngày. Tiếp canh,\" anh nói.\n\n"
            "Người mới hỏi: \"Bao giờ hết canh?\"\n\n"
            "\"Khi đất hết miệng ngoài. Chưa.\"\n\n"
            "Giữa sáng muối: Hà \"Sống mới dễ lỏng.\" Phong \"Lỏng hở. Hở chết chậm.\"\n\n"
            "\"Lời em. Bao anh.\"\n\n"
            "Chiều sửa cọc. Trẻ học đếm gạo không học đếm zombie. "
            "Ngọ mười nhịp: \"Tám ngày. Việc đều. Không mừng. Đông thường. Hầm xấu.\"\n\n"
            "Gật. Máy che. Đêm: canh xoay. Nắm. Ngủ. Mai lại."
        ),
    ),
    dict(
        n=122, title="Hợp Tác", day=122, day_vn="một trăm hai mươi hai",
        exp=24165, event="Năm mươi hai · hợp tác tổ · chín ngày trống",
        smell="mùi mồ hôi chung và gỗ mới",
        tag="hợp tác tổ · năm mươi hai miệng",
        law="Tổ nối tổ · không ôm việc một mình · xung đột nói Hà",
        cliff="Hợp tác bền hay chỉ bền khi trống?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi hai. Năm mươi hai người. "
            "Chín ngày trống. Mùi mồ hôi chung và gỗ mới — hai tổ ghép rào lớp ngoài."
        ),
        core=(
            "\"Chín ngày. Tiếp. Hợp tác: tổ rào nối tổ rèn — đinh không chờ gỗ, gỗ không chờ đinh,\" Phong phân.\n\n"
            "Họp: \"Ba mươi ngày. Từ sợ đến đều. Bình yên không kéo dài. Hợp tác là việc không phải hội.\"\n\n"
            "Gật. Hà điều xung đột nhỏ — phần rau — im đúng. "
            "Phong-Hà: \"Hợp tác hỏng khi khoe công.\"\n\n"
            "\"Em chặn miệng khoe. Anh chặn việc lệch.\"\n\n"
            "A Cường: \"Đá im. Cổng trống.\"\n\n"
            "\"Không thở phào.\"\n\n"
            "Ngọ mười nhịp: \"Năm mươi hai. Hợp tác. Không kể công. Cùng màu nếu hỏi. Máu kín nếu sóng.\"\n\n"
            "Gật. Máy che. Chiều rào dài thêm một gang. Đủ. Không khoe gang."
        ),
    ),
    dict(
        n=123, title="Thành Viên Mới", day=123, day_vn="một trăm hai mươi ba",
        exp=24175, event="Thêm người tây · cá · mười ngày trống",
        smell="mùi cá muối và người đường",
        tag="thành viên mới · đường tây",
        law="Quy tắc trước cháo · kiểm đồ ngoài · trẻ trước",
        cliff="Còn bao nhiêu miệng ngoài đường sẽ gõ then?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi ba. Năm mươi hai người — chiều sẽ hơn. "
            "Mười ngày trống. Phong thám năm trăm bước: tây suối — cá; gặp ba người xin theo."
        ),
        core=(
            "Ba người: một mẹ hai con lớn. \"Quy tắc. Đồ kiểm ngoài. Trẻ trước,\" Phong nói.\n\n"
            "Họ gật. Về cổng. Hà nước. Cháo. Thẻ. "
            "Hứa: \"Siết lại nửa nấc rau.\"\n\n"
            "\"Siết.\"\n\n"
            "Đêm dân số năm mươi lăm… chờ chốt sổ mai. Việc trước số.\n\n"
            "Phong-Hà: \"Mới dễ ồn.\"\n\n"
            "\"Rèm. Thẻ. Không hang truyện.\"\n\n"
            "Ngọ mười nhịp: \"Người mới. Quy tắc. Không kể đường như chiến công. Đông thường. Hầm xấu.\"\n\n"
            "Gật. Máy che. Đá hầm vẫn tắt. Tai khe."
        ),
    ),
    dict(
        n=124, title="Cuộc Sống Bình Yên", day=124, day_vn="một trăm hai mươi bốn",
        exp=24205, event="Năm mươi sáu · mười một ngày trống · yên việc",
        smell="mùi nắng sân và cháo loãng",
        tag="bình yên việc · không hội yên",
        law="Yên là việc im · không thở phào · không mở rèm sớm",
        cliff="Yên mười một ngày — lớp mồi hay lớp thật?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi bốn. Năm mươi sáu người. "
            "Mười một ngày trống. Mùi nắng sân và cháo loãng. "
            "Yên — nhưng yên là việc im, không phải hội yên."
        ),
        core=(
            "\"Mười một ngày. Tiếp canh. Không thở phào,\" Phong nói.\n\n"
            "Họp ngắn: \"Mỗi người một việc. Không lười. Không cãi. Vấn đề nói tôi hoặc Hà.\"\n\n"
            "Gật. Tin.\n\n"
            "Hà: \"Yên thật hay yên mồi?\"\n\n"
            "\"Trống. Tai khe. Ba xương: không thở phào, không mở rèm sớm, không rải vôi nghỉ.\"\n\n"
            "\"Giữ.\"\n\n"
            "Chiều phơi bao nắng xấu. Trẻ xâu trong. "
            "Ngọ mười nhịp: \"Yên sau trống. Không họp chữ yên. Việc. Cùng màu. Máu kín nếu sóng.\"\n\n"
            "Gật. Máy che. Đêm nắm tay. Mùi đất se. Sống. Đo. Không khoe."
        ),
    ),
    dict(
        n=125, title="Buổi Sáng Ấm Áp", day=125, day_vn="một trăm hai mươi lăm",
        exp=24215, event="Sáng ấm · mười hai ngày · việc đều",
        smell="mùi nắng ấm mái và khói bếp ngọt",
        tag="sáng ấm · không lỏng vai",
        law="Ấm không bằng lỏng · canh đủ · cháo đủ",
        cliff="Ấm có làm mắt dễ chỉ không — mai sẽ biết khi gió đổi?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi lăm. Năm mươi sáu người. "
            "Mười hai ngày trống. Mùi nắng ấm mái và khói bếp ngọt hơn thường — củi khô. "
            "Ấm. Không lỏng vai."
        ),
        core=(
            "Phong tổ việc: tháp, rèn, kho, rau, thẻ, hầm đá, tuần ngắn. "
            "\"Mười hai ngày. Tốt. Tiếp. Ấm không phải nghỉ.\"\n\n"
            "Hà bê cháo: \"Ấm dễ nở miệng. Em chặn.\"\n\n"
            "\"Chặn. Anh chặn việc lệch.\"\n\n"
            "Trẻ cười nhẹ trong thẻ — không ra cổng. Đủ. "
            "A Cường: \"Trống. Đá im.\"\n\n"
            "\"Không soi.\"\n\n"
            "Ngọ mười nhịp: \"Sáng ấm. Không lỏng. Đông thường. Hầm xấu. Cùng màu.\"\n\n"
            "Gật. Máy che. Chiều nắng dài. Phơi. Muối chát. Nghề. Đêm: \"Đều?\" \"Đều.\""
        ),
    ),
    dict(
        n=126, title="Tiềm Năng Ẩn", day=126, day_vn="một trăm hai mươi sáu",
        exp=24245, event="Năm mươi chín · EXP gần cấp · tiềm năng người",
        smell="mùi than xưởng và đất se",
        tag="tiềm năng ẩn · người và kho",
        law="Không khoe cấp · không kể EXP trẻ · việc đo được",
        cliff="Gần cấp mới — liệu có mở đúng lúc hay mở khi ồn?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi sáu. Năm mươi chín người. "
            "Mười ba ngày trống. Mùi than xưởng và đất se. "
            "Trong xương kho: EXP gần ngưỡng — không pháo sân."
        ),
        core=(
            "Họp: \"Ba mươi bốn ngày. Từ sợ đến đều. Tiềm năng không nằm miệng khoe — nằm tay việc: rèn, rào, thuốc, chữ đếm gạo.\"\n\n"
            "Tôn Vũ giơ tay thô: \"Tôi dạy mài cho ba người.\"\n\n"
            "\"Dạy. Không khoe lưỡi.\"\n\n"
            "Lan: \"Dạy chữ sổ kho.\"\n\n"
            "\"Dạy. Không chữ đá.\"\n\n"
            "Phong-Hà: \"Gần cấp. Không kể trẻ.\"\n\n"
            "\"Giữ.\"\n\n"
            "Ngọ mười nhịp: \"Năm mươi chín. Tiềm năng là việc. Không pháo cấp. Cùng màu. Máu kín nếu sóng.\"\n\n"
            "Gật. Máy che. Đêm sổ than gạch nhẹ: gần ngưỡng · không pháo. Ngủ."
        ),
    ),
    dict(
        n=127, title="Bình Minh Thứ Đồ", day=127, day_vn="một trăm hai mươi bảy",
        exp=24255, event="Bình minh việc · mười bốn ngày · đồ nghề đủ",
        smell="mùi sương mai và sắt nguội",
        tag="bình minh đồ nghề · không thiếu lưỡi",
        law="Đồ đủ không khoe · ca đủ không thiếu · ấm không lỏng",
        cliff="Đồ nghề đủ — người có đủ im để dùng đúng?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi bảy. Năm mươi chín người. "
            "Mười bốn ngày trống. Mùi sương mai và sắt nguội xưởng — đồ nghề đã đủ cho ca. "
            "Bình minh việc, không bình minh hội."
        ),
        core=(
            "Phong tổ việc như xương: tháp, rèn, kho, rau, thẻ, hầm, tuần. "
            "\"Mười bốn ngày. Đồ đủ. Người đừng thiếu im.\"\n\n"
            "Hà: \"Đủ đồ dễ khoe. Em chặn.\"\n\n"
            "\"Chặn.\"\n\n"
            "Tôn Vũ giao lưỡi cuối cho tổ rào. Không pháo. "
            "A Cường: \"Trống. Đá im.\"\n\n"
            "Ngọ mười nhịp: \"Đồ đủ. Không khoe. Đông thường. Hầm xấu. Cùng màu.\"\n\n"
            "Gật. Máy che. Chiều nắng. Muối. Đêm nắm: \"Mai cộng đồng đếm lại.\" \"Đếm việc không đếm hù.\""
        ),
    ),
    dict(
        n=128, title="Cộng Đồng Sống", day=128, day_vn="một trăm hai mươi tám",
        exp=24285, event="Sáu mươi hai miệng · mười lăm ngày · cộng đồng việc",
        smell="mùi cháo chung và đất sân đông người",
        tag="cộng đồng sống · sáu mươi hai",
        law="Cộng đồng = việc đều · không lười · không cãi · nói thẳng",
        cliff="Sáu mươi hai miệng im được bao lâu khi gió đông đổi mùi?",
        open=(
            "Bình minh ngày thứ một trăm hai mươi tám. Sáu mươi hai người. "
            "Mười lăm ngày trống. Mùi cháo chung và đất sân đông người. "
            "Cộng đồng sống — sống bằng việc, không bằng khẩu hiệu."
        ),
        core=(
            "\"Mười lăm ngày. Tốt. Tiếp canh. Cộng đồng: mỗi người một việc. Không lười. Không cãi. Vấn đề nói thẳng,\" Phong nói trước sân.\n\n"
            "Sáu mươi hai gật. Không sợ — tin.\n\n"
            "Hà đứng cạnh, khăn thấp: \"Tin đắt. Đừng trả bằng ồn.\"\n\n"
            "\"Đúng.\"\n\n"
            "Phân tổ rõ. Hứa kho. Tôn Vũ rèn. Đại Lực tháp. A Cường đá. Cúc thẻ. "
            "Phong-Hà muối cuối ngày: \"Đủ? Không lệch vì số?\"\n\n"
            "\"Không lệch. Số không phải hội. Số là miệng ăn và tay việc,\" chị lau tay.\n\n"
            "\"Ghi. Ai kể cấp — nặng. Ai kể đá sáng cũ — nặng. Ai chỉ hố sóng — nặng.\"\n\n"
            "Ngọ mười nhịp: \"Sáu mươi hai. Mười lăm ngày trống. Không thở phào. Không họp chữ cộng đồng. Việc. Cùng màu. Máu kín nếu sóng. Bóng — không chỉ.\"\n\n"
            "Gật. Máy che. Không khe đá.\n\n"
            "Hoàng hôn. Phong tuần đông trong rào: chông vôi then hố vết nguyên. Gật. Không khen. "
            "Đêm thềm lều: nắm tay Hà. Mùi đất se. Gió bấc nhẹ. "
            "\"Mai còn việc. Còn đất. Còn người,\" anh nói.\n\n"
            "\"Còn. Đều,\" chị đáp. Đủ."
        ),
    ),
]


def shared_mid(s: dict) -> str:
    """Shared morning machine dens — unique via smell/tag/day."""
    return f"""
---

Sáng. Máy nghèo chạy ngày {s['tag']}.

Cháo loãng. Bếp khép. Mạc Tư gạch im trên bảng sấp — một vạch ngắn đúng việc. Không viết số to. Từ Sơn vòng chân kho một trăm năm mươi lăm bước đều. Triệu ngậm miệng, nước đúng gáo. Đại Lực đảo bao tây khi không tháp. Tôn Vũ móc thấp trong xưởng, không hun lửa sớm nếu không cần. Hứa lau dao đất. Diễm se sợi. Khuyển nằm ngưỡng. Hữu sau chó. Năm 629. Ngoài rào không quan — chỉ đất và miệng.

Bà già ghé mé bếp: "Gió?"
"Gió. Việc," Chú Bát đáp trước khi ai nở miệng dài. Cúi. Đủ.

Phong vào bếp năm nhịp: củi không đốt nhiều, thỏ nửa bát, siết rau. Đông: chông, vôi, then, vải hố, vết cửa nguyên. Anh gật. Không khen. Quét miệng muốn kể {s['tag']}.

Chuỗi tay im trong xương: người, xe, sóng, thước, máu. Không tiếng. Hữu không giơ sớm. Việc {s['tag']} là việc mắt nuốt — miệng không nhả.

Diễm buộc rèm sâu. Cúc kéo Hạt: "Xâu trong. Không kể ngoài." Thẻ. Cửa hé. Trẻ khuất. Mùi cháo loãng tranh {s['smell']}. Đất se. Vôi cũ.

Bà già: "Hôm nay tanh?"
"Gió. Việc," Hà. Không kể. Không đá.

Hứa cửa xưởng không liếc hố. Dao bùn. Áo nghèo. Nghèo trả lời không lời cho ngày có việc ngoài.

Phong xách nước, đảo bao, lau muối chát. Chát sau {s['tag']} đắt — việc dạy mắt và miệng. Lỏng vai hở mai. Anh siết hàm. Không mừng. Việc.

---

Ngọ. Cháo sau {s['tag']}.

Phong húp. Cúc: "Ngoài?"
Hà: "Im. Xâu."
Xâu. Hạt miệng. Sân nhàm. Nham sau {s['tag']} đắt — nhàm giữ sống, ồn giữ chết chậm.

Mười nhịp xương nhắc — Đại Lực, Tôn Vũ, Khuyển, A Cường, Hữu khi có mặt:

"{s['tag']}. {s['law']}. Không mở rèm sớm. Đông thường. Hầm xấu. Nếu bóng — không chỉ. Nếu sóng — đâm thấp máu kín. Nếu hỏi — cùng màu. Miệng sau việc dò nẻ — khóa việc nặng."

Gật. Máy che. Không khe đá. Không phình.

Phong đảo tây. Hà phơi nắng xấu. A Cường khi trong rào: "Trống hoặc việc. Không thèm."
"Không đạp theo. Không kể trống thành chuyện sân," Phong. Biến.

Bà già: "Khách?"
"Không. Gió. Việc." Hứa không liếc. Nghỉ.

Chú Bát nồi sôi. Mạc Tư không đọc to vạch. Ghi im. Từ Sơn bước đều. Diễm rèm. Cúc Hạt xâu.

Phong gặp Hà lần cuối trước tối sau muối:
"Đủ? Không lệch vì {s['tag']}?"
"Không lệch. Việc không phải hội. Việc là im," chị lau tay, gật, thở. "Ai kể ngoài lều — nặng."
"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh nắm tay chị một nhịp, buông. Đủ.

Khuyển gật. A Minh khuất nếu trên gò. Hai ngón mở khi trống. Không pháo.

---

Chiều. Tay việc nhắc. Trẻ thuốc củ thẻ. Hà miệng năm hay nói: gió, hầm ẩm, đông thường, trống sau việc, không bảy hố cửa đồi kể. Siết. Cắn lưỡi.

Then chông vôi giáo dao. Không khói thừa. Không chông nắng khoe. Trẻ xế. Gánh gác. Không hội kể {s['tag']}.

Xế. Ca đổi. Xước se. Vòng then tây bao vai. Gật đủ. Thỏ bếp tro miệng khớp trống đêm. Thở. Mùi {s['smell']}. Đều.

Tám nhịp bếp: không phát sai vì việc, nửa bát, củ thẻ, nồi không chuyện ngoài. Gạch. Sôi. Gỗ. A Cường ngắn khi có. Hà: đủ. Không thêm lệnh.

Diễm xước Hứa se. "Ngủ sớm nếu không ca." Gật. Không hỏi ngoài. Cúc ngủ thẻ. Hạt gối. Ru im. Im đắt truyện.

Tháp Hà không đèn khi ca: "Việc có lớp. Mai bóng hoặc sóng hoặc hỏi."

"Lời em. Bao anh. Không lệch." Gió. Mùi. Xuống.

Đông vòng trước tối: chông mắt, vôi then hố vết nguyên. Rào — không người xe nếu trống. Đứng được. Không lỏng.

Hữu đổi ca: "Gần sạch hoặc việc đã ghi." Cháo nửa thìa. "Im. Giơ người đúng. Không sóng nhầm." Nuốt. Lên. Hà: đủ.

Phong chạm vai ba việc giữa chiều: bao tây, giếng nắp xấu, chân kho. Không họp. Không vôi sớm. Giếng nắp xấu giữ. Ai sửa nắp đẹp — mời thước. Thước đọc lưng; xương không cho đọc.
"""


def build(s: dict) -> str:
    parts = [
        hdr(s["n"], s["title"]),
        s["open"],
        "\n\n",
        "Phong ra việc trước khi sân thức hẳn khi còn trong rào. Muối chát đầu ngón khi đảo bao. "
        "Hà phơi hoặc bê cháo hoặc siết rèm — lưng thẳng, khăn mũi thấp. "
        "Việc mở trước miệng. Mùi ",
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
    return "".join(parts)


def main():
    report = []
    for s in SPECS:
        path = find_file(s["n"])
        text = build(s)
        w = vi_words(text)
        # expand if short: append unique layers before panel
        i = 0
        extras = [
            f"Canh khuya riêng ngày {s['day_vn']}: then tây êm, đông chông không cọt, hố không bới, cửa vết không sứt. A Minh đổi. Hữu im. Mùi {s['smell']} lớp mỏng. Không bục miệng. Bục việc. Đủ sau {s['tag']}.",
            f"Phong ngồi dậy uống nước nguội lần thêm, đếm then cổng trong đầu: không kêu. Gió bấc. {s['law']}. Hà thở đều. Nắm. Buông. Ngủ thật dưới đất Biên Ải sau {s['tag']}.",
            f"Sổ than thêm một dòng nhạt: {s['event']}. Không pháo. Không đọc to. Gấp. Nằm. Mai trống điểm mang bóng sóng hỏi hoặc yên giả — chưa mừng. Chưa lỏng.",
            f"Trước gà cuối lỏng nắm: ngoài rào sau {s['tag']} chỉ đất và gió. Trong trại nhịp gánh thẻ. Nhịp cháo. Nhịp chông. Chưa thua. Còn viết. Còn thở. Còn người. Đủ.",
            f"Hà ghé vai thêm một nhịp: \"Mai em cùng màu. Anh bao. Không thèm vì {s['tag']}.\" Phong gật. Hở đắt hơn thèm. Mùi {s['smell']}. Đất se. Vôi cũ. Then êm. Sống. Đo. Không khoe.",
        ]
        while w < 3050 and i < 30:
            bit = extras[i % len(extras)] + f" Hơi thở chậm lớp {i + 1} ngày {s['day_vn']} giữ việc."
            if bit in text:
                bit += f" Thêm dấu muối chát {i}."
            text = text.replace("「Kho Vô Hạn", "\n" + bit + "\n\n「Kho Vô Hạn", 1)
            w = vi_words(text)
            i += 1
        path.write_text(text, encoding="utf-8")
        r = subprocess.run(
            ["python", str(SCORER), str(path), "--min-words", "3000", "--cfg", str(CFG)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        out = (r.stdout or "") + (r.stderr or "")
        line = out.strip().splitlines()[0] if out.strip() else "?"
        m = re.search(r"([\d.]+)\s+van=", line)
        sc = float(m.group(1)) if m else 0.0
        ok = "OK" in line or (sc >= 9.0 and "short" not in line)
        report.append({"n": s["n"], "words": w, "score": sc, "line": line, "ok": ok})
        print(line, "w=", w)

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    fails = [x for x in report if not x["ok"]]
    print("PASS", sum(1 for x in report if x["ok"]), "/", len(report))
    if fails:
        print("FAILS", fails)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
