#!/usr/bin/env python3
"""
Replace all "Ghi chú: ... system_ledger" lines with unique closing scenes.
Reads each file, finds the system header block, replaces the Ghi chú line.
103 chapters. All scenes are 3-8 lines, unique per chapter.
"""
import os, re, subprocess

BASE = "C:/Dev/MythLab/Niên Đại Thương Gia"

# ─── ALL 103 UNIQUE SCENES ───
# Keyed by filename, value = replacement text (3-8 lines, no trailing newline)
S = {}

S["Chương 1 - Tỉnh lại.txt"] = """Hùng tắt đèn dầu, nằm xuống giường gỗ. Bóng tối làng quê năm 1983 dày đặc. Ông đưa tay sờ ngực — tim đập chậm, đều. Không còn cơn đau thắt, không còn tiếng bíp monitor.

\"Kiếp này, mình sống chậm lại. Sống có người thương.\"

Ông nhắm mắt. Hệ thống im lặng, chờ ngày mai."""

S["Chương 100 - Sản xuất phần mềm.txt"] = """Hùng nhìn ba đĩa mềm trên bàn — 360KB mỗi cái, chứa phần mềm quản lý HT-QL1 cho bốn xí nghiệp. Bà Hà bưng chén nước chè: 'Còn ấm.'

Hùng uống. Chè đắng, ngọt sau cùng. Một thời đại mới vừa mở ra trong căn phòng nhỏ này. Ông viết vào sổ: 'Hôm nay, một xí nghiệp ở Hà Nội không cần gõ tay ba lần một số — vì cái phần mềm mình viết.'"""

S["Chương 101 - Mở rộng cửa hàng 108.txt"] = """108 cửa hàng. Con số trên bìa sổ mới màu đỏ. Hùng đặt cuốn sổ cũ bìa xanh bạc góc lên kệ — hơn hai trăm trang viết tay về mặt bằng, hoa hồng, hợp đồng.

Sổ mới trang đầu còn trắng. Gió mùa đông bắc tràn về. 1988 sẽ khắc nghiệt hơn — và đầy hứa hẹn hơn."""

S["Chương 102 - Mở rộng nhà hàng 42.txt"] = """42 nhà hàng. Hùng đứng dưới cột đèn vàng vọt. Ba mươi tư tuổi, ba hợp đồng thuê nhà, ba bảng lương, ba mươi hai con người.

'Nếu hỏng, ai chịu?' — 'Tên trên sổ. Tên tôi.' Nhưng sổ bây giờ đã dày hơn. Ông bước tiếp, về nhà, nơi bà Hà chờ với mâm cơm đủ để người đi làm còn muốn về."""

S["Chương 104 - Mở rộng xuất khẩu châu Âu.txt"] = """Container màu xanh lắc lư trên biển, hướng Gdansk, mang mây tre, sơn mài, gốm — và gan ruột những người làm ra nó.

Sổ bìa xanh về chứng từ xuất khẩu còn nhiều trang trắng. Nhưng trang đầu đã viết xong. Hùng gấp sổ, mặc áo khoác. Sáng sương mù Hải Phòng, ông ra khỏi nhà."""

S["Chương 105 - Tổng kết Phần 3.txt"] = """Phần 3 đóng lại bằng bút chì. 17.125 EXP. 108 cửa hàng. 30 nhà máy. 700 lao động. Bài học xương máu: không bao giờ tin con số trước khi kiểm tra bằng chứng.

Phần thưởng thật sự — khi cửa còn mở, hàng còn đúng, lương còn trả, và nhà còn muốn ông về. Hùng gấp sổ, đặt dưới gối, nghe tiếng thở đều của đứa cháu nội."""

S["Chương 106 - Bắt đầu Phần 4.txt"] = """Part 4 bắt đầu bằng một chuyến tàu, một cuộc gặp, một danh thiếp giấy cứng. Lá thư mẫu trên bàn viết địa chỉ Moskva bằng tiếng Việt.

'Có thể trật. Nhưng nếu không gửi thì đã trật chắc.' Hệ thống nháy 'ghi nhận.' Ông nhìn ra cửa. Bóng tối sân nhà hòa vào bóng tối phố. Không đếm ngược. Chỉ có bước tới."""

S["Chương 108 - Mở nhà máy Indonesia.txt"] = """'Nhà máy Indonesia — ngày 1 — còn nguyên rủi ro — nhưng đã mở được cửa.' Hùng ghi vào cuối sổ, tắt đèn.

Mưa Jakarta rơi trên mái tôn. Năm 1987, Hùng không sợ mất của nữa. Thứ duy nhất ông sợ là mất người — mất lòng tin, mất chỗ dựa, mất phương hướng."""

S["Chương 11 - Đi Hà Nam.txt"] = """Tối cuối tuần, Hùng lau xe đạp, kiểm vành, bơm hơi. Việc nhỏ trước việc xa. Tất cả xếp thành hàng: giữ vải Hà Nam hai tháng, rồi mới mở thêm.

Lan ghi lịch ba ngày. Hùng dặn nếu mưa to thì lùi, nhờ xe thồ quen nhắn. Trời Thanh Xuân tối, chỉ sao và tiếng ếch. Mắt xích phía nam còn nhỏ, nhưng đã có tên, có số, có ngày, có người chịu."""

S["Chương 110 - M&A Bangkok Electronics.txt"] = """Trên máy bay về, Hùng nhìn vịnh Thái Lan qua ô cửa sổ. Không tự hào, không lo. Thương vụ này chỉ là viên gạch — còn phải xây, phải giữ, phải chịu.

Lan bàn mở văn phòng Singapore quản lý các pháp nhân. Hùng gật. Ông đóng sổ, gối đầu, ngủ một giấc trên máy bay nhưng không quên cài dây an toàn."""

