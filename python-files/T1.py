import tkinter as tk
from tkinter import messagebox

def parse_packet_structured(packet_str):
    try:
        bytes_str = packet_str.strip().split()
        if len(bytes_str) != 14:
            return None, None, None, None, "Ошибка: введите ровно 14 байт"

        bytes_hex = [int(b, 16) for b in bytes_str]

        sign = '+' if bytes_hex[0] == 0x2B else '-' if bytes_hex[0] == 0x2D else '?'
        digits = ''.join(chr(b) for b in bytes_hex[1:5])

        point_map = {
            0x30: 0,  # 0000 (no decimal point)
            0x31: 1,  # 0.000 (after first digit)
            0x32: 2,  # 00.00 (after second digit)
            0x33: 3   # 000.0 (after third digit)
        }
        decimal_pos = point_map.get(bytes_hex[6], None)
        if decimal_pos is None:
            return None, None, None, None, f"неизвестная точка (0x{bytes_hex[6]:02X})"

        sb1 = bytes_hex[7]
        sb2 = bytes_hex[8]
        sb3 = bytes_hex[9]
        sb4 = bytes_hex[10]

        def decode_flags(byte_val, flags):
            return {name: (byte_val & (1 << bit)) != 0 for bit, name in flags.items()}

        sb1_flags = decode_flags(sb1, {
            0: "BPN", 1: "HOLD", 2: "REL", 3: "AC", 4: "DC", 5: "AUTO"
        })

        sb2_flags = decode_flags(sb2, {
            0: "Z3", 1: "n", 2: "Bat", 3: "APO", 4: "MIN", 5: "MAX", 6: "Z2", 7: "Z1"
        })

        sb3_flags = decode_flags(sb3, {
            0: "Z4", 1: "%", 2: "Diode", 3: "Beep", 4: "M", 5: "k", 6: "m", 7: "μ"
        })

        sb4_flags = decode_flags(sb4, {
            0: "°F",
            1: "°C",
            2: "F",
            3: "Hz",
            4: "hFE",
            5: "Ω",
            6: "A",
            7: "V"
        })

        # Проверка: в каждой группе SB должно быть не более одного активированного значения
        for idx, sb_flags in enumerate((sb1_flags, sb2_flags, sb3_flags, sb4_flags), start=1):
            if sum(sb_flags.values()) > 1:
                return None, None, None, None, f"Ошибка: в SB{idx} должно быть не более одного активированного значения"

        return sign, digits, decimal_pos, (sb1_flags, sb2_flags, sb3_flags, sb4_flags), None

    except Exception as e:
        return None, None, None, None, f"Ошибка разбора: {str(e)}"

def draw_display(sign, digits, decimal_pos, flags):
    canvas.delete("all")
    if digits is None or decimal_pos is None or flags is None:
        canvas.create_text(10, 10, anchor="nw", text="Ошибка в данных", fill="red", font=("Courier", 14))
        return

    # Draw digits with decimal points
    x_start = 20
    y_start = 30
    digit_width = 40
    digit_height = 60
    dot_radius = 5

    # Draw sign closer to digits
    canvas.create_text(x_start + digit_width//2, y_start + digit_height//2, text=sign, font=("Courier", 48), fill="black")

    x_digits = x_start + digit_width

    for i, d in enumerate(digits):
        # Draw digit text
        canvas.create_text(x_digits + i*digit_width + digit_width//2 - 2, y_start + digit_height//2,
                           text=d, font=("Courier", 48), fill="black")
        # Draw decimal point if applicable
        if decimal_pos == i + 1:
            # Draw a standard decimal point
            dot_r = 3
            cx = x_digits + i*digit_width + digit_width - dot_r*2
            cy = y_start + digit_height - 15
            canvas.create_oval(cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
                               fill="black", outline="")

    # Отрисовка единственного активного флага каждой группы SB
    sb1_flags, sb2_flags, sb3_flags, sb4_flags = flags
    active_labels = []
    for sb_flags in (sb1_flags, sb2_flags, sb3_flags, sb4_flags):
        label = next((name for name, active in sb_flags.items() if active), None)
        if label:
            active_labels.append(label)

    # Отрисовка меток под каждой цифрой
    # x_digits уже определён выше как x_start + digit_width
    for i, label in enumerate(active_labels):
        x = x_digits + i*digit_width + digit_width//2 - 2
        y = y_start + digit_height + 30
        canvas.create_text(x, y, text=label, font=("Courier", 14))

def on_submit():
    input_text = input_example
    sign, digits, decimal_pos, flags, error = parse_packet_structured(input_text)
    if error:
        canvas.delete("all")
        canvas.create_text(10, 10, anchor="nw", text=error, fill="red", font=("Courier", 14))
    else:
        draw_display(sign, digits, decimal_pos, flags)

# GUI
input_example = "2D 31 32 33 34 20 31 02 02 02 02 00 0D 0A"  # можно изменить на любой другой пример

root = tk.Tk()
root.title("Эмулятор")
root.geometry("420x540")

btn_frame = None

canvas = tk.Canvas(root, width=400, height=500)
canvas.pack(pady=10)

on_submit()

root.mainloop()