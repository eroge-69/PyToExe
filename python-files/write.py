# esp_flash_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import serial.tools.list_ports
import threading
import time
import os
import logging

# Настройка логирования
LOG_FILE = "flash_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

# Поддерживаемые чипы
CHIPS = ["auto", "esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6", "esp8266"]

# Размер резервной копии (по умолчанию 4 МБ)
BACKUP_SIZE = 0x400000  # 4MB
BACKUP_FILE = "backup_original.bin"

class ESPFlashTool:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP Flash Tool [GUI]")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        self.setup_ui()
        self.refresh_ports()
        self.log("Инструмент запущен")

    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root, text="ESP Flash Tool", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Фрейм настроек
        frame = ttk.LabelFrame(self.root, text="Настройки", padding=10)
        frame.pack(fill="x", padx=20, pady=5)

        # Чип
        ttk.Label(frame, text="Чип:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.chip_var = tk.StringVar(value="auto")
        chip_combo = ttk.Combobox(frame, textvariable=self.chip_var, values=CHIPS, state="readonly", width=15)
        chip_combo.grid(row=0, column=1, padx=5, pady=5)

        # Порт
        ttk.Label(frame, text="COM-порт:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=3, padx=5, pady=5)
        refresh_btn = ttk.Button(frame, text="Обновить", command=self.refresh_ports)
        refresh_btn.grid(row=0, column=4, padx=5, pady=5)

        # Файл
        ttk.Label(frame, text="Файл прошивки:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.file_var, width=40).grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        file_btn = ttk.Button(frame, text="Выбрать", command=self.select_file)
        file_btn.grid(row=1, column=3, padx=5, pady=5)

        # Скорость
        ttk.Label(frame, text="Скорость (baud):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.baud_var = tk.StringVar(value="115200")
        baud_combo = ttk.Combobox(frame, textvariable=self.baud_var, values=["115200", "921600", "230400", "460800"], width=15)
        baud_combo.grid(row=2, column=1, padx=5, pady=5)

        # Кнопки действий
        btn_frame = ttk.LabelFrame(self.root, text="Действия", padding=10)
        btn_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(btn_frame, text="1. Полная прошивка + резерв", command=self.flash_full_with_backup, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="2. Обновить приложение (0x10000)", command=self.flash_app).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="3. Стереть чип", command=self.erase_chip, bg="#f44336", fg="white").grid(row=0, column=2, padx=5, pady=5)

        # Лог
        log_frame = ttk.LabelFrame(self.root, text="Лог операций", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=12, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Статус
        self.status_var = tk.StringVar(value="Готов")
        status = tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", padx=20, pady=5)

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set("")

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл прошивки (.bin)",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if path:
            self.file_var.set(path)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        logging.info(message)

    def run_esptool(self, args, success_msg, error_msg):
        def target():
            try:
                self.status_var.set("Выполняется...")
                self.log(f"Команда: esptool {' '.join(args)}")
                result = subprocess.run(
                    ["esptool"] + args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                if result.returncode == 0:
                    self.log(success_msg)
                else:
                    error = result.stdout
                    self.log(f"ОШИБКА: {error_msg}")
                    self.log(f"Вывод: {error}")
            except Exception as e:
                self.log(f"ОШИБКА: Не удалось запустить esptool — {e}")
            finally:
                self.status_var.set("Готов")

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def flash_full_with_backup(self):
        port = self.port_var.get()
        chip = self.chip_var.get()
        file_path = self.file_var.get()
        baud = self.baud_var.get()

        if not port:
            messagebox.showerror("Ошибка", "Не выбран COM-порт")
            return
        if not file_path:
            messagebox.showerror("Ошибка", "Не выбран файл прошивки")
            return

        if messagebox.askyesno("Подтверждение", "Сделать резервную копию и прошить?"):
            self.log("=== Резервное копирование и прошивка ===")
            # Сначала резерв
            backup_args = [
                "--chip", chip,
                "--port", port,
                "--baud", baud,
                "read_flash", "0x0", hex(BACKUP_SIZE), BACKUP_FILE
            ]
            self.run_esptool(
                backup_args,
                f"Резервная копия сохранена: {BACKUP_FILE}",
                "Резервное копирование не удалось"
            )

            # Через 1 секунду — прошивка
            self.root.after(1500, lambda: self._flash_after_backup(port, chip, file_path, baud))

    def _flash_after_backup(self, port, chip, file_path, baud):
        flash_args = [
            "--chip", chip,
            "--port", port,
            "--baud", baud,
            "write_flash", "0x0", file_path
        ]
        self.run_esptool(
            flash_args,
            "✅ УСПЕХ: Полная прошивка завершена",
            "❌ ОШИБКА: Полная прошивка не удалась"
        )

    def flash_app(self):
        port = self.port_var.get()
        chip = self.chip_var.get()
        file_path = self.file_var.get()
        baud = self.baud_var.get()

        if not port or not file_path:
            messagebox.showerror("Ошибка", "Проверьте порт и файл")
            return

        if messagebox.askyesno("Подтверждение", "Прошить приложение по адресу 0x10000?"):
            args = [
                "--chip", chip,
                "--port", port,
                "--baud", baud,
                "write_flash", "0x10000", file_path
            ]
            self.run_esptool(
                args,
                "✅ УСПЕХ: Приложение прошито",
                "❌ ОШИБКА: Прошивка не удалась"
            )

    def erase_chip(self):
        port = self.port_var.get()
        chip = self.chip_var.get()
        baud = self.baud_var.get()

        if not port:
            messagebox.showerror("Ошибка", "Не выбран COM-порт")
            return

        if messagebox.askyesno("Подтверждение", "Стереть ВЕСЬ чип? Это удалит все данные!"):
            args = [
                "--chip", chip,
                "--port", port,
                "--baud", baud,
                "erase_flash"
            ]
            self.run_esptool(
                args,
                "✅ УСПЕХ: Чип стёрт",
                "❌ ОШИБКА: Стирание не удалось"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ESPFlashTool(root)
    root.mainloop()