S["Chương 118 - Những ngày nằm viện.txt"] = """Hai bảy tuổi, tim hỏng. Ông nằm nhìn trần phòng bệnh. 'Mày mới hai bảy lo gì' — lời người lính già giường bên. Đầu óc không có con số, không hợp đồng. Chỉ có bát cháo hành bà Hà.

Ông nhắm mắt. Mai bay Singapore. Nếu còn sống, ông xây lại — lần này có người đứng cạnh."""

S["Chương 119 - Bước ngoặt sức khỏe.txt"] = """'Làm lớn cần hy sinh sức khỏe?' — 'Cần biết giới hạn trước khi giới hạn biết mình. Hy sinh không rõ chỉ vô ích — mất người, hỏng việc.'

Đó là lúc Hùng biết mình qua cột mốc quay đầu. Ông không quay. Đi tiếp — chậm hơn, có người đồng hành."""

S["Chương 12 - Đi Hải Dương.txt"] = """Hùng mang mẫu vitamin mới cho ông Tâm. Ông Tâm đọc hạn, gật. Lan đặt ba hộc tiền, đếm phần Hải Dương. Trang này mực phải khô thêm: bà Uyên còn gọi sau tuần thử giá.

Hùng khoanh ngày giao. Sổ hạch toán khép bằng một cái gật đầu. Sang hướng biển, Thái Bình vẫn chờ."""

S["Chương 122 - Myanmar và Campuchia.txt"] = """Đêm cuối 1989, Đà Nẵng mưa nhẹ. Hùng viết: 'Miến Điện: mở. Campuchia: bắc cầu. Một ngày khi hai nước này ổn định, mình sẽ có mặt.'

Ông gấp sổ. Chỉ có tiếng thở của những người đã đi cùng. Mưa rơi đều và dai, như dự cảm một vùng đất hứa."""

S["Chương 126 - Giá trị của sự buông.txt"] = """Sáng mai, trên bàn sẽ có tờ tổng kết của Lan. Phía dưới: 'Cảm ơn.' Hùng đọc rồi bỏ vào ngăn kéo, nơi giữ những thứ đáng giữ nhất.

Buông bớt để Lan gánh — không phải vì hết sức. Vì có những thứ chỉ đẹp khi trao đi."""

S["Chương 13 - Đi Thái Bình.txt"] = """Chiều muộn, Hùng ngồi bóc lạc với bà Hà. Kể chuyện gió mặn, chuyện chị Hường, chuyện người hỏi nguồn lạc.

Tối, ông ghé cổng chị Sáu, gõ ba tiếng. Máy may ngừng sau vách. Cửa hé. Việc ngày mai đã báo trước — đủ để người thợ sắp xếp giấc ngủ."""

S["Chương 14 - Bắt đầu sản xuất.txt"] = """Chị Sáu đặt áo đổi trả lên bàn. Vai kéo khi giơ tay. Họ không sửa riêng rồi thôi — họ hạ vòng nách nửa đốt, may lại bằng vải vụn.

Hùng mang áo đã sửa sang nhà khách. Người đàn ông xoay vai, gật. 'Mất một buổi để lô sau khỏi mất cả chợ.' Lan đánh dấu phom mới."""

S["Chương 143 - Xây dựng hệ thống chất lượng Mỹ.txt"] = """Đức ngạc nhiên khi Hùng nói đến góp vốn ngay lần gặp đầu. Hai bên bắt tay dưới bóng cây bàng — Đức tin người, Hùng tin việc.

Tối, Hùng ngồi quán nước đầu làng. Còn nhiều việc: cửa hàng, tuyến hàng, xưởng nhỏ. Về nhà, bà Hà ngồi may ở hiên. Ông chan nước rau ăn cơm nguội."""

S["Chương 144 - Mở rộng đối tác Mỹ.txt"] = """Đức ngần ngại trước con số. Một nghìn áo sơ mi — lô đầu vào Mỹ. 'Chưa chắc. Nhưng không thử thì chắc không.'

Hùng viết sổ: lô thử 1.000; nhãn tiếng Anh; cổ áo đo theo số trung bình người Mỹ. Làm đúng trước khi làm nhanh."""

S["Chương 15 - Thuê người giúp việc.txt"] = """Chiều cuối tuần, Hùng mang lương đến chị Sáu. Trả đủ, không hẹn miệng. Anh Khanh gửi lời: áo mẫu treo được một cái.

Việc tiếp theo ở mép sổ: gian ông Lân, chỗ máy, lời khách hỏi quần áo. Hùng không mở trang đó đêm nay."""

S["Chương 16 - Mở rộng xưởng may.txt"] = """Hùng trả tiền công, cho từng người tự đối chiếu. Chị Mận thiếu một nẹp, được cộng lại. Sáng chủ nhật, ông tổng kết tháng đầu.

Bảng viết: '58 áo — 4 lỗi — 0 nợ.' Xưởng may đã sống qua tháng đầu."""

S["Chương 17 - Đi Quảng Ninh.txt"] = """'Gửi đúng giờ mà hỏng cũng là hỏng.' Hùng đóng gói từ tối, không bắt lái xe chịu sự luống cuống. Chủ xe càu nhàu nhưng ký nhận.

Ba ngày sau, chị Bé báo QN-1 đủ. Bốn chiếc bán ngay phiên đầu. Cánh cửa biển đã hé."""

S["Chương 18 - Đi Nghệ An.txt"] = """Hạnh đề nghị gom đơn Vinh. Hùng chưa nhận — bà Phương mới bán lô đầu. Ông cân hòm rỗng, tách tiền bao gói.

Một tuần sau, bà Phương bán hơn nửa. Sổ ghi: 'Mở Nghệ An — đã bán, đã thu, đã ghi lỗi cần tránh.'"""

