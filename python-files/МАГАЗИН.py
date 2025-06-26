import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

root = tk.Tk()
root.title("📦 Барномаи ИДОРАИКУНИИ МАГОЗА")

# Танзими равзана ба андозаи пурраи экран (автоматӣ)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

root.configure(bg="#f8f8f8")

style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 9, "bold"), foreground="#004488")
style.configure("Treeview", font=("Arial", 9))

def validate_all(text):
    return True

def validate_numbers_only(text):
    if text == "":
        return True
    try:
        float(text)
        return True
    except ValueError:
        return False

def sort_treeview_by_name():
    items = tree.get_children()
    items_list = [(tree.item(i)["values"][0].lower(), i) for i in items]
    items_list.sort()
    for idx, (_, item) in enumerate(items_list):
        tree.move(item, '', idx)

def refresh_treeview_filter(event=None):
    term = entry_search.get().lower()
    for item in tree.get_children():
        if term in str(tree.item(item)["values"][0]).lower():
            tree.reattach(item, '', 'end')
        else:
            tree.detach(item)

def treeview_striped_rows(tv):
    for i, item in enumerate(tv.get_children()):
        tv.item(item, tags=('evenrow' if i % 2 == 0 else 'oddrow',))

def ҳисоб_кардан():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Хато", "Лутфан номи молро ворид кунед.")
        return

    quantity = entry_quantity.get().strip()
    price = entry_price.get().strip()
    percent = entry_percent.get().strip()
    unit = combo_vohid.get()
    srok = entry_srok.get().strip()
    date_input = entry_date.get().strip()

    if not quantity or not price:
        messagebox.showerror("Хато", "Лутфан ҳамаи маълумотҳоро пур кунед.")
        return
    try:
        quantity = float(quantity)
        price = float(price)
        percent = float(percent) if not disable_percent_var.get() and percent != "" else 0
    except ValueError:
        messagebox.showerror("Хато", "Шумора, нарх ва фоиз бояд рақам бошанд.")
        return

    profit = price * percent / 100
    sell_price = price + profit
    total_profit = profit * quantity

    result = f"""
🏷️ мол: {name}
🔢 шумора: {quantity} {unit}
💵 нархи омад: {price:.2f}
📅 санаи воридот: {date_input or "—"}
📅 срок: {srok or "—"}
📈 фоиз: {percent:.1f}%
💰 нархи фурӯш: {sell_price:.2f}
📊 фоида аз 1: {profit:.2f}
📦 фоидаи умумӣ: {total_profit:.2f}
------------------------------------------
"""
    left_output_box.config(state="normal")
    left_output_box.delete("1.0", tk.END)
    left_output_box.insert(tk.END, result)
    left_output_box.config(state="disabled")

    for e in (entry_name, entry_quantity, entry_price, entry_percent, entry_srok, entry_date):
        e.delete(0, tk.END)
    combo_vohid.current(0)

    global last_result
    last_result = {
        "name": name, "quantity": quantity, "unit": unit,
        "unit_price": price, "percent": percent,
        "profit": profit, "sell_price": sell_price,
        "srok": srok, "date": date_input
    }

def ворид_кардан_ба_анбор():
    if not last_result:
        messagebox.showwarning("Эзоҳ", "Аввал ҳисоб кунед!")
        return
    q = last_result["quantity"]
    p = last_result["profit"]
    tree.insert("", "end", values=(
        last_result["name"], f"{q} {last_result['unit']}",
        f"{last_result['unit_price']:.2f}", f"{last_result['percent']:.1f}",
        f"{p:.2f}", f"{last_result['sell_price']:.2f}",
        f"{p*q:.2f}", last_result["date"] or "—", last_result["srok"] or "—"
    ))
    sort_treeview_by_name()
    refresh_treeview_filter()
    treeview_striped_rows(tree)
    messagebox.showinfo("Тасдиқ", "Мол ба анбор илова шуд ✅")

def пок_натиҷа():
    left_output_box.config(state="normal")
    left_output_box.delete("1.0", tk.END)
    left_output_box.config(state="disabled")

def toggle_percent_btn():
    if disable_percent_var.get():
        entry_percent.config(state="normal", background="white", foreground="black")
        toggle_percent_btn_widget.config(text="✅", bg="green", fg="white")
        disable_percent_var.set(False)
    else:
        entry_percent.delete(0, tk.END)
        entry_percent.config(state="disabled", background="gray", foreground="white")
        toggle_percent_btn_widget.config(text="⛔", bg="gray", fg="white")
        disable_percent_var.set(True)

paned = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)  # --- ИСЛОҲ ---

left = ttk.Frame(paned, padding=15)
right = ttk.Frame(paned, padding=15)

paned.add(left, weight=1)
paned.add(right, weight=1)

# --- ИСЛОҲ: Танзими grid weights барои left frame
for i in range(20):
    left.rowconfigure(i, weight=1)
left.columnconfigure(0, weight=1)
left.columnconfigure(1, weight=1)

# --- ИСЛОҲ: Танзими grid weights барои right frame (агар grid истифода шавад)
right.rowconfigure(0, weight=1)
right.columnconfigure(0, weight=1)

ttk.Label(left, text="📋 Майдони воридкунии молҳо", font=("Arial", 14, "bold"))\
    .grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

def make_label_entry(row, label, width=18, validate=None):
    ttk.Label(left, text=label, font=("Arial",11)).grid(row=row, column=0, sticky="w")
    entry = ttk.Entry(left, width=width, font=("Arial",11))
    if validate:
        vcmd = root.register(validate)
        entry.config(validate="key", validatecommand=(vcmd, "%P"))
    entry.grid(row=row, column=1, pady=5, sticky="w")
    return entry

