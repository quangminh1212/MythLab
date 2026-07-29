# -*- coding: utf-8 -*-
import json, csv
from pathlib import Path
from collections import Counter, defaultdict

p = Path(r"C:/Dev/XLab_MTC/Niên Đại Thương Gia")
d = json.loads((p / "_eval_95_live.json").read_text(encoding="utf-8"))
results = d["results"]

csv_path = p / "_eval_95_toanbo.csv"
with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(
        [
            "chuong",
            "file",
            "final",
            "pass_9_5",
            "van",
            "cau_truc",
            "nhan_vat",
            "continuity",
            "filler",
            "he_thong",
            "words",
            "dialogue",
            "sensory",
            "pad",
            "maxrep",
            "hard_fails",
            "weakest",
        ]
    )
    for r in sorted(results, key=lambda x: x["num"]):
        ax = r["axes"]
        m = r["metrics"]
        weak = sorted(ax.items(), key=lambda kv: kv[1])[:3]
        w.writerow(
            [
                r["num"],
                r.get("file", ""),
                f"{r['final']:.2f}",
                "YES" if r["final"] >= 9.5 else "NO",
                ax.get("van_chuong"),
                ax.get("cau_truc"),
                ax.get("nhan_vat"),
                ax.get("continuity"),
                ax.get("filler_pad"),
                ax.get("he_thong"),
                m.get("words"),
                m.get("dialogue"),
                round(m.get("sensory_density", 0), 2),
                m.get("pad_total"),
                m.get("maxrep"),
                ";".join(r.get("hard_fails") or []),
                ";".join(f"{a}:{v}" for a, v in weak),
            ]
        )

below = [r for r in results if r["final"] < 9.5]
below_nums = sorted(r["num"] for r in below)

ax_sum = defaultdict(list)
for r in results:
    for a, v in r["axes"].items():
        ax_sum[a].append(v)

bc = Counter()
for r in results:
    f = r["final"]
    if f < 9:
        bc["<9.0"] += 1
    elif f < 9.3:
        bc["9.0-9.29"] += 1
    elif f < 9.4:
        bc["9.3-9.39"] += 1
    elif f < 9.5:
        bc["9.4-9.49"] += 1
    elif f < 9.7:
        bc["9.5-9.69"] += 1
    elif f < 9.9:
        bc["9.7-9.89"] += 1
    else:
        bc["9.9-10"] += 1

parts = Counter()
for n in below_nums:
    if n <= 60:
        parts["P1 1-60"] += 1
    elif n <= 120:
        parts["P2 61-120"] += 1
    elif n <= 180:
        parts["P3 121-180"] += 1
    elif n <= 240:
        parts["P4 181-240"] += 1
    elif n <= 300:
        parts["P5 241-300"] += 1
    else:
        parts["P6 301-360"] += 1

weights = {
    "van_chuong": 20,
    "cau_truc": 15,
    "nhan_vat": 15,
    "continuity": 25,
    "filler_pad": 15,
    "he_thong": 10,
}

md = []
md.append("# Danh gia MythLab — Nien Dai Thuong Gia @ threshold 9.5")
md.append("")
md.append(f"- Tong chuong: {d['total']}")
md.append(f"- PASS >=9.5: {d['pass']}/360 ({100*d['pass']/360:.1f}%)")
md.append(f"- BELOW <9.5: {d['below']}/360")
md.append(f"- AVG final: {d['avg']:.3f}")
md.append(f"- MIN final: {d['min_final']:.2f}")
md.append("- Hard-fail toan series: 0 (continuity/filler/system sach)")
md.append("- Config: min_words=3000 max_words=4200 rebirth=true year 1980-2024")
md.append("")
md.append("## Phan bo diem")
md.append("")
md.append("| Band | So ch |")
md.append("|------|------:|")
for k in ["<9.0", "9.0-9.29", "9.3-9.39", "9.4-9.49", "9.5-9.69", "9.7-9.89", "9.9-10"]:
    md.append(f"| {k} | {bc[k]} |")
md.append("")
md.append("## Trung binh 6 truc")
md.append("")
md.append("| Truc | AVG | MIN | Weight |")
md.append("|------|----:|----:|-------:|")
for a in [
    "van_chuong",
    "cau_truc",
    "nhan_vat",
    "continuity",
    "filler_pad",
    "he_thong",
]:
    md.append(
        f"| {a} | {sum(ax_sum[a])/len(ax_sum[a]):.3f} | {min(ax_sum[a]):.2f} | {weights[a]} |"
    )
