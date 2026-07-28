#!/usr/bin/env python3
"""
Batch 1/3: Chapters 1-53 (34 chapters)
Replace each "Ghi chú: sổ cái khớp..." line with a unique closing scene (3-8 lines) + the note.
"""
import os, re

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia/"

# Chapter-specific unique closing scenes
SCENES = {
    # Chương 1: Tỉnh lại — isekai mở đầu
    1: (
        "Hùng tắt đèn dầu, nằm xuống chiếu. Trần nhà tối om, tiếng dế kêu ran ngoài vườn.\n"
        "Ông đưa tay sờ vào không gian trống — hệ thống vẫn ở đó, lặng lẽ như một trang giấy trắng.\n"
        "Một cuộc đời mới bắt đầu không bằng hoa hồng, mà bằng bước chân đầu tiên ra khỏi cửa."
    ),
    # Chương 2: Bữa tối đầu tiên — gia đình
    2: (
        "Bát cơm trắng trước mặt, bà Hà nhìn Hùng đầy dấu hỏi.\n"
        "Ông gắp cho bà miếng thịt, gắp cho Lan miếng trứng.\n"
        "Cơm còn ấm. Bà Hà im lặng, nhưng tay không ngừng gắp thêm cho cháu.\n"
        "Một bữa ăn có thể không đổi đời trong một đêm. Nhưng nó đổi cái cách người ta nhìn nhau sáng hôm sau."
    ),
    # Chương 3: Đi huyện thành — bước ra xã hội
    3: (
        "Hùng đạp xe về khi nắng đã ngả vàng.\n"
        "Trong túi, tờ giấy chứng nhận mới, con dấu đỏ còn thơm mực.\n"
        "Con đường đất rung rinh dưới bánh xe, hai bên lúa non xanh rì.\n"
        "Ông nghĩ: huyện này, rồi tỉnh này, rồi xa hơn nữa — từng bước một."
    ),
    # Chương 4: Bán hàng đầu tiên — giao dịch đầu
    4: (
        "Tờ tiền đầu tiên trong tay, mồ hôi còn thấm ở mép.\n"
        "Khách quay lưng đi, Hùng đứng yên một lúc, nghe tim đập.\n"
        "Không phải vì tiền. Vì lần đầu tiên trong kiếp này, ông tự nuôi được mình.\n"
        "Ông xếp tiền vào túi vải, thắt nút ba lần, đạp xe về nhà trong bóng chiều."
    ),
    # Chương 5: Mở rộng kinh doanh — mở rộng
    5: (
        "Tối về, Hùng trải hàng ra chiếu, đếm từng cuộn vải.\n"
        "Lan ngồi bên, lấy bút chì ghi vào sổ: \"Ngày thứ tư — có lãi.\"\n"
        "Bà Hà từ bếp đi ra, nhìn hai chị em rồi lặng lẽ bắc thêm nồi nước.\n"
        "Một tuần chưa qua, nhưng cái đói đã lùi xa thêm một bước."
    ),
    # Chương 6: Tìm đối tác mới — hợp tác
    6: (
        "Bắt tay người lạ, Hùng nhìn thẳng vào mắt họ.\n"
        "Không cần giấy tờ nhiều — người thương hồ cũ nhất ở huyện bảo: \"Bắt tay mà mắt không dao động là được.\"\n"
        "Hùng ghi tên từng người vào sổ, bên cạnh là đánh giá một dòng: \"Nợ — trả — nợ tiếp.\"\n"
        "Bắt đầu cuộc chơi của những lời hứa."
    ),
    # Chương 7: Sửa nhà — sửa mái ấm
    7: (
        "Ngói mới phủ lên mái cũ, ánh sáng lọt qua khe trần không còn nữa.\n"
        "Bà Hà ngồi trong nhà, nhìn lên trần lành lặn, tay sờ vách gỗ mới.\n"
        "Bà không nói gì, chỉ đi ra bếp đập thêm quả trứng vào nồi canh.\n"
        "Hùng ngồi hiên nhìn mưa. Nước chảy xuống máng, không còn chảy vào nhà."
    ),
    # Chương 8: Mở rộng hàng hóa — chủng loại
    8: (
        "Sổ của Hùng giờ có ba trang: vải, thuốc, xà phòng.\n"
        "Lan hỏi có dàn trải quá không. Hùng chỉ vào trang cuối — nơi ông viết: \"Hàng không đủ thì người ta mua chỗ khác.\"\n"
        "Ông không giải thích thêm. Nhưng tối đó, ông mang về thêm một cuộn dây thừng và một bao muối."
    ),
    # Chương 9: Bán thuốc men — thuốc
    9: (
        "Hiệu thuốc huyện vẫn thiếu thuốc bổ, vẫn tủ kiếng mờ bụi.\n"
        "Hùng mang về ít vitamin, chia nhỏ, gói bằng giấy báo.\n"
        "Bà cụ ngoài xóm nhận thuốc, tay run run, hỏi bao nhiêu.\n"
        "Hùng lắc đầu. Bà nói: \"Mày có hiếu.\" Ông không cãi."
    ),
    # Chương 11: Đi Hà Nam
    11: (
        "Chuyến đi Hà Nam về, trời đã tối. Hùng đạp xe dọc đường đê, một bên là sông, một bên là ruộng muộn.\n"
        "Trong túi, đơn đặt hàng của Tư Hạnh ghi rõ: \"Mười mét vải, bảy ngày.\"\n"
        "Một hợp đồng nhỏ. Nhưng là lần đầu ai đó gọi ông bằng cái tên có chữ \"anh\"."
    ),
    # Chương 12: Đi Hải Dương
    12: (
        "Hải Dương chiều muộn, chợ đã thưa. Hùng ngồi bên gốc đa với bà Uyên, xé tờ sổ thanh toán.\n"
        "Bà Uyên giữ một đầu, Hùng giữ một đầu. Từng tờ được kiểm đếm.\n"
        "\"Chị cân lại đi,\" Hùng nói. Bà Uyên cười: \"Tin mày rồi.\"\n"
        "Chữ tín bắt đầu bằng việc trả đủ, kể cả khi người kia không đòi."
    ),
    # Chương 13: Đi Thái Bình
    13: (
        "Thái Bình xa, đường đất trơn sau cơn mưa. Hùng đạp xe mệt lử, áo lấm bùn.\n"
        "Nhưng chị Hường đã chờ ở đầu chợ, tay cầm hai bát nước vối.\n"
        "\"Về muộn thì ngủ đây,\" chị nói như người quen hơn chục năm.\n"
        "Hùng lắc đầu, bấm đèn pin, đạp về trong đêm.\n"
        "Trên đường, ông tập hát — giọng thều thào giữa cánh đồng tối om."
    ),
    # Chương 14: Bắt đầu sản xuất
    14: (
        "Mấy ngày sau, Hùng mang ba cái áo sơ mi bông về nhà — thành phẩm đầu tiên của xưởng gia đình.\n"
        "Bà Hà mặc thử. Áo rộng tay nhưng vừa người. Bà xoay trước gương mờ, không nói gì trong giây lát.\n"
        "Lan cúi đầu cắt chỉ thừa, khẽ cười. Hùng nhìn hai người phụ nữ, thấy mình đang dệt thứ quan trọng hơn vải."
    ),
    # Chương 15: Thuê người giúp việc
    15: (
        "Chị Sáu và thằng Cu bắt đầu từ sáng hôm sau.\n"
        "Hùng không giao việc ngay. Họ ngồi uống nước, nhìn nhau trong căn xưởng mới sửa.\n"
        "\"Thử việc bảy ngày,\" Hùng nói. \"Cơm trưa tôi lo. Có thắc mắc gì thì nói.\"\n"
        "Chị Sáu gật đầu, cầm kéo lên, xoay một vòng vải. Đường cắt thẳng tắp.\n"
        "Hùng không nói, nhưng ông thấy tay chị không run."
    ),
    # Chương 16: Mở rộng xưởng may
    16: (
        "Xưởng may chật kín ba máy. Mảnh vải vụn đầy góc, kim ghim trên tường.\n"
        "Hùng kê thêm một bàn cắt nữa bằng ván thùng, chân kê gạch.\n"
        "Lan may liên tục, đầu ghim kẹp trên vai. Chị Sáu hướng dẫn thằng Cu đóng cúc.\n"
        "Trưa, bà Hà mang cơm ra, canh nóng, cà muối. Cả bốn người ngồi xổm ăn dưới bóng cây ổi.\n"
        "Chưa có nhãn hiệu. Chưa biển hiệu. Chỉ có bốn người biết sáng mai đi về đâu."
    ),
    # Chương 17: Đi Quảng Ninh
    17: (
        "Đường Quảng Ninh bụi đỏ. Hùng đứng ở bến xe, tay xách hòm hàng mẫu.\n"
        "Bụi than bám quần áo, mồ hôi chảy thành vệt trên má.\n"
        "Chị Bé nói: \"Về Hà Nội không kịp bữa tối đâu.\"\n"
        "Hùng nhìn về phía những ống khói nhà máy xa mờ trong khói bụi — nơi những bộ áo ông may sẽ đến.\n"
        "Ổn thôi. Miễn là hàng đến trước người."
    ),
    # Chương 18: Đi Nghệ An
    18: (
        "Nghệ An, Hùng xuống xe, chân tê rần. Gió Lào thổi khô khốc, cát bỏng rát dưới dép.\n"
        "Bà Phương đón ông ở đầu chợ, đưa vào quán nước, đặt trước mặt một ấm trà xanh.\n"
        "\"Đồng chí đi xa. Uống đi rồi nói chuyện.\" Giọng Nghệ nghe ấm hơn cái nắng ngoài kia.\n"
        "Hùng mở hòm vải. Bà Phương xem từng đường kim, không khen, chỉ hỏi giá từng tấc."
    ),
    # Chương 19: Hoàn thành nhiệm vụ sản xuất
    19: (
        "Hoàn thành lô hàng. Hùng đeo sổ lên giá, nhìn ba cột: đã cắt, đã may, đã kiểm.\n"
        "Lan ghi dòng cuối: \"Lô NA-1 chốt. Đợt sau may thêm.\"\n"
        "Không hoan hô. Không vỗ tay. Chỉ có nồi cơm bà Hà nấu đầy hơn mọi ngày.\n"
        "Hùng ngồi ăn, không nói. Nhưng trong đầu, ông thấy rõ con đường: xưởng nhỏ hôm nay, nhà máy một ngày không xa."
    ),
    # Chương 21: Mở rộng làm giày
    21: (
        "Mẻ giày đầu tiên ra lò. Đế cao su còn nóng, mùi keo dính xộc vào mũi.\n"
        "Hùng xỏ thử vào chân, bước mấy bước trên nền gạch. Hơi cứng, nhưng đứng vững.\n"
        "Chị Sáu bảo: \"Giày này mà ra huyện, bán được.\"\n"
        "Hùng bỏ đôi giày lên kệ, ghi vào sổ: \"Giày nam — mẫu 01 — cần chỉnh cỡ.\"\n"
        "Một sản phẩm mới ra đời không phải khi nó được tạo ra, mà khi nó được xỏ vào chân người thật."
    ),
    # Chương 22: Đi Thành phố Hồ Chí Minh
    22: (
        "Sài Gòn. Hùng bước xuống ga Sài Gòn, ngợp trước dòng xe cộ.\n"
        "Người xe tấp nập, biển hiệu đầy phố, hơi nóng bốc lên từ mặt đường nhựa.\n"
        "Ông dừng lại trước một quán cà phê vỉa hè, gọi ly đen đá.\n"
        "Cái vị đắng mát lạnh làm tỉnh cả người. Sài Gòn. Nơi bắt đầu của những thứ lớn hơn."
    ),
    # Chương 23: Sản xuất túi xách
    23: (
        "Hùng ngồi với mẫu túi xách vẽ tay — nắp tròn, quai ngắn, kiểu đơn giản.\n"
        "Chị Sáu nhìn mẫu một lúc, chỉnh đường cong nắp túi. \"Chỗ này may cong thì nhìn sang hơn.\"\n"
        "Hùng gật, để chị tự may. Chiếc túi đầu tiên ra đời với một đường chỉ hơi lệch ở nắp.\n"
        "Lan nói: \"Vẫn bán được.\" Hùng giữ lại làm kỷ niệm."
    ),
    # Chương 24: Mở rộng làm túi
    24: (
        "Năm chiếc túi xách treo trên giá, thành phẩm. Hùng đứng nhìn chúng một lúc lâu.\n"
        "Từ cuộn vải đến đường chỉ, từ nắp đến quai — tất cả tự tay họ làm.\n"
        "Không ai đặt hàng. Nhưng chợ huyện thiếu túi xách, và Hùng biết cửa hàng nào cũng cần một chiếc kệ để hàng.\n"
        "\"Đóng thêm năm cái nữa,\" ông nói. \"Màu khác.\""
    ),
    # Chương 25: Mở cửa hàng thứ hai
    25: (
        "Cửa hàng thứ hai — một quầy nhỏ ở chợ giáp huyện — mở cửa.\n"
        "Hùng không đứng quầy. Chị Sáu đứng. Lan ghi sổ từ xa.\n"
        "Buổi sáng đầu tiên: ba khách mua áo, một khách mua túi. Chị Sáu đếm tiền xong rồi ghi vào sổ.\n"
        "Hệ thống không báo gì. Nhưng Hùng thấy vui hơn là khi nhận điểm EXP."
    ),
    # Chương 26: Mua đất xây xưởng
    26: (
        "Mảnh đất góc làng — ba trăm mét vuông — được sang tên. Hùng đứng trên nền đất, đóng cọc gỗ làm mốc.\n"
        "Hai sào ruộng bỏ không, đất hơi thấp, phải tôn nền. Nhưng nó là của họ.\n"
        "Lan hỏi: \"Có chắc không?\" Hùng nhìn bốn góc mảnh đất, không đáp.\n"
        "Trời bắt đầu mưa nhẹ. Mưa trên đất mới. Hùng đứng thêm một lúc rồi mới đi."
    ),
    # Chương 27: Đi Lào
    27: (
        "Lào, biên giới mờ mờ khói bếp. Hùng qua cửa khẩu với một hòm vải và một cuốn sổ.\n"
        "Người buôn Lào ít nói, họ nhìn hàng bằng tay, không cần lời.\n"
        "Hùng bán hết lô, mua được ít gỗ trắc và mật ong rừng.\n"
        "Trên đường về, ông nghĩ: biên giới không phải rào cản, nếu hàng đủ tốt để người ta muốn."
    ),
    # Chương 28: Đi Campuchia
    28: (
        "Campuchia sau chiến tranh còn hoang tàn. Hùng đi dọc theo đường biên.\n"
        "Ông gặp một người Việt gốc ở Kompong Chhnang — ông ta nói tiếng Việt pha tiếng Khmer.\n"
        "\"Ở đây thiếu vải, thiếu kim, thiếu chỉ. Nhưng nhiều quốc tế,\" ông ta nói.\n"
        "Hùng không hiểu \"nhiều quốc tế\" là gì. Cho đến khi ông thấy một trại tị nạn với cờ trắng từ xa."
    ),
    # Chương 29: Đi Thái Lan
    29: (
        "Thái Lan — đất nước của nụ cười và vải lụa. Hùng đi chợ Băng Cốc, mắt mở to.\n"
        "Hàng Thái đẹp, bóng, đủ màu sắc. Ông mua một cuộn lụa về làm mẫu.\n"
        "Trong khách sạn nhỏ, ông trải tấm lụa ra giường, sờ tay từng thớ.\n"
        "Người Thái họ làm vải mềm hơn mình. Hùng ghi nhớ."
    ),
    # Chương 30: Mở rộng cửa hàng
    30: (
        "Cửa hàng lớn hơn, mặt tiền rộng hơn. Hùng thuê thêm hai người.\n"
        "Giờ đây, khi ông đi ngang, người ta gọi: \"Chủ hàng!\".\n"
        "Hùng chưa quen với cái tên đó. Nhưng ông biết nó đến cùng trách nhiệm.\n"
        "Tối, bà Hà nấu canh chua. Cả nhà ăn trong im lặng quen thuộc."
    ),
    # Chương 31: Tổng kết năm 1983
    31: (
        "Trang cuối cùng của năm 1983. Hùng lật lại từng tháng — gần hai trăm ngày từ khi tỉnh lại.\n"
        "EXP tổng 9. Hàng đã bán đi khắp ba tỉnh, bốn cửa hàng nhỏ, hai xưởng may.\n"
        "Ông viết xuống dòng: \"Năm 1983 — không ai chết đói trong nhà này.\"\n"
        "Bà Hà từ buồng đi ra, tay cầm cái bánh chưng còn nóng. \"Ăn tết sớm đi con.\""
    ),
    # Chương 32: Sản xuất thực phẩm
    32: (
        "Mẻ thực phẩm đầu tiên: một nồi nước mắm pha chế và ít ruốc sấy.\n"
        "Lan gói từng gói bằng lá chuối. Hùng mang ra chợ bán thử.\n"
        "Bà cụ mua hai gói, xé ra ngửi, gật đầu. Hùng không cần lời khen hơn thế.\n"
        "Từ vải đến thực phẩm — mỗi bước là một lần học lại từ đầu."
    ),
    # Chương 33: Mở rộng thực phẩm
    33: (
        "Nồi nước mắm thêm mẻ thứ hai, thứ ba. Gian bếp của bà Hà giờ thành xưởng nhỏ.\n"
        "Mùi nước mắm quện với mùi vải trong xưởng may bên cạnh.\n"
        "Hùng không ngăn. Nhà có mùi là nhà có người làm.\n"
        "Ông viết vào sổ: \"Thực phẩm — lời mỏng, nhưng xoay vòng nhanh.\""
    ),
    # Chương 51: Mở chi nhánh Bắc Ninh
    51: (
        "Bắc Ninh, một tỉnh trọng yếu. Hùng mở chi nhánh đầu tiên ngoài huyện.\n"
        "Căn nhà thuê ở thị xã, mặt tiền chật, nhưng chỗ để hàng rộng.\n"
        "Lan điều hành. Hùng đứng sau. Mọi người tưởng cô là chủ.\n"
        "Chi nhánh đầu tiên là bước chân ra khỏi vùng an toàn."
    ),
    # Chương 52: Tuyển kỹ sư Minh
    52: (
        "Minh ngồi đối diện Hùng, tay cầm bản vẽ động cơ hai kỳ.\n"
        "Hùng nhìn bản vẽ, thấy một thứ ông không tự làm được: kỹ thuật thực thụ.\n"
        "\"Lương em muốn bao nhiêu?\" Hùng hỏi. Minh đưa ra một con số.\n"
        "Hùng không trả giá. Khoảnh khắc ấy, ông biết mình vừa mua được thứ đắt hơn tiền."
    ),
    # Chương 53: Mở phòng khám
    53: (
        "Phòng khám An Tín khai trương. Không khánh tiết, chỉ có bác sĩ già về hưu và tủ thuốc nhỏ.\n"
        "Bà con trong làng nhìn người lạ vào ra, ngờ vực.\n"
        "Hùng không bảo ai đi khám. Ông để cái tủ thuốc mở và một tấm bảng nhỏ: \"Khám miễn phí tuần đầu.\"\n"
        "Ngày thứ hai, bốn người đến ngồi chờ."
    ),
}

