#!/usr/bin/env python3
"""
Apply 103 unique ending scenes to all chapters with "sổ cái khớp".
Scene inserted BEFORE the exact "Ghi chú: sổ cái khớp..." line.
"""
import os, re

BASE = "C:/Dev/XLab_MTC/Niên Đại Thương Gia/"

# 103 UNIQUE scenes — one per chapter, keyed by chapter number
SCENES = {
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
5: ("Tối về, Hùng trải hàng ra chiếu, đếm từng cuộn vải.\n"
    "Lan ngồi bên, lấy bút chì ghi vào sổ: \"Ngày thứ tư — có lãi.\"\n"
    "Bà Hà từ bếp đi ra, nhìn hai chị em rồi lặng lẽ bắc thêm nồi nước.\n"
    "Một tuần chưa qua, nhưng cái đói đã lùi xa thêm một bước."),
6: ("Bắt tay người lạ, Hùng nhìn thẳng vào mắt họ.\n"
    "Không cần giấy tờ nhiều — người thương hồ cũ nhất ở huyện bảo: \"Bắt tay mà mắt không dao động là được.\"\n"
    "Hùng ghi tên từng người vào sổ, bên cạnh là đánh giá một dòng: \"Nợ — trả — nợ tiếp.\"\n"
    "Bắt đầu cuộc chơi của những lời hứa."),
7: ("Ngói mới phủ lên mái cũ, ánh sáng lọt qua khe trần không còn nữa.\n"
    "Bà Hà ngồi trong nhà, nhìn lên trần lành lặn, tay sờ vách gỗ mới.\n"
    "Bà không nói gì, chỉ đi ra bếp đập thêm quả trứng vào nồi canh.\n"
    "Hùng ngồi hiên nhìn mưa. Nước chảy xuống máng, không còn chảy vào nhà."),
8: ("Sổ của Hùng giờ có ba trang: vải, thuốc, xà phòng.\n"
    "Lan hỏi có dàn trải quá không. Hùng chỉ vào trang cuối — nơi ông viết: \"Hàng không đủ thì người ta mua chỗ khác.\"\n"
    "Ông không giải thích thêm. Nhưng tối đó, ông mang về thêm một cuộn dây thừng và một bao muối."),
9: ("Hiệu thuốc huyện vẫn thiếu thuốc bổ, vẫn tủ kiếng mờ bụi.\n"
    "Hùng mang về ít vitamin, chia nhỏ, gói bằng giấy báo.\n"
    "Bà cụ ngoài xóm nhận thuốc, tay run run, hỏi bao nhiêu.\n"
    "Hùng lắc đầu. Bà nói: \"Mày có hiếu.\" Ông không cãi."),
11: ("Chuyến đi Hà Nam về, trời đã tối. Hùng đạp xe dọc đường đê, một bên là sông, một bên là ruộng muộn.\n"
     "Trong túi, đơn đặt hàng của Tư Hạnh ghi rõ: \"Mười mét vải, bảy ngày.\"\n"
     "Một hợp đồng nhỏ. Nhưng là lần đầu ai đó gọi ông bằng cái tên có chữ \"anh\"."),
12: ("Hải Dương chiều muộn, chợ đã thưa. Hùng ngồi bên gốc đa với bà Uyên, xé tờ sổ thanh toán.\n"
     "Bà Uyên giữ một đầu, Hùng giữ một đầu. Từng tờ được kiểm đếm.\n"
     "\"Chị cân lại đi,\" Hùng nói. Bà Uyên cười: \"Tin mày rồi.\"\n"
     "Chữ tín bắt đầu bằng việc trả đủ, kể cả khi người kia không đòi."),
13: ("Thái Bình xa, đường đất trơn sau cơn mưa. Hùng đạp xe mệt lử, áo lấm bùn.\n"
     "Nhưng chị Hường đã chờ ở đầu chợ, tay cầm hai bát nước vối.\n"
     "\"Về muộn thì ngủ đây,\" chị nói như người quen hơn chục năm.\n"
     "Hùng lắc đầu, bấm đèn pin, đạp về trong đêm.\n"
     "Trên đường, ông tập hát — giọng thều thào giữa cánh đồng tối om."),
14: ("Mấy ngày sau, Hùng mang ba cái áo sơ mi bông về nhà — thành phẩm đầu tiên của xưởng gia đình.\n"
     "Bà Hà mặc thử. Áo rộng tay nhưng vừa người. Bà xoay trước gương mờ, không nói gì trong giây lát.\n"
     "Lan cúi đầu cắt chỉ thừa, khẽ cười. Hùng nhìn hai người phụ nữ, thấy mình đang dệt thứ quan trọng hơn vải."),
15: ("Chị Sáu và thằng Cu bắt đầu từ sáng hôm sau.\n"
     "Hùng không giao việc ngay. Họ ngồi uống nước, nhìn nhau trong căn xưởng mới sửa.\n"
     "\"Thử việc bảy ngày,\" Hùng nói. \"Cơm trưa tôi lo. Có thắc mắc gì thì nói.\"\n"
     "Chị Sáu gật đầu, cầm kéo lên, xoay một vòng vải. Đường cắt thẳng tắp.\n"
     "Hùng không nói, nhưng ông thấy tay chị không run."),
16: ("Xưởng may chật kín ba máy. Mảnh vải vụn đầy góc, kim ghim trên tường.\n"
     "Hùng kê thêm một bàn cắt nữa bằng ván thùng, chân kê gạch.\n"
     "Lan may liên tục, đầu ghim kẹp trên vai. Chị Sáu hướng dẫn thằng Cu đóng cúc.\n"
     "Trưa, bà Hà mang cơm ra, canh nóng, cà muối. Cả bốn người ngồi xổm ăn dưới bóng cây ổi.\n"
     "Chưa có nhãn hiệu. Chưa biển hiệu. Chỉ có bốn người biết sáng mai đi về đâu."),
17: ("Đường Quảng Ninh bụi đỏ. Hùng đứng ở bến xe, tay xách hòm hàng mẫu.\n"
     "Bụi than bám quần áo, mồ hôi chảy thành vệt trên má.\n"
     "Chị Bé nói: \"Về Hà Nội không kịp bữa tối đâu.\"\n"
     "Hùng nhìn về phía những ống khói nhà máy xa mờ trong khói bụi — nơi những bộ áo ông may sẽ đến.\n"
     "Ổn thôi. Miễn là hàng đến trước người."),
18: ("Nghệ An, Hùng xuống xe, chân tê rần. Gió Lào thổi khô khốc, cát bỏng rát dưới dép.\n"
     "Bà Phương đón ông ở đầu chợ, đưa vào quán nước, đặt trước mặt một ấm trà xanh.\n"
     "\"Đồng chí đi xa. Uống đi rồi nói chuyện.\" Giọng Nghệ nghe ấm hơn cái nắng ngoài kia.\n"
     "Hùng mở hòm vải. Bà Phương xem từng đường kim, không khen, chỉ hỏi giá từng tấc."),
19: ("Hoàn thành lô hàng. Hùng đeo sổ lên giá, nhìn ba cột: đã cắt, đã may, đã kiểm.\n"
     "Lan ghi dòng cuối: \"Lô NA-1 chốt. Đợt sau may thêm.\"\n"
     "Không hoan hô. Không vỗ tay. Chỉ có nồi cơm bà Hà nấu đầy hơn mọi ngày.\n"
     "Hùng ngồi ăn, không nói. Nhưng trong đầu, ông thấy rõ con đường: xưởng nhỏ hôm nay, nhà máy một ngày không xa."),
21: ("Mẻ giày đầu tiên ra lò. Đế cao su còn nóng, mùi keo dính xộc vào mũi.\n"
     "Hùng xỏ thử vào chân, bước mấy bước trên nền gạch. Hơi cứng, nhưng đứng vững.\n"
     "Chị Sáu bảo: \"Giày này mà ra huyện, bán được.\"\n"
     "Hùng bỏ đôi giày lên kệ, ghi vào sổ: \"Giày nam — mẫu 01 — cần chỉnh cỡ.\"\n"
     "Một sản phẩm mới ra đời không phải khi nó được tạo ra, mà khi nó được xỏ vào chân người thật."),
22: ("Sài Gòn. Hùng bước xuống ga, ngợp trước dòng xe cộ.\n"
     "Người xe tấp nập, biển hiệu đầy phố, hơi nóng bốc lên từ mặt đường nhựa.\n"
     "Ông dừng lại trước một quán cà phê vỉa hè, gọi ly đen đá.\n"
     "Cái vị đắng mát lạnh làm tỉnh cả người. Sài Gòn. Nơi bắt đầu của những thứ lớn hơn."),
23: ("Hùng ngồi với mẫu túi xách vẽ tay — nắp tròn, quai ngắn, kiểu đơn giản.\n"
     "Chị Sáu nhìn mẫu một lúc, chỉnh đường cong nắp túi. \"Chỗ này may cong thì nhìn sang hơn.\"\n"
     "Hùng gật, để chị tự may. Chiếc túi đầu tiên ra đời với một đường chỉ hơi lệch ở nắp.\n"
     "Lan nói: \"Vẫn bán được.\" Hùng giữ lại làm kỷ niệm."),
24: ("Năm chiếc túi xách treo trên giá, thành phẩm. Hùng đứng nhìn chúng một lúc lâu.\n"
     "Từ cuộn vải đến đường chỉ, từ nắp đến quai — tất cả tự tay họ làm.\n"
     "Không ai đặt hàng. Nhưng chợ huyện thiếu túi xách.\n"
     "\"Đóng thêm năm cái nữa,\" ông nói. \"Màu khác.\""),
25: ("Cửa hàng thứ hai — một quầy nhỏ ở chợ giáp huyện — mở cửa.\n"
     "Hùng không đứng quầy. Chị Sáu đứng. Lan ghi sổ từ xa.\n"
     "Buổi sáng đầu tiên: ba khách mua áo, một khách mua túi. Chị Sáu đếm tiền xong rồi ghi vào sổ.\n"
     "Hệ thống không báo gì. Nhưng Hùng thấy vui hơn là khi nhận điểm EXP."),
26: ("Mảnh đất góc làng — ba trăm mét vuông — được sang tên. Hùng đứng trên nền đất, đóng cọc gỗ làm mốc.\n"
     "Hai sào ruộng bỏ không, đất hơi thấp, phải tôn nền. Nhưng nó là của họ.\n"
     "Lan hỏi: \"Có chắc không?\" Hùng nhìn bốn góc mảnh đất, không đáp.\n"
     "Trời bắt đầu mưa nhẹ. Mưa trên đất mới. Hùng đứng thêm một lúc rồi mới đi."),
27: ("Lào, biên giới mờ mờ khói bếp. Hùng qua cửa khẩu với một hòm vải và một cuốn sổ.\n"
     "Người buôn Lào ít nói, họ nhìn hàng bằng tay, không cần lời.\n"
     "Hùng bán hết lô, mua được ít gỗ trắc và mật ong rừng.\n"
     "Trên đường về, ông nghĩ: biên giới không phải rào cản, nếu hàng đủ tốt để người ta muốn."),
28: ("Campuchia sau chiến tranh còn hoang tàn. Hùng đi dọc theo đường biên.\n"
     "Ông gặp một người Việt gốc ở Kompong Chhnang — ông ta nói tiếng Việt pha tiếng Khmer.\n"
     "\"Ở đây thiếu vải, thiếu kim, thiếu chỉ. Nhưng nhiều quốc tế,\" ông ta nói.\n"
     "Hùng không hiểu \"nhiều quốc tế\" là gì. Cho đến khi ông thấy một trại tị nạn với cờ trắng từ xa."),
29: ("Thái Lan — đất nước của nụ cười và vải lụa. Hùng đi chợ Băng Cốc, mắt mở to.\n"
     "Hàng Thái đẹp, bóng, đủ màu sắc. Ông mua một cuộn lụa về làm mẫu.\n"
     "Trong khách sạn nhỏ, ông trải tấm lụa ra giường, sờ tay từng thớ.\n"
     "Người Thái họ làm vải mềm hơn mình. Hùng ghi nhớ."),
30: ("Cửa hàng lớn hơn, mặt tiền rộng hơn. Hùng thuê thêm hai người.\n"
     "Giờ đây, khi ông đi ngang, người ta gọi: \"Chủ hàng!\".\n"
     "Hùng chưa quen với cái tên đó. Nhưng ông biết nó đến cùng trách nhiệm.\n"
     "Tối, bà Hà nấu canh chua. Cả nhà ăn trong im lặng quen thuộc."),
31: ("Trang cuối cùng của năm 1983. Hùng lật lại từng tháng — gần hai trăm ngày từ khi tỉnh lại.\n"
     "Hàng đã bán đi khắp ba tỉnh, bốn cửa hàng nhỏ, hai xưởng may.\n"
     "Ông viết xuống dòng: \"Năm 1983 — không ai chết đói trong nhà này.\"\n"
     "Bà Hà từ buồng đi ra, tay cầm cái bánh chưng còn nóng. \"Ăn tết sớm đi con.\""),
32: ("Mẻ thực phẩm đầu tiên: một nồi nước mắm pha chế và ít ruốc sấy.\n"
     "Lan gói từng gói bằng lá chuối. Hùng mang ra chợ bán thử.\n"
     "Bà cụ mua hai gói, xé ra ngửi, gật đầu. Hùng không cần lời khen hơn thế.\n"
     "Từ vải đến thực phẩm — mỗi bước là một lần học lại từ đầu."),
33: ("Nồi nước mắm thêm mẻ thứ hai, thứ ba. Gian bếp của bà Hà giờ thành xưởng nhỏ.\n"
     "Mùi nước mắm quện với mùi vải trong xưởng may bên cạnh.\n"
     "Hùng không ngăn. Nhà có mùi là nhà có người làm.\n"
     "Ông viết vào sổ: \"Thực phẩm — lời mỏng, nhưng xoay vòng nhanh.\""),
51: ("Bắc Ninh, một tỉnh trọng yếu. Hùng mở chi nhánh đầu tiên ngoài huyện.\n"
     "Căn nhà thuê ở thị xã, mặt tiền chật, nhưng chỗ để hàng rộng.\n"
     "Lan điều hành. Hùng đứng sau. Mọi người tưởng cô là chủ.\n"
     "Chi nhánh đầu tiên là bước chân ra khỏi vùng an toàn."),
52: ("Minh ngồi đối diện Hùng, tay cầm bản vẽ động cơ hai kỳ.\n"
     "Hùng nhìn bản vẽ, thấy một thứ ông không tự làm được: kỹ thuật thực thụ.\n"
     "\"Lương em muốn bao nhiêu?\" Hùng hỏi. Minh đưa ra một con số.\n"
     "Hùng không trả giá. Khoảnh khắc ấy, ông biết mình vừa mua được thứ đắt hơn tiền."),
53: ("Phòng khám An Tín khai trương. Không khánh tiết, chỉ có bác sĩ già về hưu và tủ thuốc nhỏ.\n"
     "Bà con trong làng nhìn người lạ vào ra, ngờ vực.\n"
     "Hùng không bảo ai đi khám. Ông để cái tủ thuốc mở và một tấm bảng nhỏ: \"Khám miễn phí tuần đầu.\"\n"
     "Ngày thứ hai, bốn người đến ngồi chờ."),
54: ("Nồi nước sôi, gói mì thả xuống, mùi gia vị lan tỏa trong căn bếp nhỏ.\n"
     "Hùng nhìn gói mì đầu tiên do chính xưởng mình sản xuất.\n"
     "Lan ghi vào sổ: \"Mẻ 01 — 300 gói — thành phẩm.\"\n"
     "Từ vải, giày, túi đến mì gói — Thương Gia đã học cách đa dạng hóa từ những thứ nhỏ nhất."),
55: ("Hùng gấp tờ trình bày lại. Cuộc họp với cán bộ huyện kết thúc.\n"
     "Trong tay ông là tờ giấy phép thí điểm có dấu đỏ.\n"
     "Một bước đi mới cho Thương Gia: tự chủ, có kiểm chứng.\n"
     "Trên đường về, ông dừng xe ở đầu làng, nhìn cánh đồng lúa đang vào vụ. Tháng Ba năm 1986, một chiều bình thường nhưng lịch sử đang được viết."),
56: ("Chín mươi ngày thử việc kết thúc. Minh đặt bộ hồ sơ lên bàn Hùng — bản thiết kế cải tiến cho máy xay bột.\n"
     "Hùng nhìn từng trang, không nói. Cuối cùng, ông đứng dậy, bắt tay Minh.\n"
     "\"Ngày mai em bắt đầu lương chính thức.\"\n"
     "Minh cười — lần đầu tiên Hùng thấy anh cười."),
58: ("Tấm biển \"Thương Gia — Thương hiệu Việt\" được treo lên mặt tiền.\n"
     "Chữ sơn đen trên nền gỗ, do chính tay Hùng viết.\n"
     "Lan đứng dưới đường nhìn lên, nheo mắt: \"Vậy là mình có tên hả anh?\"\n"
     "Hùng không trả lời, chỉ siết con ốc cuối cùng thật chặt."),
59: ("Chi nhánh Ninh Bình mở cửa. Hùng giao cho anh Đức — người địa phương, từng bán hàng thuê cho xưởng.\n"
     "Buổi tối trước khai trương, Hùng ở lại giúp anh Đức kê kệ.\n"
     "Trên đường về, trời mưa, đường đất trơn. Xe đạp lầy bánh, Hùng dắt bộ hơn cây số.\n"
     "Nhưng trong lòng nhẹ. Chi nhánh thứ ba. Thêm một nhịp."),
60: ("Hoàn thành nhiệm vụ chi nhánh. Hùng tổng kết trong sổ: tất cả các chi nhánh đều có lãi sau tháng đầu.\n"
     "Lan hỏi: \"Có nên mở thêm không?\"\n"
     "Hùng lật sổ, nhìn danh sách các tỉnh còn trống. Ông khoanh tròn ba cái tên.\n"
     "\"Mở. Nhưng từ từ.\""),
61: ("Mười chiếc xe đạp đầu tiên ra xưởng. Hùng đạp thử một vòng quanh sân, tay lái còn hơi nặng.\n"
     "Minh đứng bên, ghi chú vào sổ tay: điều chỉnh góc cổ lái, tăng độ dày ruột xăm.\n"
     "Hùng gật gù. Sản xuất xe đạp không khó bằng sản xuất lòng tin vào hàng Việt Nam thời bao cấp.\n"
     "Nhưng mười chiếc xe lăn bánh trên đường đất là mười lần chữ tín đặt xuống."),
62: ("Chiếc máy cày hai bánh nổ máy giữa thửa ruộng. Tiếng động cơ xé tanh tách bầu không khí yên tĩnh.\n"
     "Mấy ông nông dân đứng xem, tay che nắng, mắt dõi theo luống cày đầu tiên.\n"
     "Khi lưỡi cày lật đất, ai đó xuýt xoa: \"Chạy thật kìa.\"\n"
     "Hùng không nói, nhưng tay ông nắm chặt tay cày. Chiếc máy đầu tiên do Minh thiết kế và do Thương Gia sản xuất đã chạy."),
63: ("Hai máy gặt xếp dải mẫu chạy thử trên đồng. Lúa được cắt gọn, xếp thành hàng đều tăm tắp.\n"
     "Minh nâng kính bảo hộ lên, lau mồ hôi, cười tươi như đứa trẻ.\n"
     "Hùng đứng ngoài bờ, tay bẻ một bông lúa, vo hạt, bỏ vào miệng nhai.\n"
     "Hạt dẻo. Mùa này sẽ không còn cảnh phụ nữ còng lưng gặt tay dưới nắng tháng Năm."),
64: ("Ba mươi chiếc xe tải đỗ thành hàng dài trước xưởng. Đủ loại: ZIN 130, KAMAZ, một vài chiếc Hyundai cũ của lính Mỹ để lại.\n"
     "Hùng đi dọc dãy xe, tay gõ thử lốp, nhìn vào gầm, hỏi tài xế từng chiếc.\n"
     "Một anh lái xe nói: \"Cả trăm chiếc như này làm gì cho hết?\".\n"
     "Hùng không trả lời. Ông tính: mỗi tỉnh hai chiếc, mỗi chi nhánh một chiếc, còn lại để chở hàng xuất."),
65: ("Chi nhánh tài chính mở cửa. Biển hiệu nhỏ, nhưng dòng chữ \"Thương Gia Tín Dụng\" làm vài người trong huyện chú ý.\n"
     "Hùng ngồi trong phòng làm việc mới, nhìn tờ giấy phép kinh doanh thứ tư được cấp.\n"
     "Từ bán vải đến cho vay — con đường này ông không tính trước. Nhưng khi sổ sách có lãi, người ta cần giữ tiền và cần vay tiền.\n"
     "Hùng chỉ đáp ứng nhu cầu. Hệ thống ghi nhận thêm một kỹ năng."),
66: ("Trường học đầu tiên mang tên Thương Gia khởi công.\n"
     "Hùng cầm cuốc xuống lễ động thổ, nhưng ông không phải người đập cuốc đầu tiên. Ông đưa cuốc cho một em nhỏ đứng gần đó.\n"
     "\"Để sau này cháu kể lại: ngày xưa ông nội tao xây trường này.\"\n"
     "Đứa bé đập cuốc xuống đất. Mọi người cười. Hùng không cười, nhưng mắt ông hơi cay."),
67: ("Sài Gòn, một khu đất trống góc quận Bình Thạnh. Hùng đứng giữa đám cỏ dại, tay cầm bản vẽ trường học.\n"
     "Đối tác hỏi: \"Sao không xây ở quận 1, đất đắt hơn nhưng dễ gọi tên?\".\n"
     "Hùng chỉ vào bản vẽ: \"Học sinh ở quận 1 đã có trường. Chỗ này thì chưa.\"\n"
     "Trường Sài Gòn khởi công tháng sau. Hùng không dự lễ."),
68: ("Trung tâm đào tạo Thương Gia — một dãy nhà cấp bốn sau xưởng may — mở lớp đầu tiên.\n"
     "Học viên: năm nữ công nhân, ba thợ may lành nghề, một kế toán trẻ.\n"
     "Giảng viên: chị Sáu dạy cắt may, Minh dạy bảo trì máy, Hùng dạy sổ sách.\n"
     "Buổi học đầu tiên không có giáo trình. Nhưng cuối buổi, không ai hỏi mấy giờ tan."),
69: ("Phòng khám An Tín mở rộng: thêm hai phòng khám, thêm một bác sĩ trẻ mới ra trường.\n"
     "Hùng đến thăm, thấy phòng chờ đông hơn trước. Người bệnh mang cả ghế từ nhà đến.\n"
     "Bác sĩ già về hưu — giờ là trưởng khoa — nói: \"Bệnh nhân đông vì khám không mất tiền mà thuốc lại tốt.\"\n"
     "Hùng nhìn quanh, thấy một người mẹ bế con, một cụ già chống gậy, và yên tâm."),
70: ("Chuyến xe tải cuối cùng của nhiệm vụ vận chuyển lăn bánh vào lúc 4 giờ chiều.\n"
     "Hùng đứng ở cổng xưởng nhìn theo. Hàng đã lên đường, người lái đã nhận chỉ dẫn.\n"
     "Một cuộc gọi từ chi nhánh Đà Nẵng báo: \"Hàng tới nơi rồi. Nguyên vẹn.\"\n"
     "Hùng không trả lời. Ông chỉ gạch một dòng trong sổ: \"NVVC — HOÀN THÀNH.\""),
71: ("Dịch vụ cho vay mở ra từ một cái bàn nhỏ trong góc xưởng. Hùng tự tay viết hợp đồng đầu tiên.\n"
     "Người vay là bà Tư, bán hàng ngoài chợ, cần vốn xoay vòng.\n"
     "Không tài sản thế chấp. Chỉ có hai người làm chứng và lời hứa trả đúng hạn.\n"
     "Hùng đưa tiền. Bà Tư nhận, gật đầu một cái, không nói cảm ơn. Ở làng, người ta không cảm ơn bằng lời khi nhận tiền vay."),
72: ("Chi nhánh tài chính thứ hai khai trương ở thị xã. Một quầy nhỏ, một nhân viên, một két sắt cũ.\n"
     "Lan nói: \"Có người hỏi vay để mua trâu.\"\n"
     "Hùng gật: \"Cho vay. Lãi bằng nửa thị trường.\"\n"
     "Lan nhíu mày. Hùng giải thích: \"Trâu mua về cày được, người vay trả được, ta có lãi. Còn lãi cao quá họ không trả được thì mất cả vốn.\""),
73: ("Nhiệm vụ thí điểm cho vay hoàn thành. Hùng ngồi tổng kết: tỷ lệ nợ xấu bằng không, dư nợ đúng hạn.\n"
     "Lan mang cà phê vào, hỏi: \"Có nên mở rộng không?\"\n"
     "Hùng nhìn con số lợi nhuận từ cho vay, nhìn số lợi nhuận từ may mặc, so sánh.\n"
     "\"Mở rộng. Nhưng không được quên gốc: mình là thương gia, không phải chủ nợ.\""),
74: ("Hai trường đầu kỳ cộng hai mươi tám trường mới đủ điều kiện — ba mươi trường mang tên Thương Gia.\n"
     "Hùng nhận báo cáo từ đội khảo sát: mỗi trường đều có nhà vệ sinh riêng, có giếng nước, có bảng đen.\n"
     "Lan hỏi: \"Có tổ chức lễ khánh thành không?\"\n"
     "Hùng lắc đầu: \"Không cần. Trẻ con đi học là được.\""),
75: ("Ba mươi trường học. Một mốc mà Hùng không dám nghĩ tới ba năm trước.\n"
     "Ông đứng ở trường cuối cùng — một điểm trường vùng cao, mái lá, vách đất, nhưng trong lớp có bàn ghế mới.\n"
     "Cô giáo trẻ hỏi: \"Bác có muốn nói gì với các cháu không?\"\n"
     "Hùng nhìn ba mươi đứa trẻ đang ngồi ngay ngắn trên ghế. \"Học đi rồi sau này giúp nước.\""),
78: ("Phòng khám mở rộng thêm ba cơ sở nữa. Tổng cộng bảy phòng khám An Tín trên cả nước.\n"
     "Bác sĩ già viết báo cáo: \"Số bệnh nhân khám tăng 40% so với quý trước.\"\n"
     "Hùng xem báo cáo, gạch dưới một con số: \"Số ca chuyển viện kịp thời — 100%.\"\n"
     "Ông không cần biết bệnh nhân hài lòng bao nhiêu phần trăm. Ông cần biết họ có được cứu không."),
79: ("Nhiệm vụ phòng khám hoàn thành. Hùng tổng kết: bảy phòng khám, mười hai bác sĩ, ba mươi y tá.\n"
     "Ngân sách năm sau được duyệt. Bà Hà hỏi: \"Xây thêm nữa không?\"\n"
     "Hùng trả lời: \"Để các con cháu trong nhà theo ngành y, rồi tính tiếp.\"\n"
     "Bà Hà gật, không nói thêm. Nhưng tối đó bà nấu thêm một món."),
80: ("Công ty xây dựng Thương Gia thành lập. Đội ngũ: một kỹ sư xây dựng vừa nghỉ hưu từ nhà nước, ba thợ nề, năm phụ hồ.\n"
     "Hùng không xây nhà cho thuê. Ông xây trường học, phòng khám, xưởng sản xuất.\n"
     "Công trình đầu tiên: mở rộng xưởng may. Hùng cầm bay tự tay trát một mảng tường.\n"
     "Anh thợ nề nhìn ông, lắc đầu cười. Chủ doanh nghiệp tự trát tường, lần đầu thấy."),
81: ("Nhà máy điện nhỏ — một máy phát diesel công nghiệp — bắt đầu cấp điện cho xưởng.\n"
     "Bóng đèn dầu được thay bằng bóng đèn điện. Cả xưởng sáng trưng.\n"
     "Chị Sáu nói: \"Từ giờ không phải nheo mắt may nữa nhỉ?\"\n"
     "Hùng đứng dưới bóng đèn, nhìn cái bóng của mình đổ dài trên nền xi măng. Một bước nhỏ cho năng lượng, một bước lớn cho năng suất."),
82: ("Nhiệm vụ năng lượng hoàn thành. Nhà máy điện chạy ổn định.\n"
     "Hùng tính: số giờ sản xuất tăng gấp đôi sau khi có điện.\n"
     "Nhưng ông cũng tính: hóa đơn dầu diesel mỗi tháng là một con số không nhỏ.\n"
     "\"Cần tìm năng lượng khác\", ông ghi vào sổ. Một hướng đi mới đã hình thành."),
83: ("Quỹ từ thiện Thương Gia được thành lập với số vốn ban đầu khiêm tốn.\n"
     "Hùng đích thân chọn người đứng quỹ — một cô giáo về hưu, chưa từng làm doanh nghiệp.\n"
     "\"Em không biết làm từ thiện kiểu công ty,\" cô nói.\n"
     "Hùng đáp: \"Thì làm kiểu nhà. Thấy ai khó thì giúp. Chỉ cần ghi sổ rõ ràng.\""),
85: ("Mười đối tác xuất khẩu đầu tiên. Hùng ký từng hợp đồng bằng tay.\n"
     "Có đối tác từ Ba Lan, Tiệp, Nhật, Pháp. Mỗi hợp đồng một ngôn ngữ, một cách thanh toán, một chuẩn hàng khác nhau.\n"
     "Lan lo: \"Sao mình làm nổi?\"\n"
     "Hùng chỉ vào đội ngũ: Minh lo kỹ thuật, chị Sáu lo chất lượng, Lan lo kế toán. \"Mỗi người một việc. Tôi lo ký.\""),
86: ("Bảo hiểm Thương Gia ra đời. Sản phẩm đầu tiên: bảo hiểm thân thể cho công nhân.\n"
     "Chị Sáu hỏi: \"Có bắt buộc không?\"\n"
     "Hùng lắc: \"Không bắt buộc. Nhưng tôi mua cho tất cả. Công ty trả tiền.\"\n"
     "Mấy chục công nhân nghe vậy, không ai nói gì. Nhưng hôm sau, không ai đi trễ giờ."),
87: ("Máy cày ra mắt — không phải ở hội chợ, mà ở giữa đồng. Hàng trăm nông dân kéo đến xem.\n"
     "Minh lái máy, chạy ba vòng. Đất cày sâu, đều, gọn.\n"
     "Một ông nông dân già lại gần, sờ tay vào lưỡi cày, ngước lên nhìn Hùng: \"Bao nhiêu một cái?\"\n"
     "Hùng nói giá. Ông già gật đầu: \"Tiết kiệm được hai con trâu.\""),
88: ("Máy gặt ra mắt. Mùa gặt năm ấy, Thương Gia đưa máy ra đồng phục vụ miễn phí tuần đầu.\n"
     "Mấy chục héc-ta lúa được gặt trong ba ngày. Thay vì ba tuần bằng tay.\n"
     "Minh đứng trên máy suốt ba ngày, mặt đen giòn vì nắng, nhưng cười suốt.\n"
     "Hùng mang cơm ra đồng cho Minh. Anh kỹ sư trẻ ngồi trên máy ăn, mắt vẫn dõi theo lưỡi cắt."),
90: ("Phần 3 bắt đầu. Hùng viết tiêu đề lên trang mới: \"1986-1988 — Vươn ra biên giới.\"\n"
     "Bốn người ngồi quanh bàn: Hùng, Lan, Minh, Hạnh.\n"
     "Bốn cốc nước chè, một tờ giấy A4, ba mục tiêu lớn.\n"
     "Hùng nói: \"Chúng ta sẽ làm lại từ đầu. Nhưng lần này có nhau.\""),
91: ("Lò thép Hải Phòng rực lửa. Hùng đứng trước lò nung, cảm nhận sức nóng hầm hập.\n"
     "Minh đứng bên cạnh, giải thích về hàm lượng carbon, về nhiệt độ luyện, về độ tinh khiết của thép.\n"
     "Hùng nghe không hết, nhưng ông hiểu: thép của Việt Nam không thua Thái Lan nếu mình đầu tư đúng.\n"
     "Ông gật với Minh: \"Cứ làm. Có lỗ tôi chịu.\""),
92: ("Xi măng Thương Gia — lò nung thứ hai đi vào hoạt động. Công suất 78%.\n"
     "Đội ngũ kỹ sư địa phương vận hành. Không còn chuyên gia nước ngoài.\n"
     "Hùng đi tham quan dây chuyền, thấy công nhân Việt Nam đang kiểm tra chất lượng từng bao.\n"
     "Ông bốc một nắm xi măng, bóp thử. Bột mịn, trắng, không vón.\"Chuẩn rồi.\""),
93: ("Hùng gặp cô Hạnh — không phải ở văn phòng, mà ở quán cà phê vỉa hè.\n"
     "Cô Hạnh mang theo một tập hồ sơ về quy trình kiểm toán nội bộ.\n"
     "Hùng chưa đọc hết đã nói: \"Em làm được.\"\n"
     "Cô Hạnh ngạc nhiên: \"Anh chưa xem kỹ mà.\"\n"
     "Hùng cười: \"Nhìn mắt em biết thừa.\""),
94: ("Hùng gặp cô Mai và cô Lan — hai chị em cùng là kế toán trưởng ở hai công ty khác nhau.\n"
     "Cô Mai nói nhiều, cô Lan nói ít. Hùng chọn người nói ít.\n"
     "\"Vì sao?\" Lan (em gái Hùng) hỏi sau đó.\n"
     "Hùng trả lời: \"Người nói ít thường giữ được bí mật. Làm tài chính cần người giữ được bí mật.\"\n"
     "Lan suy nghĩ, gật đầu."),
95: ("Hùng chọn cô Hạnh. Không phải vì hồ sơ đẹp hơn, mà vì cô Hạnh là người duy nhất nói thẳng: \"Lương em thế này thì em không làm được.\"\n"
     "\"Em dám nói thật, em dám làm thật,\" Hùng nói với Lan.\n"
     "Lan nhìn anh, cười: \"Em tưởng anh chọn người dễ bảo.\"\n"
     "\"Anh không cần người dễ bảo. Anh cần người dám bảo anh sai.\""),
97: ("Dây chuyền điện tử đầu tiên chạy thử. Những bo mạch đơn giản cho thiết bị gia dụng.\n"
     "Minh đứng trước dây chuyền, tay cầm bo mạch vừa ra lò, soi dưới đèn.\n"
     "\"Tỉ lệ đạt 92%,\" Minh nói. \"Còn 8% kia là lỗi hàn tay.\"\n"
     "Hùng nhìn bo mạch. Những đường mạch đồng mảnh như sợi tóc. \"92% là tốt. Tháng sau nâng lên 95%.\""),
98: ("Chiếc điện thoại đầu tiên mang nhãn Thương Gia được xuất xưởng. Kiểu dáng đơn giản, đen, nặng tay.\n"
     "Hùng nhấc ống nghe, quay số thử. Tiếng chuông reo đầu dây bên kia.\n"
     "\"A lô?\" Giọng Lan từ phòng bên cạnh.\n"
     "Hùng cười. Cuộc gọi đầu tiên trên sản phẩm của mình."),
99: ("Viễn thông Thương Gia phủ sóng ba tỉnh. Hệ thống tổng đài nhỏ do Minh thiết kế.\n"
     "Hùng gọi điện cho chi nhánh Hà Nam — lần đầu tiên không cần nhờ bưu điện.\n"
     "Đầu dây bên kia, giọng Tư Hạnh nghe rõ mồn một: \"Anh Hùng hả? Nghe rõ quá!\"\n"
     "Hùng không nói gì nhiều. Ông chỉ cúp máy và gạch một dòng trong sổ: viễn thông — OK."),
100: ("Phần mềm đầu tiên — HT-QL1 — chạy trên máy IBM PC XT 286.\n"
      "Minh và đội ngũ lập trình viên đứng quanh màn hình xanh. Dòng lệnh cuộn lên.\n"
      "\"Nghiệp vụ kế toán — nhập dữ liệu — thành công,\" thằng nhỏ lập trình viên nói.\n"
      "Hùng nhìn màn hình, nhớ lại kiếp Lý Minh code đêm này qua đêm khác. \"Giỏi lắm. Nhưng còn bug.\" \"Dạ?\" \"Lỗi ấy. Sẽ có lỗi. Sửa đi.\""),
101: ("108 cửa hàng trên toàn quốc. Con số Hùng không mơ tới ba năm trước.\n"
      "Lan nói: \"Em không ngờ mình có ngày này.\"\n"
      "Hùng đóng sổ: \"Còn 108 tỉnh thành nữa.\"\n"
      "Lan cười: \"Việt Nam chỉ có 63 tỉnh.\" Hùng nhìn ra cửa sổ: \"Thì ra nước ngoài.\""),
102: ("Nhà hàng 42 — chuỗi nhà hàng đầu tiên của Thương Gia — mở cửa tại Hà Nội.\n"
      "Hùng không đặt tên Thương Gia. Ông đặt tên \"Bếp Xưa\".\n"
      "Lan hỏi: \"Sao lại đặt tên đó?\"\n"
      "Hùng trả lời: \"Để người ta nhớ những món ngày xưa mình từng ăn với bà.\"\n"
      "Bà Hà nghe vậy, quay mặt đi. Nhưng Hùng thấy bà quệt nhẹ khóe mắt."),
104: ("Container đầu tiên xuất khẩu đi châu Âu — Ba Lan, 47.500 USD.\n"
      "Hùng đứng ở cảng Hải Phòng nhìn container được cần cẩu nâng lên, đặt xuống tàu.\n"
      "Một chặng đường dài từ cuộn vải bán rong đến container xuất khẩu.\n"
      "Ông nói với Minh: \"Mai mốt ta sẽ đóng cả tàu.\" Minh tưởng ông nói đùa."),
105: ("Tổng kết Phần 3. Hùng đóng cuốn sổ dày nhất từ trước đến nay.\n"
      "108 cửa hàng, 30 nhà máy, 3 nhà hàng, dây chuyền thép, xi măng, điện tử, phần mềm, container châu Âu.\n"
      "Lan đọc báo cáo tổng kết, giọng bình thản như đọc thực đơn.\n"
      "Hùng ngồi nghe, không ngắt. Cuối cùng ông nói: \"Làm tốt lắm.\" Hai tiếng — ông hiếm khi nói với ai."),
106: ("Phần 4 bắt đầu. Hùng viết lên trang mới: \"Ra thế giới.\"\n"
      "Đà Nẵng, Jakarta, Bangkok. Những cái tên lạ, những thị trường chưa biết.\n"
      "Lan hỏi: \"Có sợ không?\"\n"
      "Hùng nhìn ra cảng Đà Nẵng, nơi những con tàu đang dần khuất ở đường chân trời. \"Sợ. Nhưng không làm thì còn sợ hơn.\""),
108: ("Jakarta. Nhà máy Indonesia bắt đầu sản xuất. Hùng đứng dưới nắng nhiệt đới, nhìn dây chuyền chạy.\n"
      "Công nhân Indonesia mặc đồng phục Thương Gia, tay thoăn thoắt.\n"
      "Một người quản lý địa phương hỏi: \"Ông có muốn nói gì với công nhân không?\"\n"
      "Hùng lắc đầu. \"Họ làm tốt rồi. Tôi chỉ đứng xem.\" Ông biết, khi mình đứng xem được, là lúc hệ thống đã vận hành."),
110: ("Bangkok Electronics trở thành công ty con đầu tiên của Thương Gia ở nước ngoài.\n"
      "Hùng ký hợp đồng mua lại — tay hơi run, nhưng chữ ký vẫn thẳng.\n"
      "Ông Somchai bắt tay ông: \"Người Việt Nam làm ăn tử tế.\"\n"
      "Hùng không đáp. Nhưng ông giữ chặt cái bắt tay ấy. Sau này, mối quan hệ đó mở ra cả khu vực Đông Nam Á."),
118: ("Những ngày nằm viện. Hùng nhìn trần nhà trắng, nghe tiếng kim đồng hồ tích tắc.\n"
      "Lần đầu tiên sau nhiều năm, ông không nghĩ đến kế hoạch kinh doanh.\n"
      "Ông nghĩ về bà Hà — người đã gần tám mươi, vẫn quảy gánh ra chợ mỗi sáng.\n"
      "Về Lan — người em gái chưa một lần than vãn dù gánh việc nặng.\n"
      "Về những người đã theo ông từ những ngày đầu — họ đang đợi ông khỏe lại."),
119: ("Bước ngoặt sức khỏe. Hùng ngồi ở ghế đá bệnh viện, tờ giấy xuất viện trên tay.\n"
      "Bác sĩ dặn: \"Giảm stress, giảm công việc, tập thể dục đều.\"\n"
      "Hùng nghe, gật đầu. Nhưng trong đầu ông đang tính: giao việc gì cho ai, cái gì bỏ bớt.\n"
      "Lan đến đón. Hùng cất tờ giấy vào túi, đứng dậy: \"Về thôi.\" Từ hôm đó, ông không thức quá 10 giờ tối."),
122: ("Myanmar và Campuchia — hai thị trường mới. Hùng đi cùng ông Tam, người từng là bộ đội Trường Sơn.\n"
      "Biên giới Tây Nam, sông nước mênh mông. Hùng nhìn dòng sông, nhớ câu hỏi của bà nội: \"Đi xa thế làm gì?\"\n"
      "Ông không trả lời bà lúc đó. Nhưng bây giờ, đứng ở bến phà Châu Đốc, ông biết câu trả lời: để hàng Việt đến những nơi tàu Việt chưa từng tới.\n"
      "Ông Tam lặng lẽ chèo thuyền, mắt nhìn về phía trước không chớp."),
126: ("\"Giá trị của sự buông\" — bốn chữ Hùng viết trên trang sổ. Ông nhìn lại danh sách việc hàng ngày, gạch bỏ những thứ không cần thiết.\n"
      "Giao cho người khác những việc người khác làm tốt hơn.\n"
      "Buông bớt trách nhiệm không phải là trốn tránh, mà là để người khác lớn lên.\n"
      "Hùng đóng sổ, ra vườn tưới cây. Lần đầu tiên ông thấy cây cam sau nhà đã ra trái."),
143: ("Los Angeles. Hùng ngồi trong phòng làm việc nhỏ, trước mặt là tiêu chuẩn kỹ thuật Mỹ dày hai trăm trang.\n"
      "Anh sinh viên UCLA phiên dịch giúp ông những thuật ngữ khó.\n"
      "Hùng ghi chép cẩn thận, từng dòng.\n"
      "\"Để hàng Việt Nam đứng trên kệ Mỹ, phải hiểu luật chơi của họ,\" ông nói.\n"
      "Anh sinh viên nhìn ông bằng ánh mắt khác. Một doanh nhân Việt chịu ngồi đọc hai trăm trang tiêu chuẩn — chuyện chưa từng thấy."),
144: ("Bản đồ thị trường Mỹ treo trên tường. Hùng đánh dấu các thành phố có đông người Việt.\n"
      "Seattle, San Jose, Houston, Dallas, Florida. Mỗi chấm đỏ là một mục tiêu.\n"
      "Linda — đối tác Mỹ gốc Việt — nói: \"Anh đi xa quá nhỉ?\"\n"
      "Hùng chỉ vào Los Angeles: \"Từ đây, đi đâu cũng được. Chỉ sợ không dám đi.\""),
182: ("Quỹ đầu tư Thương Gia thành lập — vốn điều lệ 200 tỷ đồng. Năm 1993.\n"
      "Luật sư nói: \"Khung pháp lý chưa có.\"\n"
      "Hùng đáp: \"Thì mình làm tiền lệ.\"\n"
      "Văn phòng luật sư soạn thảo hợp đồng suốt ba tuần. Hùng ngồi cùng họ, sửa từng chữ.\n"
      "Khi bộ hồ sơ hoàn tất, Hùng mang lên Ngân hàng Nhà nước, đặt lên bàn cán bộ thẩm định: \"Đây. Anh xem giúp tôi hợp lệ không.\""),
191: ("Căn phòng tập thể cũ cuối phố Huế. Bốn bạn trẻ, hai bo mạch chủ, một ước mơ.\n"
      "Hùng ngồi xuống chiếc ghế nhựa ngả màu, hỏi từng người từng câu — không về công nghệ, mà về lý do họ làm.\n"
      "Người trẻ nhất, mới hai mươi, nói: \"Tụi em không muốn Việt Nam mãi là xưởng gia công cho nước ngoài.\"\n"
      "Hùng gật đầu. Câu đó đủ để ông rót tiền."),
194: ("Morgan Stanley gửi fax. Họ muốn đầu tư vào quỹ Thương Gia.\n"
      "Hùng nhìn tờ giấy còn ấm từ máy fax. Ba triệu USD.\n"
      "Ông ngồi trong phòng khách nhà Hàng Bông suốt ba tiếng, không làm gì, chỉ nghĩ.\n"
      "Sau đó ông gọi Lan: \"Bảo họ đồng ý. Nhưng phải giữ quyền kiểm soát.\" Thế giới đã gõ cửa. Hùng không đóng."),
195: ("Chìa khóa xe máy đặt trên bàn. Lan nhìn chìa khóa, nhìn Hùng.\n"
      "\"Từ mai anh không ra Bắc nữa. Em xử lý toàn bộ mảng Hà Nội.\"\n"
      "Năm 1995, Lan hai mươi bảy tuổi.\n"
      "Cô cầm chìa khóa, không nói gì. Cô đã chạy hàng từ năm 1983, đã đếm từng đồng lời suốt mười hai năm.\n"
      "Hôm đó, cô về nhà muộn. Nhưng sáng hôm sau, cô có mặt ở văn phòng từ 6 giờ sáng."),
250: ("Quỹ R&D thành lập — 200 tỷ cho nghiên cứu và phát triển.\n"
      "Nhiều người trong công ty phản đối: \"Đầu tư vào đất có phải hơn không?\"\n"
      "Hùng lắc đầu: \"Đất có thể mua sau. Máy móc có thể thuê. Nhưng kỹ sư và công nghệ không thể mua gấp.\"\n"
      "Lan được giao đứng quỹ. Cô nói: \"Anh giao em việc khó nhất đấy.\"\n"
      "Hùng cười: \"Biết. Nên mới giao em.\""),
260: ("Cảng Tân Vũ, Hải Phòng. Container đầu tiên xuất khẩu thẳng đi châu Âu, không qua trung gian.\n"
      "Hùng đứng từ sáng sớm, nhìn từng container được xếp lên tàu.\n"
      "Gió biển mặn thổi tung tóc. Ba container giày bảo hộ lao động — 240.000 USD — đi Hamburg.\n"
      "Khi tàu rời cảng, Hùng không vẫy tay. Ông chỉ đứng nhìn cho đến khi con tàu khuất dạng."),
270: ("2008. Cuối năm. Hùng ngồi trong phòng khách, trước mặt là bản tổng kết mười hai năm.\n"
      "Từ xưởng giày nhỏ ở Hà Nội đến tập đoàn có mặt trên năm châu lục.\n"
      "Ông đọc lại từng trang. Có trang ướt — vì nước mắt hay nước mưa, ông không nhớ nữa.\n"
      "\"Tạm được,\" ông nói với chính mình, rồi gấp sổ. Còn nhiều việc phải làm."),
272: ("Tòa soạn báo đầu tiên của Thương Gia. Hùng mua lại một tờ báo nhỏ sắp phá sản.\n"
      "Hội đồng quản trị phản đối. \"Báo chí không phải là đóng giày.\"\n"
      "Hùng nói: \"Nhưng truyền thông là tiếng nói. Thương gia có tiếng nói mới là thương gia thực thụ.\"\n"
      "Sáu tháng sau, tờ báo hòa vốn. Hai năm sau, nó là tờ báo kinh tế có uy tín nhất Hà Nội."),
280: ("Một trăm trường học vùng sâu. Ý tưởng đến từ một bữa tối.\n"
      "Hùng nói với Lan: \"Hồi nhỏ mình không có trường học. Giờ mình xây cho tụi nhỏ.\"\n"
      "Dự án kéo dài ba năm, đi qua ba mươi tỉnh thành từ Hà Giang đến Cà Mau.\n"
      "Khi trường thứ một trăm khánh thành, Hùng không đến dự. Ông ở nhà, nấu bữa cơm cho bà Hà.\""),
306: ("Gặp lại ông Sato. Hai mươi năm kể từ lần đầu gặp ở Tokyo.\n"
      "Ông Sato tóc bạc trắng, đi chậm, nhưng mắt vẫn tinh. Ông đặt một hộp gỗ lên bàn: bộ ấm trà Nhật Bản.\n"
      "\"Tôi già rồi. Hợp đồng này để lại cho học trò của tôi.\"\n"
      "Hùng nhìn ông Sato. Những người già đi, những mối quan hệ ở lại.\n"
      "\"Chúng ta còn làm được nhiều việc nữa,\" Hùng nói. Ông Sato cười, im lặng."),
328: ("Hà Nội, mùa thu 2015. Hùng ký quyết định thành lập Quỹ Từ thiện 10.000 tỷ.\n"
      "Bà Hà — chín mươi hai tuổi — nhìn tờ quyết định, hỏi: \"Nhiều thế làm gì?\"\n"
      "Hùng trả lời: \"Để sau này con cháu không phải nói 'ước gì'.\"\n"
      "Bà Hà gật đầu: \"Đúng. Tao không muốn nghe chúng nó nói ước gì.\""),
344: ("Sài Gòn, tháng Mười 2018. Lễ bàn giao quyền lực.\n"
      "Hùng mặc bộ complet đen, tóc chải gọn, đứng giữa hội trường hai trăm người.\n"
      "Ông đọc quyết định bổ nhiệm thế hệ lãnh đạo mới. Giọng ông không run.\n"
      "Cuối buổi, ông bắt tay từng người. Không ai thấy ông khóc. Nhưng khi về nhà, ông ngồi trong phòng tối một lúc lâu."),
349: ("EuroSynergy — đối tác Pháp — muốn hợp tác với Thương Gia.\n"
      "Ông Pierre Lefèvre ngồi đối diện Hùng trong phòng họp tầng hai mươi.\n"
      "\"Ông có biết vì sao tôi chọn Thương Gia không?\" ông hỏi.\n"
      "Hùng lắc đầu.\"Vì tôi đã gặp hai mươi công ty Việt Nam. Chỉ có ông hỏi tôi: 'Chúng tôi có thể học gì từ các ông?' Chứ không phải 'Các ông mua bao nhiêu?'\""),
352: ("Quỹ Thương Gia Vì Cộng Đồng — 100.000 tỷ. Hùng đặt bút ký.\n"
      "Đây là số tiền lớn nhất ông từng ký giải ngân trong đời.\n"
      "Bà Hà, chín mươi chín tuổi, ngồi đối diện, đeo kính đọc từng dòng.\n"
      "Bà ký xong, đặt bút xuống, nói: \"Có thể tao không còn sống để thấy nó. Nhưng mày nhớ: đừng để ai chết vì thiếu tiền mua thuốc.\""),
356: ("Hoàng hôn tháng Chạp. Hà Nội rét mười độ. Hùng về nhà cũ Quốc Oai.\n"
      "Bà Hà nhất quyết không rời căn bếp cũ. Hùng không ép.\n"
      "Tối đó, bà nấu canh chua, kho cá. Hùng ăn hết ba bát cơm.\n"
      "Bà nhìn ông, cười: \"Vẫn ăn khỏe thế là còn làm được.\"\n"
      "Hùng không nói gì. Nhưng trong lòng ông, bốn mươi năm trôi qua như một ngày."),
}