md.append("")
md.append("## Ket luan cham")
md.append("")
md.append(
    "**Chua ALL_PASS 9.5.** 307 chuong da >=9.5; 53 chuong con 9.26-9.49."
)
md.append("")
md.append("### Nguyen nhan chinh")
md.append("")
md.append(
    "Tat ca 53 chuong BELOW deu **vuot max_words=4200** (thuc te 4345-7762 VI-tokens)."
)
md.append(
    "Cong thuc: `cau_truc -= min(2.5, (words-4200)/400)` -> cau truc tut 6.0-8.5 du van/nhan vat/continuity tot."
)
md.append(
    "**Khong hard-fail pad/year/panel.** Day la phinh chu tu cac pass expand truoc."
)
md.append("")
md.append("### BELOW theo phan")
md.append("")
for k, v in parts.items():
    md.append(f"- {k}: **{v}** ch")
md.append("")
md.append("### Danh sach 53 chuong < 9.5")
md.append("")
md.append("| Ch | Final | cau | van | nv | words | file |")
md.append("|---:|------:|----:|----:|---:|------:|------|")
for r in sorted(below, key=lambda x: (x["final"], x["num"])):
    ax = r["axes"]
    m = r["metrics"]
    md.append(
        f"| {r['num']} | {r['final']:.2f} | {ax['cau_truc']:.2f} | {ax['van_chuong']:.1f} | {ax['nhan_vat']:.1f} | {m['words']} | {r.get('file','')} |"
    )
md.append("")
md.append("### Fix toi uu ALL_PASS 9.5")
md.append("")
md.append("1. Trim 53 chuong ve **3000-4200** VI-tokens (giu beat, cat lap).")
md.append("2. Khong can rewrite toan bo — van/nv/cont da >=9.")
md.append("3. Ch.180: van=8.3 (sensory 6.58) — them giac quan khi trim.")
md.append("4. (Tuy chon) noi max_words len 5500 neu muon giu ban dai.")
md.append("")
md.append("## Tham khao tinh tiet MTC nen BO SUNG")
md.append("")
md.append(
    "Nguon: MythLab twists + plot-mining 32k MTC (xuyen/trong sinh, he thong, do thi, nien dai)."
)
md.append("Scan series: mot so beat chua co / cuc mong.")
md.append("")
md.append("### A. Gap lon (0 hit) — uu tien cam")
md.append("")
md.append("| # | Tinh tiet MTC | Nguon | Goi y cam |")
md.append("|---|---------------|-------|-----------|")
md.append(
    "| 1 | Song trong sinh — ke thu/an nhan cung quay ve | rebirth #2-3 | P3-P4 ch.160-220: doi thu lo chi tiet chi biet o kiep truoc |"
)
md.append(
    "| 2 | Pha san gia de thau tom | business #8 | P4 2008 ch.221-230: doi thu gia vo no |"
)
md.append(
    "| 3 | Franchise/clone logo + kien nguoc | business #5 | P2-P3 ch.90-140: chi nhanh gia Thuong Gia |"
)
md.append(
    "| 4 | Cong thuc bi quyet thuoc ve doi tac dang no | business #1 | P1-P2 thuc pham/mi ch.54 |"
)
md.append(
    "| 5 | Nguoi than/doi tac tin la CEO doi thu an | business #9 | Mo rong arc ch.180 (Tuan/noi gian) 3-5 ch |"
)
md.append(
    "| 6 | Butterfly: cuu nguoi le ra chet -> timeline thu moi | rebirth #7 | P1 ch.15-40 |"
)
md.append(
    "| 7 | System khong unique — bang xep hang host | system #3 | P5-P6 ch.300-355 |"
)
md.append(
    "| 8 | Quest thuong = no / khe uoc ngam | system #2 | 1 lan thuong space lon + side-quest dao duc |"
)
md.append("")
md.append("### B. Mong (da co nhung chua du xuong)")
md.append("")
md.append("| Tinh tiet | Hit | Bo sung |")
md.append("|-----------|-----|---------|")
md.append("| Tem phieu gia | ~2 | 1 arc P1 ch.8-25 |")
md.append("| Chi diem / so den | ~38 | 1 reveal 'nguoi tot la chi diem' P1 |")
md.append("| Hang cam / buon lau | ~10 | 1 bay phap ly P2-P3 |")
md.append("| Kiem toan | ~92 | Du; them 1 lan so sach che quy den neu hop cast |")
md.append("| Doi Moi / policy whip | rat nhieu | Them 1 policy whiplash dung luc vua build xong chuoi |")
md.append("")
md.append("### C. Da du / khong can nhoi")
md.append("")
md.append(
    "- Space/kho, chi nhanh, nha may, M&A, xuat khau, tu thien, tri an, panel GHI NHAN, motif ba Ha/so tay."
)
md.append("- Khong copy prose tu D:/Dev/MTC_*; chi muon xuong twist + texture nien dai.")
md.append("")
md.append("### D. Template cam 1 tinh tiet/chuong")
md.append("")
md.append("```")
md.append("Setup (truoc 5-20 ch) -> gia phai tra trong ch -> goal MC doi nhe -> micro-reveal cliff")
md.append("CAM: monologue giai thich twist; CAM: lap khung do chu.")
md.append("```")
md.append("")
md.append("## Doc mau chat luong")
md.append("")
md.append("| Ch | Diem | Nhan xet |")
md.append("|----|------|----------|")
md.append("| 1 | 9.32 | Hook trung sinh manh; dai 6498w -> cau=6.0 |")
md.append("| 77 | 9.26 | Dao tao Da Nang tot; phinh 6084w |")
md.append("| 180 | 9.46 | Lan Berlin + noi gian hay; sensory 6.58 |")
md.append("| 200 | >=9.5 | Le 10 nam on |")
md.append("| 350 | >=9.5 | Tri an doi tac gon |")
md.append("| 355 | 9.26 | Climax tot; 5391w phinh |")
md.append("")
md.append("## File kem")
md.append("")
md.append("- `_eval_95_live.json`")
md.append("- `_eval_95_toanbo.csv`")
md.append("- `worklist.json`")
md.append("- `.mythlab_score.json`")
md.append("")
md.append("## Next khi sua")
md.append("")
md.append("1. Batch trim 53 ch ve <=4200w")
md.append("2. Inject 6-8 twist MTC gap vao outline + rewrite dung beat")
md.append("3. autopilot_loop.py --threshold 9.5 den ALL_PASS")
md.append("")