# For chapters not yet assigned, use generic but unique scenes
DEFAULT_SCENES = [
    "Hùng gấp tờ sổ lại, nhìn ra ô cửa sổ nhỏ. Ngoài kia, con đường đất vẫn chưa trải nhựa, nhưng mỗi ngày ông đi nó đều thấy ngắn hơn.",
    "Tiếng máy may ngừng. Đêm xuống, chỉ còn tiếng dế và tiếng bà Hà ho trong nhà. Hùng viết tiếp trang sổ dưới ánh đèn dầu.",
    "Hùng cầm tờ hóa đơn trên tay, nhìn những con số. Lợi nhuận không lớn, nhưng nó đủ để mua thêm một cuộn vải.",
    "Trời mưa. Hùng đứng ở hiên nhìn nước chảy. Mỗi giọt mưa là một đơn hàng. Mỗi vũng nước là một bài học.",
    "Minh đưa bản vẽ đã sửa, Hùng gật đầu. Cỗ máy đầu tiên do người Việt thiết kế và do Thương Gia tài trợ bắt đầu có hình hài.",
    "Chén nước chè hết nhẫn. Hùng trả tiền, đứng dậy. Mối hàng mới không cần hợp đồng — chỉ cần cái bắt tay và ánh mắt không né.",
    "Hùng thắt lại dây giày, đứng lên. Còn mười tỉnh nữa. Còn mười năm nữa. Còn cả cuộc đời để xây một thứ mà người ta chỉ dám mơ.",
    "Tối, Hùng một mình ra bờ sông. Nước chảy vô tình, nhưng ông biết mình đi có hướng. Nếu không, đã không bắt đầu.",
    "Bà Hà bưng bát cháo từ bếp ra, đặt trước mặt Hùng. Ông không đói nhưng vẫn ăn hết. Từng muỗng.",
    "Lan từ chi nhánh gửi thư về. Tờ giấy chỉ vỏn vẹn: \"Bán chạy. Mỗi ngày thêm ba mối. Không nợ.\" Hùng gấp thư, cất vào ngăn sổ.",
    "Hùng rửa mặt bằng nước giếng, nước lạnh thấu xương. Tỉnh táo. Một ngày mới, một quyết định mới.",
    "Hiên nhà, ghế tre cũ kỹ. Hùng ngồi đến khi đèn dầu tắt. Có những quyết định không cần vội.",
    "Đèn đường huyện lẻ tẻ. Hùng đạp xe trong bóng tối, chỉ có ánh sao. Đường xa nhưng quen — như công việc này.",
    "Hùng viết một dòng cuối trang: \"Đừng quên hôm nay vì sao mình làm.\" Ông nhìn vài giây rồi gấp sổ.",
    "Kỹ sư Minh làm việc đến khuya. Hùng rót nước cho anh, không nói gì. Minh uống cạn rồi cắm mặt vào bản vẽ tiếp.",
    "Bảng giá niêm yết ngoài cửa hàng. Hùng đứng nhìn người mua. Họ đọc giá, so sánh, rồi mua. Thị trường vận hành thế đấy.",
    "Hùng đóng dấu lên tờ quyết định — dấu tròn, mực đỏ, tên công ty. Một cái dấu nhưng là cam kết của mấy chục con người.",
    "Buổi tối lành lạnh. Hùng mở cuốn sổ tay, viết: \"Năm nay khác. Không chỉ là sống. Là để lại.\"",
    "Lan và Hùng ngồi ngoài hiên, nhìn trăng. \"Em có tin nổi không?\" Lan hỏi. Hùng không trả lời, chỉ cười.",
    "Hùng nhìn tấm bản đồ Việt Nam. Mỗi tỉnh là một chấm tròn. Hơn chục chấm đã có — vài chấm nữa ông sẽ thêm.",
    "Cây ổi sau nhà trút lá. Hùng quét sân, nghĩ về mùa vụ mới. Công việc làm người ta không có thời gian để lo.",
    "Hùng xếp từng cuộn vải lên kệ, từng lọ thuốc lên tủ. Ngăn nắp. Trật tự. Một phần của chữ tín.",
    "Bát cơm nguội, miếng cà muối. Hùng ăn vội. Bà Hà nhìn rồi hỏi: \"Trưa mai có về không?\" Ông gật.",
    "Trong xưởng, tiếng máy đều đều. Hùng ngồi ở góc, lấy sổ ra ghi. Ghi xong, ông bỏ sổ vào ngăn bàn, khóa lại.",
    "Hùng nhận điện tín từng đoạn ngắn. Không điện đàm được, nhưng chữ viết trên giấy có trọng lượng riêng.",
    "Ông lấy quyển sổ cũ, lật lại. Từng trang đều có ngày tháng. Mỗi dòng là một quyết định. Sắp có trang mới.",
    "Đêm khuya. Hùng ra thăm gà, nhìn lên trời sao. Có một vì sao sáng lạ thường. Ông không tin điềm báo, nhưng thấy nhẹ lòng.",
    "Lá thư của đối tác gửi ra bưu điện. Hùng cầm trên tay, chưa mở. Ông đợi về nhà, ngồi ghế tre rồi mới xé tem.",
    "Hùng đặt tay lên cuốn sổ cuối cùng. Nó dày hơn những cuốn trước. Bìa mòn, giấy vàng. Nhưng chữ vẫn rõ.",
    "Chợ chiều tan. Hùng còn lại một mình, cuộn tấm bạt che hàng. Ông nói với anh bạn hàng cạnh: \"Mai tôi lên tỉnh.\"",
    "Cơn gió chiều thổi từ đồng vào. Hùng hít đầy phổi, vị lúa non và bụi đường. Vị của những ngày còn chưa biết mệt.",
    "Hùng dừng xe bên đường, uống nước. Người bán hàng hỏi: \"Đi xa không?\" Ông chỉ về phía trước.",
    "Bữa tối đơn giản, nhưng đông đủ. Hùng nhìn quanh bàn. Người già, người trẻ, người mới. Mái ấm không chỉ là mái.",
]

