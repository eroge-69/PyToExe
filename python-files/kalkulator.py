import tkinter as tk
from tkinter import ttk, messagebox

def calculate():
    try:
        width = float(entry_width.get()) if entry_width.get() else 0
        length = float(entry_length.get()) if entry_length.get() else 0
        height = float(entry_height.get()) if entry_height.get() else 0

        square = float(entry_square.get()) if entry_square.get() else width * length
        volume = float(entry_volume.get()) if entry_volume.get() else square * height

        entry_square.delete(0, tk.END)
        entry_square.insert(0, f"{square:.2f}")

        entry_volume.delete(0, tk.END)
        entry_volume.insert(0, f"{volume:.2f}")

        window_quality = combo_window.get()
        insulation_quality = combo_insulation.get()

        # Изчисления според отговорите
        if window_quality == "добра" and insulation_quality == "има изолация":
            cooling = volume * 40
            heating = volume * 50
        elif (window_quality == "добра" and insulation_quality == "няма изолация") or \
             (window_quality == "лоша" and insulation_quality == "има изолация"):
            cooling = volume * 45
            heating = volume * 60
        elif window_quality == "лоша" and insulation_quality == "няма изолация":
            cooling = volume * 50
            heating = volume * 70
        else:
            messagebox.showerror("Грешка", "Моля, изберете и двете опции за дограма и изолация.")
            return

        label_result.config(
            text=f"Резултат:\nЗа охлаждане: {cooling:.2f} W\nЗа отопление: {heating:.2f} W"
        )

    except ValueError:
        messagebox.showerror("Грешка", "Моля, въведете валидни числови стойности.")

# Създаване на основния прозорец
root = tk.Tk()
root.title("Калкулатор за кубатура и мощност")
root.geometry("400x500")
root.resizable(False, False)

# Полета за въвеждане
tk.Label(root, text="Ширина (м):").pack()
entry_width = tk.Entry(root)
entry_width.pack()

tk.Label(root, text="Дължина (м):").pack()
entry_length = tk.Entry(root)
entry_length.pack()

tk.Label(root, text="Височина (м):").pack()
entry_height = tk.Entry(root)
entry_height.pack()

tk.Label(root, text="Квадратура (м²):").pack()
entry_square = tk.Entry(root)
entry_square.pack()

tk.Label(root, text="Кубатура (м³):").pack()
entry_volume = tk.Entry(root)
entry_volume.pack()

# Падащи менюта
tk.Label(root, text="Каква е дограмата?").pack()
combo_window = ttk.Combobox(root, values=["добра", "лоша"], state="readonly")
combo_window.pack()

tk.Label(root, text="Има ли изолация?").pack()
combo_insulation = ttk.Combobox(root, values=["има изолация", "няма изолация"], state="readonly")
combo_insulation.pack()

# Бутон за изчисление
tk.Button(root, text="Изчисли", command=calculate, bg="lightblue").pack(pady=15)

# Резултат
label_result = tk.Label(root, text="Резултат:\n", font=("Arial", 12), justify="left")
label_result.pack()

# Стартиране на приложението
root.mainloop()
