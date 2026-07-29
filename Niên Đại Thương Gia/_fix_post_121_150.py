# -*- coding: utf-8 -*-
import glob, re, json, sys, shutil
from pathlib import Path
sys.path.insert(0, r"C:/Dev/MythLab/scripts")
import strict_score as ss

ROOT = Path(r"C:/Dev/XLab_MTC/Niên Đại Thương Gia")
cfg = json.load(open(ROOT/".mythlab_score.json", encoding="utf-8"))
led = json.load(open(ROOT/"system_ledger.json", encoding="utf-8"))["chapters"]
BACKUP = ROOT / "_fix_backup_post_121_150"
BACKUP.mkdir(exist_ok=True)

def gp(n):
    fs = list(ROOT.glob(f"Chương {n} - *.txt"))
    assert fs, n
    return fs[0]

def skill_line(n):
    sk = led[str(n)]["skills"]
    pick = sk[-3:] if len(sk) >= 3 else sk
    return ", ".join(pick)

def panel(n, note):
    c = led[str(n)]
    exp = f"{c['exp_total']:,}"
    sp = f"{c['space_m2']:,}"
    sk = skill_line(n)
    return (
        "============================================================\n"
        f"「Hệ thống — GHI NHẬN ch.{n}」\n"
        f"Năm: {c['year']}\n"
        f"Tổng EXP: {exp} (+{c['exp_delta']} nhịp này)\n"
        f"Không gian kho: {sp}m² (+{c['space_delta']}m²)\n"
        f"Kỹ năng trọng yếu: {sk}\n"
        f"Ghi chú: {note}\n"
        "============================================================\n"
    )

def score(t):
    return ss.score_chapter(t, 3000, 4200, True, cfg)

VI = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐÀ-ỹ]")

def is_unaccent_line(s):
    s = s.strip()
    if len(s) < 35:
        return False
    if VI.search(s):
        return False
    letters = sum(c.isalpha() for c in s)
    if letters < 25:
        return False
    return bool(re.search(r"\b(Hung|ong |mot |cua |nhu |khong |va |cho |voi |tu |da |nay |thi |la |Minh|Lan)\b", s, re.I))