S["Chương 182 - Mở rộng quỹ đầu tư.txt"] = """Dự phòng rủi ro: 47 tỷ. Hùng gạch 'nợ' bằng bút đỏ. Nợ là công cụ — công cụ nào cũng gãy nếu quên nó là công cụ.

Tắt đèn. Tiếng ếch ngoài ruộng. 1993, thành phố vừa cũ vừa mới. Như chính ông."""

S["Chương 19 - Hoàn thành nhiệm vụ sản xuất.txt"] = """Xưởng bó mười áo mới. Lan lấy thẻ, chị Sáu đặt phom, Cu so mép mẫu. Dấu hiệu hoàn thành: việc thường ngày không quay về cũ.

Hùng gói dép hỏng, áo mẫu, sổ nhỏ. Dặn Lan: 'Giữ lịch mười áo huyện. Nghề mới không rút người khỏi việc đang có.'"""

S["Chương 191 - Đầu tư công nghệ cao.txt"] = """Hùng nhớ một câu kiếp trước: 'Phần mềm đang ăn thế giới.' 1994, Việt Nam chưa ai biết. Nhưng Hùng biết. Ông vừa đặt cược — bằng căn phòng tập thể nóng như lò, quạt trần kêu cọt cọt, và bốn thanh niên chưa rời đất nước.

Ông nhìn trần nhà — tối. Nhưng không cần nhìn."""

S["Chương 193 - Xây dựng thương hiệu toàn cầu.txt"] = """Máy bay rời Paris. Hùng viết: 'Thương hiệu không phải tên in trên hộp. Thương hiệu là tất cả việc đã làm trước khi in.'

Ông gấp sổ, ngả ghế. Mười tiếng nữa, ông ở Hà Đông. Một tháng nữa, lô hàng nhãn mới lên tàu."""

S["Chương 194 - Mở rộng quỹ đầu tư Bắc Mỹ.txt"] = """52 tỷ dự phòng rủi ro — tấm đệm cho sai lầm. Mở rộng càng nhanh, sai càng dễ.

Ông tắt đèn. 3 triệu USD, 18 tỷ, 52 tỷ, văn phòng New York. Quỹ Bắc Mỹ đã mở. Cửa đã hé."""

S["Chương 195 - Lan chèo lái Thương Gia.txt"] = """'Tuần sau anh đi Hồng Kông. Em ở nhà, lo hải quan.' Lan nhìn anh khuất sau cánh cửa. Cô hiểu: lần này không chỉ làm ăn — là danh dự Thương Gia.

Cô phải giữ pháo đài."""

S["Chương 2 - Bữa tối đầu tiên.txt"] = """Bữa sáng cơm nguội chan nước thịt kho. Lan gắp trứng cuối sang bát bà. 'Đừng biến bữa ăn thành cuộc giành phần nhường.'

Trước ngủ, Hùng kiểm then bếp, dời trứng xa bếp nóng. Lan nhìn, nghi ngờ chưa mất nhưng bớt sắc. Chuyến huyện thành giờ là việc phải làm thật."""

S["Chương 21 - Mở rộng làm giày.txt"] = """Sau G-2, xưởng có hai bàn ráp, hai người ký trách nhiệm. Hùng cất mẫu cao su miền Nam vào bìa sổ.

Ngoài sân, Hòa khóa hộp dụng cụ thứ hai. Mở rộng không ở lời hứa mua nhiều — ở chỗ anh rời xưởng được mà chuẩn giày vẫn giữ ở nhà."""

S["Chương 22 - Đi Thành phố Hồ Chí Minh.txt"] = """Tối, Hùng kể chuyến đi: bà Sáu xoay rập, Bảy Nghiêm tranh da ẩm, kiện lệch cân. Anh mua lô đủ nhỏ để chịu được sai.

Sau cơm, Lan đặt sổ nghiệm thu cạnh sổ chi phí. Chuyến đi kết thúc khi nguồn hàng kiểm được, chi phí tính được, ngày mai có giới hạn."""

S["Chương 23 - Sản xuất túi xách.txt"] = """320 túi trên giá. Đơn Hà Nội kín hai trang. Hùng không ký nhận toàn bộ — đối chiếu vải, khóa, sức người.

Tháng sáu 1984 tới sát cửa. Việc tiếp: mở rộng mà lỗi không tăng nhanh hơn sản lượng."""

S["Chương 24 - Mở rộng làm túi.txt"] = """Những đề nghị trong họp — rổ riêng màu, bó mười chiếc, khay năm mươi khóa — chỉ làm căn phòng bớt rối. Nhưng cuối tháng, chúng giúp người lạ vào vẫn biết hàng ở đâu.

Lan treo tờ giấy bên túi lỗi: 'Không che — không đoán — không giao khi chưa kiểm.'"""

S["Chương 25 - Mở cửa hàng thứ hai.txt"] = """'Đủ sống bằng chân nó. Nhưng chưa đủ khỏe nuôi thêm.' — 'Đừng đẻ vội. Nuôi hai đứa cho tử tế đã.' Cả nhà cười.

Hùng viết: 'Tìm quyền sử dụng đất dựng xưởng — không đụng quỹ lương, không mua giấy tay.'"""

S["Chương 250 - Lan dẫn quỹ R&D.txt"] = """'Ngày xưa con chỉ bán hàng, mua rẻ bán đắt. Bây giờ con đầu tư cho công nghệ.' Bà Hà nắm tay Lan: 'Ai ngờ con làm lớn thế.'

Lan cười. Thương Gia không chỉ là buôn bán nữa. Nó đang tạo ra tương lai."""

