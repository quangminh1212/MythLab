import json, re, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = json.loads((ROOT / "system_ledger.json").read_text(encoding="utf-8"))["chapters"]
BACKUP = ROOT / f"_fix_backup_structural_finish_{datetime.now():%Y%m%d_%H%M%S}"
BACKUP.mkdir()
changed = []

for p in ROOT.glob("Chương *.txt"):
    m = re.match(r"Chương\s+(\d+)\s+-", p.name)
    if not m: continue
    n = int(m.group(1)); text = p.read_text(encoding="utf-8-sig"); original = text
    expected = str(LEDGER[str(n)]["year"])
    text = re.sub(
        rf"(「Hệ thống\s*[—\-]\s*GHI NHẬN ch\.{n}」\s*\nNăm:\s*)\d{{4}}",
        rf"\g<1>{expected}", text
    )
    if n == 246:
        panel = re.compile(r"\n={20,}\n「Hệ thống\s*[—\-]\s*GHI NHẬN ch\.246」\s*\nNăm:\s*2009\n.*?\n={20,}\s*", re.S)
        matches = list(panel.finditer(text))
        if len(matches) > 1:
            for hit in reversed(matches[1:]): text = text[:hit.start()] + text[hit.end():]
    if n == 238:
        marker = re.search(r"「Hệ thống", text)
        if not marker: raise RuntimeError("No panel insertion point ch.238")
        insert_at = text.rfind("\n", 0, marker.start()) + 1
        text = text[:insert_at] + "\nLan bổ sung ngày kiểm lại kết quả.\n" + text[insert_at:]
    if text != original:
        shutil.copy2(p, BACKUP / p.name)
        p.write_text(text, encoding="utf-8", newline="")
        changed.append(n)

print(json.dumps({"changed": changed, "backup": str(BACKUP)}, ensure_ascii=False))
