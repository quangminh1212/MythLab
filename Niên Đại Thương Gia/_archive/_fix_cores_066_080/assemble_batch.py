# -*- coding: utf-8 -*-
"""Assemble cleaned cores + unique closes + ledger panels; score each chapter."""
import re, json, glob, sys, os

BASE = r"C:/Dev/MythLab/Niên Đại Thương Gia"
os.chdir(BASE)
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
import strict_score as ss

cfg = json.load(open(".mythlab_score.json", encoding="utf-8"))
led = json.load(open("system_ledger.json", encoding="utf-8"))["chapters"]

PAD = re.compile(
    r"^(Tờ tiền giấy bạc mòn góc.*|Nước mắm cá cơm.*|Hăng hắc khói than.*|Chiếc cân bàn đĩa đồng.*"
    r"|Mảnh nilon gói hàng.*|Bùn non dưới ruộng.*|Cồn cào ruột.*|Lạnh buốt ngón tay sờ gầu.*"
    r"|Nóng rát gáy.*|Than tổ ong lúc nửa đêm.*|Đì đùng máy nổ.*|Rè rè loa phường.*|Tõm tõm gầu nước.*"
    r"|Vải mới cắt thơm mùi hồ.*|Rạ khô vừa gặt.*|Loẹt xoẹt giấy tờ.*|Ướt sũng mồ hôi lưng áo.*)$",
    re.M,
)

titles = {
    67: "Mở trường Sài Gòn",
    68: "Mở trung tâm đào tạo",
    70: "Hoàn thành nhiệm vụ vận chuyển",
    71: "Mở dịch vụ cho vay",
    72: "Mở rộng chi nhánh tài chính",
    73: "Hoàn thành nhiệm vụ cho vay",
    74: "Mở trường học tiếp",
    75: "Mở rộng trường học 30 trường",
    76: "Mở rộng trung tâm đào tạo",
    77: "Hoàn thành nhiệm vụ đào tạo",
    78: "Mở rộng phòng khám tiếp",
    79: "Hoàn thành nhiệm vụ phòng khám",
    80: "Mở rộng công ty xây dựng",
}

skills_map = {
    67: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    68: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    70: "Logistics lv1, Chiến lược lv1, Đầu tư lv2",
    71: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    72: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    73: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1, Logistics lv1",
    74: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    75: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    76: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    77: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1",
    78: "Y tế lv1, Đầu tư lv2, Quản lý lv1",
    79: "Y tế lv1, Đầu tư lv2, Quản lý lv1, Chiến lược lv1",
    80: "Đầu tư lv2, Chiến lược lv1, Quản lý lv1, Logistics lv1",
}

notes = {
    67: "Trường Bình An Bình Thạnh: thuê sửa, giáo viên Hạnh, học thử một tuần không thu trước",
    68: "Trung tâm nghề với thợ Năm Quảng Ngãi: mộc-may-sửa xe; sản phẩm đầu bán không tặng",
    70: "Khóa nhịp vận chuyển Đà Nẵng: 12 chuyến tháng, chứng từ khớp, Logistics lv1",
    71: "Thí điểm cho vay sản xuất HN: vốn tự có, từ chối hồ sơ mờ, không nhận tiền gửi",
    72: "Mở điểm nghiệp vụ tài chính: hai người ký két, mười hồ sơ đầu trung tâm kiểm lại",
    73: "Đóng vòng thí điểm vay 1986: đối soát dư nợ, bàn giao theo dõi, không tự xưng ngân hàng",
    74: "Mạng lưới trường đợt mới: kiểm trùng tên Hưng Yên, từ chối lớp tre tạm Hải Dương",
    75: "Chốt 30 trường: gỡ trùng Quốc Oai, thêm Phúc Thọ đúng mẫu kiểm, không đếm nhà tạm hai lần",
    76: "Mở rộng trung tâm đào tạo: lịch mới, giảng viên kiêm nhiệm có kiểm, không phình danh sách ảo",
    77: "Hoàn thành khóa đào tạo: 52 người nhận chứng chỉ đúng điều kiện an toàn",
    78: "Mở rộng phòng khám tiếp: tách luồng, ghế chờ, ca ưu tiên — không cơ sở 2 vội",
    79: "Khóa nhiệm vụ phòng khám: chỉ số chờ/chuyển viện, quy trình sạch bẩn ổn định",
    80: "Mở rộng công ty xây dựng: tổ đội, vật tư, nghiệm thu — không nhận thầu miệng",
}

