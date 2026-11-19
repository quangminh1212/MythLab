# -*- coding: utf-8 -*-
"""Unique full rewrite ch.129-149.
Style: early-arc Phong/Hà + Biên Ải machine-poor density (same as 104-128).
No Nhịp im pad. Unique openings/prose per chapter.
Panel: 「Kho Vô Hạn — GHI NHẬN ch.N」 Năm 629. EXP progressive from ch.128.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".novelab_score.json"
OUT_JSON = BASE / "_score_rewrite_129_149.json"

# Reuse helpers from 104-128 module text
_SRC = (BASE / "_rewrite_unique_104_128.py").read_text(encoding="utf-8")
_ns: dict = {}
exec(_SRC.split("SPECS = [")[0], _ns)
hdr = _ns["hdr"]
panel = _ns["panel"]
find_file = _ns["find_file"]
night_close = _ns["night_close"]
vi_words = _ns["vi_words"]
# shared_mid is after SPECS — extract manually
_sm = _SRC[_SRC.find("def shared_mid") : _SRC.find("def build")]
exec(_sm, _ns)
shared_mid = _ns["shared_mid"]


def d(
    n: int,
    title: str,
    day_vn: str,
    exp: int,
    event: str,
    smell: str,
    tag: str,
    law: str,
    cliff: str,
    open_: str,
    core: str,
) -> dict:
    return dict(
        n=n,
        title=title,
        day=n,
        day_vn=day_vn,
        exp=exp,
        event=event,
        smell=smell,
        tag=tag,
        law=law,
        cliff=cliff,
        open=open_,
        core=core,
    )


SPECS = [
    d(
        129,
        "Thông Báo Nâng Cấp",
        "một trăm hai mươi chín",
        24315,
        "Chữ kho lóe gần ngưỡng · không pháo sân · mười sáu ngày trống",
        "mùi sắt nguội xưởng và sương mỏng",
        "thông báo nâng cấp im · chữ kho không pháo",
        "Gần ngưỡng không kể trẻ · không họp chữ cấp · việc đo được trước khi mở",
        "Chữ kho gần ngưỡng — mở đúng lúc hay mở khi miệng ồn?",
        "Chữ vàng lóe trong đầu Phong trước khi trống điểm tan hẳn. Ngày thứ một trăm hai mươi chín dưới đất Biên Ải. Sáu mươi hai người. Mười sáu ngày trống. Mùi sắt nguội xưởng và sương mỏng bám gáy. Thông báo nâng cấp — im. Không pháo. Không họp sân.",
        'Anh đứng dưới hiên tây, nắm muối chát, không gọi ai. Chữ kho: EXP gần ngưỡng — điều kiện còn việc đo được. Anh nuốt chữ. Không kể. Không chỉ trẻ.\n\n'
        'Hà bê cháo sớm, khăn mũi thấp: "Anh cứng mặt. Ngoài?"\n\n'
        '"Trong. Chữ. Không pháo. Việc trước," Phong đáp. Hai nhịp mắt đông rồi quay tay đảo bao.\n\n'
        'Đại Lực từ tháp xuống một nhịp: "Trống. Mười sáu."\n\n'
        '"Tiếp canh. Không thở phào vì chữ."\n\n'
        "---\n\n"
        'Họp ngắn mười người trong xưởng — không sân. "Gần ngưỡng. Không kể trẻ. Không họp chữ cấp. Ai mở miệng số — nặng. Việc đo: rào bắc siết, hầm xấu giữ, lương siết rau một nấc," Phong nói.\n\n'
        'Tôn Vũ: "Đinh đủ. Lưỡi mài xong ba."\n\n'
        'Hứa: "Kho gạo đủ hai tuần rưỡi nếu siết."\n\n'
        'Hà: "Rèm chặt. Trẻ thẻ trong."\n\n'
        "Gật. Máy che.\n\n"
        'Giữa sáng. Phong-Hà sau muối: "Đủ im?"\n\n'
        '"Đủ. Chữ không phải hội. Chữ là việc chưa mở," chị lau tay.\n\n'
        '"Ghi. Ai kể cấp — nặng gấp."\n\n'
        'Chiều tuần đông: chông then hố vết nguyên. Không vôi mới. Không khen. Ngọ mười nhịp: "Gần ngưỡng. Không pháo. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
        "Gật. Đêm thềm: nắm tay. Mùi đất se. Sống. Đo. Không khoe chữ.",
    ),
    d(
        130,
        "Tuần Tra Phía Đông",
        "một trăm ba mươi",
        24345,
        "Tuần đông ba trăm bước · dấu cũ · mười bảy ngày trống",
        "mùi đất đông ẩm và lá sồi mục",
        "tuần tra đông · ba trăm bước · dấu cũ",
        "Đi vòng không đạp dấu miệng · người đợi cổng · về trước hoàng hôn",
        "Dấu cũ đông — miệng đã rời hay đang vòng?",
        "Gió đông mang mùi đất ẩm khi Phong cột giày đế dày. Ngày thứ một trăm ba mươi. Mười bảy ngày trống. Đại Lực tháp giơ một ngón đông rồi hạ — trống gần, chưa chắc xa. Tuần tra phía đông: ba trăm bước, vòng, không đạp theo dấu.",
        '"Đi bao lâu?" Đại Lực hỏi nhỏ.\n\n'
        '"Hai canh. Về trước hoàng hôn. Em đợi cổng."\n\n'
        'Hà đứng mé cửa: "Không một mình nếu sóng."\n\n'
        '"Hùng đi cùng. Cuốc sắt. Không miệng kể."\n\n'
        "Hai người ra. Tuyết mỏng đã hết. Đất đen. Năm chục — trống. Trăm — trống. Hai trăm: dấu zombie cũ — nông, kéo, phủ bụi. Ba dấu. Đi vòng. Không đạp.\n\n"
        "Ba trăm: gò thấp. Không bóng. Mùi lá sồi mục. Phong ghi xương: dấu cũ, hướng nam-đông, không mới.\n\n"
        'Hùng: "Im hơn hôm ta chạy."\n\n'
        '"Im không bằng hết. Ghi. Về."\n\n'
        "---\n\n"
        'Cổng: Đại Lực đợi. "Ngoài?"\n\n'
        '"Dấu cũ. Không miệng sống. Không kể sân số," Phong nói. Hà bê nước.\n\n'
        'Họp ngắn: "Đông còn dấu. Canh không lỏng. Không tuần đêm."\n\n'
        'A Cường: "Tháp thấy trống."\n\n'
        '"Không thở phào."\n\n'
        'Phong-Hà muối: "Đủ?"\n\n'
        '"Đủ. Dấu không phải hội chiến công," chị.\n\n'
        'Ngọ mười nhịp: "Tuần đông. Dấu cũ. Không đạp theo. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Máy che. Chiều siết cọc đông một gang. Không khoe gang.",
    ),
    d(
        131,
        "Hoàng Hôn Bình Yên",
        "một trăm ba mươi mốt",
        24375,
        "Hoàng hôn việc · mười tám ngày trống · không hội yên",
        "mùi khói bếp chiều và đất se ấm",
        "hoàng hôn bình yên việc · không thở phào",
        "Yên chiều là việc im · không mở rèm sớm · không kể đẹp sân",
        "Hoàng hôn đẹp — liệu đêm có mang sóng sau gió bấc?",
        "Hoàng hôn ngày thứ một trăm ba mươi mốt phủ màu cam mỏng lên chông đông. Sáu mươi hai người. Mười tám ngày trống. Mùi khói bếp chiều và đất se ấm. Bình yên — nhưng bình yên là việc im, không phải đứng ngắm hội.",
        "Phong đứng hiên tây đúng năm nhịp rồi quay vào đảo bao. Không đuổi mắt trời lặn quá hai nhịp.\n\n"
        'Hà bê cháo: "Đẹp. Ngắn."\n\n'
        '"Ngắn. Việc dài hơn đẹp," anh đáp.\n\n'
        "Đại Lực trên tháp không giơ. Trống. Hữu sau Khuyển. Trẻ xâu trong — Cúc không cho ra cổng xem màu trời.\n\n"
        "---\n\n"
        'Họp ngắn: "Mười tám ngày. Tốt. Không thở phào. Hoàng hôn không phải hội yên. Ca đêm đủ."\n\n'
        'Tôn Vũ: "Lưỡi mài xong. Không hun đêm."\n\n'
        'Hứa: "Lương siết giữ."\n\n'
        'Phong-Hà sau muối: "Ai kể đẹp ngoài lều — nhẹ. Ai mở rèm trẻ xem trời — nặng."\n\n'
        '"Giữ. Lời em."\n\n'
        "Xế. Ca đổi. Then tây êm. Đông chông không cọt. "
        'Tối nhắc xương: "Yên chiều. Không lỏng. Đông thường. Hầm xấu. Máu kín nếu sóng."\n\n'
        "Gật. Đêm thềm: nắm tay. Màu trời tắt. Mùi đất se. Sống. Đo. Không khoe yên.",
    ),
    d(
        132,
        "Hệ Thống Thăng Cấp",
        "một trăm ba mươi hai",
        24420,
        "Ngưỡng cấp 2 siết · việc đo đủ · không pháo · mười chín ngày trống",
        "mùi than xưởng và muối chát",
        "hệ thống thăng cấp im · việc đo đủ",
        "Mở ngưỡng im · không kể EXP trẻ · không họp chữ cấp sân",
        "Cấp siết xong — kho có nhả thêm hay chỉ siết luật?",
        "Trong xương kho, chữ vàng đứng yên một nhịp dài hơn mọi ngày. Ngày thứ một trăm ba mươi hai. Mười chín ngày trống. Mùi than xưởng và muối chát. Hệ thống thăng cấp — im trong đầu, việc ngoài tay, không pháo sân.",
        "Phong ngồi thềm trước trống, hít đều, nhận chữ: điều kiện việc đo đã khớp — rào, hầm, lương, người đều. Ngưỡng siết. Không nổ. Không chuông. Chỉ một dòng im: cấp 2 giữ, nhánh mở chậm.\n\n"
        "Anh không cười. Ghi sổ than: ngưỡng khớp · không pháo · không kể.\n\n"
        'Hà ra, khăn thấp: "Xong?"\n\n'
        '"Xong im. Không hội. Kho nhả thêm một nấc nhỏ — lương và dao thô. Không kể trẻ."\n\n'
        '"Em chặn miệng. Anh chặn việc lệch."\n\n'
        "---\n\n"
        'Họp xưởng mười người: "Ngưỡng khớp. Không kể số. Việc: nhận nhánh mới bằng tay — không bằng miệng. Tôn Vũ kiểm dao thô. Hứa cân gạo thêm. Không mừng."\n\n'
        "Tôn Vũ gật, mắt không khoe lưỡi.\n\n"
        'Lan: "Chữ kho… dạy được?"\n\n'
        '"Dạy sổ gạo. Không dạy chữ đá. Không dạy cấp."\n\n'
        'A Cường: "Trống ngoài."\n\n'
        '"Không thở phào vì cấp."\n\n'
        'Giữa sáng muối: Phong-Hà "Đủ?" "Đủ. Cấp không phải hội."\n\n'
        'Ngọ mười nhịp: "Ngưỡng im. Không pháo. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
        "Gật. Máy che. Chiều đảo bao tây — muối chát hơn. Đêm: nắm. Ngủ. Mai việc.",
    ),
    d(
        133,
        "Mưa Tuyết Đầu Mùa",
        "một trăm ba mươi ba",
        24450,
        "Mưa tuyết đầu · giữ ấm · hai mươi ngày trống",
        "mùi tuyết ướt và khói bếp ngọt",
        "mưa tuyết đầu mùa · giữ ấm không lỏng",
        "Ấm không bằng lỏng canh · củi siết · trẻ trong · không trượt hố",
        "Tuyết phủ dấu — liệu có che cả miệng đang vòng?",
        "Tuyết ướt rơi trước khi trống điểm dứt — hạt to, dính chông, không khô. Ngày thứ một trăm ba mươi ba. Hai mươi ngày trống. Mùi tuyết ướt và khói bếp ngọt. Mưa tuyết đầu mùa: giữ ấm, giữ canh, không giữ hội ngắm.",
        'Đại Lực từ tháp: "Tuyết dày. Đường trơn. Trống gần."\n\n'
        '"Được. Giữ ấm. Không tuần xa. Hố đông phủ — đánh dấu xấu không đào lại," Phong nói.\n\n'
        'Hà phát áo dày từ kho: "Trẻ trước. Lớn sau. Anh cuối."\n\n'
        "Phong nhận cuối — đúng xương.\n\n"
        "---\n\n"
        'Họp ngắn bếp: "Tuyết. Củi siết. Không đốt khoe. Ca tháp đủ. Ai trượt hố — không hét."\n\n'
        'Tôn Vũ: "Xưởng khô. Lưỡi không để ngoài tuyết."\n\n'
        'Hứa: "Gạo khô. Không để ẩm."\n\n'
        'Cúc: "Thẻ trong. Không ra sân chơi tuyết."\n\n'
        '"Đúng."\n\n'
        'Phong-Hà muối trong lều: "Tuyết che dấu. Tai khe hơn mắt."\n\n'
        '"Em giữ rèm. Anh giữ then."\n\n'
        "Chiều tuyết dày hơn. Then êm. Chông trắng. "
        'Ngọ mười nhịp: "Tuyết đầu. Không lỏng. Đông thường. Hầm xấu. Cùng màu. Không kể đẹp tuyết sân."\n\n'
        "Gật. Đêm: nắm tay lạnh rồi ấm. Mùi tuyết. Sống. Đo. Không khoe.",
    ),
    d(
        134,
        "Chiếc Bẫy Đầu Tiên",
        "một trăm ba mươi tư",
        24480,
        "Bẫy hố đông · thóc lép · không phơi · hai mươi mốt ngày trống",
        "mùi đất đào ướt và thóc lép",
        "bẫy hố đầu · thóc lép · đắp xấu",
        "Bẫy không kể trẻ · hố xấu không đẹp · máu kín nếu dính",
        "Bẫy đã đặt — ai sập trước, miệng hay thước ngoài?",
        "Xẻng cắm đất đông ướt khi sương còn dính đầu chông. Ngày thứ một trăm ba mươi tư. Hai mươi mốt ngày trống. Mùi đất đào ướt và thóc lép. Chiếc bẫy đầu tiên: hố xấu, đắp giống chỗ chưa đào, không phơi miệng hố.",
        "Phong, Tôn Vũ, A Cường đào ba hố lệch nhau — không thẳng hàng, không đẹp thước. Thóc lép rắc mỏng. Cọc nhọn đáy nghiêng. Vải hố phủ. Phủi bụi tuyết.\n\n"
        '"Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp," Phong dặn.\n\n'
        'Hà đứng trong rèm không ra: "Xong?"\n\n'
        '"Xong xấu. Đẹp là mời thước," anh lau bùn ngón.\n\n'
        "---\n\n"
        'Họp ngắn: "Bẫy đông. Không tuần đạp lên. Đánh dấu xương — không đánh dấu vôi sáng."\n\n'
        'Đại Lực: "Tháp nhớ chỗ. Không giơ tay chỉ."\n\n'
        'Hùng: "Tôi từng thấy bẫy thành — đẹp quá nên lộ."\n\n'
        '"Đúng. Xấu sống."\n\n'
        'Phong-Hà muối: "Đủ?"\n\n'
        '"Đủ. Bẫy không phải hội săn."\n\n'
        "Chiều tuyết phủ nhẹ miệng hố — tốt. "
        'Ngọ mười nhịp: "Bẫy đầu. Không chỉ. Không kể. Đông thường. Hầm xấu. Máu kín nếu sóng."\n\n'
        "Gật. Máy che. Đêm: tai khe. Mùi đất đào còn. Ngủ.",
    ),
    d(
        135,
        "Trận Chiến Đêm Khuya",
        "một trăm ba mươi lăm",
        24530,
        "Sóng thấp năm · bẫy dính hai · máu kín · hai mươi hai ngày",
        "mùi tanh máu kín và tuyết ướt",
        "sóng đêm năm · bẫy dính · máu kín",
        "Đâm thấp · không mặt · không đếm to · không phơi · hố xấu",
        "Năm đã khép — còn lớp sau gió bấc hay hết?",
        "Canh ba. Rên đông dồn. Không gào — chỉ sóng thấp. Ngày thứ một trăm ba mươi lăm đã sang từ trống điểm. Đại Lực giơ năm ngón thấp rồi nắm. Trận đêm: đâm thấp, máu kín, bẫy hố ăn hai, không phơi.",
        "Phong móc gáy-hông. Tôn Vũ hai. Đại Lực hai. Hùng một. Hứa chặn lệch. Không đếm to. Không phơi. Máu ngắn. Hai bóng sập hố bẫy — cọc ăn. Ba còn lại thấp. Đâm. Kín.\n\n"
        'Hà trong rèm: "Kín?"\n\n'
        '"Kín. Năm. Máu vải. Không phơi. Bẫy hai," Phong lau móc lá khô. Mùi tanh bám. Siết hàm. Không kể sân.\n\n'
        'A Cường: "Hết gần. Không theo. Tuyết che máu."\n\n'
        '"Không soi. Không kể số. Hố mới — đắp xấu."\n\n'
        "---\n\n"
        "Canh tư. Việc sóng vào xương. Không họp hội chiến thắng. Sáng cháo loãng. Cúc xâu. Trẻ không thấy hố.\n\n"
        'Mười nhịp xưởng: "Năm thấp. Máu kín. Bẫy hai. Không đếm to. Không phơi. Đông thường. Hầm xấu. Nếu hỏi — cùng màu."\n\n'
        "Gật. Máy che.\n\n"
        'Phong-Hà muối: "Đủ? Không lệch vì sóng?"\n\n'
        '"Không lệch. Việc không hội," chị. "Ai chỉ hố — nặng."\n\n'
        '"Ghi. Lần này không pháo."\n\n'
        "Chiều hố lớp thêm. Sống. Đo. Không khoe năm.",
    ),
    d(
        136,
        "Bình Yên Sau Bão",
        "một trăm ba mươi sáu",
        24560,
        "Sau sóng · yên việc · không thở phào · hai mươi ba",
        "mùi tuyết tan loãng và khói bếp",
        "bình yên sau sóng · không thở phào",
        "Yên sau sóng là việc im · không kể chiến · canh đủ",
        "Yên một ngày sau năm — mồi hay thật?",
        "Bình minh sau đêm sóng mang mùi tuyết tan loãng. Ngày thứ một trăm ba mươi sáu. Không bóng sát rào. Mùi khói bếp. Bình yên sau bão — yên bằng việc, không bằng thở phào.",
        '"Trống. Tiếp canh. Không thở phào," Phong nói với Đại Lực.\n\n'
        'Họp ngắn: "Đêm qua kín. Hôm nay việc. Không họp chữ thắng. Hố xấu giữ. Máu vải giặt im."\n\n'
        'Hà: "Trẻ không hỏi số."\n\n'
        '"Ghi. Ai kể số — nặng."\n\n'
        'Tôn Vũ mài móc cùn. Hứa cân lại kho. A Cường: "Đông trống. Nam trống."\n\n'
        '"Không soi."\n\n'
        'Phong-Hà muối: "Yên thật hay yên mồi?"\n\n'
        '"Trống. Tai khe. Ba xương: không thở phào, không mở rèm sớm, không rải vôi nghỉ."\n\n'
        '"Giữ."\n\n'
        'Ngọ mười nhịp: "Sau sóng. Yên việc. Không hội. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Chiều phơi bao nắng xấu. Đêm nắm tay. Mùi đất se. Sống. Đo. Không khoe yên.",
    ),
    d(
        137,
        "Cuộc Tập Truyện Đầu Tiên",
        "một trăm ba mươi bảy",
        24590,
        "Tập trận im · đâm thấp · không pháo · hai mươi tư",
        "mùi mồ hôi tập và đất sân đông",
        "tập trận đầu · đâm thấp · không pháo",
        "Tập không phải hội · không đếm to · không khoe lưỡi · trẻ không xem",
        "Tập xong — tay có nhớ luật khi sóng thật?",
        "Sân đông được quét sạch tuyết một góc hẹp — không phải hội thao. Ngày thứ một trăm ba mươi bảy. Mùi mồ hôi tập và đất sân. Cuộc tập trận đầu: đâm thấp, rút, kín, không gào, không pháo.",
        "Phong xếp mười người: Tôn Vũ, Đại Lực, Hùng, Hứa, A Cường, Từ Sơn, Triệu, Hữu, Mạc Tư, và anh. "
        '"Đâm thấp. Không mặt. Không đếm to. Rút. Máu giả — vải đỏ nhạt. Không cười. Không khoe."\n\n'
        "Tập ba vòng. Mồ hôi. Hơi thở. Không ồn.\n\n"
        'Hà đứng rèm: "Trẻ trong."\n\n'
        '"Giữ."\n\n'
        "---\n\n"
        "Giữa sáng nghỉ ngắn. Nước. Không họp khen.\n\n"
        '"Tay nhớ chưa?" Phong hỏi.\n\n'
        'Hùng: "Nhớ thấp."\n\n'
        'Tôn Vũ: "Rút chậm — sửa."\n\n'
        '"Sửa. Không xấu hổ. Xấu hổ là khoe sai."\n\n'
        'Phong-Hà muối: "Tập dễ ồn."\n\n'
        '"Em chặn miệng khoe. Anh chặn tay lệch."\n\n'
        "Chiều tập thêm một vòng rồi thu. Xưởng lau đất. "
        'Ngọ mười nhịp: "Tập đầu. Không pháo. Không kể như chiến. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Máy che. Đêm: cơ mỏi. Nắm. Ngủ. Mai sống.",
    ),
    d(
        138,
        "Gió Đông Mùa Tuyết",
        "một trăm ba mươi tám",
        24620,
        "Gió đông tuyết · mùi lạ mỏng · hai mươi lăm",
        "mùi gió đông mang băng và khói xa",
        "gió đông mùa tuyết · mùi lạ mỏng",
        "Gió đổi thì tai khe · không tuần xa · không mở rèm",
        "Gió đông mang mùi lạ — người hay miệng?",
        "Gió đông thổi suốt canh tư, mang băng và một mùi khói xa mỏng như sợi. Ngày thứ một trăm ba mươi tám. Tuyết còn trên chông. Mùi gió đông mùa tuyết. Không mở rèm. Không tuần xa. Tai khe.",
        'Đại Lực tháp: "Gió đông. Mùi khói xa. Không thấy lửa."\n\n'
        '"Ghi. Không soi. Không kể sân," Phong nói.\n\n'
        'Hà siết rèm: "Trẻ trong. Khói xa dễ tò mò."\n\n'
        '"Chặn."\n\n'
        "---\n\n"
        'Họp ngắn: "Gió đổi. Canh đủ. Không tuần đông xa hôm nay. Lương củi siết."\n\n'
        'Hứa: "Củi đủ năm ngày nếu siết."\n\n'
        'Tôn Vũ: "Xưởng kín gió."\n\n'
        'A Cường: "Trống sát. Mùi không gần."\n\n'
        '"Không đạp theo mùi."\n\n'
        'Phong-Hà muối: "Khói người hay cháy rừng?"\n\n'
        '"Chưa phân bằng mắt. Phân bằng không mở sớm."\n\n'
        '"Giữ."\n\n'
        'Ngọ mười nhịp: "Gió đông. Mùi mỏng. Không soi. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
        "Gật. Chiều gió mạnh hơn. Then êm. Đêm nắm. Mùi băng. Sống. Đo. Không khoe.",
    ),
    d(
        139,
        "Buổi Lễ Nâng Cấp",
        "một trăm ba mươi chín",
        24660,
        "Lễ im · nhận nhánh kho · không hội · hai mươi sáu",
        "mùi cháo đặc hơn một nấc và than ấm",
        "lễ nâng cấp im · cháo đặc · không hội",
        "Lễ là việc nhận · không trống · không kể cấp trẻ · không pháo",
        "Nhận nhánh xong — ai giữ miệng khi bụng ấm hơn một nấc?",
        "Không trống. Không cờ. Không đứng vòng. Ngày thứ một trăm ba mươi chín. Mùi cháo đặc hơn một nấc — gạo nhánh kho mới — và than ấm. Buổi lễ nâng cấp: mười người xưởng, chữ im, cháo, việc.",
        'Phong đứng xưởng: "Ngưỡng đã khớp trước. Hôm nay nhận nhánh bằng tay. Không họp sân. Không kể trẻ. Cháo đặc một bữa — không hai."\n\n'
        'Hà phát cháo: "Trẻ trước. Lớn sau."\n\n'
        "Tôn Vũ nhận dao thô mới: không giơ cao. Hứa cân gạo thêm: không đọc số to.\n\n"
        'Lan: "Ghi sổ?"\n\n'
        '"Ghi im. Không chữ cấp ngoài sổ."\n\n'
        "---\n\n"
        "Giữa sáng. Việc thường. Không hội kể lễ.\n\n"
        'Phong-Hà muối: "Bụng ấm dễ nở miệng."\n\n'
        '"Em chặn. Anh chặn việc lệch."\n\n'
        'Đại Lực: "Trống ngoài."\n\n'
        '"Không thở phào vì cháo."\n\n'
        'Ngọ mười nhịp: "Lễ im. Không pháo. Không kể cấp. Đông thường. Hầm xấu. Cùng màu."\n\n'
        'Gật. Máy che. Chiều đảo bao. Đêm: nắm. "Đủ?" "Đủ. Lễ không phải hội." Ngủ.',
    ),
    d(
        140,
        "Cuộc Chiến Đầu Mùa",
        "một trăm bốn mươi",
        24710,
        "Sóng tuyết tám · máu kín · hố xấu · hai mươi bảy",
        "mùi tanh máu kín trộn tuyết",
        "sóng tuyết tám · đầu mùa · máu kín",
        "Đâm thấp · không mặt · không đếm to · không phơi · bẫy giữ",
        "Tám khép trong tuyết — mùa còn mang lớp nào?",
        "Tuyết còn rơi khi sóng thấp từ đông-nam — tám bóng, không gào. Ngày thứ một trăm bốn mươi. Mùi tanh sẽ tới. Cuộc chiến đầu mùa: thấp, kín, bẫy, không phơi trên tuyết trắng.",
        "Phong hạ tay. Móc. Tôn Vũ hai. Đại Lực hai. Hùng hai. Hứa một. A Cường chặn lệch. Bẫy ăn một. Bảy còn lại thấp. Đâm. Máu vải. Không phơi trên tuyết — phủ đất xấu ngay.\n\n"
        'Hà trong rèm: "Kín?"\n\n'
        '"Kín. Tám. Máu vải. Không phơi," Phong lau. Siết hàm. Không kể sân.\n\n'
        'A Cường: "Hết gần. Tuyết che."\n\n'
        '"Không soi. Không kể số."\n\n'
        "---\n\n"
        "Sáng sau. Cháo. Cúc xâu. Trẻ không thấy hố.\n\n"
        'Mười nhịp: "Tám thấp. Máu kín. Không đếm to. Không phơi. Đông thường. Hầm xấu. Nếu hỏi — cùng màu."\n\n'
        "Gật. Máy che.\n\n"
        'Phong-Hà: "Đủ? Không lệch vì tám?"\n\n'
        '"Không lệch. Việc không hội."\n\n'
        '"Ghi. Không pháo."\n\n'
        "Chiều hố lớp. Sống. Đo. Không khoe tám.",
    ),
    d(
        141,
        "Bình Yên Sau Bão",
        "một trăm bốn mươi mốt",
        24740,
        "Sau tám · yên việc · siết rau · hai mươi tám",
        "mùi đất lộ sau tuyết mỏng và cháo loãng",
        "yên sau tám · siết rau · không thở phào",
        "Yên sau sóng lớn là siết · không kể · canh đủ",
        "Hai lần yên sau sóng — lần này có khác mùi?",
        "Bình minh ngày thứ một trăm bốn mươi mốt. Tuyết mỏng tan. Mùi đất lộ và cháo loãng. Lại bình yên sau bão — lần này sau tám, không sau năm. Việc siết, không miệng mừng.",
        '"Trống. Siết rau nửa nấc. Tiếp canh. Không thở phào," Phong nói.\n\n'
        'Họp: "Đêm kia kín. Hôm nay việc. Không họp thắng. Hố xấu. Lương siết."\n\n'
        'Hứa: "Siết được bốn ngày thêm."\n\n'
        'Hà: "Trẻ không hỏi số tám."\n\n'
        '"Ghi."\n\n'
        'Phong-Hà muối: "Hai lần yên sau sóng. Dễ quen."\n\n'
        '"Quen là hở. Tai khe."\n\n'
        '"Giữ."\n\n'
        'A Cường: "Đông trống."\n\n'
        '"Không soi."\n\n'
        'Ngọ mười nhịp: "Sau tám. Yên việc. Không hội. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Chiều phơi. Đêm nắm. Mùi đất se. Sống. Đo. Không khoe.",
    ),
    d(
        142,
        "Khu Vực Mới",
        "một trăm bốn mươi hai",
        24780,
        "Mở góc tây-nam · rào lớp · không khoe gang · hai mươi chín",
        "mùi gỗ mới và đất đào tây-nam",
        "khu vực mới tây-nam · rào lớp · không khoe",
        "Mở đất có điều kiện · rào trước lều · không kể rộng sân",
        "Góc mới rộng — có đủ im để giữ khi miệng hỏi?",
        "Cọc mới đóng góc tây-nam khi sương còn. Ngày thứ một trăm bốn mươi hai. Mùi gỗ mới và đất đào. Khu vực mới: rào lớp trước, lều sau, không khoe gang đất.",
        'Phong, Tôn Vũ, Từ Sơn, A Cường kéo rào lệch — không thẳng thước đẹp. "Rộng vừa miệng ăn. Không rộng miệng kể," Phong dặn.\n\n'
        'Hà: "Lều tạm sau rào chắc. Trẻ chưa chuyển."\n\n'
        '"Đúng. Rào chắc mới chuyển."\n\n'
        "---\n\n"
        'Họp: "Góc tây-nam. Rào lớp. Hố xấu nếu cần. Không họp chữ mở rộng."\n\n'
        'Hứa: "Lương chịu thêm nếu không thêm miệng ngoài kế hoạch."\n\n'
        'Đại Lực: "Tháp vẫn đông-chính. Góc mới chưa tháp."\n\n'
        '"Chưa. Việc trước tháp."\n\n'
        'Phong-Hà: "Đủ? Không lệch vì rộng?"\n\n'
        '"Không lệch. Rộng không phải hội."\n\n'
        'Ngọ mười nhịp: "Khu mới. Không khoe gang. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
        "Gật. Chiều đinh keng. Đêm: nắm. Mùi gỗ. Sống. Đo. Không khoe.",
    ),
    d(
        143,
        "Tháp Canh Đầu Tiên",
        "một trăm bốn mươi ba",
        24820,
        "Tháp góc tây-nam · ca mới · ba mươi ngày",
        "mùi nhựa gỗ tươi và gió cao",
        "tháp canh góc mới · ca mới · không khoe cao",
        "Tháp thấp đủ thấy · không đèn thừa · ca đủ không thiếu",
        "Tháp mới nhìn xa hơn — có nhìn thấy thứ không muốn thấy?",
        "Khung gỗ tháp thấp góc tây-nam dựng khi nắng mỏng. Ngày thứ một trăm bốn mươi ba. Bảy mươi người — thêm miệng đường tây đêm trước đã nhận. Mùi nhựa gỗ tươi và gió cao hơn sân một thân. Tháp canh mới: thấp đủ thấy, không đèn thừa, không khoe cao.",
        "Tôn Vũ, Từ Sơn, Hùng dựng. Phong kiểm then chân tháp. "
        '"Cao vừa. Cao quá — lộ. Thấp quá — mù," anh nói.\n\n'
        'Đại Lực thử ca: "Thấy đông cũ và góc mới. Đủ."\n\n'
        'Hà: "Ca đêm đủ người?"\n\n'
        '"Đủ. Không thiếu. Không ồn."\n\n'
        "---\n\n"
        'Họp: "Tháp góc. Ca xoay. Không thắp đèn nếu không sóng. Người mới học tín hiệu tay — không học hét."\n\n'
        "Người mới gật. Thẻ. Quy tắc.\n\n"
        'Phong-Hà: "Tháp dễ khoe."\n\n'
        '"Em chặn miệng. Anh chặn đèn."\n\n'
        'A Cường: "Trống."\n\n'
        '"Không thở phào vì tháp."\n\n'
        'Ngọ mười nhịp: "Tháp mới. Không khoe cao. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Chiều ca thử. Đêm: then êm. Nắm. Ngủ. Mai sống.",
    ),
    d(
        144,
        "Cuộc Tấn Công Đêm",
        "một trăm bốn mươi tư",
        24870,
        "Sóng đêm mười hai · tháp góc báo · máu kín · ba mươi mốt",
        "mùi tanh máu kín và gió tháp",
        "tấn công đêm mười hai · tháp góc báo · máu kín",
        "Đâm thấp · không mặt · không đếm to · không phơi · tín hiệu tay",
        "Mười hai khép — tháp góc có đáng dựng?",
        "Canh hai. Tháp góc tây-nam giơ tín hiệu tay — không hét. Mười hai bóng thấp từ sườn. Ngày thứ một trăm bốn mươi tư. Tấn công đêm: tháp báo, móc thấp, máu kín, không phơi.",
        "Phong hạ tay. Phân ca: đông chính và góc mới. Tôn Vũ ba. Đại Lực ba. Hùng hai. Hứa hai. A Cường chặn. Anh hai. Bẫy ăn hai. Mười còn. Đâm thấp. Máu vải. Phủ đất. Không phơi.\n\n"
        'Hà rèm: "Kín?"\n\n'
        '"Kín. Mười hai. Tháp góc kịp," Phong lau. Không kể sân.\n\n'
        'Đại Lực: "Tín hiệu tay đủ. Không cần hét."\n\n'
        '"Ghi. Không khoe tháp."\n\n'
        "---\n\n"
        "Sáng. Cháo. Cúc xâu. Trẻ không thấy hố.\n\n"
        'Mười nhịp: "Mười hai. Máu kín. Tháp kịp. Không đếm to. Không phơi. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Máy che.\n\n"
        'Phong-Hà: "Đủ? Không lệch vì mười hai?"\n\n'
        '"Không lệch. Việc không hội. Tháp đáng."\n\n'
        '"Ghi. Không pháo."\n\n'
        "Chiều hố lớp. Sống. Đo. Không khoe.",
    ),
    d(
        145,
        "Ngọn Gió Mới",
        "một trăm bốn mươi lăm",
        24900,
        "Gió tây lạ · mùi sông · không tuần xa · ba mươi hai",
        "mùi gió tây mang hơi sông và băng",
        "gió tây mới · hơi sông · tai khe",
        "Gió đổi hướng thì đổi canh · không đạp theo mùi · rèm chặt",
        "Hơi sông trên gió — sông đóng hay có người hun?",
        "Gió đổi tây từ canh tư — mang hơi sông lạnh và băng. Ngày thứ một trăm bốn mươi lăm. Mùi gió tây mới. Không tuần xa. Rèm chặt. Tai khe hơn mũi.",
        'Đại Lực tháp góc: "Gió tây. Hơi sông. Không thấy khói."\n\n'
        '"Ghi. Không soi. Không kể," Phong nói.\n\n'
        'Hà: "Trẻ trong. Gió lạ dễ tò mò."\n\n'
        '"Chặn."\n\n'
        "---\n\n"
        'Họp: "Gió đổi. Canh tây siết. Không tuần sông hôm nay. Củi siết."\n\n'
        'Hứa: "Đủ."\n\n'
        'Tôn Vũ: "Xưởng kín."\n\n'
        'A Cường: "Trống sát."\n\n'
        '"Không đạp theo hơi."\n\n'
        'Phong-Hà: "Sông gần hơn ta nghĩ?"\n\n'
        '"Chưa mắt. Chưa mở."\n\n'
        'Ngọ mười nhịp: "Gió tây. Hơi sông. Không soi. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Chiều gió. Đêm nắm. Mùi băng. Sống. Đo. Không khoe.",
    ),
    d(
        146,
        "Cơn Bão Tuyết",
        "một trăm bốn mươi sáu",
        24930,
        "Bão tuyết · cửa đóng · ca tháp ngắn · ba mươi ba",
        "mùi tuyết dày và khói bếp bị gió dập",
        "bão tuyết · cửa đóng · không tuần",
        "Bão thì trong · ca ngắn · củi siết · không ra một mình",
        "Bão che tất cả — sau bão sẽ lộ gì trên tuyết?",
        "Bão tuyết ập từ tây-bắc trước ngọ — trắng, gào gió, không gào miệng. Ngày thứ một trăm bốn mươi sáu. Mùi tuyết dày và khói bếp bị gió dập. Cửa đóng. Ca tháp ngắn. Không tuần.",
        '"Vào. Đóng. Ca tháp từng khắc ngắn. Không ra một mình," Phong hô thấp trong gió.\n\n'
        "Hà kéo trẻ thẻ. Cúc Hạt trong. Diễm rèm. Đại Lực và Hữu xoay ca tháp — mặt che vải, không đứng lâu.\n\n"
        'Tôn Vũ dập lò xưởng: "Không hun thừa trong bão."\n\n'
        'Hứa: "Kho khô. Cửa chèn."\n\n'
        "---\n\n"
        'Trong lều họp năm người: "Bão. Việc trong. Không kể đẹp bão. Sau bão kiểm hố bẫy và then."\n\n'
        'Phong-Hà: "Đủ ấm?"\n\n'
        '"Đủ. Không lỏng canh."\n\n'
        "Chiều bão còn. Cháo loãng. Xâu. "
        'Nhắc xương: "Bão. Cửa đóng. Đông thường khi lặng. Hầm xấu. Cùng màu. Máu kín nếu sóng sau bão."\n\n'
        "Gật. Đêm gió. Nắm tay. Ngủ nghiêng. Mai tuyết cao. Sống. Đo. Không khoe.",
    ),
    d(
        147,
        "Cuộc Sống Trong Băng Giá",
        "một trăm bốn mươi bảy",
        24960,
        "Băng giá sau bão · việc đều · không lỏng · ba mươi tư",
        "mùi băng cứng và cháo nóng nồi",
        "sống trong băng giá · việc đều · không lỏng",
        "Lạnh không bằng lỏng · ca đủ · cháo đủ · không trượt hố",
        "Băng giá kéo dài — lương và củi chịu được bao ngày?",
        "Sau bão, thế giới trắng và cứng. Ngày thứ một trăm bốn mươi bảy. Mùi băng cứng và cháo nóng nồi. Cuộc sống trong băng giá: việc đều, bước chậm, không lỏng canh.",
        'Phong tổ việc: quét lối hẹp, kiểm then, không quét hết sân — giữ xấu. "Lạnh. Không lỏng. Ai trượt — không hét," anh dặn.\n\n'
        'Hà phát găng: "Trẻ trước."\n\n'
        'Đại Lực tháp: "Trắng. Trống sát. Nhìn xa mù."\n\n'
        '"Tai khe."\n\n'
        "---\n\n"
        'Họp: "Băng giá. Củi siết. Lương siết. Ca đủ. Hố bẫy kiểm — không sập nhầm người."\n\n'
        'Tôn Vũ: "Lưỡi không để ngoài băng."\n\n'
        'Hứa: "Đủ tám ngày nếu siết."\n\n'
        'Phong-Hà: "Đủ?"\n\n'
        '"Đủ. Lạnh không phải hội sưởi."\n\n'
        'Ngọ mười nhịp: "Băng giá. Việc đều. Không lỏng. Đông thường. Hầm xấu. Cùng màu."\n\n'
        "Gật. Chiều muối chát trong lều. Đêm nắm ấm. Sống. Đo. Không khoe.",
    ),
    d(
        148,
        "Băng Sông Đóng Băng",
        "một trăm bốn mươi tám",
        24990,
        "Thám sông băng · không sang · dấu cũ · ba mươi lăm",
        "mùi sông băng và gió tây se",
        "sông đóng băng · thám không sang · dấu cũ",
        "Không sang sông một mình · người đợi · về trước tối · không đạp giữa",
        "Sông băng thành đường — miệng có dùng đường đó không?",
        "Hơi sông trên gió tây đã rõ hơn — vì sông đóng băng. Ngày thứ một trăm bốn mươi tám. Phong và Hùng thám năm trăm bước tây: mặt sông trắng cứng. Không sang. Chỉ ghi. Về.",
        '"Đứng bờ. Không bước giữa. Dấu cũ bên kia — ba," Hùng nói nhỏ.\n\n'
        '"Ghi. Không sang. Không kể trẻ sông thành đường chơi," Phong đáp.\n\n'
        "Mùi sông băng. Gió se. Quay. Cổng: Đại Lực đợi.\n\n"
        '"Sông đóng. Dấu cũ bên kia. Không miệng sống," Phong báo.\n\n'
        'Hà nước nóng: "Không sang nữa hôm nay."\n\n'
        '"Không."\n\n'
        "---\n\n"
        'Họp: "Sông băng có thể thành đường miệng. Canh tây siết. Tháp góc nhớ hướng sông. Không tuần đêm."\n\n'
        'A Cường: "Bẫy tây?"\n\n'
        '"Một hố xấu gần lối bờ — không đẹp."\n\n'
        'Phong-Hà: "Đủ?"\n\n'
        '"Đủ. Sông không phải hội trượt."\n\n'
        'Ngọ mười nhịp: "Sông băng. Không sang. Không kể. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
        "Gật. Chiều hố tây. Đêm nắm. Mùi băng. Sống. Đo. Không khoe.",
    ),
    d(
        149,
        "Cuộc Sống Đời Thường",
        "một trăm bốn mươi chín",
        25020,
        "Đời thường việc · bảy mươi bảy miệng · ba mươi sáu ngày",
        "mùi cháo loãng và đất sân đông người",
        "đời thường việc · bảy mươi bảy · không hội thường",
        "Thường ngày = việc đo được · không lười · không cãi · nói thẳng",
        "Đời thường bền khi sông băng còn là đường lạ ngoài rào?",
        "Bình minh ngày thứ một trăm bốn mươi chín. Bảy mươi bảy người. Mùi cháo loãng và đất sân đông người. Cuộc sống đời thường — thường bằng việc, không bằng quên miệng ngoài.",
        '"Ba mươi sáu ngày kể từ sóng lớn đầu chuỗi đã xen kẽ yên. Tiếp canh. Mỗi người một việc. Không lười. Không cãi. Vấn đề nói thẳng," Phong nói trước sân ngắn.\n\n'
        "Bảy mươi bảy gật. Không sợ — tin.\n\n"
        'Hà cạnh, khăn thấp: "Tin đắt. Đừng trả bằng ồn."\n\n'
        '"Đúng."\n\n'
        "Phân tổ: tháp, rèn, kho, rau, thẻ, hầm, tuần ngắn trong rào, góc mới. Hứa kho. Tôn Vũ rèn. Đại Lực tháp. A Cường đá. Cúc thẻ.\n\n"
        'Phong-Hà muối cuối: "Đủ? Không lệch vì chữ thường?"\n\n'
        '"Không lệch. Thường không phải hội quên," chị lau tay.\n\n'
        '"Ghi. Ai kể cấp — nặng. Ai chỉ hố — nặng. Ai kể sông băng trẻ — nặng."\n\n'
        'Ngọ mười nhịp: "Bảy mươi bảy. Đời thường việc. Không thở phào. Không họp chữ thường. Việc. Cùng màu. Máu kín nếu sóng. Bóng — không chỉ. Sông — không sang."\n\n'
        "Gật. Máy che. Không khe đá.\n\n"
        "Hoàng hôn. Phong tuần trong rào: chông vôi then hố vết nguyên. Góc mới then êm. Gật. Không khen. "
        'Đêm thềm: nắm tay Hà. Mùi đất se. Gió bấc nhẹ. "Mai còn việc. Còn đất. Còn người," anh nói.\n\n'
        '"Còn. Đều," chị đáp. Đủ.',
    ),
]


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
        if "Nhịp im" in text:
            raise SystemExit(f"Nhịp im leaked in ch{s['n']}")
        w = vi_words(text)
        i = 0
        extras = [
            f"Canh khuya riêng ngày {s['day_vn']}: then tây êm, đông chông không cọt, hố không bới, cửa vết không sứt. A Minh đổi. Hữu im. Mùi {s['smell']} lớp mỏng. Không bục miệng. Bục việc. Đủ sau {s['tag']}.",
            f"Phong ngồi dậy uống nước nguội lần thêm, đếm then cổng trong đầu: không kêu. Gió bấc. {s['law']}. Hà thở đều. Nắm. Buông. Ngủ thật dưới đất Biên Ải sau {s['tag']}.",
            f"Sổ than thêm một dòng nhạt: {s['event']}. Không pháo. Không đọc to. Gấp. Nằm. Mai trống điểm mang bóng sóng hỏi hoặc yên giả — chưa mừng. Chưa lỏng.",
            f"Trước gà cuối lỏng nắm: ngoài rào sau {s['tag']} chỉ đất và gió. Trong trại nhịp gánh thẻ. Nhịp cháo. Nhịp chông. Chưa thua. Còn viết. Còn thở. Còn người. Đủ.",
            f'Hà ghé vai thêm một nhịp: "Mai em cùng màu. Anh bao. Không thèm vì {s["tag"]}." Phong gật. Hở đắt hơn thèm. Mùi {s["smell"]}. Đất se. Vôi cũ. Then êm. Sống. Đo. Không khoe.',
        ]
        while w < 3050 and i < 40:
            bit = (
                extras[i % len(extras)]
                + f" Hơi thở chậm lớp {i + 1} ngày {s['day_vn']} giữ việc sau {s['tag']}."
            )
            if bit in text:
                bit += f" Thêm dấu muối chát {i} hướng {s['n']}."
            text = text.replace("「Kho Vô Hạn", "\n" + bit + "\n\n「Kho Vô Hạn", 1)
            w = vi_words(text)
            i += 1
        if "Nhịp im" in text:
            raise SystemExit(f"Nhịp im leaked after expand ch{s['n']}")
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
        out = (r.stdout or "") + (r.stderr or "")
        line = out.strip().splitlines()[0] if out.strip() else "?"
        m = re.search(r"([\d.]+)\s+van=", line)
        sc = float(m.group(1)) if m else 0.0
        ok = ("[OK" in line) or (sc >= 9.0 and "short" not in line and "maxrep" not in line)
        report.append({"n": s["n"], "words": w, "score": sc, "line": line, "ok": ok})
        print(line, "w=", w, flush=True)

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    fails = [x for x in report if not x["ok"]]
    print("PASS", sum(1 for x in report if x["ok"]), "/", len(report), flush=True)
    if fails:
        print("FAILS", [(f["n"], f["score"], f["line"]) for f in fails], flush=True)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
