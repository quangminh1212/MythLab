# MythLab Truyện — bản desktop (Windows)

Cửa sổ [pywebview](https://pywebview.flowrl.com/) (WebView2) bọc `reader/server.py`: server chạy trong luồng nền ở
`127.0.0.1`, giao diện là `reader/static`, có Edge TTS (`/api/tts`) như bản chạy bằng `python server.py`.

## Chạy từ mã nguồn

```powershell
python -m pip install -r apps\desktop\requirements.txt
python apps\desktop\desktop.py
```

Tham số: `--port N` (mặc định 18765; nếu bận thì chọn cổng ngẫu nhiên), `--port-file FILE` (ghi cổng đang chạy,
dùng khi kiểm thử), `--no-window` (chỉ chạy server).

Cổng cố định giữ origin cố định, nên tiến độ đọc và cài đặt (localStorage của WebView2) không mất giữa các lần mở.

## Đóng gói

```powershell
powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1          # thêm -Clean để build lại từ đầu
```

`build.ps1` tạo venv riêng ở `apps\desktop\.venv` bằng `python -m venv` (không dùng `py -3.14`), cài
`requirements.txt` rồi chạy PyInstaller với `MythLab.spec`. Kết quả là một thư mục, không có console:
`apps\desktop\dist\MythLab\MythLab.exe`. Icon lấy từ `reader/static/icons/icon-512.png` (Pillow chuyển sang `.ico`).

Không commit `build/`, `dist/`, `.venv/`.

## Dữ liệu của bản đóng gói

| Gì | Ở đâu |
|---|---|
| Giao diện (`static`) + `config.json` mặc định | trong `_internal\` cạnh exe |
| `config.json` của người dùng | cạnh `MythLab.exe` nếu có, không thì `%APPDATA%\MythLab\config.json` |
| Thư viện local mặc định | `%APPDATA%\MythLab\library` (đường dẫn tương đối trong config tính từ thư mục chứa config) |
| Cache GitHub, TTS | `%LOCALAPPDATA%\MythLab\cache` |
| Dữ liệu WebView2 (localStorage, IndexedDB) | `%LOCALAPPDATA%\MythLab\webview` |
| Kích thước cửa sổ | `%APPDATA%\MythLab\window.json` |
| Log | `%LOCALAPPDATA%\MythLab\desktop.log` |

Repo GitHub `Done_*` đọc bằng `GITHUB_TOKEN`/`GH_TOKEN` hoặc `gh auth token` như server thường.
Máy cần WebView2 Runtime (Windows 11 có sẵn).