# Vietnamese full report
md_vi = []
md_vi.append("# Đánh giá MythLab — Niên Đại Thương Gia @ threshold 9.5")
md_vi.append("")
md_vi.append(f"- **Tổng chương:** {d['total']}")
md_vi.append(f"- **PASS ≥9.5:** {d['pass']}/360 ({100*d['pass']/360:.1f}%)")
md_vi.append(f"- **BELOW <9.5:** {d['below']}/360")
md_vi.append(f"- **AVG final:** {d['avg']:.3f}")
md_vi.append(f"- **MIN final:** {d['min_final']:.2f}")
md_vi.append("- **Hard-fail toàn series:** 0 (continuity / filler / system sạch)")
md_vi.append("- **Config:** min_words=3000 · max_words=4200 · rebirth=true · 1980–2024")
md_vi.append("")
md_vi.append("## Phân bố điểm")
md_vi.append("")
md_vi.append("| Band | Số ch |")
md_vi.append("|------|------:|")
for k in ["<9.0", "9.0-9.29", "9.3-9.39", "9.4-9.49", "9.5-9.69", "9.7-9.89", "9.9-10"]:
    md_vi.append(f"| {k} | {bc[k]} |")
md_vi.append("")
md_vi.append("## Trung bình 6 trục")
md_vi.append("")
md_vi.append("| Trục | AVG | MIN | Weight |")
md_vi.append("|------|----:|----:|-------:|")
for a in [
    "van_chuong",
    "cau_truc",
    "nhan_vat",
    "continuity",
    "filler_pad",
    "he_thong",
]:
    md_vi.append(
        f"| {a} | {sum(ax_sum[a])/len(ax_sum[a]):.3f} | {min(ax_sum[a]):.2f} | {weights[a]} |"
    )
