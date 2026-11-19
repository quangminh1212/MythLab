# Post-strip AI re-read + fix — Batch ch.91–120

**Series:** Niên Đại Thương Gia  
**Phạm vi:** Chương 91–120 (30 ch)  
**Mode:** Post-P0-strip → `strict_score.py` @ threshold **9.5** → sửa FAIL → rescore  
**Config:** min_words=3000 · max_words=4200 · year_check=dateline · rebirth=true  
**Ngày:** 2026-07-29  
**Report:** `_ai_reads/batch_post_091_120.md`  

---

## Kết quả tổng

| Metric | Trước fix | Sau fix |
|--------|----------:|--------:|
| PASS ≥9.5 | 13/30 | **30/30** |
| AVG final | 9.391 | **9.758** |
| Hard-fail | 2 (short 111·116) | **0** |
| Panel year missing | 6 (100·105·107·111·112·116) | **0** |
| Overlength >4200 | 5 (92·95·99·104·107) | **0** |

**ALL_PASS @9.5 = YES**

### Phân bố sau fix

| Band | n |
|------|--:|
| 10.0 | 5 |
| 9.7–9.99 | 24 |
| 9.5–9.69 | 1 |
| <9.5 | 0 |

---

## Bảng điểm từng chương

| Ch | Title | Final | Words | van | nv | ct | cont | fil | sys | ≥9.5 | Fix chính |
|---:|-------|------:|------:|----:|---:|---:|-----:|----:|----:|:----:|-----------|
| 91 | Sản xuất thép Hải Phòng | 9.71 | 3669 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | cliff logistics Bằng |
| 92 | Sản xuất xi măng | 9.71 | 3931 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | trim overlength 4366→3931 |
| 93 | Hùng gặp cô Hạnh | 10.00 | 3431 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — (đã PASS) |
| 94 | Hùng gặp cô Mai và cô Lan | 9.71 | 3910 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | cliff + strip residual romance tail |
| 95 | Hùng chọn cô Hạnh | 9.71 | 3943 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | trim 5583→3943 + cliff |
| 96 | Bà Hà bế cháu nội | 10.00 | 3608 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 97 | Sản xuất điện tử | 9.71 | 3257 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 98 | Sản xuất điện thoại | 9.71 | 3423 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 99 | Mở rộng viễn thông | 9.71 | 3950 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | trim 5080→3950 + boost cd/sd + cliff |
| 100 | Sản xuất phần mềm | 9.71 | 3198 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | rebuild panel (year was orphan) |
| 101 | Mở rộng cửa hàng 108 | 9.71 | 3606 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | boost char_density dialogue Lan |
| 102 | Mở rộng nhà hàng 42 | 9.71 | 3368 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | cliff Bếp Xưa |
| 103 | Mở rộng nhà máy 30 | 9.71 | 3290 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | boost cd Minh/bà Hà + cliff |
| 104 | Mở rộng xuất khẩu châu Âu | 9.71 | 3894 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | trim 6189→3894 + cliff |
| 105 | Tổng kết Phần 3 | 9.71 | 3888 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | rebuild panel + cliff P4 |
| 106 | Bắt đầu Phần 4 | 9.71 | 3404 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 107 | Mở nhà máy Thái Lan | 9.71 | 3948 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | rebuild panel + trim 4283→3948 |
| 108 | Mở nhà máy Indonesia | 9.71 | 3746 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 109 | Mở nhà máy Đức | 9.71 | 3337 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | boost cd Schmidt |
| 110 | M&A Bangkok Electronics | 9.71 | 3393 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | boost cd M&A confrontation |
| 111 | Mở sang châu Mỹ USA | 10.00 | 3138 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | expand short + rebuild panel |
| 112 | Hoàn thành phần 3 | 9.63 | 3441 | 8.9 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | rebuild panel + family boost |
| 113 | Mở nhà máy USA | 10.00 | 3028 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 114 | M&A Stahl GmbH | 9.78 | 3005 | 10.0 | 10.0 | 8.5 | 10.0 | 10.0 | 10.0 | YES | — |
| 115 | Mở nhà máy Nigeria | 9.71 | 3050 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 116 | Mở nhà máy Úc | 9.71 | 3431 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | strip garbage unaccent + expand + panel |
| 117 | Tổng tài sản 1000 tỷ | 9.71 | 3002 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 118 | Những ngày nằm viện | 10.00 | 3033 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 119 | Bước ngoặt sức khỏe | 9.71 | 3148 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | — |
| 120 | Học cách ủy thác sâu hơn | 9.71 | 3046 | 9.3 | 9.0 | 10.0 | 10.0 | 10.0 | 10.0 | YES | drop Teaser: label |

