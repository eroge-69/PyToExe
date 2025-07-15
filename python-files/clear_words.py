import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from tkinter import ttk
from collections import deque
import re
import webbrowser

# Инициализация глобальных переменных
all_data = None          # Все данные из файла
filtered_data = None     # Отфильтрованные данные с учетом стоп-слов
stop_words = set()       # Множество для хранения стоп-слов
history = deque()        # История изменений для возможности отката

def load_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
    )
    if not file_path:
        return None
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            return pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
        return None

def apply_stop_words_to_data(data, stop_words_set):
    if not stop_words_set:
        return data.copy()
    pattern = r'\b(' + '|'.join(map(re.escape, stop_words_set)) + r')\b'
    return data[~data.iloc[:, 0].astype(str).str.contains(pattern, na=False, regex=True)]

def refresh_table():
    # Очистка текущего содержимого Treeview
    for item in tree.get_children():
        tree.delete(item)
    
    # Добавление отфильтрованных данных в Treeview
    if filtered_data is not None and not filtered_data.empty:
        for index, row in filtered_data.iterrows():
            values = list(row)
            tree.insert("", "end", values=values)
    else:
        tree.insert("", "end", values=["Данные отсутствуют"] + [""] * (len(all_data.columns) - 1))

    # Обновление количества строк
    count_label.config(text=f"Количество загруженных строк: {len(tree.get_children())}")

def add_stop_word(word):
    if word in stop_words:
        messagebox.showinfo("Информация", f"Слово '{word}' уже в списке стоп-слов.")
        return
    stop_words.add(word)
    history.append(stop_words.copy())  # Сохраняем текущее состояние стоп-слов
    update_filtered_data()
    refresh_table()

def remove_stop_word(word):
    if word in stop_words:
        stop_words.remove(word)
        history.append(stop_words.copy())  # Сохраняем текущее состояние стоп-слов
        update_filtered_data()
        refresh_table()

def update_filtered_data():
    global filtered_data
    if all_data is not None:
        filtered_data = apply_stop_words_to_data(all_data, stop_words)

def open_word_selection(row_phrase):
    top = Toplevel(root)
    top.title("Выбор слова")
    top.geometry("300x200")
    
    words = row_phrase.split()
    unique_words = set(word.strip(",.!?") for word in words)
    
    for word in unique_words:
        btn = tk.Button(
            top, 
            text=f"Добавить '{word}' в стоп-слова", 
            command=lambda w=word: [add_stop_word(w), top.destroy()]
        )
        btn.pack(pady=2, fill='x', padx=10)

def show_stop_words():
    top = Toplevel(root)
    top.title("Список стоп-слов")
    top.geometry("300x400")
    
    frame = tk.Frame(top)
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Добавление списка стоп-слов с кнопками удаления
    for word in sorted(stop_words):
        row_frame = tk.Frame(frame)
        row_frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(row_frame, text=word)
        lbl.pack(side='left', fill='x', expand=True)
        
        btn = tk.Button(
            row_frame, 
            text="Удалить", 
            command=lambda w=word: [remove_stop_word(w), top.destroy(), show_stop_words()]
        )
        btn.pack(side='right')

def undo_last_action():
    if history:
        last_state = history.pop()
        global stop_words
        stop_words = last_state
        update_filtered_data()
        refresh_table()
    else:
        messagebox.showinfo("Отмена", "Нет действий для отмены.")