S["Chương 26 - Mua đất xây xưởng.txt"] = """1.200 mét vuông — biên bản giao đất đã ký. Hùng về nhà, bà Hà dọn cơm muộn.

'Đất có tên chưa?' — 'Có. Nhà chưa xong.' — 'Thì ăn đã. Mai xây.' Câu nói nhẹ như muỗi, đủ để Hùng ăn hết bát."""

S["Chương 260 - Chuỗi giá trị toàn cầu.txt"] = """Tài liệu ESG vẫn mở trên bàn. Ông viết dòng cuối: '2008 — kết thúc năm đầu trong chuỗi giá trị toàn cầu. Còn rất xa.'

Ông đứng dậy, bước ra ngoài. Trong bóng tối, container mang logo Thương Gia băng qua Đại Tây Dương."""

S["Chương 27 - Đi Lào.txt"] = """Đơn thử 120 giày, 80 túi — giao hai đợt qua đầu mối ngoại thương. Hùng đọc lại từng điều khoản thanh toán.

Bà Hà dọn cơm. Ông kể một điều làm được, một điều còn hỏng. Lan giữ sổ cạnh mâm. Chuyến Lào đầu — chỉ một cái bắt tay, một tờ phiếu, một chuyến hàng qua Cầu Treo."""

S["Chương 270 - Hoàn thành Phần 4 – Siêu tập đoàn.txt"] = """'Em sẽ làm cho họ không thể nghĩ thế.' Lan ngồi thẳng. 'Được. Em nhận.'

Hùng không vỗ tay. Ông đặt sổ Phần 4 lên kệ, bên cạnh ba phần trước. Hành trình mới bắt đầu — không cho ông, cho người ông đã đào tạo. Lan sẽ viết Phần 5."""

S["Chương 272 - Đế chế truyền thông Thương Gia.txt"] = """Thương Gia Times có tòa soạn mới: mười hai phóng viên, phòng dựng phim, nhóm kỹ thuật web. Hùng đứng bên cửa sổ, gió biển Hải Phòng thổi qua.

'Đế chế?' — không. Một hạt giống. Nhưng hạt giống ấy đã có tiếng nói: độc lập, gần người lao động, đủ kiên nhẫn xây lòng tin từng bài."""

S["Chương 28 - Đi Campuchia.txt"] = """Thỏa thuận thử 60 túi vải — thanh toán qua đơn vị ngoại thương, giao sau đơn Lào.

Bà Hà dọn cơm. Hùng kể điều làm được, điều còn hỏng. Lan giữ sổ cạnh mâm, không mang con số vào bát đũa."""

S["Chương 280 - Xây 100 trường vùng sâu.txt"] = """'Em lập ngân sách ba năm cho từng trường. Quỹ chịu thư viện, nước sạch, học bổng — địa phương chịu giáo viên. Từng bên ký rõ.'

Hùng nhìn sáu vòng tròn chì trên bản đồ. 'Vậy mới gọi là xây trường.'"""

S["Chương 29 - Đi Thái Lan.txt"] = """Đơn thử 100 túi theo lịch tàu, kèm tiêu chuẩn kéo quai, ẩm, phai màu — có phạt hợp đồng.

Bà Hà dọn cơm muộn. Lan viết lịch giao. Một nước mới, một thử thách mới. Cùng một quy tắc: hàng phải qua kiểm."""

S["Chương 3 - Đi huyện thành.txt"] = """Lan mở vở cũ, ghi ngày, số bộ, tiền thu, tiền chi. Hùng không ghi điểm thưởng — biến động hệ thống để cuối chương xác nhận, cuốn vở này chỉ giữ thứ người trong nhà đếm được bằng tay.

Bà Hà giũ nong. Chum gạo kê khỏi nền. Ngày mai ông sẽ trở lại — đúng dãy, đúng số, đúng tiền lẻ."""

S["Chương 30 - Mở rộng cửa hàng.txt"] = """Ba cửa hàng chạy đủ hai chu kỳ kiểm kê. Lệch tiền bằng không, lệch tồn dưới một phần trăm.

Bà Hà dọn cơm. Hùng kể điều làm được, điều còn hỏng. Ba cửa hàng đã có nhịp riêng."""

S["Chương 306 - Gặp lại ông Sato.txt"] = """Trời mưa nhẹ. Hùng ngồi trong phòng, nghe mưa trên mái tôn. Tiếng mưa đưa ông về căn nhà vách đất 1983, nơi mỗi cơn mưa là nỗi lo — dột, ẩm, không chỗ nằm.

Ông viết: 'Hôm nay mưa. Nhớ căn nhà cũ. Nhớ bà Hà nhóm bếp. Nhớ bát cháo loãng. Liệu mình có đủ tử tế để xứng với những gì đã nhận?'"""

S["Chương 31 - Tổng kết năm 1983.txt"] = """Trước khi về, Mai nhét chìa khóa điểm ba vào túi. Chị Sáu ôm phiếu lỗi về xưởng. Hùng tắt đèn. Trên bàn, mục lục hồ sơ 1984 chỉ ba dòng.

Một năm cũ cuối cùng khép bằng con số không mượn của ngày mai."""

S["Chương 32 - Sản xuất thực phẩm.txt"] = """Người đàn ông từ Nam ghé cửa hàng ba, mua hai gói lạc, hỏi hàng chịu được bốn ngày đường không.

Hùng đặt gói lưu ngày thứ bảy cạnh gói đó. Mở rộng đã gõ cửa — hạn bảy ngày, bốn ngày đường trở thành bài toán."""

