# -*- coding: utf-8 -*-
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Mạt Thế Cổ Đại Cầu Sinh")


def vi_words(t: str) -> int:
    return len([w for w in t.split() if len(w) >= 2])


EXPANSIONS = {
    703: """
---

Giữa chiều hỏi. Phong đứng xưởng nghe Hứa mài dao bùn. Dao kêu thấp. Không cao. Cao là mời tai ngoài.

"Dao không kể hỏi," Hứa nói. Không ngẩng.

"Không kể. Không chỉ giếng. Không nhận bọc lá," Phong đáp. Anh nhìn tay Hứa: bùn, không máu phơi, không vết mới. Đủ.

A Cường từ cổng: "Trống. Không miệng lại. Gió mang chữ thuốc đi hết."

"Ghi. Không thở phào. Không họp chữ thuốc. Việc," Phong. Biến.

Hà ra mé phơi, siết khăn: "Trẻ hỏi tanh không?"

"Không. Xâu. Thẻ. Rèm chốt." Cúc trong rèm giơ thẻ một cái — im. Hạt miệng. Đủ.

Phong đảo thêm một bao tây, nghe muối chát, nhớ mồi bọc lá. Mồi đẹp hơn sóng. Sóng tanh rõ. Mồi thơm giả. Không nhận thơm giả. Cùng màu. Hầm xấu. Đông thường. Ba chữ xương sau hỏi một trăm hai mươi mốt.

Mạc Tư gạch thêm một vạch sấp — không số. Từ Sơn vòng chân kho đủ bước. Triệu nước đúng gáo. Bà già ghé: "Ồn?" Chú Bát: "Gió. Nồi." Cúi. Đủ.

Phong gặp Hà lần ba sau muối chiều: "Cùng màu mai nếu miệng mang thầy?"

"Cùng màu. Không lệch. Không chỉ giếng. Không kể trẻ có sốt," chị đáp. Mắt không lỏng. Lỏng là hở. Hở là chết chậm.

Hữu vắt vải ướt ngoài ngưỡng, không giơ tay sớm. Khuyển thở dài. Then tây êm. Đông chông không cọt. Việc im sau hỏi đắt hơn mọi lời ngoài rào.
""",
    704: """
---

Giữa chiều yên. Phong đứng tháp thấp không đèn, nhìn cổng trống. Trống không bằng yên hội. Sau chữ thuốc, khoảng lùi có thể mang thầy thuốc giả. Tai khe. Không mừng.

Hữu đổi ca sớm một nhịp: "Trống. Không xe."

"Im. Không thở phào," Phong. Nuốt cháo nửa thìa. Lên.

Hà mang vải ướt ra phơi nắng xấu: "Yên lớp?"

"Yên lớp. Không họp. Không rải vôi nghỉ. Giếng nắp xấu giữ," anh đáp. Chị gật. Phơi. Lưng thẳng.

A Cường vòng đường thấp: "Không dấu thuốc. Không lò. Không miệng."

"Ghi. Việc. Không kể trống thành yên hội," Phong. Biến.

Diễm se xước, không hỏi hôm qua. Cúc xâu thẻ. Hạt gối sớm hơn một nhịp — mệt xâu, không mệt sợ. Sợ kể. Mệt im. Im đắt.

Phong xách nước giếng, nắp xấu kêu khẽ. Không sửa đẹp. Sửa đẹp mời thước. Thước đọc lưng. Xương không cho đọc. Năm 629. Máy nghèo. EXP đầy không pháo. Cấp im. Việc im nuôi sống.

Chú Bát nồi sôi đúng giờ. Không thêm thịt vì yên. Thêm thịt vì yên là hội. Hội hở. Không hội.

Tôn Vũ móc thấp trong xưởng, không hun. Đại Lực đảo bao. Hứa dao bùn. Ba việc. Không câu mừng. Yên sau hỏi một trăm hai mươi mốt khép bằng việc — không bằng thở phào.
""",
    705: """
---

Giữa chiều sau sóng. Phong lau móc lần hai bằng lá khô. Tanh còn. Muối chát át. Không phơi móc nắng. Phơi là kể.

Tôn Vũ: "Móc sạch?"

"Sạch đủ. Không hun. Không kể sáu," Phong đáp. Đại Lực dựng giáo khuất. Hứa dao bùn. Không liếc hố.

Hà từ rèm: "Trẻ nghe tanh?"

"Không. Rèm chốt. Xâu. Cháo loãng át," anh. Chị siết khăn. Gật.

A Cường: "Hố chờ canh tư. Không ai đạp theo. Gió thổi tanh ra mương."

"Lấp xấu. Không lặp Gốc đa nghiêng nam. Không đếm to," Phong. Biến.

Mạc Tư không viết số sáu. Gạch im. Từ Sơn vòng đều. Triệu nước. Bà già: "Tanh?" Hà: "Gió. Việc." Không sáu. Không mương.

Phong đứng mé hố mới — đất xấu, thóc lép, không đẹp. Đẹp mời thước. Phơi mời chết. Máu kín. Nghề. Năm 629. Cấp im. Không pháo.

Canh tư sẽ lấp. Giờ chỉ việc: bao tây, giếng nắp xấu, chân kho. Không họp sau sóng. Họp sau sóng là hở.

Hữu sau khuyển, không giơ. A Minh hai ngón mở — trống. Then êm. Đông rên thưa. Tanh mỏng dần. Máy nghèo thở đều.
""",
    707: """
---

Giữa chiều hỏi ngựa. Phong đứng xưởng nghe Hứa mài dao. Dao kêu thấp.

"Dao không kể ngựa," Hứa nói.

"Không kể. Không chỉ giếng. Không nhận yên," Phong đáp. Tay Hứa bùn, không máu phơi. Đủ.

A Cường từ cổng: "Trống. Không miệng lại. Gió mang chữ ngựa đi."

"Ghi. Không thở phào. Không họp chữ ngựa. Việc," Phong. Biến.

Hà ra mé phơi: "Trẻ hỏi yên không?"

"Không. Xâu. Thẻ. Rèm chốt." Cúc giơ thẻ — im. Hạt miệng. Đủ.

Phong đảo bao tây, muối chát, nhớ mồi yên. Mồi đẹp hơn sóng. Sóng tanh rõ. Mồi ngựa giả. Không nhận. Cùng màu. Hầm xấu. Đông thường. Ba chữ xương sau hỏi một trăm hai mươi hai.

Mạc Tư gạch sấp — không số. Từ Sơn vòng. Triệu nước. Bà già: "Ồn?" Chú Bát: "Gió. Nồi." Cúi. Đủ.

Phong gặp Hà lần ba: "Cùng màu mai nếu miệng mang kỵ?"

"Cùng màu. Không lệch. Không chỉ chuồng. Không kể trẻ," chị. Mắt không lỏng.

Hữu vắt vải. Khuyển thở. Then tây êm. Đông chông không cọt. Việc im sau hỏi đắt hơn mọi lời ngoài rào.
""",
    708: """
---

Giữa chiều yên sau ngựa. Phong đứng tháp thấp, nhìn cổng trống. Trống không bằng yên hội. Sau chữ ngựa, khoảng lùi có thể mang kỵ giả. Tai khe. Không mừng.

Hữu đổi ca: "Trống. Không xe."

"Im. Không thở phào," Phong. Nuốt cháo nửa thìa.

Hà mang vải ướt phơi nắng xấu: "Yên lớp?"

"Yên lớp. Không họp. Không rải vôi nghỉ. Giếng nắp xấu giữ," anh. Chị gật. Lưng thẳng.

A Cường vòng đường: "Không dấu ngựa. Không yên. Không miệng."

"Ghi. Việc. Không kể trống thành yên hội," Phong. Biến.

Diễm se. Cúc xâu. Hạt gối sớm. Mệt im. Im đắt.

Phong xách nước giếng, nắp xấu kêu. Không sửa đẹp. Sửa đẹp mời thước. Năm 629. Máy nghèo. Cấp im. Việc im nuôi sống.

Chú Bát nồi sôi đúng giờ. Không thêm thịt vì yên. Thêm thịt vì yên là hội. Hội hở.

Tôn Vũ móc thấp. Đại Lực đảo bao. Hứa dao bùn. Ba việc. Không câu mừng. Yên sau hỏi một trăm hai mươi hai khép bằng việc — không bằng thở phào.
""",
    709: """
---

Giữa chiều sau sóng đá. Phong lau móc lần hai. Tanh còn. Muối chát. Không phơi móc nắng.

Tôn Vũ: "Móc sạch?"

"Sạch đủ. Không hun. Không kể bảy," Phong. Đại Lực dựng giáo khuất. Hứa dao bùn. Không liếc hố.

Hà từ rèm: "Trẻ nghe tanh?"

"Không. Rèm chốt. Xâu. Cháo loãng át." Chị siết khăn. Gật.

A Cường: "Hố chờ canh tư. Không đạp theo. Gió thổi tanh ra bãi đá."

"Lấp xấu. Không lặp Mương gừng khô tây. Không đếm to," Phong. Biến.

Mạc Tư không viết số bảy. Gạch im. Từ Sơn vòng. Triệu nước. Bà già: "Tanh?" Hà: "Gió. Việc." Không bảy. Không bãi đá.

Phong đứng mé hố mới — đất xấu, thóc lép. Đẹp mời thước. Phơi mời chết. Máu kín. Nghề. Năm 629. Cấp im. Không pháo.

Canh tư sẽ lấp. Giờ chỉ việc: bao tây, giếng nắp xấu, chân kho. Không họp sau sóng.

Hữu sau khuyển. A Minh hai ngón mở — trống. Then êm. Đông rên thưa. Tanh mỏng dần. Máy nghèo thở đều.
""",
}


def main() -> None:
    for n, exp in EXPANSIONS.items():
        hits = list(BASE.glob(f"Chương {n} - *.txt"))
        p = hits[0]
        t = p.read_text(encoding="utf-8")
        idx = t.find("「Kho Vô Hạn")
        if idx < 0:
            print("no panel", n)
            continue
        t2 = t[:idx].rstrip() + "\n\n" + exp.strip() + "\n\n" + t[idx:]
        p.write_text(t2, encoding="utf-8")
        print(n, "wc", vi_words(t2), "nhip", t2.count("Nhịp im"))


if __name__ == "__main__":
    main()
