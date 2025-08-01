import os
import hashlib
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from queue import Queue

class DuplicateFinder:
    def __init__(self):
        self.queue = Queue()
        self.stop_event = threading.Event()
        
    def calculate_file_hash(self, filepath, hash_func=hashlib.md5, chunk_size=8192):
        """Вычисляет хэш файла для сравнения"""
        if self.stop_event.is_set():
            return None
            
        h = hash_func()
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
                if self.stop_event.is_set():
                    return None
        return h.hexdigest()

    def find_duplicate_media(self, folder_path, extensions=None):
        """Находит дубликаты медиафайлов в указанной папке"""
        if extensions is None:
            extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                          '.mp4', '.avi', '.mov', '.mkv', '.flv',
                          '.mp3', '.wav', '.ogg', '.flac', '.aac'}
        
        files_by_size = defaultdict(list)
        files_by_hash = defaultdict(list)
        
        # Сначала группируем файлы по размеру (быстрая проверка)
        for root, _, files in os.walk(folder_path):
            if self.stop_event.is_set():
                return None
                
            for filename in files:
                if self.stop_event.is_set():
                    return None
                    
                ext = os.path.splitext(filename)[1].lower()
                if ext in extensions:
                    filepath = os.path.join(root, filename)
                    try:
                        file_size = os.path.getsize(filepath)
                        files_by_size[file_size].append(filepath)
                        self.queue.put(('progress', filepath))
                    except (OSError, PermissionError):
                        continue
        
        # Затем проверяем хэш файлов с одинаковым размером
        for size, files in files_by_size.items():
            if self.stop_event.is_set():
                return None
                
            if len(files) > 1:
                for filepath in files:
                    if self.stop_event.is_set():
                        return None
                        
                    try:
                        file_hash = self.calculate_file_hash(filepath)
                        if file_hash is None:  # Проверка на остановку
                            return None
                        files_by_hash[file_hash].append(filepath)
                        self.queue.put(('progress', filepath))
                    except (OSError, PermissionError):
                        continue
        
        # Возвращаем только настоящие дубликаты (хэш совпадает)
        return {h: fs for h, fs in files_by_hash.items() if len(fs) > 1}

def select_folder():
    """Открывает диалог выбора папки"""
    folder_path = filedialog.askdirectory(title="Выберите папку для поиска дубликатов")
    if folder_path:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder_path)

def start_search():
    """Запускает поиск дубликатов в отдельном потоке"""
    folder_path = entry_folder.get()
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showerror("Ошибка", "Пожалуйста, выберите корректную папку")
        return
    
    # Очистка предыдущих результатов
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Поиск дубликатов...\n")
    search_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    progress_bar['value'] = 0
    progress_bar.start()
    
    # Создаем экземпляр поисковика
    finder = DuplicateFinder()
    finder.stop_event.clear()
    
    # Запуск поиска в отдельном потоке
    def worker():
        duplicates = finder.find_duplicate_media(folder_path)
        finder.queue.put(('result', duplicates))
    
    threading.Thread(target=worker, daemon=True).start()
    
    # Проверка очереди в основном потоке
    check_queue(finder)

def stop_search():
    """Останавливает поиск дубликатов"""
    duplicate_finder.stop_event.set()
    stop_button.config(state=tk.DISABLED)
    progress_bar.stop()
    result_text.insert(tk.END, "\nПоиск остановлен пользователем\n")

def check_queue(finder):
    """Проверяет очередь сообщений из рабочего потока"""
    try:
        while True:
            msg_type, data = finder.queue.get_nowait()
            
            if msg_type == 'progress':
                # Обновляем прогресс (можно добавить счетчик файлов)
                pass
            elif msg_type == 'result':
                # Отображаем результаты
                progress_bar.stop()
                progress_bar['value'] = 100
                search_button.config(state=tk.NORMAL)
                stop_button.config(state=tk.DISABLED)
                
                if data is None:
                    result_text.insert(tk.END, "\nПоиск прерван\n")
                elif not data:
                    result_text.insert(tk.END, "\nДубликаты не найдены.\n")
                else:
                    result_text.insert(tk.END, f"\nНайдено {len(data)} групп дубликатов:\n\n")
                    for i, (hash_val, files) in enumerate(data.items(), 1):
                        result_text.insert(tk.END, f"Группа {i} (файлы идентичны):\n")
                        for file in files:
                            result_text.insert(tk.END, f" - {file}\n")
                        result_text.insert(tk.END, "\n")
                return
                
    except:
        # Если в очереди нет сообщений, проверяем снова через 100 мс
        root.after(100, lambda: check_queue(finder))

# Создание GUI
root = tk.Tk()
root.title("Поиск дубликатов медиафайлов")
root.geometry("800x600")

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Выбор папки
ttk.Label(frame, text="Папка для поиска:").grid(row=0, column=0, sticky=tk.W)
entry_folder = ttk.Entry(frame, width=50)
entry_folder.grid(row=0, column=1, sticky=tk.EW, padx=5)
ttk.Button(frame, text="Обзор...", command=select_folder).grid(row=0, column=2, padx=5)

# Кнопки управления
button_frame = ttk.Frame(frame)
button_frame.grid(row=1, column=0, columnspan=3, pady=10)
search_button = ttk.Button(button_frame, text="Найти дубликаты", command=start_search)
search_button.pack(side=tk.LEFT, padx=5)
stop_button = ttk.Button(button_frame, text="Остановить", command=stop_search, state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=5)

# Прогресс-бар
progress_bar = ttk.Progressbar(frame, mode='indeterminate')
progress_bar.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)

# Результаты
result_text = tk.Text(frame, wrap=tk.WORD)
result_text.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW, pady=5)

# Scrollbar для результатов
scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=result_text.yview)
scrollbar.grid(row=3, column=3, sticky=tk.NS)
result_text['yscrollcommand'] = scrollbar.set

# Настройка расширения
frame.columnconfigure(1, weight=1)
frame.rowconfigure(3, weight=1)

# Глобальный экземпляр поисковика
duplicate_finder = DuplicateFinder()

root.mainloop()