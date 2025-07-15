import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = "Custom_EQ_Config.cfg"

frequencies = ["125", "250", "500", "1k", "2k", "4k", "8k"]

def read_config():
    values = {}
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=")
                    values[key.strip()] = float(val.strip())
    except FileNotFoundError:
        # قيم افتراضية 0 لكل الترددات
        for freq in frequencies:
            values[freq] = 0.0
    return values

def write_config(values):
    with open(CONFIG_FILE, "w") as f:
        for k in frequencies:
            f.write(f"{k} = {values[k]:.2f}\n")

def save():
    for key in sliders:
        values[key] = sliders[key].get()
    write_config(values)
    messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح!")

app = tk.Tk()
app.title("الكنق طواف")

values = read_config()

sliders = {}
for i, key in enumerate(frequencies):
    tk.Label(app, text=key + " Hz").grid(row=i, column=0, padx=10, pady=5)
    sliders[key] = tk.Scale(app, from_=-12, to=12, resolution=0.1, orient=tk.HORIZONTAL, length=300)
    sliders[key].set(values.get(key, 0.0))
    sliders[key].grid(row=i, column=1, padx=10, pady=5)

save_button = tk.Button(app, text="حفظ التعديلات", command=save)
save_button.grid(row=len(frequencies), column=0, columnspan=2, pady=15)

app.mainloop()