# -*- coding: utf-8 -*-
import glob, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'

# List of template lines to purge
TEMPLATE_SENTENCES = [
    '— Hùng nhìn Lan, ánh mắt đăm chiêu, giọng trầm ấm: "Mọi kế hoạch kinh doanh đều phải đặt sự minh bạch và uy tín lên hàng đầu."',
    '— Lan gật đầu mỉm cười, đôi mắt rạng rỡ trả lời: "Em hoàn toàn tin tưởng vào định hướng và sự chuẩn bị kỹ lưỡng của anh."',
    '— Bà Hà nhìn hai con, đôi tay chai sạn xoa nhẹ vào nhau: "Chỉ cần các con đoàn kết, khó khăn nào rồi cũng sẽ vượt qua."',
    '— Hùng tiếp lời, nhịp thở sâu kiên định: "Chúng ta sẽ từng bước mở rộng thị trường mà không vội vàng hay mạo hiểm."',
    '— Chị Mai bước vào, đôi mắt sáng ngời, giọng nói hồ hởi: "Số lượng đơn đặt hàng tuần này đã tăng vượt mức dự kiến."',
    '— Anh Sơn gật đầu tán thành, đôi tay chỉ lên bản đồ: "Tuyến đường vận chuyển miền Trung đã sẵn sàng thông suốt."',
    '— Khánh mỉm cười tự tin, bả vai thả lỏng: "Dây chuyền máy móc mới vận hành rất trơn tru và tiết kiệm chi phí."',
    '— Ông Hà đứng dậy, đôi mắt tự hào nhìn Hùng: "Ta tin tưởng con sẽ đưa doanh nghiệp phát triển bền vững."',
    '— Bà Mai rót thêm trà, giọng dịu dàng: "Mọi người hãy nghỉ tay dùng chút nước chè ấm cho ấm người."',
    '— Lâm hăng hái chia sẻ: "Đội ngũ kỹ thuật đã hoàn thành kiểm thử quy trình mới đạt chuẩn chất lượng."',
    '— Tâm lên tiếng khích lệ: "Anh em trong xưởng đều rất phấn khởi và sẵn sàng tăng ca hoàn thành tiến độ."',
    '— Minh khẽ gật đầu: "Hệ thống sổ sách báo cáo tài chính tuần này đã được đối soát chính xác tuyệt đối."',
    '— Hùng mỉm cười nhìn cả đội ngũ: "Sự nỗ lực của tất cả mọi người chính là chìa khóa tạo nên thành công."',
    '— Lan tiếp thêm động lực: "Chúng ta sẽ tiếp tục cải tiến quy trình để nâng cao năng suất hơn nữa."',
    'Vị chát thanh của bát nước chè xanh tỏa khói ấm làm đầu óc trở nên tỉnh táo giữa cái lạnh.',
    'Ánh nắng mờ nhạt hắt qua ô cửa sổ, mang theo hơi ấm nhẹ nhàng làm dịu bớt cái lạnh mùa đông.',
    'Tiếng gió lùa rít qua rặng tre ngoài sân, tỏa mùi khói rơm thơm nồng trong cái lạnh sương sớm.',
    'Mùi keo dán hòa cùng mùi gỗ mới thơm nồng từ xưởng phảng phất trong ánh nắng ấm áp.',
    'Cái lạnh hanh khô của buổi chiều thu hòa cùng ánh nắng vàng nhạt và tiếng gió thổi qua khe cửa.',
    'Tiếng bước chân xạc xào vang lên giữa cơn mưa rào, không khí se lạnh và vị mặn mồ hôi đọng trên trán.',
    'Mùi khói rơm ẩm mốc hòa cùng không khí se lạnh buổi sớm khiến gian phòng thêm trầm mặc.',
    'Mùi thơm dịu của tách chè tươi hòa cùng cảm giác ấm áp làm không gian làm việc thêm đầm ấm.',
    'Hùng nhìn thẳng vào đối phương, ánh mắt đăm chiêu, đôi tay chai sạn siết nhẹ, nhịp thở sâu kiên định và khẽ mỉm cười.',
    'Khánh đứng tựa ban công, nhịp thở sâu thư thái, đôi mắt đăm chiêu nhìn về phía xưởng sản xuất đang rực sáng.',
    'Hùng nhìn thẳng, đôi mắt đăm chiêu khẽ gật đầu, đôi tay siết nhẹ mép bàn, nhịp thở sâu giọng trầm ấm.'
]

def clean_text_exact(text):
    for sent in TEMPLATE_SENTENCES:
        text = text.replace(sent, '')
    # replace duplicate empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

for n in [1, 6, 8, 9, 55, 100, 200, 360]:
    files = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
    if not files: files = glob.glob(os.path.join(ROOT, f'Chương {n:02d} - *.txt'))
    if not files: continue
    raw = open(files[0], encoding='utf-8').read()
    parts = raw.split('=' * 60)
    body = parts[2].split('-' * 60)[0] if len(parts) >= 3 else raw
    cbody = clean_text_exact(body)
    words = len(cbody.split())
    print(f'Ch {n:3d}: Raw words={len(body.split())}, Clean words={words}')
