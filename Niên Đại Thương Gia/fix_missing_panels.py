#!/usr/bin/env python3
"""
Add missing system panels to 12 chapters that lack them.
Each panel follows the format: 「Hệ thống — GHI NHẬN ch.XXX」
"""
import re, json, sys, glob

sys.path.insert(0, '.')
from deterministic_scorer_v2 import _panel, score_chapter

cfg = json.load(open('.mythlab_score.json', encoding='utf-8'))
files = sorted(glob.glob('Chương*.txt'))

# Panel data for each missing chapter (ch_num, year, exp, skills, note)
PANEL_DATA = {
    34:  {"year": 1983, "exp": 2220,  "space": 1110,  "skills": "Sản xuất lv2, Quản lý lv1", "note": "Tuyển kỹ sư Minh — đội ngũ cốt lõi"},
    88:  {"year": 1988, "exp": 14250, "space": 4943,  "skills": "Chiến lược lv1, Đầu tư lv2, Logistics lv1", "note": "MG thử xưởng: Minh siết bu-longyang"},
    133: {"year": 1992, "exp": 19860, "space": 6620,  "skills": "Quản trị đế chế lv1, Ngoại giao kinh tế lv1", "note": "Mở rộng Đông Nam Á — Malaysia và Philippines"},
    146: {"year": 1993, "exp": 22200, "space": 7400,  "skills": "Ngoại giao kinh tế lv2, Đàm phán lv1", "note": "Lan học cách đàm phán với người Mỹ"},
    152: {"year": 1993, "exp": 23280, "space": 7760,  "skills": "Quản trị đế chế lv2, Ngoại giao kinh tế lv2", "note": "Văn Hùng nhận huân chương"},
    246: {"year": 2006, "exp": 53667, "space": 17889, "skills": "Công nghệ cao lv2, Hạ tầng lv1", "note": "Trạm sạc toàn quốc — mạng lưới xe điện"},
    260: {"year": 2010, "exp": 58333, "space": 19444, "skills": "Quản trị đế chế lv3, Chuỗi cung ứng lv2", "note": "Chuỗi giá trị toàn cầu"},
    263: {"year": 2010, "exp": 59333, "space": 19778, "skills": "Chiến lược lv3, Ngoại giao kinh tế lv3", "note": "Flashback 25 năm — nhìn lại hành trình"},
    264: {"year": 2010, "exp": 59666, "space": 19889, "skills": "Chiến lược lv3, Sứ mệnh lv1", "note": "Tái khẳng định sứ mệnh sau 25 năm"},
    326: {"year": 2015, "exp": 80000, "space": 26667, "skills": "Công nghệ xanh lv2, ESG lv1", "note": "Net zero cam kết — chuyển đổi xanh"},
    341: {"year": 2017, "exp": 87000, "space": 29000, "skills": "Quản trị đế chế lv4, Kế thừa lv2", "note": "Lễ bàn giao quyền lực chính thức"},
    347: {"year": 2018, "exp": 90600, "space": 30200, "skills": "Từ thiện lv3, Di sản lv1", "note": "Từ thiện 100.000 tỷ lộ trình"},
}

fixed = 0
for f in files:
    t = open(f, encoding='utf-8').read()
    has_panel, _, _ = _panel(t)
    if has_panel:
        continue
    
    m = re.search(r'Chương (\d+)', f)
    ch_num = int(m.group(1)) if m else 0
    
    if ch_num not in PANEL_DATA:
        print(f"  SKIP Ch.{ch_num}: no panel data")
        continue
    
    data = PANEL_DATA[ch_num]
    
    # Build panel text
    panel = (
        f"\n「Hệ thống — GHI NHẬN ch.{ch_num}」\n"
        f"Năm: {data['year']}\n"
        f"Tổng EXP: {data['exp']:,}\n"
        f"Không gian kho: {data['space']:,}m²\n"
        f"Kỹ năng trọng yếu: {data['skills']}\n"
        f"Ghi chú: {data['note']}\n"
        f"\n"
        f"============================================================\n"
    )
    
    # Insert panel before the last separator
    last_sep = t.rfind('============================================================')
    if last_sep > 0:
        new_t = t[:last_sep] + panel + t[last_sep:]
    else:
        new_t = t + panel
    
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(new_t)
    
    # Verify
    r = score_chapter(new_t, cfg)
    status = "PASS" if r['final'] >= 9.0 else "FAIL"
    print(f"  Ch.{ch_num}: {status} (score={r['final']:.1f}) [HF: {r.get('hard_fails', [])}]")
    fixed += 1

print(f"\nFixed {fixed}/12 chapters")
