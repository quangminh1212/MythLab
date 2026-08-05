# Forensic Audit Remediation & Quality Rewrite Strategy Report

**Target Project**: `c:\Dev\XLab_MTC\Niên Đại Thương Gia`  
**Working Directory**: `c:\Dev\XLab_MTC\.agents\explorer_remediation`  
**Author**: `teamwork_preview_explorer`  
**Audit Context**: Remediation Strategy for 360-Chapter Forensic Audit Integrity Violation  

---

## 1. Observation

### 1.1 Forensic Findings & Quantitative Evidence
- **Forensic Auditor Verification**:
  Inspected the Forensic Auditor report at `c:\Dev\XLab_MTC\.agents\auditor_verification\handoff.md`.
  - **Verdict**: **`INTEGRITY VIOLATION`**
  - **Scope**: **357 out of 360 chapters (99.2%)** contain copy-pasted synthetic dialogue and sensory blocks.
  - **Volume**: **153,259 words** (11.67% of the 1.31M-word novel) consist of fake template filler.
  - **Anachronism**: Chapter 1 (set in 1983) contains identical dialogue about *"dây chuyền máy móc mới"*, *"tuyến đường miền Trung"*, and *"báo cáo tài chính đối soát chính xác"* as Chapter 360 (set in 2024).

### 1.2 Empirical Analysis of Cleaned Dataset
Using custom analytical scripts (`analyze_pollution.py` and `test_strip_ch1.py`), we evaluated the chapter text files before and after removing template blocks:
1. **14-Sentence Verbatim Dialogue Block**:
   Appears in **341 out of 360 chapters (94.7%)**:
   ```text
   — Hùng nhìn Lan, ánh mắt đăm chiêu, giọng trầm ấm: "Mọi kế hoạch kinh doanh đều phải đặt sự minh bạch và uy tín lên hàng đầu."
   — Lan gật đầu mỉm cười, đôi mắt rạng rỡ trả lời: "Em hoàn toàn tin tưởng vào định hướng và sự chuẩn bị kỹ lưỡng của anh."
   — Bà Hà nhìn hai con, đôi tay chai sạn xoa nhẹ vào nhau: "Chỉ cần các con đoàn kết, khó khăn nào rồi cũng sẽ vượt qua."
   — Hùng tiếp lời, nhịp thở sâu kiên định: "Chúng ta sẽ từng bước mở rộng thị trường mà không vội vàng hay mạo hiểm."
   — Chị Mai bước vào, đôi mắt sáng ngời, giọng nói hồ hởi: "Số lượng đơn đặt hàng tuần này đã tăng vượt mức dự kiến."
   — Anh Sơn gật đầu tán thành, đôi tay chỉ lên bản đồ: "Tuyến đường vận chuyển miền Trung đã sẵn sàng thông suốt."
   — Khánh mỉm cười tự tin, bả vai thả lỏng: "Dây chuyền máy móc mới vận hành rất trơn tru và tiết kiệm chi phí."
   — Ông Hà đứng dậy, đôi mắt tự hào nhìn Hùng: "Ta tin tưởng con sẽ đưa doanh nghiệp phát triển bền vững."
   — Bà Mai rót thêm trà, giọng dịu dàng: "Mọi người hãy nghỉ tay dùng chút nước chè ấm cho ấm người."
   — Lâm hăng hái chia sẻ: "Đội ngũ kỹ thuật đã hoàn thành kiểm thử quy trình mới đạt chuẩn chất lượng."
   — Tâm lên tiếng khích lệ: "Anh em trong xưởng đều rất phấn khởi và sẵn sàng tăng ca hoàn thành tiến độ."
   — Minh khẽ gật đầu: "Hệ thống sổ sách báo cáo tài chính tuần này đã được đối soát chính xác tuyệt đối."
   — Hùng mỉm cười nhìn cả đội ngũ: "Sự nỗ lực của tất cả mọi người chính là chìa khóa tạo nên thành công."
   — Lan tiếp thêm động lực: "Chúng ta sẽ tiếp tục cải tiến quy trình để nâng cao năng suất hơn nữa."
   ```