# Also track which scenes we've used for the remaining chapters not in SCENES dict
# These need auto-generated unique scenes
AUTO_SCENES = {
55: ("Hùng gấp tờ trình bày lại. Cuộc họp với cán bộ huyện kết thúc.\n"
     "Trong tay ông là tờ giấy phép thí điểm có dấu đỏ.\n"
     "Một bước đi mới cho Thương Gia: tự chủ, có kiểm chứng.\n"
     "Trên đường về, ông dừng xe ở đầu làng, nhìn cánh đồng lúa đang vào vụ."),
56: ("Chín mươi ngày thử việc kết thúc. Minh đặt bộ hồ sơ lên bàn Hùng.\n"
     "Hùng nhìn từng trang, không nói. Cuối cùng, ông đứng dậy, bắt tay Minh.\n"
     "\"Ngày mai em bắt đầu lương chính thức.\"\n"
     "Minh cười — lần đầu tiên Hùng thấy anh cười."),
58: ("Tấm biển \"Thương Gia — Thương hiệu Việt\" được treo lên mặt tiền.\n"
     "Chữ sơn đen trên nền gỗ, do chính tay Hùng viết.\n"
     "Lan đứng dưới đường nhìn lên: \"Vậy là mình có tên hả anh?\"\n"
     "Hùng không trả lời, chỉ siết con ốc cuối cùng thật chặt."),
59: ("Chi nhánh Ninh Bình mở cửa. Hùng giao cho anh Đức.\n"
     "Buổi tối trước khai trương, Hùng ở lại giúp kê kệ.\n"
     "Trên đường về, trời mưa, đường đất trơn, xe đạp lầy bánh.\n"
     "Nhưng trong lòng nhẹ. Chi nhánh thứ ba. Thêm một nhịp."),
60: ("Hoàn thành nhiệm vụ chi nhánh. Các chi nhánh đều có lãi sau tháng đầu.\n"
     "Lan hỏi: \"Có nên mở thêm không?\"\n"
     "Hùng lật sổ, nhìn danh sách các tỉnh còn trống. Ông khoanh tròn ba cái tên.\n"
     "\"Mở. Nhưng từ từ.\""),
61: ("Mười chiếc xe đạp đầu tiên ra xưởng. Hùng đạp thử một vòng quanh sân.\n"
     "Minh đứng bên, ghi chú vào sổ tay: điều chỉnh góc cổ lái.\n"
     "Mười chiếc xe lăn bánh trên đường đất là mười lần chữ tín đặt xuống.\n"
     "\"Ra đường được rồi,\" ông nói."),
62: ("Chiếc máy cày hai bánh nổ máy giữa thửa ruộng.\n"
     "Mấy ông nông dân đứng xem, tay che nắng, mắt dõi theo.\n"
     "Khi lưỡi cày lật đất, ai đó xuýt xoa: \"Chạy thật kìa.\"\n"
     "Hùng không nói, nhưng tay ông nắm chặt. Chiếc máy đầu tiên đã chạy."),
63: ("Hai máy gặt mẫu chạy thử trên đồng. Lúa cắt gọn, xếp thành hàng.\n"
     "Minh nâng kính bảo hộ lau mồ hôi, cười tươi.\n"
     "Hùng đứng ngoài bờ, bẻ bông lúa, vo hạt, bỏ vào miệng nhai.\n"
     "Hạt dẻo. Mùa này sẽ không còn cảnh gặt tay dưới nắng tháng Năm."),
64: ("Ba mươi xe tải đỗ thành hàng dài. Đủ loại, đủ đời.\n"
     "Hùng đi dọc dãy xe, tay gõ thử lốp, hỏi tài xế từng chiếc.\n"
     "Một anh lái hỏi: \"Cả trăm chiếc làm gì cho hết?\"\n"
     "Hùng tính: mỗi tỉnh hai chiếc, mỗi chi nhánh một chiếc, còn lại chở hàng xuất."),
65: ("Chi nhánh tài chính mở cửa. Biển hiệu nhỏ, nhưng thu hút chú ý.\n"
     "Hùng nhìn tờ giấy phép kinh doanh thứ tư.\n"
     "Từ bán vải đến cho vay — không tính trước, chỉ đáp ứng nhu cầu.\n"
     "Hệ thống ghi nhận thêm một kỹ năng."),
66: ("Trường Thương Gia khởi công. Hùng cầm cuốc, nhưng đưa cho một em nhỏ.\n"
     "\"Để sau này cháu kể lại: ngày xưa ông nội tao xây trường này.\"\n"
     "Đứa bé đập cuốc xuống đất. Mọi người cười. Hùng không cười, nhưng mắt cay."),
67: ("Sài Gòn. Một khu đất trống góc Bình Thạnh. Hùng đứng giữa cỏ dại.\n"
     "Đối tác hỏi: \"Sao không xây ở quận 1?\"\n"
     "Hùng chỉ bản vẽ: \"Học sinh ở quận 1 đã có trường. Chỗ này thì chưa.\""),
68: ("Trung tâm đào tạo mở lớp đầu tiên. Năm nữ công nhân, ba thợ may, một kế toán trẻ.\n"
     "Chị Sáu dạy cắt may, Minh dạy bảo trì máy, Hùng dạy sổ sách.\n"
     "Không giáo trình. Nhưng cuối buổi, không ai hỏi mấy giờ tan."),
69: ("Phòng khám An Tín mở rộng: thêm hai phòng, thêm một bác sĩ trẻ.\n"
     "Phòng chờ đông hơn trước. Người bệnh mang ghế từ nhà đến.\n"
     "Bác sĩ già nói: \"Đông vì khám không mất tiền mà thuốc tốt.\"\n"
     "Hùng nhìn quanh, thấy một người mẹ bế con, một cụ già chống gậy."),
70: ("Chuyến xe cuối cùng của nhiệm vụ vận chuyển lăn bánh 4 giờ chiều.\n"
     "Hùng đứng ở cổng nhìn theo. Điện thoại reo: \"Hàng tới nơi, nguyên vẹn.\"\n"
     "Ông gạch một dòng: \"NVVC — HOÀN THÀNH.\""),
71: ("Dịch vụ cho vay ra đời từ một cái bàn trong góc xưởng.\n"
     "Người vay đầu tiên: bà Tư bán hàng ngoài chợ, cần vốn xoay vòng.\n"
     "Không tài sản thế chấp, chỉ có hai người làm chứng.\n"
     "Bà Tư nhận tiền, gật đầu, không nói cảm ơn. Ở làng, người ta không cảm ơn bằng lời khi nhận tiền vay."),
72: ("Chi nhánh tài chính thứ hai. Một quầy nhỏ, một nhân viên, một két sắt cũ.\n"
     "Lan nói: \"Có người hỏi vay mua trâu.\"\n"
     "Hùng gật: \"Cho vay. Lãi bằng nửa thị trường.\"\n"
     "Giải thích: \"Trâu mua về cày được, trả được. Lãi cao họ không trả, mất cả vốn.\""),
73: ("Thí điểm cho vay hoàn thành. Tỷ lệ nợ xấu bằng không.\n"
     "Lan mang cà phê vào: \"Có nên mở rộng không?\"\n"
     "Hùng so sánh lợi nhuận cho vay và may mặc.\n"
     "\"Mở rộng. Nhưng không quên gốc: mình là thương gia, không phải chủ nợ.\""),
74: ("Hai trường đầu kỳ cộng hai mươi tám trường mới — ba mươi trường.\n"
     "Mỗi trường đều có nhà vệ sinh, giếng nước, bảng đen.\n"
     "Lan hỏi: \"Có lễ khánh thành không?\"\n"
     "\"Không cần. Trẻ con đi học là được.\""),
75: ("Ba mươi trường học. Mốc không dám nghĩ ba năm trước.\n"
     "Trường cuối — điểm trường vùng cao, mái lá, vách đất, bàn ghế mới.\n"
     "Cô giáo trẻ hỏi: \"Bác có muốn nói gì với các cháu không?\"\n"
     "Hùng nhìn ba mươi đứa trẻ: \"Học đi rồi sau này giúp nước.\""),
78: ("Phòng khám mở rộng thêm ba cơ sở. Tổng: bảy phòng khám.\n"
     "Báo cáo: số bệnh nhân tăng 40%. Số ca chuyển viện kịp thời — 100%.\n"
     "Hùng không cần biết hài lòng bao nhiêu phần trăm. Cần biết họ có được cứu không."),
79: ("Nhiệm vụ phòng khám hoàn thành. Bảy phòng, mười hai bác sĩ, ba mươi y tá.\n"
     "Bà Hà hỏi: \"Xây thêm nữa không?\"\n"
     "\"Để các con cháu trong nhà theo ngành y, rồi tính tiếp.\"\n"
     "Bà Hà gật. Tối đó bà nấu thêm một món."),
80: ("Công ty xây dựng Thương Gia thành lập. Một kỹ sư già, ba thợ nề, năm phụ hồ.\n"
     "Công trình đầu tiên: mở rộng xưởng may.\n"
     "Hùng tự tay trát một mảng tường. Anh thợ nề nhìn, lắc đầu cười."),
81: ("Nhà máy điện nhỏ — máy phát diesel — cấp điện cho xưởng.\n"
     "Bóng đèn dầu thay bằng bóng đèn điện. Cả xưởng sáng trưng.\n"
     "Chị Sáu: \"Từ giờ không phải nheo mắt may nữa nhỉ?\""),
82: ("Nhiệm vụ năng lượng hoàn thành. Sản xuất tăng gấp đôi.\n"
     "Nhưng hóa đơn dầu diesel không nhỏ.\n"
     "Hùng ghi: \"Cần tìm năng lượng khác.\" Hướng đi mới hình thành."),
83: ("Quỹ từ thiện thành lập. Hùng chọn người đứng quỹ — cô giáo về hưu.\n"
     "\"Em không biết làm từ thiện kiểu công ty.\"\n"
     "\"Thì làm kiểu nhà. Thấy ai khó thì giúp. Chỉ cần ghi sổ rõ ràng.\""),
85: ("Mười đối tác xuất khẩu. Hợp đồng từ Ba Lan, Tiệp, Nhật, Pháp.\n"
     "Mỗi hợp đồng một ngôn ngữ, một chuẩn hàng.\n"
     "Lan lo: \"Sao mình làm nổi?\"\n"
     "\"Mỗi người một việc. Minh lo kỹ thuật, chị Sáu lo chất lượng, em lo kế toán.\""),
86: ("Bảo hiểm Thương Gia ra đời. Sản phẩm đầu: bảo hiểm thân thể cho công nhân.\n"
     "Chị Sáu: \"Có bắt buộc không?\"\n"
     "\"Không. Nhưng tôi mua cho tất cả. Công ty trả tiền.\"\n"
     "Hôm sau, không ai đi trễ giờ."),
87: ("Máy cày ra mắt giữa đồng. Hàng trăm nông dân kéo đến xem.\n"
     "Minh lái ba vòng. Đất cày sâu, đều, gọn.\n"
     "Ông già sờ tay lưỡi cày: \"Bao nhiêu một cái?\"\n"
     "Hùng nói giá. \"Tiết kiệm được hai con trâu.\""),
88: ("Máy gặt ra mắt. Phục vụ miễn phí tuần đầu.\n"
     "Mấy chục héc-ta gặt trong ba ngày — thay vì ba tuần.\n"
     "Minh đứng trên máy suốt ba ngày, mặt đen nắng, cười suốt.\n"
     "Hùng mang cơm ra đồng. Minh ngồi trên máy ăn, mắt dõi lưỡi cắt."),
90: ("Phần 3 bắt đầu. Hùng viết: \"1986-1988 — Vươn ra biên giới.\"\n"
     "Bốn: Hùng, Lan, Minh, Hạnh. Bốn cốc nước chè, một tờ A4, ba mục tiêu.\n"
     "\"Chúng ta sẽ làm lại từ đầu. Nhưng lần này có nhau.\""),
91: ("Lò thép Hải Phòng rực lửa. Hùng đứng trước lò nung.\n"
     "Minh giải thích về carbon, nhiệt độ, độ tinh khiết.\n"
     "Hùng nghe không hết, nhưng hiểu: thép Việt không thua Thái.\n"
     "\"Cứ làm. Có lỗ tôi chịu.\""),
92: ("Xi măng Thương Gia — lò thứ hai hoạt động, công suất 78%.\n"
     "Kỹ sư Việt vận hành. Không còn chuyên gia nước ngoài.\n"
     "Hùng bốc một nắm xi măng, bóp thử. Bột mịn, trắng, không vón.\n"
     "\"Chuẩn rồi.\""),
93: ("Hùng gặp cô Hạnh ở quán cà phê vỉa hè.\n"
     "Cô mang hồ sơ kiểm toán nội bộ. Hùng chưa đọc đã nói: \"Em làm được.\"\n"
     "Cô Hạnh: \"Anh chưa xem kỹ.\" Hùng: \"Nhìn mắt em biết thừa.\""),
94: ("Hùng gặp cô Mai và cô Lan. Cô Mai nói nhiều, cô Lan nói ít.\n"
     "Hùng chọn cô Lan. \"Người nói ít thường giữ được bí mật.\" Lan suy nghĩ, gật đầu."),
95: ("Hùng chọn cô Hạnh. Cô là người duy nhất nói thẳng: \"Lương thế này em không làm được.\"\n"
     "\"Anh không cần người dễ bảo. Anh cần người dám bảo anh sai.\""),
97: ("Dây chuyền điện tử chạy thử. Bo mạch đơn giản cho thiết bị gia dụng.\n"
     "Minh soi bo mạch dưới đèn: \"Tỉ lệ đạt 92%.\"\n"
     "Hùng nhìn đường mạch đồng mảnh như sợi tóc. \"Tốt. Tháng sau nâng lên 95%.\""),
98: ("Chiếc điện thoại Thương Gia đầu tiên. Đen, đơn giản, nặng tay.\n"
     "Hùng nhấc ống nghe, quay số. Chuông reo.\n"
     "\"A lô?\" Giọng Lan từ phòng bên. Hùng cười."),
99: ("Viễn thông Thương Gia phủ sóng ba tỉnh.\n"
     "Hùng gọi chi nhánh Hà Nam — lần đầu không qua bưu điện.\n"
     "Tư Hạnh: \"Anh Hùng hả? Nghe rõ quá!\"\n"
     "Ông cúp máy, gạch một dòng: viễn thông — OK."),
100: ("Phần mềm HT-QL1 chạy trên IBM PC XT 286. Màn hình xanh, dòng lệnh cuộn.\n"
      "\"Nghiệp vụ kế toán — thành công.\" Hùng nhớ kiếp Lý Minh code đêm này qua đêm khác.\n"
      "\"Giỏi lắm. Nhưng còn bug. Sửa đi.\""),
101: ("108 cửa hàng trên toàn quốc. Lan: \"Không ngờ mình có ngày này.\"\n"
      "Hùng đóng sổ: \"Còn 108 tỉnh thành nữa.\"\n"
      "Lan: \"Việt Nam có 63 tỉnh.\" Hùng: \"Thì ra nước ngoài.\""),
102: ("Nhà hàng \"Bếp Xưa\" — chuỗi đầu tiên — mở cửa ở Hà Nội.\n"
      "Lan hỏi vì sao đặt tên đó. Hùng: \"Để người ta nhớ món ngày xưa ăn với bà.\"\n"
      "Bà Hà nghe vậy quay mặt đi. Hùng thấy bà quệt khóe mắt."),
104: ("Container đầu tiên đi châu Âu — Ba Lan, 47.500 USD.\n"
      "Hùng đứng cảng Hải Phòng nhìn container lên tàu.\n"
      "Từ cuộn vải bán rong đến container xuất khẩu. Ông nói: \"Mai mốt ta đóng cả tàu.\""),
105: ("Tổng kết Phần 3. Hùng đóng cuốn sổ dày nhất.\n"
      "108 cửa hàng, 30 nhà máy, 3 nhà hàng, thép, xi măng, điện tử, phần mềm, container châu Âu.\n"
      "Lan đọc báo cáo. Hùng nghe, cuối cùng nói: \"Làm tốt lắm.\" Hai tiếng hiếm hoi."),
106: ("Phần 4. Hùng viết: \"Ra thế giới.\" Đà Nẵng, Jakarta, Bangkok.\n"
      "Lan hỏi: \"Có sợ không?\"\n"
      "Hùng nhìn tàu khuất ở đường chân trời. \"Sợ. Nhưng không làm còn sợ hơn.\""),
108: ("Jakarta. Nhà máy Indonesia bắt đầu sản xuất.\n"
      "Công nhân Indonesia mặc đồng phục Thương Gia.\n"
      "Quản lý hỏi: \"Ông có muốn nói gì?\" Hùng lắc. \"Họ làm tốt rồi.\""),
110: ("Bangkok Electronics — công ty con đầu tiên ở nước ngoài.\n"
      "Hùng ký hợp đồng mua lại. Ông Somchai: \"Người Việt làm ăn tử tế.\"\n"
      "Hùng giữ chặt cái bắt tay. Sau này nó mở ra cả khu vực."),
118: ("Những ngày nằm viện. Hùng nhìn trần nhà, nghe kim đồng hồ.\n"
      "Ông nghĩ về bà Hà gần tám mươi vẫn quảy gánh ra chợ.\n"
      "Về Lan chưa một lần than vãn. Về những người đang đợi ông."),
119: ("Bước ngoặt sức khỏe. Bác sĩ dặn giảm stress.\n"
      "Hùng tính: giao việc gì, bỏ cái gì. Lan đến đón.\n"
      "Từ hôm đó, ông không thức quá 10 giờ tối."),
122: ("Myanmar và Campuchia. Hùng đi với ông Tam, cựu binh Trường Sơn.\n"
      "Đứng bến phà Châu Đốc, ông biết: để hàng Việt đến nơi chưa từng tới.\n"
      "Ông Tam chèo thuyền, mắt nhìn phía trước không chớp."),
126: ("\"Giá trị của sự buông\" — bốn chữ Hùng viết trên sổ.\n"
      "Gạch bỏ việc không cần. Giao việc người khác làm tốt hơn.\n"
      "Buông để người khác lớn. Hùng ra vườn, thấy cam đã ra trái."),
143: ("Los Angeles. Tiêu chuẩn kỹ thuật Mỹ dày hai trăm trang.\n"
      "Sinh viên UCLA phiên dịch. Hùng ghi chép cẩn thận.\n"
      "Một doanh nhân Việt ngồi đọc hai trăm trang tiêu chuẩn — chuyện chưa từng thấy."),
144: ("Bản đồ Mỹ trên tường. Chấm đỏ khắp nơi: Seattle, Houston, Dallas, Florida.\n"
      "Linda: \"Anh đi xa quá nhỉ?\" Hùng chỉ Los Angeles: \"Từ đây đi đâu cũng được.\""),
182: ("Quỹ đầu tư 200 tỷ. Năm 1993, khung pháp lý chưa có.\n"
      "Luật sư: \"Khung pháp lý chưa có.\" Hùng: \"Thì mình làm tiền lệ.\"\n"
      "Mang hồ sơ lên Ngân hàng Nhà nước: \"Anh xem giúp tôi hợp lệ không.\""),
191: ("Bốn bạn trẻ, hai bo mạch chủ, một ước mơ. Căn tập thể cuối phố Huế.\n"
      "Người trẻ nhất: \"Tụi em không muốn Việt Nam mãi là xưởng gia công.\"\n"
      "Câu đó đủ để Hùng rót tiền."),
194: ("Morgan Stanley gửi fax. Ba triệu USD.\n"
      "Hùng ngồi ba tiếng, không làm gì, chỉ nghĩ.\n"
      "Gọi Lan: \"Đồng ý. Nhưng giữ quyền kiểm soát.\" Thế giới gõ cửa."),
195: ("Chìa khóa trên bàn. \"Từ mai em xử lý mảng Hà Nội.\"\n"
      "Lan hai mươi bảy. Cầm chìa khóa, không nói.\n"
      "Sáng hôm sau, cô có mặt ở văn phòng từ 6 giờ."),
250: ("Quỹ R&D 200 tỷ. Phản đối: \"Đầu tư đất có phải hơn?\"\n"
      "Hùng: \"Đất mua sau. Máy thuê. Kỹ sư không mua gấp được.\"\n"
      "Lan đứng quỹ: \"Anh giao em việc khó nhất.\" \"Biết. Nên mới giao em.\""),
260: ("Cảng Tân Vũ, Hải Phòng. Container đi Hamburg, 240.000 USD.\n"
      "Hùng đứng từ sáng. Gió biển mặn.\n"
      "Khi tàu rời cảng, ông đứng nhìn đến khi khuất dạng."),
270: ("2008. Tổng kết mười hai năm — từ xưởng giày đến tập đoàn năm châu.\n"
      "Có trang ướt — nước mắt hay nước mưa, không nhớ nữa.\n"
      "\"Tạm được.\" Gấp sổ. Còn nhiều việc."),
272: ("Tòa soạn đầu tiên. Mua lại tờ báo sắp phá sản.\n"
      "HĐQT phản đối. Hùng: \"Truyền thông là tiếng nói. Thương gia có tiếng nói mới thực thụ.\"\n"
      "Sáu tháng hòa vốn. Hai năm sau, là tờ báo kinh tế uy tín nhất Hà Nội."),
280: ("Trăm trường vùng sâu. Ý tưởng từ một bữa tối.\n"
      "\"Hồi nhỏ không có trường. Giờ xây cho tụi nhỏ.\"\n"
      "Trường thứ một trăm khánh thành, Hùng ở nhà nấu cơm cho bà Hà."),
306: ("Gặp lại ông Sato sau hai mươi năm. Tóc bạc, đi chậm, mắt tinh.\n"
      "Ông đặt bộ ấm trà lên bàn: \"Tôi già rồi. Để lại cho học trò.\"\n"
      "\"Chúng ta còn làm được nhiều việc.\" Ông Sato cười, im lặng."),
328: ("Hà Nội, mùa thu 2015. Quỹ từ thiện 10.000 tỷ.\n"
      "Bà Hà chín mươi hai: \"Nhiều thế làm gì?\"\n"
      "\"Để sau này con cháu không phải nói 'ước gì'.\" Bà gật."),
344: ("Lễ bàn giao 2018. Hùng đọc quyết định, giọng không run.\n"
      "Bắt tay từng người. Về nhà, ngồi trong phòng tối một lúc."),
349: ("EuroSynergy. Ông Pierre: \"Sao tôi chọn Thương Gia?\n"
      "Hai mươi công ty Việt, chỉ ông hỏi 'Chúng tôi học gì từ các ông?'\""),
352: ("Quỹ 100.000 tỷ. Bà Hà chín mươi chín đọc từng dòng.\n"
      "Ký xong: \"Đừng để ai chết vì thiếu tiền mua thuốc.\""),
356: ("Hoàng hôn tháng Chạp. Hùng về nhà cũ Quốc Oai.\n"
      "Bà nấu canh chua, kho cá. Hùng ăn ba bát.\n"
      "Bà cười: \"Vẫn ăn khỏe là còn làm được.\"\n"
      "Bốn mươi năm trôi qua như một ngày."),
}

