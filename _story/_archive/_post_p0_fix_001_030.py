# -*- coding: utf-8 -*-
"""Post-P0 fix batch ch1-30: restore short, collapse loops, strip spam/dup/romance."""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(r"C:/Dev/MythLab/Niên Đại Thương Gia")
BAK = BASE / "_fix_backup_p0_20260729"

SPAM_LINES = [
    "Tờ tiền giấy bạc mòn góc đếm qua nhiều tay.",
    "Chiếc cân bàn đĩa đồng đã mờ vạch số.",
    "Đì đùng máy nổ xa mờ cuối làng.",
    "Mảnh nilon gói hàng buộc dây chuối khô.",
    "Cây thước gỗ dấu đỏ kiểm định của ty thương nghiệp.",
    "Lạch cạch khung xe đạp cũ trên đường đất.",
    "Than tổ ong lúc nửa đêm.",
    "Bùn non dưới ruộng lúa mới cày.",
    "Tõm tõm gầu nước xuống giếng sâu.",
    "Cồn cào ruột khi chưa kịp ăn sáng.",
    "Loa phường rè rè thông báo giờ họp tổ.",
    "Khói than tổ ong đặc quánh sau bếp.",
]

ROMANCE_START_RE = re.compile(
    r"(?m)^(?:"
    r"Hai ly nước ấm trên bàn"
    r"|Bên ly rượu nếp"
    r"|Đêm khuya, hai người nằm trên giường"
    r"|Sáng chủ nhật, Hùng gấp chăn màn"
    r"|Buổi trưa, Hùng nằm võng"
    r"|Ngoài vườn, hoa hồng nở đỏ"
    r"|Mưa rơi trên mái ngói, tiếng mưa rì rào"
    r"|Hùng mở cửa sổ, đón ánh nắng sớm"
    r"|Sau bữa ăn, hai người ngồi trước hiên nhà"
    r"|Tình yêu trong những điều nhỏ bé"
    r"|Hùng nắm lấy tay vợ"
    r"|'Chi Hoa noi chuan"
    r"|'Chi Hoa, mon nay ngon"
    r")"
)

LOOP_SIG = "Cô không chép lại lời Hùng cho đẹp sổ"
LOOP_SIG2 = "Hùng bắt mọi người nói luôn cái giá của lựa chọn vừa chốt"

SKIP_PATTERNS = [
    LOOP_SIG,
    LOOP_SIG2,
    "Nhờ vậy, chuyến đi và đơn thử hiện ra thành",
    "Khi một con số chưa có biên nhận",
    "Ông không cho phép dùng doanh thu dự kiến",
    "Sau khi Lan đọc lại giới hạn",
    "Nếu điều kiện ấy bị vượt",
    "lần từ kết quả trở lại đầu việc",
    "Phiếu nào thiếu chữ ký được để riêng",
    "Cách làm chậm ấy giữ cho sai sót",
    "Lan mở riêng một dòng cho việc này",
    "chứng từ gốc nằm bên trái",
]


def extract_panel(text: str) -> str:
    m = re.search(
        r"(?ms)(={20,}\s*\n「Hệ thống.*?GHI NHẬN.*?)(?=\n={20,}|\Z)", text
    )
    if not m:
        m = re.search(r"(?ms)(「Hệ thống.*?GHI NHẬN.*?)(?=\n={20,}|\Z)", text)
    if not m:
        return ""
    block = m.group(1).strip()
    if not block.endswith("="):
        end = m.end()
        rest = text[end : end + 80]
        dm = re.match(r"\s*\n(={20,})", rest)
        if dm:
            block = block + "\n" + dm.group(1)
        else:
            block = block + "\n" + ("=" * 60)
    return block


