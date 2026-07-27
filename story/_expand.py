"""Expand all chapters to 3000+ word-tokens"""
import os, re

BASE = r'C:\Dev\XLab_MTC\Niên Đại Thương Gia'

def expand_chapter(num, title, addon):
    path = os.path.join(BASE, f'Chương {num} - {title}.txt')
    c = open(path, encoding='utf-8').read()
    idx = c.find('「Hệ thống')
    if idx > 0:
        body = c[:idx].rstrip()
        panel = c[idx:]
    else:
        panel_end = c.find('\n============================================================')
        if panel_end > 0:
            body = c[:panel_end].rstrip()
            panel = c[panel_end:]
        else:
            print(f"{num}: no split point found!")
            return
    new_c = body + '\n\n' + addon + '\n\n' + panel
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_c)
    new_wc = len(new_c.split())
    print(f"{num}: {len(c.split())} -> {new_wc} words {'✓' if new_wc >= 3000 else '✗'}")

# ====== CH 289 ====== (+400 words)
e289 = """
Tuần sau đó, Hùng nhận được báo cáo đầu tiên từ phòng kiểm toán nội bộ: đã rà soát toàn bộ sổ sách bảy công ty con. Kết quả: không phát hiện thêm sai sót nào ngoài vụ đã công bố. Báo cáo được gửi đến Sở Giao dịch Chứng khoán, đăng tải công khai. Giá cổ phiếu Thương Gia — sau khi giảm 4% trong tuần họp báo — bắt đầu hồi phục. Một quỹ đầu tư nước ngoài mua thêm 2% cổ phần, nâng tỷ lệ nắm giữ lên 8%. Thông điệp của họ: tin vào sự minh bạch của Thương Gia.

Ông Phúc gọi: "Thấy chưa, nói thật có mất gì đâu?" Hùng: "Mất ngủ một tuần, chú ạ." "Nhưng ngủ được phần đời còn lại."""

expand_chapter('289', 'Phản ứng minh bạch', e289)

# ====== CH 291 ====== (+350 words)
e291 = """
Trong chuyến bay về Hà Nội, Hùng ngồi cạnh một người đàn ông trạc ba mươi lăm, đang đọc bản in dày về logistics. Họ bắt chuyện. Người đàn ông tên Minh — CEO của một startup logistics vừa gọi vốn thành công 2 triệu USD từ quỹ đầu tư Nhật. Minh hỏi Hùng: "Anh làm nghề gì?" Hùng cười: "Tôi cũng làm logistics, nhưng kiểu cũ. Anh làm kiểu mới. Nói tôi nghe."

Minh nửa giờ sau vẫn nói. Hùng nghe, thỉnh thoảng hỏi. Khi máy bay hạ cánh, Hùng rút danh thiếp: "Nếu cần đối tác già — gọi tôi." Minh nhìn danh thiếp, mắt mở to: "Anh là... Trần Văn Hùng?" "Ừ. Tôi già, nhưng còn học được."""

expand_chapter('291', 'Hội nghị thượng đỉnh doanh nghiệp', e291)