def read_last_body_lines(lines):
    """Find last meaningful body lines before the system footer."""
    body_end = len(lines)
    # Look for the system footer marker
    for i in range(len(lines)-1, -1, -1):
        line = lines[i].rstrip()
        if line.startswith('「Hệ thống') or line.startswith('Kỹ năng') or line.startswith('Tổng EXP') or line.startswith('Không gian'):
            continue
        if line == '':
            if i < len(lines)-3:
                pass
            continue
        body_end = i + 1
        break
    return body_end

# Get all files
import subprocess
result = subprocess.run(
    ['grep', '-rln', 'sổ cái khớp', '--include=*.txt', BASE],
    capture_output=True, text=True
)
files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

def sort_key(f):
    m = re.search(r'(\d+)', os.path.basename(f))
    return int(m.group(1)) if m else 9999

files_sorted = sorted(files, key=sort_key)

# Assign scenes
scene_idx = 0
COUNT = 0
for f in files_sorted:
    base = os.path.basename(f)
    m = re.search(r'(\d+)', base)
    chap_num = int(m.group(1)) if m else 0
    
    if chap_num in SCENES:
        scene = SCENES[chap_num]
    else:
        scene = DEFAULT_SCENES[scene_idx % len(DEFAULT_SCENES)]
        scene_idx += 1

    # Read file
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
        lines = content.split('\n')
    
    # Find the exact line with "sổ cái khớp"
    target_line_idx = -1
    for i, line in enumerate(lines):
        if 'sổ cái khớp' in line:
            target_line_idx = i
            break
    
    if target_line_idx < 0:
        print(f"WARNING: Could not find 'sổ cái khớp' in {base}")
        continue
    
    old_line = lines[target_line_idx]
    
    # New content: scene + blank line + the original note
    new_text = scene + '\n\n' + old_line
    
    # Replace in file
    old_text = old_line  # match the exact line
    
    new_content = content.replace(old_text, new_text, 1)
    
    if new_content == content:
        print(f"WARNING: Failed to replace in {base}")
        continue
    
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(new_content)
    
    COUNT += 1
    print(f"✓ #{chap_num} {base}")

print(f"\nBatch 1 complete: {COUNT} files patched")
