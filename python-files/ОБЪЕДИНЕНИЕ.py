import pandas as pd
import os
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading

class ExcelMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Объединение Excel файлов")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Переменные
        self.folder_path = tk.StringVar()
        self.output_filename = tk.StringVar(value="объединенный_файл.xlsx")
        self.progress = tk.DoubleVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Объединение Excel файлов", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Выбор папки
        ttk.Label(main_frame, text="Папка с файлами:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(folder_frame, textvariable=self.folder_path).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(folder_frame, text="Обзор", command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        
        # Имя выходного файла
        ttk.Label(main_frame, text="Имя выходного файла:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_filename).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Найти файлы", command=self.find_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Объединить файлы", command=self.start_merge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Очистить", command=self.clear_log).pack(side=tk.LEFT)
        
        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Добавляем контекстное меню для лога
        self.create_context_menu()
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.log_text, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_log)
        self.context_menu.add_command(label="Очистить", command=self.clear_log)
        
        self.log_text.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    
    def copy_log(self):
        try:
            selected_text = self.log_text.get("sel.first", "sel.last")
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
        except:
            pass
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку с Excel файлами")
        if folder:
            self.folder_path.set(folder)
            self.log("Выбрана папка: " + folder)
    
    def find_files(self):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Ошибка", "Папка не выбрана или не существует")
            return
        
        excel_files = glob.glob(os.path.join(folder, "*.xlsx")) + \
                     glob.glob(os.path.join(folder, "*.xls"))
        
        self.clear_log()
        if excel_files:
            self.log(f"Найдено файлов: {len(excel_files)}")
            for file in excel_files:
                self.log(f"✓ {os.path.basename(file)}")
        else:
            self.log("Excel файлы не найдены!")
    
    def start_merge(self):
        if not self.folder_path.get():
            messagebox.showerror("Ошибка", "Сначала выберите папку с файлами")
            return
        
        # Запуск в отдельном потоке чтобы не блокировать GUI
        thread = threading.Thread(target=self.merge_files)
        thread.daemon = True
        thread.start()
    
    def merge_files(self):
        try:
            self.update_status("Начало объединения...")
            self.progress.set(0)
            
            folder = self.folder_path.get()
            output_file = self.output_filename.get()
            
            excel_files = glob.glob(os.path.join(folder, "*.xlsx")) + \
                         glob.glob(os.path.join(folder, "*.xls"))
            
            if not excel_files:
                self.log("❌ Excel файлы не найдены!")
                self.update_status("Файлы не найдены")
                return
            
            self.clear_log()
            self.log(f"🔍 Найдено файлов: {len(excel_files)}")
            self.log("Начинаю объединение...")
            
            all_dataframes = []
            processed_files = 0
            
            for file in excel_files:
                try:
                    self.log(f"📖 Читаю файл: {os.path.basename(file)}")
                    
                    df = pd.read_excel(file)
                    all_dataframes.append(df)
                    processed_files += 1
                    
                    self.log(f"✅ Обработан: {os.path.basename(file)} - {len(df)} строк")
                    
                    # Обновляем прогресс
                    progress_value = (processed_files / len(excel_files)) * 100
                    self.progress.set(progress_value)
                    self.update_status(f"Обработано {processed_files}/{len(excel_files)} файлов")
                    
                except Exception as e:
                    self.log(f"❌ Ошибка в файле {os.path.basename(file)}: {str(e)}")
            
            if all_dataframes:
                self.log("📊 Объединяю данные...")
                combined_df = pd.concat(all_dataframes, ignore_index=True)
                
                self.log("💾 Сохраняю результат...")
                combined_df.to_excel(output_file, index=False)
                
                self.log("=" * 50)
                self.log(f"✅ ОБЪЕДИНЕНИЕ ЗАВЕРШЕНО!")
                self.log(f"📁 Итоговый файл: {output_file}")
                self.log(f"📈 Всего строк: {len(combined_df)}")
                self.log(f"📂 Обработано файлов: {len(all_dataframes)}")
                self.log("=" * 50)
                
                self.progress.set(100)
                self.update_status("Объединение завершено!")
                
                messagebox.showinfo("Готово", 
                                  f"Файлы успешно объединены!\n\n"
                                  f"Результат: {output_file}\n"
                                  f"Всего строк: {len(combined_df)}\n"
                                  f"Обработано файлов: {len(all_dataframes)}")
            else:
                self.log("❌ Не удалось прочитать ни одного файла")
                self.update_status("Ошибка - файлы не прочитаны")
                
        except Exception as e:
            error_msg = f"Критическая ошибка: {str(e)}"
            self.log(error_msg)
            self.update_status("Ошибка выполнения")
            messagebox.showerror("Ошибка", error_msg)
    
    def log(self, message):
        def update_log():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.update_idletasks()
        
        self.root.after(0, update_log)
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def update_status(self, message):
        def update():
            self.status_label.config(text=message)
        
        self.root.after(0, update)

def main():
    try:
        # Проверяем наличие необходимых библиотек
        import pandas
        import openpyxl
    except ImportError as e:
        print("Необходимо установить библиотеки:")
        print("pip install pandas openpyxl")
        return
    
    root = tk.Tk()
    app = ExcelMergerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()