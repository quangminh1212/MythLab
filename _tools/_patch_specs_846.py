from pathlib import Path
import re
import ast

dst = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh/_rewrite_clone_846_853.py")
text = dst.read_text(encoding="utf-8")

new_specs = r'''SPECS = [
    dict(
        n=846,
        day=966,
        day_vi="chín trăm sáu mươi sáu",
        title="Bóng Gò Lần 79 Không Chỉ",
        kind="bong",
        open_hook="Gió bấc mang mùi túi vải ẩm và gai khô khi trống điểm tan",
        place="gò đông",
        event_short="bóng gò lần bảy mươi chín",
        detail=(
            "một bóng đặt túi vải trên gai; không lê; không nhìn trẻ; "
            "khép bằng chân bóng không mở túi gai không ném đá không hô đáp"
        ),
        law="thấy, không chỉ, không mở túi gai, không đạp theo, không nhổ mốc",
        report=(
            "Gò đông. Một bóng. Đặt túi vải trên gai. "
            "Không lê. Không nhìn trẻ. Không mang xẻng."
        ),
        order=(
            "Không mở. Không chỉ. Không mở túi gai. Không đạp theo. "
            "Không nhổ mốc. Việc"
        ),
        scent="túi vải ẩm gai khô",
        micro="túi vải trên gai; không mở; chân bóng khép",
        bones="Một bóng gò đông · túi vải trên gai · không chỉ · không mở túi · không đạp",
        panel_ev=(
            "Bóng gò lần 79 · gò đông · túi vải trên gai · không chỉ · "
            "cấp im · máy nghèo"
        ),
        tag="bóng túi gai",
    ),
    dict(
        n=847,
        day=967,
        day_vi="chín trăm sáu mươi bảy",
        title="Hỏi Lần 157 Cùng Màu",
        kind="hoi",
        open_hook="Sương mỏng dính bọc lá khô khi trống điểm tan sớm",
        place="cổng đông",
        event_short="hỏi lần một trăm năm mươi bảy",
        detail=(
            "một miệng hỏi có thuốc bắc không, đổi bọc lá lấy nước; giọng khác lần trước; "
            "Hạt suýt há — Cúc bịt trước khi chữ thuốc lọt mắt trẻ"
        ),
        law="đông thường, hầm xấu, không nhận thuốc, không đổi bọc, cùng màu nếu phải đáp",
        report=(
            "Cổng đông. Một miệng. Hỏi thuốc bắc đổi bọc lá lấy nước. "
            "Giọng khác. Không lê."
        ),
        order=(
            "Không mở. Không kể trẻ. Không chỉ giếng. Không nhận thuốc. "
            "Không đổi bọc. Đông thường. Hầm xấu. Việc"
        ),
        scent="bọc lá thuốc khê",
        micro="Hạt suýt há — Cúc bịt; không nhận thuốc",
        bones="Thuốc bắc · đổi bọc lá lấy nước · không nhận · không đổi · cùng màu · Cúc chặn",
        panel_ev=(
            "Hỏi lần 157 · thuốc bắc đổi bọc lá · cùng màu · không nhận · "
            "không mở · cấp im · máy nghèo"
        ),
        tag="hỏi thuốc",
        ask1="Trong ơi — có thuốc bắc không, đổi bọc lá lấy nước!",
        ask2="Bọc lá ngoài là của tao — trong có thầy thuốc không?",
        reply="Đông thường. Hầm xấu.",
    ),
    dict(
        n=848,
        day=968,
        day_vi="chín trăm sáu mươi tám",
        title="Ngày Yên Sau Hỏi 157",
        kind="yen",
        open_hook="Nắng mỏng chạm bao muối muộn hơn hôm miệng thuốc",
        place="trong rào",
        event_short="ngày yên sau hỏi một trăm năm mươi bảy",
        detail=(
            "trống không bằng yên hội; sau chữ thuốc, yên có thể là khoảng lùi mang thầy thuốc giả; "
            "giữa trưa thoáng mùi bọc lá khô ngoài rào nhưng không miệng"
        ),
        law="không thở phào, không mở rèm sớm, không rải vôi nghỉ, tai khe sau chữ thuốc",
        report="Cổng trống. Ngoài trống. Không miệng. Không dấu thuốc. Không bọc lá rơi.",
        order="Không thở phào. Không họp chữ thuốc. Không rải vôi nghỉ. Việc",
        scent="bọc lá khô ngoài rào",
        micro="mùi bọc lá giữa trưa — không mở; không mừng yên",
        bones="Yên sau hỏi thuốc · trống ≠ yên hội · không thở phào · mùi bọc lá không miệng",
        panel_ev=(
            "Yên sau hỏi 157 · trống ≠ yên hội · không thở phào · thuốc · "
            "cấp im · máy nghèo"
        ),
        tag="yên sau thuốc",
    ),
    dict(
        n=849,
        day=969,
        day_vi="chín trăm sáu mươi chín",
        title="Sóng Thấp Lần 153",
        kind="song",
        open_hook="Tro lạnh kêu khẽ khi gió bấc kéo qua gò sườn tây thấp",
        place="gò sườn tây thấp",
        event_short="sóng thấp lần một trăm năm mươi ba",
        detail=(
            "sáu bóng thấp từ gò sườn tây thấp; không gào; chỉ sóng; máu phải kín; "
            "hố mới sát gò sườn — không trùng bờ suối cạn đông-nam; máu lẫn đất se "
            "— rửa bằng vải không bằng nước sạch"
        ),
        law="đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không nước sạch",
        report=(
            "Gò sườn tây thấp. Sáu thấp. Không gào. Dấu riêng chỗ này. Không mang xẻng."
        ),
        order="Máu kín. Không đếm sáu to. Không phơi. Đổi chỗ lê. Hố xấu. Việc",
        scent="tanh đất se gò sườn",
        micro="sáu thấp; máu vải; hố không trùng suối đông-nam",
        bones="Sáu thấp gò sườn tây · máu kín · hố xấu · máu vải không nước sạch",
        panel_ev=(
            "Sóng thấp lần 153 · gò sườn tây thấp · sáu · máu kín · "
            "cấp im · máy nghèo"
        ),
        tag="sóng gò sườn sáu",
    ),
    dict(
        n=850,
        day=970,
        day_vi="chín trăm bảy mươi",
        title="Bóng Thước Lần 80 Không Chỉ",
        kind="bong",
        open_hook="Đường bụi nam sáng như muối rơi khi gió bấc kéo ngang thước sơn",
        place="đường bụi nam",
        event_short="bóng thước lần tám mươi",
        detail=(
            "một bóng kẻ than lên thước sơn; không gào; không chỉ; "
            "A Minh suýt nhặt thước — Phong chặn bằng mắt"
        ),
        law="thấy, không chỉ, không nhặt thước sơn, không đạp theo, không nhổ mốc",
        report=(
            "Đường bụi nam. Một bóng. Kẻ than lên thước sơn. "
            "Không lê. Không nhìn trẻ."
        ),
        order=(
            "Không mở. Không chỉ. Không nhặt thước sơn. Không đạp theo. "
            "Không nhổ mốc. Việc"
        ),
        scent="than thước sơn bụi nam",
        micro="thước sơn kẻ than; không nhặt; A Minh đã chặn",
        bones="Một bóng thước nam · thước sơn kẻ than · không chỉ · không nhặt · không đạp",
        panel_ev=(
            "Bóng thước lần 80 · đường bụi nam · thước sơn · không chỉ · "
            "cấp im · máy nghèo"
        ),
        tag="bóng thước than",
    ),
    dict(
        n=851,
        day=971,
        day_vi="chín trăm bảy mươi mốt",
        title="Hỏi Lần 158 Cùng Màu",
        kind="hoi",
        open_hook="Sương tây tan chậm hơn sương đông khi trống điểm dứt sau chữ ngựa",
        place="cổng đông",
        event_short="hỏi lần một trăm năm mươi tám",
        detail=(
            "một miệng hỏi có ngựa thồ không, đổi yên lấy gạo; giọng khàn nam; "
            "Hữu suýt bước ra — Phong ra hiệu đứng im trước khi chữ ngựa lọt sân"
        ),
        law="đông thường, hầm xấu, không nhận yên, không đổi gạo, cùng màu nếu phải đáp",
        report=(
            "Cổng đông. Một miệng. Hỏi ngựa thồ đổi yên lấy gạo. "
            "Giọng khàn. Không lê."
        ),
        order=(
            "Không mở. Không kể trẻ. Không chỉ kho. Không nhận yên. "
            "Không đổi gạo. Đông thường. Hầm xấu. Việc"
        ),
        scent="da yên ngựa khô",
        micro="Hữu suýt bước — chặn; không nhận yên; không đổi gạo",
        bones="Ngựa thồ · đổi yên lấy gạo · không nhận · không đổi · cùng màu · Hữu đã chặn",
        panel_ev=(
            "Hỏi lần 158 · ngựa thồ đổi yên · cùng màu · không nhận · "
            "không mở · cấp im · máy nghèo"
        ),
        tag="hỏi ngựa",
        ask1="Trong ơi — có ngựa thồ không, đổi yên lấy gạo!",
        ask2="Yên ngoài là của tao — trong có chuồng ngựa không?",
        reply="Đông thường. Hầm xấu.",
    ),
    dict(
        n=852,
        day=972,
        day_vi="chín trăm bảy mươi hai",
        title="Ngày Yên Sau Hỏi 158",
        kind="yen",
        open_hook="Khói bếp còn thấp khi trống điểm tan muộn sau chữ ngựa",
        place="trong rào",
        event_short="ngày yên sau hỏi một trăm năm mươi tám",
        detail=(
            "trống không bằng yên hội; sau chữ ngựa, yên có thể mang kỵ giả; "
            "sáng sớm thấy một sợi da yên rơi ngoài cổng — không nhặt, phủ bụi"
        ),
        law="không thở phào, không mở rèm sớm, không rải vôi nghỉ, không nhặt da yên ngoài",
        report=(
            "Cổng trống. Ngoài trống. Không miệng. Da yên rơi ngoài đã phủ bụi. Không nhặt."
        ),
        order=(
            "Không thở phào. Không họp chữ ngựa. Không nhặt da yên ngoài. "
            "Không rải vôi nghỉ. Việc"
        ),
        scent="bụi cổng da yên",
        micro="da yên phủ bụi — không nhặt; không mừng yên",
        bones="Yên sau hỏi ngựa · trống ≠ yên hội · không thở phào · da yên ngoài phủ bụi không nhặt",
        panel_ev=(
            "Yên sau hỏi 158 · trống ≠ yên hội · không thở phào · ngựa · "
            "cấp im · máy nghèo"
        ),
        tag="yên sau ngựa",
    ),
    dict(
        n=853,
        day=973,
        day_vi="chín trăm bảy mươi ba",
        title="Sóng Thấp Lần 154",
        kind="song",
        open_hook="Lá dứa dại kêu khẽ khi gió bấc kéo qua bụi bắc-tây",
        place="bụi dứa dại bắc-tây",
        event_short="sóng thấp lần một trăm năm mươi tư",
        detail=(
            "bảy bóng thấp từ bụi dứa dại bắc-tây; không gào; chỉ sóng; máu kín; "
            "lá dứa dính tanh; chân thây vướng gốc dứa — lợi dụng; máu bó vải không vôi "
            "vì vôi thiếu sau sóng gò sườn"
        ),
        law="đâm thấp, không mặt, không đếm to, không phơi, hố xấu, máu vải không vôi",
        report=(
            "Bụi dứa dại bắc-tây. Bảy thấp. Không gào. Dấu riêng chỗ này. "
            "Dứa vướng. Không mang xẻng."
        ),
        order="Máu kín. Không đếm bảy to. Không phơi. Đổi chỗ lê. Hố xấu. Máu vải. Việc",
        scent="dứa dại tanh",
        micro="bảy thấp; dứa vướng; máu vải không vôi",
        bones="Bảy thấp bụi dứa bắc-tây · máu kín · dứa vướng · máu vải không vôi",
        panel_ev=(
            "Sóng thấp lần 154 · bụi dứa dại bắc-tây · bảy · máu kín · "
            "cấp im · máy nghèo"
        ),
        tag="sóng dứa bảy",
    ),
]
'''

m = re.search(r"^SPECS = \[", text, re.M)
if not m:
    raise SystemExit("SPECS not found")
start = m.start()
m2 = re.search(r"^def morning_cast", text, re.M)
if not m2:
    raise SystemExit("morning_cast not found")
end = m2.start()
new_text = text[:start] + new_specs + "\n\n" + text[end:]
dst.write_text(new_text, encoding="utf-8")
ast.parse(new_text)
print("SPECS replaced, syntax ok, size", dst.stat().st_size)
print("nums", re.findall(r"n=(\d+)", new_specs))