# ====== CH 292 ====== (+1700 words needed - use longer addon)
e292 = """Một tuần sau buổi gặp Thủ tướng, điện thoại của Hùng không ngừng reo. Các doanh nghiệp trong ngành gọi, hỏi về chính sách mới. Các nhà báo gọi, xin phỏng vấn. Một số người trong ngành điện — những người làm nghề lâu năm — gọi để nói: "Lâu lắm mới có người dám nói thẳng như ông. Bọn tôi cảm ơn."

Hùng không ngờ đề xuất của mình lại gây được tiếng vang như vậy. Nó cho thấy một điều: rất nhiều người đang chờ một tiếng nói dám đứng lên, nhưng họ không dám. Khi ông làm, họ theo.

Chiều thứ sáu, Hùng nhận được cuộc gọi từ một người không quen biết. "Tôi là Kỹ sư trưởng nhà máy nhiệt điện Phả Lại. Tôi xin phép nói: đề xuất của ông hay, nhưng thực tế thi công không đơn giản như báo cáo McKinsey. Nếu ông cần người hiểu về vận hành điện, tôi sẵn sàng góp ý."

Hùng ghi lại số điện thoại. Một chuyên gia trong ngành, không được hỏi, tự nguyện gọi. Đó là dấu hiệu cho thấy đề xuất của ông đã chạm đúng nhu cầu thực tế.

Cuối tuần, Hùng bay vào Đà Nẵng cùng Lan. Họ đi dọc bãi biển, nơi dự kiến đặt nhà máy. Mặt trời lặn, nước biển nhuộm màu cam. "Em thấy không," Hùng nói, "cái đẹp nhất của năng lượng mặt trời không phải là tiết kiệm tiền. Mà là nó sạch. Cháu nội mình sau này sẽ hỏi: ông đã làm gì khi cả thế giới chuyển sang năng lượng sạch? Mình phải có câu trả lời."

"Nhưng anh có chắc sẽ làm được không?"

"Không chắc. Nhưng nếu không thử, chắc chắn không làm được. Có những việc phải làm, dù biết có thể thất bại. Vì thất bại cũng đáng hơn không làm."

Trên đường về khách sạn, họ ghé qua một khu chợ nhỏ. Một bà lão bán rau, thấy Hùng mặc comple, hỏi: "Chú ở đâu tới?" "Hà Nội." "Vô đây làm gì?" "Tìm đất xây nhà máy." Nhà máy gì?" "Pin mặt trời." Bà lão cười: "Có cái nắng này mà làm ra điện được hả chú?" Hùng cười theo: "Dạ, nhờ cái nắng đó." "Vậy tốt. Rẻ hơn điện nhà nước không?" "Sẽ rẻ hơn trong năm năm nữa." "Ừ, vậy làm đi. Chừng nào có điện rẻ, bà mua."""

expand_chapter('292', 'Đề xuất chính sách xanh', e292)

# ====== CH 293 ====== (+2000 words needed)
e293 = """Buổi tối tại khách sạn Fullerton, Hùng không ngủ được. Ông ra ban công, nhìn xuống vịnh Marina. Singapore sáng rực — ánh đèn từ những tòa nhà cao tầng, từ những cây cầu, từ con tàu du lịch đang neo đậu. Một thành phố của tương lai. Ông nhớ lại lần đầu tiên đến Singapore năm 1995. Hồi đó, Thương Gia còn nhỏ, tiền ít, đối tác chưa tin tưởng. Ông đi với một chiếc vali rẻ tiền, ở khách sạn giá rẻ khu Geylang. Ăn cơm hộp mua từ tiệm tạp hóa Việt Nam.

Mười bảy năm sau, ông ở Fullerton, ăn tối với đối tác Nhật, trình bày thương hiệu quốc gia. Nhưng trong lòng, vẫn là cậu bé nghèo Hà Đông. Ông không muốn mất đi cái đó. Cái đó — cảm giác nhỏ bé, đói khát, biết ơn từng cơ hội — là động lực đưa ông đi suốt ba mươi năm.

Sáng hôm sau, trước giờ trình bày, Hùng đi dạo một vòng quanh khu vực Marina. Ông gặp một người bán hàng rong — bánh mì Việt Nam. Người phụ nữ khoảng năm mươi, tay nhanh thoăn thoắt, nụ cười tươi. "Mua bánh mì không anh? Bánh mì Việt Nam, chuẩn vị Huế." Hùng dừng lại. "Chị qua đây lâu chưa?" "Mười năm rồi. Theo chồng. Ổng làm kỹ sư. Em buồn quá nên mở quầy."

Hùng mua hai cái. Bánh mì nóng, giòn, nhân đầy đặn. Ông ăn trên ghế đá, nhìn dòng người Singapore hối hả. "Thương hiệu quốc gia," ông nói với Lan. "Nó không phải là những gì mình nói. Nó là những gì mình làm. Và đôi khi, nó nằm ở những thứ nhỏ nhặt nhất — như cái bánh mì này."

"Em không hiểu."

"Thì cũng không cần hiểu. Chỉ cần làm đúng. Thương hiệu sẽ tự đến."

Buổi chiều, khi trình bày xong, giám khảo người Nhật hỏi Hùng một câu cuối: "Ông nghĩ ba mươi năm nữa, Thương Gia sẽ ở đâu?" Hùng suy nghĩ một lúc. "Tôi hy vọng không còn nữa." Cả phòng ngạc nhiên. Hùng tiếp: "Ba mươi năm nữa, Thương Gia không còn là một cái tên. Nó sẽ là một phần của câu chuyện Việt Nam. Giống như Sony với Nhật, Samsung với Hàn. Khi thương hiệu trở thành câu chuyện chung, không còn là sở hữu riêng nữa. Tôi hy vọng điều đó xảy ra. Nó sẽ là thành công lớn nhất."""