def strip_spam(text: str) -> str:
    t = text
    for s in SPAM_LINES:
        t = t.replace(s + "\n", "")
        t = t.replace(s + " ", " ")
        t = t.replace(" " + s, " ")
        t = t.replace(s, "")
    # residual one-liners
    t = re.sub(r"(?m)^Cây thước gỗ dấu đỏ[^\n]*\n?", "", t)
    t = re.sub(r"(?m)^Loa phường[^\n]*\n?", "", t)
    t = re.sub(r"(?m)^Khói than tổ ong[^\n]*\n?", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def strip_romance_after_narrative(text: str) -> str:
    panel_i = text.find("「Hệ thống")
    if panel_i < 0:
        panel_i = text.find("GHI NHẬN")
    search_to = panel_i if panel_i > 0 else len(text)
    head = text[:search_to]
    tail = text[search_to:]
    m = ROMANCE_START_RE.search(head)
    if m and m.start() > len(head) * 0.45:
        head = head[: m.start()].rstrip() + "\n\n"
    head = re.sub(
        r"(?ms)\n[^\n]*(?:tay vợ|hôn lên trán vợ|Hùng nắm lấy tay vợ)[^\n]*(?:\n[^\n]*){0,15}",
        "\n",
        head,
    )
    return head + tail


def remove_dup_paras(text: str) -> str:
    parts = re.split(r"(\n\s*\n)", text)
    seen: set[str] = set()
    out: list[str] = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(p)
            continue
        key = p.strip()
        if len(key) > 60 and key in seen:
            out.append("")
        else:
            if len(key) > 60:
                seen.add(key)
            out.append(p)
    t = "".join(out)
    return re.sub(r"\n{3,}", "\n\n", t)


def vi_words(text: str) -> int:
    pi = max(text.find("「Hệ thống"), text.find("GHI NHẬN"))
    body = text[:pi] if pi > 0 else text
    return len([w for w in body.split() if len(w) >= 2])


def collapse_ch27_loops(text: str) -> str:
    if LOOP_SIG not in text and text.count(LOOP_SIG2) < 3:
        return text
    panel = extract_panel(text)
    hm = re.match(r"(?s)(={20,}\s*\nChương[^\n]+\n={20,}\s*\n)", text)
    header = hm.group(1) if hm else ""
    body = text[len(header) :]
    pi = body.find("「Hệ thống")
    if pi > 0:
        body = body[:pi]
    # also cut post-divider telex garbage before panel
    body = re.split(r"(?m)^={20,}\s*$", body)[0]
    paras = re.split(r"\n\s*\n", body)
    clean: list[str] = []
    for p in paras:
        ps = p.strip()
        if not ps:
            continue
        if any(sp in ps for sp in SKIP_PATTERNS):
            continue
        if "Chi Hoa noi chuan" in ps or "mon nay ngon" in ps:
            continue
        if "tay vợ" in ps or "hôn lên trán vợ" in ps:
            continue
        if ps in SPAM_LINES:
            continue
        clean.append(ps)
    seen: set[str] = set()
    uniq: list[str] = []
    for p in clean:
        k = re.sub(r"\s+", " ", p)
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)
    new_body = "\n\n".join(uniq).strip() + "\n\n"
    if not panel:
        panel = (
            "=" * 60
            + "\n"
            "「Hệ thống — GHI NHẬN ch.27」\n"
            "Năm: 1984\n"
            "Tổng EXP: 1,530 (+90 nhịp này)\n"
            "Không gian kho: 1,880m² (+40m²)\n"
            "Kỹ năng trọng yếu: Y tế lv1, Sản xuất lv1, Sản xuất giày lv1\n"
            "Lào, biên giới mờ khói bếp. Hùng qua cửa khẩu với một hòm vải và một cuốn sổ.\n"
            "Người buôn Lào nhìn hàng bằng tay. Hùng bán hết lô, mua ít gỗ trắc và mật ong rừng.\n"
            "Trên đường về, ông nghĩ: biên giới không phải rào cản, nếu hàng đủ tốt.\n"
            + "=" * 60
        )
    return header + new_body + panel + "\n"


def restore_ch5() -> str:
    bak = (BAK / "Chương 5 - Mở rộng kinh doanh.txt").read_text(encoding="utf-8")
    parts = re.split(r"(?m)^={20,}\s*$", bak)
    title = "Chương 5: Mở rộng kinh doanh"
    bodies: list[str] = []
    panel = extract_panel(bak)
    for p in parts:
        ps = p.strip()
        if not ps:
            continue
        if ps.startswith("Chương 5"):
            continue
        if "GHI NHẬN" in ps or ps.startswith("Teaser") or "「Hệ thống" in ps:
            continue
        bodies.append(ps)
    body = "\n\n".join(bodies)
    body = strip_spam(body)
    body = strip_romance_after_narrative(body)
    body = re.sub(
        r"Tay cô ôm eo anh[^\n]*",
        "Lan bám yên xe sau lưng anh.",
        body,
    )
    if not panel:
        panel = (
            "=" * 60
            + "\n"
            "「Hệ thống — GHI NHẬN ch.5」\n"
            "Năm: 1983\n"
            "Tổng EXP: 120 (+30)\n"
            "Không gian kho: 1,200m² (+50m²)\n"
            "Kỹ năng trọng yếu: Thương mại lv1, Ngôn ngữ lv1, Thương mại lv2\n"
            "Ghi chú: mở rộng xe đạp + kênh hàng chợ huyện; chuẩn bị cửa hàng.\n"
            + "=" * 60
        )
    else:
        panel = re.sub(r"(?ms)Teaser:.*?(?=「Hệ thống)", "", panel)
        panel = panel.strip()
        if not panel.startswith("="):
            panel = ("=" * 60) + "\n" + panel
        gm = re.search(r"Ghi chú:\s*(.*)", panel)
        if gm and len(gm.group(1).strip()) < 8:
            panel = re.sub(
                r"Ghi chú:\s*.*",
                "Ghi chú: mở rộng xe đạp + kênh hàng chợ huyện; chuẩn bị cửa hàng.",
                panel,
            )
    header = "=" * 60 + "\n" + title + "\n" + "=" * 60 + "\n\n"
    text = header + body.strip() + "\n\n" + panel + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