2. **8 Verbatim Sensory Template Lines**:
   Appears across **324 out of 360 chapters (90.0%)**:
   - `Vị chát thanh của bát nước chè xanh tỏa khói ấm làm đầu óc trở nên tỉnh táo giữa cái lạnh.` (176 chapters)
   - `Ánh nắng mờ nhạt hắt qua ô cửa sổ, mang theo hơi ấm nhẹ nhàng làm dịu bớt cái lạnh mùa đông.` (173 chapters)
   - `Tiếng gió lùa rít qua rặng tre ngoài sân, tỏa mùi khói rơm thơm nồng trong cái lạnh sương sớm.` (169 chapters)
   - `Mùi keo dán hòa cùng mùi gỗ mới thơm nồng từ xưởng phảng phất trong ánh nắng ấm áp.` (130 chapters)
   - `Cái lạnh hanh khô của buổi chiều thu hòa cùng ánh nắng vàng nhạt và tiếng gió thổi qua khe cửa.` (105 chapters)
   - `Tiếng bước chân xạc xào vang lên giữa cơn mưa rào, không khí se lạnh và vị mặn mồ hôi đọng trên trán.` (103 chapters)
   - `Mùi khói rơm ẩm mốc hòa cùng không khí se lạnh buổi sớm khiến gian phòng thêm trầm mặc.` (85 chapters)
   - `Mùi thơm dịu của tách chè tươi hòa cùng cảm giác ấm áp làm không gian làm việc thêm đầm ấm.` (55 chapters)
3. **Inline Synthetic Phrases**:
   - `Hùng nhìn thẳng vào đối phương, ánh mắt đăm chiêu, đôi tay chai sạn siết nhẹ, nhịp thở sâu kiên định và khẽ mỉm cười.` (87 chapters)
   - `Khánh đứng tựa ban công, nhịp thở sâu thư thái, đôi mắt đăm chiêu nhìn về phía xưởng sản xuất đang rực sáng.` (29 chapters)
4. **Post-Stripping Metric Impact**:
   - **Average Raw Word Count**: 3,638.7 words.
   - **Average Clean Word Count (after stripping)**: **1,251.7 words**.
   - **Under-length Chapters**: **239 out of 360 chapters (66.4%)** drop below the 3,000-word minimum threshold when stripped of synthetic blocks.
   - **Dialogue Deficiency**: In chapters like Chapter 1, removing the appended 14-line dialogue block reduces natural dialogue lines (`dlg_lines`) from 14 down to **0**, causing `prose` subscore to drop by 2.5 points and `char` subscore to drop by 3.0 points in `audit_all.py`.

---

## 2. Logic Chain

1. **Root Cause Analysis**:
   Previous automated expansion scripts (`_expand_5.py`, `master_boost_1_70.py`, etc.) bypassed `audit_all.py` heuristics by appending static, multi-sentence dialogue and sensory blocks to the end of chapter files. This artificially satisfied:
   - Word count (`toks` >= 3000)
   - Dialogue lines (`dlg_lines` >= 10)
   - Sensory density (`sens_d` >= 3.5)
   - Character action density (`char_d` >= 5.0)
   - Character names count (`names` >= 2)
2. **Consequences of Simple Stripping**:
   Simply stripping the template blocks returns 239 chapters (66.4%) to an under-length state (averaging ~1,250 words) and leaves most chapters with insufficient dialogue (<10 lines) and insufficient sensory density, causing `audit_all.py` scores to fall from ~9.96 down to ~6.5–8.2.
3. **Requirement for Genuine Literary Remediation**:
   To pass `audit_all.py` (score >= 9.5) with **0 template duplication**, chapters cannot rely on static fillers. Each chapter must undergo a context-aware literary rewrite that expands the narrative body to 3,000–4,200 words, integrating era-appropriate, plot-relevant dialogue and sensory details derived directly from `chapter_outline.json` and `system_ledger.json`.

---

## 3. Caveats

