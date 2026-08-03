# Deterministic Scorer v2 — Full 360-Chapter Report

**Version:** 2.0.0  
**Date:** 2026-08-03  
**Repos analyzed:** textstat, TextDescriptives, LexicalRichness, py-readability-metrics, TAALED, lexical_diversity  
**Cloned to:** C:\Dev\_upstream

## Results
- **Total:** 360 chapters
- **PASS ≥9.0:** 262/360 (72.8%)
- **FAIL:** 98/360 (27.2%)
- **AVG:** 9.07

## 32 Binary Criteria (8 axes weighted)

### Axis weights (same as v1 for backward compat)
| Axis | Weight | Criteria |
|------|--------|----------|
| Văn chương | 20% | van_sensory, van_char, van_sent_var, van_vocab, van_hapax |
| Cấu trúc | 15% | cau_words, cau_scene, cau_teaser, cau_para_var |
| Nhân vật | 15% | nv_dialogue, nv_char_action, nv_dialogue_var, nv_no_name_leak |
| Continuity | 20% | cont_year, cont_anach, cont_timeline |
| Fillers | 15% | fill_pad, fill_maxrep, fill_no_cliche_open, fill_no_template_trans, fill_no_filler_phrases, fill_no_redundancy |
| Hệ thống | 10% | sys_panel, sys_year |
| Pacing | 5% | pac_consistent, pac_sent_var |
| Nâng cao | 5% | adv_emotion, adv_sensory_var |

### FAIL distribution (360 chapters)
| Criteria | FAIL count | % | Description |
|----------|-----------|---|-------------|
| cau_teaser_ok | 118 | 32.8% | No cliffhanger at chapter end |
| van_hapax_ok | 103 | 28.6% | Hapax ratio < 0.18 (too repetitive) |
| fill_pad_ok | 76 | 21.1% | System panel pad markers detected |
| adv_emotion_ok | 49 | 13.6% | No emotion words in chapter |
| fill_no_template_trans | 19 | 5.3% | Template transition phrases |
| fill_no_redundancy | 18 | 5.0% | Same sentence starters repeated |
| cont_anach_ok | 17 | 4.7% | Anachronism detected |
| pac_consistent_ok | 16 | 4.4% | Paragraph length too uneven |
| sys_panel_ok | 12 | 3.3% | Missing system panel |
| sys_year_ok | 12 | 3.3% | Missing panel year |
| cau_para_var_ok | 10 | 2.8% | Paragraph variance too low |
| cau_scene_ok | 9 | 2.5% | No scene breaks |
| fill_no_cliche_open | 7 | 1.9% | Cliche opening phrases |
| fill_no_filler_phrases | 6 | 1.7% | Filler phrases detected |
| nv_no_name_leak | 4 | 1.1% | Character name inconsistency |
| van_vocab_ok | 4 | 1.1% | TTR < 0.28 (low vocabulary diversity) |

### Hard-fail types
| Type | Count | Cap |
|------|-------|-----|
| pad_markers | 76 | 6.5 |
| anachronism | 17 | 6.5 |
| missing_system_panel | 12 | 7.5 |

## New v2 criteria (not in v1)
1. **van_sent_var_ok** — Sentence length variance ≥1000 (prose rhythm variety)
2. **van_vocab_ok** — TTR ≥0.28 (type-token ratio, vocabulary diversity)
3. **van_hapax_ok** — Hapax ratio ≥0.18 (words appearing once)
4. **cau_para_var_ok** — Paragraph length variance ≥8000
5. **nv_dialogue_var_ok** — At least 2 dialogue speakers
6. **cont_timeline_ok** — Chapter mentions time anchors
7. **fill_no_cliche_open** — No cliche opening phrases in first 500 chars
8. **fill_no_template_trans** — No template transition phrases
9. **fill_no_filler_phrases** — No filler phrases
10. **fill_no_redundancy** — Same sentence starters ≤2
11. **pac_consistent_ok** — max_para/avg_para < 8x
12. **pac_sent_var_ok** — Sentence length variance ≥1000
13. **adv_emotion_ok** — At least 1 emotion word
14. **adv_sensory_var_ok** — At least 3 different senses

## Determinism
- 100 runs × 3 chapters = **ZERO variance** ✅
- 10-chapter spot check = 7/10 PASS (3 hard-fail = legitimate)

## Threshold calibration (from 100-chapter sample)
| Metric | p10 | p25 | p50 | p75 | p90 | Threshold |
|--------|-----|-----|-----|-----|-----|-----------|
| sent_var | 1384 | 1524 | 1892 | 2490 | 3023 | ≥1000 |
| ttr | 0.3 | 0.3 | 0.3 | 0.4 | 0.4 | ≥0.28 |
| hapax | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | ≥0.18 |
| para_var | 11185 | 17375 | 24136 | 41344 | 57615 | ≥8000 |
| emotions | 0 | 1 | 1 | 2 | 3 | ≥1 |
| senses | 5 | 5 | 5 | 5 | 5 | ≥3 |
| max_para/avg | 3.2 | 3.7 | 4.5 | 5.9 | 7.9 | <8x |

## Comparison: v1 vs v2
| Metric | v1 (12 criteria) | v2 (32 criteria) |
|--------|------------------|------------------|
| PASS ≥9.0 | 358/360 (99.4%) | 262/360 (72.8%) |
| AVG | 9.79 | 9.07 |
| Criteria | 12 | 32 |
| Deterministic | ✅ | ✅ |
| Zero variance | ✅ | ✅ |
