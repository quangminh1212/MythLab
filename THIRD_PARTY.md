# Third-party credits / Ghi công bên thứ ba

Giọng đọc chạy trên thiết bị (Piper WASM, Kokoro Lite, Kokoro 14 giọng); mô hình được tải từ Hugging Face / GitHub release vào Cache API, không đi qua máy chủ MythLab. Nguồn, kích thước và SHA-256 nằm trong `web/src/app/player/piper.ts` và `web/scripts/piper-models.json`.

| Giọng | Dữ liệu / tác giả | Giấy phép | Ghi chú |
|---|---|---|---|
| Piper v3 (5 giọng) | CakeByVPBank | MIT | Huấn luyện trên dữ liệu giọng tổng hợp |
| Vais1000 (giọng "Mai", nữ) | VAIS-1000 (VAIS); mô hình Piper (Rhasspy) | CC BY 4.0 | Cần ghi công |
| 25 giờ (25hours_single, giọng "Hương", nữ) | InfoRe; mô hình Piper (Rhasspy) | Chưa rõ | Dùng phi thương mại cho đến khi làm rõ |
| Kokoro Vietnamese Lite (Nữ Diễm Trinh, Nam Đức Duy) | loanhviet; chưng cất từ contextboxai/Kokoro-Vietnamese và hexgrad/Kokoro-82M; từ điển SEA-G2P (pnnbao97) | Apache-2.0 | Văn bản giấy phép: `web/src/app/player/kokoro/` |
| Kokoro 14 giọng (kokoro-vi-web; 7 nữ: Diễm Trinh, Mai Linh, Mai Loan, Mỹ Yến, Ngọc Huyền, Storyvert, Thục Trinh; 6 nam: Đức An, Đức Duy, Hưng Thịnh, Mạnh Dũng, Phát Tài, Thành Đạt; Tuấn Ngọc chưa rõ giới tính) | relingo; chuyển đổi từ contextboxai/Kokoro-Vietnamese và hexgrad/Kokoro-82M; từ điển SEA-G2P (pnnbao97) | Apache-2.0 | Giấy phép dữ liệu huấn luyện giọng không được nêu. Cần onnxruntime-web 1.30 (`onnxruntime-web-130`, chỉ nạp cho giọng này). Giới tính suy ra từ tần số cơ bản đo được (Đức An, Hưng Thịnh, Phát Tài nằm gần ngưỡng 150-190 Hz nên có thể sai) |

## Thư viện chạy

- **Piper phonemize / espeak-ng** (`@diffusionstudio/piper-wasm`): espeak-ng theo **GPL-3.0**. Dữ liệu espeak được cắt gọn cho tiếng Việt bởi `web/scripts/espeak-trim.mjs`. Các giọng Piper dùng nó để phiên âm; Kokoro Lite có bộ phiên âm riêng và không dùng espeak-ng.
- **onnxruntime-web** (Microsoft): MIT. Bản 1.22.0 cho Piper và Kokoro Lite, bản 1.30.0 (`onnxruntime-web-130`) riêng cho Kokoro 14 giọng.
- **Phông chữ**: OFL-1.1 / Apache-2.0, xem `web/public/fonts`.

Mã nguồn MythLab: MIT (`LICENSE`).

## Giọng đã xem xét nhưng không đưa vào

Không đưa vào vì giấy phép không rõ hoặc không cho dùng tự do: vnhellboy (Alto Trầm, Điềm Đạm, Trầm Vang; không có văn bản giấy phép, tác giả cảnh báo dữ liệu gốc en_US-lessac chỉ cho nghiên cứu), InfoRe espeak của Phoonnx (thẻ MIT nhưng dữ liệu InfoRe không rõ giấy phép), acut (không có giấy phép, tác giả nói là bản thử nghiệm), 19 giọng NGHI-TTS (không có giấy phép, huấn luyện trên âm thanh giọng người nổi tiếng/giọng thương mại), Vivos, mms-graphemes, Valtec, ViFastTts, F5, ZipVoice, viXTTS (phi thương mại hoặc Coqui). Vais1000 int8 (cùng giọng, CC BY 4.0, 19 MB) chạy chậm gấp 8 lần bản thường trong WebAssembly nên không dùng.
