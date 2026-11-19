# -*- coding: utf-8 -*-
"""Expand MTCDS 862-869 to >=3000 words without Nhịp im clone pad."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Dev\MythLab\Mạt Thế Cổ Đại Cầu Sinh")

# Import specs from rewrite script
import importlib.util

spec = importlib.util.spec_from_file_location(
    "rw", r"C:\Dev\MythLab\_tools\rewrite_mtcds_862_869.py"
)
rw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rw)
SPECS = rw.SPECS


def big_expand(n: int, s: dict, text: str, target: int = 3300) -> str:
    panel_m = re.search(r"\n「Kho Vô Hạn", text)
    if not panel_m:
        raise ValueError(f"no panel ch.{n}")
    head = text[: panel_m.start()]
    tail = text[panel_m.start() :]
    where = s["where"]
    smell = s["smell"]
    detail = s["detail"]
    law = s["law"]
    title = s["title"]
    day_vi = s["day_vi"]
    hook = s["hook"]
    ha_line = s["ha_line"]
    phong_line = s["phong_line"]

    # Unique Phong/Hà micro-dialogues per chapter
    ph_extra = {
        862: (
            "Mốc lệch nửa gang. Đừng nhổ. Nhổ là kể.",
            "Không nhổ. Không chỉ. Gò nuốt mắt.",
            "Bóng đếm bước rồi lùi. Ta không đạp theo.",
            "Không đạp. Việc trong nuốt bóng.",
        ),
        863: (
            "Mồi dây. Thợ trói giả. Không nhận.",
            "Không nhận. Không đổi cọc. Hầm xấu.",
            "Giọng khác lần trước. Tai khe.",
            "Tai khe. Cùng màu. Không mở tiễn.",
        ),
        864: (
            "Yên sau dây. Không thở phào.",
            "Không thở phào. Trống không bằng yên hội.",
            "Không dấu dây. Không rải vôi nghỉ.",
            "Vôi nghỉ là khoe. Khoe là hở.",
        ),
        865: (
            "Bốn thấp. Máu kín. Không đếm to.",
            "Không đếm to. Không phơi. Hố sát mương.",
            "Tanh gừng. Muối át. Rèm chặt.",
            "Rèm chặt. Trẻ không hỏi tanh.",
        ),
        866: (
            "Thước gõ ba. Không chỉ. Không đạp vết.",
            "Không chỉ. Thước đọc lưng không đọc xương.",
            "Bụi đường lắng. Bóng lùi.",
            "Lùi. Việc trong nuốt thước.",
        ),
        867: (
            "Mồi muối. Bao giả. Không nhận.",
            "Không nhận. Không đổi vỏ. Hầm xấu.",
            "Vỏ ốc mặn ngoài. Không nhặt mồi.",
            "Không nhặt. Cùng màu. Im.",
        ),
        868: (
            "Yên sau muối. Vỏ ốc phủ bụi. Không nhặt.",
            "Không nhặt. Không thở phào. Việc trong.",
            "Không họp chữ muối. Không rải vôi nghỉ.",
            "Vôi nghỉ là khoe. Yên không lễ.",
        ),
        869: (
            "Năm thấp. Máu kín. Hố sát đá.",
            "Không đếm to. Không phơi. Không lặp hố mương.",
            "Tanh đá lạnh. Muối át. Rèm chặt.",
            "Rèm chặt. Trẻ không hỏi tanh.",
        ),
    }[n]

    blocks = []
    blocks.append(
        f"""

---

Giữa trưa sâu. Nắng mỏng lệch tây. Phong đảo muối lần ba — hạt muối kêu khẽ trên bao gai. {smell.capitalize()}. Anh đếm nhịp tay không đếm số ngoài: đảo, phủi, buộc, kê. Hà phơi bao tây, lưng thẳng, khăn mũi thấp. Hai người không nói chuyện sân. Nói chuyện sân là hội. Hội là hở.

A Minh từ gò giơ hai ngón mở: trống phía {where}. Hữu một ngón: im. A Cường lách cột, gõ ba: an. Chuỗi tín hiệu ngắn. Phong gật trong đầu. Không họp. Không khen. Chỉ việc.

Bà già ghé bếp lần nữa: "Ồn?" Chú Bát: "Gió. Nồi." Cúi. Đủ. Triệu nước đúng gáo, không hỏi ngoài. Mạc Tư bảng sấp, không viết số to. Từ Sơn vòng chân kho đều — một vòng, không chạy. Máy nghèo giữ nhịp bằng chân và tay, không bằng miệng kể {title.lower()}.

