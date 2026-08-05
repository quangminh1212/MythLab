# -*- coding: utf-8 -*-
"""Expand ch.766-773 with unique Phong/Hà afternoon scenes for scorer words>=3000."""
from __future__ import annotations

import os

BASE = r"C:\Dev\XLab_MTC\Mạt Thế Cổ Đại Cầu Sinh"

EXPAND = {
    766: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau muối.

Anh lau ngón chát, mắt nhìn gò đông hai nhịp rồi cúi. Chị siết khăn mũi, thở đều, không hỏi số mốc.

"Mốc tre còn ngoài?" Hà hỏi khẽ.

"Còn. Ta không nhổ. Không đếm to. Không chỉ trẻ," Phong đáp. Anh nắm tay chị, siết một nhịp, buông. "Máy nghèo nhớ nghề. Không khoe."

"Rèm chặt. Mai nếu bóng quay — cùng luật," chị gật, liếc sân, cau nhẹ. "Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp."

"Ghi. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh thở ra. Mùi đất se. Mùi vôi cũ. Gió bấc lạnh gáy. Tiếng then êm.

Đại Lực ghé: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mừng. Phong gật, không khen to.

Hà đứng dậy, ngẩng nhìn rèm trẻ: "Hạt ngủ thẻ. Cúc xâu xong."

"Đủ. Không mở sớm," anh nói. Nắm bao. Siết hàm. Sống. Đo. Không khoe.

A Cường ngoài ngưỡng hai chữ: "Trống. Việc." Rồi biến. Khuyển gõ giếng một tiếng. Từ Sơn vòng đều. Mạc Tư bảng sấp — không viết số to.

Phong thì thầm: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im một nét rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc cổng, cúi, thở. Đủ cho chiều muộn gò đông.
""",
    767: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau muối.

Anh lau ngón chát, mắt nhìn cổng đông hai nhịp rồi cúi. Chị siết khăn, thở đều, không nhắc chữ dây.

"Miệng hỏi dây còn quanh?" Hà hỏi khẽ, nhíu.

"Không nghe lại. Ta không nhận. Không đổi cọc. Đông thường. Hầm xấu," Phong đáp. Anh nắm then trong đầu, siết hàm, thở. "Cùng màu nếu hỏi lại. Không lệch."

"Lời em nếu miệng. Bao anh," chị gật, liếc rèm, cau. "Trẻ không ra gần cổng."

"Ghi. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Không pháo." Anh buông tay xuống bao. Mùi dây thừng se còn nhạt. Mùi đất se. Gió bấc.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Phong gật.

Hà ngẩng: "Giọng khác lần trước — ghi xương không ghi miệng sân."

"Ghi xương. Không kể," anh nói. Nắm tay chị một nhịp. Siết. Buông. Đủ.

A Cường: "Trống. Việc." Biến. Khuyển ngưỡng. Mạc Tư không đọc to vạch.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc cổng, cúi, thở. Đủ cho chiều muộn hỏi dây.
""",
    768: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau yên.

Anh lau ngón chát, mắt không nở mừng vì cổng trống. Chị siết khăn, thở đều, không thở phào.

"Yên thật hay yên lùi?" Hà hỏi khẽ, cau.

"Trống. Không thở phào. Tai khe — miệng hỏi dây có thể mang thợ trói giả," Phong đáp. Anh nắm muối, siết, thở. "Không rải vôi nghỉ. Không mở rèm sớm."

"Rèm chặt. Trẻ không ra sớm," chị gật, liếc sân. "Việc không phải hội. Việc là im."

"Ghi. Ai kể ngoài lều — nặng. Ai chỉ hố — nặng. Không pháo." Anh buông. Mùi cháo loãng. Mùi đất se. Gió bấc lạnh gáy. Tiếng then êm.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mừng.

Hà ngẩng: "A Cường còn báo trống?"

"Trống. Không soi. Không kể," anh nói. Nắm tay chị. Siết. Buông. Đủ.

A Cường ngoài ngưỡng: "Trống. Việc." Biến. Khuyển gõ giếng. Mạc Tư gạch im — yên đang giữ.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc cổng, cúi, thở. Không thở phào. Đủ cho chiều yên sau hỏi dây.
""",
    769: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau sóng.

Anh lau móc bằng lá khô, mắt nhìn gò sườn tây thấp hai nhịp rồi cúi. Chị siết khăn, thở đều, không hỏi số bốn.

"Hố mới đã lớp?" Hà hỏi khẽ, nhíu.

"Canh tư sẽ lớp. Thóc lép. Đắp xấu. Không đếm bốn to. Không phơi. Không lặp hố bờ suối cạn đông-nam," Phong đáp. Anh nắm tay chị, siết, thở. "Máu kín. Máu vải không vôi."

"Rèm chặt. Trẻ không thấy hố," chị gật, liếc sân, cau. "Ai kể số — nặng. Ai chỉ hố — nặng gấp."

"Ghi. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh buông. Mùi tanh đất sườn tây còn nhạt. Mùi đất se. Gió bấc.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Phong gật, không khen to.

Hà ngẩng: "Bốn thấp — ghi xương."

"Ghi xương. Không kể sân," anh nói. Nắm. Siết. Buông. Đủ.

A Cường: "Trống. Không thèm thấp." Biến. Khuyển ngưỡng. Mạc Tư bảng sấp.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc gò sườn, cúi, thở. Đủ cho chiều sau sóng thấp.
""",
    770: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau thước.

Anh lau ngón chát, mắt nhìn đường bụi đông hai nhịp rồi cúi. Chị siết khăn, thở đều, không nhắc thước tre.

"Thước tre còn nghiêng ngoài?" Hà hỏi khẽ.

"Còn. Ta không nhổ. Không đếm to. Không chỉ trẻ," Phong đáp. Anh nắm tay chị, siết một nhịp, buông. "Máy nghèo nhớ nghề. Không khoe."

"Rèm chặt. Mai nếu bóng quay — cùng luật," chị gật, liếc sân, cau nhẹ. "Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp."

"Ghi. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh thở ra. Mùi bụi đường. Mùi thước tre ướt sương. Gió bấc lạnh gáy. Tiếng then êm.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mừng. Phong gật.

Hà đứng dậy, ngẩng nhìn rèm trẻ: "Hạt ngủ thẻ. Cúc xâu xong."

"Đủ. Không mở sớm," anh nói. Nắm bao. Siết hàm. Sống. Đo. Không khoe.

A Cường: "Trống. Việc." Biến. Khuyển gõ giếng. Từ Sơn vòng đều. Mạc Tư bảng sấp.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc đường bụi, cúi, thở. Đủ cho chiều muộn bóng thước.
""",
    771: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau muối hỏi.

Anh lau ngón chát, mắt nhìn cổng đông hai nhịp rồi cúi. Chị siết khăn, thở đều, không nhắc chữ muối thô.

"Miệng hỏi muối còn quanh?" Hà hỏi khẽ, nhíu.

"Không nghe lại. Ta không nhận. Không đổi vỏ ốc. Đông thường. Hầm xấu," Phong đáp. Anh nắm then trong đầu, siết hàm, thở. "Cùng màu nếu hỏi lại. Không lệch."

"Lời em nếu miệng. Bao anh," chị gật, liếc rèm, cau. "Trẻ không ra gần cổng."

"Ghi. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Không pháo." Anh buông tay xuống bao. Mùi muối thô se. Mùi vỏ ốc khô. Gió bấc.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Phong gật.

Hà ngẩng: "Giọng khác lần trước — ghi xương không ghi miệng sân."

"Ghi xương. Không kể," anh nói. Nắm tay chị một nhịp. Siết. Buông. Đủ.

A Cường: "Trống. Việc." Biến. Khuyển ngưỡng. Mạc Tư không đọc to vạch.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc cổng, cúi, thở. Đủ cho chiều muộn hỏi muối.
""",
    772: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau yên muối.

Anh lau ngón chát, mắt không nở mừng vì cổng trống. Chị siết khăn, thở đều, không thở phào.

"Yên thật hay yên lùi?" Hà hỏi khẽ, cau.

"Trống. Không thở phào. Tai khe — miệng hỏi muối có thể mang bao muối giả," Phong đáp. Anh nắm muối, siết, thở. "Không rải vôi nghỉ. Không mở rèm sớm."

"Rèm chặt. Trẻ không ra sớm," chị gật, liếc sân. "Việc không phải hội. Việc là im."

"Ghi. Ai kể ngoài lều — nặng. Ai chỉ hố — nặng. Không pháo." Anh buông. Mùi cháo loãng. Mùi đất se. Gió bấc lạnh gáy. Tiếng then êm.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Không câu mừng.

Hà ngẩng: "A Cường còn báo trống?"

"Trống. Không soi. Không kể," anh nói. Nắm tay chị. Siết. Buông. Đủ.

A Cường ngoài ngưỡng: "Trống. Việc." Biến. Khuyển gõ giếng. Mạc Tư gạch im — yên đang giữ.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc cổng, cúi, thở. Không thở phào. Đủ cho chiều yên sau hỏi muối.
""",
    773: """
---

Chiều muộn. Phong và Hà ngồi ghế đá tây sau sóng dứa.

Anh lau móc bằng lá khô, mắt nhìn bụi dứa dại bắc-tây hai nhịp rồi cúi. Chị siết khăn, thở đều, không hỏi số năm.

"Hố mới đã lớp?" Hà hỏi khẽ, nhíu.

"Canh tư sẽ lớp. Thóc lép. Đắp xấu. Không đếm năm to. Không phơi. Không lặp hố gò sườn tây thấp," Phong đáp. Anh nắm tay chị, siết, thở. "Máu kín. Máu vải không vôi."

"Rèm chặt. Trẻ không thấy hố," chị gật, liếc sân, cau. "Ai kể số — nặng. Ai chỉ hố — nặng gấp."

"Ghi. Ai kể cấp — nặng gấp đôi. Lần này không pháo." Anh buông. Mùi nhựa dứa dại lẫn tanh còn nhạt. Mùi đất se. Gió bấc.

Đại Lực: "Bao đủ." Tôn Vũ: "Móc sạch." Hứa: "Dao đất." Ba câu việc. Phong gật, không khen to.

Hà ngẩng: "Năm thấp — ghi xương."

"Ghi xương. Không kể sân," anh nói. Nắm. Siết. Buông. Đủ.

A Cường: "Trống. Không thèm thấp." Biến. Khuyển ngưỡng. Mạc Tư bảng sấp.

Phong: "Còn thở đều không?"

"Đều. Không lỏng," Hà đáp, cười im rồi tắt. "Mai vẫn việc. Không hội."

"Rèm chặt. Không kể ngoài." Anh liếc bụi dứa, cúi, thở. Đủ cho chiều sau sóng dứa dại.
""",
}


def main() -> None:
    for n, block in EXPAND.items():
        path = next(
            os.path.join(BASE, f)
            for f in os.listdir(BASE)
            if f.startswith(f"Chương {n} ")
        )
        t = open(path, encoding="utf-8").read()
        if "Chiều muộn. Phong và Hà ngồi ghế đá" in t:
            print(n, "already expanded")
            continue
        marker = "Canh một sau việc"
        if marker not in t:
            marker = "「Kho Vô Hạn"
        t = t.replace(marker, block.strip() + "\n\n" + marker, 1)
        open(path, "w", encoding="utf-8", newline="\n").write(t)
        print(n, "expanded", len(t.split()))


if __name__ == "__main__":
    main()
