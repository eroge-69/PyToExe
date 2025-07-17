import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "dictionary.json"
COLORS = [
    ("Красный", "#ff5f56"),
    ("Оранжевый", "#ffbd2e"),
    ("Жёлтый", "#ffe14a"),
    ("Зелёный", "#27c93f"),
    ("Синий", "#007aff"),
    ("Фиолетовый", "#a259c1"),
    ("Серый", "#8e8e93")
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def refresh_list():
    terms_list.delete(*terms_list.get_children())
    data_to_display = []
    sort_mode = sort_var.get()
    if sort_mode == "alphabet":
        # Алфавитная сортировка
        data_to_display = sorted(dictionary, key=lambda x: x["term"].lower())
        for entry in data_to_display:
            color_hex = next((c[1] for c in COLORS if c[0] == entry["color"]), "#ffffff")
            terms_list.insert('', 'end', values=('', entry["term"], entry["color"]), tags=(entry["color"],))
            terms_list.tag_configure(entry["color"], background=color_hex)
    else:
        # Группировка по цвету
        for color_name, color_hex in COLORS:
            # Группа терминов данного цвета, отсортированных по алфавиту
            group = [entry for entry in dictionary if entry["color"] == color_name]
            if group:
                parent = terms_list.insert('', 'end', values=('', f"— {color_name} —", ''), tags=(color_name + "_grp",))
                terms_list.tag_configure(color_name + "_grp", background=color_hex)
                group_sorted = sorted(group, key=lambda x: x["term"].lower())
                for entry in group_sorted:
                    terms_list.insert(parent, 'end', values=('', entry["term"], entry["color"]), tags=(entry["color"],))
                    terms_list.tag_configure(entry["color"], background=color_hex)

def on_add():
    term = term_var.get().strip()
    desc = desc_text.get("1.0", tk.END).strip()
    color = color_var.get()
    if not term or not desc:
        messagebox.showerror("Ошибка", "Заполните оба поля!")
        return
    for entry in dictionary:
        if entry["term"].lower() == term.lower():
            messagebox.showwarning("Дубликат", "Такой термин уже есть!")
            return
    dictionary.append({"term": term, "description": desc, "color": color})
    save_data(dictionary)
    refresh_list()
    term_var.set("")
    desc_text.delete("1.0", tk.END)

def on_select(event):
    selected = terms_list.selection()
    if selected:
        item = terms_list.item(selected[0])
        term = item['values'][1]
        # Игнорируем выбор группы-цвета
        if term.startswith("— "):
            return
        entry = next((e for e in dictionary if e["term"] == term), None)
        if entry:
            show_description(entry)

def show_description(entry):
    win = tk.Toplevel(root)
    win.title(entry["term"])
    win.geometry("400x200")
    canvas = tk.Canvas(win, width=20, height=20, highlightthickness=0)
    canvas.create_oval(2, 2, 18, 18, fill=next((c[1] for c in COLORS if c[0]==entry["color"]), "#ffffff"), outline="")
    canvas.pack(pady=10)
    tk.Label(win, text=entry["term"], font=("Helvetica", 16, "bold")).pack()
    tk.Label(win, text=entry["color"], fg=next((c[1] for c in COLORS if c[0]==entry["color"]), "#000")).pack()
    tk.Label(win, text=entry["description"], wraplength=350, justify="left").pack(pady=10)
    tk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

def on_sort_change():
    refresh_list()

root = tk.Tk()
root.title("Словарь терминов")
root.geometry("650x540")

dictionary = load_data()

# Сортировка
sort_var = tk.StringVar(value="alphabet")
sort_frame = tk.Frame(root)
sort_frame.pack(pady=4)
tk.Label(sort_frame, text="Сортировка: ").pack(side="left")
tk.Radiobutton(sort_frame, text="По алфавиту", variable=sort_var, value="alphabet", command=on_sort_change).pack(side="left")
tk.Radiobutton(sort_frame, text="По цвету", variable=sort_var, value="color", command=on_sort_change).pack(side="left")

# Список терминов
terms_list = ttk.Treeview(root, columns=("color", "Термин", "Цвет"), show="headings", height=16)
terms_list.heading("color", text="")
terms_list.heading("Термин", text="Термин")
terms_list.heading("Цвет", text="Цвет")
terms_list.column("color", width=30, anchor="center")
terms_list.column("Термин", width=220)
terms_list.column("Цвет", width=110)
terms_list.pack(fill="both", expand=True, pady=10)
terms_list.bind("<<TreeviewSelect>>", on_select)

refresh_list()

# Ввод новых терминов
frm = tk.LabelFrame(root, text="Добавить новый термин", padx=10, pady=10)
frm.pack(fill="x", padx=10, pady=10)

term_var = tk.StringVar()
color_var = tk.StringVar(value=COLORS[0][0])
tk.Label(frm, text="Термин:").grid(row=0, column=0, sticky="e")
tk.Entry(frm, textvariable=term_var, width=30).grid(row=0, column=1, sticky="w")

tk.Label(frm, text="Описание:").grid(row=1, column=0, sticky="ne")
desc_text = tk.Text(frm, width=45, height=3)
desc_text.grid(row=1, column=1, sticky="w")

tk.Label(frm, text="Метка-цвет:").grid(row=2, column=0, sticky="e")
color_menu = tk.OptionMenu(frm, color_var, *[c[0] for c in COLORS])
color_menu.grid(row=2, column=1, sticky="w")

tk.Button(frm, text="Добавить", command=on_add, width=15).grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()