def save_stop_words_to_file():
    if not stop_words:
        messagebox.showinfo("Информация", "Список стоп-слов пуст.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt", 
        filetypes=[("Text files", "*.txt")]
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(stop_words)))
            messagebox.showinfo("Успех", "Список стоп-слов сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

def load_stop_words_from_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt")]
    )
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = set(line.strip() for line in f if line.strip())
                if words:
                    history.append(stop_words.copy())  # Сохраняем текущее состояние стоп-слов
                    stop_words.update(words)
                    update_filtered_data()
                    refresh_table()
                    messagebox.showinfo("Успех", "Стоп-слова загружены и применены.")
                else:
                    messagebox.showinfo("Информация", "Файл стоп-слов пуст.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

def save_file():
    if filtered_data is None or filtered_data.empty:
        messagebox.showinfo("Информация", "Нет данных для сохранения.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx", 
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
    )
    if file_path:
        try:
            if file_path.endswith(".csv"):
                filtered_data.to_csv(file_path, index=False)
            else:
                filtered_data.to_excel(file_path, index=False)
            messagebox.showinfo("Успех", "Файл успешно сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

def load_data():
    global all_data, filtered_data
    all_data = load_file()
    if all_data is not None:
        update_filtered_data()
        refresh_table()

def sort_by_column(index, ascending=True):
    global filtered_data
    if filtered_data is not None:
        filtered_data = filtered_data.sort_values(by=filtered_data.columns[index], ascending=ascending)
        refresh_table()

def sort_alphabetically():
    sort_by_column(0)

def sort_by_statistics1():
    sort_by_column(1, ascending=False) 

def sort_by_statistics2():
    sort_by_column(2, ascending=False) 

def sort_by_statistics3():
    sort_by_column(3, ascending=False) 

def contact_author():
    top = Toplevel(root)
    top.title("Связаться с автором")
    top.geometry("300x200")

    lbl = tk.Label(top, text="Обработка слов v1.0\nАвтор: Эльдар Ибрагимов", justify=tk.CENTER)
    lbl.pack(pady=10)

    btn_vk = tk.Button(top, text="ВК", command=lambda: webbrowser.open("https://vk.com/mr.crutch"))
    btn_vk.pack(side=tk.LEFT, padx=30)

    btn_tg = tk.Button(top, text="TG", command=lambda: webbrowser.open("https://t.me/God_SMM"))
    btn_tg.pack(side=tk.RIGHT, padx=30)

# Инициализация программы
root = tk.Tk()
root.title("Обработка стоп-слов")
root.geometry("1000x768")

# Создание фрейма для кнопок
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

btn_load = tk.Button(btn_frame, text="Загрузить файл", command=load_data)
btn_load.grid(row=0, column=0, padx=5, pady=5)

btn_save = tk.Button(btn_frame, text="Выгрузить файл", command=save_file)
btn_save.grid(row=0, column=1, padx=5, pady=5)

btn_save_stop_words = tk.Button(btn_frame, text="Сохранить стоп-слова", command=save_stop_words_to_file)
btn_save_stop_words.grid(row=0, column=2, padx=5, pady=5)

btn_load_stop_words = tk.Button(btn_frame, text="Загрузить стоп-слова", command=load_stop_words_from_file)
btn_load_stop_words.grid(row=0, column=3, padx=5, pady=5)

btn_show_stop_words = tk.Button(btn_frame, text="Просмотр стоп-слов", command=show_stop_words)
btn_show_stop_words.grid(row=0, column=4, padx=5, pady=5)

btn_undo = tk.Button(btn_frame, text="Назад", command=undo_last_action)
btn_undo.grid(row=0, column=5, padx=5, pady=5)

btn_sort = tk.Button(btn_frame, text="Сортировка", command=lambda: sort_menu.tk_popup(btn_sort.winfo_rootx(), btn_sort.winfo_rooty() + btn_sort.winfo_height()))
btn_sort.grid(row=0, column=6, padx=5, pady=5)

# Создание выпадающего меню для сортировки
sort_menu = tk.Menu(root, tearoff=0)
sort_menu.add_command(label="По алфавиту", command=sort_alphabetically)
sort_menu.add_command(label="Частотность", command=sort_by_statistics1)
sort_menu.add_command(label="\"!Частостность\"", command=sort_by_statistics2)
sort_menu.add_command(label="\"[!Частостность]\"", command=sort_by_statistics3)

# Создание Treeview с прокруткой
tree_frame = tk.Frame(root)
tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

columns = ("Фраза", "Частотность", "\"!Частостность\"", "\"[!Частостность]\"")  # Настройте в соответствии с вашими данными

tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

# Определение заголовков столбцов
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor='w')

# Добавление вертикальной прокрутки
vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side='right', fill='y')

# Добавление горизонтальной прокрутки
hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
tree.configure(xscrollcommand=hsb.set)
hsb.pack(side='bottom', fill='x')

tree.pack(fill='both', expand=True)

# Метка для отображения количества загруженных строк
count_label = tk.Label(root, text="Количество загруженных строк: 0")
count_label.pack(side='bottom', padx=10, pady=5)

# Функция для обработки двойного клика на строке
def on_double_click(event):
    item = tree.identify_row(event.y)
    if item:
        values = tree.item(item, "values")
        if values and values[0] != "Данные отсутствуют":
            open_word_selection(values[0])

tree.bind("<Double-1>", on_double_click)

# Кнопка для связи с автором
btn_contact = tk.Button(btn_frame, text="Связаться с автором", command=contact_author)
btn_contact.grid(row=0, column=7, padx=5, pady=5)

root.mainloop()