PAD_START_MARKERS = [
    "Mot hom,", "Mot lan,", "Mot buoi", "Mot chieu", "Mot ngay", "Mot mua",
    "Bay gio, cuoc song", "O cam oi", "O nho ngay", "Cuoi tuan, Hung dua gia dinh",
    "Hùng nhận lời tham dự một buổi tiệc",
    "Hùng mở một khoá đào tạo nội bộ",
    "Hùng ký quyết định thành lập Quỹ Học bổng",
    "Một ngày mùa thu, Hùng nhận được thư mời tham dự lễ tốt nghiệp",
    "Sang som, Hung nhan",
    "Mot lân, Hung đoc",
    "Hung gặp môt nhom sinh viên",
    "Khi nghi toi con minh",
    "Hom nay, Hung thuc day",
    "Mot doan khach quoc te",
    "Hon 50 nam song",
    "Khi moi đen Sai Gon",
    "Nhieu nguoi hoi ve ton giao",
    "Cuộc đời là những câu chuyện",
    "Trong phòng khách, Hùng mở tủ sách",
    "Đêm xuống, Hùng nằm trên giường, mắt mở, nhìn lên trần nhà. Bên cạnh, bà Hà đã ngủ say",
    "Chiều tà, Hùng ngồi bậc thềm",
    "Mot lan cuoi cung, Hung truoc khi ve huu",
    "Hung mo rong san xuat ra tinh ngoai",
    "O thay, dang sau moi hop dong",
    "Cuoc đoi cua Hùng",
    "Cuoc đoi cua Hung",
    "Hom ay la ngay cuoi",
    "Mua xuan nam 1989, Hung mo them",
    "Sau nay, khi Thuong Gia da lon",
    "Hung noi voi Minh: 'Con thay khong",
    "Mot lan, Hung bi doi thu",
    "Doi thu khong dung lai",
    "Sau nhieu lan doi thu lat keo",
    "Va that la, nhung gi ong de lai",
    "Teaser:",
    "Hùng nhận được telex từ đối tác Singapore. Mẫu hàng mới vừa được kiểm định",
    "Sau khi mở rộng nhà máy, Hùng cần tìm một quản đốc mới",
    "Một buổi trưa, Hùng xuống nhà máy ăn cơm cùng công nhân. Hiền ngồi cạnh",
    "Một tuần sau khi nhận Hiền làm quản đốc",
    "Giữa lúc mở rộng sản xuất, Hùng nhận được tin một người chú họ",
    "Từ ngày có Hiền làm quản đốc",
    'Hùng ngồi trong phòng, lật cuốn sổ tay cũ. Đến trang cuối, ông thấy mình viết: "Nếu mất tất cả',
    "Một chiều mưa, Hùng ngồi trong quán cà phê cóc",
    "Một hôm, Hùng nhận được một lá thư của một giáo sư kinh tế",
    "Hùng quyết định viết một cuốn sách",
    "Cuối tuần, Hùng đưa cả gia đình đi chơi Vườn Bách Thảo",
    "Sau nhiều năm làm ăn, Hùng nhận ra một chân lý đơn giản",
    "So vay ngân hàng đầu tiên",
    "Khi Thuong Gia mo rong, Hung can mot nguoi",
    "Mot lan, Hung đoc thay mot bai bao",
    "Khi nhin lai, Hung thay cuoc đoi",
    "O cam oi đoi",
    "Bay gio, cuoc song đa khac",
    "Mot hom, Hung va ban di cau ca",
    "Hung nho mai mot ky niem",
    "Mot lan, Hung tham gia khoa hoc",
    "Mot chieu cuoi tuan, Hung rong Minh",
    "Mot lan, Hung cung ba Ha di an toi",
    "Hùng ghé thăm một người bạn cũ đang mở tiệm sửa xe đạp",
    "Bây giờ Thương Gia có cả một đội ngũ kỹ thuật với máy móc hiện đại",
    "Một buổi tối, Hùng nhận được điện thoại từ một đối tác cũ ở Quảng Ninh",
    "Một lần, Hùng mời hai đối tác nước ngoài về nhà ăn cơm",
    "Hùng đi tham quan một bảo tàng",
    "Những chuyến công tác nước ngoài dạy Hùng nhiều bài học",
    "Qua su nghiệp, Hung đa xay dung",
    "Nhin nhung đua chau nho",
    "May hom nay tot khong",
]

CUT = {
124: 145,
130: 71,
133: 75,
135: 49,
141: 81,
143: 175,
}

NOTES = {
123: "Đội XK 7 người — họp 30 phút, lương công khai, Quang/Duyên/Vinh vào việc",
124: "Ba lớp hàng vs TQ; xưởng Hà Đông; nhãn Hà Nội; Tanaka −15% — giữ uy tín",
130: "Lan qua thử thách 3 ngày — chìa khóa chuyển giao có tên",
131: "Singapore — lô đầu 6 chủng loại, PSB; không chạy giá Thái",
133: "Penang Lim nhãn song ngữ; Manila Martinez; chọn chân không chọn to",
135: "Tokyo Tanaka sửa phạt; Seoul Park bắt lỗi dịch bảo hiểm; chờ Sato",
139: "Seoul Daesang Logistics — 20 container gạo/mì; điều 7 đàm 0.5%",
141: "Chuyến bay đầu Mỹ 1990 — Narita/Anchorage/LA; bà Lê; Little Saigon",
143: "Hung MTC Inc.; Phạm+Hạnh QC; 5 rủi ro Linda; lỗi xưởng 12%→6%",
}

def load_closes():
    # closes stored as separate utf8 file next to script
    p = ROOT / "_closes_121_150.json"
    return json.loads(p.read_text(encoding="utf-8"))