closes = {
    67: """***

Chiều muộn, Hùng đứng ở cửa lớp nhìn cô Hạnh viết bảng. Mùi phấn mới, mùi gỗ bàn còn hăng sơn. Ngoài cổng, đứa trẻ chân đất hôm trước đã có mặt — tay cầm cây bút chì gãy, mắt đỏ vì nắng. Lan ghi tên em vào sổ học thử, giọng đều:

— Một tuần. Đủ vở. Không thu trước.

Hùng gật, siết mép sổ bìa xanh rồi buông. Ông không cần biển lớn. Ông cần sáng mai còn chỗ ngồi thật, còn phấn, còn người dám bảo học thử mà không run tay khi bị hỏi tiền.""",
    68: """***

Trước khi lên đường về Hà Nội, Hùng ghé lại xưởng ông Năm một lần nữa. Tiếng cưa, tiếng máy may, tiếng ai đó cười vì đóng lệch mộng rồi sửa lại. Lan đưa tờ điểm danh tháng đầu — hai mươi tên, đủ nghề. Hùng liếc, cau nhẹ ở dòng vắng hai buổi:

— Gọi lại. Vắng không báo là cắt suất thực hành, không cắt người vội.

Ông Năm đứng bên, tay nắm bào, gật. Hùng bước ra ngõ, bụi mịn bám gót. Phía trước là lịch dạy phải giữ đều — không phải bài phát biểu về nghề.""",
    70: """***

Tối về bến, Hùng đối lại lần cuối vận đơn với phiếu cảng dưới ánh đèn vàng. Mùi dầu máy, mùi bụi đường còn trên tay Cường. Tư Hải đứng chờ, thở:

— Tháng sau có thêm tuyến không anh?

— Có khi số khớp và không ai giấu móp xe. — Hùng đáp, mắt không rời cột số. — Logistics không phải chạy nhiều. Là chạy đến nơi còn đúng giấy.

Ông gập sổ, gật với ba tài xế. Đèn bến le lói. Phía trước là bảo dưỡng phớt dầu và một tháng mới — chưa mở lời ăn mừng.""",
    71: """***

Đêm khuya, Hùng và Lan khóa két quỹ vay riêng. Tiếng then sắt. Mùi giấy than. Bà Hà mang hai chén nước, đặt xuống, không hỏi lãi:

— Ăn chưa?

— Ăn rồi mẹ. — Hùng ngẩng, cười mỏi.

Lan ghi dòng cuối ngày: hai hồ sơ giải ngân, một từ chối, không nhận gửi. Hùng siết bút, nhìn ánh đèn:

— Sáng mai chỉ mở cửa cho người đúng mục đích. Ai mang chuyện quen — trả lời bằng quy trình, không bằng cảm xúc.""",
    72: """***

Trên xe về Hà Nội, Lan đọc lại biên bản điểm mới. Hùng lắng, thỉnh thoảng gật. Đèn đường lướt qua mặt kính. Ông nhớ câu chị Mến hỏi có phải biếu gì không — và câu trả lời không phải được lặp lại ở mọi điểm, không chỉ ở chỗ ông ngồi.

— Tuần sau kiểm đột xuất két điểm hai. — Ông nói.

— Em xếp người không trùng tổ giải ngân. — Lan đáp, tay nắm cặp.

Phía trước là ba điểm cùng một mẫu sổ. Hùng không sợ thiếu lòng tin. Ông sợ lòng tin bị ủy thác quá sớm.""",
    73: """***

Hùng đóng bìa tiêu chí thí điểm, để lên tủ hồ sơ — không treo tường. Lan đưa phụ lục bàn giao dư nợ. Ông ký từng trang, mắt nhìn ngày đến hạn kế tiếp:

— Ai mang hồ sơ trường sang bàn này trước khi báo cáo kỳ hạn xong, em dừng.

— Rõ. — Lan gật.

Ngoài cửa, gió tháng Giêng se. Hùng thở, buông bút. Việc vay chưa xong đời. Nó chỉ vừa chứng minh được một vòng — và vòng sau bắt đầu từ dòng theo dõi còn mở.""",
    74: """***

Lan xếp tám hồ sơ đạt vào bìa cứng, hai mươi còn lại chia chờ đất và chờ giáo viên. Hùng kẻ một dòng cuối trang tổng:

— Không đếm trường trên giấy. Đếm phòng có mái và trẻ có tên thật.

Ông ngẩng nhìn mưa bụi ngoài cửa sổ văn phòng. Phía trước là chuyến khảo sát tiếp — không phải lễ công bố số trường.""",
    75: """***

Biển trường Phúc Thọ vẫn úp vào tường. Hùng chỉ cho treo khi tổ kiểm độc lập ký đủ ba trang. Lan gập sổ, mắt cười rất nhẹ rồi nghiêm lại:

— Ba mươi. Đúng chữ, đúng chỗ.

— Ba mươi. — Hùng nhắc. — Mai ai viết ba mươi mốt, em cầm bút đỏ gạch trước khi báo cáo lên.

Ông tắt đèn phòng họp. Ngoài hành lang còn mùi phấn từ bản đồ dán tường. Việc mạng lưới không kết bằng vỗ tay — kết bằng danh sách không đếm trùng.""",
    76: """***

Cuối ngày, Hùng đứng ngoài hàng lớp thực hành. Mùi gỗ bào, mùi dầu máy may. Một giảng viên kiêm nhiệm xin nghỉ hai buổi vì xưởng chính tăng ca. Lan ghi lịch bù, không để trống miệng.

— Không lấy danh sách dài để đẹp báo cáo. — Hùng nói. — Lấy lịch dạy có người đứng lớp.

Ông nắm tay vịn cầu thang sắt, buông, bước xuống sân. Phía trước là tuyển thêm đúng nghề thiếu — không phải treo biển trung tâm lớn.""",
    77: """***

Năm mươi hai phong bì chứng chỉ nằm trong thùng thiếc. Hùng không phát trên sân khấu. Từng người nhận, ký, Lan đối tên. Một người đến trễ vì ca làm — vẫn nhận đủ, không bị cắt vì mất trật tự lễ.

Minh đứng cuối hàng, thở:

— Khóa sau siết an toàn máy hơn nữa.

— Siết. — Hùng gật. — Không để số đẹp che tai nạn suýt.

Ông nhìn sân trống sau khi tan. Phía trước là việc giữ nghề cho người vừa cầm giấy — không phải in thêm giấy.""",
    78: """***

Đêm, An Tín tắt đèn phòng chờ. Vân khóa sổ. Hòa rửa tay lần cuối. Hùng đi dọc hành lang mới, đếm ghế, đếm cửa sạch bẩn. Mùi sát trùng loãng. Ông dừng ở vạch sơn còn ướt:

— Mai sơn lại chỗ mòn. Không để xe bẩn lấn.

Lan ghi. Không ai nói lời lớn. Phòng khám mở rộng bằng centimet có chủ — không bằng khẩu hiệu giường bệnh.""",
    79: """***

Biên bản khóa nhiệm vụ phòng khám chỉ có số: lượt, chờ trung vị, chuyển viện, sự cố suýt. Hùng ký, đưa Tuấn và Hòa cùng ký. Không có băng rôn.

— Ai muốn mở cơ sở hai, đem đủ người và quy trình sạch đã chạy ở đây trước. — Ông nói.

Lan gập hồ sơ. Ngoài phố mưa bụi. Hùng đứng hiên, tay nắm thành cửa rồi buông. Việc y tế không kết bằng lời cảm ơn — kết bằng sáng mai còn đúng ghế và đúng cửa.""",
    80: """***

Trên bãi tập kết, Hùng kiểm lại đống thép hình và bao xi măng theo phiếu. Đội trưởng xin nhận thêm một hạng mục miệng từ quen biết. Hùng lắc:

— Có bản vẽ, có dự toán, có người giám sát — mới nhận. Không có thì về.

Lan ghi từ chối thầu miệng. Tiếng máy trộn vang xa. Hùng liếc bầu trời phía đông, gật với chính mình: công ty xây dựng lớn bằng việc dám nói không — trước khi dám nói có.""",
}