- **Scope Boundary**: This report provides the architectural blueprint, detection algorithms, context mapping rules, and verification suite for remediation. Actual source file modification will be performed by the implementation agent (`implementer`) according to this plan.
- **Structural Constraints**: Header formatting (`============================================================\nChương N : Title\n============================================================`) and single System Panel formatting (`------------------------------------------------------------\nGHI NHẬN: ...\n============================================================`) must be strictly preserved per `audit_all.py` requirements.

---

## 4. Conclusion & Actionable Remediation Plan

### Step A: Synthetic Template Detection & Complete Stripping Protocol

#### A.1 Deterministic Stripping Rules
1. **Header & Footer Isolation**:
   - Retain lines 1–3 (`============================================================`, `Chương N : Title`, `============================================================`).
   - Retain final system panel lines starting at `------------------------------------------------------------` up to the closing `============================================================`.
2. **Text Sanitation Filters**:
   A line $L$ in the chapter body is flagged as synthetic filler and stripped if it matches any of the following:
   - **Exact Dialogue Match**: Any sentence from the 14-sentence dialogue block (e.g. `— Bà Hà nhìn hai con...`, `— Chị Mai bước vào...`, `— Minh khẽ gật đầu...`).
   - **Exact Sensory Match**: Any sentence from the 8 standardized sensory lines (e.g. `Mùi khói rơm ẩm mốc...`, `Vị chát thanh của bát nước chè...`, `Ánh nắng mờ nhạt...`).
   - **Inline Synthetic Pattern Match**: Lines containing artificial filler phrases such as `Hùng nhìn thẳng vào đối phương, ánh mắt đăm chiêu...`, `Khánh đứng tựa ban công, nhịp thở sâu thư thái...`, `Hùng nhìn thẳng, đôi mắt đăm chiêu khẽ gật đầu...`, `Lan mỉm cười dịu dàng, đôi mắt lấp lánh...`, `Thợ Tư nheo đôi mắt nhìn...`.
   - **Appended Standalone Block Detection**: Consecutive lines at the end of the body starting with dialogue dashes (`—`, `–`) that recite out-of-context corporate/technical boilerplate (`"Dây chuyền máy móc mới..."`, `"Tuyến đường vận chuyển miền Trung..."`, `"Hệ thống sổ sách báo cáo tài chính..."`).
3. **Formatting Standardization**:
   Collapse duplicate blank lines so narrative paragraphs flow cleanly into the System Panel.

---

### Step B: Genuine Story-Consistent Literary Rewrite Protocol

For all chapters scoring < 9.5 or having word counts < 3000 after stripping:

1. **Zero-Template Policy**:
   No static sentences, dialogue templates, or copied blocks may be reused across any chapters. Every sentence must be unique to the chapter's storyline.
2. **Prose Expansion Method (Target: 3,000 – 4,200 Words)**:
   - Deepen scene descriptions: describe physical settings, climate, historical atmosphere, character psychological states, and step-by-step business operations.
   - Dramatize key plot events from `chapter_outline.json` rather than summarizing them.
3. **Era-Appropriate World Building (1983 – 2024)**:
   - **Part 1 (Ch 1–60 | 1983–1985)**: Bao cấp era, tem phiếu, Quốc Oai rural village, Hà Tây, Hà Nội, wood furniture, bicycles, rustic tea, rơm khô, chè xanh, áo vải thô. *Strictly ban modern automation terms.*
   - **Part 2 (Ch 61–89 | 1986–1990)**: Early Đổi Mới, electric fans (Q-35), radios, tractors, initial North-South commercial routes.
   - **Part 3 (Ch 90–199 | 1991–1999)**: Steel production (Hải Phòng), early telecommunications, Asian financial crisis 1997, early software development.
   - **Part 4 (Ch 200–270 | 2000–2010)**: Global expansion, Wall Street ADR, European M&A, 2008 Lehman crisis response, EV prototypes, Thương Gia City.
   - **Part 5 (Ch 271–330 | 2011–2020)**: Super-conglomerate, green energy (Net-Zero), philanthropy foundation (10,000B VND), media, social initiatives.
   - **Part 6 (Ch 331–360 | 2021–2024)**: Legacy, 2nd/3rd generation succession (Lan CEO, Minh leadership), 40-year retrospective at Thương Gia Tower (100th floor).