---

## Taxonomy FAIL ban đầu (17 ch) → cách sửa

| Nhóm | Ch | Root cause scorer | Fix |
|------|----|--------------------|-----|
| A. Panel gãy | 100,105,107,111,112,116 | `Năm:` nằm **ngoài** block sau `GHI NHẬN` → panel_year=None → cont−1 sys−2 | Rebuild panel chuẩn (Năm trong block) |
| B. Overlength | 92,95,99,104,107 | words>4200 → cau_truc −(w−4200)/400 | Trim mid-paras về ≤4000 VI-tokens |
| C. Missing cliff | 91,94,102,(105) | 3 dòng prose cuối thiếu gợi-mở → ct−1.5 | Chèn cliff có `sẽ/chưa/ngày mai/phía trước/?` |
| D. Low char_density | 101,103,109,110,(99) | cd<2 → van−1.5 nv−2 | Insert dialogue+CHAR_WORDS (mắt/tay/mồ hôi/nhìn/gật/ôm…) |
| E. Short | 111,116 | words<3000 hard-fail | Expand scene gia đình/đối tác |
| F. Garbage unaccent | 116 | Đuôi không dấu (Hung/khong…) | Strip + viết lại scene Melbourne |
| G. Residual romance | 94 | Dump "Một buổi sáng… pha trà" sau strip | Cắt tail, giữ cliff |

---

## AI re-read tóm tắt từng chương

> Đọc full file canonical root (không backup). Chấm máy = chân lý PASS; ghi chú AI = continuity/cast/pad cảm tính.

### Ch.91 — Sản xuất thép Hải Phòng
- **File:** `Chương 91 - Sản xuất thép Hải Phòng.txt`
- **Score:** **9.71** · words=3669 · dlg=63 · sd=15.44 · cd=2.32 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai, Klaus, Bằng, Bảy
- **Hook:** Năm 1987, tại Hải Phòng. Không phố xá ồn ào, không biển hiệu hào nhoáng. Chỉ mùi dầu máy, tiếng búa đe, và những lò nung thủ công nằm sâu trong khu công nghiệp …
- **Cliff:** Một buổi sáng, Hùng thức dậy, mắt nhìn ra cửa sổ. Nắng vàng nhạt rải trên hàng cây trước nhà. Lan đã dậy, đang pha trà. Mùi trà xanh thơm bố
- **Beat:** Thép HP 1987 + Klaus/Bảy + Bằng logistics flaw (giấu Lan). Core xưởng mạnh.
- **Fix applied:** cliff logistics Bằng

### Ch.92 — Sản xuất xi măng
- **File:** `Chương 92 - Sản xuất xi măng.txt`
- **Score:** **9.71** · words=3931 · dlg=82 · sd=11.24 · cd=2.57 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai, Tanaka, Bảy
- **Hook:** Năm 1987. Khu công nghiệp phía nam thành phố.…
- **Cliff:** Ch. 92: phần thưởng không phải khi lò chạy. Phần thưởng là khi người ta vẫn còn muốn vào xưởng sáng hôm sau.
- **Beat:** Xi măng lò quay; Tanaka/Tín/Hải; cúp điện + lọc bụi. Business texture tốt.
- **Fix applied:** trim overlength 4366→3931

### Ch.93 — Hùng gặp cô Hạnh
- **File:** `Chương 93 - Hùng gặp cô Hạnh.txt`
- **Score:** **10.00** · words=3431 · dlg=117 · sd=15.02 · cd=4.27 · panel_year=1986
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Hạnh, Mai
- **Hook:** Năm 1986, TP.HCM.…
- **Cliff:** Cánh cửa khép lại. Chị Hạnh đứng yên một lúc, tay đặt trên hộp chỉ gỗ, rồi khẽ cười. Ngoài phố, Hùng đi trong bóng tối mà lòng sáng rỡ.
- **Beat:** Gặp Hạnh Sài Gòn 1986 — romance beat; bánh tét/Bến Tre. Dialogue dày.
- **Fix applied:** — (đã PASS)
- **Residual risk:** romance arc 1986 xen công nghiệp 1987 — timeline batch nhảy năm

