#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import shutil
from pathlib import Path
import sys
import os

class DDSCopierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DDS File Copier - Копіювання DDS файлів")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Переменные
        self.source_var = tk.StringVar()
        self.names_dir_var = tk.StringVar()
        self.out_dir_var = tk.StringVar()
        self.recursive_var = tk.BooleanVar()
        self.overwrite_var = tk.BooleanVar()
        self.dry_run_var = tk.BooleanVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка грида
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="DDS File Copier", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # Исходный файл
        ttk.Label(main_frame, text="Исходный .dds файл:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Выбрать", 
                  command=self.browse_source_file).grid(
            row=row, column=2, padx=(0, 0), pady=5)
        row += 1
        
        # Папка с именами
        ttk.Label(main_frame, text="Папка с .dds-эталонами:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.names_dir_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Выбрать", 
                  command=self.browse_names_dir).grid(
            row=row, column=2, padx=(0, 0), pady=5)
        row += 1
        
        # Папка назначения
        ttk.Label(main_frame, text="Папка для сохранения:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.out_dir_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Выбрать", 
                  command=self.browse_out_dir).grid(
            row=row, column=2, padx=(0, 0), pady=5)
        row += 1
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        row += 1
        
        # Опции
        options_frame = ttk.LabelFrame(main_frame, text="Опции", padding="10")
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(options_frame, text="Рекурсивный поиск в подпапках", 
                       variable=self.recursive_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Перезаписывать существующие файлы", 
                       variable=self.overwrite_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Сухой прогон (только показать действия)", 
                       variable=self.dry_run_var).grid(row=2, column=0, sticky=tk.W)
        row += 1
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(buttons_frame, text="Начать копирование", 
                                      command=self.start_copying, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Очистить всё", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        row += 1
        
        # Текстовое поле для логов
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        # Текстовое поле с прокруткой
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_source_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите исходный .dds файл",
            filetypes=[("DDS files", "*.dds"), ("All files", "*.*")]
        )
        if filename:
            self.source_var.set(filename)
            
    def browse_names_dir(self):
        dirname = filedialog.askdirectory(title="Выберите папку с .dds-эталонами")
        if dirname:
            self.names_dir_var.set(dirname)
            
    def browse_out_dir(self):
        dirname = filedialog.askdirectory(title="Выберите папку для сохранения копий")
        if dirname:
            self.out_dir_var.set(dirname)
            
    def clear_all(self):
        self.source_var.set("")
        self.names_dir_var.set("")
        self.out_dir_var.set("")
        self.recursive_var.set(False)
        self.overwrite_var.set(False)
        self.dry_run_var.set(False)
        self.log_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        
    def log_message(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def gather_dds_files(self, folder: Path, recursive: bool) -> list[Path]:
        """Собирает список .dds файлов в папке"""
        if not folder.exists() or not folder.is_dir():
            raise FileNotFoundError(f"Папку не знайдено або це не папка: {folder}")
        files = []
        it = folder.rglob("*") if recursive else folder.glob("*")
        for p in it:
            if p.is_file() and p.suffix.lower() == ".dds":
                files.append(p)
        return files
        
    def validate_inputs(self):
        """Проверяет корректность введенных данных"""
        if not self.source_var.get().strip():
            messagebox.showerror("Ошибка", "Выберите исходный .dds файл")
            return False
            
        if not self.names_dir_var.get().strip():
            messagebox.showerror("Ошибка", "Выберите папку с .dds-эталонами")
            return False
            
        if not self.out_dir_var.get().strip():
            messagebox.showerror("Ошибка", "Выберите папку для сохранения")
            return False
            
        src = Path(self.source_var.get().strip())
        if not src.exists() or not src.is_file():
            messagebox.showerror("Ошибка", f"Исходный файл не найден: {src}")
            return False
            
        if src.suffix.lower() != ".dds":
            messagebox.showerror("Ошибка", f"Исходный файл должен быть .dds (сейчас: {src.suffix})")
            return False
            
        return True
        
    def start_copying(self):
        """Запускает процесс копирования в отдельном потоке"""
        if not self.validate_inputs():
            return
            
        self.start_button.config(state='disabled')
        self.log_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.copy_files_thread, daemon=True)
        thread.start()
        
    def copy_files_thread(self):
        """Основная логика копирования файлов"""
        try:
            src = Path(self.source_var.get().strip())
            names_dir = Path(self.names_dir_var.get().strip())
            out_dir = Path(self.out_dir_var.get().strip())
            recursive = self.recursive_var.get()
            overwrite = self.overwrite_var.get()
            dry_run = self.dry_run_var.get()
            
            self.log_message(f"🔍 Поиск .dds файлов в '{names_dir}'...")
            
            try:
                name_files = self.gather_dds_files(names_dir, recursive)
            except Exception as e:
                self.log_message(f"❌ Ошибка доступа к папке: {e}")
                return
                
            if not name_files:
                self.log_message("⚠️ В папке не найдено ни одного .dds файла")
                return
                
            # Создание папки назначения
            try:
                out_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.log_message(f"❌ Не удалось создать папку назначения: {e}")
                return
                
            self.log_message(f"✅ Найдено {len(name_files)} .dds файлов")
            self.log_message(f"{'🔎 Сухой прогон' if dry_run else '🗂️ Начинаю копирование'} "
                           f"(перезапись: {'да' if overwrite else 'нет'})")
            
            copied = 0
            skipped = 0
            total = len(name_files)
            
            for i, ref in enumerate(name_files):
                target = out_dir / ref.name
                
                # Обновление прогресса
                progress_value = (i / total) * 100
                self.progress['value'] = progress_value
                self.root.update_idletasks()
                
                if target.exists() and not overwrite:
                    self.log_message(f"⏭️ Пропуск (существует): {target.name}")
                    skipped += 1
                    continue
                    
                if dry_run:
                    self.log_message(f"→ Создал бы копию: {target.name}")
                    copied += 1
                else:
                    try:
                        shutil.copy2(src, target)
                        self.log_message(f"✅ Скопировано: {target.name}")
                        copied += 1
                    except Exception as e:
                        self.log_message(f"❌ Ошибка копирования '{target.name}': {e}")
                        
            self.progress['value'] = 100
            self.log_message(f"\n🎉 Готово! Скопировано: {copied}, пропущено: {skipped}, всего: {total}")
            
            if not dry_run and copied > 0:
                messagebox.showinfo("Успех", f"Операция завершена!\nСкопировано: {copied} файлов")
                
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {e}")
            messagebox.showerror("Критическая ошибка", str(e))
        finally:
            self.start_button.config(state='normal')

def main():
    root = tk.Tk()
    
    # Настройка стилей
    style = ttk.Style()
    style.theme_use('clam')  # Современная тема
    
    # Создание приложения
    app = DDSCopierGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()