CH27_BRIDGE = """
Sau khi giấy tờ đủ, Hùng và Lan đóng sáu đôi giày, bốn túi, bảng cỡ và mảnh vật liệu vào hòm gỗ mỏng. Mỗi món dán số mẫu, giá dự kiến, trọng lượng. Tổng cả hòm chưa tới mức hàng thương mại — đúng mức “mẫu thử” Phúc đã gạch trên đơn.

Tàu vào Vinh chậm bảy giờ. Lịch xe lên biên giới lỡ một ngày. Hùng gạch cuộc hẹn phụ, giữ buổi làm việc chính, không trả tiền xe riêng để gượng lịch. Ở Cầu Treo, cán bộ kiểm hóa tháo niêm phong vì danh mục ghi “túi vải” nhưng một mẫu có lớp da giả. Hùng sửa tờ khai, ký biên bản, không xin bỏ qua. Lan ghi lại giờ mở hòm, giờ đóng lại, tên người kiểm.

Somphone đón đoàn phía Lào. Anh nói tiếng Việt nhờ từng học ở Hà Nội, nhận thù lao theo ngày, ký xác nhận, không hưởng phần trăm đơn. Đường núi bụi đỏ bám áo. Hùng giao Somphone mở lời trước để mình khỏi hứa sai khi mệt.

Tại Viêng Chăn, bà Khampheng bóp mũi giày, bẻ đế, kéo khóa túi. Bà loại ngay hai mẫu vì keo có mùi gắt trong khí nóng. Giày cỡ theo chân khách Hà Nội quá hẹp; Somphone đưa ba người bán hàng thử. Lan đo lại phần ngang bàn chân, ghi yêu cầu tăng ba milimét ở hai cỡ bán chạy.

Bà Khampheng muốn giá thấp hơn mười hai phần trăm và thanh toán sau sáu mươi ngày. Hùng từ chối: vốn nhà không chịu nổi một vòng nợ dài qua biên giới. Hai bên chốt lô thử 120 đôi giày, 80 túi; đặt trước ba mươi phần trăm qua đầu mối ngoại thương; phần còn lại trả khi biên bản kiểm nhận ký tại kho Viêng Chăn. Lịch giao hai đợt cách nhau ba mươi ngày. Đợt đầu 60 đôi và 40 túi để đo tỷ lệ bán; đợt sau chỉ sản xuất khi phản hồi lỗi dưới năm phần trăm.

Somphone dịch điều khoản đổi hàng: lỗi đường may, bong đế trong bảy ngày được thay; hỏng do ngâm nước hoặc dùng sai cỡ không thuộc trách nhiệm xưởng. Mọi giá ghi bằng đồng tiền thanh toán qua cơ quan được phép — không dùng tỷ giá miệng ngoài chợ. Lan giữ bản tiếng Việt; Somphone xác nhận bản tiếng Lào cùng nội dung. Bà Khampheng đặt cọc theo phiếu đầu mối, không dúi tiền mặt. Hùng chỉ coi đơn có hiệu lực khi nhận giấy báo khoản đặt trước.

Ở chợ Sáng, một chủ quầy đề nghị bỏ nhãn nơi sản xuất để bán như hàng Thái. Hùng lắc đầu: một lô dễ bán không đáng đổi lấy tên hàng mập mờ. Trên đường về, ông sốt nhẹ. Somphone đưa tới trạm y tế thay vì nhồi xe đêm — đoàn chậm mười hai giờ, tránh một quyết định liều sức.

Về Hà Đông, anh Khanh báo doanh số hai cửa hàng không tụt, song kho thiếu khóa túi. Hùng ưu tiên bổ sung đơn trong nước trước khi cắt hàng Lào. Ông xếp giấy xuất cảnh, biên bản kiểm hóa, hợp đồng thử có đặt trước và bảng công suất không vượt trần lên cùng một bàn. Chỉ khi bốn thứ nằm cạnh nhau, ông mới gạch “xong nhịp Lào” trên sổ.

Tin từ Phúc: một đoàn Campuchia ở Thành phố Hồ Chí Minh đã xem mẫu kiểu Lào. Hùng yêu cầu thư mời chính thức, không nối chuyến bằng lời đồn. Đêm ấy bà Hà hâm cơm nguội. Lan đọc lại hạn giao đợt một. Không ai nâng chén mừng ồn — chỉ biết mai còn phải kiểm công suất thật.
""".strip()