expand_chapter('293', 'Thương hiệu quốc gia', e293)

# ====== CH 294 ====== (+2000 words needed)
e294 = """Sau lễ khánh thành ba ngày, bảo tàng đón hơn năm nghìn lượt khách. Một con số lớn đối với một bảo tàng doanh nghiệp — nhưng ý nghĩa hơn cả con số là những dòng cảm tưởng để lại trong sổ vàng. Hùng đọc chúng vào tối thứ bảy, khi bảo tàng đóng cửa, ngồi một mình ở tầng ba. Một du khách viết: "Tôi không phải người Hà Nội. Tôi vào thăm vì tò mò. Ra về, tôi thấy tự hào vì là người Việt Nam." Một học sinh lớp chín viết: "Em muốn sau này làm doanh nhân như chú Hùng." Một công nhân viết: "Cảm ơn Thương Gia đã cho tôi việc làm hai mươi năm." Hùng đọc từng dòng, gấp sổ, cất vào ngăn kéo.

Sáng chủ nhật, Hùng đưa bà Hà đến thăm bảo tàng — lần đầu tiên bà đến sau ngày khánh thành, vì hôm đó bà bận tiếp khách. Bà mặc áo dài, tóc bới cao, đi giày búp bê — lần hiếm hoi bà ăn mặc chỉnh chu. Hùng dắt bà đi từng tầng, giải thích từng hiện vật. Bà thỉnh thoảng gật gù, thỉnh thoảng sờ tay lên tủ kính, nhìn chăm chú.

Đến tầng hai, trước tấm ảnh đen trắng — người đàn ông đội nón lá đẩy xe hàng rong — bà dừng lại lâu nhất. "Ổng mà còn sống chắc không tin nổi." "Con cũng không tin."

Bà quay sang nhìn Hùng. "Mẹ có một điều hối tiếc. Hồi ba con mất, mẹ không có tiền mua quan tài tử tế. Phải mua loại gỗ tạp — chỉ dùng được ba năm, sau đó phải sang cát. Nếu..." Bà không nói hết. Hùng nắm tay bà. "Bà ơi, thôi đừng nhắc chuyện đó. Quan tài gì bây giờ cũng không còn quan trọng. Ba biết mình làm được cái này — chắc ổng cũng vui.""""

expand_chapter('294', 'Bảo tàng Thương Gia', e294)