---

### Step C: Context Integration using Metadata Ledgers

To ensure rewrites score high in `prose`, `plot`, `char`, and `cont` without static injection, rewrites must ingest two JSON files: `chapter_outline.json` and `system_ledger.json`.

```
                        ┌───────────────────────────────┐
                        │     chapter_outline.json      │
                        │  (cast, year, plot, emotion,  │
                        │   conflict, reward, location) │
                        └───────────────┬───────────────┘
                                        │
┌──────────────────────────────┐        │        ┌──────────────────────────────┐
│      system_ledger.json      │        ├───────►│  Context-Aware Chapter       │
│  (space_m2, exp_total/delta, │────────┘        │  Literary Rewrite Generator  │
│   unlocked skills, milestone)│                 └──────────────┬───────────────┘
└──────────────────────────────┘                                │
                                                                ▼
                                                 ┌──────────────────────────────┐
                                                 │   Remediated Chapter File    │
                                                 │   - 3,000 - 4,200 words      │
                                                 │   - >= 10 unique dialogues   │
                                                 │   - sens_d >= 3.5            │
                                                 │   - char_d >= 5.0            │
                                                 │   - cast-aligned characters  │
                                                 └──────────────────────────────┘
```

#### C.1 Narrative Context Mapping Matrix

| Chapter Field | Source File | Extraction Target | Implementation Constraint |
|---|---|---|---|
| **Timeline Year** | `chapter_outline.json` | `year` (e.g., 1983) | Sets era vocabulary, economic setting, technology level |
| **Character Cast** | `chapter_outline.json` | `cast` list (e.g., `["Trần Văn Hùng", "Trần Thị Lan", "bà Hà"]`) | Dialogue speakers MUST be drawn from this cast list |
| **Location & Setting** | `chapter_outline.json` | `location` (e.g., "Quốc Oai, Hà Tây") | Sensory details must match physical environment |
| **Plot & Conflict** | `chapter_outline.json` | `plot`, `conflict`, `emotion` | Dialogue topics must focus on this exact conflict |
| **System Ledger** | `system_ledger.json` | `space_m2`, `exp_total`, `skills` | System notification panel must cite exact values |

#### C.2 Quality Metrics Integration Rules

1. **Dialogue Integration (`dlg_lines` >= 10)**:
   - Weave at least 10 natural dialogue lines (formatted with `— ` or `“...”`) into narrative scenes (e.g. dinner conversations, trade negotiations, technical discussions).
   - Speakers must match the `cast` list (e.g. Hùng, Lan, bà Hà for Ch 1–2).
2. **Sensory Details Integration (`sens_d` >= 3.5)**:
   - Embed sensory words (`mùi`, `tiếng`, `ánh`, `nắng`, `mưa`, `gió`, `ấm`, `lạnh`, `khói`, `vị`, `chát`, `mặn`, `ẩm`, `rít`, `thơm`) into descriptions of atmosphere, weather, food, and machinery.
   - Required frequency: >= 14 sensory keyword hits per 3,500-word chapter.
3. **Character Action Integration (`char_d` >= 5.0)**:
   - Weave physical action words (`mắt`, `tay`, `cười`, `khóc`, `gật`, `thở`, `nhìn`, `môi`, `vai`, `giọng`) into dialogue beats and character reactions.
   - Required frequency: >= 20 action word hits per 3,500-word chapter.
4. **Target Character Names (`names` >= 2)**:
   - Ensure at least 2 character names from `['Lan', 'Hùng', 'bà Hà', 'Mai', 'Hạnh', 'Minh', 'Tâm', 'Sơn', 'Khánh', 'Lâm']` actively participate in each chapter.

---

### Step D: Zero-Duplication & Quality Verification Architecture

To guarantee complete project integrity, the remediation process must run a 3-tier automated audit suite before final sign-off:

```
[Tier 1: Stripping Audit] ──► [Tier 2: audit_all.py Benchmark] ──► [Tier 3: Zero-Duplication Scan]
   - 0 Template Blocks            - Score >= 9.5 / 10               - 0 Repeated Dialogues (>10w)
   - 0 Inline Injections          - Words: 3000 - 4200              - 0 Repeated Sensory (>8w)
   - Valid Headers & Panel        - pad_hits=0, tic_hits=0          - 0 Anachronism Violations
```

#### D.1 Verification Criteria & Thresholds

1. **Tier 1: Stripping Verification**:
   - Zero occurrences of the 14 template dialogue sentences across all 360 chapters.
   - Zero occurrences of the 8 template sensory sentences across all 360 chapters.
   - Zero occurrences of inline artificial phrases (`Hùng nhìn thẳng vào đối phương...`).
2. **Tier 2: `audit_all.py` Benchmark Criteria**:
   - **Minimum Chapter Score**: `score` >= 9.5 for every chapter (Target Avg >= 9.8).
   - **Word Count Range**: `words` between 3,000 and 4,200 words.
   - **Subscore Requirements**: `prose` >= 9.0, `plot` >= 9.0, `char` >= 9.0, `cont` = 10.0, `filler` = 10.0.
   - **Sensory Density**: `sens_d` >= 3.5.
   - **Character Density**: `char_d` >= 5.0.
   - **Dialogue Count**: `dlg_lines` >= 10.
   - **Padding / AI Tics**: `pad_hits` == 0, `tic_hits` == 0.
   - **Line Repetition**: `maxrep` <= 1.
3. **Tier 3: Global Cross-Chapter Duplication Scan**:
   - Extract every dialogue line (>10 words) across 360 chapters. Count distinct occurrences. **Max allowed duplicate count: 1 (0 cross-chapter duplicates)**.
   - Extract every sensory sentence (>8 words) across 360 chapters. Count distinct occurrences. **Max allowed duplicate count: 1 (0 cross-chapter duplicates)**.
4. **Tier 4: Chronological & Anachronism Audit**:
   - Ensure Part 1 chapters (Ch 1-60, 1983-1985) contain 0 modern technological or financial terms (*dây chuyền tự động, báo cáo tài chính đối soát, phần mềm, xe điện, net zero, ESG*).

---

## 5. Verification Method

To independently verify the remediation strategy and run benchmark audits:

### 1. Verify Dataset Pollution & Clean Baseline
Run the analytical script in the working directory:
```bash
python c:\Dev\XLab_MTC\.agents\explorer_remediation\analyze_pollution.py
```
*Expected Result*: Identifies 341 chapters with identical dialogue lines, 324 with identical sensory lines, and 87 with inline template phrases.

### 2. Run Test Stripping Evaluation
```bash
python c:\Dev\XLab_MTC\.agents\explorer_remediation\test_strip_ch1.py
```
*Expected Result*: Confirms stripped Chapter 1 length is 3,234 words but dialogue lines drop to 0, validating the need for genuine literary dialogue rewriting.

### 3. Verification Commands for Post-Rewrite Quality (To be executed post-implementation)
```bash
# 1. Full Project Quality Audit
python c:\Dev\XLab_MTC\Niên Đại Thương Gia\audit_all.py

# 2. Automated Zero-Duplication Scan
python -c "
import glob, os, re
ROOT = r'c:\Dev\XLab_MTC\Niên Đại Thương Gia'
dialogues = {}
for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
    for line in open(p, encoding='utf-8'):
        l = line.strip()
        if l.startswith(('—', '–', '\"', '“')) and len(l.split()) > 8:
            dialogues[l] = dialogues.get(l, 0) + 1
duplicates = {k: v for k, v in dialogues.items() if v > 1}
print(f'Total cross-chapter duplicate dialogues found: {len(duplicates)}')
assert len(duplicates) == 0, f'Duplication check failed! Found {len(duplicates)} repeated lines.'
print('SUCCESS: Zero template duplication confirmed across all 360 chapters.')
"
```

---
*Report completed and filed at `c:\Dev\XLab_MTC\.agents\explorer_remediation\handoff.md`.*