S["Chương 328 - Quỹ 10.000 tỷ.txt"] = """'Mỗi đồng chi ra phải có người nhận ký tên và địa chỉ. Nếu một ngày tôi không còn, quỹ vẫn chạy.' Hùng ký vào góc tờ giấy Lan soạn.

Cô gấp giấy, bỏ vào sổ bìa xanh — cuốn sổ sẽ mở khi ông không còn ở đây."""

S["Chương 33 - Mở rộng thực phẩm.txt"] = """Mai cất bản sao lịch giao hàng. Chị Sáu nhận phiếu lô giày. Lan khóa sổ muộn nhất.

Tuyến thực phẩm đã xa hơn Hà Đông. Nút thắt không còn là tìm khách — là tìm người biến thử thành lô hàng ổn định."""

S["Chương 344 - Lễ bàn giao quyền lực.txt"] = """Ngày mai, ông không còn là chủ tịch. Ngày mai, ông làm chồng, làm cha, làm con — những vai trò ông từng gác lại.

'Thương Gia giờ của Lan. Còn tôi — của gia đình tôi.' Ông cười. Lần đầu cười mà không nghĩ đến ngày mai."""

S["Chương 349 - Hợp tác với đối tác quốc tế.txt"] = """'Chúng tôi đánh giá cao sự tỉ mỉ. Làm điện tử là làm bằng mắt và tay.' Kyoto Precision Components ký hợp đồng gia công — 500.000 bo mạch, ba triệu euro.

Hùng viết: 'Pháp tin kỹ thuật. Nhật tin con người. Cả hai đều đúng.'"""

S["Chương 352 - Từ thiện 100.000 tỷ.txt"] = """Hùng xoay chiếc vòng lanh trên tay — sợi thô ráp, không mùi, không màu. 'Chiếc vòng này đáng giá hơn 100.000 tỷ. Vì nó không mua được — chỉ có người cho.'

Lan nhìn anh — tóc bạc, vai khòm, nếp nhăn hằn sâu. Cô hiểu: ông xây Thương Gia không để giàu — để trả ơn."""

S["Chương 356 - Bữa tối gia đình.txt"] = """Ông gấp sổ, tắt đèn. Một ngày không chiến lược, không báo cáo. Chỉ có cá kho, canh chua, tiếng cười cháu nội.

Ngày mai là cuối năm. Ông không có kế hoạch gì, ngoài ở nhà, ăn sáng với bà, coi mấy luống rau muống."""

S["Chương 4 - Bán hàng đầu tiên.txt"] = """Về nhà, bà Hà không cầm xấp tiền. Bà nhận chai dầu, gói thuốc, xem hạn, bảo Lan cất hóa đơn. Đồng tiền đầu tiên biến thành thứ bếp thiếu.

Hùng phủi bùn. Lan hong áo. Ngày bán đầu kết thúc bằng hai việc không ai thấy: một món lỗi giữ lại, một khoản nợ từ chối."""

S["Chương 5 - Mở rộng kinh doanh.txt"] = """Đêm, Hùng không vẽ đế chế. Ông ghi ba việc: hỏi Khanh mẫu đơn; giao đúng bộ đã đo; ký vị trí giúp việc.

Từ một sạp thành hai điểm bán — hàng lần đầu đi khỏi tầm mắt mà vẫn có tên người kiểm."""

S["Chương 51 - Mở chi nhánh Bắc Ninh.txt"] = """'Mở cửa xong. Giữ được hay không mới bắt đầu.'

Hùng viết: 'Chi nhánh Bắc Ninh. 24/11/1985. Ba nhân sự. Một kho. Một quầy. Kiểm phiếu cuối ngày. Không có chữ ký, không nhập sổ cái.'"""

S["Chương 52 - Tuyển kỹ sư Minh.txt"] = """Hùng cộng chi phí: lô hàng trả, thử mẫu, công chuyển, lương tháng đầu. Lớn hơn dự tính, nhỏ hơn giá lô hàng bị trả khi mạng lưới phân phối rộng.

Ông nhìn những ô có số, tên, hạn. Tuyển Minh hoàn tất không ở nét bút — khi xưởng làm đúng lúc cả ông và Minh quay lưng."""

S["Chương 53 - Mở phòng khám.txt"] = """Hùng nhìn tấm biển phòng khám An Tín, rồi cuốn sổ hẹn trong tay Vân. 'Cửa mở rồi. Còn phòng khám thì ngày nào cũng phải mở lại cho đúng.'

Đêm ấy, khi sổ tiền trùng số thuốc xuất và hồ sơ hoàn tất, âm thanh quen thuộc vang lên."""

S["Chương 54 - Sản xuất mì ăn liền.txt"] = """'Ý tưởng lớn không qua được một gói hàng lỗi thì chỉ là lời.' Hùng khép sổ. Chi phí thử mì, dầu loại, bao bì hỏng — tất cả ghi vào cột 'học phí.'

Khi dòng cuối khớp, âm thanh quen thuộc vang lên. Ông không nhìn thùng mì như chiến thắng — như một phép thử đã qua."""

S["Chương 55 - Đổi Mới 1986.txt"] = """Hùng đối chiếu phần thưởng hệ thống với sổ cái. Kỳ thí điểm không tạo doanh thu riêng. Các dòng khớp.

Một bảng sáng hiện ra duy nhất — không thêm nhiệm vụ phụ. Đổi Mới 1986, cánh cửa bắt đầu hé mở."""

S["Chương 56 - Minh qua chín mươi ngày thử việc.txt"] = """Hùng đối chiếu sổ chi nhánh với sổ cái Hà Nội. Mười tám nghìn đồng vốn chuẩn bị được tách rõ: tiền mặt, kho, thiết bị. Các dòng khớp.

Âm thanh quen thuộc. Hùng nhìn bảng sáng, rồi nhìn hai tập hồ sơ trên bàn. Chín mươi ngày — đủ để biết một người có làm được việc hay không."""