entry_name = make_label_entry(1, "📦 Номи мол:", 25, validate=validate_all)
entry_quantity = make_label_entry(2, "🧮 Шумора:", 18, validate=validate_numbers_only)
entry_price = make_label_entry(3, "💵 Нарх:", 18, validate=validate_numbers_only)

ttk.Label(left, text="📅 Санаи ворид:", font=("Arial", 11)).grid(row=4, column=0, sticky="w")
entry_date = ttk.Entry(left, width=18, font=("Arial", 11))
entry_date.grid(row=4, column=1, pady=5, sticky="w")
entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

entry_srok = make_label_entry(5, "📅 Срок:", 18, validate=validate_numbers_only)

ttk.Label(left, text="📦 Бастабандӣ:", font=("Arial",11)).grid(row=6, column=0, sticky="w")
combo_vohid = ttk.Combobox(left, values=["кг","л","м","м²","м³","дона","табақа","қуттӣ","баста","каробка"],
                           state="readonly", font=("Arial",11), width=16)
combo_vohid.grid(row=6, column=1, pady=5, sticky="w")
combo_vohid.current(0)

ttk.Label(left, text="📈 Фоиз (%):", font=("Arial",11)).grid(row=7, column=0, sticky="w")
percent_frame = ttk.Frame(left)
percent_frame.grid(row=7, column=1, pady=5, sticky="w")
entry_percent = ttk.Entry(percent_frame, width=13, font=("Arial",11),
                          validate="key", validatecommand=(root.register(validate_numbers_only), "%P"))
entry_percent.pack(side="left")
disable_percent_var = tk.BooleanVar(value=False)
toggle_percent_btn_widget = tk.Button(percent_frame, text="✅", width=3, font=("Arial",10),
    bg="green", fg="white", command=toggle_percent_btn)
toggle_percent_btn_widget.pack(side="left", padx=8)

tk.Button(left, text="➕ Ҳисоб кардан ва нишон додан", command=ҳисоб_кардан,
          font=("Arial",12,"bold"), bg="#004488", fg="white", width=41)\
    .grid(row=8, column=0, columnspan=4, pady=10, sticky="w")

ttk.Label(left, text="📄 Натиҷа:", font=("Arial",11,"bold"))\
    .grid(row=9, column=0, columnspan=2, sticky="w", pady=(10, 5))

left_output_box = tk.Text(left, height=10, width=41, font=("Consolas", 14), wrap="word", state="disabled")
left_output_box.grid(row=10, column=0, columnspan=2, pady=5, sticky="nsew", padx=(0, 100))  # --- ИСЛОҲ ---

tk.Button(left, text="✅ Илова ба анбор ➡️", command=ворид_кардан_ба_анбор,
          bg="#004488", fg="white", font=("Arial",10), width=33)\
    .grid(row=11, column=0, columnspan=2, sticky="w", pady=5)

tk.Button(left, text="📋 Ревизия", command=lambda: messagebox.showinfo("Маълумот","Функсияи ревизия ҳоло нест."),
          bg="#0066cc", fg="white", font=("Arial",10), width=33)\
    .grid(row=12, column=0, columnspan=2, sticky="w", pady=5)

tk.Button(left, text="🧹 Пок кардани натиҷаҳо", command=пок_натиҷа,
          bg="gray", fg="white", font=("Arial",10), width=30)\
    .grid(row=13, column=0, columnspan=2, sticky="w", pady=10)

ttk.Label(right, text="📦 Ҷадвали анбор", font=("Arial", 14, "bold")).pack(anchor="w")

tree_frame = ttk.Frame(right)
tree_frame.pack(fill=tk.BOTH, expand=True, padx=(20,0))  # --- ИСЛОҲ ---

tree_columns = (
    "мол", "шумора", "нархи_омад", "фоиз", "фоида_аз_1",
    "нархи_фуруш", "фоидаи_умумӣ", "санаи_воридот", "срок"
)

headers = [
    "🏷️ мол", "🔢 шумора", "💵 нархи омад", "📈 фоиз",
    "📊 фоида аз 1", "💰 нархи фурӯш", "📦 фоидаи умумӣ",
    "📅 санаи воридот", "📅 срок"
]

tree = ttk.Treeview(tree_frame, columns=tree_columns, show="headings", height=20)

widths = [170, 70, 95, 55, 93, 100, 110, 110, 80]

for col, w, head in zip(tree_columns, widths, headers):
    tree.heading(col, text=head)
    tree.column(col, width=w, minwidth=w, stretch=False, anchor="center")

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # --- ИСЛОҲ ---
scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scrollbar.set)

search_frame = ttk.Frame(right)
search_frame.pack(anchor="nw", padx=(20,0), pady=(5, 0))
ttk.Label(search_frame, text="🔍 ҷустуҷӯи мол:", font=("Arial",10)).pack(side="left")
entry_search = ttk.Entry(search_frame, width=30, font=("Arial",11), validate="key",
                         validatecommand=(root.register(lambda t: True), "%P"))
entry_search.pack(side="left", padx=5)
entry_search.bind("<KeyRelease>", refresh_treeview_filter)

tree.tag_configure('evenrow', background='#E8E8E8')
tree.tag_configure('oddrow', background='#DFDFDF')

last_result = {}

root.mainloop()
