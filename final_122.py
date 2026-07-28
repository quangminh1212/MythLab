#!/usr/bin/env python3
"""
FINAL script — 122 chapters, 122 UNIQUE scenes. Clean insert before note line.
Read each file, insert scene before the 'Ghi chú:' line, verify uniqueness.
"""
import os, re

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia/"

CHAPTER_SCENES = {
1: ("Hùng tắt đèn dầu, nằm xuống chiếu. Trần nhà tối om, tiếng dế kêu rả rích ngoài vườn.\n"
    "Ông đưa tay sờ vào khoảng không trống — hệ thống vẫn ở đó, lặng lẽ như trang giấy trắng.\n"
    "Một cuộc đời mới bắt đầu không bằng hoa hồng, mà bằng bước chân đầu tiên ra khỏi cửa."),
2: ("Bát cơm trắng trước mặt, bà Hà nhìn Hùng đầy dấu hỏi.\n"
    "Ông gắp cho bà miếng thịt, gắp cho Lan miếng trứng.\n"
    "Bà Hà im lặng, nhưng tay không ngừng gắp thêm cho cháu.\n"
    "Một bữa ăn không đổi đời trong một đêm. Nhưng nó đổi cách người ta nhìn nhau sáng hôm sau."),
3: ("Hùng đạp xe về khi nắng đã ngả vàng.\n"
    "Trong túi, tờ giấy chứng nhận mới, con dấu đỏ còn thơm mực.\n"
    "Con đường đất rung rinh dưới bánh xe, hai bên lúa non xanh rì.\n"
    "Ông nghĩ: huyện này, rồi tỉnh này, rồi xa hơn nữa."),
4: ("Tờ tiền đầu tiên trong tay, mồ hôi còn thấm ở mép.\n"
    "Khách quay lưng đi, Hùng đứng yên một lúc, nghe tim đập.\n"
    "Không phải vì tiền. Vì lần đầu tiên trong kiếp này, ông tự nuôi được mình.\n"
    "Ông xếp tiền vào túi vải, thắt nút ba lần, đạp xe về nhà trong bóng chiều."),
5: ("Tối về, Lan ghi vào sổ: \"Ngày thứ tư — có lãi.\"\n"
    "Bà Hà từ bếp đi ra, nhìn hai chị em rồi lặng lẽ bắc thêm nồi nước.\n"
    "Một tuần chưa qua, nhưng cái đói đã lùi xa thêm một bước."),
6: ("Bắt tay người lạ, Hùng nhìn thẳng vào mắt họ.\n"
    "Người thương hồ cũ nhất huyện bảo: \"Bắt tay mà mắt không dao động là được.\"\n"
    "Hùng ghi tên từng người vào sổ, bên cạnh ghi: \"Nợ — trả — nợ tiếp.\"\n"
    "Bắt đầu cuộc chơi của những lời hứa."),
7: ("Ngói mới phủ lên mái cũ, ánh sáng lọt qua khe trần không còn nữa.\n"
    "Bà Hà ngồi trong nhà, tay sờ vách gỗ mới, rồi ra bếp đập thêm quả trứng vào nồi canh.\n"
    "Hùng ngồi hiên nhìn mưa. Nước chảy xuống máng, không còn chảy vào nhà."),
8: ("Sổ của Hùng giờ có ba trang: vải, thuốc, xà phòng.\n"
    "Lan hỏi có dàn trải quá không. Hùng chỉ vào trang cuối — nơi ông viết: \"Hàng không đủ thì người ta mua chỗ khác.\"\n"
    "Tối đó, ông mang về thêm một cuộn dây thừng và một bao muối."),
9: ("Hiệu thuốc huyện tủ kính mờ bụi, thuốc bổ hết từ đầu quý.\n"
    "Hùng mang về ít vitamin, chia nhỏ, gói bằng giấy báo. Bà cụ ngoài xóm nhận thuốc, tay run run.\n"
    "Hùng lắc đầu không lấy tiền. Bà nói: \"Mày có hiếu.\" Ông không cãi."),
11: ("Chuyến đi Hà Nam về, trời đã tối. Hùng đạp xe dọc đường đê, một bên là sông, một bên là ruộng muộn.\n"
     "Trong túi, đơn đặt hàng của Tư Hạnh ghi rõ: \"Mười mét vải, bảy ngày.\"\n"
     "Một hợp đồng nhỏ. Nhưng là lần đầu ai đó gọi ông bằng cái tên có chữ \"anh\"."),
12: ("Hải Dương chiều muộn, chợ đã thưa. Hùng ngồi bên gốc đa với bà Uyên, xé tờ sổ thanh toán.\n"
     "Bà Uyên giữ một đầu, Hùng giữ một đầu. Từng tờ được kiểm đếm.\n"
     "\"Chị cân lại đi,\" Hùng nói. Bà Uyên cười: \"Tin mày rồi.\"\n"
     "Chữ tín bắt đầu bằng việc trả đủ, kể cả khi người kia không đòi."),
13: ("Thái Bình xa, đường đất trơn sau cơn mưa. Chị Hường chờ ở đầu chợ, tay cầm hai bát nước vối.\n"
     "\"Về muộn thì ngủ đây,\" chị nói như người quen hơn chục năm. Hùng lắc đầu, bấm đèn pin đạp về.\n"
     "Trên đường, ông tập hát — giọng thều thào giữa cánh đồng tối om."),
14: ("Mấy ngày sau, ba cái áo sơ mi bông — thành phẩm đầu tiên — ra lò.\n"
     "Bà Hà mặc thử. Áo rộng tay nhưng vừa người. Bà xoay trước gương mờ, không nói gì.\n"
     "Lan cúi đầu cắt chỉ thừa, khẽ cười. Hùng thấy mình đang dệt thứ quan trọng hơn vải."),
15: ("Chị Sáu và thằng Cu bắt đầu từ sáng hôm sau. Họ ngồi uống nước, nhìn nhau trong xưởng mới.\n"
     "\"Thử việc bảy ngày,\" Hùng nói. \"Cơm trưa tôi lo.\"\n"
     "Chị Sáu gật đầu, cầm kéo lên, xoay một vòng vải. Đường cắt thẳng tắp. Hùng thấy tay chị không run."),
16: ("Xưởng may chật kín ba máy. Vải vụn đầy góc, kim ghim trên tường.\n"
     "Hùng kê thêm bàn cắt bằng ván thùng. Trưa, bà Hà mang cơm ra, bốn người ngồi xổm ăn dưới bóng cây ổi.\n"
     "Chưa nhãn hiệu, chưa biển hiệu. Chỉ có bốn người biết sáng mai đi về đâu."),
17: ("Đường Quảng Ninh bụi đỏ. Hùng đứng bến xe, hòm hàng mẫu trên tay, bụi than bám áo.\n"
     "Chị Bé nói: \"Về Hà Nội không kịp bữa tối đâu.\"\n"
     "Hùng nhìn về phía ống khói nhà máy xa mờ — nơi những bộ áo ông may sẽ đến. Ổn thôi. Miễn hàng đến trước người."),
18: ("Nghệ An, Hùng xuống xe, chân tê rần. Gió Lào thổi khô khốc, cát bỏng dưới dép.\n"
     "Bà Phương đón ở đầu chợ, đưa vào quán, đặt trước mặt ấm trà xanh: \"Đồng chí đi xa. Uống đi rồi nói.\"\n"
     "Hùng mở hòm. Bà Phương xem từng đường kim, không khen, chỉ hỏi giá từng tấc."),
19: ("Hoàn thành lô hàng. Lan ghi dòng cuối: \"Lô NA-1 chốt. Đợt sau may thêm.\"\n"
     "Không hoan hô, không vỗ tay. Chỉ có nồi cơm bà Hà nấu đầy hơn mọi ngày.\n"
     "Hùng ngồi ăn, không nói. Trong đầu ông thấy rõ: xưởng nhỏ hôm nay, nhà máy một ngày không xa."),
21: ("Mẻ giày đầu tiên ra lò. Đế cao su còn nóng, mùi keo dính xộc vào mũi.\n"
     "Hùng xỏ thử vào chân, bước mấy bước. Chị Sáu bảo: \"Giày này mà ra huyện bán được.\"\n"
     "Hùng bỏ đôi giày lên kệ, ghi vào sổ: \"Giày nam — mẫu 01 — cần chỉnh cỡ.\"\n"
     "Một sản phẩm ra đời không phải khi nó được tạo ra, mà khi nó được xỏ vào chân người thật."),
22: ("Sài Gòn. Hùng bước xuống ga, ngợp trước dòng xe cộ tấp nập, biển hiệu đầy phố.\n"
     "Ông dừng lại quán cà phê vỉa hè, gọi ly đen đá. Cái vị đắng mát lạnh làm tỉnh cả người.\n"
     "Sài Gòn. Nơi bắt đầu của những thứ lớn hơn."),
23: ("Hùng ngồi với mẫu túi xách vẽ tay. Chị Sáu nhìn mẫu, chỉnh đường cong nắp túi.\n"
     "\"Chỗ này may cong thì nhìn sang hơn.\" Hùng gật, để chị tự may.\n"
     "Chiếc túi đầu tiên ra đời với đường chỉ hơi lệch ở nắp. Lan nói: \"Vẫn bán được.\" Hùng giữ lại làm kỷ niệm."),
24: ("Năm chiếc túi xách treo trên giá. Từ cuộn vải đến quai túi — tất cả tự tay họ làm.\n"
     "Chợ huyện thiếu túi xách. \"Đóng thêm năm cái nữa,\" ông nói. \"Màu khác.\""),
25: ("Cửa hàng thứ hai — một quầy nhỏ ở chợ giáp huyện — mở cửa. Hùng không đứng quầy.\n"
     "Buổi sáng đầu tiên: ba khách mua áo, một khách mua túi. Chị Sáu đếm tiền, ghi vào sổ.\n"
     "Hệ thống không báo gì. Nhưng Hùng thấy vui hơn là khi nhận điểm EXP."),
26: ("Mảnh đất góc làng — ba trăm mét vuông — được sang tên. Hùng đóng cọc gỗ làm mốc.\n"
     "Đất hơi thấp, phải tôn nền. Lan hỏi: \"Có chắc không?\" Hùng nhìn bốn góc, không đáp.\n"
     "Trời mưa nhẹ. Mưa trên đất mới. Hùng đứng thêm một lúc rồi mới đi."),
27: ("Lào, biên giới mờ khói bếp. Hùng qua cửa khẩu với một hòm vải và một cuốn sổ.\n"
     "Người buôn Lào nhìn hàng bằng tay. Hùng bán hết lô, mua ít gỗ trắc và mật ong rừng.\n"
     "Trên đường về, ông nghĩ: biên giới không phải rào cản, nếu hàng đủ tốt."),
28: ("Campuchia sau chiến tranh còn hoang tàn. Hùng gặp một người Việt gốc ở Kompong Chhnang.\n"
     "\"Ở đây thiếu vải, thiếu kim, thiếu chỉ. Nhưng nhiều quốc tế,\" ông ta nói.\n"
     "Hùng không hiểu \"nhiều quốc tế\" là gì. Cho đến khi thấy trại tị nạn với cờ trắng từ xa."),
29: ("Thái Lan. Hùng đi chợ Băng Cốc, mắt mở to. Hàng Thái đẹp, bóng, đủ màu sắc.\n"
     "Ông mua một cuộn lụa về làm mẫu. Trong khách sạn nhỏ, trải tấm lụa ra giường, sờ từng thớ.\n"
     "Người Thái làm vải mềm hơn mình. Hùng ghi nhớ."),
30: ("Cửa hàng lớn hơn, mặt tiền rộng hơn. Hùng thuê thêm hai người.\n"
     "Người ta gọi: \"Chủ hàng!\" Hùng chưa quen, nhưng biết nó đến cùng trách nhiệm.\n"
     "Tối, bà Hà nấu canh chua. Cả nhà ăn trong im lặng."),
31: ("Trang cuối năm 1983. Hùng lật từng tháng — gần hai trăm ngày từ khi tỉnh lại.\n"
     "Hàng bán ba tỉnh, bốn cửa hàng, hai xưởng. Ông viết: \"Năm 1983 — không ai chết đói trong nhà này.\"\n"
     "Bà Hà từ buồng đi ra, tay cầm bánh chưng: \"Ăn tết sớm đi con.\""),
32: ("Mẻ thực phẩm đầu tiên: nước mắm pha và ruốc sấy. Lan gói bằng lá chuối.\n"
     "Bà cụ mua hai gói, xé ra ngửi, gật đầu. Hùng không cần lời khen hơn thế.\n"
     "Từ vải đến thực phẩm — mỗi bước là một lần học lại từ đầu."),
33: ("Nồi nước mắm thêm mẻ thứ hai, thứ ba. Gian bếp bà Hà thành xưởng nhỏ.\n"
     "Mùi nước mắm quện với mùi vải bên cạnh. Hùng không ngăn. Nhà có mùi là nhà có người làm.\n"
     "Ông viết: \"Thực phẩm — lời mỏng, nhưng xoay vòng nhanh.\""),
51: ("Bắc Ninh, chi nhánh đầu tiên ngoài huyện. Căn nhà thuê mặt tiền chật, chỗ để hàng rộng.\n"
     "Lan điều hành, Hùng đứng sau. Mọi người tưởng cô là chủ.\n"
     "Chi nhánh đầu tiên là bước chân ra khỏi vùng an toàn."),
52: ("Minh ngồi đối diện Hùng, tay cầm bản vẽ động cơ hai kỳ. Hùng thấy thứ ông không tự làm được: kỹ thuật thực thụ.\n"
     "\"Lương em muốn bao nhiêu?\" Minh đưa ra một con số. Hùng không trả giá.\n"
     "Khoảnh khắc ấy, ông biết mình vừa mua được thứ đắt hơn tiền."),
53: ("Phòng khám An Tín khai trương. Không khánh tiết, chỉ có bác sĩ già và tủ thuốc nhỏ.\n"
     "Hùng để bảng nhỏ: \"Khám miễn phí tuần đầu.\" Ngày thứ hai, bốn người đến ngồi chờ."),
54: ("Nồi mì đầu tiên ra lò. Hùng nhìn gói mì do chính xưởng mình sản xuất. Lan ghi: \"Mẻ 01 — 300 gói.\"\n"
     "Từ vải, giày, túi đến mì gói — Thương Gia đã học cách đa dạng hóa từ những thứ nhỏ nhất."),
55: ("Hùng gấp tờ trình bày. Cuộc họp với cán bộ huyện kết thúc, giấy phép thí điểm có dấu đỏ.\n"
     "Trên đường về, ông dừng xe ở đầu làng, nhìn cánh đồng lúa đang vào vụ. Tháng Ba 1986, một chiều bình thường."),
56: ("Chín mươi ngày thử việc kết thúc. Minh đặt bản thiết kế cải tiến lên bàn Hùng.\n"
     "Hùng đứng dậy, bắt tay Minh: \"Ngày mai em bắt đầu lương chính thức.\"\n"
     "Minh cười — lần đầu tiên Hùng thấy anh cười."),
58: ("Tấm biển \"Thương Gia — Thương hiệu Việt\" treo lên mặt tiền. Chữ sơn đen trên nền gỗ.\n"
     "Lan đứng dưới đường nhìn lên: \"Vậy là mình có tên hả anh?\" Hùng siết con ốc cuối cùng."),
59: ("Chi nhánh Ninh Bình mở cửa, giao cho anh Đức. Hùng ở lại giúp kê kệ tối khai trương.\n"
     "Trên đường về, trời mưa, đường trơn, xe đạp lầy bánh. Trong lòng nhẹ. Chi nhánh thứ ba."),
60: ("Các chi nhánh đều có lãi sau tháng đầu. Lan hỏi: \"Có nên mở thêm không?\"\n"
     "Hùng lật sổ, nhìn các tỉnh còn trống, khoanh tròn ba cái tên. \"Mở. Nhưng từ từ.\""),
61: ("Mười chiếc xe đạp đầu tiên ra xưởng. Hùng đạp thử một vòng quanh sân, tay lái còn nặng.\n"
     "Minh điều chỉnh góc cổ lái. Mười chiếc xe lăn bánh trên đường đất là mười lần chữ tín."),
62: ("Chiếc máy cày hai bánh nổ máy giữa thửa ruộng. Mấy ông nông dân đứng xem, tay che nắng.\n"
     "Khi lưỡi cày lật đất, ai đó xuýt xoa: \"Chạy thật kìa.\" Hùng nắm chặt tay cày. Máy đầu tiên đã chạy."),
63: ("Hai máy gặt mẫu chạy thử trên đồng. Minh lau mồ hôi, cười tươi như trẻ con.\n"
     "Hùng đứng bờ ruộng, bẻ bông lúa, vo hạt bỏ vào miệng nhai. Hạt dẻo. Mùa này không còn cảnh gặt tay."),
64: ("Ba mươi xe tải đỗ thành hàng. Đủ loại, đủ đời. Hùng đi dọc, vỗ thử lốp, hỏi tài xế.\n"
     "Một anh lái hỏi: \"Cả trăm chiếc làm gì cho hết?\" Hùng tính: mỗi tỉnh hai chiếc, còn lại chở hàng xuất."),
65: ("Chi nhánh tài chính mở cửa. Hùng nhìn tờ giấy phép kinh doanh thứ tư.\n"
     "Từ bán vải đến cho vay — không tính trước, chỉ đáp ứng nhu cầu. Hệ thống ghi nhận thêm kỹ năng."),
66: ("Trường Thương Gia khởi công. Hùng cầm cuốc, rồi đưa cho một em nhỏ.\n"
     "\"Để sau này cháu kể: ngày xưa ông nội tao xây trường này.\" Đứa bé đập cuốc. Mọi người cười."),
67: ("Sài Gòn, một khu đất trống góc Bình Thạnh. Hùng đứng giữa cỏ dại, tay cầm bản vẽ.\n"
     "\"Sao không xây ở quận 1?\" — \"Học sinh ở quận 1 đã có trường. Chỗ này thì chưa.\""),
68: ("Trung tâm đào tạo mở lớp đầu tiên: năm nữ công nhân, ba thợ may, một kế toán.\n"
     "Chị Sáu dạy cắt may, Minh dạy bảo trì, Hùng dạy sổ sách. Không giáo trình. Không ai hỏi mấy giờ tan."),
69: ("Phòng khám An Tín mở rộng: thêm hai phòng, thêm bác sĩ trẻ. Phòng chờ đông hơn trước.\n"
     "Bác sĩ già nói: \"Đông vì khám không mất tiền mà thuốc tốt.\" Hùng thấy một mẹ bế con, một cụ chống gậy."),
70: ("Chuyến xe cuối cùng của nhiệm vụ vận chuyển lăn bánh lúc 4 giờ.\n"
     "Điện thoại reo: \"Hàng tới nơi, nguyên vẹn.\" Hùng gạch một dòng: \"NVVC — HOÀN THÀNH.\""),
71: ("Dịch vụ cho vay từ một cái bàn trong góc xưởng. Người vay đầu tiên: bà Tư bán hàng chợ.\n"
     "Không tài sản thế chấp, chỉ hai người làm chứng. Bà nhận tiền, gật đầu, không nói cảm ơn."),
72: ("Chi nhánh tài chính thứ hai — quầy nhỏ, một nhân viên, một két sắt cũ.\n"
     "Lan: \"Có người hỏi vay mua trâu.\" — \"Cho vay. Lãi nửa thị trường.\""),
73: ("Thí điểm cho vay hoàn thành, nợ xấu bằng không. Lan: \"Có nên mở rộng?\"\n"
     "Hùng so sánh lợi nhuận: \"Mở rộng. Nhưng mình là thương gia, không phải chủ nợ.\""),
74: ("Hai trường đầu kỳ cộng hai mươi tám trường mới — ba mươi. Mỗi trường có nhà vệ sinh, giếng nước.\n"
     "Lan hỏi: \"Có lễ khánh thành không?\" — \"Không cần. Trẻ con đi học là được.\""),
75: ("Ba mươi trường học. Mốc không dám nghĩ ba năm trước. Trường cuối — vùng cao, mái lá, bàn ghế mới.\n"
     "Cô giáo hỏi: \"Bác muốn nói gì với các cháu?\" Hùng nhìn ba mươi đứa trẻ: \"Học đi rồi giúp nước.\""),
78: ("Phòng khám mở rộng thêm ba cơ sở, tổng bảy. Số bệnh nhân tăng 40%.\n"
     "Hùng không cần biết hài lòng bao nhiêu. Cần biết họ có được cứu không."),
79: ("Bảy phòng khám, mười hai bác sĩ, ba mươi y tá. Bà Hà hỏi: \"Xây thêm nữa không?\"\n"
     "\"Để con cháu trong nhà theo ngành y, rồi tính.\" Bà Hà gật. Tối đó bà nấu thêm món."),
80: ("Công ty xây dựng thành lập. Một kỹ sư già, ba thợ nề, năm phụ hồ.\n"
     "Công trình đầu: mở rộng xưởng may. Hùng tự tay trát một mảng tường. Anh thợ nề lắc đầu cười."),
81: ("Máy phát diesel cấp điện cho xưởng. Bóng đèn dầu thay bằng đèn điện. Cả xưởng sáng trưng.\n"
     "Chị Sáu: \"Từ giờ không phải nheo mắt may nữa nhỉ?\""),
82: ("Nhà máy điện chạy ổn định, sản xuất tăng gấp đôi. Nhưng hóa đơn dầu diesel không nhỏ.\n"
     "Hùng ghi: \"Cần tìm năng lượng khác.\" Hướng đi mới hình thành."),
83: ("Quỹ từ thiện thành lập. Hùng chọn người đứng quỹ — cô giáo về hưu.\n"
     "\"Em không biết làm từ thiện kiểu công ty.\" — \"Thì làm kiểu nhà. Thấy ai khó thì giúp. Ghi sổ rõ ràng.\""),
85: ("Mười đối tác xuất khẩu: Ba Lan, Tiệp, Nhật, Pháp. Mỗi hợp đồng một ngôn ngữ, một chuẩn hàng.\n"
     "Lan lo: \"Sao mình làm nổi?\" — \"Mỗi người một việc. Minh lo kỹ thuật, em lo kế toán.\""),
86: ("Bảo hiểm Thương Gia ra đời. Sản phẩm đầu: bảo hiểm thân thể công nhân.\n"
     "Chị Sáu: \"Có bắt buộc không?\" — \"Không. Nhưng tôi mua cho tất cả. Công ty trả.\" Hôm sau không ai đi trễ."),
87: ("Máy cày ra mắt giữa đồng, hàng trăm nông dân kéo đến xem. Minh lái ba vòng, đất cày sâu, đều.\n"
     "Ông già sờ lưỡi cày: \"Bao nhiêu một cái?\" — \"Tiết kiệm được hai con trâu.\""),
88: ("Máy gặt ra mắt. Phục vụ miễn phí tuần đầu. Mấy chục héc-ta gặt trong ba ngày, thay vì ba tuần.\n"
     "Minh đứng trên máy suốt ba ngày, mặt đen nắng. Hùng mang cơm ra đồng cho anh."),
90: ("Phần 3 bắt đầu. Hùng viết: \"1986-1988 — Vươn ra biên giới.\"\n"
     "Bốn người: Hùng, Lan, Minh, Hạnh. Bốn cốc nước chè, một tờ A4, ba mục tiêu.\n"
     "\"Chúng ta sẽ làm lại từ đầu. Lần này có nhau.\""),
91: ("Lò thép Hải Phòng rực lửa. Minh giải thích về carbon, nhiệt độ, độ tinh khiết.\n"
     "Hùng hiểu: thép Việt không thua Thái nếu mình đầu tư đúng. \"Cứ làm. Có lỗ tôi chịu.\""),
92: ("Xi măng Thương Gia — lò thứ hai hoạt động, 78% công suất. Kỹ sư Việt vận hành.\n"
     "Hùng bốc nắm xi măng, bóp thử. Bột mịn, trắng, không vón. \"Chuẩn rồi.\""),
93: ("Hùng gặp cô Hạnh ở quán cà phê vỉa hè. Cô mang hồ sơ kiểm toán nội bộ.\n"
     "Hùng chưa đọc: \"Em làm được.\" — \"Anh chưa xem kỹ.\" — \"Nhìn mắt em biết thừa.\""),
94: ("Hùng gặp cô Mai và cô Lan. Cô Mai nói nhiều, cô Lan nói ít. Hùng chọn cô Lan.\n"
     "\"Người nói ít thường giữ bí mật. Làm tài chính cần người giữ được bí mật.\""),
95: ("Hùng chọn cô Hạnh — người duy nhất nói thẳng: \"Lương thế này em không làm được.\"\n"
     "\"Anh không cần người dễ bảo. Anh cần người dám bảo anh sai.\""),
97: ("Dây chuyền điện tử chạy thử. Minh soi bo mạch dưới đèn: \"Tỉ lệ đạt 92%.\"\n"
     "Hùng nhìn đường mạch đồng mảnh như sợi tóc. \"Tốt. Tháng sau nâng lên 95%.\""),
98: ("Chiếc điện thoại Thương Gia đầu tiên. Đen, đơn giản, nặng tay.\n"
     "Hùng nhấc ống nghe, quay số. \"A lô?\" — Giọng Lan từ phòng bên. Hùng cười."),
99: ("Viễn thông Thương Gia phủ sóng ba tỉnh. Hùng gọi chi nhánh Hà Nam, không qua bưu điện.\n"
     "Tư Hạnh: \"Anh Hùng hả? Nghe rõ quá!\" Ông cúp máy, gạch một dòng: viễn thông — OK."),
100: ("Phần mềm HT-QL1 chạy trên IBM PC XT 286. Màn hình xanh, dòng lệnh cuộn.\n"
      "\"Nghiệp vụ kế toán — thành công.\" Hùng nhớ kiếp Lý Minh. \"Giỏi. Nhưng còn bug. Sửa đi.\""),
101: ("108 cửa hàng toàn quốc. Lan: \"Không ngờ mình có ngày này.\"\n"
      "Hùng: \"Còn 108 tỉnh thành nữa.\" — \"Việt Nam có 63 tỉnh.\" — \"Thì ra nước ngoài.\""),
102: ("\"Bếp Xưa\" — chuỗi nhà hàng đầu tiên — mở cửa Hà Nội. Lan hỏi vì sao tên đó.\n"
      "\"Để người ta nhớ món ngày xưa ăn với bà.\" Bà Hà quay mặt đi. Hùng thấy bà quệt khóe mắt."),
103: ("Nhà máy thứ 30 đi vào hoạt động. Hùng đứng trước cổng, nhìn dây chuyền chạy.\n"
      "Từ một xưởng may sau nhà đến ba mươi nhà máy. Ông không nói gì, chỉ gật đầu với Minh."),
104: ("Container đầu tiên đi châu Âu — Ba Lan, 47.500 USD. Hùng đứng cảng Hải Phòng.\n"
      "Từ cuộn vải bán rong đến container xuất khẩu. \"Mai mốt ta đóng cả tàu,\" ông nói."),
105: ("Tổng kết Phần 3. Hùng đóng cuốn sổ dày nhất. 108 cửa hàng, 30 nhà máy, container châu Âu.\n"
      "Lan đọc báo cáo. Hùng nói: \"Làm tốt lắm.\" Hai tiếng hiếm hoi."),
106: ("Phần 4. Hùng viết: \"Ra thế giới.\" Đà Nẵng, Jakarta, Bangkok. Lan hỏi: \"Có sợ không?\"\n"
      "Hùng nhìn tàu khuất ở chân trời. \"Sợ. Nhưng không làm còn sợ hơn.\""),
108: ("Jakarta. Nhà máy Indonesia bắt đầu sản xuất. Công nhân mặc đồng phục Thương Gia.\n"
      "Quản lý hỏi: \"Ông muốn nói gì?\" Hùng lắc đầu. \"Họ làm tốt rồi.\""),
110: ("Bangkok Electronics thành công ty con đầu tiên ở nước ngoài. Hùng ký hợp đồng mua lại.\n"
      "Ông Somchai: \"Người Việt làm ăn tử tế.\" Cái bắt tay đó mở ra cả khu vực Đông Nam Á."),
118: ("Những ngày nằm viện. Hùng nhìn trần nhà trắng, nghe kim đồng hồ.\n"
      "Ông nghĩ về bà Hà gần tám mươi vẫn quảy gánh, về Lan chưa một lần than vãn."),
119: ("Bước ngoặt sức khỏe. Bác sĩ dặn giảm stress. Hùng tính: giao việc gì, bỏ cái gì.\n"
      "Từ hôm đó, ông không thức quá 10 giờ tối."),
122: ("Myanmar và Campuchia. Hùng đi với ông Tam, cựu binh Trường Sơn.\n"
      "Đứng bến phà Châu Đốc, Hùng hiểu: để hàng Việt đến nơi chưa từng tới."),
126: ("\"Giá trị của sự buông.\" Hùng gạch bỏ việc không cần, giao việc người khác làm tốt hơn.\n"
      "Buông để người khác lớn. Ra vườn, thấy cam đã ra trái."),
136: ("Nhật Bản — thị trường khó tính nhất. Hùng gặp ông Sato, người đặt câu hỏi về chất lượng.\n"
      "Ông Sato không bắt tay ngay. Ông xem mẫu hàng trong im lặng rồi hỏi: \"Tại sao tôi nên tin ông?\""),
138: ("Thử thách từ ông Sato: một lô hàng phải đạt chuẩn Nhật. Minh ở lại xưởng ba ngày liền.\n"
      "Khi lô hàng được thông qua, Hùng gửi cho ông Sato một hộp trà Việt."),
141: ("Chuyến bay đầu tiên đến Mỹ. Hùng ngồi cạnh cửa sổ, nhìn đất nước lùi dần.\n"
      "Tay ông nắm chặt tập tài liệu tiếng Anh dày, tự học từng từ trên máy bay."),
142: ("Thử thách đầu tiên tại Mỹ. Đối tác hỏi về chứng nhận chất lượng, Hùng chưa có.\n"
      "Ông nói thật: \"Chúng tôi sẽ có trong sáu tháng.\" Đối tác mỉm cười, cho ông 6 tháng."),
143: ("Los Angeles. Tiêu chuẩn kỹ thuật Mỹ dày hai trăm trang. Sinh viên UCLA phiên dịch.\n"
      "Một doanh nhân Việt ngồi đọc hai trăm trang tiêu chuẩn — chuyện chưa từng thấy."),
144: ("Bản đồ Mỹ trên tường với chấm đỏ khắp nơi. Linda: \"Anh đi xa quá nhỉ?\"\n"
      "Hùng chỉ vào Los Angeles: \"Từ đây, đi đâu cũng được.\""),
147: ("Lan đối mặt áp lực Mỹ. Đối tác đòi giảm giá 15%. Lan từ chối, giải thích từng khoản.\n"
      "Hùng ngồi sau, không nói. Khi đối tác đồng ý giá cũ, ông chỉ cười."),
148: ("Bữa tối ba thế hệ: bà Hà, Hùng, Lan. Bà gắp thức ăn cho cả hai, như ngày xưa.\n"
      "Hùng nhìn bà lúc chín mươi, thấy thời gian đã lấy đi sức khỏe nhưng không lấy đi tình thương."),
152: ("Văn Hùng nhận huân chương. Ông đứng trên bục, nhìn xuống hàng ghế. Lan ngồi hàng đầu.\n"
      "Bài phát biểu của ông chỉ có ba câu. Câu cuối: \"Cảm ơn những người đã tin tôi từ lúc không có gì.\""),
176: ("Lan về nước sau chuyến công tác châu Âu. Cô mang về bản hợp đồng xuất khẩu lớn nhất từ trước đến nay.\n"
      "Hùng đọc hợp đồng, gật đầu: \"Em lớn rồi.\" Lan cười, mệt nhưng vui."),
182: ("Quỹ đầu tư 200 tỷ, năm 1993, khung pháp lý chưa có. Luật sư: \"Chưa có.\" Hùng: \"Thì mình làm tiền lệ.\"\n"
      "Mang hồ sơ lên Ngân hàng Nhà nước: \"Anh xem giúp tôi hợp lệ không.\""),
191: ("Bốn bạn trẻ, hai bo mạch, một ước mơ. Căn tập thể cuối phố Huế.\n"
      "Người trẻ nhất: \"Tụi em không muốn Việt Nam mãi là xưởng gia công.\" Câu đó đủ rót tiền."),
194: ("Morgan Stanley gửi fax ba triệu USD. Hùng ngồi ba tiếng chỉ nghĩ.\n"
      "Gọi Lan: \"Đồng ý. Nhưng giữ quyền kiểm soát.\" Thế giới gõ cửa."),
195: ("Chìa khóa trên bàn. \"Từ mai em xử lý mảng Hà Nội.\" Lan hai mươi bảy tuổi.\n"
      "Cầm chìa khóa, không nói. Sáng hôm sau cô có mặt ở văn phòng từ 6 giờ."),
196: ("Bà Hà sức khỏe giảm. Bà nằm viện lần đầu. Hùng ngồi cạnh giường, tay giữ tay bà.\n"
      "Bà nói: \"Tao không lo nữa. Mày làm được rồi.\" Hùng không khóc trước mặt bà."),
200: ("Lễ kỷ niệm 10 năm Thương Gia. Hùng không tổ chức lớn, chỉ mời những người đầu tiên.\n"
      "Chị Sáu, thằng Cu, Minh, Lan — ngồi quanh mâm cơm, nhìn nhau, cười."),
208: ("New York, Wall Street. Hùng bước vào tòa nhà cao ốc, cà vạt thẳng, đầu ngẩng cao.\n"
      "Gã môi giới hỏi: \"Ông muốn bao nhiêu?\" — \"Không bao nhiêu. Tôi đến để học.\""),
220: ("Triển lãm công nghệ châu Á. Gian hàng Thương Gia nhỏ nhất hội trường.\n"
      "Nhưng sản phẩm của Minh — một cảm biến nông nghiệp — thu hút nhiều người xem nhất."),
250: ("Quỹ R&D 200 tỷ. Phản đối: \"Đầu tư đất có phải hơn?\" Hùng: \"Đất mua sau. Kỹ sư không mua gấp.\"\n"
      "Lan đứng quỹ: \"Anh giao em việc khó nhất.\" — \"Biết. Nên mới giao em.\""),
256: ("Top thương gia Việt Nam. Hùng được xếp hạng, nhưng ông không dự lễ.\n"
      "Hôm đó ông về làng, ăn cơm với bà Hà, ra thăm xưởng cũ."),
260: ("Cảng Tân Vũ, Hải Phòng. Container đi Hamburg, 240.000 USD.\n"
      "Gió biển mặn. Tàu rời cảng. Hùng đứng nhìn đến khi khuất dạng."),
264: ("Tái khẳng định sứ mệnh. Hùng viết lại tuyên ngôn của Thương Gia: \"Kinh doanh là tạo giá trị.\"\n"
      "Lan góp ý từng chữ. Bản cuối cùng chỉ có năm dòng."),
270: ("2008. Tổng kết mười hai năm — từ xưởng giày đến tập đoàn năm châu. Có trang ướt.\n"
      "\"Tạm được.\" Gấp sổ. Còn nhiều việc."),
272: ("Tòa soạn đầu tiên. Mua lại tờ báo sắp phá sản. HĐQT phản đối.\n"
      "Hùng: \"Truyền thông là tiếng nói. Thương gia có tiếng nói mới thực thụ.\""),
280: ("Trăm trường vùng sâu — từ bữa tối đến hiện thực. \"Hồi nhỏ không có trường. Giờ xây cho tụi nhỏ.\"\n"
      "Trường thứ một trăm khánh thành, Hùng ở nhà nấu cơm cho bà Hà."),
288: ("Khủng hoảng truyền thông giả. Một bài báo nói sai về Thương Gia. Thị trường hoảng loạn.\n"
      "Hùng không cải chính ngay. Ông mở sổ sách cho báo vào kiểm tra. Bài báo sai bị đính chính."),
299: ("Hùng 50 tuổi. Ông ngồi một mình bên bờ sông, nhìn lại nửa đời người.\n"
      "Từ chàng trai 30 tuổi tỉnh dậy trong thân xác lạ, đến ông chủ tập đoàn. Ông không hối tiếc."),
306: ("Gặp lại ông Sato sau hai mươi năm. Tóc bạc, đi chậm, mắt vẫn tinh.\n"
      "Ông đặt bộ ấm trà lên bàn: \"Tôi già rồi. Để lại cho học trò.\""),
309: ("Quỹ học bổng mang tên bà Hà. Bà không đồng ý: \"Sao lại lấy tên tao?\"\n"
      "Hùng cười: \"Để tụi nhỏ nhớ: có một bà già ở Quốc Oai thương tụi nó.\" Bà lắc đầu nhưng mắt sáng."),
311: ("Giải Thương gia huyền thoại. Hùng nhận giải, nhưng phát biểu chỉ nhắc đến nhân viên.\n"
      "\"Tôi chỉ là người mở cửa. Họ là người đi qua cánh cửa đó.\""),
313: ("Sách trắng quản trị Thương Gia. Hùng ngồi với luật sư, viết từng điều khoản.\n"
      "Bản sách trắng dày 50 trang, nhưng nguyên tắc cốt lõi chỉ một dòng: \"Làm đúng, ghi rõ, chịu trách nhiệm.\""),
328: ("Hà Nội, mùa thu 2015. Quỹ từ thiện 10.000 tỷ. Bà Hà chín mươi hai: \"Nhiều thế làm gì?\"\n"
      "\"Để sau này con cháu không phải nói 'ước gì'.\" Bà gật."),
344: ("Lễ bàn giao 2018. Hùng đọc quyết định, giọng không run. Bắt tay từng người.\n"
      "Về nhà, ngồi trong phòng tối một lúc lâu."),
349: ("EuroSynergy. Ông Pierre: \"Sao chọn Thương Gia? Hai mươi công ty, chỉ ông hỏi 'Chúng tôi học gì?\"\""),
352: ("Quỹ 100.000 tỷ. Bà Hà chín mươi chín đọc từng dòng. Ký xong bà nói:\n"
      "\"Đừng để ai chết vì thiếu tiền mua thuốc.\""),
356: ("Hoàng hôn tháng Chạp, Hùng về nhà cũ Quốc Oai. Bà nấu canh chua.\n"
      "Hùng ăn ba bát. Bà cười: \"Vẫn ăn khỏe là còn làm được.\" Bốn mươi năm trôi qua như một ngày."),
}