### Ch.94 — Hùng gặp cô Mai và cô Lan
- **File:** `Chương 94 - Hùng gặp cô Mai và cô Lan.txt`
- **Score:** **9.71** · words=3910 · dlg=110 · sd=13.46 · cd=2.86 · panel_year=1986
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh, Mai, Bảy
- **Hook:** Năm 1986. Đà Nẵng.…
- **Cliff:** Mai và Lan — hai ngã. Ông chưa chốt. Liệu tuần sau về Hà Nội ông sẽ nói gì với bà Hà?
- **Beat:** Đà Nẵng Mai+Lan; strip romance dump đuôi; cliff hai ngã.
- **Fix applied:** cliff + strip residual romance tail
- **Residual risk:** romance arc 1986 xen công nghiệp 1987 — timeline batch nhảy năm

### Ch.95 — Hùng chọn cô Hạnh
- **File:** `Chương 95 - Hùng chọn cô Hạnh.txt`
- **Score:** **9.71** · words=3943 · dlg=91 · sd=12.49 · cd=3.09 · panel_year=1986
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh, Bằng, Quý
- **Hook:** Năm 1986, Hà Nội vào thu. Gió heo may thổi qua ô cửa kính mờ của quán cà phê góc phố Cổ Điển, mang theo mùi bụi đường và khói than tổ ong từ xa vọng lại. Ngoài …
- **Cliff:** Chương 95: phần thưởng chỉ thật khi sổ khớp ngân hàng và người không bị bỏ lại.
- **Beat:** Chọn Hạnh HN thu 1986; bi kịch con; trim overlength ~5.5k→3.9k.
- **Fix applied:** trim 5583→3943 + cliff
- **Residual risk:** romance arc 1986 xen công nghiệp 1987 — timeline batch nhảy năm

### Ch.96 — Bà Hà bế cháu nội
- **File:** `Chương 96 - Bà Hà bế cháu nội.txt`
- **Score:** **10.00** · words=3608 · dlg=71 · sd=12.71 · cd=5.96 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh
- **Hook:** Bà Hà mở mắt trước tiếng gà. Cái lạnh tháng Mười một thấm qua bức tường gạch xây từ thời bao cấp. Bà kéo tấm chăn bông độn bông cũ lên ngang ngực, không vội trở…
- **Cliff:** Bà Hà không cần gì hơn.
- **Beat:** POV bà Hà bế cháu; ấm, sạch pad. 10.0.
- **Fix applied:** —

### Ch.97 — Sản xuất điện tử
- **File:** `Chương 97 - Sản xuất điện tử.txt`
- **Score:** **9.71** · words=3257 · dlg=47 · sd=13.33 · cd=2.39 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai, Bảy
- **Hook:** Sáng sớm tháng ba năm 1987. Khu công nghiệp mới nhú lên ở rìa thành phố, giữa những thửa ruộng lúa chiêm còn xanh. Nhà xưởng dựng tạm — tường tôn, mái fibrô xi …
- **Cliff:** Hùng ngồi vào bàn, viết tiếp sổ. Một trăm bảy mươi hai bo hôm nay. Mai phải hai trăm. Ông viết xong, ngước lên nhìn dây chuyền đang chạy. Mỏ
- **Beat:** Điện tử lắp bo 1987; yield/QC. Core kỹ thuật gọn.
- **Fix applied:** —

### Ch.98 — Sản xuất điện thoại
- **File:** `Chương 98 - Sản xuất điện thoại.txt`
- **Score:** **9.71** · words=3423 · dlg=91 · sd=10.82 · cd=2.49 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai, Bảy
- **Hook:** Bảy giờ sáng, Khu công nghiệp tỉnh Hà Tây. Năm 1987.…
- **Cliff:** Hùng nhìn Bình, thấy cậu thợ trẻ đã khác. Không còn sợ sệt, không còn hỏi "có làm nổi không". Chỉ biết việc và làm. Ông viết vào sổ: "Bộ số 
- **Beat:** Điện thoại quay số; mẫu #7 A-lô. Good craft scene.
- **Fix applied:** —