S["Chương 58 - Xây dựng thương hiệu Thương Gia trong 30 ngày.txt"] = """Một chi nhánh mở cửa thành công khi người bán, người khuân hàng, người giữ sổ và người ở nhà đều không phải hô hoán.

Ba mươi ngày kết thúc. Kết quả thật ở bộ quy chuẩn chung. Đêm nay, cửa Nam Định đã đóng đúng giờ, người làm đã về nhà."""

S["Chương 59 - Mở chi nhánh Ninh Bình.txt"] = """Về nhà, bà Hà vá quai túi cho Lan. Bà hỏi đã ăn chưa. Hùng mở sổ cái sau bữa. Ninh Bình đã có giấy, kho, người, tuyến giao.

Ngày hôm sau không dành cho mở nơi mới. Ba cuốn sổ Thái Bình, Nam Định, Ninh Bình phải về Hà Nội đổi nhịp."""

S["Chương 6 - Tìm đối tác mới.txt"] = """Trên đường về, Hùng ghé xưởng ông Lân đặt quầy gỗ, hai kệ, bốn móc. Tối, Lan trải giấy giữa mâm, đọc lại tên từng người.

Trước ngủ, Hùng ghi ba điều không quên: không lấy lòng tin thay hợp đồng; không lấy lý lịch Tâm che hàng không rõ nguồn; không nhận vốn không hỏi lại gốc."""

S["Chương 60 - Hoàn thành nhiệm vụ chi nhánh.txt"] = """Sau cơm, Hùng ra hiên lật xe đạp kiểm tra. Tay chạm mối hàn khung, xoay bánh sau.

Nó bắt đầu từ làm ra thứ giúp người ta qua cánh cửa. Cuối năm 1985, Hùng sẽ đến xưởng, đặt xe đạp cũ lên bàn, yêu cầu tháo thành từng bộ phận."""

S["Chương 61 - Sản xuất xe đạp.txt"] = """Bà gật như chỉ là ngày buôn bán bình thường. Hùng ghi: lô thử mười xe; ba xe bán; bảy xe tiếp tục.

Dòng chữ hệ thống hiện sau khi con số thực nằm trên giấy."""

S["Chương 62 - Sản xuất máy cày.txt"] = """Lan khép sổ. Hùng không mơ cánh đồng đầy máy. Ông nghĩ đến năm bộ khung, ba động cơ, bốn hộ thử, sổ phụ tùng.

Trước ngủ, hệ thống hiện một lần. Ánh chữ đứng yên, không thêm thưởng ngoài sổ cái đã khóa."""

S["Chương 64 - Mua 30 xe tải.txt"] = """Ba mươi xe — đã có trọng lượng, tuyến đường, người chịu trách nhiệm. Hùng viết: 'Mua đúng không ở lúc ký giá thấp. Mua đúng ở ngày chiếc xe cuối cùng vẫn chở hàng về an toàn.'"""

S["Chương 65 - Mở rộng chi nhánh tài chính.txt"] = """Hùng khép sổ. Chi nhánh mới chưa thắng thị trường, chưa chứng minh được gì ngoài một sổ giao dịch có tên.

Nhưng mọi cơ nghiệp bền vững đều bắt đầu từ những ngày bình thường. Sáng mai, cánh cửa ấy sẽ lại mở."""

S["Chương 66 - Mở rộng trường học.txt"] = """Ngày mai, Lan gửi biên bản cho hội đồng cổ đông. Minh cắm mốc hiện trường. Đội thợ Lâm đào rãnh thoát nước.

Hùng viết: 'Trường mở rộng từ lúc đứa trẻ cuối cùng còn chỗ — người nhường đất không mất bổng lộc.'"""

S["Chương 67 - Mở trường Sài Gòn.txt"] = """Hùng nhìn theo. Góc phố, tiếng rao chiều vang lên. Khu lao động đã thay đổi một chút.

Ông đóng cánh cửa gỗ mới. Hệ thống nháy sáng. Ông không nhìn — đang nghĩ về đứa trẻ ngồi vào bàn và bắt đầu tin nó có thể viết được tên mình."""

S["Chương 68 - Mở trung tâm đào tạo.txt"] = """Hùng gấp thư, cất vào ngăn. Hà Nội mưa phùn. Ông không trả lời ngay.

Nhưng trong lúc xếp sổ cuối năm, ông mở trang kẹp bức thư đầu của ông Năm, ghi thêm một dòng: 'Mở trung tâm dạy nghề. Mua lại niềm tin cho bốn mươi tay không biết cầm bút.'"""

S["Chương 69 - Mở rộng phòng khám.txt"] = """Lan đặt tổng hợp vận chuyển cạnh sổ phòng khám. Hùng khép sổ An Tín. Phòng khám không thành bệnh viện — chỉ có căn nhà gạch một tầng với tủ thuốc và hồ sơ bệnh án.

Âm thanh quen thuộc. Hùng đợi dòng sáng hiện đủ, đối chiếu sổ cái. Không double-book."""

S["Chương 7 - Sửa nhà.txt"] = """Nửa đêm mưa chuyển gió. Hùng thức, cầm đèn dầu. Mép tôn rung, nền hắt vệt nước. Ông kê cao hòm thuốc, chèn giẻ khe cửa.

Sáng, chậu vẫn khô. Bà Hà chống gậy ra hiên: gỗ lành thành thanh thờ, lá lành sang chuồng, tôn lỗi trả hàng, đinh cong gom riêng."""