# ====== CH 295 ====== (+1800 words needed)
e295 = """Ngày hội công nhân kết thúc, nhưng dư âm của nó kéo dài nhiều ngày. Những bức ảnh chụp Hùng ngồi ăn cơm cùng công nhân được chia sẻ trên các diễn đàn nội bộ, lan sang một số trang mạng xã hội. Phòng truyền thông gọi Lan, hỏi có nên can thiệp. Lan hỏi Hùng. Hùng bảo: "Để yên. Nếu báo chí hỏi, nói thật: ông chủ ăn cơm với công nhân, chuyện lạ à?"

Trong tuần sau đó, Hùng nhận được hơn bốn mươi lá thư tay từ công nhân các nhà máy. Một số cảm ơn, một số đề xuất cải tiến, một số kể hoàn cảnh gia đình và xin giúp đỡ. Hùng đọc tất cả. Có những lá thư làm ông mất ngủ — một nữ công nhân đơn thân, con bị bệnh tim, không đủ tiền mổ. Sáng hôm sau, ông gọi Lan: "Liên hệ quỹ từ thiện của công ty, xử lý. Và xem còn trường hợp nào tương tự."

"Có nhiều lắm, anh. Hơn em tưởng."

"Thì làm từng cái một."

Buổi chiều, Hùng ngồi trong văn phòng, nhìn ra sân nhà máy. Công nhân đang tan ca, hàng trăm chiếc xe đạp, xe máy đổ ra cổng. Những khuôn mặt mệt mỏi nhưng vui. Ông nghĩ: mỗi người trong số họ có một câu chuyện. Có người vay mượn để nuôi con ăn học. Có người ở trọ, mỗi tháng gửi tiền về quê. Có người đang nuôi cha mẹ già, có người đang trả nợ từ cơn bão lũ năm ngoái. Họ thức dậy lúc 5h sáng, làm việc mười tiếng, về nhà nấu cơm, dạy con học. Vòng quay ấy lặp lại hết ngày này qua ngày khác. Họ không phàn nàn. Họ chỉ yêu cầu được đối xử công bằng.

Hùng ghi vào sổ: "Ngày hội công nhân — một ngày. Nhưng nó phải trở thành ba trăm sáu mươi lăm ngày. Không phải tổ chức sự kiện — mà là thay đổi cách vận hành. Lắng nghe trước khi họ phải la to. Công bằng từ trong quy chế, không phải từ lòng tốt của ông chủ."

Đêm, ông gọi cho Klaus: "Klaus, tôi vừa ký thỏa ước lao động tập thể." Klaus cười: "Ở Đức, chuyện đó là bình thường." "Ở Việt Nam, nó là bước tiến." "Vậy thì — chúc mừng ông. Tiến lên."""

expand_chapter('295', 'Ngày hội công nhân', e295)

# ====== CH 297 ====== (+1800 words needed)
e297 = """Việc xử lý vụ Dũng và ban hành quy chế kỷ luật tạo ra hiệu ứng tích cực hơn Hùng tưởng. Một tuần sau khi quy chế có hiệu lực, mười hai vụ tranh chấp lao động nhỏ ở các nhà máy được giải quyết thông qua hội đồng kỷ luật — thay vì bị đẩy lên thành xung đột công đoàn. Các quản đốc bắt đầu thận trọng hơn trong cách xử lý công nhân. Không ai muốn bị đưa ra hội đồng.

Mạnh gọi: "Anh Hùng, hiệu quả ngoài mong đợi. Công nhân thấy có chỗ dựa, họ yên tâm làm việc. Mấy quản đốc hay quát tháo cũng dịu lại."

Hùng: "Chưa xong đâu. Đây mới là khởi đầu. Tôi muốn mỗi quý, công đoàn tổ chức một buổi đối thoại trực tiếp giữa tôi và đại diện công nhân. Không qua trung gian. Tôi trả lời trực tiếp. Có biên bản, công bố nội bộ."

"Bao nhiêu người?"

"Mỗi xưởng cử một đại diện. Năm mươi người mỗi quý. Tôi dành cả ngày. Không xử lý việc khác."

"Anh thật sự làm?"

"Tôi không nói đùa, Mạnh."

Hai tháng sau, buổi đối thoại đầu tiên diễn ra tại nhà máy Hà Đông. Lan chuẩn bị phòng họp lớn, sắp xếp bàn ghế hình chữ U, chuẩn bị nước uống và bánh kẹo — nhưng Hùng bảo dẹp đi. "Làm như hội nghị. Để họ thấy tôi không phải ông chủ từ xa. Kê ghế vòng tròn, không phân biệt thứ bậc."

Buổi đối thoại kéo dài bốn tiếng. Công nhân hỏi về lương, về ca đêm, về điều hòa trong xưởng — nơi có các dây chuyền sản xuất linh kiện điện tử, nhiệt độ lên tới bốn mươi độ vào mùa hè. Một nữ công nhân hỏi: "Chú Hùng, xưởng lắp ráp linh kiện của tụi con không có máy lạnh, chỉ có quạt công nghiệp. Nóng quá, tụi con hay xỉn. Có cách nào không?" Hùng trả lời: "Tuần sau, tôi cho người khảo sát lắp máy lạnh cho toàn bộ xưởng — ưu tiên xưởng linh kiện trước. Nếu chi phí cao, tôi sẽ điều chỉnh kế hoạch. Trong vòng hai tháng, có máy lạnh."

Cả phòng vỗ tay. Hùng giơ tay: "Đừng vỗ tay. Khi nào máy chạy hãy vỗ.""""

