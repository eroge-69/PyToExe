import socket
import threading
import time
import subprocess
import platform

# Импорт tkinter компонентов
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class IPScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Сканер IP адресов")
        self.root.geometry("600x500")
        self.center_window()
        
        # Очередь для потоков
        self.queue = Queue()
        self.scanning = False
        
        self.setup_ui()
        
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Сканирование IP диапазона", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Диапазон IP
        ip_frame = ttk.LabelFrame(main_frame, text="Диапазон IP адресов", padding="10")
        ip_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(ip_frame, text="192.168.1.1 - 192.168.1.255", 
                 font=("Arial", 10)).pack()
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Начать сканирование", 
                                      command=self.start_scan)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Остановить", 
                                     command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Очистить результаты", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к сканированию")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Результаты
        results_frame = ttk.LabelFrame(main_frame, text="Результаты сканирования", padding="10")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview для результатов
        columns = ("IP", "Статус", "Имя хоста")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Копирайт
        copyright_label = ttk.Label(main_frame, 
                                   text="ГБУЗ РБ Красноусольская ЦРБ (С) 2025 (A. Aibatov)",
                                   font=("Arial", 8),
                                   foreground="gray")
        copyright_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def ping_host(self, ip):
        """Пинг хоста"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', '-w', '1000', ip]
            return subprocess.call(command, stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL) == 0
        except:
            return False
    
    def get_hostname(self, ip):
        """Получение имени хоста"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return "Неизвестно"
    
    def worker(self):
        """Рабочая функция для потоков"""
        while self.scanning:
            try:
                ip = self.queue.get_nowait()
            except:
                break
            
            if self.ping_host(ip):
                hostname = self.get_hostname(ip)
                self.root.after(0, self.add_result, ip, "Доступен", hostname)
            else:
                self.root.after(0, self.add_result, ip, "Недоступен", "")
            
            self.queue.task_done()
            time.sleep(0.01)  # Небольшая задержка для плавности
    
    def start_scan(self):
        """Начать сканирование"""
        if self.scanning:
            return
        
        self.scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.clear_results()
        
        # Заполнение очереди IP адресами
        for i in range(1, 256):
            ip = f"192.168.1.{i}"
            self.queue.put(ip)
        
        # Настройка прогресс бара
        self.progress['maximum'] = 255
        self.progress['value'] = 0
        
        # Запуск потоков
        self.status_label.config(text="Сканирование...")
        
        for _ in range(50):  # 50 потоков для быстрого сканирования
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
        
        # Запуск обновления прогресс бара
        self.update_progress()
    
    def stop_scan(self):
        """Остановить сканирование"""
        self.scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Сканирование остановлено")
    
    def update_progress(self):
        """Обновление прогресс бара"""
        if self.scanning:
            current = 255 - self.queue.qsize()
            self.progress['value'] = current
            
            if current < 255:
                self.root.after(100, self.update_progress)
            else:
                self.scanning = False
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.status_label.config(text="Сканирование завершено")
    
    def add_result(self, ip, status, hostname):
        """Добавление результата в таблицу"""
        if status == "Доступен":
            tags = ('available',)
        else:
            tags = ('unavailable',)
        
        self.tree.insert("", tk.END, values=(ip, status, hostname), tags=tags)
    
    def clear_results(self):
        """Очистка результатов"""
        for item in self.tree.get_children():
            self.tree.delete(item)

# Класс очереди для многопоточности
class Queue:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
    
    def put(self, item):
        with self.lock:
            self.items.append(item)
    
    def get(self):
        with self.lock:
            if self.items:
                return self.items.pop(0)
        return None
    
    def get_nowait(self):
        return self.get()
    
    def qsize(self):
        with self.lock:
            return len(self.items)
    
    def task_done(self):
        pass

def main():
    """Основная функция"""
    root = tk.Tk()
    app = IPScanner(root)
    
    # Настройка тегов для цветов
    app.tree.tag_configure('available', background='#e8f5e8')
    app.tree.tag_configure('unavailable', background='#ffe6e6')
    
    root.mainloop()

if __name__ == "__main__":
    main()