import tkinter as tk
from tkinter import messagebox
from escpos.printer import Usb
import datetime
import csv
import os

# 🔹 Настройки за принтера (смени VID/PID според твоя принтер!)
VENDOR_ID = 0x0416
PRODUCT_ID = 0x5011

# Свързване с касовия принтер
try:
    printer = Usb(VENDOR_ID, PRODUCT_ID, 0, 0x81, 0x03)
except Exception as e:
    printer = None
    print("⚠️ Няма връзка с принтера:", e)

items = []

def add_item():
    name = entry_name.get().strip()
    try:
        price = float(entry_price.get().strip())
    except ValueError:
        messagebox.showerror("Грешка", "Цената трябва да е число!")
        return

    if name == "":
        messagebox.showerror("Грешка", "Въведи име на артикул!")
        return

    items.append((name, price))
    listbox.insert(tk.END, f"{name} - {price:.2f} лв")

    entry_name.delete(0, tk.END)
    entry_price.delete(0, tk.END)

def print_receipt():
    if not items:
        messagebox.showwarning("Внимание", "Няма добавени артикули!")
        return

    if not printer:
        messagebox.showerror("Грешка", "Принтерът не е свързан!")
        return

    subtotal = sum(price for _, price in items)
    vat = subtotal * 0.20
    total = subtotal + vat

    # Заглавие
    printer.set(align="center", bold=True, double_height=True)
    printer.text("КАСОВА БЕЛЕЖКА\n")
    printer.set(align="center", bold=True)
    printer.text("Джоб чек - 70 ЕООД\n")
    printer.text("ЕИК/ДДС: 206318702\n")
    printer.text("гр. София, р-н Сердика, бл. 41\n")
    printer.text("--------------------------------\n")

    # Артикули
    printer.set(align="left", bold=False)
    for item, price in items:
        line = f"{item:<15}{price:>7.2f} лв\n"
        printer.text(line)

    printer.text("--------------------------------\n")
    printer.text(f"Междинна сума: {subtotal:.2f} лв\n")
    printer.text(f"ДДС (20%):     {vat:.2f} лв\n")
    printer.text(f"Общо:          {total:.2f} лв\n")
    printer.text("--------------------------------\n")

    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    printer.text("Дата: " + now + "\n")
    printer.text("Благодарим Ви за покупката!\n\n")
    printer.cut()

    # Запис в CSV файл
    save_receipt_csv(now, items, subtotal, vat, total)

    messagebox.showinfo("Успех", "Бележката е отпечатана и записана!")
    items.clear()
    listbox.delete(0, tk.END)

def save_receipt_csv(date, items, subtotal, vat, total):
    filename = "kasovi_belejki.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        # Заглавен ред при първо създаване
        if not file_exists:
            writer.writerow(["Дата", "Артикул", "Цена", "Междинна сума", "ДДС", "Общо"])
        # Всеки артикул се записва като ред
        for item, price in items:
            writer.writerow([date, item, f"{price:.2f}", f"{subtotal:.2f}", f"{vat:.2f}", f"{total:.2f}"])

# --- GUI ---
root = tk.Tk()
root.title("Касов принтер - Джоб чек 70")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Артикул:").grid(row=0, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
entry_price = tk.Entry(frame)
entry_price.grid(row=1, column=1, padx=5, pady=5)

btn_add = tk.Button(frame, text="Добави", command=add_item)
btn_add.grid(row=2, column=0, columnspan=2, pady=10)

listbox = tk.Listbox(root, width=40, height=10)
listbox.pack(pady=10)

btn_print = tk.Button(root, text="Печатай бележка", command=print_receipt, bg="green", fg="white")
btn_print.pack(pady=10)

root.mainloop()
