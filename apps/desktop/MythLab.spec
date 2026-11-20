# -*- mode: python ; coding: utf-8 -*-
# PyInstaller: một thư mục, không console → dist/MythLab/MythLab.exe
# Chạy qua build.ps1 (hoặc: pyinstaller --noconfirm apps/desktop/MythLab.spec)
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

HERE = Path(SPECPATH)
READER = HERE.parents[1] / "reader"
ICONS = READER / "static" / "icons"


def make_icon() -> str | None:
    """icon.ico (16–256) từ icons/icon-512.png; thiếu ảnh thì vẽ tạm ô vuông teal."""
    out = HERE / "build" / "icon.ico"
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    src = ICONS / "icon-512.png"
    if src.exists():
        img = Image.open(src).convert("RGBA")
    else:
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, 255, 255), radius=64, fill="#00A19A")
        d.rectangle((72, 64, 124, 200), fill="#ffffff")
        d.rectangle((136, 64, 184, 200), fill="#ffffff")
    img.save(out, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return str(out)


icon = make_icon()
datas = [(str(READER / "static"), "static")]
if (READER / "config.json").exists():
    datas.append((str(READER / "config.json"), "."))
datas += collect_data_files("edge_tts") + collect_data_files("certifi")

a = Analysis(
    [str(HERE / "desktop.py")],
    pathex=[str(READER)],
    datas=datas,
    hiddenimports=["server"] + collect_submodules("edge_tts"),
    excludes=["tkinter", "PIL"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MythLab",
    console=False,
    icon=icon,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="MythLab", upx=False)
