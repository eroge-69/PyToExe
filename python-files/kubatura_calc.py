import tkinter as tk
from tkinter import ttk

def calculate():
    try:
        width = float(entry_width.get()) if entry_width.get() else 0
        length = float(entry_length.get()) if entry_length.get() else 0
        height = float(entry_height.get()) if entry_height.get() else 0

        area = width * length
        volume = area * height

        if manual_area.get():
            area = float(manual_area.get())
        if manual_volume.get():
            volume = float(manual_volume.get())

        window_quality = window_option.get()
        insulation_quality = insulation_option.get()

        # Определяне на коефициентите
        if window_quality == "добра" and insulation_quality == "има изолация":
            cooling_factor = 40
            heating_factor = 50
        elif window_quality == "лоша" and insulation_quality == "няма изолация":
            cooling_factor = 50
            heating_factor = 70
        else:
            cooling_factor = 45
            heating_factor = 60

        cooling_result = volume * cooling_factor
        heating_result = volume * heating_factor

        result_label.config(text=f"за охлаждане: {cooling_result:.2f} W\nза отопление: {heating_result:.2f} W")
    except ValueError:
        result_label.config(text="Моля, въведи валидни числа.")

# Създаване на прозорец
root = tk.Tk()
root.title("Калкулатор за кубатура и мощност")

# Въвеждане на размери
tk.Label(root, text="Ширина (m):").grid(row=0, column=0, sticky="e")
entry_width = tk.Entry(root)
entry_width.grid(row=0, column=1)

tk.Label(root, text="Дължина (m):").grid(row=1, column=0, sticky="e")
entry_length = tk.Entry(root)
entry_length.grid(row=1, column=1)

tk.Label(root, text="Височина (m):").grid(row=2, column=0, sticky="e")
entry_height = tk.Entry(root)
entry_height.grid(row=2, column=1)

# Ръчно въвеждане
tk.Label(root, text="(По избор) Квадратура (m²):").grid(row=3, column=0, sticky="e")
manual_area = tk.Entry(root)
manual_area.grid(row=3, column=1)

tk.Label(root, text="(По избор) Кубатура (m³):").grid(row=4, column=0, sticky="e")
manual_volume = tk.Entry(root)
manual_volume.grid(row=4, column=1)

# Избор на дограма
tk.Label(root, text="Каква е дограмата:").grid(row=5, column=0, sticky="e")
window_option = ttk.Combobox(root, values=["добра", "лоша"])
window_option.current(0)
window_option.grid(row=5, column=1)

# Избор на изолация
tk.Label(root, text="Дали има изолация:").grid(row=6, column=0, sticky="e")
insulation_option = ttk.Combobox(root, values=["има изолация", "няма изолация"])
insulation_option.current(0)
insulation_option.grid(row=6, column=1)

# Бутон за изчисление
tk.Button(root, text="Изчисли", command=calculate).grid(row=7, column=0, columnspan=2, pady=10)

# Резултат
result_label = tk.Label(root, text="")
result_label.grid(row=8, column=0, columnspan=2)

root.mainloop()
