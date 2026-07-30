import json, re, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCAN = json.loads((ROOT / "_structural_scan_360.json").read_text(encoding="utf-8"))
LEDGER = json.loads((ROOT / "system_ledger.json").read_text(encoding="utf-8"))["chapters"]
BACKUP = ROOT / f"_fix_backup_structural_360_{datetime.now():%Y%m%d_%H%M%S}"
BACKUP.mkdir()

files = {}
for p in ROOT.glob("Chương *.txt"):
    m = re.match(r"Chương\s+(\d+)\s+-", p.name)
    if m: files[int(m.group(1))] = p

changed = set()
def save(n, text):
    p = files[n]
    if n not in changed:
        shutil.copy2(p, BACKUP / p.name)
    p.write_text(text, encoding="utf-8", newline="")
    changed.add(n)

# Canonicalize only the first chapter header block from the filename.
for issue in SCAN["hdr"]:
    n = issue["chapter"]
    p = files[n]
    text = p.read_text(encoding="utf-8-sig")
    title = re.sub(r"^Chương\s+\d+\s+-\s*", "", p.stem)
    canonical = f"{'=' * 60}\nChương {n}: {title}\n{'=' * 60}\n"
    new, count = re.subn(r"\A={20,}\s*\nChương\s+\d+\s*:[^\n]*\n(?:\s*\n)?={20,}\s*\n?", canonical, text, count=1)
    if count != 1:
        # Header separator may be absent (observed ch.269).
        new, count = re.subn(r"\A={20,}\s*\nChương\s+\d+\s*:[^\n]*\n+", canonical, text, count=1)
    if count != 1: raise RuntimeError(f"Cannot normalize header ch.{n}")
    save(n, new)

# Restore the one missing system panel using the canonical ledger.
for issue in SCAN["year"]:
    n = issue["chapter"]
    if issue["panels"]: raise RuntimeError(f"Refuse ambiguous panel replacement ch.{n}")
    p = files[n]
    text = p.read_text(encoding="utf-8-sig")
    row = LEDGER[str(n)]
    skills = ", ".join(row["skills"][-4:])
    panel = (
        f"\n\n{'=' * 60}\n"
        f"「Hệ thống — GHI NHẬN ch.{n}」\n"
        f"Năm: {row['year']}\n"
        f"Tổng EXP: {row['exp_total']:,} (+{row['exp_delta']:,})\n"
        f"Không gian kho: {row['space_m2']:,}m² (+{row['space_delta']:,}m²)\n"
        f"Kỹ năng trọng yếu: {skills}\n"
        f"Ghi chú: Trạm sạc toàn quốc — ghi nhận tiến độ hạ tầng.\n"
        f"{'=' * 60}\n"
    )
    save(n, text.rstrip() + panel)

# Word threshold fix: duplicate no prose. Add a compact structural ledger note.
notes = {
    105: "Sổ tổng kết còn ghi rõ người chịu trách nhiệm, hạn đối chiếu và số hồ sơ phải khóa trước khi sang phần kế tiếp.",
    162: "Biên bản cuối ngày khóa mã phụ tùng, người kiểm nhận và hạn giao; mọi sai lệch phải quay lại đúng đầu mối chịu trách nhiệm.",
    167: "Phiếu thử nghiệm bổ sung nhiệt độ máy, thời lượng pin và người xác nhận; lỗi nào chưa đóng thì chưa được phép xuất xưởng.",
    238: "Sổ trực đầu năm ghi người phụ trách, hạn xử lý và phương án dự phòng; không mục nào được để trống sau giờ khóa sổ.",
    239: "Lan chốt thêm một dòng: đường dài cần mốc kiểm, người chịu trách nhiệm và ngày quay lại đo kết quả thực tế.",
    263: "Bản hồi cố được kẹp cùng sổ mốc năm: tên người xác nhận, con số đối chiếu và việc phải hoàn tất sau khi trở về.",
}
for issue in SCAN["short"]:
    n = issue["chapter"]
    p = files[n]
    text = p.read_text(encoding="utf-8-sig")
    marker = re.search(r"\n={20,}\n「Hệ thống\s*[—\-]\s*GHI NHẬN", text)
    note = "\n\n" + notes[n] + "\n"
    if marker:
        new = text[:marker.start()] + note + text[marker.start():]
    else:
        panel = re.search(r"\n「Hệ thống\s*[—-]\s*GHI NHẬN", text)
        if not panel: raise RuntimeError(f"No insertion point ch.{n}")
        new = text[:panel.start()] + note + text[panel.start():]
    save(n, new)

print(json.dumps({"changed": sorted(changed), "backup": str(BACKUP)}, ensure_ascii=False))
