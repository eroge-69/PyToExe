import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path


def rename_files():
    folder_path = entry_folder.get()
    pattern = entry_pattern.get()
    replacement = entry_replacement.get()
    file_format = combo_format.get().lower()

    if not folder_path:
        messagebox.showerror("Ошибка", "Укажите путь к папке")
        return

    try:
        folder = Path(folder_path)
        if not folder.is_dir():
            messagebox.showerror("Ошибка", "Указанная папка не существует")
            return

        files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == f".{file_format}"]

        if not files:
            messagebox.showinfo("Информация", f"Файлы с расширением .{file_format} не найдены")
            return

        regex_pattern = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        compiled_pattern = re.compile(regex_pattern, re.IGNORECASE)

        renamed_count = 0
        errors = []

        for file in files:
            try:
                new_name = compiled_pattern.sub(replacement, file.stem) + file.suffix
                if new_name != file.name:
                    new_path = file.parent / new_name
                    if new_path.exists():
                        errors.append(f"Файл {new_name} уже существует (оригинал: {file.name})")
                        continue
                    file.rename(new_path)
                    renamed_count += 1
            except Exception as e:
                errors.append(f"Ошибка при переименовании {file.name}: {str(e)}")

        result_message = f"Переименовано файлов: {renamed_count}/{len(files)}"
        if errors:
            result_message += "\n\nОшибки:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_message += f"\n\n...и еще {len(errors) - 5} ошибок"

        messagebox.showinfo("Готово", result_message)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Непредвиденная ошибка:\n{str(e)}")


def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder)


def show_pattern_help():
    help_text = """Шаблоны поиска и замены:

* - заменяет любое количество символов
? - один символ

Примеры:
"файл_10" → "файл_*" → "файл_5"
"файл_01.jpg" → "файл_0?.jpg" → "файл_02.jpg"
"""
    messagebox.showinfo("Помощь по шаблонам", help_text)


def toggle_examples():
    if examples_frame.winfo_ismapped():
        examples_frame.grid_remove()
        btn_examples.config(text="Показать примеры ▼")
    else:
        examples_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        btn_examples.config(text="Скрыть примеры ▲")


# --- GUI ---
root = tk.Tk()
root.title("Переименование файлов v2.3")
root.minsize(500, 300)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.columnconfigure(1, weight=1)

# Путь
tk.Label(main_frame, text="Папка:").grid(row=0, column=0, sticky="w", pady=2)
entry_folder = tk.Entry(main_frame)
entry_folder.grid(row=0, column=1, sticky="ew", padx=5)
tk.Button(main_frame, text="Обзор", command=browse_folder).grid(row=0, column=2)

# Шаблоны
tk.Label(main_frame, text="Шаблон:").grid(row=1, column=0, sticky="w", pady=2)
entry_pattern = tk.Entry(main_frame)
entry_pattern.grid(row=1, column=1, sticky="ew", padx=5)
tk.Button(main_frame, text="?", command=show_pattern_help, bg="lightblue").grid(row=1, column=2)

tk.Label(main_frame, text="Замена:").grid(row=2, column=0, sticky="w", pady=2)
entry_replacement = tk.Entry(main_frame)
entry_replacement.grid(row=2, column=1, sticky="ew", padx=5, columnspan=2)

# Формат
tk.Label(main_frame, text="Формат:").grid(row=3, column=0, sticky="w", pady=2)
formats = ["pdf", "dxf", "stp", "x_t", "cdw", "a3d", "m3d", "spf", "frw"]
combo_format = ttk.Combobox(main_frame, values=formats)
combo_format.grid(row=3, column=1, sticky="w", padx=5)
combo_format.current(0)

# Кнопка примеров
btn_examples = tk.Button(main_frame, text="Показать примеры ▼", command=toggle_examples)
btn_examples.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)

# Примеры
examples_frame = tk.LabelFrame(main_frame, text=" Примеры ")
for i, (orig, pat, rep, res) in enumerate([
    ("файл_старый.pdf", "файл_*", "документ_*", "документ_старый.pdf"),
    ("изображение_01.jpg", "изображение_??", "img_??", "img_01.jpg"),
    ("отчет_2023_финал.pdf", "отчет_*_финал", "", "2023.pdf"),
    ("лишний_текст_файл.txt", "лишний_текст_*", "", "файл.txt")
]):
    tk.Label(examples_frame, text=orig).grid(row=i, column=0, sticky="w", padx=3)
    tk.Label(examples_frame, text=pat).grid(row=i, column=1, sticky="w", padx=3)
    tk.Label(examples_frame, text=rep if rep else "(пусто)").grid(row=i, column=2, sticky="w", padx=3)
    tk.Label(examples_frame, text=res).grid(row=i, column=3, sticky="w", padx=3)

# Кнопка запуска
btn_rename = tk.Button(main_frame, text="Переименовать", command=rename_files,
                       bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
btn_rename.grid(row=6, column=0, columnspan=3, pady=10)

# Запуск
root.mainloop()
