import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import rarfile
import os
import subprocess
import threading
from itertools import product
import string
import sys

class RARPasswordTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Восстановление пароля RAR")
        self.geometry("600x400")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_frame = ttk.LabelFrame(self, text="Файл RAR")
        self.file_frame.pack(fill="x", padx=10, pady=5)
        self.rar_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.rar_path, width=50)
        self.file_entry.pack(side="left", padx=5, pady=5)
        self.file_browse = ttk.Button(self.file_frame, text="Обзор", command=self.browse_file)
        self.file_browse.pack(side="left", padx=5)

        # Attack Type
        self.attack_frame = ttk.LabelFrame(self, text="Тип атаки")
        self.attack_frame.pack(fill="x", padx=10, pady=5)
        self.attack_type = tk.StringVar(value="dict")
        ttk.Radiobutton(self.attack_frame, text="Словарь", variable=self.attack_type,
                        value="dict", command=self.toggle_attack_options).pack(side="left", padx=10)
        ttk.Radiobutton(self.attack_frame, text="Перебор", variable=self.attack_type,
                        value="brute", command=self.toggle_attack_options).pack(side="left", padx=10)

        # Attack Options Frame
        self.options_frame = ttk.Frame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        # Dictionary Attack Widgets
        self.dict_frame = ttk.Frame(self.options_frame)
        self.dict_frame.pack(fill="x")
        self.wordlist_path = tk.StringVar()
        ttk.Label(self.dict_frame, text="Файл словаря:").pack(side="left")
        self.wordlist_entry = ttk.Entry(self.dict_frame, textvariable=self.wordlist_path, width=40)
        self.wordlist_entry.pack(side="left", padx=5)
        self.wordlist_browse = ttk.Button(self.dict_frame, text="Обзор", command=self.browse_wordlist)
        self.wordlist_browse.pack(side="left")

        # Brute Force Attack Widgets (Initially Hidden)
        self.brute_frame = ttk.Frame(self.options_frame)
        self.brute_frame.pack(fill="x", pady=5)
        self.brute_frame.pack_forget()
        ttk.Label(self.brute_frame, text="Символы:").pack(side="left")
        self.charset = tk.StringVar(value="abcdefghijklmnopqrstuvwxyz")
        self.charset_entry = ttk.Entry(self.brute_frame, textvariable=self.charset, width=30)
        self.charset_entry.pack(side="left", padx=5)
        ttk.Label(self.brute_frame, text="Макс. длина:").pack(side="left")
        self.max_len = tk.IntVar(value=4)
        self.max_len_spin = ttk.Spinbox(self.brute_frame, from_=1, to=10, textvariable=self.max_len, width=3)
        self.max_len_spin.pack(side="left", padx=5)

        # Start Button
        self.start_btn = ttk.Button(self, text="Начать", command=self.start_attack)
        self.start_btn.pack(pady=10)

        # Status Log
        self.status_log = tk.Text(self, height=10, state="disabled")
        self.status_log.pack(fill="both", padx=10, pady=5, expand=True)

    def toggle_attack_options(self):
        if self.attack_type.get() == "dict":
            self.dict_frame.pack(fill="x")
            self.brute_frame.pack_forget()
        else:
            self.dict_frame.pack_forget()
            self.brute_frame.pack(fill="x")

    def log(self, message):
        self.status_log.config(state="normal")
        self.status_log.insert(tk.END, message + "\n")
        self.status_log.config(state="disabled")
        self.status_log.see(tk.END)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("RAR Files", "*.rar")])
        if path:
            self.rar_path.set(path)

    def browse_wordlist(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.wordlist_path.set(path)

    def start_attack(self):
        rar_path = self.rar_path.get()
        if not rar_path or not os.path.exists(rar_path):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите корректный RAR-файл.")
            return

        if self.attack_type.get() == "dict":
            wordlist_path = self.wordlist_path.get()
            if not wordlist_path or not os.path.exists(wordlist_path):
                messagebox.showerror("Ошибка", "Пожалуйста, выберите файл словаря.")
                return
            self.log("Запуск атаки по словарю...")
            self.attack_thread = threading.Thread(target=self.dictionary_attack, args=(rar_path, wordlist_path))
        else:
            charset = self.charset.get()
            max_len = self.max_len.get()
            if not charset:
                messagebox.showerror("Ошибка", "Введите символы для перебора.")
                return
            self.log(f"Запуск перебора паролей (длина до {max_len})...")
            self.attack_thread = threading.Thread(target=self.brute_force_attack, args=(rar_path, charset, max_len))

        self.attack_thread.daemon = True
        self.attack_thread.start()

    def dictionary_attack(self, rar_path, wordlist_path):
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    password = line.strip()
                    if self.check_password(rar_path, password):
                        self.handle_success(rar_path, password)
                        return
            self.log("Пароль не найден в словаре.")
        except Exception as e:
            self.log(f"Ошибка: {e}")

    def brute_force_attack(self, rar_path, charset, max_len):
        for length in range(1, max_len + 1):
            for guess in product(charset, repeat=length):
                password = ''.join(guess)
                if self.check_password(rar_path, password):
                    self.handle_success(rar_path, password)
                    return
        self.log("Пароль не найден при переборе.")

    def check_password(self, rar_path, password):
        try:
            with rarfile.RarFile(rar_path) as rf:
                if rf.needs_password():
                    rf.setpassword(password)
                rf.testrar()  # This checks password validity
            return True
        except rarfile.PasswordRequired:
            return False
        except Exception as e:
            self.log(f"Ошибка: {e}")
            return False

    def handle_success(self, rar_path, password):
        self.log(f"✅ Пароль найден: {password}")
        answer = messagebox.askyesno("Успех", "Пароль найден! Хотите извлечь файлы?")
        if answer:
            self.extract_files(rar_path, password)

    def extract_files(self, rar_path, password):
        extract_dir = os.path.splitext(rar_path)[0] + "_extracted"
        os.makedirs(extract_dir, exist_ok=True)
        try:
            with rarfile.RarFile(rar_path) as rf:
                rf.extractall(path=extract_dir, pwd=password)
            self.log(f"Файлы извлечены в: {extract_dir}")
            messagebox.showinfo("Готово", f"Файлы успешно извлечены в:\n{extract_dir}")
        except Exception as e:
            self.log(f"Ошибка при извлечении: {e}")
            messagebox.showerror("Ошибка", f"Не удалось извлечь файлы: {e}")

if __name__ == "__main__":
    # Add unrar to PATH if bundled
    if hasattr(sys, '_MEIPASS'):
        os.environ['PATH'] += os.pathsep + sys._MEIPASS
    app = RARPasswordTool()
    app.mainloop()