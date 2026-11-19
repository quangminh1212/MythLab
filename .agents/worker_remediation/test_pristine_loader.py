# -*- coding: utf-8 -*-
import sys, os, glob, re, json

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'c:\Dev\MythLab\Niên Đại Thương Gia'
sys.path.insert(0, ROOT)

from audit_all import audit_chapter, body_of, SENSORY, CHAR_WORDS

with open(os.path.join(ROOT, 'chapter_outline.json'), encoding='utf-8') as f:
    OUTLINE = json.load(f)['chapters']
with open(os.path.join(ROOT, 'system_ledger.json'), encoding='utf-8') as f:
    LEDGER = json.load(f)['chapters']

GLOBAL_SEEN_DIALOGUES = set()

# Pre-load pristine base texts for all 360 chapters
PRISTINE_BASE_PARAGRAPHS = {}

# Collect all duplicate template lines across original files
line_counts = {}
for p in glob.glob(os.path.join(ROOT, 'Chương *.txt')):
    with open(p, encoding='utf-8') as f:
        for l in f:
            line = l.strip()
            if len(line) > 15 and not line.startswith('=' * 10) and not line.startswith('-' * 10) and not line.startswith('Chương ') and not line.startswith('GHI NHẬN'):
                line_counts[line] = line_counts.get(line, 0) + 1

DUP_SET = set(k for k, v in line_counts.items() if v > 1)

GENERATED_PHRASE_PREFIXES = (
    "Vào năm ", "Trong hành trình phát triển", "Tại địa bàn ", "Nhịp sống lao động ",
    "Giai đoạn triển khai ", "Đến cuối ngày làm việc ", "Nhìn lại chặng đường ",
    "Toàn bộ kế hoạch ", "Sự thành công rực rỡ ", "Trong không khí sản xuất ",
    "Hành trình chinh phục ", "Chiến lược tổng thể ", "Sự đồng thuận cao ",
    "Những nỗ lực không ngừng ", "Khép lại giai đoạn "
)

def init_pristine_base_texts():
    for n in range(1, 361):
        files = glob.glob(os.path.join(ROOT, f'Chương {n} - *.txt'))
        if not files: files = glob.glob(os.path.join(ROOT, f'Chương {n:02d} - *.txt'))
        if not files: continue
        
        raw = open(files[0], encoding='utf-8').read()
        parts = raw.split('=' * 60)
        body_raw = parts[2].split('-' * 60)[0] if len(parts) >= 3 else raw
        
        clean_paras = []
        for p in body_raw.split('\n\n'):
            p_strip = p.strip()
            if not p_strip: continue
            if p_strip.startswith('— ') or p_strip in DUP_SET: continue
            if any(p_strip.startswith(prefix) for prefix in GENERATED_PHRASE_PREFIXES): continue
            if 'Hùng nhìn thẳng vào đối phương' in p_strip or 'Khánh đứng tựa ban công' in p_strip: continue
            clean_paras.append(p_strip)
        
        PRISTINE_BASE_PARAGRAPHS[n] = clean_paras

init_pristine_base_texts()
print(f"Pristine base texts loaded for {len(PRISTINE_BASE_PARAGRAPHS)} chapters.")
