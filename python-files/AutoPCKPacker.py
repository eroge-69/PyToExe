import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import gzip
import os
import shutil

class JSProcessorApp:
    # Константы с правилами замены функций
    FUNCTION_REPLACEMENTS = {
        """function loadFetch(file, tracker, fileSize, raw) {
\t\ttracker[file] = {
\t\t\ttotal: fileSize || 0,
\t\t\tloaded: 0,
\t\t\tdone: false,
\t\t};
\t\treturn fetch(file).then(function (response) {
\t\t\tif (!response.ok) {
\t\t\t\treturn Promise.reject(new Error(`Failed loading file '${file}'`));
\t\t\t}
\t\t\tconst tr = getTrackedResponse(response, tracker[file]);
\t\t\tif (raw) {
\t\t\t\treturn Promise.resolve(tr);
\t\t\t}
\t\t\treturn tr.arrayBuffer();
\t\t});
\t}""" : 
        """//changed by autoPCK
function loadFetch(file, tracker, fileSize, raw) {
    var p_file = file;

    tracker[file] = {
        total: fileSize || 0,
        loaded: 0,
        done: false,
    };

    return fetch(file).then(function (response) {
        if (!response.ok) {
            return Promise.reject(new Error(`Failed loading file '${file}'`));
        }

        const tr = getTrackedResponse(response, tracker[p_file]);
        return Promise.resolve(tr.arrayBuffer().then(buffer => {
            return new Response(pako.inflate(buffer), { headers: tr.headers });
        }));
    });
}""",
        
        """\tthis.preload = function (pathOrBuffer, destPath, fileSize) {
\t\tlet buffer = null;
\t\tif (typeof pathOrBuffer === 'string') {
\t\t\tconst me = this;
\t\t\treturn this.loadPromise(pathOrBuffer, fileSize).then(function (buf) {
\t\t\t\tme.preloadedFiles.push({
\t\t\t\t\tpath: destPath || pathOrBuffer,
\t\t\t\t\tbuffer: buf,
\t\t\t\t});
\t\t\t\treturn Promise.resolve();
\t\t\t});
\t\t} else if (pathOrBuffer instanceof ArrayBuffer) {
\t\t\tbuffer = new Uint8Array(pathOrBuffer);
\t\t} else if (ArrayBuffer.isView(pathOrBuffer)) {
\t\t\tbuffer = new Uint8Array(pathOrBuffer.buffer);
\t\t}
\t\tif (buffer) {
\t\t\tthis.preloadedFiles.push({
\t\t\t\tpath: destPath,
\t\t\t\tbuffer: pathOrBuffer,
\t\t\t});
\t\t\treturn Promise.resolve();
\t\t}
\t\treturn Promise.reject(new Error('Invalid object for preloading'));
\t};""" : 
        """//changed by autoPCK
this.preload = function (pathOrBuffer, destPath, fileSize) {
    let buffer = null;
    if (typeof pathOrBuffer === 'string') {
        const me = this;
        return this.loadPromise(pathOrBuffer, fileSize).then(function (buf) {
            buf.arrayBuffer().then(data => {
                me.preloadedFiles.push({
                    path: destPath || pathOrBuffer,
                    buffer: data,
                });
            });
            return Promise.resolve();
        });
    } else if (pathOrBuffer instanceof ArrayBuffer) {
        buffer = new Uint8Array(pathOrBuffer);
    } else if (ArrayBuffer.isView(pathOrBuffer)) {
        buffer = new Uint8Array(pathOrBuffer.buffer);
    }
    if (buffer) {
        this.preloadedFiles.push({
            path: destPath,
            buffer: pathOrBuffer,
        });
        return Promise.resolve();
    }
    return Promise.reject(new Error('Invalid object for preloading'));
};"""
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("PCK Compressor")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Устанавливаем современную тему
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настраиваем цвета и стили
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Status.TLabel', font=('Segoe UI', 9))
        self.style.configure('Modern.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Переменные для отслеживания состояния
        self.current_filename = "index"
        
        # Создаем основной фрейм с отступами
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="JS File Processor", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Секция выбора папки
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(folder_frame, text="Project Folder:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.folder_entry = ttk.Entry(folder_frame, width=50, font=('Segoe UI', 10))
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder, style='Modern.TButton')
        browse_btn.grid(row=0, column=2)
        
        folder_frame.columnconfigure(1, weight=1)
        
        # Секция имени файла
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(file_frame, text="Main File Name:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.filename_entry = ttk.Entry(file_frame, width=50, font=('Segoe UI', 10))
        self.filename_entry.grid(row=0, column=1, sticky="ew")
        self.filename_entry.insert(0, self.current_filename)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Секция уровней сжатия
        compression_frame = ttk.LabelFrame(main_frame, text="Compression Settings", padding=10)
        compression_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Label(compression_frame, text="WASM Compression Level:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.wasm_compression = ttk.Combobox(compression_frame, values=list(range(10)), state="readonly", width=5)
        self.wasm_compression.set(6)
        self.wasm_compression.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(compression_frame, text="PCK Compression Level:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.pck_compression = ttk.Combobox(compression_frame, values=list(range(10)), state="readonly", width=5)
        self.pck_compression.set(6)
        self.pck_compression.grid(row=0, column=3, sticky="w")
        
        compression_frame.columnconfigure(1, weight=1)
        compression_frame.columnconfigure(3, weight=1)
        
        # Привязка событий к комбобоксам сжатия
        self.wasm_compression.bind('<<ComboboxSelected>>', self.on_compression_changed)
        self.pck_compression.bind('<<ComboboxSelected>>', self.on_compression_changed)
        
        # Статус файлов
        self.status_label = ttk.Label(main_frame, text="Files status: Please select a folder", style='Status.TLabel')
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)
        
        # Создаем Notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=10)
        
        # Вкладка операций
        operations_tab = ttk.Frame(notebook, padding=10)
        notebook.add(operations_tab, text="Operations")
        
        # Информация о дополнительных действиях
        additional_frame = ttk.LabelFrame(operations_tab, text="Additional Actions", padding=10)
        additional_frame.pack(fill=tk.X, pady=5)
        
        self.additional_info = tk.Text(additional_frame, width=70, height=3, font=('Segoe UI', 9), 
                                      bg='#f9f9f9', relief='flat')
        self.additional_info.pack(fill=tk.X)
        self.additional_info.insert(tk.END, 
            "✓ Copy pako_inflate.min.js to target folder\n"
            "✓ Add pako script to index.html before main script")
        self.additional_info.config(state=tk.DISABLED)
        
        # Информация о заменяемых функциях
        functions_frame = ttk.LabelFrame(operations_tab, text="Function Replacements", padding=10)
        functions_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(functions_frame, width=70, height=4, font=('Segoe UI', 9), 
                                bg='#f9f9f9', relief='flat')
        self.info_text.pack(fill=tk.X)
        self.info_text.insert(tk.END, "The following functions will be replaced:\n- loadFetch function\n- preload function")
        self.info_text.config(state=tk.DISABLED)
        
        # Информация о сжимаемых файлах
        compress_frame = ttk.LabelFrame(operations_tab, text="File Compression", padding=10)
        compress_frame.pack(fill=tk.X, pady=5)
        
        self.compress_info = tk.Text(compress_frame, width=70, height=3, font=('Segoe UI', 9), 
                                    bg='#f9f9f9', relief='flat')
        self.compress_info.pack(fill=tk.X)
        self.update_compress_info()
        self.compress_info.config(state=tk.DISABLED)
        
        # Вкладка информации о сжатии
        info_tab = ttk.Frame(notebook, padding=10)
        notebook.add(info_tab, text="Compression Info")
        
        # Информация об уровнях сжатия
        compression_info = tk.Text(info_tab, width=70, height=15, font=('Segoe UI', 9), 
                                  bg='#f9f9f9', relief='flat', wrap=tk.WORD)
        compression_info.pack(fill=tk.BOTH, expand=True)
        compression_info.insert(tk.END, 
            "Compression Levels Guide:\n\n"
            "0 - No compression (fastest)\n"
            "   - Only adds gzip header\n"
            "   - Best for already compressed files\n\n"
            "1 - Fastest compression\n"
            "   - Minimal compression ratio\n"
            "   - Fastest processing time\n\n"
            "6 - Balanced (default)\n"
            "   - Good compression ratio\n"
            "   - Reasonable speed\n\n"
            "9 - Maximum compression\n"
            "   - Best compression ratio\n"
            "   - Slowest processing time\n\n"
            "Recommended:\n"
            "• WASM files: Level 6 (good balance)\n"
            "• PCK files: Level 9 (maximum compression)")
        compression_info.config(state=tk.DISABLED)
        
        # Кнопка выполнения
        self.process_button = ttk.Button(main_frame, text="PROCESS FILES", command=self.process, 
                                        style='Modern.TButton')
        self.process_button.grid(row=6, column=0, columnspan=3, pady=20, ipadx=20, ipady=10)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Настраиваем вес строк и колонок для правильного растягивания
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Привязка событий к полям ввода
        self.folder_entry.bind('<KeyRelease>', self.on_folder_changed)
        self.folder_entry.bind('<FocusOut>', self.on_folder_changed)
        
        self.filename_entry.bind('<KeyRelease>', self.on_filename_changed)
        self.filename_entry.bind('<FocusOut>', self.on_filename_changed)
        self.filename_entry.bind('<Return>', lambda e: self.process())
        
        # Первоначальное обновление статуса
        self.update_file_status()
    
    def on_folder_changed(self, event=None):
        """Вызывается при изменении папки"""
        self.update_file_status()
    
    def on_filename_changed(self, event=None):
        """Вызывается при изменении имени файла"""
        self.current_filename = self.filename_entry.get().strip() or "index"
        self.update_compress_info()
        self.update_file_status()
    
    def on_compression_changed(self, event=None):
        """Вызывается при изменении уровня сжатия"""
        self.update_compress_info()
    
    def update_compress_info(self):
        """Обновляет информацию о сжимаемых файлах"""
        wasm_level = self.wasm_compression.get()
        pck_level = self.pck_compression.get()
        
        self.compress_info.config(state=tk.NORMAL)
        self.compress_info.delete(1.0, tk.END)
        
        # Определяем описания уровней сжатия
        wasm_desc = self.get_compression_description(wasm_level)
        pck_desc = self.get_compression_description(pck_level)
        
        self.compress_info.insert(tk.END, 
            f"Files will be compressed and replace originals:\n\n"
            f"• {self.current_filename}.wasm\n"
            f"  Compression level: {wasm_level} ({wasm_desc})\n\n"
            f"• {self.current_filename}.pck\n"
            f"  Compression level: {pck_level} ({pck_desc})")
        
        self.compress_info.config(state=tk.DISABLED)
    
    def get_compression_description(self, level):
        """Возвращает текстовое описание уровня сжатия"""
        level = int(level)
        if level == 0:
            return "No compression"
        elif level <= 3:
            return "Fast compression"
        elif level <= 6:
            return "Balanced"
        elif level <= 8:
            return "High compression"
        else:
            return "Maximum compression"
    
    def update_file_status(self):
        """Обновляет статус файлов и активирует/деактивирует кнопку"""
        folder = self.folder_entry.get()
        filename = self.filename_entry.get().strip() or "index"
        
        if not folder:
            self.status_label.config(text="Please select a folder", foreground="red")
            self.process_button.config(state="disabled")
            return
        
        if not os.path.exists(folder):
            self.status_label.config(text="Selected folder does not exist", foreground="red")
            self.process_button.config(state="disabled")
            return
        
        # Пути к файлам
        js_file = os.path.join(folder, filename + ".js")
        wasm_file = os.path.join(folder, filename + ".wasm")
        pck_file = os.path.join(folder, filename + ".pck")
        html_file = os.path.join(folder, "index.html")
        
        # Проверяем существование файлов
        js_exists = os.path.exists(js_file)
        wasm_exists = os.path.exists(wasm_file)
        pck_exists = os.path.exists(pck_file)
        html_exists = os.path.exists(html_file)
        
        # Формируем текст статуса с иконками
        status_parts = []
        if js_exists:
            status_parts.append("JS: ✓")
        else:
            status_parts.append("JS: ✗")
            
        if wasm_exists:
            status_parts.append("WASM: ✓")
        else:
            status_parts.append("WASM: ✗")
            
        if pck_exists:
            status_parts.append("PCK: ✓")
        else:
            status_parts.append("PCK: ✗")
            
        if html_exists:
            status_parts.append("HTML: ✓")
        else:
            status_parts.append("HTML: ✗")
        
        status_text = "Files status: " + " | ".join(status_parts)
        
        # Устанавливаем цвет и состояние кнопки
        if js_exists:
            self.status_label.config(text=status_text, foreground="green")
            self.process_button.config(state="normal")
        else:
            self.status_label.config(text=status_text, foreground="red")
            self.process_button.config(state="disabled")
    
    def browse_folder(self):
        """Обзор папки"""
        folder = filedialog.askdirectory(title="Select folder containing files")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.update_file_status()
    
    # Остальные методы без изменений (replace_functions_in_content, compress_and_replace_file, 
    # copy_pako_js, add_pako_to_html, normalize_code, replace_function_smart)
    
    def normalize_code(self, code):
        """Нормализует код для сравнения (удаляет лишние пробелы)"""
        lines = code.split('\n')
        normalized_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                normalized_lines.append(stripped)
        return ' '.join(normalized_lines)
    
    def replace_functions_in_content(self, content):
        """Заменяет функции в содержимом JS файла"""
        # Сначала попробуем точное совпадение
        for old_func, new_func in self.FUNCTION_REPLACEMENTS.items():
            if old_func in content:
                content = content.replace(old_func, new_func)
                print("Function replaced using exact match")
                continue
            
            # Если точное совпадение не найдено, используем более умный подход
            content = self.replace_function_smart(content, old_func, new_func)
        
        return content
    
    def replace_function_smart(self, content, old_func, new_func):
        """Умная замена функции с поиском по сигнатуре"""
        # Извлекаем имя функции из старого кода
        func_name_match = re.search(r'function\s+(\w+)', old_func)
        if not func_name_match:
            # Пробуем для методов (this.functionName)
            func_name_match = re.search(r'this\.(\w+)\s*=\s*function', old_func)
        
        if func_name_match:
            func_name = func_name_match.group(1)
            print(f"Looking for function: {func_name}")
            
            # Создаем паттерн для поиска функции по имени и параметрам
            param_pattern = r'\([^)]*\)'
            func_pattern = rf'function\s+{re.escape(func_name)}\s*{param_pattern}\s*{{'
            
            # Ищем функцию в контенте
            match = re.search(func_pattern, content)
            if match:
                print(f"Found function {func_name} by pattern")
                
                # Находим начало и конец функции
                start_index = match.start()
                
                # Находим парные скобки для тела функции
                brace_count = 0
                i = start_index
                function_started = False
                
                while i < len(content):
                    if content[i] == '{':
                        brace_count += 1
                        function_started = True
                    elif content[i] == '}':
                        brace_count -= 1
                    
                    if function_started and brace_count == 0:
                        # Нашли конец функции
                        end_index = i + 1
                        
                        # Заменяем функцию
                        content = content[:start_index] + new_func + content[end_index:]
                        print(f"Successfully replaced function {func_name}")
                        break
                    
                    i += 1
        
        return content
    
    def compress_and_replace_file(self, filepath, compression_level):
        """Сжимает файл и заменяет оригинал сжатой версией"""
        try:
            # Создаем временный файл для сжатия
            temp_file = filepath + '.tmp.gz'
            
            with open(filepath, 'rb') as f_in:
                with gzip.open(temp_file, 'wb', compresslevel=compression_level) as f_out:
                    f_out.writelines(f_in)
            
            # Заменяем оригинальный файл сжатым
            # Сначала удаляем оригинал, затем переименовываем сжатый файл
            os.remove(filepath)
            shutil.move(temp_file, filepath)
            
            return True
        except Exception as e:
            # В случае ошибки пытаемся удалить временный файл
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            print(f"Error compressing {filepath}: {e}")
            return False
    
    def copy_pako_js(self, target_folder):
        """Копирует pako_inflate.min.js из папки со скриптом в целевую папку"""
        try:
            # Получаем путь к папке со скриптом
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pako_source = os.path.join(script_dir, "pako_inflate.min.js")
            pako_target = os.path.join(target_folder, "pako_inflate.min.js")
            
            if os.path.exists(pako_source):
                shutil.copy2(pako_source, pako_target)
                return True, "pako_inflate.min.js copied successfully"
            else:
                return False, f"pako_inflate.min.js not found in {script_dir}"
        except Exception as e:
            return False, f"Error copying pako_inflate.min.js: {str(e)}"
    
    def add_pako_to_html(self, html_file, js_filename):
        """Добавляет скрипт pako в index.html перед основным скриптом"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Создаем backup
            backup_file = html_file + '.backup'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Ищем строку с подключением основного JS файла
            script_pattern = rf'<script\s+src=["\']{re.escape(js_filename)}\.js["\']\s*></script>'
            match = re.search(script_pattern, content)
            
            if match:
                # Нашли скрипт, добавляем pako перед ним
                pako_script = f'<script src="pako_inflate.min.js"></script>\n    '
                new_content = content[:match.start()] + pako_script + content[match.start():]
                
                # Сохраняем изменения
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True, "pako script added to index.html"
            else:
                return False, f"Could not find {js_filename}.js script tag in index.html"
                
        except Exception as e:
            return False, f"Error modifying index.html: {str(e)}"
    
    def process(self, event=None):
        """Основная функция обработки"""
        # Запускаем прогресс-бар
        self.progress.start()
        self.process_button.config(state="disabled")
        
        # Обновляем интерфейс
        self.root.update_idletasks()
        
        try:
            folder = self.folder_entry.get()
            filename = self.filename_entry.get().strip() or "index"
            
            # Получаем уровни сжатия
            try:
                wasm_level = int(self.wasm_compression.get())
                pck_level = int(self.pck_compression.get())
            except:
                messagebox.showerror("Error", "Please select valid compression levels (0-9)")
                return
            
            # Пути к файлам
            js_file = os.path.join(folder, filename + ".js")
            wasm_file = os.path.join(folder, filename + ".wasm")
            pck_file = os.path.join(folder, filename + ".pck")
            html_file = os.path.join(folder, "index.html")
            
            # 1. Обрабатываем JS файл
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Создаем backup
            backup_file = js_file + '.backup'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Заменяем функции
            new_content = self.replace_functions_in_content(content)
            
            # Сохраняем изменения
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 2. Сжимаем файлы (заменяем оригиналы)
            compressed_files = []
            
            if os.path.exists(wasm_file):
                if self.compress_and_replace_file(wasm_file, wasm_level):
                    compressed_files.append(f"{filename}.wasm (level {wasm_level})")
            
            if os.path.exists(pck_file):
                if self.compress_and_replace_file(pck_file, pck_level):
                    compressed_files.append(f"{filename}.pck (level {pck_level})")
            
            # 3. Копируем pako_inflate.min.js
            pako_result, pako_message = self.copy_pako_js(folder)
            
            # 4. Обновляем index.html
            html_result, html_message = False, "index.html not found"
            if os.path.exists(html_file):
                html_result, html_message = self.add_pako_to_html(html_file, filename)
            
            # Формируем сообщение об успехе
            message_parts = [f"✓ JS file processed: {filename}.js"]
            
            if compressed_files:
                message_parts.append(f"✓ Compressed files: {', '.join(compressed_files)}")
            else:
                message_parts.append("⚠ No files found for compression")
            
            message_parts.append(f"✓ {pako_message}")
            
            if os.path.exists(html_file):
                status_icon = "✓" if html_result else "⚠"
                message_parts.append(f"{status_icon} {html_message}")
            
            message_parts.append(f"📁 Backup created: {filename}.js.backup")
            if os.path.exists(html_file):
                message_parts.append(f"📁 HTML backup: index.html.backup")
            
            messagebox.showinfo("Processing Complete", "\n".join(message_parts))
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        finally:
            # Останавливаем прогресс-бар и обновляем статус
            self.progress.stop()
            self.update_file_status()

if __name__ == "__main__":
    root = tk.Tk()
    app = JSProcessorApp(root)
    root.mainloop()