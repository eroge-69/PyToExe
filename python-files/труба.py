import tkinter as tk
from tkinter import messagebox
import math

def arc_length(angle_deg, radius):
    return math.pi * radius * angle_deg / 180 if 0 < angle_deg <= 180 and radius > 0 else 0

def arc_projection(angle_deg, radius):
    angle_rad = math.radians(angle_deg / 2)
    return 2 * radius * math.sin(angle_rad) if 0 < angle_deg <= 180 and radius > 0 else 0

def deg_to_rad(deg):
    return math.radians(deg)

def validate_diameter(event=None):
    try:
        D = float(entry_fields["Диаметр трубы (мм):"].get())
        allowed_diameters = [10, 12, 14, 15, 16, 18, 20, 22, 25]
        if D not in allowed_diameters:
            messagebox.showerror("Ошибка", f"Допустимые диаметры: {allowed_diameters}")
            entry_fields["Диаметр трубы (мм):"].focus_set()
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректный диаметр трубы.")
        entry_fields["Диаметр трубы (мм):"].focus_set()

def calculate():
    try:
        D = float(entry_fields["Диаметр трубы (мм):"].get())
        allowed_diameters = [10, 12, 14, 15, 16, 18, 20, 22, 25]
        if D not in allowed_diameters:
            messagebox.showerror("Ошибка", f"Допустимые диаметры: {allowed_diameters}")
            return

        R = float(entry_fields["Радиус гиба (мм):"].get())
        if R <= 0:
            messagebox.showerror("Ошибка", "Радиус гиба должен быть положительным.")
            return

        lengths = []
        angles = []
        for label in input_order:
            val = entry_fields[label].get()
            if val.strip() == "":
                val = "0"
                entry_fields[label].delete(0, tk.END)
                entry_fields[label].insert(0, "0")
            val = float(val)
            if "Длина" in label:
                lengths.append(val)
            elif "Угол" in label:
                if val != 0 and not 1 <= val <= 180:
                    messagebox.showerror("Ошибка", f"Недопустимый угол '{label}': {val}. Диапазон: 1-180°.")
                    return
                angles.append(val)

        result_lines = [f"Диаметр трубы: {int(D)} мм", f"Радиус гиба: {int(R)} мм"]
        arc_total = 0
        corrected_lengths = []

        for i in range(len(lengths)):
            angle_prev = angles[i - 1] if i > 0 and i - 1 < len(angles) else 0
            angle_next = angles[i] if i < len(angles) else 0

            if i > 0:
                arc_total += arc_length(angle_prev, R)

            if 85 <= angle_prev <= 95 or 175 <= angle_prev <= 180:
                reduction_prev = R
            else:
                reduction_prev = arc_length(angle_prev, R) / 2

            if 85 <= angle_next <= 95 or 175 <= angle_next <= 180:
                reduction_next = R
            else:
                reduction_next = arc_length(angle_next, R) / 2

            if i == 0:
                length_corr = lengths[i] - reduction_next
            else:
                length_corr = lengths[i] - reduction_prev - reduction_next

            corrected_lengths.append(max(length_corr, 0))

        for i, L in enumerate(corrected_lengths):
            if int(round(L)) > 0:
                result_lines.append(f"Длина {chr(65+i)}: {int(round(L))} мм")
            if i < len(angles):
                angle = angles[i]
                arc = arc_length(angle, R)
                if int(round(angle)) > 0:
                    result_lines.append(f"Угол {chr(65+i)}{chr(66+i)}: {int(round(angle))}° (дуга: {int(round(arc))} мм)")

        total_length = sum(corrected_lengths) + arc_total

        # Построение цепочки сложения отрезков и дуг
        sequence_values = []
        current_sum = 0
        for i in range(len(corrected_lengths)):
            current_sum += corrected_lengths[i]
            sequence_values.append(current_sum)
            if i < len(angles):
                arc = arc_length(angles[i], R)
                current_sum += arc
                sequence_values.append(current_sum)

        sequence_str = " - ".join(str(int(round(v))) for v in sequence_values)
        result_lines.append(f"Цепочка значений: {sequence_str}")
        result_lines.append(f"\nОбщая длина трубы: {int(round(total_length))} мм")
        result_lines.append(f"Длина 2 (с запасом 20%): {int(round(total_length * 1.2))} мм")

        output.delete("1.0", tk.END)
        output.insert(tk.END, "\n".join(result_lines))

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения.")

def add_input(label_text, row, col):
    label = tk.Label(root, text=label_text)
    label.grid(row=row, column=col*2, sticky="w", padx=5, pady=2)
    entry = tk.Entry(root)
    entry.grid(row=row, column=col*2 + 1, padx=5, pady=2)
    entry.bind("<Return>", lambda e, idx=row: focus_next(idx + 1))
    entry_fields[label_text] = entry

def focus_next(row):
    if row < len(input_order):
        entry_fields[input_order[row]].focus_set()

def add_segment():
    global next_index, add_row
    seg_label = f"Длина {chr(65 + next_index)} (мм):"
    angle_label = f"Угол {chr(65 + next_index)}{chr(66 + next_index)} (°):"
    input_order.append(seg_label)
    input_order.append(angle_label)
    add_input(seg_label, add_row, 1)
    add_input(angle_label, add_row + 1, 1)
    add_row += 2
    next_index += 1

root = tk.Tk()
root.title("Расчёт длины трубы")
root.geometry("900x900")

entry_fields = {}
input_order = [
    "Диаметр трубы (мм):", "Радиус гиба (мм):",
    "Длина A (мм):", "Угол AB (°):",
    "Длина B (мм):", "Угол BC (°):",
    "Длина C (мм):", "Угол CD (°):",
    "Длина D (мм):", "Угол DE (°):",
    "Длина E (мм):"
]
next_index = 5
add_row = 0

for i, label in enumerate(input_order):
    col = 0 if i < 12 else 1
    row = i if col == 0 else (i - 12)
    if label not in entry_fields:
        add_input(label, row, col)

entry_fields["Диаметр трубы (мм):"].bind("<Return>", validate_diameter)

tk.Button(root, text="Рассчитать", command=calculate).grid(row=20, column=0, columnspan=2, pady=10)
tk.Button(root, text="Добавить участок", command=add_segment).grid(row=21, column=0, columnspan=2, pady=5)

output = tk.Text(root, height=20, width=100)
output.grid(row=22, column=0, columnspan=4, padx=5, pady=10)

root.mainloop()