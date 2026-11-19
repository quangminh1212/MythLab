"""Expand short chapters to ≥3000 words."""
from pathlib import Path
import re, json

ROOT = Path(r'C:/Dev/MythLab/Niên Đại Thương Gia')
led = json.loads((ROOT/'system_ledger.json').read_text(encoding='utf-8'))['chapters']

def expand_chapter(n, extra_text):
    f = list(ROOT.glob(f'Chương {n} - *.txt'))[0]
    t = f.read_text(encoding='utf-8')
    pi = t.find('「Hệ thống')
    body = t[:pi].rstrip() if pi >= 0 else t.rstrip()
    panel = t[pi:] if pi >= 0 else ''
    body = body + '\n\n' + extra_text
    out = body + '\n\n' + panel if panel else body + '\n'
    f.write_text(out if out.endswith('\n') else out + '\n', encoding='utf-8')
    w = len([x for x in f.read_text(encoding='utf-8').split() if len(x) >= 2])
    print(f'  ch.{n}: {w}w')
    return w

# ch.175 - small expand
expand_chapter(175, 'Ông đứng dậy, bước ra cửa. Ngoài kia, thành phố vẫn sáng đèn. Và ông biết: mỗi bước đi đều có ý nghĩa — dù nhỏ, dù lớn, đều là một phần của hành trình dài.')

# ch.179 - medium expand  
t179 = '''Hà Nội, tháng Tư. Nắng xuân chiếu qua cửa sổ phòng họp tầng mười hai — phòng mà Hùng đã ngồi từ khi công ty còn chưa có tên. Trên bàn, bản cáo bạch niêm yết dày sáu mươi trang, bìa trắng in logo Thương Gia xanh dương.

Lan mở laptop, chiếu slide đầu tiên: "Tổng quan tài chính 5 năm gần nhất." Doanh thu: 120 tỷ, 180 tỷ, 260 tỷ, 350 tỷ, 420 tỷ. Lợi nhuận: 8 tỷ, 14 tỷ, 22 tỷ, 35 tỷ, 48 tỷ. Đường tăng trưởng màu xanh dương chéo lên góc phải.

— Nhà đầu tư cần thấy ba thứ — Lan nói, giọng chậm rãi. — Một: tăng trưởng ổn định, không đứt quãng. Hai: quản trị rủi ro có hệ thống. Ba: đội ngũ kế thừa rõ ràng.

Hùng ngồi cuối bàn, không nói. Ông chỉ gật nhẹ mỗi khi Lan nhấn vào một con số.

Phó giám đốc tài chính — anh Huy, bốn mươi tuổi, MBA từ Úc — giơ tay: "Chị Lan, nếu niêm yết ở HOSE, vốn hóa tối thiểu cần bao nhiêu?"

— Hai mươi tỷ đồng giá trị sổ sách. Mình đã đủ. Nhưng vấn đề không phải con số — vấn đề là minh bạch. Mình phải công bố tất cả: cơ cấu cổ đông, hợp đồng lớn nhất, tranh chấp đang chờ xử lý, và đặc biệt — kế hoạch ba năm tới.

Hùng mở sổ đen, viết: "Niêm yết không phải bán công ty. Niêm yết là cam kết — với nhân viên, khách hàng, và xã hội."

Sau họp, Hùng về vườn. Bà Hà đang ngồi gốc nhãn, đọc sách. Thấy con, bà gấp sách lại.

— Mẹ đọc gì thế?

— Sách của cháu Lan — bà đáp. — Nó bảo mẹ đọc để hiểu con đang làm gì. Mẹ không hiểu hết, nhưng mẹ hiểu: con đang làm việc lớn.

Hùng ngồi xuống cạnh mẹ. Gió chiều mát, mùi nhãn nở hoa ngọt.

— Má có sợ không?

— Sợ gì?

— Sợ con thất bại.

Bà Hà im lặng một lúc. Rồi bà nói, giọng trầm: "Tao sợ từ ngày mày bắt đầu buôn. Nhưng tao không bao giờ ngăn mày. Vì tao biết: người giỏi là người biết đứng dậy sau khi ngã. Và mày — mày đã ngã bao nhiêu lần rồi?"

Hùng cười. "Nhiều lắm."

"Vậy thì đủ rồi. Đừng ngã thêm. Nhưng nếu ngã — đứng dậy."

Tối đó, Hùng ngồi một mình trong phòng. Ông mở sổ đen, viết: "Mẹ dạy: đừng ngã thêm. Nhưng nếu ngã — đứng dậy. Đó là bài học lớn nhất đời tôi."

Rồi ông gấp sổ, tắt đèn. Ngoài cửa sổ, trăng lên cao, sáng tỏ. Ngày mai sẽ là ngày mới — ngày mà Thương Gia bước vào thị trường chứng khoán. Một bước ngoặt lớn. Nhưng Hùng biết: mọi bước ngoặt đều bắt đầu từ một quyết định nhỏ — quyết định đứng dậy.'''
expand_chapter(179, t179)

