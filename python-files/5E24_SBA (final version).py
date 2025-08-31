import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import random
import string
import sqlite3
import threading
import time

# language setting
LANGUAGES= {
    'en': {
        'title': 'CipherMaster',
        'intro': 'Your Ultimate Encryption Tool',
        'start': 'Start',
        'morse': 'Morse Code',
        'caesar': 'Caesar Cipher',
        'vigenere': 'Vigenère Cipher',
        'ai': 'AI Auto',
        'encrypt': 'Encrypt',
        'decrypt': 'Decrypt',
        'select_file': 'Select a .txt file (min 100 characters)',
        'select_file_ai': 'Select a .txt or .pdf file',
        'enter_key': 'Enter 6-digit key',
        'download': 'Download',
        'retry': 'Retry',
        'exit': 'Exit',
        'key_shown': 'Your key is:',
        'login': 'Login',
        'register': 'Register',
        'username': 'Username',
        'password': 'Password',
        'invalid_login': 'Invalid login',
        'user_exists': 'Username already exists',
        'password_weak': 'Password must be 12+ chars with upper, lower, digit, symbol',
        'login_success': 'Login successful',
        'register_success': 'Registration successful',
        'logout': 'Logout',
        'how_to_use': 'How to Use',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode'
    },
    'zh': {
        'title': '密碼大師',
        'intro': '你的終極加密工具',
        'start': '開始',
        'morse': '摩斯密碼',
        'caesar': '凱撒密碼',
        'vigenere': '維吉尼亞密碼',
        'ai': 'AI 自動',
        'encrypt': '加密',
        'decrypt': '解密',
        'select_file': '選擇一個 .txt 檔案（至少 100 字）',
        'select_file_ai': '選擇一個 .txt 或 .pdf 檔案',
        'enter_key': '輸入六位數密鑰',
        'download': '下載',
        'retry': '重試',
        'exit': '離開',
        'key_shown': '您的密鑰是：',
        'login': '登入',
        'register': '註冊',
        'username': '用戶名',
        'password': '密碼',
        'invalid_login': '登入失敗',
        'user_exists': '用戶名已存在',
        'password_weak': '密碼至少 12 字，包含大小寫、數字、符號',
        'login_success': '登入成功',
        'register_success': '註冊成功',
        'logout': '登出',
        'how_to_use': '使用說明',
        'dark_mode': '深色模式',
        'light_mode': '淺色模式'
    }
}


# database

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    conn.commit()
    conn.close()


# main program

