import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import random

# === Темы ===
themes = {
    "Светлая": {"bg": "white", "fg": "black"},
    "Тёмная": {"bg": "#2c2c2c", "fg": "white"},
    "Радужная": {"bg": random.choice(["#ff9999", "#99ff99", "#9999ff", "#ffff99"]), "fg": "black"},
}

def apply_theme(theme_name):
    theme = themes[theme_name]
    root.configure(bg=theme["bg"])
    for widget in root.winfo_children():
        try:
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        except:
            pass

def update_table(data):
    tree.delete(*tree.get_children())
    for row in data:
        tree.insert("", "end", values=row)

def load_database():
    global df, headers
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        return
    try:
        df = pd.read_excel(file_path)
        headers = list(df.columns)
        tree["columns"] = headers
        tree["show"] = "headings"
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')
        update_table(df.values.tolist())
        # Активируем кнопки после загрузки базы
        search_btn.config(state="normal")
        price_btn.config(state="normal")
        brand_entry.config(state="normal")
        messagebox.showinfo("Успех", "База успешно загружена!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

def search_by_brand():
    brand = brand_entry.get().lower()
    if brand:
        if 'Фирма' in df.columns:
            filtered = df[df['Фирма'].str.lower().str.contains(brand)]
            update_table(filtered.values.tolist())
        else:
            messagebox.showerror("Ошибка", "В файле нет столбца 'Фирма'!")
    else:
        update_table(df.values.tolist())

sort_asc = [True]
def sort_by_price():
    if 'Цена (₽)' in df.columns:
        sorted_df = df.sort_values(by='Цена (₽)', ascending=sort_asc[0])
        update_table(sorted_df.values.tolist())
        sort_asc[0] = not sort_asc[0]
    else:
        messagebox.showerror("Ошибка", "В файле нет столбца 'Цена (₽)'!")

# === Интерфейс ===
root = tk.Tk()
root.title("Уход за волосами")
root.geometry("1000x600")

# === Заголовок ===
label = tk.Label(root, text="База данных по уходу за волосами", font=("Arial", 16, "bold"))
label.pack(pady=10)

# === Панель поиска и фильтра ===
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

tk.Button(search_frame, text="Загрузить базу", command=load_database).pack(side="left", padx=5)

tk.Label(search_frame, text="Фирма:").pack(side="left")
brand_entry = tk.Entry(search_frame, state="disabled")
brand_entry.pack(side="left", padx=5)

search_btn = tk.Button(search_frame, text="Поиск по фирме", command=search_by_brand, state="disabled")
search_btn.pack(side="left", padx=5)

price_btn = tk.Button(search_frame, text="Цена", command=sort_by_price, state="disabled")
price_btn.pack(side="left", padx=5)

# === Таблица ===
frame = tk.Frame(root)
frame.pack(expand=True, fill='both', padx=10)

tree = ttk.Treeview(frame)
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
# === Темы ===
theme_frame = tk.Frame(root)
theme_frame.pack(pady=5)
tk.Label(theme_frame, text="Тема:").pack(side="left", padx=5)

for name in themes:
    tk.Button(theme_frame, text=name, command=lambda n=name: apply_theme(n)).pack(side="left", padx=5)

# === Факт ===
facts = [
    "Волосы состоят из кератина.",
    "Мы теряем до 100 волос в день.",
    "Маски улучшают эластичность волос.",
    "Слишком частое мытьё — вредно.",
    "Мокрые волосы более уязвимы к повреждениям.",
    "Температура воды влияет на блеск волос.",
    "Масла защищают волосы от ломкости."
]

tk.Button(
    root,
    text="💡 Факт о волосах",
    command=lambda: messagebox.showinfo("Факт", random.choice(facts))
).pack(pady=10)

root.mainloop()