def clean_body(text: str) -> str:
    lines = text.splitlines()
    i = 0
    while i < len(lines) and (
        lines[i].startswith("=") or lines[i].startswith("Chương") or not lines[i].strip()
    ):
        i += 1
    prose = "\n".join(lines[i:])
    prose = PAD.sub("", prose)
    for pat in [
        r"Hùng quay sang, nhìn vợ[^\n]*",
        r"tay ôm nhẹ Lan\.[^\n]*",
        r"tay chạm tay Lan\.[^\n]*",
        r"Mắt họ chạm nhau[^\n]*",
        r"Lan dựa đầu[^\n]*",
        r"vuốt tóc[^\n]*",
        r"nhìn vợ[^\n]*",
    ]:
        prose = re.sub(pat, "", prose)
    cut = len(prose)
    markers = [
        "Mưa rơi trên mái ngói",
        "Hai người ăn cơm tối",
        "Buổi trưa, Hùng nằm võng",
        "Hùng mở cửa sổ, đón",
        "Sau bữa ăn, hai người ngồi",
        "tay ôm nhẹ Lan",
        "Chiều tà, Hùng ngồi bậc thềm",
        "Trong phòng khách, Hùng mở tủ sách",
        "Lan đến ngồi bên cạnh, nhìn vào cuốn",
        "Họ nắm tay",
        "Anh yêu",
        "Thôi, vì em",
        "Có em ở đây",
        "phe phẩy quạt",
        "xoa vai anh",
        "Liệu ngày mai",
        'Hùng rút thuốc ra, Lan nhìn',
        'Hùng rút thuốc ra, bà',
    ]
    thresh = int(len(prose) * 0.55)
    for mk in markers:
        j = prose.find(mk)
        if j >= thresh and j < cut:
            cut = j
    prose = prose[:cut].rstrip()
    prose = re.sub(r"\n{3,}", "\n\n", prose)
    return prose.strip()