md_vi.append("")
md_vi.append("## Kết luận chấm")
md_vi.append("")
md_vi.append(
    "**Chưa ALL_PASS 9.5.** 307 chương ≥9.5; 53 chương còn **9.26–9.49**."
)
md_vi.append("")
md_vi.append("### Nguyên nhân chính (cơ học scorer)")
md_vi.append("")
md_vi.append(
    "Cả 53 chương BELOW đều **vượt `max_words=4200`** (thực tế **4345–7762** VI-tokens)."
)
md_vi.append(
    "Công thức: `cau_truc -= min(2.5, (words-4200)/400)` → cấu trúc tụt 6.0–8.5 dù văn/nhân vật/continuity tốt."
)
md_vi.append(
    "**Không hard-fail pad/year/panel.** Đây là phình chữ từ các pass expand trước — không phải lỗi logic continuity."
)
md_vi.append("")
md_vi.append("### BELOW theo phần")
md_vi.append("")
for k, v in parts.items():
    md_vi.append(f"- {k}: **{v}** ch")
md_vi.append("")
md_vi.append(f"### Danh sách {len(below)} chương < 9.5")
md_vi.append("")
md_vi.append("| Ch | Final | cau | van | nv | words | file |")
md_vi.append("|---:|------:|----:|----:|---:|------:|------|")
for r in sorted(below, key=lambda x: (x["final"], x["num"])):
    ax = r["axes"]
    m = r["metrics"]
    md_vi.append(
        f"| {r['num']} | {r['final']:.2f} | {ax['cau_truc']:.2f} | {ax['van_chuong']:.1f} | {ax['nhan_vat']:.1f} | {m['words']} | {r.get('file','')} |"
    )
