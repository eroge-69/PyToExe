import qrcode
from qrcode.constants import ERROR_CORRECT_Q
import tkinter as tk
from tkinter import messagebox
import os

# ==== Генерация QR ====
def generate_qr():
    first_name = entry_first.get().strip()
    last_name = entry_last.get().strip()
    phone = entry_phone.get().strip()
    email = entry_email.get().strip()

    if not (first_name and last_name and phone and email):
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    # Формируем vCard
    vcard = f"""BEGIN:VCARD
VERSION:3.0
N:{last_name};{first_name};;;
FN:{first_name} {last_name}
TEL;TYPE=WORK:{phone}
EMAIL;TYPE=WORK:{email}
END:VCARD
"""

    # Генерация QR
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_Q,
        box_size=10,
        border=4
    )
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Путь к папке "Загрузки"
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    file_path = os.path.join(downloads_path, "contact_vcard.png")

    img.save(file_path)
    messagebox.showinfo("Готово", f"QR-код сохранён в:\n{file_path}")

# ==== GUI ====
root = tk.Tk()
root.title("Генератор QR визитки")
root.geometry("360x230")
root.configure(bg="#f0f4f8")
root.resizable(False, False)

# ==== Стили ====
label_style = {"bg": "#f0f4f8", "fg": "#333", "font": ("Segoe UI", 10)}
entry_style = {"font": ("Segoe UI", 10)}
button_style = {"bg": "#4CAF50", "fg": "white", "font": ("Segoe UI", 11, "bold"), "bd": 0, "relief": "flat"}

# ==== Поля ввода ====
tk.Label(root, text="Имя:", **label_style).grid(row=0, column=0, sticky="e", padx=10, pady=5)
entry_first = tk.Entry(root, width=25, **entry_style)
entry_first.grid(row=0, column=1, pady=5)

tk.Label(root, text="Фамилия:", **label_style).grid(row=1, column=0, sticky="e", padx=10, pady=5)
entry_last = tk.Entry(root, width=25, **entry_style)
entry_last.grid(row=1, column=1, pady=5)

tk.Label(root, text="Телефон:", **label_style).grid(row=2, column=0, sticky="e", padx=10, pady=5)
entry_phone = tk.Entry(root, width=25, **entry_style)
entry_phone.grid(row=2, column=1, pady=5)

tk.Label(root, text="E-mail:", **label_style).grid(row=3, column=0, sticky="e", padx=10, pady=5)
entry_email = tk.Entry(root, width=25, **entry_style)
entry_email.grid(row=3, column=1, pady=5)

# ==== Кнопка ====
btn = tk.Button(root, text="Сгенерировать QR", command=generate_qr, **button_style)
btn.grid(row=4, column=0, columnspan=2, pady=15, ipadx=5, ipady=3)

# Эффект наведения на кнопку
def on_enter(e):
    btn.config(bg="#45a049")
def on_leave(e):
    btn.config(bg="#4CAF50")

btn.bind("<Enter>", on_enter)
btn.bind("<Leave>", on_leave)

root.mainloop()
