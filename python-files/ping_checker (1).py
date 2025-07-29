import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import platform
import re

class PingChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Перевірка IP-адрес через Ping")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Створення основного фрейму
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Перевірка доступності IP-адреси", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Поле для введення IP-адреси
        ttk.Label(main_frame, text="IP-адреса:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.ip_entry = ttk.Entry(main_frame, width=20, font=('Arial', 11))
        self.ip_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.ip_entry.bind('<Return>', lambda event: self.ping_address())
        
        # Встановлюємо початкове значення
        self.ip_entry.insert(0, "10.0.23.")
        # Встановлюємо курсор в кінець
        self.ip_entry.icursor(tk.END)
        
        # Кнопка Ping
        self.ping_button = ttk.Button(main_frame, text="Ping", command=self.ping_address)
        self.ping_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Прогрес-бар (спочатку прихований)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.progress.grid_remove()  # Приховуємо спочатку
        
        # Налаштування розміру колонок
        main_frame.columnconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Фокус на поле введення
        self.ip_entry.focus()
    
    def is_valid_ip(self, ip):
        """Перевіряє чи є введена адреса валідною IP-адресою або доменним ім'ям"""
        # Перевірка IP-адреси
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ip_pattern, ip):
            return True
        
        # Перевірка домену (спрощена)
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]?(?:\.[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]?)*$'
        if re.match(domain_pattern, ip) and '.' in ip:
            return True
        
        return False
    
    def ping_address(self):
        """Виконує ping команду для введеної адреси"""
        ip_address = self.ip_entry.get().strip()
        
        if not ip_address:
            messagebox.showwarning("Попередження", "Будь ласка, введіть IP-адресу або домен")
            return
        
        if not self.is_valid_ip(ip_address):
            messagebox.showerror("Помилка", "Введена адреса не є валідною IP-адресою або доменом")
            return
        
        # Запускаємо ping в окремому потоці, щоб не блокувати GUI
        self.ping_button.config(state='disabled', text='Перевіряю...')
        self.progress.grid()
        self.progress.start(10)
        
        thread = threading.Thread(target=self.perform_ping, args=(ip_address,))
        thread.daemon = True
        thread.start()
    
    def perform_ping(self, ip_address):
        """Виконує ping команду в окремому потоці"""
        try:
            # Визначаємо параметри ping для різних ОС
            if platform.system().lower() == "windows":
                ping_cmd = ["ping", "-n", "4", ip_address]
            else:
                ping_cmd = ["ping", "-c", "4", ip_address]
            
            # Виконуємо ping команду
            result = subprocess.run(ping_cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            # Обробляємо результат в головному потоці
            self.root.after(0, self.handle_ping_result, result.returncode == 0, ip_address)
            
        except subprocess.TimeoutExpired:
            self.root.after(0, self.handle_ping_result, False, ip_address, "Час очікування вичерпано")
        except Exception as e:
            self.root.after(0, self.handle_ping_result, False, ip_address, f"Помилка: {str(e)}")
    
    def handle_ping_result(self, success, ip_address, error_msg=None):
        """Обробляє результат ping команди"""
        # Зупиняємо прогрес-бар та відновлюємо кнопку
        self.progress.stop()
        self.progress.grid_remove()
        self.ping_button.config(state='normal', text='Ping')
        
        if success:
            messagebox.showinfo("Результат", f"Все ОК!\n\nАдреса {ip_address} доступна")
        else:
            if error_msg:
                messagebox.showerror("Результат", f"Задана адреса не відповідає\n\n{error_msg}")
            else:
                messagebox.showerror("Результат", f"Задана адреса не відповідає\n\nАдреса {ip_address} недоступна")

def main():
    root = tk.Tk()
    app = PingChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()