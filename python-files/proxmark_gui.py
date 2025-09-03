import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess

class ProxmarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxmark3 HID Cloner")

        # Параметры
        tk.Label(root, text="COM порт:").grid(row=0, column=0, sticky="e")
        self.com_entry = tk.Entry(root)
        self.com_entry.insert(0, "COM3")
        self.com_entry.grid(row=0, column=1)

        tk.Label(root, text="Facility Code:").grid(row=1, column=0, sticky="e")
        self.fc_entry = tk.Entry(root)
        self.fc_entry.insert(0, "85")
        self.fc_entry.grid(row=1, column=1)

        tk.Label(root, text="Начальный CN:").grid(row=2, column=0, sticky="e")
        self.start_entry = tk.Entry(root)
        self.start_entry.insert(0, "29999")
        self.start_entry.grid(row=2, column=1)

        tk.Label(root, text="Конечный CN:").grid(row=3, column=0, sticky="e")
        self.end_entry = tk.Entry(root)
        self.end_entry.insert(0, "30010")
        self.end_entry.grid(row=3, column=1)

        # Кнопки
        self.start_button = tk.Button(root, text="Старт", command=self.start_process)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.next_button = tk.Button(root, text="Далее (записать карту)", command=self.write_card, state="disabled")
        self.next_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Лог
        self.log = scrolledtext.ScrolledText(root, width=60, height=15, state="disabled")
        self.log.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # Внутренние данные
        self.current = None
        self.end = None

    def log_message(self, msg):
        self.log.config(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.yview(tk.END)
        self.log.config(state="disabled")

    def start_process(self):
        try:
            self.com = self.com_entry.get().strip()
            self.fc = int(self.fc_entry.get().strip())
            self.current = int(self.start_entry.get().strip())
            self.end = int(self.end_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные параметры!")
            return

        self.log_message(f"Старт записи карт с CN {self.current} по {self.end}, FC={self.fc}, порт={self.com}")
        self.start_button.config(state="disabled")
        self.next_button.config(state="normal")

    def write_card(self):
        if self.current is None or self.end is None:
            return

        if self.current > self.end:
            self.log_message("Готово! Все карты прошиты.")
            self.next_button.config(state="disabled")
            return

        cmd = [
            "proxmark3.exe",
            self.com,
            "lf", "hid", "clone",
            "-w", "H10301",
            "--fc", str(self.fc),
            "--cn", str(self.current)
        ]

        self.log_message(f">>> Запись карты CN={self.current}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            self.log_message(result.stdout)
            if result.stderr:
                self.log_message("Ошибка: " + result.stderr)
        except Exception as e:
            self.log_message("Ошибка запуска: " + str(e))

        self.current += 1

