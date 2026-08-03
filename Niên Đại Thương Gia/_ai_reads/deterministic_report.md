# Deterministic Scorer Report — Niên Đại Thương Gia
> Date: 2026-08-03 | Scorer: deterministic_scorer.py v1.0

## Kết quả: 358/360 PASS (99.4%), AVG 9.79

### Phân phối điểm
| Điểm | Số chương | Tỷ lệ |
|------|-----------|-------|
| 10.0 | 223 | 61.9% |
| 9.5 | 123 | 34.2% |
| 9.0 | 12 | 3.3% |
| 8.5 | 2 | 0.6% |

### 2 chương FAIL (<9.0)

#### Chương 256 — Top thương gia Việt Nam (8.5)
- **Vấn đề:** `van_char_ok` FAIL (mật độ hành vi nhân vật <2/kchar) + `cau_teaser` FAIL
- **Cần sửa:** Thêm chi tiết hành vi nhân vật (mắt/tay/cười) + teaser/cliff cuối chương

#### Chương 73 — Hoàn thành nhiệm vụ cho vay (8.5)
- **Vấn đề:** `cau_scene` FAIL (không scene break) + `cau_teaser` FAIL + `sys_year` FAIL
- **Cần sửa:** Thêm phân cảnh (separator) + teaser + fix panel year

### Hệ thống tiêu chí (12 binary YES/NO)

| Trục | Tiêu chí | Trọng số |
|------|----------|----------|
| **Văn chương** | `van_sensory_ok`: sensory ≥3/kchar | 20% |
| | `van_char_ok`: char_density ≥2/kchar | |
| **Cấu trúc** | `cau_words_ok`: words ≥3000 | 15% |
| | `cau_scene_ok`: có scene break | |
| | `cau_teaser_ok`: có cliff/teaser cuối | |
| **Nhân vật** | `nv_dialogue_ok`: dialogue ≥6 lượt | 15% |
| **Continuity** | `cont_year_ok`: panel year = prose year (dateline mode) | 25% |
| | `cont_anach_ok`: không anachronism | |
| **Filler/Pad** | `fill_pad_ok`: 0 pad markers | 15% |
| | `fill_maxrep_ok`: maxrep <3 | |
| **Hệ thống** | `sys_panel_ok`: có panel 「GHI NHẬN」 | 10% |
| | `sys_year_ok`: panel có năm | |

### HARD-FAIL caps
| Điều kiện | Cap |
|-----------|-----|
| pad_markers ≥1 | 6.5 |
| maxrep ≥3 | 7.0 |
| year_mismatch (dateline) | 6.0 |
| anachronism | 6.5 |
| words <3000 | 7.5 |
| missing_system_panel | 7.5 |
| almost_no_dialogue | 7.5 |
| thin_prose (sensory <2/kchar) | 7.5 |

### Determinism verification
- 100 runs × 4 chapters = **400 scores, 0 variance** ✅
- Same input → same output, always
- `python deterministic_scorer.py --test-loop --times 100 --dir .`
