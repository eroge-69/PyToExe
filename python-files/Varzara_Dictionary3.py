import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "dictionary_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)

def add_word(event=None):
    fa = fa_entry.get().strip()
    en = en_entry.get().strip()
    if fa and en:
        dictionary[fa] = en
        refresh_table()
        fa_entry.delete(0, tk.END)
        en_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("هشدار", "لطفاً هر دو فیلد را پر کنید.")

def on_select(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected)
        fa_word = item["values"][0]
        en_word = item["values"][1]
        fa_entry.delete(0, tk.END)
        en_entry.delete(0, tk.END)
        fa_entry.insert(0, fa_word)
        en_entry.insert(0, en_word)
        edit_button.config(state=tk.NORMAL)
    else:
        edit_button.config(state=tk.DISABLED)

def edit_word():
    selected = tree.selection()
    if selected:
        old_fa = tree.item(selected)["values"][0]
        new_fa = fa_entry.get().strip()
        new_en = en_entry.get().strip()
        if new_fa and new_en:
            if old_fa in dictionary:
                del dictionary[old_fa]
            dictionary[new_fa] = new_en
            refresh_table()
            fa_entry.delete(0, tk.END)
            en_entry.delete(0, tk.END)
            edit_button.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("هشدار", "لطفاً هر دو فیلد را پر کنید.")

def delete_word():
    selected = tree.selection()
    if selected:
        fa_word = tree.item(selected)["values"][0]
        if fa_word in dictionary:
            del dictionary[fa_word]
            refresh_table()
            fa_entry.delete(0, tk.END)
            en_entry.delete(0, tk.END)
            edit_button.config(state=tk.DISABLED)

def refresh_table():
    tree.delete(*tree.get_children())
    for fa, en in sorted(dictionary.items(), key=lambda x: x[0]):
        tree.insert("", tk.END, values=(fa, en))

def live_search(event):
    query = search_entry.get().strip().lower()
    tree.delete(*tree.get_children())
    for fa, en in dictionary.items():
        if query in fa.lower() or query in en.lower():
            tree.insert("", tk.END, values=(fa, en))

def sort_by_persian():
    sorted_items = sorted(dictionary.items(), key=lambda x: x[0])
    tree.delete(*tree.get_children())
    for fa, en in sorted_items:
        tree.insert("", tk.END, values=(fa, en))
    tree.column("fa", anchor="e")
    tree.column("en", anchor="w")

def sort_by_english():
    sorted_items = sorted(dictionary.items(), key=lambda x: x[1])
    tree.delete(*tree.get_children())
    for fa, en in sorted_items:
        tree.insert("", tk.END, values=(fa, en))
    tree.column("fa", anchor="e")
    tree.column("en", anchor="w")

def on_exit():
    save_data()
    root.destroy()

# ---------- برنامه اصلی ----------
root = tk.Tk()
root.title("📘 دیکشنری ورزآرا - آزمایشی")
root.geometry("680x560")
root.configure(bg="#f2f2f2")
root.option_add("*Font", "Tahoma 12")

dictionary = load_data()

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=('Tahoma', 12, 'bold'), background="#2980b9", foreground="white")
style.configure("Treeview", font=('Tahoma', 11), rowheight=28, background="#ffffff", fieldbackground="#ffffff")

# قاب ورودی
input_frame = tk.Frame(root, bg="#f2f2f2")
input_frame.pack(pady=10)

fa_label = tk.Label(input_frame, text="کلمه فارسی:", bg="#f2f2f2")
fa_label.grid(row=0, column=2, padx=5, sticky="w")
fa_entry = tk.Entry(input_frame, width=30, justify="right", bd=2, relief="groove")
fa_entry.grid(row=0, column=1, padx=5)

en_label = tk.Label(input_frame, text="ترجمه انگلیسی:", bg="#f2f2f2")
en_label.grid(row=1, column=2, padx=5, sticky="w")
en_entry = tk.Entry(input_frame, width=30, bd=2, relief="groove")
en_entry.grid(row=1, column=1, padx=5)

add_button = tk.Button(input_frame, text="➕ افزودن (Enter)", bg="#27ae60", fg="white", command=add_word)
add_button.grid(row=2, column=1, pady=10, sticky="w")

edit_button = tk.Button(input_frame, text="✏️ ویرایش و ذخیره", bg="#f39c12", fg="white", state=tk.DISABLED, command=edit_word)
edit_button.grid(row=2, column=2, sticky="w")

# قاب جستجو
search_frame = tk.Frame(root, bg="#f2f2f2")
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text="🔍 جستجوی زنده:", bg="#f2f2f2")
search_label.pack(side=tk.RIGHT)
search_entry = tk.Entry(search_frame, width=40, bd=2, relief="groove")
search_entry.pack(side=tk.RIGHT, padx=5)
search_entry.bind("<KeyRelease>", live_search)

# جدول کلمات
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(tree_frame, columns=("fa", "en"), show="headings", height=10)
tree.heading("fa", text="کلمه فارسی")
tree.heading("en", text="ترجمه انگلیسی")

tree.column("fa", width=220, anchor="e")
tree.column("en", width=220, anchor="w")

tree.pack(fill=tk.BOTH, expand=True, padx=10)
tree.bind("<<TreeviewSelect>>", on_select)

# دکمه‌های پایینی
button_frame = tk.Frame(root, bg="#f2f2f2")
button_frame.pack(pady=10)

sort_fa_btn = tk.Button(button_frame, text="🔤 مرتب‌سازی فارسی", bg="#3498db", fg="white", command=sort_by_persian)
sort_fa_btn.pack(side=tk.RIGHT, padx=5)

sort_en_btn = tk.Button(button_frame, text="🔤 مرتب‌سازی انگلیسی", bg="#3498db", fg="white", command=sort_by_english)
sort_en_btn.pack(side=tk.RIGHT, padx=5)

delete_btn = tk.Button(button_frame, text="🗑️ حذف", bg="#e74c3c", fg="white", command=delete_word)
delete_btn.pack(side=tk.RIGHT, padx=5)

exit_btn = tk.Button(button_frame, text="💾 ذخیره و خروج", bg="#7f8c8d", fg="white", command=on_exit)
exit_btn.pack(side=tk.LEFT)

# کلید میانبر
root.bind("<Return>", add_word)

refresh_table()
root.mainloop()