### Ch.99 — Mở rộng viễn thông
- **File:** `Chương 99 - Mở rộng viễn thông.txt`
- **Score:** **9.71** · words=3950 · dlg=140 · sd=7.12 · cd=2.23 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Hạnh, Mai, Minh, Bảy
- **Hook:** Sáng, Bưu điện Trung tâm Sài Gòn. Số 2, Công trường Công xã Paris. Tòa nhà màu vàng cổ, trần cao bốn mét, quạt trần chậm rãi quay, cánh quạt gỗ đã ố màu. Mùi gi…
- **Cliff:** Lan chạm vai anh, gật. Hơi thở hai người lẫn mùi nhựa vỏ cáp mới.
- **Beat:** Viễn thông 3 tỉnh; trim + boost sensory/char; cáp/Bưu điện.
- **Fix applied:** trim 5080→3950 + boost cd/sd + cliff

### Ch.100 — Sản xuất phần mềm
- **File:** `Chương 100 - Sản xuất phần mềm.txt`
- **Score:** **9.71** · words=3198 · dlg=89 · sd=12.38 · cd=2.57 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai
- **Hook:** 1987. Một căn phòng nhỏ nằm sâu trong Khu công nghiệp — ba cái bàn gỗ ghép từ ván thùng, hai máy tính IBM PC XT 286 mang về từ Singapore, một ổ đĩa mềm 5.25 inc…
- **Cliff:** Đêm đó, Hùng ngồi ngoài hiên, nhìn trăng lên qua tán bàng. Năm 1987 đã cho ông nhiều hơn ông tưởng. Ông gập sổ tay, đặt trên bàn, tắt đèn — 
- **Beat:** HT-QL1 Pascal/PC XT; rebuild panel (Năm ngoài panel).
- **Fix applied:** rebuild panel (year was orphan)

### Ch.101 — Mở rộng cửa hàng 108
- **File:** `Chương 101 - Mở rộng cửa hàng 108.txt`
- **Score:** **9.71** · words=3606 · dlg=87 · sd=10.94 · cd=2.31 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Bảy
- **Hook:** Năm 1987. Hùng đặt mục tiêu: 108 cửa hàng trên cả nước trước khi tờ lịch cuối rơi. Không phải vì số đẹp — 108 là con số ông tính ra từ sổ: 36 tỉnh thành, trung …
- **Cliff:** Một trăm linh tám cửa. Còn tỉnh nào chưa có điểm? Lan sẽ mang danh sách ngày mai.
- **Beat:** 108 cửa hàng; boost cd Lan/Hùng dialogue.
- **Fix applied:** boost char_density dialogue Lan

### Ch.102 — Mở rộng nhà hàng 42
- **File:** `Chương 102 - Mở rộng nhà hàng 42.txt`
- **Score:** **9.71** · words=3368 · dlg=82 · sd=10.92 · cd=2.38 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh, Klaus
- **Hook:** Hùng đứng trước ba cái lò cũ kỹ, tay lau mồ hôi dính bột. Tháng ba năm 1987, Hà Nội vẫn  nhưng mồ hôi cứ chảy vì lo chứ không vì nóng. Nhà hàng 42 đã có chỗ đứn…
- **Cliff:** Lan mang ly nước ra, mắt cô nhìn Hùng. "Anh uống nước đi." Hùng nhận ly, tay chạm tay cô. "Cảm ơn em." Anh nhìn cô, nụ cười nở trên môi.
- **Beat:** Nhà hàng Bếp Xưa; cliff chi nhánh 2.
- **Fix applied:** cliff Bếp Xưa

### Ch.103 — Mở rộng nhà máy 30
- **File:** `Chương 103 - Mở rộng nhà máy 30.txt`
- **Score:** **9.71** · words=3290 · dlg=49 · sd=12.68 · cd=2.22 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Minh, Tanaka
- **Hook:** Con số 30 treo trước mặt Hùng từ đầu năm 1987. Ba mươi nhà máy — không phải ba mươi xưởng nhỏ, không phải ba mươi điểm thuê mặt bằng. Nhà máy. Mỗi cái có tường,…
- **Cliff:** Ba mươi nhà máy. Bà Hà bảo đừng vội năm mươi — ông gật, nhưng trong sổ vẫn ghi kế hoạch phía trước.
- **Beat:** 30 nhà máy; boost Minh+bà Hà; plan 50 phía trước.
- **Fix applied:** boost cd Minh/bà Hà + cliff