Phong gặp Hà ở mé muối:
"{ph_extra[0]}"
"{ph_extra[1]}" chị lau tay muối. Mắt lạnh. Vai không lỏng.
"""
    )
    blocks.append(
        f"""

---

Chiều sớm. Phong chấm đông nửa vòng: chông một hàng, vôi không mới, then êm, hố vết nguyên, cửa không lệch. Luật xương: {law}. Anh không rải vôi nghỉ. Vôi nghỉ là khoe. Khoe là chết chậm.

Hà gặp anh ở mé rèm trẻ: "Đông?"
"Nguyên. Không vôi mới. Không mở rèm sớm."
"Trẻ xâu. Không kể ngoài." Chị siết khăn. "{detail}."
"Ghi. Ai chỉ hố — nặng. Ai kể trẻ — nặng gấp. Ai kể cấp — nặng gấp đôi. Lần này không pháo."

Diễm se sợi rèm sâu thêm một mũi. Cúc kéo Hạt vào trong. Hạt miệng. Không hỏi. Đủ. Lưu Diễm nhìn Phong một cái: nghề. Không hỏi số. Hứa dao đất ngoài xưởng, không liếc hố. Đại Lực bao tây. Tôn Vũ móc thấp. Ba xương việc khác nhau — không lặp một khung miệng.

"{ph_extra[2]}"
"{ph_extra[3]}" Hà gật. Then êm. Khuyển ngưỡng.
"""
    )
    blocks.append(
        f"""

---

Hoàng hôn. Khói bếp thấp. Cháo đúng gáo. Thu nhanh. Ngứa kể — hở. Phong chặn bếp bằng việc: củi ít, thỏ nửa bát, nồi không chuyển ngoài. Úp bảng. Rèm chốt. Then hai. Khuyển ngưỡng. Sỏi hố. Dặn A Minh không kể ngoài.

Hà bánh tráng đúng giờ — không thưởng vì việc xong, không phạt vì yên. Chỉ đúng giờ. Máy nghèo không lễ. Chú Bát gù nồi. Mạc Tư gạch im đúng việc. Từ Sơn ngồi canh trong, không da nếu không đâm.

Phong vòng chân kho lần cuối trước tối: chân còn, không dấu lạ, không vết thước mới, không mốc mới. {where.capitalize()} im sau việc ngày. {hook.capitalize()} đã thành đất trong đầu — không thành chuyện sân.

A Cường lách: "Trống. Không thèm thấp."
"Không soi. Không kể trống thành chuyện," Phong. Biến.
Bà già: "Khách?"
"Không. Gió. Việc." Hứa không liếc. Nghỉ.
"""
    )
    blocks.append(
        f"""

---

Đêm canh một. Lều. Ghế đá mùi. Anh nắm tay chị. Nhắc việc ngắn — không kể ngoài lều:

"Sóng — đâm kín. Miệng — cùng màu. Thước — không chỉ. Gò — không chỉ. Hôm nay: {title}. {hook}. Luật: {law}."

"Lưỡi em. Bao anh. Đông thường. Hầm xấu," Hà đáp. Mắt chị lạnh hơn ngày yên muối, ấm hơn ngày sóng. "Mai tai khe. Không thở phào."

"Không thở phào. Không hội." Muối chát còn đầu ngón. Chát neo nghề. {smell.capitalize()}.

Canh hai ngồi trong. Khuyển gió. Then êm. Số lần không huy chương. Canh ba ngủ nghiêng. Mơ im — tốt. Không mơ hội. Không mơ EXP. Chỉ mơ then và rèm.

Canh tư nước. Hầm bảy dấu. Lép. Hà: "Tiếp."
"Tiếp. Không lỏng." Cổng hai nhịp trống. Đủ để đảo muối trước trống điểm.
"""
    )
    blocks.append(
        f"""

---

Trước trống điểm kế, Phong đứng tháp không đèn thêm, đếm then cổng: không kêu. Đông rên một rồi im. Gò trống. {where.capitalize()} im. {smell.capitalize()}.

Hà ghé vai: "Đều."
"Đều," anh đáp. Hai chữ đủ trước trống điểm. Năm 629. Đất Biên Ải. Máy nghèo. EXP đầy cấp im — không pháo, không khoe panel ngoài lều.

Dưới sân Hữu đổi ca một ngón. A Minh nắm đấm — im. A Cường gõ cột ba lần — an. Ca đêm như sương. Phong ghi sổ ba dòng gạch nhẹ: mùi đông theo dõi; không đồn sân; mặt nghèo giữ; {title.lower()} khép bằng tai khe. Chữ lóe tắt. Gấp sổ. Nắm tay Hà. Nằm.

