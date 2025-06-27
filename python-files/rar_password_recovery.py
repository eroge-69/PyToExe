import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import rarfile
import os
import threading
import queue
import itertools
import string
import logging
from datetime import datetime

class RarPasswordRecoveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Восстановление пароля RAR")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.task_queue = queue.Queue()
        self.running = False
        self.setup_logging()
        self.create_widgets()

    def setup_logging(self):
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, f"rar_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(filename=log_file, level=logging.INFO, 
                           format="%(asctime)s - %(levelname)s - %(message)s", encoding='utf-8')

    def create_widgets(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Восстановление пароля для RAR архивов", font=("Arial", 14, "bold")).pack(pady=10)

        # RAR Files Selection
        ttk.Label(main_frame, text="Выберите RAR файлы:").pack(pady=5)
        self.rar_listbox = tk.Listbox(main_frame, width=60, height=4)
        self.rar_listbox.pack(pady=5)
        ttk.Button(main_frame, text="Добавить RAR", command=self.browse_rar).pack(pady=5)
        ttk.Button(main_frame, text="Очистить список", command=self.clear_rar_list).pack(pady=5)

        # Wordlist Selection
        ttk.Label(main_frame, text="Выберите файл со списком паролей (опционально):").pack(pady=5)
        self.wordlist_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.wordlist_path_var, width=50, state="readonly").pack(pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_wordlist).pack(pady=5)

        # Output Directory
        ttk.Label(main_frame, text="Выберите папку для извлечения:").pack(pady=5)
        self.output_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path_var, width=50, state="readonly").pack(pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_output).pack(pady=5)

        # Password Generation Options
        ttk.Label(main_frame, text="Настройки генерации паролей:").pack(pady=5)
        self.generate_passwords_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Генерировать пароли, если список не указан", 
                       variable=self.generate_passwords_var).pack(pady=5)
        ttk.Label(main_frame, text="Максимальная длина пароля:").pack()
        self.max_length_var = tk.IntVar(value=8)
        ttk.Spinbox(main_frame, from_=1, to_=12, textvariable=self.max_length_var, width=5).pack(pady=5)

        # Progress
        self.progress_var = tk.StringVar(value="Готово к началу")
        ttk.Label(main_frame, textvariable=self.progress_var, wraplength=600).pack(pady=10)
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Начать восстановление", command=self.start_recovery, 
                  style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отменить", command=self.cancel_recovery, 
                  style="TButton").pack(side=tk.LEFT, padx=5)

        # Style
        style = ttk.Style()
        style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 12))

    def browse_rar(self):
        files = filedialog.askopenfilenames(filetypes=[("RAR files", "*.rar")])
        for file in files:
            if file not in self.rar_listbox.get(0, tk.END):
                self.rar_listbox.insert(tk.END, file)

    def clear_rar_list(self):
        self.rar_listbox.delete(0, tk.END)

    def browse_wordlist(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.wordlist_path_var.set(file_path)

    def browse_output(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path_var.set(folder_path)

    def validate_inputs(self):
        if not self.rar_listbox.get(0, tk.END):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите хотя бы один RAR файл.")
            return False
        if not self.output_path_var.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите папку для извлечения.")
            return False
        if not os.path.exists(self.output_path_var.get()):
            messagebox.showerror("Ошибка", "Указанная папка для извлечения не существует.")
            return False
        return True

    def generate_passwords(self, max_length):
        characters = string.ascii_letters + string.digits
        for length in range(1, max_length + 1):
            for password in itertools.product(characters, repeat=length):
                yield ''.join(password)

    def start_recovery(self):
        if not self.validate_inputs():
            return
        if self.running:
            messagebox.showwarning("Предупреждение", "Восстановление уже выполняется!")
            return

        self.running = True
        self.progress_var.set("Подготовка к восстановлению...")
        self.progress_bar['value'] = 0
        self.root.update()

        rar_files = self.rar_listbox.get(0, tk.END)
        wordlist_path = self.wordlist_path_var.get()
        output_path = self.output_path_var.get()

        # Start recovery in a separate thread
        self.task_queue = queue.Queue()
        threading.Thread(target=self.recovery_worker, args=(rar_files, wordlist_path, output_path), daemon=True).start()
        self.root.after(100, self.check_queue)

    def recovery_worker(self, rar_files, wordlist_path, output_path):
        try:
            passwords = ["password", "123456", "admin", "test", "qwerty"]
            if wordlist_path and os.path.exists(wordlist_path):
                with open(wordlist_path, 'r', encoding='utf-8') as f:
                    passwords.extend(line.strip() for line in f)
            elif self.generate_passwords_var.get():
                max_length = self.max_length_var.get()
                passwords = self.generate_passwords(max_length)
            else:
                passwords = []

            total_passwords = len(passwords) if isinstance(passwords, list) else 1000  # Estimate for generator
            processed = 0

            for rar_path in rar_files:
                if not self.running:
                    break
                try:
                    with rarfile.RarFile(rar_path) as rar:
                        if not rar.needs_password():
                            self.task_queue.put(("info", f"Архив {rar_path} не защищен паролем."))
                            self.extract_rar(rar, output_path, None)
                            continue

                        for password in passwords:
                            if not self.running:
                                break
                            self.task_queue.put(("progress", processed / total_passwords * 100, f"Попытка пароля для {rar_path}: {password}"))
                            processed += 1
                            logging.info(f"Попытка пароля для {rar_path}: {password}")
                            try:
                                self.extract_rar(rar, output_path, password)
                                self.task_queue.put(("success", f"Пароль найден для {rar_path}: {password}\nФайлы извлечены в {output_path}"))
                                break
                            except RuntimeError:
                                continue
                        else:
                            self.task_queue.put(("warning", f"Пароль не найден для {rar_path}."))
                except Exception as e:
                    self.task_queue.put(("error", f"Ошибка при обработке {rar_path}: {e}"))
                    logging.error(f"Ошибка при обработке {rar_path}: {e}")

            self.task_queue.put(("done", "Восстановление завершено."))
        except Exception as e:
            self.task_queue.put(("error", f"Общая ошибка: {e}"))
            logging.error(f"Общая ошибка: {e}")

    def extract_rar(self, rar, output_path, password):
        try:
            rar.extractall(path=output_path, pwd=password)
            logging.info(f"Успешное извлечение в {output_path} с паролем {password}")
        except RuntimeError as e:
            if "password" in str(e).lower():
                raise RuntimeError("Неверный пароль")
            raise

    def check_queue(self):
        try:
            while True:
                msg_type, *args = self.task_queue.get_nowait()
                if msg_type == "progress":
                    progress, text = args
                    self.progress_bar['value'] = progress
                    self.progress_var.set(text)
                elif msg_type == "success":
                    messagebox.showinfo("Успех", args[0])
                    self.progress_var.set("Готово к началу")
 self.progress_bar['value'] = 0
                elif msg_type == "warning":
                    messagebox.showwarning("Предупреждение", args[0])
                elif msg_type == "error":
                    messagebox.showerror("Ошибка", args[0])
                elif msg_type == "info":
                    messagebox.showinfo("Информация", args[0])
                elif msg_type == "done":
                    self.progress_var.set("Готово к началу")
                    self.progress_bar['value'] = 0
                    self.running = False
        except queue.Empty:
            if self.running:
                self.root.after(100, self.check_queue)
            else:
                self.progress_var.set("Готово к началу")
                self.progress_bar['value'] = 0

    def cancel_recovery(self):
        if self.running:
            self.running = False
            self.progress_var.set("Отмена операции...")
            self.root.after(1000, lambda: self.progress_var.set("Готово к началу"))
            messagebox.showinfo("Отмена", "Операция восстановления была отменена.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RarPasswordRecoveryApp(root)
    root.mainloop()