def build(n: int, prose: str) -> str:
    e = led[str(n)]
    exp = f"{e['exp_total']:,}"
    sp = f"{e['space_m2']:,}"
    return (
        f"{'=' * 60}\n"
        f"Chương {n}: {titles[n]}\n"
        f"{'=' * 60}\n\n"
        f"{prose}\n\n"
        f"{closes[n]}\n\n"
        f"{'=' * 60}\n"
        f"「Hệ thống — GHI NHẬN ch.{n}」\n"
        f"Năm: {e['year']}\n"
        f"Tổng EXP: {exp} (+{e['exp_delta']} nhịp này)\n"
        f"Không gian kho: {sp}m² (+{e['space_delta']}m²)\n"
        f"Kỹ năng trọng yếu: {skills_map[n]}\n"
        f"Ghi chú: {notes[n]}\n"
        f"{'=' * 60}\n"
    )


def main(chapters):
    results = []
    for n in chapters:
        raw = open(f"_fix_cores_066_080/ch{n}_core.txt", encoding="utf-8").read()
        prose = clean_body(raw)
        body = build(n, prose)
        fp = glob.glob(f"Chương {n} - *.txt")[0]
        open(fp, "w", encoding="utf-8").write(body)
        rv = ss.score_chapter(body, 3000, 4200, True, cfg)
        row = (
            n,
            rv["final"],
            rv["metrics"]["words"],
            rv.get("hard_fails"),
            round(rv["metrics"].get("char_density", 0), 2),
            rv["metrics"].get("dialogue"),
            rv["axes"],
        )
        results.append(row)
        print(
            f"Ch{n} final={rv['final']} words={rv['metrics']['words']} "
            f"hard={rv.get('hard_fails')} cd={row[4]} dlg={row[5]}"
        )
    return results


if __name__ == "__main__":
    chs = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [68, 70, 71, 72, 73, 74, 75, 77, 78, 79, 80]
    main(chs)