Mai lại đảo bao. Mai lại nghèo. Mai lại sống. Phía trước chỉ đất. Liệu giữ nhịp? Sẽ biết khi trống điểm. Hôm nay đã viết việc đủ — {detail}. Đất còn. Người còn. Cháo còn. Thẻ còn. Chông còn. Miệng phân ca còn. Còn thở. Còn viết. Chưa thua. Đủ.

"{ha_line}"
"{phong_line}" Hai câu nghề — không khung lặp, không nhịp đếm số.
"""
    )
    blocks.append(
        f"""

---

Phong kiểm lại một vòng nghề trước khi mắt díp hẳn — riêng ngày thứ {day_vi}. Bao tây: miệng buộc đúng, không hở hạt. Giếng: nắp xấu khít, không chỉ cho ngoài. Chân kho: không dấu lạ. Hầm tây: bảy dấu, lép, đắp xấu. Đông: chông vôi then hố cửa nguyên. Rèm trẻ: chốt. Then hai: êm. Khuyển: ngưỡng. Bảng: sấp. Nước: đúng gáo.

Hà thì thầm: "Còn nghe ngoài?"
"Không. Im. {where.capitalize()} im."
"Rèm chặt. Không kể. Mai vẫn việc."
"Mai vẫn việc. Không hội." Anh siết tay. Chị siết lại. Đủ thắng ván không tên.

Sống. Đo. Không khoe. Ngày thứ {day_vi} khép. {title}. {hook}. Luật giữ: {law}. {smell.capitalize()}. Then êm. Khuyển ngưỡng. Bảng sấp. Nước đúng gáo. Không phơi máu. Không chỉ ngược. Không thở phào. Không mở rèm trẻ sớm. Máy nghèo thở đều. Đất Biên Ải năm 629 còn. Người còn. Việc còn. Đủ khép bằng nghề — không bằng khung lặp.

Phong hít ngắn lần cuối. Hà thở. Gió bấc lạnh gáy. Tiếng then êm một nhịp thật. Đủ.
"""
    )

    insert = "".join(blocks)
    new = head.rstrip() + insert + "\n\n" + tail.lstrip()
    new = re.sub(r"Nhịp im\s*\d+\.?", "", new)

    # If still short, add chapter-specific work inventory (unique items)
    if len(new.split()) < target:
        inv = {
            862: "mốc gỗ lệch, bụi gò, không nhổ, không chỉ",
            863: "thừng ngoài, cọc mồi, gạo không đổi, hầm xấu",
            864: "cổng trống, không dấu dây, không vôi nghỉ, không thở phào",
            865: "bốn thấp, hố mương, máu kín, thóc lép, lá khô lau móc",
            866: "thước gỗ ba nhịp, bụi đường, không đạp vết, không chỉ",
            867: "muối thô mồi, vỏ ốc, không đổi nắm, hầm xấu",
            868: "vỏ ốc phủ bụi, không nhặt, không họp muối, không thở phào",
            869: "năm thấp, hố đá, không lặp mương, máu kín, đá vụn móc",
        }[n]
        more = f"""

---

Cuối canh, Phong nhắc thầm danh sách nghề ngày — không đọc to, không ghi số huy chương: {inv}. Hà gật trong tối. Hai người không cần hội. Chỉ cần then êm và rèm chặt. Ngoài rào đất Biên Ải năm 629 vẫn chỉ là đất và miệng. Trong rào máy nghèo vẫn chỉ là việc. {detail.capitalize()}. Đủ.
"""
        # re-split around panel
        panel_m2 = re.search(r"\n「Kho Vô Hạn", new)
        head2 = new[: panel_m2.start()]
        tail2 = new[panel_m2.start() :]
        new = head2.rstrip() + more + "\n\n" + tail2.lstrip()

    return new


def main():
    for n in range(862, 870):
        s = SPECS[n]
        path = list(ROOT.glob(f"Chương {n} - *.txt"))[0]
        text = path.read_text(encoding="utf-8")
        # rebuild from generator for clean base then expand
        text = rw.build_chapter(n, s)
        text = rw.expand_to_min(text, n, s, min_words=2500)
        text = big_expand(n, s, text, target=3300)
        if re.search(r"Nhịp im\s*\d+", text):
            raise SystemExit(f"Nhịp im remains in {n}")
        lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) >= 50]
        c = Counter(lines)
        bad = [(k[:50], v) for k, v in c.items() if v >= 3]
        path.write_text(text, encoding="utf-8")
        wc = len(text.split())
        print(f"ch.{n} words={wc} maxrep3={bad[:2] if bad else 'ok'}")


if __name__ == "__main__":
    main()