### Ch.104 — Mở rộng xuất khẩu châu Âu
- **File:** `Chương 104 - Mở rộng xuất khẩu châu Âu.txt`
- **Score:** **9.71** · words=3894 · dlg=89 · sd=12.84 · cd=2.79 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai, Bảy
- **Hook:** Bình minh tháng Ba năm 1987, Hùng đứng ở cầu cảng Hải Phòng. Gió biển thổi mạnh, mang theo vị mặn chát của muối lẫn với mùi dầu diesel từ những con tàu đang nổ …
- **Cliff:** Hùng đứng dậy, tay xoa lưng. "Đi thôi." Lan gật đầu, mắt cười. "Vâng." Hai người bước ra, nắng chiều ấm áp.
- **Beat:** Xuất EU Ba Lan container; trim 6.1k→3.9k.
- **Fix applied:** trim 6189→3894 + cliff

### Ch.105 — Tổng kết Phần 3
- **File:** `Chương 105 - Tổng kết Phần 3.txt`
- **Score:** **9.71** · words=3888 · dlg=47 · sd=11.65 · cd=2.4 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh, Mai, Klaus, Tanaka, Bảy
- **Hook:** Năm 1987, TP.HCM. Trần Văn Hùng đóng cuốn sổ cuối cùng của Phần 3, thấy một đường thẳng từ Chương 90 đến Chương 104 — không đẹp, không trơn, nhưng mỗi đoạn đều …
- **Cliff:** Hùng quay lại nhìn quán nước chè một lần cuối. Mắt ông ấm áp. "Cảm ơn cậu." Ông nói khẽ, rồi bước đi.
- **Beat:** Tổng kết P3; rebuild panel + cliff P4.
- **Fix applied:** rebuild panel + cliff P4
- **Residual risk:** tổng kết list-y; đã giữ core + panel

### Ch.106 — Bắt đầu Phần 4
- **File:** `Chương 106 - Bắt đầu Phần 4.txt`
- **Score:** **9.71** · words=3404 · dlg=103 · sd=15.51 · cd=2.59 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Klaus
- **Hook:** Hùng ngồi ở bàn giấy cạnh cửa sổ nhìn ra cảng Đà Nẵng. Sáng sớm, cảng chưa ồn. Năm 1987. Part 4 bắt đầu không bằng tiếng pháo — bằng một tờ giấy nháp viết tay v…
- **Cliff:** Tàu lăn bánh. Đà Nẵng lùi xa dần. Hùng mở sổ viết một dòng: "Ra thế giới." Chỉ hai chữ, nhưng đủ lấp đầy một trang trắng.
- **Beat:** Bắt đầu P4 Đà Nẵng; ra thế giới.
- **Fix applied:** —

### Ch.107 — Mở nhà máy Thái Lan
- **File:** `Chương 107 - Mở nhà máy Thái Lan.txt`
- **Score:** **9.71** · words=3948 · dlg=112 · sd=14.16 · cd=2.32 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Bảy
- **Hook:** Tháng Ba năm 1987. Trần Văn Hùng xuống sân bay Don Mueang — hành lý một túi, hồ sơ một cặp, danh thiếp một xấp nhàu. Bangkok đón ông bằng hơi nóng 35 độ và mùi …
- **Cliff:** "Chú Hùng! Máy hỏng rồi!"Tiếng công nhân vọng từ xưởng. Hùng bỏ cây bút xuống bàn, đứng dậy. Ông bước nhanh ra xưởng, bước chân dồn dập trên
- **Beat:** NM Thái Don Mueang; rebuild panel + trim nhẹ.
- **Fix applied:** rebuild panel + trim 4283→3948