S["Chương 70 - Hoàn thành nhiệm vụ vận chuyển.txt"] = """Ông rút sổ, viết bốn chữ cuối: 'Người chịu trách nhiệm: Trần Văn Hùng.'

—"""

S["Chương 71 - Mở dịch vụ cho vay.txt"] = """Lan đặt con dấu xuống trang cuối. Hà Nội đang đổi. Hùng đóng hồ sơ: ngày mở, nguồn vốn, người chịu trách nhiệm, giới hạn dừng.

Ông đặt sổ theo dõi kỳ trả đầu lên trên cùng. Dịch vụ đã mở — rủi ro chưa khép."""

S["Chương 72 - Mở rộng chi nhánh tài chính.txt"] = """Lan ký người lập. Hùng ký người chịu trách nhiệm chung. Hai phong bì báo cáo được đóng.

Ngoài phố, tiếng xe thưa dần. Họ khép sổ sau khi kiểm lần cuối. Lan tắt đèn bàn. Cùng mang chìa tủ ra khỏi phòng."""

S["Chương 73 - Hoàn thành nhiệm vụ cho vay.txt"] = """'Ngày mai xem hồ sơ trường. Khoản vay theo lịch của nó — không mang người giữ nợ đi làm việc khác.'

Hùng đưa Lan bản phụ lục. Con dấu cuối cùng khô mực — bảng sáng quen thuộc hiện ra."""

S["Chương 74 - Mở trường học tiếp.txt"] = """Trang tài chính ghi dư nợ 97.000 đồng đã bàn giao. Hai trang nằm cạnh — không lấy số của nhau.

Ông kẻ đường dưới dòng cuối: 'Chương 74. Ba mươi trường. Không double-book.'"""

S["Chương 75 - Mở rộng trường học 30 trường.txt"] = """Ba mươi trường — không phải ba mươi tấm biển. Ba mươi nơi có địa bàn rõ, có người nhận.

Ông khép sổ tại con số ba mươi. Trang kế tiếp vẫn để trắng."""

S["Chương 78 - Mở rộng phòng khám tiếp.txt"] = """'Để bác sĩ Đức đặt — chuyên môn của ông ấy.' Bà Hà gật, tắt đèn.

Bóng tối và tiếng côn trùng mùa hè. Hùng nhắm mắt. Mai lại bắt đầu."""

S["Chương 79 - Hoàn thành nhiệm vụ phòng khám.txt"] = """Ông lật sổ tay, gạch chân dòng cuối: 'Đủ để mở. Chưa đủ để yên.'

Rồi viết thêm: 'Chiều — xem đất bến xe.'"""

S["Chương 8 - Mở rộng hàng hóa.txt"] = """Tối, bà Hà phân loại túi giấy, buộc dây từng gói. Hùng trả bà một đồng tượng trưng. Bà mắng rồi cất vào hộp gỗ.

Hùng chốt ba ngưỡng: thiết yếu nhập đủ hai phiên, hàng mới thử mười đơn vị, thuốc chỉ bán nguyên hộp có nhãn."""

S["Chương 80 - Mở rộng công ty xây dựng.txt"] = """Hùng ừ, gấp sổ. 'Ngày kia anh ghé Khu công nghiệp. Nghe nói bên đó sắp mở.'

Lan ghi dòng dự phòng. Hùng viết: 'Ngày đầu — đội mới đã đứng việc. Máy mới quay. Giấy tờ chờ. Còn một tuần để về.'"""

S["Chương 81 - Mở rộng năng lượng nhà máy điện.txt"] = """Hùng cười — lần đầu trong ngày.

Trước ngủ, ông đọc dòng cuối ghi ở hiên nhà máy: 'Tháng Mười Một, 1986 — nước đổi. Nhiệt điện vẫn đỏ. Nhưng mai có người ra lò.'"""

S["Chương 82 - Hoàn thành nhiệm vụ năng lượng.txt"] = """Hoàn thành hôm nay chỉ là cái mốc. Mai có việc khác. Nhưng tối nay, Hùng cho phép mình nằm mơ.

Ngoài kia, cột điện mới sáng. Trong nhà nhỏ dọc đường dây, trẻ con ngồi dưới bóng đèn học bài. Hùng thở một hơi dài, rồi ngủ thiếp."""

S["Chương 83 - Mở rộng từ thiện quỹ.txt"] = """Đêm khuya. Hùng ra thăm gà, nhìn lên trời sao. Một vì sao sáng lạ thường. Ông không tin điềm báo, nhưng thấy nhẹ lòng."""

S["Chương 85 - Mở rộng xuất khẩu 10 đối tác.txt"] = """Container đầu tiên đã rời cảng. Không pháo hoa, không băng rôn. Chỉ có mười bộ chứng từ trên bàn.

Những container ấy đêm nay đang trên biển — và ngày mai thuộc về người dám ký tên thật."""

S["Chương 86 - Mở rộng bảo hiểm.txt"] = """'Tối về ăn cơm không?' — 'Có. Hẹn bà Hà rồi.'

Hùng mở cửa, nắng tràn vào phòng, rọi lên tập hồ sơ bảo hiểm hàng hóa. Một công việc nữa — một tầng bảo vệ nữa cho những chuyến hàng."""

S["Chương 87 - Sản xuất máy cày ra mắt.txt"] = """Hùng gấp phiếu. Mai: gửi giá cho Cầu Diễn. Gặp chị Hai. Sửa tay lái rung.

Chương 87 đóng lại không bằng chiến thắng — bằng một bước đi vững: bảy đơn hàng, hai góp ý kỹ thuật, một lỗi cần sửa."""