# Merge with auto scenes taking priority for chapters not in SCENES
ALL_SCENES = {**AUTO_SCENES, **SCENES}

# Get all files
files = []
for root, dirs, fnames in os.walk(BASE):
    for f in fnames:
        if f.endswith('.txt'):
            files.append(os.path.join(root, f))

def sort_key(f):
    m = re.search(r'(\d+)', os.path.basename(f))
    return int(m.group(1)) if m else 9999

files_sorted = sorted(files, key=sort_key)

count = 0
errors = []
for fpath in files_sorted:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find the note line
    note_idx = -1
    for i, line in enumerate(lines):
        if 'Ghi chú' in line and 'sổ cái khớp' in line:
            note_idx = i
            break
    
    if note_idx < 0:
        continue
    
    base_name = os.path.basename(fpath)
    m = re.search(r'(\d+)', base_name)
    chap_num = int(m.group(1)) if m else 0
    
    if chap_num not in ALL_SCENES:
        errors.append(f"No scene for chapter {chap_num}")
        continue
    
    scene = ALL_SCENES[chap_num]
    note_line = lines[note_idx]
    
    # Build new content: keep everything before the note, insert scene, blank line, then note line
    before = '\n'.join(lines[:note_idx])
    after = '\n'.join(lines[note_idx:])
    
    # Insert scene between before and note
    new_content = before + '\n' + scene + '\n\n' + note_line
    if note_idx + 1 < len(lines):
        new_content += '\n' + '\n'.join(lines[note_idx+1:])
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    count += 1
    print(f"✓ #{chap_num} {base_name}")

print(f"\n===== RESULTS =====")
print(f"Patched: {count}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")

# Verify no repeats
print("\n--- Verifying uniqueness ---")
all_scenes_text = {}
repeat_found = False
for fpath in files_sorted:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'sổ cái khớp' not in content:
        continue
    base_name = os.path.basename(fpath)
    m = re.search(r'(\d+)', base_name)
    chap_num = int(m.group(1)) if m else 0
    
    # Extract scene
    lines = content.split('\n')
    note_idx = -1
    for i, line in enumerate(lines):
        if 'Ghi chú' in line and 'sổ cái khớp' in line:
            note_idx = i
            break
    
    # Back up to find scene start
    scene_start = note_idx - 1
    while scene_start >= 0 and lines[scene_start].strip() != '':
        scene_start -= 1
    # scene_start is now at blank line before scene
    
    scene_text = '\n'.join(lines[scene_start+1:note_idx]).strip()
    
    if scene_text in all_scenes_text:
        print(f"REPEAT: #{chap_num} same as #{all_scenes_text[scene_text]}")
        repeat_found = True
    all_scenes_text[scene_text] = chap_num

if not repeat_found:
    print("ALL 103 SCENES ARE UNIQUE ✓")
