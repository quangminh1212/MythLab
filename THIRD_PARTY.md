# Third-party credits / Ghi công bên thứ ba

Giọng đọc chạy trên thiết bị (Piper WASM, Kokoro Lite); mô hình được tải từ Hugging Face / GitHub release vào Cache API, không đi qua máy chủ MythLab. Nguồn, kích thước và SHA-256 nằm trong `web/src/app/player/piper.ts` và `web/scripts/piper-models.json`.

| Giọng | Dữ liệu / tác giả | Giấy phép | Ghi chú |
|---|---|---|---|
| Vivos (10 giọng Nam/Nữ, mặc định `vi_VN-vivos-x_low`) | VIVOS (AILAB, ĐH Khoa học Tự nhiên TP.HCM); mô hình Piper (Rhasspy) | CC BY-NC-SA 4.0 | Chỉ phi thương mại, chia sẻ tương tự |
| Piper v3 (5 giọng) | CakeByVPBank | MIT | Huấn luyện trên dữ liệu giọng tổng hợp |
| Vais1000 | VAIS-1000 (VAIS); mô hình Piper (Rhasspy) | CC BY 4.0 | Cần ghi công |
| 25 giờ (25hours_single) | InfoRe; mô hình Piper (Rhasspy) | Chưa rõ | Dùng phi thương mại cho đến khi làm rõ |
| Kokoro Vietnamese Lite (Nữ Diễm Trinh, Nam Đức Duy) | loanhviet; chưng cất từ contextboxai/Kokoro-Vietnamese và hexgrad/Kokoro-82M; từ điển SEA-G2P (pnnbao97) | Apache-2.0 | Văn bản giấy phép: `web/src/app/player/kokoro/` |

## Thư viện chạy

- **Piper phonemize / espeak-ng** (`@diffusionstudio/piper-wasm`): espeak-ng theo **GPL-3.0**. Dữ liệu espeak được cắt gọn cho tiếng Việt bởi `web/scripts/espeak-trim.mjs`. Các giọng Piper dùng nó để phiên âm; Kokoro Lite có bộ phiên âm riêng và không dùng espeak-ng.
- **onnxruntime-web** (Microsoft): MIT.
- **Phông chữ**: OFL-1.1 / Apache-2.0, xem `web/public/fonts`.

Mã nguồn MythLab: MIT (`LICENSE`).
