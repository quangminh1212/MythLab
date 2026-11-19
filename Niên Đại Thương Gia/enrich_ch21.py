# -*- coding: utf-8 -*-
import os, sys, re, unicodedata

def norm(s): return unicodedata.normalize('NFC', s)

fpath = r'C:\Dev\MythLab\Niên Đại Thương Gia\Chương 21 - Mở rộng làm giày.txt'
with open(fpath, 'r', encoding='utf-8') as f:
    text = norm(f.read())

# Tăng cường các cụm từ tương tác giác quan và cử chỉ nhân vật một cách tự nhiên
replacements = [
    ("Hùng nhận lời ngay", "Hùng khẽ gật đầu nhận lời ngay"),
    ("thợ Tư nói", "thợ Tư chau mày nhìn Hùng, ánh mắt đăm chiêu, giọng trầm tư nói"),
    ("Lan lật", "Đôi tay Lan khẽ run lật"),
    ("Anh không mang", "Ánh mắt Hùng trầm tư, anh không mang"),
    ("Ba Mẫn không có", "Ba Mẫn mỉm cười xòe tay, ông không có"),
    ("Hùng đến nơi", "Hùng đến nơi khi ánh nắng rực rỡ chiếu xuống,"),
    ("Tấm thứ nhất", "Mùi hồ dán thơm nhẹ phảng phất, tấm thứ nhất"),
    ("Tấm thứ hai", "Mùi dầu nặng nồng nặc ở tấm thứ hai"),
    ("Ba Mẫn nói", "Ba Mẫn mỉm cười vỗ tay nói"),
    ("Hùng đáp", "Hùng nhìn thẳng vào mắt Ba Mẫn, giọng trầm đĩnh đạc đáp"),
    ("Hai Độ cười", "Hai Độ nheo mắt cười lớn"),
    ("Hùng đặt đôi", "Hùng mỉm cười đặt đôi"),
    ("người gom giữ", "người gom nhìn Hùng gật đầu giữ"),
    ("Hùng về tới nhà", "Hùng về tới nhà khi gió lạnh lùa qua cửa,"),
    ("Lan đã nhận", "ánh mắt Lan lấp lánh nụ cười vui mừng khi nhận"),
    ("Thợ Tư đeo", "Thợ Tư chau mày đeo chiếc kính lão, đôi mắt nheo lại nhìn"),
    ("Lan thêm", "Lan mỉm cười gật đầu thêm"),
    ("Hùng gạch", "Hùng chau mày nén thở gạch"),
    ("Cô Tý đề nghị", "Cô Tý mỉm cười nhanh nhảu đề nghị"),
    ("Hòa đến", "Hòa đến khi ánh nắng chiều nhạt màu, đôi tay ngập ngừng"),
    ("Thợ Tư không hỏi", "Thợ Tư ngước mắt nhìn Hòa, giọng nghiêm nghị hỏi"),
    ("Hòa làm hỏng", "Đôi tay Hòa run run làm hỏng"),
    ("Bà Hà", "Ánh mắt dịu dàng của bà Hà"),
]

for old, new in replacements:
    text = text.replace(old, new, 1)

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Enriched Ch21")
