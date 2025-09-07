import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import threading
import time
from datetime import datetime
import re
import json

class AutoOrderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоперезаказ справок и накладных")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Центрирование окна
        self.center_window()
        
        # Переменные для хранения данных
        self.utm_address = tk.StringVar()
        self.fsrar_id = tk.StringVar()
        self.email = tk.StringVar()
        self.selected_window = tk.StringVar(value="spravki")
        
        # Загрузка сохраненных настроек
        self.load_settings()
        
        # Создание интерфейса
        self.create_widgets()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.utm_address.set(settings.get("utm_address", ""))
                    self.fsrar_id.set(settings.get("fsrar_id", ""))
                    self.email.set(settings.get("email", ""))
        except:
            pass
            
    def save_settings(self):
        settings = {
            "utm_address": self.utm_address.get(),
            "fsrar_id": self.fsrar_id.get(),
            "email": self.email.get()
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        
    def create_widgets(self):
        # Стиль
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 10))
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Автоперезаказ документов", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Выбор типа документа
        doc_type_frame = ttk.LabelFrame(main_frame, text="Тип документа", padding="10")
        doc_type_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        ttk.Radiobutton(doc_type_frame, text="Перезапрос справок Б", 
                       variable=self.selected_window, value="spravki").pack(anchor="w")
        ttk.Radiobutton(doc_type_frame, text="Перезапрос накладных", 
                       variable=self.selected_window, value="nakladnie").pack(anchor="w")
        
        # Поля ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        ttk.Label(input_frame, text="Адрес работы УТМ:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.utm_address, width=40).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(input_frame, text="FSRAR ID:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.fsrar_id, width=40).grid(row=1, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(input_frame, text="Email для результатов:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.email, width=40).grid(row=2, column=1, padx=(10, 0), pady=5)
        
        # Кнопка выбора файла
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        ttk.Label(file_frame, text="Файл с данными:").pack(side="left")
        self.file_path_label = ttk.Label(file_frame, text="Файл не выбран", foreground="gray")
        self.file_path_label.pack(side="left", padx=(10, 0))
        ttk.Button(file_frame, text="Выбрать файл", command=self.select_file).pack(side="right")
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 15))
        
        ttk.Button(button_frame, text="Запустить перезаказ", command=self.start_processing).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Сохранить настройки", command=self.save_settings).pack(side="left")
        
        # Лог выполнения
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Делаем лог растягиваемым
        main_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Переменные для обработки
        self.selected_file_path = ""
        self.is_processing = False
        
    def select_file(self):
        file_types = [("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.config(text=os.path.basename(file_path))
            self.log_message(f"Выбран файл: {file_path}")
    
    def validate_inputs(self):
        if not self.utm_address.get():
            messagebox.showerror("Ошибка", "Введите адрес работы УТМ")
            return False
            
        if not self.fsrar_id.get():
            messagebox.showerror("Ошибка", "Введите FSRAR ID")
            return False
            
        if not self.email.get() or "@" not in self.email.get():
            messagebox.showerror("Ошибка", "Введите корректный email")
            return False
            
        if not self.selected_file_path:
            messagebox.showerror("Ошибка", "Выберите файл с данными")
            return False
            
        return True
    
    def start_processing(self):
        if not self.validate_inputs():
            return
            
        if self.is_processing:
            messagebox.showwarning("Внимание", "Процесс уже выполняется")
            return
            
        self.is_processing = True
        self.status_var.set("Обработка...")
        
        # Сохраняем настройки
        self.save_settings()
        
        # Запуск в отдельном потоке, чтобы не блокировать интерфейс
        thread = threading.Thread(target=self.process_data)
        thread.daemon = True
        thread.start()
    
    def process_data(self):
        try:
            # Создаем папку для сохранения результатов
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_folder = os.path.join(os.getcwd(), "Done", timestamp)
            os.makedirs(result_folder, exist_ok=True)
            
            # Читаем данные из файла
            with open(self.selected_file_path, 'r', encoding='utf-8') as file:
                data_lines = file.readlines()
            
            valid_data = []
            invalid_data = []
            
            # Проверяем данные в зависимости от выбранного типа
            doc_type = self.selected_window.get()
            if doc_type == "spravki":
                pattern = r'^FB-\d{15}$'
                doc_name = "справок Б"
            else:
                pattern = r'^TTN-\d{10}$'
                doc_name = "накладных"
            
            for line in data_lines:
                line = line.strip()
                if re.match(pattern, line):
                    valid_data.append(line)
                else:
                    invalid_data.append(line)
            
            # Сохраняем валидные данные в файл в папке Done
            result_file = os.path.join(result_folder, "valid_data.txt")
            with open(result_file, 'w', encoding='utf-8') as file:
                for item in valid_data:
                    file.write(f"{item}\n")
            
            # Логируем процесс
            self.log_message(f"Найдено валидных записей: {len(valid_data)}")
            self.log_message(f"Найдено невалидных записей: {len(invalid_data)}")
            
            if invalid_data:
                self.log_message("Невалидные записи:")
                for item in invalid_data:
                    self.log_message(f"  {item}")
            
            # Имитация процесса перезаказа
            self.log_message("Начинается процесс перезаказа...")
            
            for i, item in enumerate(valid_data):
                # Имитация задержки обработки
                time.sleep(0.2)
                self.log_message(f"Обрабатывается {item} ({i+1}/{len(valid_data)})")
                
                # Здесь будет реальный код для перезаказа через УТМ
                # В реальном приложении здесь должен быть код взаимодействия с API УТМ
            
            self.log_message("Обработка завершена!")
            
            # Сохраняем полный отчет
            report_file = os.path.join(result_folder, "report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"Отчет о перезаказе {doc_name}\n")
                f.write(f"Время обработки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Адрес УТМ: {self.utm_address.get()}\n")
                f.write(f"FSRAR ID: {self.fsrar_id.get()}\n")
                f.write(f"Успешно обработано: {len(valid_data)}\n")
                f.write(f"Невалидных записей: {len(invalid_data)}\n\n")
                
                if invalid_data:
                    f.write("Невалидные записи:\n")
                    for item in invalid_data:
                        f.write(f"{item}\n")
            
            # Отправка email с результатами
            self.send_email(report_file, result_file, len(valid_data), len(invalid_data), doc_name)
            
            self.status_var.set("Обработка завершена")
            self.log_message(f"Результаты сохранены в папку: {result_folder}")
            
        except Exception as e:
            self.log_message(f"Ошибка при обработке: {str(e)}")
            self.status_var.set("Ошибка обработки")
        finally:
            self.is_processing = False
    
    def send_email(self, report_file, result_file, valid_count, invalid_count, doc_name):
        try:
            self.log_message("Подготовка к отправке email...")
            
            # В реальном приложении здесь нужно указать настройки SMTP сервера
            # Это пример для Gmail, для других почтовых сервисов настройки будут другими
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_username = "your_email@gmail.com"  # Замените на вашу почту
            smtp_password = "your_app_password"     # Замените на ваш пароль приложения
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = self.email.get()
            msg['Subject'] = f"Результаты автоматического перезаказа {doc_name}"
            
            # Текст сообщения
            body = f"""
            Результаты автоматического перезаказа {doc_name}:
            
            Адрес УТМ: {self.utm_address.get()}
            FSRAR ID: {self.fsrar_id.get()}
            Время обработки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Успешно обработано: {valid_count}
            Невалидных записей: {invalid_count}
            
            Подробный отчет и валидные данные находятся в прикрепленных файлах.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Прикрепляем файл с отчетом
            with open(report_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(report_file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file)}"'
                msg.attach(part)
                
            # Прикрепляем файл с результатами
            with open(result_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(result_file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(result_file)}"'
                msg.attach(part)
            
            # Отправляем сообщение
            self.log_message("Отправка email...")
            
            # В реальном приложении раскомментируйте этот код и настройте под ваш SMTP-сервер:
            """
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            """
            
            # Вместо реальной отправки просто выводим сообщение
            self.log_message(f"Email успешно отправлен на {self.email.get()}")
            self.log_message("(В демо-режиме отправка не выполняется)")
            
        except Exception as e:
            self.log_message(f"Ошибка при отправке email: {str(e)}")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Добавляем сообщение в лог (выполняем в основном потоке)
        self.root.after(0, lambda: self.log_text.insert(tk.END, formatted_message))
        self.root.after(0, lambda: self.log_text.see(tk.END))

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoOrderApp(root)
    root.mainloop()