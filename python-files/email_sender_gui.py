import pandas as pd
import smtplib
import time
import logging
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_sender.log'),
        logging.StreamHandler()
    ]
)

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Sender")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Переменные для хранения данных
        self.emails = []
        self.is_sending = False
        self.stop_sending = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка настроек
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.settings_frame, text="Настройки")
        
        # Вкладка рассылки
        self.sending_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.sending_frame, text="Рассылка")
        
        # Заполнение вкладки настроек
        self.create_settings_tab()
        
        # Заполнение вкладки рассылки
        self.create_sending_tab()
        
    def create_settings_tab(self):
        # Поля для SMTP настроек
        ttk.Label(self.settings_frame, text="SMTP сервер:").grid(row=0, column=0, sticky="w", pady=5)
        self.smtp_server = ttk.Entry(self.settings_frame, width=40)
        self.smtp_server.grid(row=0, column=1, pady=5, padx=5)
        self.smtp_server.insert(0, "smtp.gmail.com")
        
        ttk.Label(self.settings_frame, text="Порт:").grid(row=1, column=0, sticky="w", pady=5)
        self.smtp_port = ttk.Entry(self.settings_frame, width=40)
        self.smtp_port.grid(row=1, column=1, pady=5, padx=5)
        self.smtp_port.insert(0, "587")
        
        ttk.Label(self.settings_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=5)
        self.email = ttk.Entry(self.settings_frame, width=40)
        self.email.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(self.settings_frame, text="Пароль:").grid(row=3, column=0, sticky="w", pady=5)
        self.password = ttk.Entry(self.settings_frame, width=40, show="*")
        self.password.grid(row=3, column=1, pady=5, padx=5)
        
        # Поля для содержимого письма
        ttk.Label(self.settings_frame, text="Тема письма:").grid(row=4, column=0, sticky="w", pady=5)
        self.subject = ttk.Entry(self.settings_frame, width=40)
        self.subject.grid(row=4, column=1, pady=5, padx=5)
        self.subject.insert(0, "Важное сообщение")
        
        ttk.Label(self.settings_frame, text="Текст письма:").grid(row=5, column=0, sticky="w", pady=5)
        self.body = ScrolledText(self.settings_frame, width=50, height=10)
        self.body.grid(row=5, column=1, pady=5, padx=5)
        self.body.insert("1.0", "Здравствуйте!\n\nЭто тестовое письмо.\n\nС уважением,\nВаша компания")
        
        # Кнопка для выбора файла с email
        ttk.Label(self.settings_frame, text="Файл с email:").grid(row=6, column=0, sticky="w", pady=5)
        self.file_path = ttk.Entry(self.settings_frame, width=30)
        self.file_path.grid(row=6, column=1, pady=5, padx=5, sticky="ew")
        
        self.browse_btn = ttk.Button(self.settings_frame, text="Обзор", command=self.browse_file)
        self.browse_btn.grid(row=6, column=2, pady=5, padx=5)
        
        # Поле для задержки
        ttk.Label(self.settings_frame, text="Задержка (секунды):").grid(row=7, column=0, sticky="w", pady=5)
        self.delay = ttk.Entry(self.settings_frame, width=40)
        self.delay.grid(row=7, column=1, pady=5, padx=5)
        self.delay.insert(0, "60")
        
        # Кнопка для проверки соединения
        self.test_btn = ttk.Button(self.settings_frame, text="Проверить соединение", command=self.test_connection)
        self.test_btn.grid(row=8, column=1, pady=10)
        
    def create_sending_tab(self):
        # Поле для отображения логов
        ttk.Label(self.sending_frame, text="Лог отправки:").grid(row=0, column=0, sticky="w", pady=5)
        self.log_text = ScrolledText(self.sending_frame, width=80, height=20)
        self.log_text.grid(row=1, column=0, columnspan=3, pady=5, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(self.sending_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Кнопки управления рассылкой
        self.start_btn = ttk.Button(self.sending_frame, text="Начать рассылку", command=self.start_sending)
        self.start_btn.grid(row=3, column=0, pady=10, padx=5)
        
        self.stop_btn = ttk.Button(self.sending_frame, text="Остановить", command=self.stop_sending, state=tk.DISABLED)
        self.stop_btn.grid(row=3, column=1, pady=10, padx=5)
        
        self.clear_btn = ttk.Button(self.sending_frame, text="Очистить лог", command=self.clear_log)
        self.clear_btn.grid(row=3, column=2, pady=10, padx=5)
        
        # Настройка расширяемости
        self.sending_frame.columnconfigure(0, weight=1)
        self.sending_frame.rowconfigure(1, weight=1)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с email адресами",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, filename)
            
    def test_connection(self):
        # Проверка соединения с SMTP сервером
        try:
            server = smtplib.SMTP(self.smtp_server.get(), int(self.smtp_port.get()))
            server.starttls()
            server.login(self.email.get(), self.password.get())
            server.quit()
            messagebox.showinfo("Успех", "Соединение с SMTP сервером установлено успешно!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к SMTP серверу: {str(e)}")
            
    def log_message(self, message):
        # Добавление сообщения в лог
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def clear_log(self):
        # Очистка лога
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def read_emails_from_excel(self):
        # Чтение email адресов из Excel файла
        try:
            file_path = self.file_path.get()
            if not file_path:
                messagebox.showerror("Ошибка", "Выберите файл с email адресами")
                return []
                
            df = pd.read_excel(file_path)
            # Попробуем найти колонку с email
            email_columns = [col for col in df.columns if 'email' in col.lower()]
            if not email_columns:
                messagebox.showerror("Ошибка", "Не найдена колонка с email адресами в файле")
                return []
                
            emails = df[email_columns[0]].dropna().tolist()
            self.log_message(f"Прочитано {len(emails)} email адресов из файла")
            return emails
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка чтения файла: {str(e)}")
            return []
            
    def send_email(self, to_email, subject, body):
        # Отправка одного email
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email.get()
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server.get(), int(self.smtp_port.get()))
            server.starttls()
            server.login(self.email.get(), self.password.get())
            server.sendmail(self.email.get(), to_email, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            self.log_message(f"Ошибка отправки письма {to_email}: {str(e)}")
            return False
            
    def start_sending(self):
        # Начало рассылки в отдельном потоке
        if self.is_sending:
            return
            
        # Получение email адресов
        self.emails = self.read_emails_from_excel()
        if not self.emails:
            return
            
        # Проверка заполненности полей
        if not all([self.smtp_server.get(), self.smtp_port.get(), self.email.get(), self.password.get()]):
            messagebox.showerror("Ошибка", "Заполните все поля SMTP настроек")
            return
            
        # Изменение состояния кнопок
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_sending = True
        self.stop_sending = False
        
        # Настройка прогрессбара
        self.progress['maximum'] = len(self.emails)
        self.progress['value'] = 0
        
        # Запуск рассылки в отдельном потоке
        thread = threading.Thread(target=self.sending_thread)
        thread.daemon = True
        thread.start()
        
    def stop_sending(self):
        # Остановка рассылки
        self.stop_sending = True
        self.log_message("Рассылка остановлена пользователем")
        
    def sending_thread(self):
        # Поток для отправки писем
        subject = self.subject.get()
        body = self.body.get("1.0", tk.END)
        delay = int(self.delay.get())
        sent_count = 0
        
        for i, email in enumerate(self.emails):
            if self.stop_sending:
                break
                
            # Отправка письма
            success = self.send_email(email, subject, body)
            if success:
                sent_count += 1
                self.log_message(f"Письмо отправлено: {email}")
            else:
                self.log_message(f"Ошибка отправки: {email}")
                
            # Обновление прогрессбара
            self.progress['value'] = i + 1
            self.root.update_idletasks()
            
            # Пауза между письмами (кроме последнего)
            if i < len(self.emails) - 1 and not self.stop_sending:
                for sec in range(delay, 0, -1):
                    if self.stop_sending:
                        break
                    self.log_message(f"Следующее письмо через {sec} сек...")
                    time.sleep(1)
                    
        # Завершение рассылки
        self.is_sending = False
        self.log_message(f"Рассылка завершена! Отправлено: {sent_count}/{len(self.emails)}")
        
        # Восстановление состояния кнопок
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Показать результаты
        messagebox.showinfo("Завершено", f"Рассылка завершена!\nОтправлено: {sent_count}/{len(self.emails)}")

def main():
    # Создание и запуск приложения
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()