def find_pad_start(lines):
    start_scan = max(20, len(lines)//3)
    for i in range(start_scan, len(lines)):
        l = lines[i].strip()
        if not l:
            continue
        if l.startswith("===") or "Hệ thống" in l or "GHI NHẬN" in l:
            continue
        if is_unaccent_line(l):
            return i
        for m in PAD_START_MARKERS:
            if l.startswith(m) or (len(m) > 20 and m in l[:100]):
                return i
    return None

def extract_core(n, text):
    lines = text.splitlines()
    if n == 123:
        idx = None
        for i, l in enumerate(lines):
            if "Bên ngoài, mưa đã tạnh" in l:
                idx = i
                break
        if idx is not None:
            core_lines = lines[: idx + 1]
        else:
            core_lines = lines[:99]
    elif n in CUT:
        core_lines = lines[: CUT[n]]
    else:
        pad_i = find_pad_start(lines)
        if pad_i is None:
            core_lines = []
            for i, l in enumerate(lines):
                if "Hệ thống" in l or "GHI NHẬN" in l:
                    break
                if l.strip().startswith("===") and i > 5:
                    rest = "\n".join(lines[i : i + 5])
                    if "Hệ thống" in rest or "GHI NHẬN" in rest:
                        break
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("==="):
                        break
                core_lines.append(l)
        else:
            core_lines = lines[:pad_i]
    while core_lines and (not core_lines[-1].strip() or core_lines[-1].strip().startswith("===")):
        core_lines.pop()
    return "\n".join(core_lines).rstrip() + "\n"

def rebuild(n, closes):
    path = gp(n)
    raw = path.read_text(encoding="utf-8")
    shutil.copy2(path, BACKUP / path.name)
    raw2 = raw.replace("Mở rộngsang", "Mở rộng sang").replace("Mở rộngĐông", "Mở rộng Đông")
    core = extract_core(n, raw2)
    close = closes[str(n)].strip() + "\n\n"
    pan = panel(n, NOTES[n])
    out = core.rstrip() + "\n\n" + close + pan
    if not out.endswith("\n"):
        out += "\n"
    path.write_text(out, encoding="utf-8", newline="\n")
    r = score(out)
    print(
        f"Ch{n}: final={r['final']:.2f} w={r['metrics']['words']} hf={r['hard_fails']} "
        f"van={r['axes']['van_chuong']} nv={r['axes']['nhan_vat']} cau={r['axes']['cau_truc']} "
        f"cont={r['axes']['continuity']} he={r['axes']['he_thong']} "
        f"cd={r['metrics']['char_density']:.2f} sd={r['metrics']['sensory_density']:.2f} dlg={r['metrics']['dialogue']}"
    )
    return r

def strip_residual_pad_all():
    """Strip residual pad from ALL 121-150 that still pass but have garbage tails."""
    fixed = []
    for n in range(121, 151):
        if n in (123, 124, 130, 131, 133, 135, 139, 141, 143, 145):
            continue  # handled specially
        path = gp(n)
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        # find panel
        pidx = None
        for i, l in enumerate(lines):
            if "Hệ thống" in l or "GHI NHẬN" in l:
                pidx = i
                break
        if pidx is None:
            continue
        # scan for pad before panel
        pad_i = None
        start_scan = max(20, pidx // 3)
        for i in range(start_scan, pidx):
            l = lines[i].strip()
            if not l:
                continue
            if is_unaccent_line(l):
                pad_i = i
                break
            for m in PAD_START_MARKERS:
                if l.startswith(m) or (len(m) > 25 and m in l[:100]):
                    pad_i = i
                    break
            if pad_i is not None:
                break
        if pad_i is None:
            # still clean double trailing seps after panel
            new_lines = lines[:]
            # extract panel block
            # just drop extra === after last content
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            # collapse multiple trailing ===
            # rebuild: body + single panel ending
            text = "\n".join(new_lines) + "\n"
            # remove double sep at end
            text2 = re.sub(r"(=\n){2,}={0,}\s*$", "============================================================\n", text)
            # simpler: if ends with two seps
            text2 = re.sub(
                r"\n={10,}\s*\n={10,}\s*$",
                "\n============================================================\n",
                text,
            )
            if text2 != raw and text2 != text:
                shutil.copy2(path, BACKUP / path.name)
                path.write_text(text2, encoding="utf-8", newline="\n")
                fixed.append((n, "dsep"))
            continue
        # cut pad, keep panel (may be incomplete - try keep as-is)
        shutil.copy2(path, BACKUP / path.name)
        body = lines[:pad_i]
        while body and (not body[-1].strip() or body[-1].strip().startswith("===")):
            body.pop()
        # panel from pidx
        panel_lines = lines[pidx:]
        # trim trailing double seps
        while len(panel_lines) >= 2 and panel_lines[-1].strip().startswith("===") and panel_lines[-2].strip().startswith("==="):
            panel_lines.pop()
        # ensure panel has year
        pan_text = "\n".join(panel_lines)
        if "Năm:" not in pan_text:
            # rebuild panel from ledger with note from old if any
            note = f"ch.{n}"
            for l in panel_lines:
                if l.strip().startswith("Ghi chú:"):
                    note = l.split(":", 1)[-1].strip()
            pan_text = panel(n, note).rstrip()
        out = "\n".join(body).rstrip() + "\n\n" + pan_text.strip() + "\n"
        path.write_text(out, encoding="utf-8", newline="\n")
        fixed.append((n, f"pad@{pad_i}"))
    return fixed

def trim_ch145():
    path = gp(145)
    raw = path.read_text(encoding="utf-8")
    shutil.copy2(path, BACKUP / path.name)
    lines = raw.splitlines()
    # Keep strong core: through main Bolsa/Bằng arc; drop redundant home breakfast loop if duplicated
    # Find panel
    pidx = None
    for i, l in enumerate(lines):
        if "Hệ thống" in l or "GHI NHẬN" in l:
            pidx = i
            break
    body = lines[:pidx] if pidx else lines
    # Remove trailing soft home scenes after main close if words too high
    # Find "Xích lô rẽ vào phố Xã Đàn" as late beat - keep through that + short end, drop extra breakfast if needed
    text_body = "\n".join(body)
    # Drop paragraphs that are pure recap lists after the six-contact climax
    # Heuristic: keep first ~3800 words of body
    words = text_body.split()
    if len(words) > 4000:
        # cut at paragraph boundary near 3900 words
        acc = []
        count = 0
        paras = text_body.split("\n\n")
        for p in paras:
            pw = len(p.split())
            if count + pw > 3900 and count > 3200:
                break
            acc.append(p)
            count += pw
        text_body = "\n\n".join(acc).rstrip()
    # ensure cliff
    if "ngày mai" not in text_body[-400:].lower() and "?" not in text_body[-400:]:
        text_body += (
            "\n\nHùng gập sổ. Sáu đầu mối đã có tên. Nhưng Bằng vẫn chưa lộ mặt trên giấy tờ Mỹ — "
            "và Lan hỏi khẽ: \"Anh có gọi em cùng đàm không, hay anh lại một mình?\" "
            "Ông không trả lời ngay. Câu hỏi đó sẽ theo ông sang buổi gọi điện sáng mai."
        )
    note = "Hùng thăm dò thị trường Mỹ, sáu đầu mối cộng đồng Việt; Bằng hàng nhái ID"
    out = text_body.rstrip() + "\n\n" + panel(145, note)
    path.write_text(out, encoding="utf-8", newline="\n")
    r = score(out)
    print(
        f"Ch145: final={r['final']:.2f} w={r['metrics']['words']} hf={r['hard_fails']} "
        f"cau={r['axes']['cau_truc']} van={r['axes']['van_chuong']} nv={r['axes']['nhan_vat']}"
    )
    return r

def main():
    closes = load_closes()
    print("=== REBUILD FAILS ===")
    for n in [123, 124, 130, 131, 133, 135, 139, 141, 143]:
        rebuild(n, closes)
    print("=== TRIM 145 ===")
    trim_ch145()
    print("=== STRIP RESIDUAL ===")
    fixed = strip_residual_pad_all()
    print("residual fixed:", fixed)
    print("=== RESCORE 121-150 ===")
    below = []
    rows = []
    for n in range(121, 151):
        t = gp(n).read_text(encoding="utf-8")
        r = score(t)
        rows.append((n, r))
        flag = "OK" if r["final"] >= 9.5 and not r["hard_fails"] else "FIX"
        print(
            f"[{flag}] Ch{n} {r['final']:.2f} w={r['metrics']['words']} "
            f"van={r['axes']['van_chuong']} nv={r['axes']['nhan_vat']} cau={r['axes']['cau_truc']} "
            f"cont={r['axes']['continuity']} he={r['axes']['he_thong']} hf={r['hard_fails']}"
        )
        if r["final"] < 9.5 or r["hard_fails"]:
            below.append(n)
    avg = sum(r["final"] for _, r in rows) / len(rows)
    print(f"AVG={avg:.3f} PASS={30-len(below)}/30 BELOW={below}")

if __name__ == "__main__":
    main()
