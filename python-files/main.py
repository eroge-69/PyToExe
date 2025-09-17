import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False  # такой юзер уже есть
    conn.close()
    return True

def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0] #айдишник 
    return None

def save_name(user_id, name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO names (user_id, name) VALUES (?, ?)', (user_id, name))
    conn.commit()
    conn.close()

def get_names(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM names WHERE user_id = ?', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return [item[0] for item in data]

class RegistrationWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Регистрация")
        self.geometry("258x400")

        self.label_user = tk.Label(self, text="Имя пользователя:")
        self.label_user.pack(pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        self.label_pass = tk.Label(self, text="Пароль:")
        self.label_pass.pack(pady=5)
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        self.btn_register = tk.Button(self, text="Зарегистрироваться", command=self.register)
        self.btn_register.pack(pady=10)

    def register(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showerror("Ошибка", " заполните все поля.")
            return
        
        if register_user(username, password):
            messagebox.showinfo("Успех", "Регистрация успешна!")
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Имя пользователя уже занято.")

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Вход")
        self.geometry("300x200")

        self.label_user = tk.Label(self, text="Имя пользователя:")
        self.label_user.pack(pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        self.label_pass = tk.Label(self, text="Пароль:")
        self.label_pass.pack(pady=5)
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        self.btn_login = tk.Button(self, text="Войти", command=self.login)
        self.btn_login.pack(pady=10)

        self.btn_register = tk.Button(self, text="Зарегистрироваться", command=self.open_registration)
        self.btn_register.pack()

    def open_registration(self):
        reg_win = RegistrationWindow(self)
        reg_win.grab_set()  # сделаем окно модальным

    def login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        user_id = validate_user(username, password)
        if user_id:
            self.destroy()
            MainApp(user_id)
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

class MainApp(tk.Tk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Добавление имён")
        self.geometry("400x300")

        self.label = tk.Label(self, text="Введите имя для добавления:")
        self.label.pack(pady=5)

        self.entry_name = tk.Entry(self)
        self.entry_name.pack(pady=5)

        self.btn_add = tk.Button(self, text="Добавить имя", command=self.add_name)
        self.btn_add.pack(pady=5)

        self.names_listbox = tk.Listbox(self)
        self.names_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_names()

        self.mainloop()

    def load_names(self):
        self.names_listbox.delete(0, tk.END)
        names = get_names(self.user_id)
        for name in names:
            self.names_listbox.insert(tk.END, name)

    def add_name(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Имя не может быть пустым.")
            return
        save_name(self.user_id, name)
        self.entry_name.delete(0, tk.END)
        self.load_names()

# --- Запуск ---

if __name__ == "__main__":
    init_db()
    app = LoginWindow()
    app.mainloop()
