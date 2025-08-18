import tkinter as tk
from tkinter import messagebox
from escpos.printer import Usb
import datetime

# Фирмени данни
FIRMA = "Джоб чек - 70 ЕООД"
EIK = "ЕИК ДДС: 206318702"
MAGAZIN = "Магазин: гр. София, р-н Сердика, бл. 41"

def print_receipt(items, total):
    try:
        # Свързване с касовия принтер (замени с твоите USB параметри)
        p = Usb(0x04b8, 0x0202)  # EPSON пример VID/PID

        p.text(FIRMA + "\n")
        p.text(EIK + "\n")
        p.text(MAGAZIN + "\n")
        p.text("=" * 32 + "\n")

        now = datetime.datetime.now()
        p.text("Дата: " + now.strftime("%d.%m.%Y %H:%M:%S") + "\n")
        p.text("-" * 32 + "\n")

        for item, price in items:
            p.text(f"{item:20} {price:>8.2f} лв.\n")

        p.text("-" * 32 + "\n")
        p.text(f"Общо: {total:.2f} лв.\n")
        p.text("=" * 32 + "\n")
        p.text("Благодарим Ви!\n\n")

        p.cut()

    except Exception as e:
        messagebox.showerror("Грешка", f"Неуспешен печат: {e}")

def add_item():
    name = entry_item.get()
    try:
        price = float(entry_price.get())
    except ValueError:
        messagebox.showerror("Грешка", "Въведи валидна цена!")
        return

    items.append((name, price))
    listbox.insert(tk.END, f"{name} - {price:.2f} лв.")
    update_total()

def update_total():
    total = sum(price for _, price in items)
    label_total.config(text=f"Общо: {total:.2f} лв.")

def print_now():
    total = sum(price for _, price in items)
    if total == 0:
        messagebox.showwarning("Внимание", "Няма добавени артикули!")
        return
    print_receipt(items, total)

# --- GUI ---
root = tk.Tk()
root.title("Издаване на касова бележка - Джоб чек 70 ЕООД")

items = []

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Артикул:").grid(row=0, column=0, padx=5, pady=5)
entry_item = tk.Entry(frame)
entry_item.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
entry_price = tk.Entry(frame)
entry_price.grid(row=1, column=1, padx=5, pady=5)

btn_add = tk.Button(frame, text="Добави", command=add_item)
btn_add.grid(row=2, column=0, columnspan=2, pady=5)

listbox = tk.Listbox(root, width=40)
listbox.pack(pady=10)

label_total = tk.Label(root, text="Общо: 0.00 лв.")
label_total.pack()

btn_print = tk.Button(root, text="Печат", command=print_now)
btn_print.pack(pady=10)

root.mainloop()