expand_chapter('297', 'Công đoàn đối thoại', e297)

# ====== CH 298 ====== (+1600 words needed)
e298 = """Ba tháng sau khóa học đầu tiên, Hùng nhận được báo cáo kết quả từ Lan. Mười hai trong số ba mươi nhân viên đã được thăng chức hoặc chuyển sang vị trí quản lý. Toàn — nhân viên bảo vệ — được thăng làm phó quản đốc kho. Chị Hương — tổ trưởng tổ may — được cử đi học thêm về quản lý chất lượng. Tỷ lệ hài lòng của học viên đạt 94%.

"Anh có muốn mở rộng chương trình không?" Lan hỏi.

"Mở. Nhưng không phải tràn lan. Mỗi năm ba khóa, mỗi khóa ba mươi người. Chọn người từ các xưởng khác nhau, ưu tiên những người có hoàn cảnh khó khăn nhưng chịu học."

"Tại sao lại ưu tiên người khó khăn?"

"Vì những người đó — nếu được trao cơ hội — họ sẽ trân trọng nó nhiều hơn. Ngày xưa, khi tôi mới mở xưởng, tôi thuê một người thợ không có bằng cấp, chỉ có đôi tay khéo. Anh ta làm với tôi hai mươi năm, chưa bao giờ trễ một ngày. Cống hiến của một người được cho cơ hội gấp ba lần người vốn đã có mọi thứ."

Lan ghi chép. "Em sẽ thiết kế lại chương trình. Thêm phần thực hành, giảm lý thuyết."

"Đúng. Và nhớ: dạy họ những gì họ cần, không phải những gì mình muốn dạy. Đừng biến nó thành trường đại học. Học xong phải áp dụng được ngay. Nếu không, họ sẽ quên và thất vọng."

Khóa thứ hai của chương trình được khai giảng vào tháng 2/2013, với ba mươi lăm học viên — tăng thêm năm so với khóa đầu. Lần này, đơn xin tham gia nhiều gấp đôi chỗ học. Phải chọn, phải loại — và đó là dấu hiệu tốt.

Hùng không tham gia giảng dạy. Ông chỉ đến khai giảng mười lăm phút, nói một câu: "Các anh chị là tương lai của Thương Gia. Tương lai đó do các anh chị tự viết, tôi chỉ mở cửa." Rồi ông đi. Nhưng câu nói đó, theo Lan, là động lực lớn nhất cho các học viên. Họ biết: ông chủ không chỉ nói — ông làm."""

expand_chapter('298', 'Đào tạo lãnh đạo trẻ', e298)

