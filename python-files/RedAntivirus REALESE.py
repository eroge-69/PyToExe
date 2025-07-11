import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import time
import threading
import os
import subprocess

class KasperskyAntivirus:
    def __init__(self, root):
        self.root = root
        self.root.title("RedAntiVirus Release")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        
        # Состояние подписки
        self.subscription_active = False
        self.scan_active = False
        
        # Создаем vana.bat при запуске (если его нет)
        self.create_bat_file()
        
        # Стиль для виджетов
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#1a1a2e')
        self.style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('Red.TButton', foreground='white', background='#e94560')
        self.style.configure('Green.TButton', foreground='white', background='#2dcc70')
        self.style.configure('Blue.TButton', foreground='white', background='#0078d7')
        self.style.configure('Gold.TButton', foreground='black', background='#FFD700')
        self.style.configure('TProgressbar', thickness=20, troughcolor='#16213e', background='#0078d7')
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        
        # Создание интерфейса
        self.create_ui()
        
    def create_bat_file(self):
        """Создает vana.bat с фиксированным содержимым, если его нет"""
        if not os.path.exists("vana.bat"):
            bat_content = """@echo off
echo ====================================
echo Red Antivirus - Virus Removal
echo ====================================
echo.
echo Scanning system...
echo Detected threats: 349
echo.
echo Removing malware...
echo Cleaning registry...
echo Deleting infected files...
echo.
echo Successfully removed all threats!
echo.
pause
"""
            with open("vana.bat", "w") as f:
                f.write(bat_content)
    
    def create_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопка активации подписки
        self.subscription_button = ttk.Button(
            main_frame, 
            text="Активировать подписку", 
            style='Gold.TButton', 
            command=self.activate_subscription
        )
        self.subscription_button.pack(fill=tk.X, pady=(0, 10))
        
        # Статус подписки
        self.subscription_status = ttk.Label(
            main_frame, 
            text="Подписка не активирована", 
            foreground="red",
            font=('Helvetica', 10, 'bold')
        )
        self.subscription_status.pack(fill=tk.X, pady=(0, 10))
        
        # Логотип и заголовок
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Создаем логотип с помощью Pillow (только зеленый)
        logo_img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo_img)
        draw.ellipse((10, 10, 90, 90), fill='#2dcc70')
        draw.ellipse((25, 25, 75, 75), fill='#1a1a2e')
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        
        self.logo_label = ttk.Label(logo_frame, image=self.logo_photo)
        self.logo_label.pack(side=tk.LEFT, padx=(0, 20))
        
        title_label = ttk.Label(logo_frame, text="RedAntivirus - Твой выбор!", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Статус защиты
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.protection_status = ttk.Label(status_frame, text="Защита включена", foreground="#2dcc70", font=('Helvetica', 12, 'bold'))
        self.protection_status.pack(side=tk.LEFT)
        
        self.protection_icon = ttk.Label(status_frame, text="✓", foreground="#2dcc70", font=('Helvetica', 12, 'bold'))
        self.protection_icon.pack(side=tk.LEFT, padx=5)
        
        # Кнопки действий
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.scan_button = ttk.Button(
            buttons_frame, 
            text="Быстрая проверка", 
            style='Blue.TButton', 
            command=lambda: self.start_scan("quick"),
            state=tk.DISABLED
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.full_scan_button = ttk.Button(
            buttons_frame, 
            text="Полная проверка", 
            style='Blue.TButton', 
            command=lambda: self.start_scan("full"),
            state=tk.DISABLED
        )
        self.full_scan_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(
            buttons_frame, 
            text="Обновить базы", 
            style='Green.TButton', 
            command=self.update_databases,
            state=tk.DISABLED
        )
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.settings_button = ttk.Button(
            buttons_frame, 
            text="Настройки", 
            style='TButton', 
            command=self.open_settings
        )
        self.settings_button.pack(side=tk.RIGHT, padx=5)
        
        # Прогресс сканирования
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Активируйте подписку для проверки")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        self.scan_details = ttk.Label(self.progress_frame, text="")
        self.scan_details.pack()
        
        # Кнопка удаления вирусов
        self.remove_viruses_button = ttk.Button(
            self.progress_frame, 
            text="Удалить вирусы", 
            style='Red.TButton', 
            command=self.remove_viruses,
            state=tk.DISABLED
        )
        self.remove_viruses_button.pack(pady=(10, 0))
        
        # Лог событий
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_label = ttk.Label(log_frame, text="Последние события:", font=('Helvetica', 10, 'bold'))
        log_label.pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, height=10, bg='#16213e', fg='white', insertbackground='white', 
                               selectbackground='#0078d7', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Начальные сообщения в лог
        self.add_to_log("Антивирус Red запущен")
        self.add_to_log("Активируйте подписку для полного доступа")
    
    def activate_subscription(self):
        """Активация подписки"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Активация подписки")
        dialog.geometry("400x200")
        dialog.configure(bg='#1a1a2e')
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Введите 12-значный код подписки:").pack(pady=(10, 5))
        
        self.code_entry = ttk.Entry(dialog, font=('Helvetica', 12))
        self.code_entry.pack(fill=tk.X, padx=20, pady=5)
        
        def validate_code():
            code = self.code_entry.get().replace("-", "").replace(" ", "")
            if len(code) == 12 and code.isdigit():
                self.subscription_active = True
                self.subscription_status.config(text="Подписка активна до 31.12.2099", foreground="green")
                self.subscription_button.config(state=tk.DISABLED)
                self.scan_button.config(state=tk.NORMAL)
                self.full_scan_button.config(state=tk.NORMAL)
                self.update_button.config(state=tk.NORMAL)
                self.progress_label.config(text="Готов к проверке")
                self.add_to_log("Подписка успешно активирована")
                dialog.destroy()
                messagebox.showinfo("Успех", "Подписка успешно активирована!")
            else:
                messagebox.showerror("Ошибка", "Неверный код подписки! Попробуйте снова.")
        
        ttk.Button(
            dialog, 
            text="Активировать", 
            style='Green.TButton', 
            command=validate_code
        ).pack(pady=10)
        
        ttk.Button(
            dialog, 
            text="Отмена", 
            style='Red.TButton', 
            command=dialog.destroy
        ).pack(pady=5)
    
    def start_scan(self, scan_type):
        """Запуск проверки"""
        if not self.subscription_active:
            messagebox.showwarning("Ошибка", "Активируйте подписку для использования этой функции!")
            return
            
        if self.scan_active:
            messagebox.showwarning("Внимание", "Проверка уже выполняется!")
            return
            
        self.scan_active = True
        self.remove_viruses_button.config(state=tk.DISABLED)
        
        if scan_type == "quick":
            self.progress_label.config(text="Выполняется быстрая проверка...")
            self.add_to_log("Запущена быстрая проверка системы")
            max_time = 0.05
            steps = 100
        else:
            self.progress_label.config(text="Выполняется полная проверка системы...")
            self.add_to_log("Запущена полная проверка системы")
            max_time = 0.1
            steps = 200
        
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = steps
        
        def scan_thread():
            for i in range(1, steps + 1):
                if not self.scan_active:
                    break
                    
                time.sleep(max_time * random.uniform(0.8, 1.2))
                self.progress_bar['value'] = i
                
                if i % 10 == 0:
                    if scan_type == "quick":
                        details = [
                            f"Проверено файлов: {random.randint(100, 500)}",
                            f"Проверка процессов: {random.randint(5, 15)}/{random.randint(15, 25)}",
                            "Сканирование памяти...",
                            "Проверка автозагрузки...",
                            "Анализ системных файлов..."
                        ]
                    else:
                        details = [
                            f"Проверено файлов: {random.randint(1000, 5000)}",
                            "Проверка реестра...",
                            "Сканирование загрузочных секторов...",
                            "Анализ сетевых подключений...",
                            "Проверка документов...",
                            "Сканирование временных файлов..."
                        ]
                    self.scan_details.config(text=random.choice(details))
                
                if i % 5 == 0:
                    self.root.update()
            
            if self.scan_active:
                self.scan_complete()
        
            self.scan_active = False
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def scan_complete(self):
        """Действия после завершения сканирования"""
        threats = 349
        self.progress_label.config(text=f"Проверка завершена. Обнаружено угроз: {threats}")
        self.add_to_log(f"Проверка завершена. Обнаружено угроз: {threats}")
        self.remove_viruses_button.config(state=tk.NORMAL)
        
        messagebox.showwarning("Обнаружены угрозы", 
                             f"Обнаружено {threats} угроз(ы). Нажмите кнопку 'Удалить вирусы' для очистки системы.")
    
    def remove_viruses(self):
        """Удаление вирусов"""
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все обнаруженные вирусы?"):
            return
            
        self.scan_active = True
        self.remove_viruses_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Удаление вирусов...")
        self.progress_bar['value'] = 0
        self.add_to_log("Запущено удаление вирусов")
        
        def remove_thread():
            for i in range(1, 101):
                if not self.scan_active:
                    break
                    
                time.sleep(0.05 * random.uniform(0.8, 1.2))
                self.progress_bar['value'] = i
                
                if i % 10 == 0:
                    self.scan_details.config(text=f"Удалено {i}% вирусов...")
                    self.root.update()
            
            if self.scan_active:
                try:
                    subprocess.Popen(["vana.bat"], shell=True)
                    
                    self.progress_label.config(text="Вирусы успешно удалены!")
                    self.scan_details.config(text="Система очищена от угроз")
                    self.add_to_log("Все вирусы успешно удалены")
                    messagebox.showinfo("Удаление завершено", "Все вирусы успешно удалены из системы.")
                except Exception as e:
                    self.add_to_log(f"Ошибка при удалении вирусов: {str(e)}")
                    messagebox.showerror("Ошибка", f"Не удалось выполнить удаление: {str(e)}")
            
            self.scan_active = False
        
        threading.Thread(target=remove_thread, daemon=True).start()
    
    def update_databases(self):
        """Обновление антивирусных баз"""
        if not self.subscription_active:
            messagebox.showwarning("Ошибка", "Активируйте подписку для использования этой функции!")
            return
            
        if self.scan_active:
            messagebox.showwarning("Внимание", "Дождитесь завершения текущей операции!")
            return
            
        self.scan_active = True
        self.progress_label.config(text="Обновление антивирусных баз...")
        self.progress_bar['value'] = 0
        self.add_to_log("Запущено обновление антивирусных баз")
        self.remove_viruses_button.config(state=tk.DISABLED)
        
        def update_thread():
            for i in range(1, 101):
                if not self.scan_active:
                    break
                    
                time.sleep(0.03 * random.uniform(0.8, 1.2))
                self.progress_bar['value'] = i
                
                if i % 10 == 0:
                    self.scan_details.config(text=f"Загружено {i}%...")
                    self.root.update()
            
            if self.scan_active:
                self.progress_label.config(text="Базы данных успешно обновлены")
                self.scan_details.config(text="Базы актуальны")
                self.add_to_log("Антивирусные базы успешно обновлены")
                messagebox.showinfo("Обновление завершено", "Антивирусные базы данных успешно обновлены.")
            
            self.scan_active = False
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def open_settings(self):
        """Окно настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки RedAntivirus")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#1a1a2e')
        
        tab_control = ttk.Notebook(settings_window)
        
        # Вкладка защиты
        protection_tab = ttk.Frame(tab_control)
        tab_control.add(protection_tab, text='Защита')
        
        ttk.Label(protection_tab, text="Защита в реальном времени:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Checkbutton(protection_tab, text="Включить файловый антивирус").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Checkbutton(protection_tab, text="Включить мониторинг поведения").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Checkbutton(protection_tab, text="Включить защиту почты").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Checkbutton(protection_tab, text="Включить защиту интернета").pack(anchor=tk.W, padx=20, pady=2)
        
        # Вкладка проверки с "особой" настройкой
        scan_tab = ttk.Frame(tab_control)
        tab_control.add(scan_tab, text='Проверка')
        
        ttk.Label(scan_tab, text="Настройки проверки:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Checkbutton(scan_tab, text="Проверять архивы").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Checkbutton(scan_tab, text="Проверять по маске").pack(anchor=tk.W, padx=20, pady=2)
        
        # Неотключаемая настройка
        self.download_viruses_var = tk.BooleanVar(value=True)
        download_cb = ttk.Checkbutton(
            scan_tab, 
            text="Скачивать вирусы для анализа", 
            variable=self.download_viruses_var,
            state='disabled'  # Нельзя отключить
        )
        download_cb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Вкладка дополнительно
        advanced_tab = ttk.Frame(tab_control)
        tab_control.add(advanced_tab, text='Дополнительно')
        
        ttk.Label(advanced_tab, text="Дополнительные настройки:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Checkbutton(advanced_tab, text="Создавать отчет").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Checkbutton(advanced_tab, text="Уведомлять о событиях").pack(anchor=tk.W, padx=20, pady=2)
        
        tab_control.pack(expand=1, fill='both')
        
        buttons_frame = ttk.Frame(settings_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="OK", style='Green.TButton', command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", style='Red.TButton', command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Применить", style='Blue.TButton').pack(side=tk.RIGHT, padx=5)
    
    def add_to_log(self, message):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = KasperskyAntivirus(root)
    root.mainloop()