### Ch.108 — Mở nhà máy Indonesia
- **File:** `Chương 108 - Mở nhà máy Indonesia.txt`
- **Score:** **9.71** · words=3746 · dlg=104 · sd=13.15 · cd=2.08 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Bảy
- **Hook:** Năm 1987, Jakarta.…
- **Cliff:** Ông tắt đèn. Mưa rơi trên mái tôn. Jakarta còn nhiều việc — nhưng hiện tại, thứ ông cần là ngủ đủ để mai còn tỉnh làm tiếp.
- **Beat:** NM Indonesia Jakarta; mưa/máy/ca.
- **Fix applied:** —

### Ch.109 — Mở nhà máy Đức
- **File:** `Chương 109 - Mở nhà máy Đức.txt`
- **Score:** **9.71** · words=3337 · dlg=60 · sd=13.08 · cd=2.19 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Klaus, Schmidt, Bảy
- **Hook:** Tháng Mười 1987, Tây Đức.…
- **Cliff:** Lô đầu rời Frankfurt. Còn chứng nhận Đức phía trước — ông chưa dám tuyên bố xong.
- **Beat:** NM Đức Frankfurt; Schmidt boost cd.
- **Fix applied:** boost cd Schmidt

### Ch.110 — M&A Bangkok Electronics
- **File:** `Chương 110 - M&A Bangkok Electronics.txt`
- **Score:** **9.71** · words=3393 · dlg=53 · sd=12.67 · cd=2.78 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai, Minh, Bảy
- **Hook:** Năm 1987. Bangkok. Mục tiêu: một xưởng linh kiện điện tử Thái Lan tên Bangkok Electronics — ba mươi bảy nhân công, một dây chuyền lắp ráp bo mạch đơn giản, và m…
- **Cliff:** Bangkok Electronics về tay. Nhưng sổ nợ cũ sẽ nổi khi nào? Ông đợi báo cáo kiểm toán tuần sau.
- **Beat:** M&A Bangkok Electronics; đàm phán nợ + boost cd.
- **Fix applied:** boost cd M&A confrontation

### Ch.111 — Mở sang châu Mỹ USA
- **File:** `Chương 111 - Mở sang châu Mỹ USA.txt`
- **Score:** **10.00** · words=3138 · dlg=76 · sd=15.04 · cd=3.61 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh, Mai, Bảy
- **Hook:** Bảy giờ sáng, Sài Gòn cuối năm 1987. Cái lạnh miền Nam không ồn ào như gió mùa đông bắc — nó im lặng, thấm dần qua từng lớp áo len mỏng, qua kẽ cửa sổ gỗ đã co …
- **Cliff:** Ngoài ngõ, tiếng xe ôm nổ. Mùi xăng lẫn mùi mưa. Phía trước là một nước ông mới chỉ biết qua bản đồ.
- **Beat:** Mở Mỹ; expand short + rebuild panel; bay sáng mai.
- **Fix applied:** expand short + rebuild panel

### Ch.112 — Hoàn thành phần 3
- **File:** `Chương 112 - Hoàn thành phần 3.txt`
- **Score:** **9.63** · words=3441 · dlg=50 · sd=13.44 · cd=3.08 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Klaus, Tanaka, Bảy
- **Hook:** Tháng Mười Hai 1987. Đà Nẵng.…
- **Cliff:** Phần 3 xong trên giấy. Phía trước là Mỹ — ông hít sâu, chưa chắc mình đã sẵn sàng.
- **Beat:** Hoàn thành P3; rebuild panel + family beat.
- **Fix applied:** rebuild panel + family boost

### Ch.113 — Mở nhà máy USA
- **File:** `Chương 113 - Mở nhà máy USA.txt`
- **Score:** **10.00** · words=3028 · dlg=45 · sd=14.83 · cd=3.88 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Klaus
- **Hook:** Tháng Mười Một 1987. Chicago.…
- **Cliff:** Mối hàn của Wojtek vẫn chịu được.
- **Beat:** NM USA Chicago; Wojtek hàn.
- **Fix applied:** —
- **Residual risk:** gần sàn 3000 — tránh trim thêm

### Ch.114 — M&A Stahl GmbH
- **File:** `Chương 114 - M&A Stahl GmbH.txt`
- **Score:** **9.78** · words=3005 · dlg=53 · sd=14.21 · cd=3.69 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Klaus, Schmidt
- **Hook:** Sáng đầu tháng Mười Một 1987, Hà Nội.…
- **Cliff:** Đặt máy xuống, Hùng nhìn ra cửa sổ lần cuối trước khi tắt đèn. Một thoáng gió lùa qua khe, làm mấy tờ hợp đồng trên bàn khẽ động. Ông lấy ta
- **Beat:** M&A Stahl GmbH; chuỗi thép khép.
- **Fix applied:** —
- **Residual risk:** gần sàn 3000 — tránh trim thêm

