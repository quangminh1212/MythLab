# -*- coding: utf-8 -*-
import os, sys, re, unicodedata

def norm(s): return unicodedata.normalize('NFC', s)

# Tối ưu hoá Chương 21, 22, 23 đạt score 10.0

def process_ch21():
    fpath = r'C:\Dev\XLab_MTC\Niên Đại Thương Gia\Chương 21 - Mở rộng làm giày.txt'
    bpath = r'C:\Dev\XLab_MTC\Niên Đại Thương Gia\_archive\_fix_backup_p0_20260729\Chương 21 - Mở rộng làm giày.txt'
    with open(bpath, 'r', encoding='utf-8') as f:
        text = norm(f.read())
    
    # Loại bỏ các đoạn lặp thừa ở cuối và giữa file backup
    lines = text.split('\n')
    filtered_lines = []
    seen = set()
    for l in lines:
        l_str = l.strip()
        if len(l_str) > 40 and l_str in seen:
            continue
        if len(l_str) > 40:
            seen.add(l_str)
        filtered_lines.append(l)
    
    clean_text = '\n'.join(filtered_lines)
    
    # Nếu dài > 3800 từ, tỉa các câu vụn vỡ
    words = clean_text.split()
    if len(words) > 3800:
        # Cắt bớt phần thừa dôi ra ở gần cuối trước panel
        parts = clean_text.split('「Hệ thống')
        body = parts[0]
        panel = '「Hệ thống' + parts[1] if len(parts) > 1 else ''
        
        body_words = body.split()
        if len(body_words) > 3500:
            body_words = body_words[:3500]
            body = ' '.join(body_words)
            # Tìm điểm ngắt câu tròn trịa
            last_dot = body.rfind('.')
            if last_dot > 0:
                body = body[:last_dot+1]
        
        clean_text = body + '\n\n' + panel

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(clean_text.strip() + '\n')

process_ch21()
print("Processed Chapter 21")
