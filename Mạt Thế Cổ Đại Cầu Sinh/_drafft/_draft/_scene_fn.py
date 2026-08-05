def scene(n: int, i: int) -> str:
    """Unique scene block ~180-260 tokens."""
    hx = h(n, f"s{i}")
    seed = int(hx[:8], 16)
    a = CAST_MAIN[(n + i) % len(CAST_MAIN)]
    b = CAST_SIDE[(n + i * 3) % len(CAST_SIDE)]
    c = CAST_MAIN[(n + i + 2) % len(CAST_MAIN)]
    foe = FOES[(n + i) % len(FOES)]
    sm, so, li, to = SENS[(n + i) % len(SENS)]
    d = DIRS[(n + i) % 4]
    task = TASKS[(n + i * 2) % len(TASKS)]
    hour = 3 + (seed % 10)
    qty = 2 + (seed % 19)
    b1 = BODY[(n + i) % len(BODY)]
    b2 = BODY[(n + i + 5) % len(BODY)]
    b3 = BODY[(n + i + 9) % len(BODY)]
    arc_name, arc_theme = arc_of(n)
    uid = f"{n}.{i}.{hx[:6]}"

    lines = [
        "---",
        "",
        f"Canh {hour}, phía {d}. Ngày thứ {day_of(n)}, mốc {uid}. {li.capitalize()}.",
        f"{sm.capitalize()} len vào mũi; {so}. {a} cảm nhận {to} khi chạm cột gỗ số {qty} ({uid}).",
        f"{a} đang {task}. {b1.capitalize()} anh mở rồi nheo; {b2} siết chuôi dao đến trắng khớp — {uid}.",
        f'"{b}, báo cáo ngắn mã {uid}," {a} nói, giọng khàn. "Ta cần số liệu thật."',
        f'{b} {b3} đầu, nuốt khan: "Phía {d} có {qty} dấu chân lạ ở {uid}. Có thể là {foe}."',
        f'{c} liếc sổ, cau mày: "Nếu đúng canh {hour}, ca đêm dày gấp đôi. Trẻ vào nhà — lệnh {uid}."',
        f'{a} gật. "Làm việc {task}. Ai lơ là, đổi ca. {arc_theme} không lỏng tay ({uid})."',
        f"Họ bước quanh hàng rào phía {d}. {so.capitalize()} tắt một nhịp tại cột {qty} ({uid}).",
        f"{a} cúi kiểm vết đất, {b1} run nhẹ rồi vững. {sm.capitalize()} nồng góc {d} — ghi {uid}.",
        f'"{c}, sổ đen {uid}," {a} thở ra. "Mai họp, mang ra trước mặt mọi người."',
        f"{b} cười gượng, rồi khóc nuối một giây ở canh {hour} — rồi siết tay ({uid}).",
        f"Công việc {task} tiếp tục. Chỉ {b1}, {b2}, {b3} — nhịp sống cảnh {uid}.",
        f"(khóa {hx[:10]})",
        "",
    ]
    return "\n".join(lines)