# Get all files
files = []
for f in os.listdir(BASE):
    if not f.endswith('.txt'):
        continue
    fpath = os.path.join(BASE, f)
    with open(fpath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if 'sổ cái khớp' in content:
        files.append(f)

def sort_key(f):
    m = re.search(r'(\d+)', f)
    return int(m.group(1)) if m else 9999

files_sorted = sorted(files, key=sort_key)
print(f"Files to process: {len(files_sorted)}")

count = 0
scene_texts = {}
repeats = []
missing = []

for fname in files_sorted:
    fpath = os.path.join(BASE, fname)
    m = re.search(r'(\d+)', fname)
    chap_num = int(m.group(1)) if m else 0
    
    if chap_num not in CHAPTER_SCENES:
        missing.append(fname)
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find the FIRST Ghi chú with sổ cái khớp
    note_idx = -1
    note_line = ""
    for i, line in enumerate(lines):
        if line.strip().startswith('Ghi chú') and 'sổ cái khớp' in line.strip():
            note_idx = i
            note_line = line
            break
    
    if note_idx < 0:
        missing.append(f"{fname} (no note)")
        continue
    
    scene = CHAPTER_SCENES[chap_num]
    scene_text = scene.strip()
    
    # Insert scene before the note, separated by blank line
    before = '\n'.join(lines[:note_idx])
    after = '\n'.join(lines[note_idx:])
    
    new_content = before + '\n' + scene_text + '\n\n' + after
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    count += 1
    
    # Verify uniqueness
    if scene_text in scene_texts:
        repeats.append(f"#{chap_num} ({fname}) = #{scene_texts[scene_text]}")
    scene_texts[scene_text] = chap_num
    
    print(f"{count:3d}. ✓ #{chap_num:3d} {fname}")

print(f"\n{'='*60}")
print(f"PATCHED: {count}")
print(f"UNIQUE SCENES: {len(set(scene_texts.keys()))}")
if repeats:
    print(f"REPEATS FOUND: {len(repeats)}")
    for r in repeats:
        print(f"  {r}")
if missing:
    print(f"MISSING SCENES: {len(missing)}")
    for m in missing:
        print(f"  {m}")
print(f"{'='*60}")
