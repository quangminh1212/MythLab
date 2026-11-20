"""MythLab Truyện — bản desktop (Windows): chạy reader/server.py trong luồng nền + cửa sổ pywebview.

Chạy từ mã nguồn:  python apps/desktop/desktop.py [--port N] [--port-file FILE] [--no-window]
Bản đóng gói:      MythLab.exe (cùng tham số).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
APPDATA = Path(os.environ.get("APPDATA") or Path.home()) / "MythLab"
LOCAL = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "MythLab"
WIN_FILE = APPDATA / "window.json"
PREFERRED_PORT = 18765  # cổng cố định → origin cố định → localStorage (tiến độ, cài đặt) không mất giữa các lần mở

if not FROZEN:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "reader"))

# bản windowed không có console: stdout/stderr = None → ghi ra file log
if sys.stdout is None or sys.stderr is None:
    LOCAL.mkdir(parents=True, exist_ok=True)
    _log = open(LOCAL / "desktop.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or _log
    sys.stderr = sys.stderr or _log
    import faulthandler

    faulthandler.enable(_log)

import server  # noqa: E402  (reader/server.py)


def load_win() -> dict:
    try:
        w = json.loads(WIN_FILE.read_text(encoding="utf-8"))
        return {"width": max(420, int(w["width"])), "height": max(600, int(w["height"]))}
    except Exception:  # noqa: BLE001
        return {"width": 1200, "height": 820}


def save_win(size: dict):
    try:
        APPDATA.mkdir(parents=True, exist_ok=True)
        WIN_FILE.write_text(json.dumps(size), encoding="utf-8")
    except OSError:
        pass


def start_server(port: int | None):
    for p in ([port] if port is not None else [PREFERRED_PORT, 0]):
        try:
            srv = server.make_server("127.0.0.1", p)
            break
        except OSError:
            if p == 0 or port is not None:
                raise
    threading.Thread(target=srv.serve_forever, name="mythlab-server", daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser(description="MythLab Truyện (desktop)")
    ap.add_argument("--port", type=int, default=None, help=f"cổng (mặc định {PREFERRED_PORT}, bận thì chọn ngẫu nhiên)")
    ap.add_argument("--port-file", help="ghi cổng đang chạy vào file này (để kiểm thử)")
    ap.add_argument("--no-window", action="store_true", help="chỉ chạy server, không mở cửa sổ")
    args = ap.parse_args()

    srv = start_server(args.port)
    port = srv.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    print(f"MythLab desktop: {url}  (edge-tts: {'có' if server.edge_tts else 'không'})", flush=True)
    if args.port_file:
        Path(args.port_file).write_text(str(port), encoding="utf-8")

    try:
        if args.no_window:
            threading.Event().wait()
            return
        import webview

        size = load_win()
        win = webview.create_window("MythLab Truyện", url, width=size["width"], height=size["height"],
                                    min_size=(420, 600), background_color="#ffffff", text_select=True)

        def on_resized(width, height):
            size.update(width=width, height=height)

        win.events.resized += on_resized
        win.events.closed += lambda: save_win(size)
        LOCAL.mkdir(parents=True, exist_ok=True)
        webview.start(private_mode=False, storage_path=str(LOCAL / "webview"))
    except KeyboardInterrupt:
        pass
    finally:
        srv.shutdown()
        srv.server_close()


if __name__ == "__main__":
    main()
