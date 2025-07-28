import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
from queue import Queue

class DriverInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Установщик драйверов")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Очередь для обновления GUI из потока
        self.queue = Queue()
        
        # Стили
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Red.TLabel', foreground='red')
        self.style.configure('Green.TLabel', foreground='green')
        
        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Установщик драйверов", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Фрейм выбора папки
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="Папка с драйверами:").pack(side=tk.LEFT)
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = ttk.Button(folder_frame, text="Обзор...", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT)
        
        # Фрейм списка драйверов
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(list_frame, text="Доступные драйверы:").pack(anchor=tk.W)
        
        self.drivers_tree = ttk.Treeview(list_frame, columns=('status'), show='tree headings', selectmode='none')
        self.drivers_tree.column('#0', width=400, anchor=tk.W)
        self.drivers_tree.column('status', width=150, anchor=tk.W)
        self.drivers_tree.heading('#0', text='Драйвер')
        self.drivers_tree.heading('status', text='Статус')
        self.drivers_tree.pack(fill=tk.BOTH, expand=True)
        
        # Лог установки
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(log_frame, text="Лог установки:").pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.scan_btn = ttk.Button(button_frame, text="Сканировать", command=self.scan_drivers)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.install_btn = ttk.Button(button_frame, text="Установить", command=self.install_drivers, state=tk.DISABLED)
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = ttk.Button(button_frame, text="Выход", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="Выберите папку с драйверами")
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.scan_btn.config(state=tk.NORMAL)
    
    def scan_drivers(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Укажите корректную папку с драйверами")
            return
        
        # Очищаем дерево
        for item in self.drivers_tree.get_children():
            self.drivers_tree.delete(item)
        
        self.log("Сканирование папки с драйверами...")
        self.status_var.set("Сканирование папки с драйверами...")
        
        # Сканируем в отдельном потоке
        Thread(target=self._scan_drivers_thread, args=(folder,), daemon=True).start()
    
    def _scan_drivers_thread(self, folder):
        drivers_found = []
        
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.inf'):
                    driver_path = os.path.join(root, file)
                    drivers_found.append(driver_path)
        
        # Обновляем GUI через очередь
        self.queue.put(('update_drivers_list', drivers_found))
        self.queue.put(('log', f"Найдено {len(drivers_found)} драйверов"))
        self.queue.put(('status', "Готов к установке"))
    
    def install_drivers(self):
        if not self.drivers_tree.get_children():
            messagebox.showwarning("Предупреждение", "Нет драйверов для установки")
            return
        
        self.log("Начало установки драйверов...")
        self.status_var.set("Установка драйверов...")
        self.install_btn.config(state=tk.DISABLED)
        
        # Получаем список всех драйверов
        drivers_to_install = []
        for item in self.drivers_tree.get_children():
            drivers_to_install.append(self.drivers_tree.item(item, 'values')[0])
        
        # Устанавливаем в отдельном потоке
        Thread(target=self._install_drivers_thread, args=(drivers_to_install,), daemon=True).start()
    
    def _install_drivers_thread(self, drivers):
        for driver in drivers:
            self.queue.put(('log', f"Установка драйвера: {driver}"))
            
            try:
                result = subprocess.run(
                    ['pnputil', '/add-driver', driver, '/install'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self.queue.put(('log', "Установка успешна!"))
                self.queue.put(('log', result.stdout))
                self.queue.put(('update_driver_status', driver, "Установлен", "green"))
            except subprocess.CalledProcessError as e:
                self.queue.put(('log', f"Ошибка при установке драйвера:"))
                self.queue.put(('log', e.stderr))
                self.queue.put(('update_driver_status', driver, "Ошибка", "red"))
            except Exception as e:
                self.queue.put(('log', f"Неизвестная ошибка:"))
                self.queue.put(('log', str(e)))
                self.queue.put(('update_driver_status', driver, "Ошибка", "red"))
        
        self.queue.put(('status', "Установка завершена"))
        self.queue.put(('install_complete',))
    
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def check_queue(self):
        while not self.queue.empty():
            task = self.queue.get()
            
            if task[0] == 'update_drivers_list':
                drivers = task[1]
                for driver in drivers:
                    self.drivers_tree.insert('', tk.END, text=os.path.basename(driver), values=(driver, "Не установлен"))
                
                if drivers:
                    self.install_btn.config(state=tk.NORMAL)
            
            elif task[0] == 'update_driver_status':
                driver, status, color = task[1], task[2], task[3]
                for item in self.drivers_tree.get_children():
                    if self.drivers_tree.item(item, 'values')[0] == driver:
                        self.drivers_tree.item(item, values=(driver, status))
                        self.drivers_tree.set(item, 'status', status)
                        break
            
            elif task[0] == 'log':
                self.log(task[1])
            
            elif task[0] == 'status':
                self.status_var.set(task[1])
            
            elif task[0] == 'install_complete':
                self.install_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Готово", "Установка драйверов завершена")
        
        self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = DriverInstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()