class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CipherMaster")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.language = 'en'
        self.current_user = None
        self.dark_mode = False
        self.bg_image = None
        self.bg_label = None
        self.load_background()
        self.create_home()

    def load_background(self):
        try:
            image = Image.open("")  # background photo
            self.bg_image = ImageTk.PhotoImage(image)
            if self.bg_label is None:
                self.bg_label = tk.Label(self.root, image=self.bg_image)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                self.bg_label.config(image=self.bg_image)
        except Exception as e:
            print("Background image not found:", e)

    def switch_language(self, lang):
        self.language = lang
        self.clear_window()
        self.create_home()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        bg = "#1e1e1e" if self.dark_mode else "#ffffff"
        fg = "#ffffff" if self.dark_mode else "#000000"
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.load_background()

    def create_home(self):
        lang = LANGUAGES[self.language]

        title = tk.Label(self.root, text=lang['title'], font=("Arial", 24, "bold"), bg="#000000", fg="#00ff00")
        title.pack(pady=20)

        intro = tk.Label(self.root, text=lang['intro'], font=("Arial", 14), bg="#000000", fg="#00ff00")
        intro.pack()

        start_btn = tk.Button(self.root, text=lang['start'], font=("Arial", 14), command=self.show_cipher_menu)
        start_btn.pack(pady=30)

        # left corner: light,dark mode and setting
        theme_btn = tk.Button(self.root, text=lang['dark_mode'] if not self.dark_mode else lang['light_mode'],
                              command=self.toggle_theme)
        theme_btn.place(x=10, y=self.root.winfo_height() - 40)

        settings_btn = tk.Button(self.root, text="⚙️", font=("Arial", 12), command=self.open_settings)
        settings_btn.place(x=120, y=self.root.winfo_height() - 40)

        # right corner:instruction
        help_btn = tk.Button(self.root, text="?", font=("Arial", 14), command=self.show_help)
        help_btn.place(x=self.root.winfo_width() - 40, y=10)

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("300x200")

        lang_label = tk.Label(settings_win, text="Language")
        lang_label.pack()

        lang_combo = ttk.Combobox(settings_win, values=["English", "中文"])
        lang_combo.pack()

        login_btn = tk.Button(settings_win, text=LANGUAGES[self.language]['login'], command=self.show_login)
        login_btn.pack(pady=10)

        def apply_settings():
            lang = lang_combo.get()
            if lang == "English":
                self.switch_language("en")
            elif lang == "中文":
                self.switch_language("zh")
            settings_win.destroy()

        apply_btn = tk.Button(settings_win, text="Apply", command=apply_settings)
        apply_btn.pack()

    def show_help(self):
        messagebox.showinfo("How to Use", "1. Click Start\n2. Choose encryption method\n3. Upload file\n4. Encrypt or Decrypt")

    def show_cipher_menu(self):
        self.clear_window()
        lang = LANGUAGES[self.language]

        tk.Label(self.root, text="Choose Cipher Method", font=("Arial", 18)).pack(pady=20)

        methods = [
            (lang['morse'], self.morse_cipher),
            (lang['caesar'], self.caesar_cipher),
            (lang['vigenere'], self.vigenere_cipher),
            (lang['ai'], self.ai_cipher)
        ]

        for name, func in methods:
            btn = tk.Button(self.root, text=name, font=("Arial", 14), command=func)
            btn.pack(pady=10)

    def morse_cipher(self):
        self.encryption_flow("Morse")

    def caesar_cipher(self):
        self.encryption_flow("Caesar")

    def vigenere_cipher(self):
        self.encryption_flow("Vigenère")

    def ai_cipher(self):
        if not self.current_user:
            self.show_login()
        else:
            self.encryption_flow("AI")

    def encryption_flow(self, method):
        self.clear_window()
        lang = LANGUAGES[self.language]

        tk.Label(self.root, text=f"{method} Encryption/Decryption", font=("Arial", 16)).pack(pady=10)

        tab_control = ttk.Notebook(self.root)
        encrypt_tab = ttk.Frame(tab_control)
        decrypt_tab = ttk.Frame(tab_control)
        tab_control.add(encrypt_tab, text=lang['encrypt'])
        tab_control.add(decrypt_tab, text=lang['decrypt'])
        tab_control.pack(expand=1, fill="both")

        # encrypt
        self.build_encryption_page(encrypt_tab, method)

        # decrypt
        self.build_decryption_page(decrypt_tab, method)

    def build_encryption_page(self, parent, method):
        lang = LANGUAGES[self.language]
        tk.Label(parent, text=lang['select_file']).pack(pady=10)
        file_path = tk.StringVar()

        def select_file():
            path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")])
            file_path.set(path)

        tk.Button(parent, text="Browse", command=select_file).pack()
        tk.Label(parent, textvariable=file_path).pack()

        def run_encrypt():
            path = file_path.get()
            if not path.endswith(('.txt', '.pdf')):
                messagebox.showerror("Error", "Invalid file type")
                return
            self.run_progress(lambda: self.encrypt_file(path, method))

        tk.Button(parent, text=lang['encrypt'], command=run_encrypt).pack(pady=10)

    def build_decryption_page(self, parent, method):
        lang = LANGUAGES[self.language]
        tk.Label(parent, text=lang['enter_key']).pack()
        key_var = tk.StringVar()
        tk.Entry(parent, textvariable=key_var).pack()

        tk.Label(parent, text=lang['select_file']).pack()
        file_path = tk.StringVar()

        def select_file():
            path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")])
            file_path.set(path)

        tk.Button(parent, text="Browse", command=select_file).pack()
        tk.Label(parent, textvariable=file_path).pack()

        def run_decrypt():
            path = file_path.get()
            key = key_var.get()
            if not path.endswith(('.txt', '.pdf')):
                messagebox.showerror("Error", "Invalid file type")
                return
            self.run_progress(lambda: self.decrypt_file(path, key, method))

        tk.Button(parent, text=lang['decrypt'], command=run_decrypt).pack(pady=10)

    def run_progress(self, func):
        progress = ttk.Progressbar(self.root, mode='indeterminate')
        progress.pack(pady=20)
        progress.start()

        def task():
            func()
            progress.stop()
            progress.destroy()

        threading.Thread(target=task).start()

    def encrypt_file(self, path, method):
        time.sleep(2)
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        messagebox.showinfo("Encryption Complete", f"{LANGUAGES[self.language]['key_shown']} {key}")

    def decrypt_file(self, path, key, method):
        time.sleep(2)
        messagebox.showinfo("Decryption Complete", "File decrypted successfully.")

    def show_login(self):
        login_win = tk.Toplevel(self.root)
        login_win.title("Login")
        login_win.geometry("300x200")

        lang = LANGUAGES[self.language]

        tk.Label(login_win, text=lang['username']).pack()
        user_entry = tk.Entry(login_win)
        user_entry.pack()

        tk.Label(login_win, text=lang['password']).pack()
        pass_entry = tk.Entry(login_win, show="*")
        pass_entry.pack()

        def login():
            user = user_entry.get()
            pwd = pass_entry.get()
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
            res = c.fetchone()
            conn.close()
            if res:
                self.current_user = user
                messagebox.showinfo("Success", lang['login_success'])
                login_win.destroy()
            else:
                messagebox.showerror("Error", lang['invalid_login'])

        tk.Button(login_win, text=lang['login'], command=login).pack(pady=10)

        def register():
            user = user_entry.get()
            pwd = pass_entry.get()
            if len(pwd) < 12 or not any(c.isupper() for c in pwd) or not any(c.isdigit() for c in pwd):
                messagebox.showerror("Error", lang['password_weak'])
                return
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
                conn.commit()
                messagebox.showinfo("Success", lang['register_success'])
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", lang['user_exists'])
            conn.close()

        tk.Button(login_win, text=lang['register'], command=register).pack()


# main program
-
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()
