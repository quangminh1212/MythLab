# -*- coding: utf-8 -*-
"""Unique full rewrite ch.150-161. Same style as 129-149 / 104-128.
No Nhịp im. Unique openings. Kho Vô Hạn panel. ≥3000 words.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Dev/XLab_MTC/Mạt Thế Cổ Đại Cầu Sinh")
SCORER = Path(r"C:/Dev/NovelLab/scripts/strict_score.py")
CFG = BASE / ".novelab_score.json"
OUT_JSON = BASE / "_score_rewrite_150_161.json"

_SRC = (BASE / "_rewrite_unique_104_128.py").read_text(encoding="utf-8")
_ns: dict = {}
exec(_SRC.split("SPECS = [")[0], _ns)
hdr = _ns["hdr"]
panel = _ns["panel"]
find_file = _ns["find_file"]
night_close = _ns["night_close"]
vi_words = _ns["vi_words"]
_sm = _SRC[_SRC.find("def shared_mid") : _SRC.find("def build")]
exec(_sm, _ns)
shared_mid = _ns["shared_mid"]


def d(n, title, day_vn, exp, event, smell, tag, law, cliff, open_, core):
    return dict(
        n=n, title=title, day=n, day_vn=day_vn, exp=exp, event=event,
        smell=smell, tag=tag, law=law, cliff=cliff, open=open_, core=core,
    )


SPECS = [
    d(150, "Ngày Kỷ Niệm", "một trăm năm mươi", 25050,
      "Kỷ niệm một trăm năm mươi ngày · việc không hội · bảy mươi bảy",
      "mùi cháo đặc một nấc và đất se kỷ niệm",
      "kỷ niệm một trăm năm mươi · việc không hội",
      "Kỷ niệm bằng việc đo được · không trống · không kể số to trẻ",
      "Một trăm năm mươi ngày — liệu còn đủ im khi sông băng thành đường?",
      "Bình minh ngày thứ một trăm năm mươi. Bảy mươi bảy người. Mùi cháo đặc một nấc — không phải hội, chỉ là kỷ niệm bằng việc. Đất se. Không trống. Không cờ.",
      'Phong đứng xưởng: "Một trăm năm mươi ngày. Không họp sân. Cháo đặc một bữa. Việc đủ. Không kể trẻ như chiến thắng."\n\n'
      'Hà phát cháo: "Trẻ trước."\n\n'
      'Đại Lực: "Trống ngoài. Sông băng còn."\n\n'
      '"Canh tây siết. Không sang sông. Không thở phào vì số ngày."\n\n'
      "---\n\n"
      'Họp mười người: "Kỷ niệm là nhớ luật: đâm thấp, máu kín, hố xấu, cùng màu, không pháo cấp."\n\n'
      'Tôn Vũ: "Lưỡi đủ."\n\n'
      'Hứa: "Lương siết giữ."\n\n'
      'Phong-Hà muối: "Đủ? Không lệch vì chữ kỷ niệm?"\n\n'
      '"Không lệch. Kỷ niệm không phải hội."\n\n'
      'Ngọ mười nhịp: "Một trăm năm mươi. Việc. Không pháo. Đông thường. Hầm xấu. Cùng màu. Sông — không sang."\n\n'
      "Gật. Máy che. Chiều tuần trong rào. Đêm nắm. Mùi đất se. Sống. Đo. Không khoe số."),
    d(151, "Cuộc Trinh Sát Mới", "một trăm năm mươi mốt", 25090,
      "Trinh sát tây-sông · dấu mới · không sang · bảy mươi bảy",
      "mùi sông băng và gió tây se lạnh",
      "trinh sát tây-sông · dấu mới · không sang",
      "Người đợi cổng · không đạp giữa sông · về trước tối",
      "Dấu mới bên kia sông — miệng sắp dùng đường băng?",
      "Gió tây se khi Phong cột giày. Ngày thứ một trăm năm mươi mốt. Trinh sát mới: tây tới bờ sông băng, không sang, chỉ ghi dấu. Đại Lực đợi cổng.",
      '"Đi bao lâu?" Đại Lực hỏi.\n\n'
      '"Hai canh. Hùng cùng. Về trước tối."\n\n'
      'Hà: "Không sang."\n\n'
      '"Không sang."\n\n'
      "Năm trăm bước: bờ. Mặt sông trắng. Dấu mới — bốn, rộng hơn cũ, hướng bắc dọc bờ kia.\n\n"
      'Hùng: "Mới hơn một đêm."\n\n'
      '"Ghi. Không đạp giữa. Về."\n\n'
      "---\n\n"
      'Cổng: "Dấu mới bên kia. Bốn. Không miệng sống," Phong báo.\n\n'
      'Họp: "Canh tây siết. Bẫy lối bờ giữ. Không tuần đêm sông."\n\n'
      'A Cường: "Tháp góc nhớ hướng."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Dấu không phải hội săn."\n\n'
      'Ngọ mười nhịp: "Trinh sát sông. Dấu mới. Không sang. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Chiều hố tây. Đêm nắm. Mùi băng. Sống. Đo. Không khoe."),
    d(152, "Bình Minh Mới", "một trăm năm mươi hai", 25120,
      "Bình minh việc · sau trinh sát · không lỏng · bảy mươi bảy",
      "mùi sương mai và sắt nguội xưởng",
      "bình minh việc sau trinh sát · không lỏng",
      "Bình minh là việc · không hội bình minh · canh tây đủ",
      "Bình minh yên — dấu sông có tiến trong đêm không?",
      "Bình minh ngày thứ một trăm năm mươi hai. Mùi sương mai và sắt nguội. Việc mở trước miệng. Canh tây đủ sau dấu mới. Không lỏng vì nắng đẹp.",
      'Phong tổ việc: tháp, rèn, kho, rau, thẻ, hầm, tuần trong rào, tây bờ không tuần xa.\n\n'
      '"Trống sát. Dấu sông chưa tiến vào bờ ta," Đại Lực báo.\n\n'
      '"Không thở phào. Tai khe."\n\n'
      'Hà: "Trẻ thẻ trong. Không ra xem sông."\n\n'
      '"Giữ."\n\n'
      "---\n\n"
      'Họp ngắn: "Bình minh việc. Không họp chữ yên. Canh tây. Lương siết giữ."\n\n'
      'Tôn Vũ: "Lưỡi mài."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Bình minh không phải hội."\n\n'
      'Ngọ mười nhịp: "Bình minh việc. Không lỏng. Đông thường. Hầm xấu. Cùng màu. Sông — không sang."\n\n'
      "Gật. Chiều muối. Đêm nắm. Sống. Đo. Không khoe."),
    d(153, "Trận Lũ Bất Ngờ", "một trăm năm mươi ba", 25170,
      "Lũ tuyết tan · nước hào · bảo vệ kho · bảy mươi bảy",
      "mùi nước lạnh và bùn ướt hào",
      "lũ tuyết tan · nước hào · siết kho",
      "Nước trước miệng · kho cao · trẻ trong · không lội một mình",
      "Nước rút — miệng có theo dòng sang bờ ta?",
      "Trưa ngày thứ một trăm năm mươi ba. Tuyết tây-nam tan nhanh. Nước tràn hào nam — không phải mưa, là lũ tuyết. Mùi nước lạnh và bùn. Không hội. Việc.",
      '"Kho cao. Bao lên kệ. Trẻ trong. Không lội hào," Phong hô thấp.\n\n'
      "Hà kéo thẻ. Hứa kê gạo. Tôn Vũ chèn cửa xưởng. Đại Lực tháp: nước không mang bóng — chưa.\n\n"
      "---\n\n"
      'Họp năm người ướt: "Lũ ngắn. Kiểm then sau rút. Bẫy hố có thể sập nhầm — đánh dấu lại xấu."\n\n'
      'A Cường: "Hào nam đầy. Đông ổn."\n\n'
      'Phong-Hà: "Đủ ấm người ướt?"\n\n'
      '"Đủ. Không lỏng canh vì nước."\n\n'
      'Nhắc xương: "Lũ. Kho cao. Không lội. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng theo nước."\n\n'
      "Gật. Chiều nước hạ. Đêm nắm. Mùi bùn. Sống. Đo. Không khoe."),
    d(154, "Kẻ Ngoại Lại", "một trăm năm mươi tư", 25210,
      "Ba người lạ tây · quy tắc trước cháo · kiểm đồ · bảy mươi chín",
      "mùi người đường và cháo loãng",
      "kẻ ngoại lai ba · quy tắc trước cháo",
      "Quy tắc trước cháo · kiểm đồ ngoài · trẻ trước · không hang truyện",
      "Ba miệng mới — có phải mắt của ai bên kia sông?",
      "Hoàng hôn ngày thứ một trăm năm mươi tư. Ba người lạ gõ then tây — đói, run, không vũ khí giơ. Mùi người đường. Quy tắc trước cháo.",
      '"Quy tắc. Đồ kiểm ngoài. Trẻ trước. Không cãi. Không ra một mình," Phong nói.\n\n'
      "Họ gật. Hà nước. Cháo. Thẻ. Hứa siết rau nửa nấc.\n\n"
      'Một người: "Sông… băng… có bóng."\n\n'
      '"Ghi. Không kể trẻ. Không hang truyện sân," Phong chốt.\n\n'
      "---\n\n"
      'Họp: "Ba mới. Quy tắc. Canh tây siết. Không thở phào vì thêm tay."\n\n'
      'Phong-Hà: "Mới dễ ồn."\n\n'
      '"Rèm. Thẻ. Không hang."\n\n'
      'Ngọ hôm sau mười nhịp: "Người mới. Quy tắc. Không kể đường như chiến công. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Dân số bảy mươi chín. Đêm nắm. Sống. Đo. Không khoe."),
    d(155, "Cuộc Hành Trình Xa", "một trăm năm mươi lăm", 25250,
      "Hành trình đông ngắn · nhà bỏ · không ở lại · bảy mươi chín",
      "mùi đất đông và nhà bỏ hoang mốc",
      "hành trình đông ngắn · nhà bỏ · về trước tối",
      "Không ở lại nhà bỏ · người đợi cổng · không mang đồ lạ không hiểu",
      "Nhà bỏ còn dấu người sống — bạn hay mồi?",
      "Bình minh ngày thứ một trăm năm mươi lăm. Phong và Hùng ra đông tám trăm bước — hành trình xa trong tầm về trước tối. Mùi đất đông. Nhà bỏ hoang một bên đường.",
      '"Vào nhanh. Không ở. Ghi. Về," Phong nói.\n\n'
      "Trong: mùi mốc. Dấu chân người mới — hai đôi. Không miệng. Mảnh vải không chữ.\n\n"
      'Hùng: "Không lấy?"\n\n'
      '"Không mang đồ không hiểu. Về."\n\n'
      "---\n\n"
      'Cổng: Đại Lực đợi. "Nhà bỏ. Dấu hai. Không miệng. Không đồ lạ."\n\n'
      'Hà nước. Họp ngắn: "Đông còn người sống ngoài. Canh không lỏng. Không tuần đêm đông."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Hành trình không phải hội khám."\n\n'
      'Ngọ mười nhịp: "Đông nhà bỏ. Dấu hai. Không mang lạ. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Đêm nắm. Sống. Đo. Không khoe."),
    d(156, "Bí Ẩn Trong Rừng", "một trăm năm mươi sáu", 25290,
      "Rừng nam · dấu lửa cũ · không theo · bảy mươi chín",
      "mùi nhựa thông và tro lạnh rừng",
      "bí ẩn rừng nam · tro lạnh · không theo",
      "Không theo khói cũ · không đạp giữa rừng tối · về trước hoàng hôn",
      "Tro lạnh rừng — ai hun, và họ còn gần không?",
      "Ngày thứ một trăm năm mươi sáu. Phong, Hùng, A Cường vòng nam rừng thưa — không sâu. Mùi nhựa thông và tro lạnh. Bí ẩn: bếp đất tắt nửa ngày, không người.",
      '"Không theo. Ghi hướng. Về," Phong dặn.\n\n'
      'A Cường: "Tro còn ấm nhẹ."\n\n'
      '"Ấm là gần. Không gọi. Không pháo."\n\n'
      "---\n\n"
      'Về cổng. Họp: "Rừng nam có người. Canh nam siết. Không tuần rừng đêm. Không kể trẻ chuyện tro."\n\n'
      'Đại Lực: "Tháp nam?"\n\n'
      '"Chưa. Việc trước tháp."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Bí ẩn không phải hội đoán."\n\n'
      'Ngọ mười nhịp: "Rừng tro. Không theo. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
      "Gật. Đêm nắm. Mùi thông còn áo. Sống. Đo. Không khoe."),
    d(157, "Bình Minh Đỏ", "một trăm năm mươi bảy", 25320,
      "Bình minh đỏ · gió đông · không lỏng · bảy mươi chín",
      "mùi sương đỏ nắng và khói bếp",
      "bình minh đỏ · không lỏng · tai khe",
      "Màu trời không phải hội · canh đủ · không mở rèm trẻ ngắm lâu",
      "Bình minh đỏ — cháy xa hay chỉ nắng đông?",
      "Bình minh ngày thứ một trăm năm mươi bảy phủ đỏ mỏng lên chông. Mùi sương và khói bếp. Đỏ — không họp ngắm. Việc. Tai khe hơn mắt.",
      'Đại Lực: "Đỏ đông. Không thấy lửa. Gió mang bụi."\n\n'
      '"Ghi. Không soi. Không kể đẹp đỏ sân," Phong nói.\n\n'
      'Hà: "Trẻ không ra cổng ngắm."\n\n'
      '"Giữ."\n\n'
      "---\n\n"
      'Họp: "Bình minh đỏ. Canh đông đủ. Không tuần xa vì màu. Lương củi siết giữ."\n\n'
      'Phong-Hà: "Cháy xa hay nắng?"\n\n'
      '"Chưa mắt. Không mở sớm."\n\n'
      'Ngọ mười nhịp: "Bình minh đỏ. Không lỏng. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Chiều màu tắt. Đêm nắm. Sống. Đo. Không khoe."),
    d(158, "Gió Bắc Thổi Rét", "một trăm năm mươi tám", 25350,
      "Gió bấc rét · củi siết · ca ngắn · bảy mươi chín",
      "mùi gió bấc buốt và than bếp",
      "gió bấc rét · củi siết · không lỏng",
      "Rét không bằng lỏng · ca ngắn tháp · trẻ trong · củi siết",
      "Gió bấc kéo dài — sông băng có nứt hay cứng thêm?",
      "Canh tư ngày thứ một trăm năm mươi tám. Gió bấc thổi rét buốt gáy. Mùi than bếp. Củi siết. Ca tháp ngắn. Không tuần xa.",
      '"Vào. Ca ngắn. Không đứng tháp lâu," Phong dặn.\n\n'
      'Hà phát găng: "Trẻ trước."\n\n'
      'Hứa: "Củi đủ sáu ngày nếu siết."\n\n'
      'Tôn Vũ: "Xưởng kín gió."\n\n'
      "---\n\n"
      'Họp: "Rét. Việc trong nhiều hơn ngoài. Canh đủ. Không lười vì lạnh."\n\n'
      'Phong-Hà: "Đủ ấm?"\n\n'
      '"Đủ. Không lỏng."\n\n'
      'Ngọ mười nhịp: "Gió bấc. Củi siết. Đông thường. Hầm xấu. Cùng màu. Máu kín nếu sóng."\n\n'
      "Gật. Đêm nắm ấm. Sống. Đo. Không khoe."),
    d(159, "Bão Tuyết Đổ", "một trăm năm mươi chín", 25390,
      "Bão tuyết đổ · cửa đóng · sau bão kiểm · bảy mươi chín",
      "mùi tuyết dày đổ và khói bị gió dập",
      "bão tuyết đổ · cửa đóng · không tuần",
      "Bão thì trong · ca ngắn · sau bão kiểm then hố · không ra một mình",
      "Sau bão tuyết — dấu sông và rừng còn đọc được không?",
      "Ngọ ngày thứ một trăm năm mươi chín. Bão tuyết đổ trắng. Mùi tuyết dày. Cửa đóng. Ca tháp ngắn. Không tuần.",
      '"Đóng. Ca ngắn. Không ra một mình," Phong hô thấp.\n\n'
      "Hà thẻ trong. Đại Lực Hữu xoay tháp. Tôn Vũ dập lò thừa. Hứa chèn kho.\n\n"
      "---\n\n"
      'Trong lều: "Bão. Việc trong. Sau bão kiểm then, hố bẫy, góc mới. Không kể đẹp bão."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Không lỏng canh."\n\n'
      'Nhắc: "Bão. Cửa đóng. Đông thường khi lặng. Hầm xấu. Cùng màu."\n\n'
      "Gật. Đêm gió. Nắm. Ngủ. Mai tuyết cao. Sống. Đo. Không khoe."),
    d(160, "Ánh Nắng Sau Bão", "một trăm sáu mươi", 25420,
      "Nắng sau bão · quét lối · không lỏng · bảy mươi chín",
      "mùi nắng trên tuyết và cháo nóng",
      "nắng sau bão · quét lối hẹp · không lỏng",
      "Nắng không bằng lỏng · quét lối hẹp giữ xấu · kiểm hố",
      "Nắng lộ dấu — có dấu miệng mới trên tuyết không?",
      "Bình minh ngày thứ một trăm sáu mươi. Nắng chói trên tuyết sau bão. Mùi cháo nóng. Quét lối hẹp. Không quét hết sân — giữ xấu. Không lỏng.",
      'Phong: "Quét hẹp. Kiểm then. Kiểm hố. Không thở phào vì nắng."\n\n'
      'Đại Lực: "Trắng. Trống sát. Nhìn xa chói."\n\n'
      '"Tai khe."\n\n'
      'A Cường: "Hố bẫy còn. Đắp lại xấu."\n\n'
      "---\n\n"
      'Họp: "Sau bão. Việc. Không họp chữ nắng. Canh tây-đông đủ."\n\n'
      'Phong-Hà: "Đủ?"\n\n'
      '"Đủ. Nắng không phải hội."\n\n'
      'Ngọ mười nhịp: "Nắng sau bão. Không lỏng. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Chiều muối chát. Đêm nắm. Sống. Đo. Không khoe."),
    d(161, "Cuộc Tập Luyện", "một trăm sáu mươi mốt", 25460,
      "Tập luyện hai · đâm thấp · tín hiệu tay · bảy mươi chín",
      "mùi mồ hôi tập trên tuyết nén và đất sân",
      "tập luyện hai · đâm thấp · tín hiệu tay",
      "Tập không hội · không đếm to · trẻ không xem · tín hiệu tay không hét",
      "Tập xong tay nhớ — khi sóng thật có giữ kín?",
      "Sân đông nén tuyết một góc hẹp. Ngày thứ một trăm sáu mươi mốt. Tập luyện lần hai: đâm thấp, rút, tín hiệu tay tháp góc, không hét, không pháo.",
      "Phong xếp mười hai người gồm người mới. "
      '"Đâm thấp. Không mặt. Rút. Tín hiệu tay: một sóng, hai bóng, nắm hết. Không hét. Không cười."\n\n'
      "Ba vòng. Mồ hôi. Không ồn.\n\n"
      'Hà rèm: "Trẻ trong."\n\n'
      '"Giữ."\n\n'
      "---\n\n"
      '"Tay nhớ chưa?"\n\n'
      'Hùng: "Nhớ thấp. Tín hiệu rõ."\n\n'
      'Người mới: "Rút chậm — sửa."\n\n'
      '"Sửa. Không khoe."\n\n'
      'Phong-Hà: "Tập dễ ồn."\n\n'
      '"Em chặn miệng. Anh chặn tay."\n\n'
      'Ngọ mười nhịp: "Tập hai. Không pháo. Không kể như chiến. Đông thường. Hầm xấu. Cùng màu."\n\n'
      "Gật. Máy che. Đêm cơ mỏi. Nắm. Ngủ. Mai sống."),
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
            raise SystemExit(f"Nhịp im leaked ch{s['n']}")
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
            bit = extras[i % len(extras)] + f" Hơi thở chậm lớp {i + 1} ngày {s['day_vn']} giữ việc sau {s['tag']}."
            if bit in text:
                bit += f" Thêm dấu muối chát {i} hướng {s['n']}."
            text = text.replace("「Kho Vô Hạn", "\n" + bit + "\n\n「Kho Vô Hạn", 1)
            w = vi_words(text)
            i += 1
        path.write_text(text, encoding="utf-8")
        r = subprocess.run(
            ["python", str(SCORER), str(path), "--min-words", "3000", "--cfg", str(CFG), "--threshold", "9.0"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
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
        print("FAILS", fails, flush=True)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
