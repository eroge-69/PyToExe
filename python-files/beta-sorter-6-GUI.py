import os
import shutil
import pandas as pd
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

class PhotoSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сортиране на снимки")
        self.root.geometry("700x650")
        
        # Променливи за пътищата
        self.t1_path = tk.StringVar()
        self.t2_path = tk.StringVar()
        self.t3_path = tk.StringVar()
        self.excel_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Създаване на интерфейса
        self.create_widgets()
        
        # Конфигурация на стилове
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))
        
    def create_widgets(self):
        # Фрейм за входни данни
        input_frame = ttk.LabelFrame(self.root, text="Входни параметри", padding=(15, 10))
        input_frame.pack(fill="x", padx=15, pady=10)
        
        # T1
        ttk.Label(input_frame, text="Папка T1:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.t1_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.t1_path)).grid(row=0, column=2)
        
        # T2
        ttk.Label(input_frame, text="Папка T2:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.t2_path, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.t2_path)).grid(row=1, column=2)
        
        # T3
        ttk.Label(input_frame, text="Папка T3:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.t3_path, width=60).grid(row=2, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.t3_path)).grid(row=2, column=2)
        
        # Excel файл
        ttk.Label(input_frame, text="Excel файл:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.excel_path, width=60).grid(row=3, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_file(self.excel_path)).grid(row=3, column=2)
        
        # Изходна папка
        ttk.Label(input_frame, text="Изходна папка:").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.output_path, width=60).grid(row=4, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.output_path)).grid(row=4, column=2)
        
        # Лог прозорец
        log_frame = ttk.LabelFrame(self.root, text="Лог на процеса", padding=(15, 10))
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=15)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.config(state="disabled")
        
        # Бутони за действие
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Button(button_frame, text="Стартирай сортирането", command=self.run_sorting).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Изчисти лога", command=self.clear_log).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Нулиране", command=self.reset_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Изход", command=self.root.destroy).pack(side="right", padx=5)
        
    def browse_folder(self, path_var):
        folder_path = filedialog.askdirectory()
        if folder_path:
            path_var.set(folder_path)
            
    def browse_file(self, path_var):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            path_var.set(file_path)
            
    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
    def reset_all(self):
        """Нулира всички полета и лога"""
        self.t1_path.set("")
        self.t2_path.set("")
        self.t3_path.set("")
        self.excel_path.set("")
        self.output_path.set("")
        self.clear_log()
        
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()
        
    def run_sorting(self):
        # Проверка за попълнени всички полета
        if not all([self.t1_path.get(), self.t2_path.get(), self.t3_path.get(), 
                   self.excel_path.get(), self.output_path.get()]):
            messagebox.showerror("Грешка", "Моля, попълнете всички полета!")
            return
            
        try:
            # Изпълнение на основната логика
            self.execute_sorting_logic()
        except Exception as e:
            self.log_message(f"❌ Критична грешка: {str(e)}")
            messagebox.showerror("Грешка", f"Възникна грешка:\n{str(e)}")
            
    def execute_sorting_logic(self):
        # Подобрен регулярен израз, който обработва интервали в скобите
        pattern = re.compile(r"\(\s*(\d+)\s*\)")
        
        # Статистика
        stats = {
            "T1": {"total": 0, "success": 0, "files_copied": 0, "duplicates": 0},
            "T2": {"total": 0, "success": 0, "files_copied": 0, "duplicates": 0},
            "T3": {"total": 0, "success": 0, "files_copied": 0, "duplicates": 0}
        }
        
        # Валидни файлови разширения
        VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.nef', '.cr2', '.dng', '.arw'}
        
        copied_files = set()  # За проследяване на вече копирани файлове
        
        source_folders = {
            "T1": self.t1_path.get(),
            "T2": self.t2_path.get(),
            "T3": self.t3_path.get()
        }
        destination_folder = self.output_path.get()
        excel_path = self.excel_path.get()
        
        def find_files_by_number(folder, number):
            if not os.path.exists(folder):
                return []
            
            matching_files = []
            # Подобрен регулярен израз, който обработва интервали около числото
            num_pattern = re.compile(rf'(^|\D|\s){number}(\D|\s|$)')
            
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isdir(file_path):
                    continue
                    
                _, ext = os.path.splitext(filename)
                if ext.lower() not in VALID_EXTENSIONS:
                    continue
                    
                name_without_ext = os.path.splitext(filename)[0]
                
                if num_pattern.search(name_without_ext):
                    matching_files.append(filename)
                    
            return matching_files

        try:
            df = pd.read_excel(excel_path, header=None)
            os.makedirs(destination_folder, exist_ok=True)

            # Събиране на валидни номера
            valid_numbers = {"T1": set(), "T2": set(), "T3": set()}
            
            for col_idx, location in enumerate(["T1", "T2", "T3"]):
                column_data = df[col_idx].dropna()
                for cell_value in column_data:
                    # Преобразуване в низ и обработка на интервалите
                    cell_str = str(cell_value).strip()
                    match = pattern.search(cell_str)
                    if match:
                        file_number = match.group(1)
                        valid_numbers[location].add(file_number)
                        stats[location]["total"] += 1

            # Копиране на файлове
            for location in ["T1", "T2", "T3"]:
                source_folder = source_folders[location]
                
                for file_number in valid_numbers[location]:
                    # Премахване на интервали около номера
                    clean_number = file_number.strip()
                    matched_files = find_files_by_number(source_folder, clean_number)
                    
                    if matched_files:
                        copied_count = 0
                        duplicate_count = 0
                        for filename in matched_files:
                            file_key = f"{location}_{clean_number}_{filename}"
                            if file_key in copied_files:
                                self.log_message(f"⚠️ Файлът вече е копиран в този сеанс: {location}/{filename}")
                                continue
                                
                            source_path = os.path.join(source_folder, filename)
                            dest_path = os.path.join(destination_folder, filename)
                            
                            # Проверка за съществуващ файл в изходната папка
                            if os.path.exists(dest_path):
                                self.log_message(f"⚠️ Дублиран файл пропуснат: {location}/{filename} (вече съществува в изходната папка)")
                                stats[location]["duplicates"] += 1
                                duplicate_count += 1
                                continue

                            try:
                                shutil.copy2(source_path, dest_path)
                                copied_count += 1
                                copied_files.add(file_key)
                                self.log_message(f"✓ Успешно: {location}/{filename}")
                            except Exception as copy_error:
                                self.log_message(f"❌ Грешка при копиране: {location}/{filename} - {str(copy_error)}")
                        
                        if copied_count > 0:
                            stats[location]["success"] += 1
                        stats[location]["files_copied"] += copied_count
                        stats[location]["duplicates"] += duplicate_count
                    else:
                        self.log_message(f"✖ Грешка: Няма файлове с номер {clean_number} в {location}")

            # Статистика
            self.log_message("\n" + "="*50)
            self.log_message("ДЕТАЙЛНА СТАТИСТИКА ЗА КОПИРАНЕТО")
            self.log_message("="*50)
            
            total_entries = 0
            total_success_numbers = 0
            total_copied_files = 0
            total_duplicates = 0
            
            for location, data in stats.items():
                total_entries += data["total"]
                total_success_numbers += data["success"]
                total_copied_files += data["files_copied"]
                total_duplicates += data["duplicates"]
                
                self.log_message(f"\n{location}:")
                self.log_message(f"  - Общо номера: {data['total']}")
                self.log_message(f"  - Намерени номера: {data['success']}")
                self.log_message(f"  - Копирани файлове: {data['files_copied']}")
                self.log_message(f"  - Дублирани файлове (пропуснати): {data['duplicates']}")
            
            self.log_message("\n" + "-"*50)
            self.log_message("ОБЩА СТАТИСТИКА:")
            self.log_message(f"  - Общо обработени номера: {total_entries}")
            self.log_message(f"  - Общо намерени номера: {total_success_numbers}")
            self.log_message(f"  - Общо копирани файлове: {total_copied_files}")
            self.log_message(f"  - Общо дублирани файлове (пропуснати): {total_duplicates}")
            self.log_message("="*50)
            
            self.log_message(f"\nГотово! Всички файлове са в: {destination_folder}")
            
            # Показване на статистиката в прозорец
            message = "СТАТИСТИКА ЗА КОПИРАНЕТО\n\n"
            for location, data in stats.items():
                message += f"{location}:\n"
                message += f"  - Общо номера: {data['total']}\n"
                message += f"  - Намерени номера: {data['success']}\n"
                message += f"  - Копирани файлове: {data['files_copied']}\n"
                message += f"  - Дублирани файлове: {data['duplicates']}\n\n"
            
            message += "ОБЩА СТАТИСТИКА:\n"
            message += f"  - Общо обработени номера: {total_entries}\n"
            message += f"  - Общо намерени номера: {total_success_numbers}\n"
            message += f"  - Общо копирани файлове: {total_copied_files}\n"
            message += f"  - Общо дублирани файлове: {total_duplicates}\n"
            
            messagebox.showinfo("Копиране на снимки - Завършено", message)

        except Exception as e:
            self.log_message(f"❌ Критична грешка: {str(e)}")
            messagebox.showerror("Грешка", f"Възникна грешка по време на копирането:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSorterApp(root)
    root.mainloop()