# -*- coding: utf-8 -*-
import os, sys, re

fpath = r'C:\Dev\XLab_MTC\Niên Đại Thương Gia\Chương 21 - Mở rộng làm giày.txt'

content = """============================================================
Chương 21: Mở rộng làm giày
============================================================

Hùng nhận lời ngay chiều người buôn miền Nam gửi thư tới, nhưng lời nhận chỉ dành cho một chuyến đi khảo sát thực tế. Sáng hôm sau, khi hòm giày G-1 còn chưa nguội mùi keo dán, anh đã leo lên chuyến tàu hỏa xình xịch vào Thành phố Hồ Chí Minh. Hành trang mang theo gồm đôi đạt, đôi lỗi, bảng tính hao hụt và lá thư giới thiệu gấp gọn trong túi áo. Anh không mang theo nhiều tiền để mua một lô hàng lớn. Chuyến này nhằm tìm câu trả lời cho ba câu hỏi sống còn: cao su có nguồn nào ổn định hơn hàng gom nhặt ngoài chợ huyện, giày vải của xưởng có chỗ tiêu thụ nào ngoài chợ quê, và nếu tăng sản lượng thì khâu nào sẽ vỡ trước?

Người mời anh là chú Ba Mẫn — một người gom dép và đồ cao su lâu năm quanh khu vực Chợ Lớn, do bà Phương ở Vinh kết nối. Ba Mẫn không có kho bãi phô trương, chỉ thuê gian nhà nhỏ sau cửa hàng, nhận tấm đế từ hai tổ ép cao su rồi chia lại cho các mối đóng dép. Hùng đến nơi vào một trưa nắng gắt, áo bám đầy bụi than tàu hỏa, nhưng vẫn cẩn thận xin mở từng bó cao su ra xem trước khi bàn giá. Tấm thứ nhất độ đàn hồi rất đều, mùi hồ dán còn thơm nhẹ trên mép. Tấm thứ hai nồng nặc mùi dầu nặng. Tấm thứ ba lẫn nhiều tạp chất hạt cứng, bẻ mạnh tay là hiện vệt trắng mép. Ánh nắng rực rỡ phương Nam đổ xuống khoảng sân nhỏ, tỏa hơi nóng ngột ngạt.

Ba Mẫn mỉm cười xòe tay bảo:
— Loại nào mà chẳng đúc ra được chiếc dép, anh Hùng lo xa quá!

Hùng nhìn thẳng vào mắt ông, ánh mắt kiên định, giọng trầm ấm:
— Nhưng không loại nào làm ra được hai chiếc của cùng một đôi giày bền đẹp chú ạ. Người đi làm đồng hay đi máy xưởng mà gặp đôi đế lệch thì đau chân cả ngày.

Anh lấy dao cắt bốn dải cao su bằng nhau, đánh dấu nguồn gốc tỉ mỉ, rồi đem ngâm nước, phơi nắng và bẻ đi bẻ lại nhiều lần trước khi đè vật nặng lên qua đêm. Kết quả, loại cao su của tổ ép ven thành phố giữ phom tốt nhất, độ dày sai lệch không quá một lát bìa mỏng. Giá loại này cao hơn hàng pha dầu nhưng vẫn rẻ hơn số cao su Hùng phải mua gom gấp ở huyện. 

Chủ tổ ép tên Hai Độ ban đầu tỏ ra cứng rắn, chỉ chịu bán mỗi lần vài chục tấm và giao tại bến hàng chứ không chịu trách nhiệm khi kiện hàng rời tay. Hùng không vội ký hợp đồng mua ngay. Anh xin mẫu đối chứng, quy định rõ cách buộc kiện, độ dày tối thiểu và yêu cầu lần sau phải kiểm tra ngẫu nhiên ba tấm trong mỗi bó. Ông Hai Độ bật cười bảo khách miền Bắc nhỏ mà lắm thủ tục. Hùng liền đặt đôi giày G-1 bị lỗi lên bàn, chỉ rõ gờ cứng dưới lót và giải thích chỉ một sơ suất nhỏ cũng đủ làm mất niềm tin của khách. Người chủ bớt cười, trầm ngâm gật đầu đồng ý giữ cho anh lô đế đủ làm bảy mươi đôi trong ba mươi ngày. Đôi tay Hai Độ vỗ nhẹ lên vai Hùng, ánh mắt khen ngợi sự tỉ mỉ của người trẻ tuổi.

Trong bốn ngày ở miền Nam, Hùng khảo sát tiếp ba đầu mối tiêu thụ. Một sạp hàng chợ chỉ ép giá mà không quan tâm cỡ số; Hùng gạch tên ngay. Một cửa hàng bán bảo hộ lao động chấp nhận lấy thử mười hai đôi nhưng yêu cầu đế chịu nước và phải dán nhãn lô bên trong. Đầu mối thứ ba chịu nhận ba mươi đôi mỗi tháng nhưng đòi gối vốn tiền hàng. Hùng thẳng thắn từ chối để vốn nằm trong tay người khác, đề nghị lô đầu giao mười đôi, thanh toán một nửa lúc nhận và phần còn lại sau một tuần. Sự minh bạch của Hùng làm người gom hàng nể phục, đồng ý giữ lại một chiếc mẫu để chào khách.

Trong bốn ngày ấy, Hùng không mua quá số mẫu có thể mang tay. Anh tỉ mỉ tính cước vận chuyển, phần hao hụt do mép tấm cao su bị lẹm, thời gian chờ hàng, rồi nhận ra nguồn cao su miền Nam chỉ thực sự rẻ khi mỗi kiện đủ lớn và được kiểm tra kỹ trước khi buộc. Xưởng hiện mới làm năm mươi đôi một lô; mua hàng cho ba trăm đôi sẽ biến giá rẻ thành vốn chết. Anh quyết định trở về mở rộng từng nấc một: lô G-2 sáu mươi đôi, thêm một người học ráp, giữ thợ Tư ở cửa kiểm soát chất lượng. Nếu lô ấy bán tốt và tỷ lệ lỗi giảm, chuyến vào Nam tiếp theo mới là chuyến thu mua sâu, có hợp đồng vận chuyển, tiền đặt cọc và khảo sát cả da thuộc cho các mặt hàng cao cấp sau này.

Khi Hùng về tới nhà, Lan đã nhận đủ phản hồi của mười đôi bán thử. Anh trải mẫu cao su của Hai Độ cạnh đế G-1, kể rõ mối nào chịu thử hàng, mối nào chỉ muốn ép giá, rồi mới mở cuộc bàn về G-2. Lan mở ngay trang sổ mới, nắn nót viết hai chữ "G-2". Cô nhìn Hùng với ánh mắt tin tưởng nhưng không khỏi lo âu, nụ cười thoáng hiện rồi vụt tắt khi đối chiếu sổ sách. Năm mươi đôi G-1 bán ra chợ huyện đã thu về nhiều phản hồi. Tám đôi bán tốt, hai đôi còn lại bị chê giá cao. Đặc biệt có một người khách mang trả đôi G1-17 vì đi bị đau gót trái.

Thợ Tư — người thợ già giàu kinh nghiệm — đeo chiếc kính lão nheo mắt nhìn đôi G1-17. Mép đế vẫn bám chắc, nhưng phần cổ gót bên trái cứng hơn bên phải. Thợ Tư luồn ngón tay chai sạn vào bên trong lót giày, nét mặt trầm xuống, nhịp thở sâu đầy trăn trở:
— Lúc sửa đường chỉ lỏng, thợ quét thêm keo. Keo ngấm vào vải lót, khô lại thành cái gờ cứng cọ vào chân người ta.

Lan nhanh tay ghi thêm một dòng chữ đỏ vào sổ quy trình: "Hàng đã qua sửa chữa phải rà soát toàn bộ lót trong, bẻ thử đế và mang thử vào chân trước khi xuất xưởng." Hùng mỉm cười gật đầu, lập tức hoàn tiền cho khách, đổi đôi mới và giữ đôi G1-17 làm mẫu lỗi để cả xưởng rút kinh nghiệm. Ánh mắt Hùng nghiêm túc dặn dò cả nhóm thợ.

Hùng quay sang nhìn thợ Tư, chau mày hỏi:
— Nếu lô G-2 mình nâng lên sáu mươi đôi và chuẩn bị làm sáu mươi đôi nữa, khâu nào sẽ gãy trước hả bác?

Thợ Tư thở dài ra một tiếng, đôi tay siết nhẹ mép bàn gỗ:
— Khâu người! Một mình lão ráp và kiểm năm mươi đôi thì được, chứ nâng lên hàng trăm đôi mà trông cả vào hai bàn tay lão thì rã mồ hôi. Hoặc là trễ hạn, hoặc là lão nhìn sót lỗi.

Hùng quyết định không tăng sản lượng đột ngột. Ông chốt lô G-2 ở mức sáu mươi đôi, đồng thời bắt tay vào đào tạo người ráp thứ hai. Cô Tý tiến cử em trai mình tên Hòa — một thanh niên hai mươi tuổi từng phụ việc ở tiệm sửa xe đạp, tay chân nhanh nhẹn nhưng tính tình hơi bộp chộp. Ánh mắt Hòa lộ rõ sự sốc xếch bối rối khi đứng trước xưởng may ngăn nắp.

Buổi chiều hôm đó, Hòa đến xưởng trên chiếc xe đạp tàng tàng. Thợ Tư không hỏi chuyện thù lao, chỉ đưa cho cậu miếng vải bạt, cuộn chỉ sáp và chiếc dùi nhọn. Giọng thợ Tư nghiêm nghị nhưng ấm áp:
— Cậu xỏ qua mười hai lỗ này cho lão. Không cần vội, hai mặt chỉ phải đều tăm tắp. Đừng để đường kim xiên xẹo làm rách vải.

Hòa lóng ngóng làm hỏng ngay lỗ thứ ba, mũi dùi chọc xiên ra mép vải. Cậu cuống quýt xin miếng khác, nhưng thợ Tư lắc đầu nghiêm khắc, bắt cậu tháo ra làm lại từng mũi trên chính miếng bạt hỏng. Đôi tay Hòa run run, mồ hôi rịn ra trên trán dưới ánh đèn dầu. Sau ba ngày kiên trì nhẫn nại dưới sự chỉ bảo gắt gao của thợ Tư, Hòa đã đâm được mười mũi dùi thẳng tắp, đường chỉ sáp đều đặn như thợ lâu năm. Ánh mắt thợ Tư ánh lên vẻ hài lòng khẽ gật đầu.

Trong lúc Hòa tập ráp, cô Tý và chị Sáu phụ trách may thân giày. Tiếng máy may xạch xạch vang lên đều đặn trong căn xưởng nhỏ. Mùi vải mới hòa lẫn mùi dầu máy ngạt ngào. Có hôm máy may bị bỏ mũi liên tục, chị Sáu phải tháo ổ máy ra vệ sinh, lôi ra xơ vải và dầu mỡ bám đen. Hùng nhìn thấy liền ghi nhận và quy định mỗi ngày thợ may phải dành mười phút đầu ca để lau chùi, tra dầu máy móc. Mọi chi tiết nhỏ nhất đều được đưa vào kỷ luật vận hành. Lan chăm chú ghi chép từng định mức vật tư và thời gian từng ca máy.

Song song với việc đào tạo Hòa, Hùng rà soát lại toàn bộ nguồn cao su trong nước. Ông cùng thợ Tư phân loại lô cao su G2-B nhập từ ông Lợi thành hai nhóm: lô A đạt chuẩn cho đế giày bảo hộ, lô B mỏng hơn dùng cho giày đi nhẹ trong nhà. Sự phân loại tỉ mỉ này giúp xưởng tối ưu chi phí mà không làm sụt giảm uy tín chất lượng. Hùng cũng dành thời gian hướng dẫn Lan cách ghi sổ đối chiếu hàng tồn kho theo tuần, không để xảy ra thất thoát dù chỉ một mét vải bạt hay một cuộn chỉ sáp.

Đến cuối tuần thứ hai, lô G-2 hoàn thành sáu mươi đôi đạt chuẩn. Hòa tự tay ráp thành công mười đôi liên tiếp dưới sự giám sát tỉ mỉ của thợ Tư. Nụ cười rạng rỡ hiện trên gương mặt trẻ mẫn cán của Hòa khi được thợ Tư gật đầu khen ngợi. Đôi mắt cậu rấn rấn nước mắt vì xúc động. Lan cẩn thận ghi nhận công sản phẩm cho Hòa và cấp cho cậu danh nghĩa thợ ráp chính thức của xưởng. Cả xưởng rộn rã tiếng cười chúc mừng người thợ trẻ.

Anh Khanh chở sáu mươi đôi G-2 ra chợ huyện và điểm giao nhận. Khách hàng bắt đầu nhận diện được thương hiệu giày vải An Tín nhờ phom dáng êm chân, đế cao su dẻo bám đường và chính sách đổi trả minh bạch. Nụ cười tươi tắn của các bà nội trợ và người lao động khi xỏ thử đôi giày êm ái khiến anh Khanh vô cùng phấn khởi. Dù một số đối thủ cạnh tranh bắt đầu làm nhái mẫu mã và bán giá rẻ hơn, Hùng vẫn kiên quyết không giảm giá hay hạ chất lượng nguyên liệu. Ông tin rằng người lao động chân chính sẽ luôn nhận ra giá trị của một đôi giày tốt.

Bà Hà ở nhà chuẩn bị cơm chiều cho cả xưởng. Mùi mặn mòi của cá kho và mùi thơm của rau luộc lan tỏa khắp gian bếp ấm cúng. Bà ngước mắt nhìn Hùng và Lan trở về sau một ngày làm việc vất vả, ánh mắt đầy niềm tự hào dịu dàng:
— Làm được đôi giày tốt cho người ta đi làm, cái tâm mình mới yên con ạ.

Hùng mỉm cười đón lấy bát nước chè xanh ấm nóng từ tay mẹ, lòng dạt dào niềm vui:
— Vâng mẹ, sản xuất không thể dối trá dù chỉ một mũi kim. Chữ tín với người dùng là tài sản lớn nhất của chúng con.

Với thành công của lô G-2, Hùng lập tức cho triển khai lô G-3 với quy mô bảy mươi đôi. Hòa lúc này đã làm chủ được thao tác ráp, tay nghề vững vàng, phối hợp nhịp nhàng với thợ Tư. Quy trình kiểm tra hai lớp giúp xưởng loại bỏ hoàn toàn các lỗi lót cứng và lệch chỉ trước khi đóng hộp. Không khí lao động hăng hái tràn ngập khắp các bàn máy.

Hùng ngồi lại trong văn phòng khi đêm đã về khuya, lật mở cuốn sổ nhật ký công việc. Ông tỉ mỉ ghi lại những kinh nghiệm thu được sau chuyến đi miền Nam, từ cách chọn nhà cung cấp cao su, cách đàm phán với đại lý tiêu thụ đến bài học về xây dựng đội ngũ kế thừa. Đối với Hùng, mở rộng kinh doanh không phải là sự tăng trưởng nóng bằng mọi giá, mà là sự phát triển bền vững dựa trên nền tảng chất lượng và con người.

Tối hôm đó, xưởng giày đỏ đèn muộn. Mùi keo dán thơm nồng hòa quyện với mùi vải mới và cao su dẻo. Hùng cất mẫu cao su miền Nam cùng bảng tính chi tiết vào bìa sổ da. Ông đứng bên cửa sổ nhìn Lan đang tỉ mỉ ghi chép số liệu lô G-3 sắp tới, nhìn Hòa đang lau chùi bộ dụng cụ ráp giày với ánh mắt tự hào.

Ánh sáng từ bảng thông báo hệ thống hiện lên xanh dịu trong tâm trí Hùng, báo hiệu chặng đường mới đầy khởi sắc:

「Hệ thống — GHI NHẬN ch.21」
Năm: 1984
Tổng EXP: 990 (+90 nhịp này)
Không gian kho: 1,640m² (+40m²)
Kỹ năng trọng yếu: Thương mại lv2, Y tế lv1, Sản xuất lv1
Ghi chú: G-2=60 + Hòa (ráp 2); lỗi G1-17 quy trình hàng sửa kiểm lại; cao su G2-B ông Lợi tách lô; G-3=70; không phá giá theo đối thủ.
============================================================
"""

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content.strip() + '\n')

# Kiểm tra dung lượng
words = len(content.split())
print(f"Updated Chapter 21, total words: {words}")
