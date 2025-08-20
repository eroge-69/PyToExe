import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
import os
import shutil
import subprocess
import bcrypt
import getpass

# Кфг БК мессенджеры ( тут все пути )
BASE_TELEGRAM_DIR = r'C:\Telegram Desktop\Telegram'  # тг путь 
VIBER_EXE_PATH = r'C:\Program Files\Viber\Viber.exe'  # вайбер путь
ACCOUNTS_DIR = os.path.join(os.path.dirname(__file__), 'accounts')  # копии
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')  #  бд лог пас

os.makedirs(ACCOUNTS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                  (id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, name TEXT, path_or_user TEXT)''')
conn.commit()

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Для Ярослава Качана и его банды")
        self.root.geometry("400x300")
        self.current_user_id = None
        self.show_login()

    def show_login(self):
        self.clear_window()
        tk.Label(self.root, text="Логин:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Label(self.root, text="Пароль:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        tk.Button(self.root, text="Войти", command=self.login).pack()
        tk.Button(self.root, text="Регистрация", command=self.register).pack()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')
        cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password, user[1].encode('utf-8')):
            self.current_user_id = user[0]
            self.show_main()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните поля")
            return
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed.decode('utf-8')))
            conn.commit()
            messagebox.showinfo("Успех", "Зарегистрировано")
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Логин занят")

    def show_main(self):
        self.clear_window()
        tk.Label(self.root, text=f"Привет, пользователь {self.current_user_id}!").pack()
        self.account_list = tk.Listbox(self.root)
        self.account_list.pack(fill=tk.BOTH, expand=True)
        self.load_accounts()
        tk.Button(self.root, text="+ Добавить аккаунт", command=self.add_account).pack()
        tk.Button(self.root, text="Запустить выбранный", command=self.launch_account).pack()
        tk.Button(self.root, text="Выход", command=self.show_login).pack()

    def load_accounts(self):
        self.account_list.delete(0, tk.END)
        cursor.execute("SELECT id, type, name FROM accounts WHERE user_id=?", (self.current_user_id,))
        for acc in cursor.fetchall():
            self.account_list.insert(tk.END, f"{acc[1]}: {acc[2]} (id: {acc[0]})")

    def add_account(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Добавить аккаунт")
        tk.Label(add_win, text="Тип:").pack()
        acc_type = ttk.Combobox(add_win, values=["telegram", "viber"])
        acc_type.pack()
        tk.Label(add_win, text="Имя аккаунта:").pack()
        name_entry = tk.Entry(add_win)
        name_entry.pack()
        def save():
            typ = acc_type.get()
            name = name_entry.get()
            if not typ or not name:
                messagebox.showerror("Ошибка", "Заполните поля")
                return
            if typ == "telegram":
                new_dir = os.path.join(ACCOUNTS_DIR, f"telegram_{name}")
                if os.path.exists(new_dir):
                    messagebox.showerror("Ошибка", "Аккаунт существует")
                    return
                try:
                    shutil.copytree(BASE_TELEGRAM_DIR, new_dir)
                    path_or_user = new_dir
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось скопировать Telegram: {str(e)}")
                    return
            elif typ == "viber":
                win_username = f"viber_{name}"
                win_password = simpledialog.askstring("Пароль", "Введите пароль для нового Windows-user:", show="*")
                if not win_password:
                    return
                try:
                    subprocess.check_call(['net', 'user', win_username, win_password, '/add'], shell=True)
                    subprocess.check_call(['net', 'localgroup', 'Users', win_username, '/add'], shell=True)
                except subprocess.CalledProcessError:
                    messagebox.showerror("Ошибка", "Не удалось создать user. Проверьте права админа.")
                    return
                path_or_user = win_username + ';' + win_password
            cursor.execute("INSERT INTO accounts (user_id, type, name, path_or_user) VALUES (?, ?, ?, ?)",
                           (self.current_user_id, typ, name, path_or_user))
            conn.commit()
            add_win.destroy()
            self.load_accounts()
            messagebox.showinfo("Успех", "Аккаунт добавлен. Для первого запуска войдите в него.")
        tk.Button(add_win, text="Сохранить", command=save).pack()

    def launch_account(self):
        selected = self.account_list.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите аккаунт")
            return
        acc_str = self.account_list.get(selected[0])
        acc_id = int(acc_str.split("id: ")[1].strip(")"))
        cursor.execute("SELECT type, name, path_or_user FROM accounts WHERE id=?", (acc_id,))
        typ, name, path_or_user = cursor.fetchone()
        try:
            if typ == "telegram":
                exe_path = os.path.join(path_or_user, 'Telegram.exe')
                subprocess.Popen([exe_path])
            elif typ == "viber":
                win_username, win_password = path_or_user.split(';')
                cmd = f'runas /user:{win_username} /savecred "{VIBER_EXE_PATH}"'
                subprocess.Popen(cmd, shell=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.root.mainloop()