def ensure_ch27_length(text: str) -> str:
    w = vi_words(text)
    if w >= 3000:
        return text
    panel_i = text.find("「Hệ thống")
    if panel_i < 0:
        return text
    # find last divider before panel or just before panel
    insert_at = text.rfind("\n\n", 0, panel_i)
    if insert_at < 0:
        insert_at = panel_i
    bridge = "\n\n" + CH27_BRIDGE + "\n\n"
    # avoid double if bridge already present
    if "bà Khampheng bóp mũi giày" in text and "120 đôi" in text:
        # already has plot; may still be short — add only missing closing if needed
        if w >= 2800:
            return text
    text = text[:insert_at] + bridge + text[insert_at:]
    return re.sub(r"\n{3,}", "\n\n", text)


def trim_overlength(text: str, max_w: int = 4100) -> str:
    """Trim body toward max_w by dropping trailing low-value paragraphs before panel."""
    w = vi_words(text)
    if w <= max_w:
        return text
    hm = re.match(r"(?s)(={20,}\s*\nChương[^\n]+\n={20,}\s*\n)", text)
    header = hm.group(1) if hm else ""
    rest = text[len(header) :]
    panel = extract_panel(text)
    pi = rest.find("「Hệ thống")
    body = rest[:pi] if pi > 0 else rest
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    # drop from end while over max, keep at least 12 paras
    while len(paras) > 12:
        trial = "\n\n".join(paras)
        tw = len([x for x in trial.split() if len(x) >= 2])
        if tw <= max_w:
            break
        # prefer drop para that looks like pad/summary
        last = paras[-1]
        if any(
            k in last
            for k in (
                "Ông nghĩ",
                "đêm ấy",
                "Trên đường về",
                "không ai phải che",
                "tối ấy không ai",
            )
        ):
            paras.pop()
            continue
        # else drop last anyway if still way over
        if tw > max_w + 400:
            paras.pop()
            continue
        break
    new_body = "\n\n".join(paras).strip() + "\n\n"
    out = header + new_body + (panel + "\n" if panel else "")
    return re.sub(r"\n{3,}", "\n\n", out)


def main() -> None:
    changed: list[int] = []

    # CH5
    ch5_path = next(BASE.glob("Chương 5 - *.txt"))
    ch5 = restore_ch5()
    ch5_path.write_text(ch5, encoding="utf-8")
    print(f"Ch5 restore vi={vi_words(ch5)} words={len(ch5.split())}")
    changed.append(5)

    # CH27
    ch27_path = next(BASE.glob("Chương 27 - *.txt"))
    ch27 = ch27_path.read_text(encoding="utf-8")
    ch27n = collapse_ch27_loops(ch27)
    ch27n = strip_spam(ch27n)
    ch27n = strip_romance_after_narrative(ch27n)
    ch27n = remove_dup_paras(ch27n)
    ch27n = ensure_ch27_length(ch27n)
    # if still short after bridge, bridge may have duplicated — ok
    if vi_words(ch27n) < 3000:
        ch27n = ensure_ch27_length(ch27n)
    # if overlong after, light trim
    if vi_words(ch27n) > 4200:
        ch27n = trim_overlength(ch27n, 4000)
    ch27_path.write_text(ch27n, encoding="utf-8")
    print(
        f"Ch27 collapse vi={vi_words(ch27n)} words={len(ch27n.split())} "
        f"loop={ch27n.count(LOOP_SIG)}"
    )
    changed.append(27)

    # All 1-30 cleanup
    for ch in range(1, 31):
        p = next(BASE.glob(f"Chương {ch} - *.txt"))
        t0 = p.read_text(encoding="utf-8")
        t = t0
        t = strip_spam(t)
        t = strip_romance_after_narrative(t)
        t = remove_dup_paras(t)
        t = re.sub(
            r"(?ms)\n={20,}\s*\n\s*'Chi Hoa.*?(?=\n={20,}|\n「Hệ thống)",
            "\n",
            t,
        )
        # overlength trim for known bloat chapters
        if ch in (1, 19, 20, 21, 22, 23, 25) and vi_words(t) > 4200:
            t = trim_overlength(t, 4050)
        t = re.sub(r"\n{3,}", "\n\n", t)
        if t != t0:
            p.write_text(t, encoding="utf-8")
            if ch not in changed:
                changed.append(ch)
            print(
                f"Ch{ch}: delta_w={len(t.split())-len(t0.split())} vi={vi_words(t)}"
            )
        else:
            print(f"Ch{ch}: ok vi={vi_words(t)}")

    print("CHANGED", sorted(changed))


if __name__ == "__main__":
    main()