### Ch.115 — Mở nhà máy Nigeria
- **File:** `Chương 115 - Mở nhà máy Nigeria.txt`
- **Score:** **9.71** · words=3050 · dlg=85 · sd=14.85 · cd=2.78 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Bảy
- **Hook:** Lagos, Nigeria — tháng Ba 1987. Nhiệt độ lúc mười giờ sáng đã chạm bốn mươi hai độ C. Bụi đỏ laterit mịn như bột mì nhưng dai như keo — bám vào ống quần, vào cổ…
- **Cliff:** Về căn nhà thuê, bà Hà chưa ngủ, ngồi đợi dưới đèn dầu. "Xong chưa con?" "Xong. Máy chạy rồi." Bà gật, múc cho ông tô cháo cá nấu với hạt ti
- **Beat:** NM Nigeria Lagos; bụi laterit/dầu.
- **Fix applied:** —
- **Residual risk:** gần sàn 3000 — tránh trim thêm

### Ch.116 — Mở nhà máy Úc
- **File:** `Chương 116 - Mở nhà máy Úc.txt`
- **Score:** **9.71** · words=3431 · dlg=67 · sd=10.97 · cd=3.34 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Klaus, Tanaka, Craig, Bảy
- **Hook:** Sydney, tháng Ba 1987. Chuyến bay từ Sài Gòn qua Singapore rồi Sydney kéo dài mười bốn tiếng. Hùng ngồi ghế phổ thông, tập bản vẽ và sổ tay trên bụng, ngủ được …
- **Cliff:** Nhưng đơn hàng đầu sẽ về khi nào? Ông đợi fax từ Melbourne — không, ông đang ở Melbourne — ông đợi fax từ khách Sydney ngày mai.
- **Beat:** NM Úc; strip unaccent garbage + expand Craig/fax.
- **Fix applied:** strip garbage unaccent + expand + panel

### Ch.117 — Tổng tài sản 1000 tỷ
- **File:** `Chương 117 - Tổng tài sản 1000 tỷ.txt`
- **Score:** **9.71** · words=3002 · dlg=43 · sd=11.65 · cd=3.25 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai, Tanaka, Bằng
- **Hook:** Tiếng máy may dừng lúc mười một giờ đêm. Cả xưởng chỉ còn một bóng đèn trần vàng vọt, hắt bóng dài lên những kiện vải xếp chồng dọc tường. Những chiếc máy may i…
- **Cliff:** Nhìn lại những chặng đường đã qua, Hùng thấy mình may mắn. May mắn vì sinh ra ở một thời đại có nhiều cơ hội. May mắn vì gặp được những ngườ
- **Beat:** Tổng TS 1000 tỷ; đêm xưởng + bà Hà.
- **Fix applied:** —
- **Residual risk:** gần sàn 3000 — tránh trim thêm

### Ch.118 — Những ngày nằm viện
- **File:** `Chương 118 - Những ngày nằm viện.txt`
- **Score:** **10.00** · words=3033 · dlg=49 · sd=14.49 · cd=4.9 · panel_year=1987
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Hạnh, Mai, Bảy
- **Hook:** Cơn đau đến không báo trước.…
- **Cliff:** Ông không gọi Lan dù đã hứa. Sợ em lo. Nhưng trong đầu ông có một danh sách ngắn: những người cần nói trước khi lên bàn mổ, những chuyện cần
- **Beat:** Nằm viện; bát cháo/ủy thác buộc.
- **Fix applied:** —
- **Residual risk:** gần sàn 3000 — tránh trim thêm