S["Chương 88 - Sản xuất máy gặt ra mắt.txt"] = """Chưa ai bị bỏ lại. Hôm nay làm được máy gặt — nhưng làm máy mà không mất người mới là cái cần giữ.

Phần thưởng chỉ thật khi máy chạy ngoài đồng và thợ còn muốn vào xưởng sáng hôm sau."""

S["Chương 9 - Bán thuốc men.txt"] = """Về nhà, Lan kể chuyện đứa bé sốt. Bà Hà lấy túi thuốc, hỏi từng viên. Họ bỏ một gói giảm đau cũ.

Sổ cuối ngày có hai hộp loại bỏ, một lần hoàn tiền, ba khách chuyển bác sĩ. Lan đặt tên cột mới: 'Không bán vì an toàn.'"""

S["Chương 90 - Bắt đầu Phần 3.txt"] = """Đã kéo ai đi cùng mà không vứt lại? Nếu mai khó hơn hôm nay, liệu câu trả lời có còn giống không?

Trời hửng nắng. Ông không tự trả lời. Ngày mới trả lời."""

S["Chương 91 - Sản xuất thép Hải Phòng.txt"] = """Hùng ghé xưởng... tổng kết: dây chuyền ổn, phôi đạt, tồn kho khớp, mẻ CT5 đã đạt yêu cầu.

Ông gấp sổ. Ngoài kia biển Hải Phòng vỗ đều, cảng sáng đèn. Một thời kỳ mới đang đến — dù mệt, ông còn muốn thức."""

S["Chương 92 - Sản xuất xi măng.txt"] = """Từng việc một — có tên, có hạn, có cách kiểm. Ông gấp sổ. Tiếng xe máy năm 1987 lấn đường xe đạp.

Phần thưởng không phải khi lò chạy. Là khi người ta còn muốn vào xưởng sáng hôm sau."""

S["Chương 93 - Hùng gặp cô Hạnh.txt"] = """Cái giá của yêu lại không phải tiền. Cái giá là sợ — sợ làm người kia tổn thương, sợ mình không đủ.

Nhưng Hùng nhìn bầu trời Sài Gòn chiều muộn màu tím pha hồng. Sợ cũng được. Sợ nhưng vẫn đi. Chậm. Có người cùng đi."""

S["Chương 94 - Hùng gặp cô Mai và cô Lan.txt"] = """Chuyến xe về Hà Nội dài, đường xóc, nhưng Hùng không mệt. Một câu hỏi nhẹ nhàng lướt qua suốt chặng.

Ông biết câu trả lời sẽ đến lúc khác. Hôm nay, ông chỉ muốn nhớ: 1986, Đà Nẵng — hai con người, một bữa cơm."""

S["Chương 95 - Hùng chọn cô Hạnh.txt"] = """Một người đàn ông bốn mươi, sau tất cả thăng trầm, biết rằng — hối tiếc vì điều đã làm nhẹ hơn hối tiếc vì điều không dám.

Hà Nội, thu 1986. Hùng đã chọn. Và ông sẽ không quay lại."""

S["Chương 97 - Sản xuất điện tử.txt"] = """Hùng về nhà trong bóng tối. Đường đất, không đèn. Tiếng ếch từ ruộng bên.

Sản xuất điện tử năm 1987, tại xưởng nhỏ ven thành phố. Không robot, không phần mềm. Chỉ mỏ hàn, đồng hồ vạn năng, và một người tin rằng Việt Nam có thể làm được."""

S["Chương 98 - Sản xuất điện thoại.txt"] = """'15/7/1987 — ra được một cuộc gọi thật từ điện thoại tự làm. Sau cháo năm tỉnh lại, sau khu chợ vải.'

Ông gấp sổ. Mưa rào tháng Bảy gõ mái tôn. Trong phòng, đèn dầu vàng nhạt. Ông không mơ: mai còn việc."""

S["Chương 99 - Mở rộng viễn thông.txt"] = """'Tháng 9/1987 — mạng viễn thông khu vực Hà Đông hoạt động. 20 thuê bao. 8 km cáp. 150 số tổng đài.'

Ông gấp sổ. Mưa tháng Chín gõ mái tôn, đều, không vội. Cáp đồng. Tổng đài cũ. Nhưng kết nối — thật."""

print(f"Total scenes defined: {len(S)}")

# Verify all 103 files have scenes
result = subprocess.run(
    ["grep", "-rl", "system_ledger", BASE, "--include=*.txt"],
    capture_output=True, text=True
)
all_files = set()
for f in result.stdout.strip().split('\n'):
    fn = os.path.basename(f.strip())
    if fn:
        all_files.add(fn)

missing = all_files - set(S.keys())
if missing:
    print(f"WARNING: Missing scenes for {len(missing)} files:")
    for m in sorted(missing):
        print(f"  {m}")
else:
    print("All 103 files have scenes. Ready to apply.")

# Apply replacements
for fname, scene in S.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"  SKIP: {fname} not found")
        continue
    
    # Read the file
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the system header block
    # Pattern: ====\n「Hệ thống — xxx」... Ghi chú: ... ====\n
    # We need to replace just the Ghi chú line
    
    # Find all Ghi chú lines containing system_ledger
    old_patterns = []
    for line in content.split('\n'):
        if 'system_ledger' in line and 'Ghi chú' in line:
            old_patterns.append(line)
    
    if not old_patterns:
        print(f"  SKIP: {fname} — no system_ledger found")
        continue
    
    old_line = old_patterns[0]
    new_line = scene
    
    # Replace: keep everything else intact, change only the Ghi chú line
    new_content = content.replace(old_line, new_line, 1)
    
    if new_content == content:
        print(f"  FAIL: {fname} — replacement did nothing")
        continue
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  OK: {fname} — replaced '{old_line[:50]}...'")

print("\nDone!")
