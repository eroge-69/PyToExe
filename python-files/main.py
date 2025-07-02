import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import serial.tools.list_ports
import serial
import threading
import platform
import re
import os
import pandas as pd
from datetime import datetime


class LabelPrinterApp:
    def __init__(self, master):
        self.master = master
        master.title("Генератор этикеток для TSC TDP-200")

        # Элементы интерфейса
        self.label = tk.Label(master, text="Выберите Excel файл с данными пациентов")
        self.label.pack(pady=10)

        self.load_btn = tk.Button(master, text="Загрузить Excel", command=self.load_excel)
        self.load_btn.pack(pady=5)

        # Поле выбора принтера
        self.printer_frame = tk.Frame(master)
        self.printer_frame.pack(pady=5)

        self.printer_label = tk.Label(self.printer_frame, text="Принтер:")
        self.printer_label.pack(side=tk.LEFT)

        self.printer_combo = ttk.Combobox(self.printer_frame, width=40)
        self.printer_combo.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = tk.Button(self.printer_frame, text="Обновить", command=self.refresh_printers)
        self.refresh_btn.pack(side=tk.LEFT)

        self.print_btn = tk.Button(master, text="Напечатать", command=self.print_labels)
        self.print_btn.pack(pady=5)
        self.print_btn.config(state=tk.DISABLED)

        self.save_btn = tk.Button(master, text="Сохранить команды", command=self.save_commands)
        self.save_btn.pack(pady=5)
        self.save_btn.config(state=tk.DISABLED)

        self.status = tk.Label(master, text="Статус: Ожидание загрузки файла")
        self.status.pack(pady=10)

        self.excel_path = ""
        self.patient_data = []
        self.tspl_commands = ""

        # Поиск принтеров при запуске
        self.refresh_printers()

    def refresh_printers(self):
        """Обновление списка доступных принтеров"""
        self.printer_combo['values'] = self.find_tsc_printers()
        if self.printer_combo['values']:
            self.printer_combo.current(0)

    def find_tsc_printers(self):
        """Поиск принтеров TSC по различным критериям"""
        tsc_printers = []
        ports = serial.tools.list_ports.comports()

        # Идентификаторы TSC принтеров (VID/PID)
        tsc_ids = [
            (0x0483, 0x070B),  # TSC TDP-200
            (0x0483, 0x5710),  # Другие модели TSC
            (0x0483, 0x5720),
            (0x0483, 0x5740),
            (0x0483, 0xA348),
            (0x0483, 0xA349)
        ]

        # Паттерны для определения TSC принтеров по описанию
        tsc_patterns = [
            r"tsc",
            r"tdp[-_\s]?200",
            r"thermal\s+printer",
            r"label\s+printer",
            r"printer\s+\(tsc\)",
            r"serial printer"
        ]

        for port in ports:
            # Поиск по VID/PID
            if (port.vid, port.pid) in tsc_ids:
                desc = f"{port.device} - {port.description}" if port.description else port.device
                tsc_printers.append(desc)
                continue

            # Поиск по описанию (для macOS/Linux)
            if port.description:
                description = port.description.lower()
                for pattern in tsc_patterns:
                    if re.search(pattern, description):
                        desc = f"{port.device} - {port.description}"
                        tsc_printers.append(desc)
                        break

        # Добавляем ручной выбор порта
        tsc_printers.append("Указать вручную...")
        return tsc_printers

    def get_port_name(self, selection):
        """Извлечение имени порта из выбранного значения"""
        if selection == "Указать вручную...":
            return self.manual_port_selection()

        # Извлекаем имя порта из строки (формат: "COM3 - TSC TDP-200")
        if " - " in selection:
            return selection.split(" - ")[0].strip()
        return selection

    def manual_port_selection(self):
        """Ручной выбор порта через диалоговое окно"""
        port = filedialog.askstring(
            "Выбор порта",
            "Введите имя последовательного порта:",
            parent=self.master
        )
        if port:
            # Нормализация пути для macOS/Linux
            if platform.system() != "Windows" and not port.startswith("/dev/"):
                return f"/dev/{port}"
        return port

    def load_excel(self):
        """Загрузка Excel файла"""
        self.excel_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not self.excel_path:
            return

        self.status.config(text=f"Загружен: {os.path.basename(self.excel_path)}")

        try:
            # Читаем Excel файл
            df = pd.read_excel(self.excel_path)

            # Проверяем наличие необходимых колонок
            required_columns = ['ФИО пациента', 'IDS', 'Дата регистрации', 'Номер карты', 'Тип материала']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Ошибка", f"В файле отсутствует колонка: {col}")
                    return

            # Обрабатываем каждую строку
            self.patient_data = []
            for _, row in df.iterrows():
                # Форматируем дату: оставляем только дату (без времени)
                reg_date = row['Дата регистрации']
                if pd.notnull(reg_date):
                    if isinstance(reg_date, str):
                        reg_date = reg_date.split()[0]  # берем только дату
                    else:
                        reg_date = reg_date.strftime("%d.%m.%Y")

                # Номер карты: если пустой, то ставим "-"
                card_num = row['Номер карты']
                if pd.isnull(card_num):
                    card_num = "-"
                else:
                    # Преобразуем в целое, затем в строку, если это число
                    try:
                        card_num = str(int(card_num))
                    except:
                        card_num = str(card_num)

                patient = {
                    "name": row['ФИО пациента'],
                    "id": str(row['IDS']),
                    "reg_date": reg_date if pd.notnull(reg_date) else "-",
                    "card_num": card_num,
                    "material": row['Тип материала']
                }
                self.patient_data.append(patient)

            # Генерируем команды
            self.tspl_commands = self.create_tspl_commands()
            self.print_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.NORMAL)
            self.status.config(text=f"Загружено записей: {len(self.patient_data)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла:\n{str(e)}")
            self.status.config(text="Ошибка загрузки")

    def print_labels(self):
        """Печать этикеток через отдельный поток"""
        selection = self.printer_combo.get()
        if not selection:
            messagebox.showerror("Ошибка", "Принтер не выбран!")
            return

        port_name = self.get_port_name(selection)
        if not port_name:
            return

        # Запускаем печать в отдельном потоке
        threading.Thread(
            target=self.send_to_printer,
            args=(port_name, self.tspl_commands),
            daemon=True
        ).start()

    def save_commands(self):
        """Сохранение команд в текстовый файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.tspl_commands)
            messagebox.showinfo("Успех", f"Команды сохранены в файл:\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def create_tspl_commands(self):
        """Формирование TSPL кода с новыми полями"""
        header = [
            "SIZE 30 mm, 20 mm",
            "GAP 2 mm, 0",
            "CLS",
            "CODEPAGE UTF-8"
        ]

        body = []
        for patient in self.patient_data:
            body.append("CLS")
            # Выводим каждое поле с новой строки
            body.append(f'TEXT 20,20,"0",0,1,1,"{patient["name"]}"')
            body.append(f'TEXT 20,50,"0",0,1,1,"{patient["id"]}"')
            body.append(f'TEXT 20,80,"0",0,1,1,"{patient["reg_date"]}"')
            body.append(f'TEXT 20,110,"0",0,1,1,"{patient["card_num"]}"')
            body.append(f'TEXT 20,140,"0",0,1,1,"{patient["material"]}"')
            body.append("PRINT 1")

        return "\r\n".join(header + body) + "\r\n"

    def send_to_printer(self, port_name, commands):
        """Отправка команд на принтер"""
        try:
            self.status.config(text="Печать...")

            # Настройки порта для разных ОС
            baudrate = 115200
            timeout = 2 if platform.system() == "Windows" else 5

            with serial.Serial(
                    port=port_name,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=timeout
            ) as printer:
                printer.write(commands.encode('utf-8'))
                printer.flush()
                # Ожидаем завершения печати
                printer.read(1024)

            self.status.config(text="Готово к печати")
            messagebox.showinfo("Успех", "Этикетки отправлены на печать")

        except Exception as e:
            self.status.config(text="Ошибка подключения")
            messagebox.showerror("Ошибка", f"Не удалось подключиться к принтеру:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelPrinterApp(root)
    root.geometry("600x250")
    root.mainloop()