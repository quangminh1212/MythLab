import os

os.chdir("C:/Dev/XLab_MTC/Niên Đại Thương Gia")

def write_chapter(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    wc = len([w for w in content.split() if len(w) >= 2])
    print(f"  Written: {filename} ({wc} words)")
    return wc

# ============================================================
# CHƯƠNG 111
# ============================================================
ch111 = """\
============================================================
Chương 111: Mở sang châu Mỹ USA
============================================================

Bảy giờ sáng, Sài Gòn cuối năm 1986. Cái lạnh miền Nam là thứ lạnh ẩm, thấm vào người không ồn ào như gió mùa đông bắc — nó im lặng đi qua lớp áo len mỏng, qua kẽ cửa sổ gỗ đã co lại vì ẩm, qua khe cửa nhà sau còn ướt sau khi tắm. Trời vừa tạnh một cơn mưa nhỏ từ năm giờ sáng. Mái tôn nhà bếp còn nhỏ giọt, tiếng nước rơi lộp độp trên nền xi măng, chảy thành dòng xuống rãnh hẻm mang theo mùi bùn đất pha mùi rêu xanh ở chân tường. Những giọt nước cuối cùng còn đọng trên tàu lá chuối trong sân, thỉnh thoảng lại rơi một giọt xuống nền.

Trong căn nhà nhỏ trên đường Nguyễn Đình Chiểu, Hùng ngồi trước tập catalogue của Los Angeles Importers Inc. — mười bảy trang in trên giấy bóng loáng, ảnh chụp sản phẩm với nền trắng sạch, mỗi ảnh đều có chú thích bằng tiếng Anh. Một chiếc bình gốm men xanh trên trang bảy khiến ông dừng lại thật lâu. Hình dáng giống gốm Bình Dương — men chảy mềm, xương gốm nung ở nhiệt độ cao — nhưng cách lên men khác, men dày hơn, tạo độ bóng sâu. Ông lấy bút chì mềm khoanh tròn bức ảnh, ghi bên lề bằng nét chữ nhỏ nhưng dứt khoát: Sản xuất được. Cần mẫu đối chiếu với lò Bình Dương. Xem men xanh có đúng chuẩn không.

Những thứ này — gốm sứ men lam, mây tre đan tinh xảo, sơn mài khảm trai, đồ gỗ chạm trổ — Việt Nam sản xuất được. Thậm chí, với một số mặt hàng, Việt Nam có thể làm tốt hơn Trung Quốc, Thái Lan về độ tinh xảo. Vấn đề không phải sản xuất. Vấn đề là bán — và bán cho ai, bằng cách nào, với niềm tin nào, ở giữa một vùng tối mờ mịt của cấm vận thương mại và quan hệ hai nước chưa bình thường hóa.

Ông mở cuốn sổ tay bìa xanh. Gáy đã bong chỉ, vài trang rách ở gáy vì lật mở hàng trăm lần suốt hai năm rưỡi. Trang đầu tiên của mục mới — hai chữ "USA" viết bằng mực xanh, gạch chân hai lần — vẫn trống. Chỉ có một dòng viết bằng bút chì ở góc trên bên phải: Ai chịu khi hỏng? Viết xong, ông xóa đi, viết lại: Nếu hỏng, tôi chịu. Lại xóa. Cuối cùng để trống.

Khoảng cách từ Việt Nam đến Mỹ không đo bằng hải lý qua Thái Bình Dương. Nó đo bằng số chữ ký trên hợp đồng, số lần tra từ điển, số đêm thức trắng vì một điều khoản không hiểu, số lần gọi điện thoại đường dài đắt gấp ba cước thường.

Bà Hà từ bếp đi ra, tay bưng dĩa bánh tráng cuốn — bánh tráng mềm cuốn tôm khô, rau thơm, giá đỗ, chấm nước mắm chua ngọt pha ớt đỏ. Bà đặt dĩa xuống bàn bên cạnh tập catalogue, liếc qua những trang in màu, không hỏi một câu. Im lặng của bà không phải vô tâm — là một loại im lặng đã được rèn qua nhiều năm làm vợ, làm mẹ, khi biết rằng đôi khi hỏi chỉ làm phiền người đang nghĩ. Ở tuổi năm mươi lăm, bà đã biết khi nào hỏi là thừa.

Hùng gật, nhưng không rời mắt khỏi catalogue.

#

Trần Thị Lan bước vào lúc tám giờ. Chị không ngồi — chị đứng cạnh bàn, chờ Hùng ngước lên. Đó là thói quen cũ từ hồi còn cửa hàng nhỏ, khi không gian chật đến nỗi đứng nhanh hơn ngồi. Chị mặc áo sơ mi trắng tay ngắn, quần tây đen, sổ tay kẹp dưới nách. Dáng đứng của người sẵn sàng đi năm chỗ trong một buổi sáng.

— Có chuyện — chị nói, giọng đều, không thừa một âm. — Bảng kiểm hàng Mỹ em làm tuần trước thiếu cột "số đơn vị kiện". Nếu không ghi số kiện, khi hải quan bên kia mở container ra đếm không đủ, mình không chứng minh được mình đã gửi đủ số lượng. Họ sẽ giữ hàng, phạt lưu container, và gửi công văn yêu cầu giải trình — tổng cộng có thể mất ba tuần, chưa kể tiền phạt lưu bãi và chi phí đi lại.

Hùng nhìn chị. Lan nhỏ hơn ông gần chục tuổi, nhưng mắt chị — thứ mắt của người từng đếm từng cái kẹo, từng gói mì khi mới mở cửa hàng — đã có cái nhìn tổng thể trước khi vào chi tiết. Chị học không qua sách vở, nhưng qua sai lầm. Và chị đã sai đủ nhiều để bắt đầu đúng.

— Em sửa chưa?

— Sửa rồi. Viết thêm cột mới, chép lại toàn bộ bảng — từ sáu cột thành bảy. Tối qua em làm tới mười hai giờ dưới ngọn đèn dầu — mất điện từ chín giờ.

Hùng gật. Một cái gật nhẹ. Lan hiểu — không cần lời khen.

#

Cô Hạnh vào lúc chín giờ. Hai mươi ba tuổi, quê Bến Tre, con nhà nghèo, tự học may nuôi mẹ già. Trên tay cô là cuốn từ điển Anh-Việt bìa cứng in từ thời Mỹ ngụy — gáy bong, ruột rách vài trang vì mọt, mùi giấy ẩm mốc pha lẫn mùi keo dán mới. Trên bàn, một tập phiếu nhỏ, mỗi phiếu ghi một thuật ngữ thương mại, xếp theo thứ tự abc — cách cô tự dạy mình từ những ngày đầu tiên vào làm.

— Em tra được tới đây — cô nói, giọng hơi run. — Nhưng mấy chỗ em không chắc. "Without prejudice" — em không thấy trong từ điển.

Hùng cầm tập phiếu, lật từng cái. Chữ cô Hạnh rất đẹp — nét chữ thẳng, đều, từng con chữ không lem mực, viết nắn nót từng nét.

— "Without prejudice" nghĩa là "không ảnh hưởng đến quyền lợi pháp lý". Khi một bên gửi thư đề nghị hòa giải hoặc thương lượng, họ ghi dòng này. Nếu hai bên nói chuyện mà không đi đến đâu, những gì họ nói trong quá trình đó không thể bị đưa ra tòa làm bằng chứng chống lại họ.

Cô Hạnh gật gù, viết vào phiếu mới. — Kiểu nói thử, thăm dò, nhưng không chính thức.

— Đúng. Còn gì nữa?

Cô giở tập phiếu: — "Force majeure" là bất khả kháng. "Arbitration" là trọng tài thương mại. "Demurrage" là tiền phạt lưu container.

— Đúng hết. Những từ này sẽ xuất hiện nhiều trong các hợp đồng tới.

— Hỏi một chữ còn hơn sai một lô — cô nói, như nhắc lại điều đã thuộc từ những buổi họp đầu tiên.

Hùng cười nhẹ. Cô học nhanh.

#

Buổi chiều, Hùng đi tìm ông Bảy.

Ông Bảy trước 1975 làm cho American President Lines — chạy văn phòng ở bến tàu Sài Gòn. Sau giải phóng, hãng giải thể, ông mất việc, mở quán hủ tiếu trong một cái hẻm nhỏ đường Nguyễn Cư Trinh. Quán không tên. Một cái bạt xanh cũ kéo trên mấy cây sắt, sáu bàn nhựa, một tủ kính đựng thịt heo quay và giá sống. Nồi nước dùng sôi liu riu, khói trắng bốc lên, mùi xương hầm thảo quả phảng phất xa.

Hùng ngồi xuống. Ông Bảy thấy, nhận ra, tự mang tô hủ tiếu ra. Kéo ghế ngồi xuống đối diện.

— Chú Hùng, lâu quá không ghé.

— Rảnh để hỏi bác một chuyện — Hùng nói, giọng thấp. — Tôi sắp gửi hàng sang Mỹ.

Ông Bảy đang xoay cái muỗng nhôm trên bàn — thói quen cũ từ hồi đi tàu — ngừng hẳn. Một khoảng im lặng dài. Vài giây. Rồi năm giây. Ông nhìn Hùng thật lâu, qua làn khói thuốc.

— Ai đứng tên bên kia?

— Một nhà nhập khẩu ở California. Người Việt kiều giới thiệu.

— Gặp mặt chưa?

— Chưa. Chỉ thư từ và telex.

— Thư từ bao lâu một lần?

— Hai tháng một hồi âm. Telex nhanh hơn — một tuần — nhưng đắt, tính theo phút.

Ông Bảy châm một điếu thuốc, rít một hơi. — Người Mỹ có cách nói riêng. Không phải lúc nào nói "có" cũng là có. "Let me think about it" — là không. "I'll get back to you" — cũng không. "I'll check and let you know" — còn cửa. "Let's take a look" — cửa rộng hơn. Nhưng câu chắc nhất: "Let's do it" — là muốn làm.

— Còn câu nào nữa không?

— "That's interesting" — chẳng nghĩa gì. Họ nói cho lịch. "We should do lunch sometime" — là không bao giờ có lunch.

— Còn bắt tay?

—Nhìn thẳng mắt, bóp chặt, ba cái, thả. Tay phải, dù anh là tay trái. Đừng đứng gần quá một mét — họ có vùng riêng. Đứng gần quá họ lùi, mất điểm ngay từ giây đầu.

— Còn gì nữa?

— Nếu họ mời ăn tối, đừng từ chối. Trong bữa ăn họ mới nói thật. Văn phòng là để nói vừa. Bàn tiệc là để ký hợp đồng. Cà phê — họ uống đen, không đường. Giờ làm việc không uống rượu. Uống rượu trưa là mất điểm.

Hùng viết hết vào sổ, gấp lại. Ông Bảy nhìn cuốn sổ đang đầy dần, khẽ gật — kiểu gật của người già thấy người trẻ làm việc có hệ thống.

#

Tối hôm đó, Hùng ngồi viết bức thư đầu tiên bằng tiếng Anh. Bà Hà mang ra tách trà gừng nóng ấm, đặt lên bàn. Rồi im lặng ra ngoài, đóng cửa phòng nhẹ nhàng như đóng cửa tủ — thói quen của người biết khi nào cần im lặng.

Hùng viết. Câu đầu tiên viết xong, đọc lại, gạch. Câu thứ hai viết xong, cũng gạch. Câu thứ ba dài hơn, nhưng sai ngữ pháp — gạch tiếp. Tờ nháp đầu tiên vò vứt vào sọt rác. Tờ thứ hai thành một đống chữ nghịch ngoằn ngoèo. Tờ thứ ba bắt đầu có hình hài. Tờ thứ tư. Tờ thứ năm — đến gần nửa đêm — ông giữ lại câu mở đầu mà ông viết ra từ lần đầu tiên, không sửa:

We make things we trust. We ship things we check.

Bức thư dài một trang rưỡi. Ông gấp lại, bỏ vào phong bì, chưa dán.

Sáng hôm sau, ông mang sang nhà một người bạn từng du học Mỹ năm năm. Anh bạn đọc, gật gù — giọng văn ổn. Rồi dừng lại ở chữ "trust". Anh ngước lên nhìn Hùng: — Tôi sửa "trust" thành "believe in". Trust mạnh quá. Nếu hàng có vấn đề gì, họ sẽ nhớ lại chữ này và nghĩ mình hứa hão.

Hùng cầm tờ giấy, nhìn một lúc thật lâu. Một phút. Hai phút. Rồi ông nói, giọng không cao nhưng dứt khoát: — Nếu mình không dám dùng chữ trust với họ, thì mình đừng gửi hàng.

Tiếng nói dứt khoát, không để lại khoảng trống cho thương lượng thêm.

#

Ba ngày sau, bức thư rời Sài Gòn bằng đường hàng không. Hùng tự tay mang ra bưu điện trung tâm — tòa nhà màu vàng cũ kỹ trên đường Công Lý. Xếp hàng mười lăm phút. Mua tem đường hàng không đắt nhất. Dán xong còn ấn tay xuống mấy lần, như để đảm bảo tem không rơi giữa đường.

Cuối tháng Giêng 1987, telex đầu tiên từ California trả lời. Chín chữ trên mảnh giấy in nhiệt mỏng, chữ màu tím nhạt, còn ấm: "Interested in your samples. Please send price list."

Hùng đọc. Lần thứ nhất. Lần thứ hai. Lần thứ ba. Rồi ông lật úp tờ giấy xuống bàn. Bà Hà đang quét nhà, thấy vậy dừng chổi. Hùng không nói. Ông lấy cuốn sổ, viết: Ngày 28 tháng Giêng — telex từ California. Trả lời: gửi price list. Sau đó ông uống hết tách cà phê nguội.

#

Hùng mướn một phòng nhỏ trên đường Nguyễn Thái Học làm văn phòng giao dịch đường Mỹ. Tầng một, hai mươi mét vuông, một bàn gỗ tạp, một tủ sắt trắng cũ kỹ, một cái quạt đứng chạy ồn ào, một chiếc điện thoại mới lắp. Số điện thoại in lên tờ giấy tiêu đề — cô Hạnh đánh máy trên chiếc Olivetti cũ. Lần đầu tiên, Thương Gia có một địa chỉ kinh doanh không trùng với địa chỉ nhà.

Đêm đầu tiên trong căn phòng đó, Hùng ngồi một mình đến khuya. Không bật đèn. Chỉ có ánh đèn đường vàng vọt hắt qua ô cửa sổ nhỏ, vẽ lên sàn nhà một hình chữ nhật ánh sáng. Ông nhìn dãy phố vắng, những cánh cửa đã đóng từ lâu, những bóng người thưa thớt. Mỗi cánh cửa là một người cũng đang tìm ra biển.

Trong cuốn sổ xanh, có một dòng viết từ tháng trước bằng bút chì, mờ dần vì quẹt tay nhiều lần: Đừng để tên Việt trên bao bì nếu hàng bên trong không xứng.

"""
ch111 += """\

============================================================
「Hệ thống — GHI NHẬN ch.111」
Năm: 1987
Tổng EXP: 17,875
Không gian kho: 5,867m²
Kỹ năng trọng yếu: Tài chính lv1, Tài chính lv2, Giáo dục lv1
Ghi chú: sổ cái khớp system_ledger — không double-book
============================================================

Telex từ California nằm trong ngăn kéo. Container chưa rời cảng. Nhưng cuốn sổ đã có đủ chữ ký để mở cửa. Khi container chưa xuất phát, điều duy nhất chạy đúng hạn là chữ tín.
"""

# ============================================================
# CHƯƠNG 112
# ============================================================
ch112 = """\
============================================================
Chương 112: Hoàn thành phần 3
============================================================

Tháng Mười Hai, 1987. Đà Nẵng.

Hùng đứng ở hiên nhà kho — cái kho tường gạch trần tôn, nơi hai năm trước chỉ có bụi hồng và mấy thùng hàng lẻ. Năm 1987 sắp hết. Gió biển thổi vào mang theo vị mặn của muối và tiếng còi tàu từ cảng Tiên Sa xa xa. Hoàng hôn buông nhanh, ráng chiều đỏ cam phủ lên những mái tôn loang lổ rỉ sét. Trong tay ông là một tập sổ bìa nâu — hai mươi tư tháng của Phần 3, mỗi tháng một cuốn, gáy dán băng keo, ruột đầy số viết tay và bút đỏ gạch chân.

Hoàn thành Phần 3 không có pháo hoa. Không có băng rôn, không có báo chí, không có bài phát biểu. Có một cái gật đầu từ Tanaka — khi ông già Nhật kiểm lô hàng cuối, thước cặp trong tay, đo xong, gật. Có tiếng thở phào của cô Hạnh ở góc bàn khi chị đóng cuốn sổ theo dõi xuất khẩu dày nhất từ trước tới nay. Và có mắt bà Hà — thứ ông cần hơn bất kỳ bảng lương nào.

#

Hùng không gọi cuộc họp tổng kết kiểu báo cáo. Ông gọi đội lõi ra cái nhà kho tạm ở Đà Nẵng — tám người, tám cái ghế nhựa, một cái bàn gỗ tạp. Bụi hồng từ lô hàng mới nhập dính đầy gấu quần. Bên ngoài, gió biển thổi tới mang theo mùi cá khô từ làng chài gần đó.

Tanaka lật trang sổ tay, nơi tiếng Nhật xen tiếng Việt nguệch ngoạc, đọc một dòng: bốn trăm mười hai ngày kể từ khi bắt đầu. Bốn trăm mười hai ngày làm việc tại năm tỉnh, ba nhà máy, hai cảng xuất hàng, một chi nhánh nước ngoài. Gần như không ngày nghỉ. Ông già Nhật đã già hơn hai năm trước — tóc bạc thêm, mắt sâu hơn, nhưng tay vẫn vững khi cầm thước cặp.

Trần Thị Lan đọc số liệu từ cuốn sổ tay cô mang theo bên mình suốt hai năm — bìa đã bong, góc đã quăn, ruột đầy những dòng checklist gạch bằng bút đỏ. Cô đọc không bằng giọng tự hào — cô đọc bằng giọng của người đã tự mình kiểm từng con số, và biết con số nào còn nợ.

— Một trăm linh tám cửa hàng — từ chín điểm lên một trăm linh tám. Ba mươi nhà máy — năm cụm: Bắc Ninh cơ khí, Hải Dương dệt may, Hưng Yên bao bì, Nam Định nguyên liệu, Hà Nội lắp ráp hoàn thiện. Mười sáu nghìn bốn trăm mét vuông mặt bằng sản xuất. Chín trăm nhân sự — bảy trăm lao động nhà máy, một trăm tám mươi bốn nhân sự cửa hàng, mười bảy người quản lý. Sáu trăm tám mươi bảy triệu doanh thu tháng — so với một trăm linh bốn triệu đầu Phần 3.

Cô gấp sổ. Mọi người im lặng. Những con số tự nói lên tất cả.

#

Hùng gật. Ít người biết rằng mỗi con số Lan đọc đều có một cuốn sổ chi tiết tương ứng — mỗi cửa hàng một tờ giấy than, mỗi nhà máy một bìa hồ sơ, mỗi lô hàng một dòng chữ ký. Không phần mềm, không máy tính — chỉ có bút bi, giấy kẻ ô, và một người phụ nữ không bao giờ nói "sẽ cố" mà chỉ nói "đã làm".

Ông mở cuốn sổ riêng — sổ ghi chép đối ngoại.

Ba đối tác quốc tế chính thức. Tanaka & Co. Nhật Bản — mối linh kiện điện tử và tư vấn kỹ thuật gắn bó từ đầu Part 2, nay đã trở thành cổ đông chiến lược. CEL Handel Ba Lan — container đầu tiên trị giá 47.500 USD rời cảng Hải Phòng tháng Ba 1987, hàng mây tre đan và sơn mài, qua sáu tháng đàm phán telex, mười bảy bức điện, bức dài nhất bốn mươi bảy phút. Lợi nhuận gộp 15,5% — không cao, nhưng đường đi đã được xác lập. Đơn hàng thứ hai: ba container trị giá 142.500 USD — gấp ba lần đầu. Motokov Tiệp Khắc — hàng dệt may theo tiêu chuẩn ČSN, kiểm bằng kính lúp và tay.

Rồi những chuyến đi xa: Đức — tìm đối tác máy móc cơ khí chính xác. Pháp — đàm phán cà phê robusta, ẩm độ dưới 13,5%, kiểm từng bao. Anh — gặp nhà nhập khẩu hàng thủ công mỹ nghệ. Mỹ — chưa kịp, nhưng đã có lịch trong sổ.

Châu Âu mở ra không phải bằng lời hứa. Mở ra bằng mười một loại chứng từ cho mỗi lô, bằng những bức telex dài đọc mỏi mắt, bằng một container đầu tiên lênh đênh bốn mươi hai ngày trên biển từ Hải Phòng đến Gdansk.

#

Ba nhà máy sản xuất chính.

Thép Hải Phòng. Dây chuyền cán Liên Xô đời sáu mươi, da đen dầu mỡ, tiếng gầm khi chạy thử rung từ móng chân lên tới đỉnh đầu. Klaus — kỹ sư người Đức cao gầy — kiểm tra mác thép bằng kính lúp và cảm quan tay, đứng canh nhiệt kế lò nung như canh nồi thuốc. Nhiệt độ lý tưởng: 1.200 độ C. Thấp hơn 50 độ — phôi nứt. Cao hơn 30 độ — thép cháy mất carbon.

Xi măng Khu công nghiệp. Lò nung dài hơn trăm mét nằm nghiêng, tro bụi bám trắng tóc sau mười phút đứng gần cửa lò. Mẻ đầu clinker xốp như bọt biển. Hùng mua tủ dưỡng hộ mẫu, máy phát dự phòng 150 KVA sau khi cúp điện làm ngừng toàn bộ dây chuyền — mỗi giờ mất 2,5 tấn clinker. Hải — người thợ già hai mươi năm trong nghề — có thể đo độ mòn bi nghiền bằng tai. Năng suất đạt 78% thiết kế.

Điện tử Hà Tây. Xưởng dựng tạm giữa ruộng lúa — tường tôn, mái fibrô xi măng, băng tải ván ép chạy mô-tơ máy khâu cũ. Mười bảy người, mười bảy cây mỏ hàn. Ngày đầu yield 86%. Ngày thứ tư yield 92%. Chú Bảy năm mươi hai tuổi hàn radio từ thời Mỹ, chỉ chỗ yếu bằng tay không cần lời.

Và cái máy điện thoại 98-01 — vỏ nhựa đen, mâm quay nhôm đúc, chuông 75V. Ngày đầu hai mươi ba bộ, mười lăm bộ qua kiểm. Ba trăm bộ đặt hàng từ Bưu điện tỉnh.

#

Hệ thống. Đó là từ Hùng dùng nhiều nhất trong sổ ghi chép Phần 3. Không phải máy móc — là cách làm việc.

Checklist của Lan — ba mươi tờ giấy than hai lớp thu về mỗi tuần, mỗi tổ trưởng đánh dấu ba mục: số đầu ca, hỏng hóc ca trước, vật tư thiếu. Sổ tay chất lượng của Tanaka — kẻ sẵn cột: mã lô, kích thước, dung sai, ngày kiểm, người kiểm. Hùng dịch ra tiếng Việt, in ronéo, giao cho ba mươi tổ trưởng.

Quy tắc ba-có: việc nào chưa có tên thì coi như chưa giao. Việc nào chưa có hạn thì coi như chưa có việc. Việc nào chưa có cách kiểm thì coi như không ai làm.

Năm chỗ dễ gian: ca làm, cân đong, báo cáo tồn, chiết khấu, hoa hồng môi giới. Hùng viết hoa, dán trong xưởng. Kiểm tra luân phiên, không báo trước.

#

Cái giá. Cuối Phần 3: vốn đầu tư 1,39 tỷ — trong két 320 triệu, nợ ngân hàng 180 triệu, nợ bạn hàng 63 triệu, công nợ phải thu 94 triệu. Hàng tồn 312 triệu tính theo giá vốn.

Nợ người: một lời cảm ơn chưa gửi. Ba người trẻ trong đội cần được nghe "làm tốt" trước khi nghe "chỗ còn thiếu". Một bữa cơm với bà cụ Hàng Bông chưa kịp sắp.

#

Xế chiều, Hùng đi chậm quanh khu vực. Ông dừng lâu nhất ở những chỗ dễ bỏ qua — góc tối nhà kho, quầy phụ, ca chiều đã tan.

Ông nhìn về phía cảng. 1987 sắp hết. Đất nước đã khác xa 1986. Đổi Mới không phải là nghị quyết trên giấy — là những container thật rời cảng, những mẻ thép thật ra lò, những đường dây điện thoại thật kết nối.

Bà Hà hỏi ăn chưa trước khi hỏi doanh thu. Lan bưng nước. Mâm cơm canh cua, cá kho tộ, rau muống luộc — đủ để người đi làm còn muốn về. Hùng kể chuyện bằng ngôn ngữ nhà: Tanaka gật đầu, lô thép cuối năm đạt chuẩn, Hải nghe bi nghiền bằng tai, Minh lắp tổng đài Nhật hai ngày không ngủ.

Không biến bàn ăn thành phòng họp.

#

Sau bữa cơm, Hùng ra hiên. Đà Nẵng đêm tháng Chạp se lạnh — gió biển thổi qua những dãy nhà thấp, mang theo mùi cá khô từ làng chài gần đó. Ông nhìn về phía cảng Tiên Sa — nơi container đầu tiên của Thương Gia đã rời bến, nơi những chuyến hàng tiếp theo sẽ đến từ Đức, từ Nhật, từ Mỹ.

Part 4 đang chờ. Những thị trường chưa đặt chân đến. Những đối tác chưa gặp mặt. Những bài học chưa học.

Nhưng tối nay — Phần 3 được khép lại.

Ông mở cuốn sổ cuối cùng — trang ông không cho ai xem.

Viết: Năm 1987. Năm chín trăm mười ngày. Năm từ chín cửa hàng lên một trăm linh tám. Từ một xưởng nhỏ lên ba mươi nhà máy. Từ không có gì ra container đầu tiên đi châu Âu. Năm bà Hà bế được cháu nội. Ngày mai sẽ mở Part 4. Sẽ có sai lầm mới. Sẽ có đêm không ngủ. Nhưng hôm nay, viết xong trang này, gấp sổ lại, tôi biết: không ai bị bỏ lại.

Ông gấp sổ. Tắt đèn. Ngoài kia, cảng Đà Nẵng vẫn sáng đèn — những ánh đèn vàng le lói của tàu cá, của cần cẩu container, của một thời kỳ mới đang đến gần.

Phần 3 đã xong. Nhưng cả đời — thì chưa.

"""
ch112 += """\

============================================================
「Hệ thống — CỘT MỐC ch.112 — HOÀN THÀNH PHẦN 3」
Năm: 1987
Tổng EXP: 17,125
Không gian kho: 5,667m²
Kỹ năng trọng yếu: Logistics lv1, Logistics lv2, Tài chính lv1, Sản xuất lv1
Thành quả chính: 108 cửa hàng | 30 nhà máy (16.400m²)| 3 nhà hàng | dây chuyền thép Hải Phòng | xi măng | điện tử (yield 92%) | 300 máy điện thoại 98-01 | OKI-200 | 3 container xuất khẩu
Ghi chú: sổ cái khớp system_ledger — không double-book
============================================================

Cảng Đà Nẵng sáng đèn. Những container tiếp theo sẽ đi xa hơn. Còn đêm nay, Phần 3 khép lại bằng một bát cơm nguội và một câu hỏi: Mai còn mở cửa được không?
"""

# ============================================================
# CHƯƠNG 113
# ============================================================
ch113 = """\
============================================================
Chương 113: Mở nhà máy USA
============================================================

Tháng Mười Một, 1987. Chicago.

Hùng đứng trên khu đất trống, giày lún trong bùn đông cứng. Ba nghìn hai trăm mét vuông — con số đã nhẩm trong đầu suốt bốn tháng. Gió từ hồ Michigan thổi vào mặt như dao cạo, mang theo mùi nước lạnh và tuyết xa. Ông nhắm mắt, cố hình dung dây chuyền, tiếng máy, ánh đèn. Lúc này chưa có gì — chỉ bùn, cỏ dại, và tấm biển FOR SALE đã bạc màu vì mưa.

Bên cạnh ông, Brad Hawkins — cựu lính Thủy quân lục chiến từng đóng quân ở Đà Nẵng năm 1970 — đang hút thuốc. Brad nói tiếng Việt đủ để chửi thề và đủ để im lặng đúng lúc. Hùng trả lương Brad cao hơn mặt bằng ba mươi phần trăm không phải vì thiện chí — vì Brad sẽ đứng trước hội đồng thành phố mà nói: Đây là việc làm cho con em chúng ta, không phải nỗi sợ của chúng ta.

— Tháng sau tôi muốn thấy móng — Hùng nói.

Brad nhìn ông, không cười. — Ông nghiêm túc hơn tôi tưởng.

Ba lô đất đầu tiên rụng vì lý do không ai đoán trước. Một cái dính vùng đất ngập nước theo mùa — luật liên bang cấm xây. Một cái nằm cạnh đường ống dẫn dầu cũ không ai khai báo. Một cái thì dân địa phương ký đơn phản đối vì "tiếng ồn từ nhà máy châu Á" — dù chưa có nhà máy nào. Hùng không nổi nóng. Ông ghi vào sổ: Chống đối không phải vì lý do — vì chưa từng thấy.

Bốn tháng trước đó, Hùng đã ngồi với luật sư Richard Feldman — người Do Thái gầy, mắt xám, hỏi từng câu như công tố viên — suốt hai tuần để hiểu zoning variance, environmental impact waiver, union jurisdiction clause. Feldman nói: Ông không mua đất. Ông mua giấy phép. Đất chỉ là cái giá treo.

Hùng ghi từng chữ. Lần đầu tiên trong đời, ông thấy nước Mỹ vận hành — qua một hợp đồng dày hai mươi trang, mỗi trang bốn năm thuật ngữ không biết. Ông gạch dưới, dò từ điển, gọi cho người bạn du học, hỏi từng chữ. Nhiều đêm ông ngủ gục trên bàn, đầu gối lên tập hợp đồng. Sáng dậy, mặt in chữ "arbitration".

#

Bây giờ ông đứng giữa dây chuyền lắp ráp đầu tiên. Ba nghìn hai mét vuông — sàn bê tông đánh bóng, trần cao sáu mét, đèn huỳnh quang trắng gắt hắt lên từng góc nhỏ, tiếng máy nén khí thở phì phò từ cuối xưởng. Một phần ba diện tích còn trống, chờ lô máy chưa qua hải quan từ Hamburg.

Sáu tuần đàm phán với nhà cung cấp Đức qua ba phiên dịch. Một lần suýt mất hợp đồng vì ngân hàng Mỹ không chấp nhận thư tín dụng từ Việt Nam. Một chuyến bay cuống cuồng sang Frankfurt để ngồi trực tiếp với giám đốc xuất khẩu — Schmitt — người Đức không cười, không bắt tay. Schmitt chỉ gật một cái duy nhất khi Hùng nói: Tôi trả tiền mặt, toàn bộ, trước khi giao hàng.

Hùng hiểu: ở Mỹ, thời gian là tiền. Ở Đức, chữ tín là thép. Ở Việt Nam, cả hai đều phải tự kiếm.

#

Số lượng đặt: ba nghìn sản phẩm cho lô đầu. Hơn một trăm nghìn USD tiền vật tư chưa kể nhân công. Nếu lô đầu lỗi, ông mất không chỉ tiền — mất cửa vào thị trường Mỹ.

Hùng nói với bà Hà trong bếp tối hôm quyết định: — Anh không thể về Việt Nam nói "thử rồi mà không được". Em biết họ chờ mình thất bại.

Bà Hà không khuyên. Bà hỏi: — Thiếu bao nhiêu?

Hùng nói con số. Bà im lặng một lúc, đứng dậy, mở tủ lấy một phong bì đã chuẩn bị sẵn — toàn bộ số tiền tiết kiệm riêng từ mười lăm năm dạy học. Hùng không nói gì. Ông chỉ cầm phong bì, để lên bàn thờ tổ tiên đêm đó, thắp một nén hương.

#

Ông hỏi người thợ già nhất — Wojtek Kowalski, năm mươi tám tuổi, người Mỹ gốc Ba Lan, ba mươi năm làm nhà máy ô tô Detroit — chỗ nào hay hỏng nhất.

Wojtek không trả lời ngay. Ông ta đi dọc băng tải, gõ từng khớp nối bằng ngón tay cái, lắng nghe âm thanh như bác sĩ gõ ngực bệnh nhân. Đến khớp thứ bảy, ông ta dừng.

— Here. Thiết kế không tính đến độ rung thực tế. Rung ba tháng là nứt. Tụi Đức vẽ đẹp, nhưng không bao giờ chạy thực tế đủ lâu.

Hùng ghi vào sổ, không cãi một câu. Wojtek nói để được làm. Hùng nhận ra sự khác biệt ngay từ tuần đầu tiên tuyển người: công nhân Mỹ không thích bị dạy, nhưng họ tôn trọng người biết lắng nghe. Ông bảo Wojtek đứng đầu tổ bảo trì. Lương thêm ba trăm đô một tháng, quyền tự động thay phụ tùng mà không cần xin phép. Wojtek không nói "cảm ơn" — nhưng từ hôm sau, ông ta có mặt sớm nhất, về trễ nhất.

Hùng hiểu: lòng trung thành ở Mỹ không mua bằng tiền — mua bằng việc được tin tưởng.

#

Mẫu thử đầu tiên nằm trên bàn giữa phân xưởng — một cụm cơ khí cỡ trung, sơn tĩnh điện màu xám nhạt, hai mươi hai chi tiết lắp ráp. Klaus Weber, kỹ sư Đức ba mươi tư tuổi ông đưa từ Việt Nam sang, cầm thước cặp đo từng mép. Klaus có thói quen lắc đầu trước khi nói — hai lần lắc nhẹ, nhíu mày, rồi nói. Ông ta lắc hai lần trước khi gật một lần.

Hùng không hỏi "có ổn không" — ông hỏi "chỗ nào sẽ hỏng trong sáu tháng đầu". Klaus chỉ ba điểm. Khớp chịu lực chính. Mối hàn trên khung đỡ. Lớp sơn tĩnh điện.

Hùng ghi cả ba. Cuộc họp kéo dài thêm bốn mươi lăm phút — đáng giá hơn ba tháng sửa lỗi sau này.

Giữa buổi, điện thoại từ Sài Gòn — lô phụ tùng linh kiện bị đứt đoạn, tàu trễ cảng vì bão biển Đông. Chuỗi cung ứng chưa kịp nối đã đứt. Hùng không nóng, không chửi. Ông rút bản phương án B đặt sẵn trong cặp — một phong bì màu nâu, viết chữ "Backup — Texas" — đưa cho trợ lý: chuyển qua nhà cung ứng dự phòng ở Houston. Giá cao hơn mười lăm phần trăm. Vận chuyển đường bộ thêm ba ngày. Nhưng không làm chậm ca chạy thử.

#

Hai giờ chiều, tin đối thủ — một công ty Ohio — giảm giá mười phần trăm. Cả phòng im lặng. Ba mươi bảy giây.

Hùng không ngẩng mặt khỏi bản vẽ. Giọng bình thản: — Giảm bằng cắt chất lượng thì để họ giảm. Mình giữ hàng.

Derek — thợ trẻ — lên tiếng. Hùng ngước lên: — Cậu từng mua thứ rẻ nhất chưa? Tôi từng. Và tôi đã trả giá lại hai lần. Một lần khi nó hỏng, một lần khi tôi mua cái thay thế.

#

Buổi chiều, Hùng dành một tiếng đi vòng xưởng. Chiến thuật học từ quản lý nhà máy đầu tiên ở Sài Gòn: sự hiện diện của người đứng đầu, nếu đúng liều, hiệu quả hơn một cuộc họp. Một lần mỗi ca, đi chậm, không nói nhiều, gật đầu với người đang làm.

Ông nhận ra người Mỹ cần biết "tại sao" trước khi làm. Người Việt của ông nhận lệnh là làm. Người Mỹ muốn hiểu lý do. Nếu không hiểu, họ làm miễn cưỡng, chất lượng tụt. Ông dành mười lăm phút mỗi sáng giải thích cái gì, tại sao, cho ai.

#

Về căn nhà thuê cách xưởng mười lăm phút. Bà Hà hỏi "ăn chưa" trước khi hỏi doanh thu — câu hỏi duy nhất bà chưa bao giờ quên. Mâm cơm canh rau, cá kho, thịt luộc. Hùng kể chuyện nhà máy. Derek hỏi về giảm giá. Wojtek gõ từng khớp nối. Klaus nhại giọng Hùng — cả xưởng cười.

Không biến bàn ăn thành phòng họp.

#

Trước khi ngủ, ông viết sổ tay. Thu, chi, nợ lời, nợ người. Một người thợ vừa hỏi vay tạm ứng vì con ốm. Một người cần giấy bảo lãnh vợ sang Mỹ. Những món nợ không ghi trong sổ sách — nhưng nếu không trả, nhà máy đứng trên nền cát.

Đêm đó, Hùng nằm nghe tiếng gió. Ngoài kia, tuyết bắt đầu rơi.

Sáng hôm sau, đúng bảy giờ, ca chạy thử thứ hai bắt đầu. Tiếng máy nổ. Băng tải lăn. Sáu giờ liên tục. Sản phẩm thứ một trăm linh hai qua trạm kiểm tra. Klaus giơ ngón cái từ cuối xưởng.

Không pháo hoa. Chỉ tiếng máy chạy đều hơn.

Giữa ca, Brad gọi: — Hội đồng thành phố muốn tổ chức giới thiệu nhà máy. Mời báo chí. Mời thị trưởng.

— Tuần sau. Để chạy xong lô thử. Không mang cái chưa hoàn thiện ra mắt thiên hạ.

"""
ch113 += """\

============================================================
「Hệ thống — GHI NHẬN ch.113」
Năm: 1987
Tổng EXP: 18,083
Không gian kho: 5,917m²
Kỹ năng trọng yếu: Tài chính lv1, Tài chính lv2, Giáo dục lv1
Ghi chú: sổ cái khớp system_ledger — không double-book
============================================================

Ba tuần. Một nhà máy. Một lô thử. Phần thưởng chỉ thật khi nhà vẫn muốn ông về.
"""

# ============================================================
# CHƯƠNG 114
# ============================================================
ch114 = """\
============================================================
Chương 114: M&A Stahl GmbH
============================================================

Sáng tháng Mười Một năm 1987, Hà Nội.

Cái rét đầu mùa chưa kịp xuống hết đã bị nắng xé ra từng mảng trên phố. Hùng đứng trước dãy nhà cấp bốn đã được sửa lại thành một văn phòng nhỏ — mái ngói đỏ cũ, tường quét vôi trắng, cửa sắt xanh đã bạc. Một cái bảng nhỏ bằng tôn sơn trắng, chữ xanh viết tay: M&A Stahl GmbH. Không đèn led. Không logo thiết kế. Không biển hiệu quảng cáo.

Trong lòng Hùng, cái bảng đó nặng hơn bất kỳ quảng cáo nào từng thấy ở Sài Gòn trước giải phóng.

Ông đứng ngoài cổng năm phút. Đủ để nhìn lại những gì đã đưa mình đến đây. Đất nước vừa mở cửa chưa bao lâu — Đổi Mới bắt đầu từ tháng Chạp năm ngoái nhưng phải tới năm 1987 mới thấm vào lớp thịt của nền kinh tế. Hợp tác xã kiểu cũ đang chết dần. Cơ chế hai giá — giá nhà nước và giá thị trường — vẫn còn, tạo ra một không gian xám màu mỡ cho người biết đi nhưng nguy hiểm cho người bước hụt.

M&A Stahl GmbH không phải một công ty to. Nó là một trạm trung chuyển thép. Nhập thép cuộn từ Nhật và Đức qua trung gian, cắt theo yêu cầu, phân phối lại cho các xưởng cơ khí nhỏ quanh Hà Nội và Hải Phòng. Vốn liếng — vay từ bà con, gom từ mấy lô hàng xoay vòng. Không ngân hàng. Hồ sơ thành lập doanh nghiệp tư nhân chỉ mới được phép từ năm ngoái — M&A Stahl GmbH nằm trong số những tờ khai đầu tiên ở Hà Nội, viết bằng bút bi trên mẫu giấy của UBND thành phố.

Cán bộ huyện nhìn tờ khai với đôi mắt dò xét. Một doanh nghiệp tư nhân chuyên thép? Họ hỏi năm lần: Anh chắc? Anh biết luật chưa? Anh có bảo lãnh? Hùng trả lời từng câu bằng số liệu và bằng chữ ký của ba người bảo lãnh — tất cả đều là người có nhà, có đất, có họ hàng trong cơ quan. Ông không nói dối. Ông cũng không nói hết.

#

Bên trong văn phòng, Trần Thị Lan đã có mặt từ sớm. Chị quét nền, đốt bếp than nhỏ để ấm nước. Trên chiếc bàn gỗ tạp không sơn, năm bộ hồ sơ được xếp thành một hàng. Một quyển sổ cái, một cây bút mực xanh, một cây bút đỏ cho lỗi. Chị đánh dấu từng mục bằng tay: nhập, xuất, tồn, tiền mặt, nợ phải thu.

— Mấy hồ sơ này — chị nói, đẩy chồng giấy mỏng về phía Hùng. — Của lô thép số ba. Tàu về Hải Phòng ngày mười bảy. Nhưng giấy tờ từ Nhật mới tới hôm qua, thiếu chữ ký của đại diện hãng.

Hùng cầm tập giấy lên. Mùi mực in từ máy roneo còn thoảng. Ông lật từng trang — chứng từ gốc, vận đơn, danh sách kiện hàng, biên bản giám định sơ bộ. Thiếu một chữ ký. Một cái tên. Nhưng với Hùng, thiếu một chữ ký là thiếu một cửa thoát nạn khi có chuyện.

— Ai đứng ra nhận tàu?

— Tanaka-san từ Nhật qua. Ông ấy đang ở khách sạn Thắng Lợi.

Hùng không đợi chiều. Ông bảo Lan gọi điện — cái điện thoại quay số duy nhất của văn phòng, nối qua tổng đài huyện, chờ tới mười lăm phút mới có đường dây — hẹn Tanaka ra quán cà phê đầu phố. Không phải vì vội, mà vì Hùng muốn gặp mặt trước khi giấy tờ chạm tay. Ở thời kỳ chuyển tiếp này, uy tín không nằm trong hợp đồng — nó nằm trong ánh mắt và cách bắt tay.

#

Quán cà phê đầu phố là một cái bạt xanh cũ kéo trên mấy cây sắt, bàn nhựa ghế nhựa. Tanaka-san đến đúng hẹn — mặc vest xám, không cà vạt, tay cầm cặp da đã cũ. Ông ngồi xuống, gọi cà phê đen, không đường. Hùng cũng gọi cà phê đen.

Họ nói chuyện quanh lô thép. Tanaka giải thích: lô thép số ba xuất xưởng từ Nhật tháng Tám, qua Đức gia công thêm lớp mạ, sau đó mới lên tàu về Việt Nam. Giấy tờ bị tách làm ba lần — xuất Nhật, nhập Đức, tái xuất. Mỗi lần đều cần chữ ký. Chữ ký cuối cùng của bên Đức thất lạc do văn phòng ở Hamburg gửi thiếu.

Hùng nghe. Không ngắt. Chỉ gật và ghi vài dòng vào cuốn sổ nhỏ mang theo. Sau khi Tanaka nói xong, Hùng hỏi một câu mà Tanaka không ngờ tới:

— Nếu lô này lỗi, ai chịu?

Tanaka nhướng mày. — Hàng Nhật, kiểm tra nhà máy. Rất khó lỗi.

— Tôi biết. Nhưng nếu lỗi — ai chịu? Lỗi khi vận chuyển? Lỗi lớp mạ? Lỗi tờ khai hải quan? Mỗi chỗ đều có người chịu — tôi chỉ muốn biết tên.

Tanaka im lặng. Ở một nơi mà luật pháp vừa được viết lại, người ta cần biết ai sẽ đứng ra trước khi có thể ngủ yên.

— Tôi — Tanaka nói cuối cùng. — Tôi đứng cho giấy tờ. Hãng bảo hiểm đứng cho hàng. Anh chỉ đứng cho khâu thanh toán và phân phối.

Hùng gật, rút từ cặp một bản cam kết viết tay, hai trang, soạn tối qua. — Vậy ký chỗ này. Để cả hai cùng nhớ.

Không giận. Không ngại. Tanaka đọc lướt, rút bút, ký.

Hai người uống hết cốc cà phê. Chỉ có lịch giao: mười chín tháng Mười Một, cảng Hải Phòng, lô thép số ba. Nếu đúng hạn, bắt đầu lô số bốn.

#

Trở về văn phòng, Trần Thị Lan đã đun xong ấm nước. Hùng kể lại cuộc gặp. Lan gạch một dòng trong checklist, đánh dấu "ĐÃ KÝ" bằng bút đỏ. Nhưng hôm nay có việc khác. Trong lúc Hùng đi, một người phụ nữ đã đến — bà Nguyễn Thị Hà, trạc bốn mươi, đại diện một tổ dệt nhỏ ở Hà Đông. Họ cần thép tấm ba ly, nửa tấn, trả một nửa bằng tiền mặt, một nửa bằng hàng đổi hàng.

Hùng đọc mảnh giấy Lan đưa, không nói gì. Hàng đổi hàng là thời kỳ quá độ. Người ta chưa tin vào tiền — lạm phát năm 1987 ở mức ba, bốn trăm phần trăm. Ai cầm tiền mặt qua đêm là mất một phần.

— Chị có hẹn chưa?

— Bà ấy nói quay lại bốn giờ.

Còn năm tiếng. Đủ để suy nghĩ.

#

Bốn giờ chiều, bà Nguyễn Thị Hà đến đúng hẹn. Áo nâu, quần đen, dép nhựa — một người phụ nữ làm bằng tay, bằng mắt, bằng kinh nghiệm. Bà mang theo một tấm vải mẫu — vải chàm dày, dệt tay, nhuộm bằng lá — và một tập giấy ghi chép bằng bút chì viết nắn nót.

Bà ngồi xuống ghế nhựa trước bàn Hùng, đặt mẫu vải lên mặt bàn.

— Tôi có tổ dệt, bảy người. Cần thép để làm khung máy dệt. Máy cũ hỏng hết, sửa bằng sắt vụn không chịu nổi.

— Thép từ Nhật, qua Đức. Chất lượng kiểm tra được. Giá cao hơn hàng Trung Quốc ba mươi phần trăm.

— Tôi biết. Hàng rẻ hỏng ba tháng, hàng tốt dùng được mười năm. Tôi không tính theo tháng, tôi tính theo năm.

— Thanh toán. Chị muốn đổi hàng?

Bà Hà đặt tay lên tấm vải. — Vải này. Chàm dày, dệt tay. Bảy nghìn đồng một mét, chợ Đồng Xuân săn đón. Tôi trả bằng vải hai phần ba số thép. Một phần ba tiền mặt.

— Tôi không cần vải.

— Anh không cần. Nhưng anh có người quen cần — bà Hà nói, không nao núng. — Nhà buôn giỏi biết thanh toán bằng hàng người khác cần hơn đòi tiền mất giá.

Hùng im, mân mê tấm vải. Bà nói đúng. Ở Thái Nguyên có xưởng may hỏi vải tốt tuần trước.

— Để tôi kiểm. Chiều mai trả lời.

Bà Hà gật, không nài nỉ, đứng dậy. Hùng giơ tay: — Vải để lại.

Bà cười lần đầu trong buổi gặp — nụ cười người biết mình gần tới đích.

#

Sau khi bà đi, Lan mang trà nóng ra. Đợi Hùng tàn thuốc:

— Em nghĩ bà ấy tin được.

— Sao em biết?

— Không nói quá. Cho mượn vải mẫu không sợ mất. Người làm ăn biết mình bỏ ra cái gì.

— Đánh giá thử xem lời bao nhiêu nếu đổi một nửa.

Lan mở sổ, tính mười lăm phút bằng tay. Một trang đầy số. Cuối cùng: — Với gần nửa trả vải, mình lời ít hơn bán tiền mặt tám phần trăm. Nhưng bà ấy trả một phần ba tiền mặt, đủ xoay vòng. Và vải có thể bán lại Thái Nguyên.

— Được. Nhưng thêm một điều — cắt thử một mét, đưa Tanaka xem. Nếu đủ tốt xuất khẩu, đổi nhiều hơn.

"""

ch114 += """\

============================================================
「Hệ thống — GHI NHẬN ch.114」
Năm: 1987
Tổng EXP: 18,167
Không gian kho: 5,933m²
Kỹ năng trọng yếu: Tài chính lv1, Tài chính lv2, Giáo dục lv1
Ghi chú: sổ cái khớp system_ledger — không double-book
============================================================

Lô thép ba đã vào cảng. Một sợi dây đang nối giữa Nhật, Đức, và một tổ dệt Hà Đông — nối bằng chữ ký tay, không in sẵn.
"""

# ============================================================
# CHƯƠNG 115
# ============================================================
ch115 = """\
============================================================
Chương 115: Mở nhà máy Nigeria
============================================================

Lagos, Nigeria — tháng Ba, 1987.

Không trải thảm đỏ. Chỉ có việc, người, và cái nóng.

Mảnh đất mua từ năm ngoái giờ dựng xưởng. Hàng rào thép gai chưa kịp sơn. Mái tôn mới phản xạ nắng chói đến mức không dám nhìn thẳng. Trên bản vẽ, nó là "giai đoạn 1 — công suất 3000 tấn/năm". Trên thực tế, nó là một cái xác nhà máy đang cố thở giữa một đất nước mà mọi thứ đều muốn ngăn nó thở.

Hùng đứng ở cửa chính từ sáu giờ sáng, tay cầm tập bản vẽ đã gập góc. Bụi đỏ Nigeria — thứ bụi laterit mịn như bột mì nhưng dai như keo — bám vào ống quần, vào cổ áo, vào khóe mắt. Ông không nói gì với ai, chỉ nhìn. Dây chuyền nhập từ Nhật về, tháo kiện hôm qua. Dầu máy mới còn thơm, mùi sơn công nghiệp hăng hắc, nhưng mồ hôi công nhân địa phương đã kịp phủ lên tất cả một lớp người. Trên nền xi măng còn dấu giày đủ loại: dép cao su, giày bata, sandal thủng quai, một đôi giày tây từ chợ Balogun.

Trần Thị Lan đi cạnh ông, tay trái sổ đen, tay phải bút bi. Bà ghi nhanh — không thêm, không bớt. Máy số 3 kêu lạ, tiếng lạch cạch. Con dấu sở cảnh sát chưa đóng. Ba thợ đứng chờ góc xưởng D — nhìn nhau, nhìn đồng hồ, nhìn trần.

— Người đâu?

— Hai thợ hàn ốm. Một thợ điện xin giấy phép Eti-Osa chưa về. Thằng nhỏ bị kẹt trạm thu phí.

— Cân nặng? Xe không mười tấn.

— Cân nặng của tờ tiền. Tài xế chưa bôi trơn trạm.

Hùng gật. Nigeria mà.

#

Ông bước vào xưởng — không phải bước của chủ kiểm, mà của người muốn hiểu. Sàn xi măng nứt chân chim. Ống nước qua mái không bảo ôn. Ổ khóa cổng phụ một đạp là bật. Ông không la, không phê — ghi.

Xưởng rộng ba nghìn mét, lợp tôn mười hai nhịp. Sáu dãy đèn, ba có bóng. Cửa cuốn chưa hạ vì xi lanh mất dầu. Nhà vệ sinh nam hai vòi không nước.

Adeyemi — thợ già tổ lắp ráp, người Yoruba ngoài năm mươi — thấy Hùng đứng lại chỗ máy số 3. Ông ta không chào, chỉ nói, giọng khàn:

— Chỗ này hay hỏng. Tôi đã bảo bên lắp máy. Họ bảo "sẽ xem". Không ai xem.

Hùng ghi vào sổ: tiếng lạ máy số 3, người báo: Adeyemi. Rồi hỏi:

— Anh làm ở đâu trước?

— Lever Brothers. Năm năm. Trước đó xưởng cưa Ikeja. Mười năm.

— Chỗ đó mà về đây?

— Chỗ đó trả lương ba tháng một lần. Ở đây ông hứa đầu tháng. Tôi tin lời hứa hơn tiền. Tiền ai cũng thiếu. Lời hứa mới biết người.

— Anh phụ trách tổ lắp ráp. Máy hỏng, báo trực tiếp.

Adeyemi không nói. Cái bắt tay — chặt, khô — là câu trả lời.

#

Nguyễn Văn Đức — kỹ thuật viên Việt mới từ Sài Gòn sang — ngồi trên nền xi măng, tay cầm căn lá. Mồ hôi nhỏ tong tong xuống bản vẽ.

— Cái khuôn — tôi canh chuẩn Nhật — nhưng nó rung — chắc bệ máy không bằng phẳng —

— Nói thẳng, đừng đệm. Khuôn sao?

— Máy rung vì chân chưa đổ móng chuẩn. Nền làm trên đất mới đắp. Khuôn số 7 chạy thử sẽ lỗi đường kính hai li, bề mặt sần. Tôi không dám chạy đại vì sợ hỏng khuôn.

— Lịch chạy thử tuần sau, nhưng — Đức phân bua.

— Lịch tôi ký. Lịch tôi phá. Anh làm đúng. Khi nào xong móng mới, báo tôi.

#

Giữa trưa, mẫu thử đặt trên bàn. Bốn mươi hai độ. Quạt treo hết cứu.

Ai khen — Hùng gật. Ai chỉ lỗi — mời ngồi gần.

Chibuzor — thanh niên Igbo QA, tự học từ quân đội — chỉ mối hàn: — Nóng chảy không đều. Chỗ dày ba li, chỗ mỏng. Khi chịu tải nứt trước.

— Thấy bao nhiêu chỗ?

— Năm trên mẫu này. Cần thử phá hủy ba mẫu.

— Làm đi. Cần gì?

— Cần máy đo độ bền kéo ở kho B. Thùng số 11. Nằm dưới đáy.

Hùng quay Lan: — Dỡ trước năm giờ. Xong chưa?

— Xong.

#

Chiều, tàu Lagos bị kẹt. Phụ tùng máy dập ở lại bãi Apapa — hải quan kiểm xong nhưng tờ khai chưa duyệt.

Đức chờ lệnh.

— Lùi lịch. Giao lỗi còn tệ hơn trễ. Mất một tháng không chết.

— Nhưng hứa với đối tác...

— Tôi gọi nói thẳng. Đức ghét nói dối hơn ghét trễ.

Năm giờ, điện tắt. Đèn xưởng vụt tắt không báo trước.

— NEPA cắt — Adeyemi nói, giọng không ngạc nhiên.

Máy phát rống sau ba phút — tập chạy tám lần, bảy thất bại. Lần thứ tám nổ.

Hùng tính: mười hai tiếng mất điện ngày. Máy phát tám tiếng, ba trăm lít dầu. Tồn hai nghìn. Gọi Lan: — Nhờ Total mở tài khoản dầu trả chậm. Không thì tìm mối thị trường.

#

Xuống xưởng. Hai mươi bảy công nhân dưới ánh đèn vàng cam. Hùng hỏi Adeyemi:

— Mệt không?

— Có. Nhưng làm được.

— Oán không?

Adeyemi lau mồ hôi: — Mai mất điện không đủ dầu thì oán.

Hùng cười: — Tôi lo dầu. Anh lo người.

Góc xưởng, phụ nữ Nigeria vừa gắn phụ kiện vừa hát. Fatima — trạc bốn mươi — nhìn ông, cười: — Ông chủ thích nhạc?

— Thích. Hát có chậm tay không?

— Chồng mất năm ngoái, năm con. Kano không việc. Ở đây có. Biết ơn.

Emeka — hai ba tuổi — dũa tay dưới đèn. Hùng hỏi: — Sao không dùng máy?

— Máy chạy điện. Cha tôi dạy: tay dũa được thì mắt tự sửa.

— Từ mai phụ trách tổ sửa nguội. Lương thêm mười phần trăm.

#

Tối, căn nhà thuê gần xưởng. Bà Hà hỏi ăn chưa. Mâm cơm cá kho tộ, thịt sả ớt, canh rau muống trồng thùng xốp — hạt giống từ Sài Gòn.

— Mẹ có xuống xưởng?

— Xuống, chỉ mấy chị cách trồng rau. Vui lắm. Lạ mà vui.

Trước ngủ, Hùng mở sổ dưới đèn dầu. Viết: Thu chi. Phương án B — đường bộ Cotonou nhập lậu. Phương án C — Halogen Security. Phương án D — chuyển USD nếu Naira mất giá.

Cuối trang: Hôm nay có ai bị bỏ lại không?

Tự trả lời: Chibuzor không. Adeyemi không. Emeka không. Fatima không.

Ngày đầu tiên của nhà máy Nigeria. Không pháo hoa. Một tờ sổ, một lời hứa, một câu hỏi: mai mở cửa được không?

"""
ch115 += """\

============================================================
「Hệ thống — GHI NHẬN ch.115」
Năm: 1987
Tổng EXP: 18,250
Không gian kho: 5,950m²
Kỹ năng trọng yếu: Tài chính lv1, Tài chính lv2, Giáo dục lv1
Ghi chú: sổ cái khớp system_ledger — không double-book
============================================================

Còn hỏi được là còn sống. Ngày mai dầu diesel phải đủ, móng máy phải khô, và bà Fatima sẽ lại hát.
"""

# ============================================================
# CHƯƠNG 116
# ============================================================
ch116 = """\
============================================================
Chương 116: Mở nhà máy Úc
============================================================

Tháng Ba 1987. Sydney.

Chuyến bay từ Sài Gòn qua Singapore rồi Sydney kéo dài mười bốn tiếng. Hùng ngồi khoang phổ thông, tập bản vẽ và sổ tay trên bụng, ngủ được ba tiếng lẻ. Xuống sân bay Kingsford Smith, cái lạnh khác — khô và sắc, không giống ẩm thấp Sài Gòn. Trên đường từ sân bay về khu công nghiệp phía tây, ông nhìn qua cửa kính taxi: đường cao tốc rộng, xe tải chạy bên trái, biển quảng cáo tiếng Anh dựng dọc lối ra. Một thế giới khác.

Trần Thị Lan ngồi cạnh, ghi vào sổ: Ngày 12 tháng 3, 9h sáng, 22 độ C, Sydney. Trời trong. Từ sân bay về factory 45 phút. Rộng, sạch, khác bản vẽ.

#

Sáu nghìn mét vuông nhà xưởng. Con số trên giấy là một chuyện; đứng giữa nó là chuyện khác.

Hùng bước qua cửa cuốn còn xếp nếp, giày bảo hộ mới dán nhãn còn nguyên. Dưới chân ông — nền bê tông đánh bóng, màu xám nhạt mịn. Phía trên — dàn đèn huỳnh quang trải dài như những đường kẻ song song vô tận. Mái cao tám mét, kèo thép sơn trắng.

Mùi: sơn công nghiệp khô chưa hết, dầu nhờn máy móc, bụi xi măng lắng đọng.

Khung nhà xưởng được dựng bởi một nhà thầu địa phương tên Ronan — người Ireland gốc, ba mươi năm trong nghề. Ronan đứng cạnh cửa, tay cầm ca cà phê đen, nhìn Hùng lặng lẽ đi vòng quanh sàn. Mười lăm phút sau, Ronan mới nói:

— You walked the whole floor before you shook my hand. That's a first.

— If it breaks, my name's on it.

Ronan gật, không nói thêm.

#

Dây chuyền sản xuất — nhập từ Nhật qua Melbourne — được đặt trên bệ bê tông đúc sẵn. Bốn máy dập thủy lực, hai máy cắt CNC, ba băng tải lắp ráp, hệ thống hút bụi trung tâm, phòng kiểm định kính cường lực ở góc tây nam. Thiết bị đến cảng Sydney ngày 5 tháng 3, thông quan mất ba ngày. Còn thiếu bảy đầu cắt dự phòng.

Xưởng chia ba khu rõ rệt: tiếp nhận nguyên liệu và gia công thô phía bắc, lắp ráp tinh trung tâm, đóng gói kiểm định phía nam sát cửa xuất. Mỗi khu vạch sơn vàng rộng mười phân.

Hùng hỏi Geoff — người thợ già nhất, sáu mươi hai tuổi, người Anh di cư, bốn mươi năm trong nghề. Geoff đang nằm dưới gầm máy dập số hai. Hùng ngồi xuống cạnh, mượn cờ-lê, tự vặn thử.

— Where's it break first?

— Number two press. The hydraulic seal. They cheap out on the rubber. Three months, maybe four — she weeps. Six months — ram seizes.

Hùng ghi vào sổ bằng tiếng Việt. — Can you fix it?

— Get the seals. Aftermarket.

— Order. Copy to Miss Trần.

Geoff gật — lần đầu trong sáng.

#

Mẫu thử đầu tiên đặt trên bàn — cụm cơ khí bốn mươi kilôgam, sơn tĩnh điện xám. Mười người tụ quanh. Hùng không ngồi — ông đứng, tay đặt trên sổ.

— Who sees a problem?

Phong — kỹ sư trưởng người Việt từ Đức — chỉ mối hàn ở góc đông bắc. — Thiếu hai li ở góc. Rung ba tháng nứt.

— Sửa được?

— Cắt lại, hàn đủ. Thêm một ngày rưỡi.

Hùng nhìn James Henderson — đối tác phân phối Úc. — Shipment delays one and a half days. Problem?

— Our warehouse can absorb two days. This once.

— You'll have quality cert from today.

#

Mười một giờ, một chiếc Holden Commodore trắng đậu trước cổng. Thanh tra lao động — Margaret Chen, người Úc gốc Hoa. Không báo trước. Hùng tự ra đón.

Bà Chen kiểm biển báo an toàn, hồ sơ đào tạo, hệ thống chữa cháy, lối thoát hiểm. Phòng nhân sự, Lan mở tủ, mười hai bộ hồ sơ song ngữ — ảnh, điện thoại khẩn cấp, chữ ký đọc nội quy.

— Your file system is better than half the factories I've seen. Who set this up?

— My wife.

— Conditional pass. Air compressor room vented by Friday. Send photos.

— Friday morning.

Bốn mươi bảy phút.

#

Chiều, vấn đề thật. Phụ tùng Nhật — ba mươi phần trăm ống dẫn thủy lực sai kích thước. 10mm thay 12mm. Họ gửi lại mất mười ngày.

Hùng nhìn Geoff: — Can we ream?

— Wall thin. Not safe past 80 bar. Lines run 120.

— Alternative?

— German 12mm. Stronger. Need adapters. Two days each.

— Six adapters. Twelve days.

Hùng im, mười nhịp thở. Quay Lan: — Tìm nhà cung ứng trăm cây số.

Ba cuộc gọi. Thứ nhất không có. Thứ hai không đúng ren. Thứ ba — xưởng Wollongong, Ivan người Croatia. Adapter thép không gỉ, giao hai ngày.

— Đặt.

#

Bảy giờ tối, ca chiều tan. Sáu nghìn mét vuông chìm trong đèn vàng cam. Hùng đứng lối ra, nhìn công nhân về. Geoff lên ute bạc. Hai kỹ thuật Philippines đi chung. Một nhóm công nhân địa phương ra bến xe.

Mệt — thấy. Oán — chưa.

Ông đi vòng cuối một mình. Góc tối máy dập, bảng điện phụ phía tây, phòng vệ sinh. Sàn ướt — vòi rỉ. Ghi vào sổ.

#

Nhà thuê Cabramatta. Khu phố có tiệm vàng Việt, tiệm phở, chùa nhỏ trong hẻm. Bà Hà trong bếp — canh chua, cá basa chiên, rau muống. Giá gấp ba Sài Gòn, nhưng có đủ.

— Ăn chưa? — câu đầu tiên.

Hùng kể chuyện: thanh tra gốc Hoa, Ivan Croatia, Geoff sáu mươi vặn bu-lông.

#

Chín giờ, Lan trước laptop Toshiba T1100 — màn hình xanh đen, gõ báo cáo. Lưu ổ mềm. In hai bản. Cô thử chương trình Peachtree trên DOS: "Nhập hàng Nhật — $12,500. Ivan adapter — $1,870." Máy tự cộng.

Hùng: — Về Sài Gòn mua một bộ.

— Bản quyền đắt. Nhưng chắc hơn tính tay.

#

Trước ngủ, Hùng mở sổ.

Thu: 0. Chi: adapter $1,870, lương $4,200, nguyên liệu $12,500.

Phương án B: không có. Ivan phải kịp.

Cuối trang: Hôm nay có ai bị bỏ lại không?

Ba giờ sáng, ông thức, viết thêm: Nói Phong — kiểm định trước sản xuất. Nói Geoff — đào tạo hai thợ Việt trẻ.

Ký tên.

Năm 1987. Úc. Sáu nghìn mét vuông. Không pháo hoa. Một cuốn sổ. Một người dám đứng ra.

"""
ch116 += """\

============================================================
「Hệ thống — GHI NHẬN ch.116」
Năm: 1987
Tổng EXP: 18,416
Không gian kho: 6,000m²
Kỹ năng trọng yếu: Tài chính lv1, Tài chính lv2, Giáo dục lv1, Quản lý lv1
Ghi chú: sổ cái khớp system_ledger — không double-book
============================================================

Adapter của Ivan đến sân bay sáng mai. Geoff lắp trước một giờ. Đèn Cabramatta tắt. Một ngày nữa bắt đầu.
"""

# ============================================================
# WRITE ALL FILES & CHECK
# ============================================================
write_chapter("Chương 111 - Mở sang châu Mỹ USA.txt", ch111)
write_chapter("Chương 112 - Hoàn thành phần 3.txt", ch112)
write_chapter("Chương 113 - Mở nhà máy USA.txt", ch113)
write_chapter("Chương 114 - M&A Stahl GmbH.txt", ch114)
write_chapter("Chương 115 - Mở nhà máy Nigeria.txt", ch115)
write_chapter("Chương 116 - Mở nhà máy Úc.txt", ch116)

print()
print("=== ALL WORD COUNTS ===")
for f in ["Chương 111 - Mở sang châu Mỹ USA.txt",
          "Chương 112 - Hoàn thành phần 3.txt",
          "Chương 113 - Mở nhà máy USA.txt",
          "Chương 114 - M&A Stahl GmbH.txt",
          "Chương 115 - Mở nhà máy Nigeria.txt",
          "Chương 116 - Mở nhà máy Úc.txt"]:
    t = open(f, encoding="utf-8").read()
    wc = len([w for w in t.split() if len(w) >= 2])
    ok = "PASS" if wc >= 3000 else "FAIL"
    print(f"  {f}: {wc} words [{ok}]")