# ====== CH 299 ====== (+1800 words needed)
e299 = """Sáng ngày sinh nhật, Hùng dậy sớm hơn thường lệ một tiếng. Ông không chạy bộ, không đọc báo — ngồi trước bàn, mở cuốn sổ cũ, đọc lại trang đầu tiên của ba mươi năm trước. Nét chữ nguệch ngoạc, mực đã phai: "Hôm nay tôi bắt đầu. Không biết kết thúc thế nào, nhưng tôi sẽ đi." Ông lật từng trang: những con số lỗ lãi, những địa chỉ đối tác ghi nguệch ngoạc, những bức thư phác thảo. Mỗi trang một ký ức.

Đến trang giữa cuốn sổ — năm 1997 — ông dừng lại. Trang đó ghi: "Nhà máy Đức lỗ. Mọi người bảo về. Tôi bảo ở. Nếu bây giờ bỏ cuộc, mười năm sau sẽ hối hận." Bên cạnh là một vết mực lem — chắc do nước mắt. Hùng không nhớ mình có khóc không. Nhưng nhìn vết mực, ông hiểu: ngày đó không dễ.

Buổi sáng, ông nhận được cuộc gọi từ con trai. Trần Minh Quân — đang học thạc sĩ quản trị kinh doanh tại Anh. "Ba, con có chuyện muốn nói. Tết này con về, con không quay lại Anh nữa." Hùng im. "Học xong chưa?" "Còn luận văn. Con có thể viết từ xa. Con muốn về làm việc."

"Nhưng con muốn làm gì?"

"Con muốn vào Thương Gia. Từ vị trí thấp nhất."

"Tại sao?"

"Vì con muốn hiểu công ty của ba. Vì con muốn xứng đáng với cái tên Trần. Vì con không muốn sau này người ta nói: thằng đó chỉ vì là con ông chủ."

Hùng im lâu. Rồi ông nói: "Về đi. Ba sắp xếp."

Dập máy, ông nhìn ra cửa sổ. Ngoài kia, Hà Nội vào đông. Cây bàng trụi lá. Một người đàn ông đang đạp xích lô chở hai đứa trẻ đi học. Cuộc đời vận hành vòng quay của nó. Thế hệ trước đi, thế hệ sau tiếp nối. Ông đã chuẩn bị cho khoảnh khắc này — nhưng không ngờ nó đến nhanh vậy.

Buổi tối, bà Hà nấu bữa cơm đúng kiểu ngày xưa: cá kho tộ, thịt luộc, canh chua, cà pháo mắm nêm. Cả nhà quây quần — Lan, bà Hà, Hùng. Ba người — nhưng đủ ấm. Lan kể chuyện hồi nhỏ, bà Hà cười sặc sụa. Bà nói: "Hồi tao mới về làm dâu, nhà nghèo, có bữa phải ăn cơm với nước mắm ớt. Thằng Hùng nó ăn, nó bảo: ngon. Tao biết nó nói dối, nhưng tao thương."

"Con nói thật mà," Hùng cãi.

"Thật cái gì? Cơm với nước mắm mà ngon? Là tại con thương mẹ không muốn mẹ buồn." Bà cười, mắt rưng rưng.

Đêm, Hùng vào phòng riêng, mở cuốn sổ mới — bìa đen, trang trắng. Trang đầu: "Trần Văn Hùng — 2013. Hành trình tiếp theo." Ông viết:

"50 tuổi. Còn khoảng hai mươi năm làm việc. Mục tiêu:
1) Nhà máy pin mặt trời vận hành.
2) Lan làm CEO.
3) Quân vào công ty.
4) Bà Hà khoẻ — đưa bà đi Pháp.
5) Viết xong hồi ký — cho cháu nội.

Nếu làm được năm điều này, 70 tuổi tôi có thể nhắm mắt."""

expand_chapter('299', 'Hùng 50 tuổi – nhìn lại', e299)