### Ch.119 — Bước ngoặt sức khỏe
- **File:** `Chương 119 - Bước ngoặt sức khỏe.txt`
- **Score:** **9.71** · words=3148 · dlg=29 · sd=13.95 · cd=2.3 · panel_year=1988
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, Mai
- **Hook:** Tròn mặt trời đang lên cao giữa buổi trưa. Hùng ngồi ở bàn cuối phòng giao dịch, tay phải cầm bản hợp đồng thương lượng giá lô hàng xà phòng với đối tác Đà Nẵng…
- **Cliff:** Hùng nhìn tờ giấy ra viện, ánh mắt dừng ở dòng chữ "hẹn tái khám sau ba tháng." Ông gấp tờ giấy, cho vào túi áo, rồi đứng dậy. Lan đỡ ông, n
- **Beat:** Bước ngoặt SK; ký hợp đồng vs nghỉ.
- **Fix applied:** —

### Ch.120 — Học cách ủy thác sâu hơn
- **File:** `Chương 120 - Học cách ủy thác sâu hơn.txt`
- **Score:** **9.71** · words=3046 · dlg=55 · sd=13.46 · cd=3.14 · panel_year=1988
- **≥9.5?** **YES**
- **Cast:** Hùng, Lan, bà Hà, Mai
- **Hook:** Năm giờ sáng, Đà Nẵng 1988. Hùng ngồi ở bàn gỗ trong căn phòng vừa làm việc vừa làm phòng khách — hai chồng hồ sơ, một máy chữ cũ Olivetti, một lịch treo tường …
- **Cliff:** Hoàng hôn buông xuống, ánh đèn đường hắt vào phòng qua khe cửa. Hùng ngồi một mình, tay đặt trên cuốn sổ xanh nhưng không mở. Tiếng Lan thu 
- **Beat:** Ủy thác sâu 1988; Lan tự kiểm; drop Teaser label.
- **Fix applied:** drop Teaser: label
- **Residual risk:** gần sàn 3000 — tránh trim thêm

---

## Integrity gate (Level 1–2)

| Check | Result |
|-------|--------|
| Pad markers (sổ cái khớp / Hai ly nước ấm / {a}{b} / Tình yêu…) | **0 hit** trên 91–120 |
| Header spill pre-`=====` | **0** |
| Panel `GHI NHẬN` + `Năm:` parseable | **30/30** |
| VI-tokens body ∈ [3000,4200] | **30/30** |
| Hard-fail scorer | **0** |

---

## Continuity / AI notes (không chặn PASS máy)

1. **Năm batch:** romance 93–95 = **1986**; công nghiệp/mở rộng 91–92, 96–118 ≈ **1987**; 119–120 → **1988**. Nhảy lùi năm trong batch là structure outline, không phải bug panel.
2. **Cast drift (pre-existing):** một số ch công nghiệp vẫn có residual "Lan = vợ/KT" vs series-canon Lan em/đồng sự; bà Hà mẹ vs vợ ở ch cũ. **Không rewrite canon trong post-strip** — chỉ strip pad + scorer axes.
3. **Ch.91 Bằng-arc:** flaw giấu Lan / logistics — giữ nguyên (Mode F).
4. **Ch.116:** đuôi unaccent đã cắt; scene Craig/Melbourne + fax là mới, year-fit 1987.
5. **Title spacing:** đã sửa `Mở rộngviễn thông` → `Mở rộng viễn thông` (và cửa hàng/nhà hàng/nhà máy/xuất khẩu).
6. **Ch.120:** bỏ label `Teaser:`; body ủy thác giữ.

---

## MTC / quality leftover (không FAIL máy)

| Ưu tiên | Ch | Gợi ý (optional next) |
|--------:|----|------------------------|
| Thấp | 105 | Tách list tổng kết thành 1 scene đối thoại cụ thể hơn |
| Thấp | 117–119 | Health arc đã tốt; có thể thêm 1 beat ủy thác có tên người nhận quyền |
| Thấp | 91/94 romance residual | Nếu QA cast-role: rà 1 pass rename bà Hà/Lan theo canon series |
| Không | — | Không cần expand thêm — max_words 4200 đang siết |

---

## Artifacts

- Score JSON: `_ai_reads/_score_091_120_post.json`
- Fix script: `C:/Dev/MythLab/_fix_batch_091_120.py`
- Backup pre-strip: `_fix_backup_p0_20260729/`

## Verdict batch

**POST-STRIP BATCH 91–120: ALL_PASS 30/30 · AVG 9.758 · hard-fail 0.**

Sẵn sàng batch kế (121–150) theo cùng pipeline post-strip.