md_vi.append("")
md_vi.append("### Fix tối ưu để ALL_PASS 9.5")
md_vi.append("")
md_vi.append("1. **Trim** 53 chương về **3000–4200** VI-tokens (giữ beat, cắt lặp giác quan/mở rộng máy).")
md_vi.append("2. Không cần rewrite toàn bộ — van/nv/cont đã ≥9.")
md_vi.append("3. Ch.180: van=8.3 (sensory 6.58) — thêm giác quan Berlin/Hà Nội khi trim.")
md_vi.append("4. (Tuỳ chọn) nới `max_words` lên 5500 nếu muốn giữ bản dài — premium target vẫn 3–3.5k.")
md_vi.append("")
md_vi.append("## Tham khảo tình tiết MTC nên BỔ SUNG")
md_vi.append("")
md_vi.append(
    "Nguồn: MythLab `twists/*` + plot-mining ~32k MTC (xuyên/trọng sinh, hệ thống, đô thị, niên đại)."
)
md_vi.append("Đã scan series bằng grep — một số beat **chưa có / cực mỏng**.")
md_vi.append("")
md_vi.append("### A. Gap lớn (0 hit trong series) — ưu tiên cắm")
md_vi.append("")
md_vi.append("| # | Tình tiết MTC | Nguồn bank | Gợi ý cắm chương |")
md_vi.append("|---|---------------|------------|------------------|")
md_vi.append(
    "| 1 | **Song trọng sinh** — kẻ thù/ân nhân cũng quay về | rebirth #2–3; MTC “Song Trọng Sinh” | P3–P4 (ch.160–220): đối thủ HK/TQ lộ chi tiết chỉ người kiếp trước biết |"
)
md_vi.append(
    "| 2 | **Phá sản giả để thâu tóm** | business #8 | P4 khủng hoảng 2008 (ch.221–230): đối thủ giả vỡ nợ → Hùng suýt mua bẫy |"
)
md_vi.append(
    "| 3 | **Franchise / clone logo** + kiện ngược | business #5 | P2–P3 (ch.90–140): chi nhánh giả “Thương Gia” tỉnh lẻ |"
)
md_vi.append(
    "| 4 | **Công thức bí quyết thuộc đối tác đang nợ** | business #1 | P1–P2 thực phẩm/mì (~ch.54) |"
)
md_vi.append(
    "| 5 | **Người tin cậy là CEO đối thủ ẩn** | business #9 | Mở rộng arc ch.180 (Tuấn/nội gián) thành 3–5 ch |"
)
md_vi.append(
    "| 6 | **Butterfly: cứu người lẽ ra chết → timeline thù mới** | rebirth #7 | P1 sớm (ch.15–40) |"
)
md_vi.append(
    "| 7 | **System không unique — bảng xếp hạng host** | system #3 | P5–P6 (ch.300–355): panel lộ Host #N |"
)
md_vi.append(
    "| 8 | **Quest thưởng = nợ / khế ước ngầm** | system #2 | 1 lần thưởng space lớn + side-quest đạo đức (không phá ledger) |"
)
md_vi.append("")
md_vi.append("### B. Mỏng (đã có nhưng chưa đủ xương)")
md_vi.append("")
md_vi.append("| Tình tiết | Hit hiện tại | Bổ sung |")
md_vi.append("|-----------|-------------|---------|")
md_vi.append("| Tem phiếu giả / cắt tem sổ | ~2 file | 1 arc P1 (ch.8–25) |")
md_vi.append("| Chỉ điểm / sổ đen thôn–đơn vị | ~38 file | 1 reveal “người tốt là chỉ điểm” (niendai #1) ở P1 |")
md_vi.append("| Hàng cấm / buôn lậu chuỗi cung | ~10 file | 1 bẫy pháp lý P2–P3 (business #4) |")
md_vi.append("| Kiểm toán / audit | ~92 file | Đủ; có thể thêm 1 lần sổ sạch che quỹ đen gia đình |")
md_vi.append("| Đổi Mới / policy whiplash | rất nhiều | Thêm 1 nhát đúng lúc vừa build xong chuỗi (niendai #10) |")
md_vi.append("")
md_vi.append("### C. Đã đủ — không nhồi (tránh pad)")
md_vi.append("")
md_vi.append(
    "- Space/kho hệ thống, mở chi nhánh, nhà máy, M&A, xuất khẩu, từ thiện, tri ân đối tác, panel GHI NHẬN, motif bà Hà / sổ tay."
)
md_vi.append(
    "- **Không copy prose** từ `D:\\Dev\\MTC_*`; chỉ mượn **xương twist + texture niên đại**."
)
md_vi.append("")
md_vi.append("### D. Template cắm 1 tình tiết/chương (anti-pad)")
md_vi.append("")
md_vi.append("```")
md_vi.append("Setup (trước 5–20 ch) → giá phải trả trong ch → goal MC đổi nhẹ → micro-reveal cliff")
md_vi.append("CẤM: monologue giải thích twist; CẤM: lặp khung độn chữ.")
md_vi.append("```")
md_vi.append("")
md_vi.append("## Đọc mẫu chất lượng (thủ công)")
md_vi.append("")
md_vi.append("| Ch | Điểm | Nhận xét ngắn |")
md_vi.append("|----|------|---------------|")
md_vi.append("| 1 | 9.32 | Hook trùng sinh mạnh, sensory tốt; **dài 6498w** → cau=6.0 |")
md_vi.append("| 77 | 9.26 | Đào tạo Đà Nẵng chi tiết số liệu tốt; phình 6084w |")
md_vi.append("| 180 | 9.46 | Lan Berlin + nội gián Tuấn hay; van thấp (sensory 6.58) |")
md_vi.append("| 200 | ≥9.5 | Lễ 10 năm — giọng lễ + bà Hà/Lan ổn |")
md_vi.append("| 350 | ≥9.5 | Tri ân đối tác — gọn, đúng di sản |")
md_vi.append("| 355 | 9.26 | Climax nhiệm vụ tối thượng tốt; **5391w** phình |")
md_vi.append("")
md_vi.append("## File kèm")
md_vi.append("")
md_vi.append("- `_eval_95_live.json` — full scorer dump")
md_vi.append("- `_eval_95_toanbo.csv` — 360 dòng điểm")
md_vi.append("- `worklist.json` — 53 ch cần fix")
md_vi.append("- `.mythlab_score.json` — config scorer")
md_vi.append("")
md_vi.append("## Next (khi bảo sửa)")
md_vi.append("")
md_vi.append("1. Batch trim 53 ch (disjoint, cap 6 agent) về ≤4200w")
md_vi.append("2. Inject 6–8 twist MTC gap vào outline + rewrite đúng beat (không đụng ledger năm/EXP)")
md_vi.append("3. `python C:/Dev/MythLab/scripts/autopilot_loop.py --dir \"...\" --threshold 9.5` đến ALL_PASS")
md_vi.append("")

report = p / "_EVAL_9_5_REPORT.md"
report.write_text("\n".join(md_vi), encoding="utf-8")
print("csv", csv_path)
print("report", report)
print("PASS", d["pass"], "BELOW", d["below"], "AVG", d["avg"], "MIN", d["min_final"])
print("below", below_nums)
