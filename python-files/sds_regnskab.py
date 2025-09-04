
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

# Opret sti til datafil
data_file_path = "sds_regnskab_data.json"

# Indlæs eksisterende data eller opret ny struktur
if os.path.exists(data_file_path):
    with open(data_file_path, "r") as f:
        data = json.load(f)
else:
    data = {"2025": {"transactions": [], "buttons": [], "balance": 0}}

current_year = "2025"

# Funktioner
def save_data():
    with open(data_file_path, "w") as f:
        json.dump(data, f)

def add_transaction(description, amount, type_):
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": float(amount),
        "type": type_
    }
    data[current_year]["transactions"].append(transaction)
    if type_ == "Indtægt":
        data[current_year]["balance"] += float(amount)
    else:
        data[current_year]["balance"] -= float(amount)
    update_display()
    save_data()

def update_display():
    transactions_list.delete(0, tk.END)
    for t in data[current_year]["transactions"]:
        transactions_list.insert(tk.END, f"{t['date']} - {t['description']} - {t['amount']} kr - {t['type']}")
    balance_var.set(f"Kassebeholdning: {data[current_year]['balance']:.2f} kr")

def add_custom_button():
    name = simpledialog.askstring("Ny Salgsknap", "Navn på vare:")
    price = simpledialog.askfloat("Pris", f"Pris for {name}:")
    if name and price is not None:
        data[current_year]["buttons"].append({"name": name, "price": price})
        save_data()
        render_buttons()

def render_buttons():
    for widget in button_frame.winfo_children():
        widget.destroy()
    for item in data[current_year]["buttons"]:
        btn = tk.Button(button_frame, text=f"{item['name']} ({item['price']} kr)", 
                        command=lambda i=item: add_transaction(i["name"], i["price"], "Indtægt"))
        btn.pack(pady=2)

# GUI setup
root = tk.Tk()
root.title("SDS Regnskab - Prototype")

# Kassebeholdning
balance_var = tk.StringVar()
balance_label = tk.Label(root, textvariable=balance_var, font=("Helvetica", 14))
balance_label.pack(pady=10)

# Transaktionsliste
transactions_list = tk.Listbox(root, width=60)
transactions_list.pack(pady=10)

# Variabel post
desc_entry = tk.Entry(root)
desc_entry.pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

def add_variable_transaction(type_):
    try:
        desc = desc_entry.get()
        amount = float(amount_entry.get())
        if desc and amount:
            add_transaction(desc, amount, type_)
            desc_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Fejl", "Indtast et gyldigt beløb")

tk.Button(root, text="Tilføj Indtægt", command=lambda: add_variable_transaction("Indtægt")).pack(pady=2)
tk.Button(root, text="Tilføj Udgift", command=lambda: add_variable_transaction("Udgift")).pack(pady=2)

# Salgsknapper
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
render_buttons()

tk.Button(root, text="Tilføj Salgsknap", command=add_custom_button).pack(pady=5)

update_display()
root.mainloop()