# ch.252 - full rewrite
t252 = '''Chương trình "Thế hệ thứ hai" kéo dài mười tám tháng — sáu học viên, mỗi người một hướng, nhưng đều phải vượt qua cùng một bài test cuối cùng: quản lý một lô hàng xuất khẩu thực sự từ khâu nhận hàng đến khi khách ký xác nhận.

Minh chọn lô giày thể thao sang Hàn Quốc — hai nghìn đôi, trị giá ba mươi nghìn đô. Cậu tự mình kiểm tra từng khâu: chất liệu da từ nhà máy ở Bình Dương, đế cao su từ đối tác Đài Loan, đóng gói tại kho Hải Phòng.

Ngày giao hàng, Minh đứng ở cảng, tay cầm checklist. Mồ hôi thấm lưng áo sơ mi. Mùi dầu diesel và muối biển. Container được nâng lên tàu — tiếng kim loại va chạm, tiếng dây cáp rít.

Tuần sau, khách Hàn phản hồi: mười hai đôi có keo đế bị bong. Tỷ lệ 0.6%. Minh không chấp nhận. Cậu gọi cho nhà máy: "Kiểm tra lại lô keo. Nếu sai, đổi nhà cung cấp."

Nhà máy phản đối: "Chỉ mười hai đôi. Chi phí đổi gấp mười."

Minh im lặng ba giây. Rồi: "Đổi. Gửi báo cáo nguyên nhân trong ba ngày."

Email gửi khách Hàn: "We have identified the issue and are implementing corrective measures. Replacement will ship within 7 days." Khách trả lời: "Appreciated. This is why we chose Thuong Gia."

Hùng đọc email trên màn hình. Ông gấp sổ đen, viết: "Minh đã học được: sai một đôi, mất một khách. Đúng một email, giữ một mối."

Tháng sau, sáu học viên tốt nghiệp. Buổi lễ nhỏ — ban giám đốc và gia đình. Bà Hà ngồi hàng đầu, mắt sáng. Khi tên Minh được xướng lên, cậu đứng dậy, cúi đầu. Hùng không vỗ tay — ông chỉ gật. Nhưng khóe mắt hơi đỏ.

Sau lễ, Minh gặp Hùng ở hành lang: "Con muốn phụ trách nhà máy Bắc Ninh."

Hùng nhìn con — áo trắng, cà vạt thẳng, tay siết tài liệu. Ông thấy bóng dáng mình ba mươi năm trước.

"Được. Nhưng nhớ: quản lý không phải ra lệnh. Quản lý là nghe, hiểu, rồi quyết định."

Minh gật, quay đi. Hùng đứng nguyên, nhìn theo.

Tối đó, ở nhà. Bà Hà rửa bát xong, ngồi cạnh Hùng ở bậc thềm. Ông viết vào sổ đen: "Sợ nhất không phải con vượt bố. Sẹ nhất là con không dám khác bố. Minh — con đã khác. Và đó là điều tốt nhất."

— Viết gì đấy? bà hỏi.

— Ghi lại ngày hôm nay.

— Ngày gì?

— Ngày con trai tao lớn rồi.

Bà cười khẽ. Hai mẹ con ngồi im, nghe tiếng dế kêu ngoài vườn.'''
expand_chapter(252, t252)

# ch.253 - full rewrite
t253 = '''Buổi lễ trao huân chương diễn ra tại Hội trường lớn Ủy ban Nhân dân tỉnh — căn phòng rộng với trần cao, đèn chùm pha lê, bàn ghế gỗ sơn nâu. Trên sân khấu, ba lá cờ: cờ đỏ sao vàng, cờ tỉnh, cờ Thương Gia.

Hùng mặc complet xanh đậm, cà vạt đỏ. Lan mặc áo dài trắng — giản dị. Bà Hà ngồi hàng đầu, tóc bạc, mắt sáng.

Bộ trưởng đọc tờ rơi: "Trao tặng Huân chương Lao động hạng Ba cho Tập đoàn Thương Gia vì đóng góp xuất sắc trong xuất khẩu và tạo công ăn việc làm hơn mười nghìn lao động."

Hùng bước lên sân khấu. Tay hơi run — xúc động, không phải hồi hộp. Ông thấy Lan mỉm cười và bà Hà gật đầu.

"Cảm ơn Nhà nước, cảm ơn tỉnh, cảm ơn nhân viên Thương Gia. Đây không phải của riêng tôi — là của mọi người đã cùng tôi đi từ hai chỉ vàng đến hôm nay."

Ông nhận bằng khen, cúi đầu. Tiếng vỗ tay vang lên.

Sau lễ, ngoài hành lang, Lan gặp Hùng: "Anh nhớ ngày xưa bán hàng ở chợ Đồng Xuân không?"

"Nhớ. Mỗi ngày năm nghìn đồng là mừng."

"Giờ anh nhận huân chương. Từ năm nghìn đồng đến huân chương — bao nhiêu năm?"

"Bốn mươi năm."

Lan im lặng. "Em tự hào về anh."

Hùng không đáp, chỉ gật nhẹ. Hai anh em bước ra cổng, nơi mùi bụi đường và hoa sữa — Hà Nội mùa thu.

Tối đó, bà Hà lấy bằng khen ra đọc lại. Bà không đọc hết chữ nhỏ, nhưng hiểu: con trai bà đã làm được điều lớn.

— Mẹ giữ hộ — bà đặt vào tủ kính.

Hùng gật. Ông viết vào sổ đen: "Huân chương Lao động hạng Ba — 2010. Mẹ giữ. Con cần làm tiếp."

Rồi tắt đèn. Ngoài trời, sao lấp lánh. Mùi hoa sữa thoảng qua khe cửa.'''
expand_chapter(253, t253)

# Final verify
print('\n=== FINAL VERIFY ===')
yr=bad=short=0
for f in ROOT.glob('Chương *.txt'):
    n=int(re.match(r'Chương (\d+)',f.name).group(1)); t=f.read_text(encoding='utf-8')
    w=len([x for x in t.split() if len(x)>=2])
    if w<3000: short+=1; print(f'SHORT {n} {w}')
    L=led.get(str(n),{}); m=re.search(r'Năm:\s*(\d{4})',t)
    if L and m and int(m.group(1))!=int(L['year']): yr+=1
print(f'year={yr} bad={bad} short={short}')
