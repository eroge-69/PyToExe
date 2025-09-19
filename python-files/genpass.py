import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import string
import os

FILE_NAME = "password_dict.txt"
admin_key = "MySecretAdminKey"

def load_dict():
    dictionary = {}
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    dictionary[key] = val
    return dictionary

def save_dict(dictionary):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        for k, v in dictionary.items():
            f.write(f"{k} : {v}\n")

def random_separator():
    symbols = string.punctuation + string.digits
    return random.choice(symbols)

def generate_phrase():
    if not password_dict:
        result.set("Словарь пуст")
        return
    count = random.randint(3, 5)
    selected_words = random.sample(list(password_dict.keys()), min(count, len(password_dict)))
    translated = [password_dict[w] for w in selected_words]
    phrase = ""
    for i, word in enumerate(translated):
        phrase += word
        if i < len(translated) - 1:
            phrase += random_separator()
    result.set(phrase)

def open_admin_panel():
    def save_changes():
        lines = dict_box.get("1.0", tk.END).strip().split("\n")
        new_dict = {}
        for line in lines:
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                new_dict[key] = val
        save_dict(new_dict)
        global password_dict
        password_dict = new_dict
        messagebox.showinfo("Сохранено", "Словарь сохранён во внешний файл")
        admin_win.destroy()

    admin_win = tk.Toplevel(root)
    admin_win.title("Админ-панель - Редактирование словаря")

    dict_box = tk.Text(admin_win, width=50, height=20)
    dict_box.pack()

    for k, v in password_dict.items():
        dict_box.insert(tk.END, f"{k} : {v}\n")

    tk.Button(admin_win, text="Сохранить изменения", command=save_changes).pack(pady=5)

def admin_login():
    key = simpledialog.askstring("Админ", "Введите ключ администратора:", show="*")
    if key == admin_key:
        open_admin_panel()
    else:
        messagebox.showerror("Ошибка", "Неправильный ключ")

password_dict = load_dict()

root = tk.Tk()
root.title("Генератор парольных фраз")

tk.Label(root, text="Нажмите кнопку для генерации парольной фразы").pack()

result = tk.StringVar()
tk.Label(root, textvariable=result, font=("Arial", 16), fg="blue").pack(pady=10)

tk.Button(root, text="Сгенерировать фразу", command=generate_phrase).pack(pady=5)
tk.Button(root, text="Админ-доступ", command=admin_login).pack(pady=5)

root.mainloop()