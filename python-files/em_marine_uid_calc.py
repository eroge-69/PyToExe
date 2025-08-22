
import tkinter as tk
from tkinter import messagebox

def calculate_uid():
    try:
        ref_id = int(entry_ref_id.get())
        ref_uid = int(entry_ref_uid.get())
        new_id = int(entry_new_id.get())

        diff = new_id - ref_id
        new_uid = ref_uid + diff
        new_uid_hex = hex(new_uid)

        result_text.set(f"UID (десятичный): {new_uid}\nUID (HEX): {new_uid_hex.upper()}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

app = tk.Tk()
app.title("EM-Marine UID калькулятор (RusGuard)")

tk.Label(app, text="Референсный ID карты:").grid(row=0, column=0, sticky='e')
entry_ref_id = tk.Entry(app)
entry_ref_id.grid(row=0, column=1)
entry_ref_id.insert(0, "40797")

tk.Label(app, text="Референсный UID (десятичный):").grid(row=1, column=0, sticky='e')
entry_ref_uid = tk.Entry(app)
entry_ref_uid.grid(row=1, column=1)
entry_ref_uid.insert(0, "356512931677")

tk.Label(app, text="Новый ID карты:").grid(row=2, column=0, sticky='e')
entry_new_id = tk.Entry(app)
entry_new_id.grid(row=2, column=1)
entry_new_id.insert(0, "51260")

tk.Button(app, text="Рассчитать", command=calculate_uid).grid(row=3, column=0, columnspan=2, pady=10)

result_text = tk.StringVar()
tk.Label(app, textvariable=result_text, fg="blue").grid(row=4, column=0, columnspan=2)

app.mainloop()
