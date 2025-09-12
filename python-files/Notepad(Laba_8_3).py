from tkinter import *
import tkinter as tk
from tkinter import simpledialog, messagebox, font, filedialog
from datetime import datetime
import subprocess
import os

root = Tk()
root.title('Блокнот')
root.geometry("900x600")

# -----Изначальные параметры шрифта-----
default_font_family = "Arial"
default_font_size = 12
current_font_family = default_font_family
current_font_size = default_font_size

# -----Глобальные переменные для настроек-----
wrap_enabled = False
status_enabled = True

# -----Строка состояния до текстового поля-----
status_bar = Frame(root, bd=1, relief=SUNKEN)

# -----Элементы строки состояния-----
line_label = Label(status_bar, text="Строка: 1", anchor=W, padx=5)
line_label.pack(side=LEFT)

col_label = Label(status_bar, text="Столбец: 1", anchor=W, padx=5)
col_label.pack(side=LEFT)

encoding_label = Label(status_bar, text="UTF-8", anchor=W, padx=5)
encoding_label.pack(side=LEFT)

windows_style_label = Label(status_bar, text="Windows (CRLF)", anchor=W, padx=5)
windows_style_label.pack(side=LEFT)

zoom_label = Label(status_bar, text="100%", anchor=E, padx=5)
zoom_label.pack(side=RIGHT)

scrollV = Scrollbar(root, orient=VERTICAL)
scrollV.pack(side=RIGHT, fill=Y)
scrollH = Scrollbar(root, orient=HORIZONTAL)
scrollH.pack(side=BOTTOM, fill=X)

text = Text(root, width=500, height=350, wrap=NONE, undo=True)
text.config(yscrollcommand=scrollV.set, xscrollcommand=scrollH.set)
text.pack(fill=BOTH, expand=1)

scrollV.config(command=text.yview)
scrollH.config(command=text.xview)

#=====Функции=====
# -----Функции для вкладки Файл-----
current_file = None
def new_window(event=None):
    file_path = r"D:\Кито-310 Федянов\интерфейсы\Notepad(Laba_8_3).py"
    if os.path.exists(file_path):
        try:
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                
                subprocess.Popen(
                    ['python', file_path],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть новое окно: {e}")
    else:
        messagebox.showerror("Ошибка", f"Файл не найден:\n{file_path}")

def open_file(event=None):
    try:
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            text.delete('1.0', END)
            text.insert('1.0', content)
            update_status()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

def save_file(event=None):
    global current_file
    if current_file:
        try:
            with open(current_file, 'w', encoding='utf-8') as file:
                text1 = text.get(1.0, tk.END)
                file.write(text1)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    else:
        save_as()

def save_as(event=None):
    global current_file
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    if filename:
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                text1 = text.get(1.0, tk.END)
                file.write(text1)
            current_file = filename
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def exit_app(event=None):
    root.destroy()

# -----Функции для вкладки Изменить-----
def undo(event=None):
    try:
        text.edit_undo()
    except TclError:
        pass
    update_status()

def cut(event=None):
    try:
        if text.tag_ranges("sel"):
            text.event_generate("<<Cut>>")
    except TclError:
        pass
    update_status()

def copy(event=None):
    try:
        if text.tag_ranges("sel"):
            text.event_generate("<<Copy>>")
    except TclError:
        pass

def paste(event=None):
    try:
        text.event_generate("<<Paste>>")
    except TclError:
        pass
    update_status()

def delete(event=None):
    try:
        text.delete("sel.first", "sel.last")
    except TclError:
        pass
    update_status()

search_start_index = "1.0"
last_search_text = ""

def find(event=None):
    global search_start_index, last_search_text
    needle = simpledialog.askstring("Найти", "Введите текст для поиска:")
    if needle:
        last_search_text = needle
        pos = text.search(needle, "1.0", END)
        if pos:
            end_pos = f"{pos}+{len(needle)}c"
            text.tag_remove('sel', '1.0', END)
            text.tag_add('sel', pos, end_pos)
            text.mark_set("insert", end_pos)
            text.see("insert")
            search_start_index = end_pos
            text.focus()
            update_status()
        else:
            messagebox.showinfo("Результаты поиска", f"'{needle}' не найдено.")

def find_next(event=None):
    global search_start_index, last_search_text
    if not last_search_text:
        find()
        return
    pos = text.search(last_search_text, search_start_index, END)
    if pos:
        end_pos = f"{pos}+{len(last_search_text)}c"
        text.tag_remove('sel', '1.0', END)
        text.tag_add('sel', pos, end_pos)
        text.mark_set("insert", end_pos)
        text.see("insert")
        search_start_index = end_pos
        text.focus()
        update_status()
    else:
        messagebox.showinfo("Результаты поиска", "Достигнут конец документа.")
        search_start_index = "1.0"

def find_previous(event=None):
    global search_start_index, last_search_text
    if not last_search_text:
        find()
        return
    pos = None
    idx = "1.0"
    while True:
        found = text.search(last_search_text, idx, search_start_index)
        if found == "":
            break
        pos = found
        idx = f"{found}+1c"
    if pos:
        end_pos = f"{pos}+{len(last_search_text)}c"
        text.tag_remove('sel', '1.0', END)
        text.tag_add('sel', pos, end_pos)
        text.mark_set("insert", pos)
        text.see("insert")
        search_start_index = pos
        text.focus()
        update_status()
    else:
        messagebox.showinfo("Результаты поиска", "Достигнуто начало документа.")
        search_start_index = END

def replace(event=None):
    needle = simpledialog.askstring("Заменить", "Текст для замены:")
    if needle is None:
        return
    replacement = simpledialog.askstring("Заменить", f"Заменить '{needle}' на:")
    if replacement is None:
        return

    pos = text.search(needle, "1.0", END)
    if pos:
        end_pos = f"{pos}+{len(needle)}c"
        text.delete(pos, end_pos)
        text.insert(pos, replacement)
        messagebox.showinfo("Замена", "Первое вхождение заменено")
        update_status()
    else:
        messagebox.showinfo("Замена", f"'{needle}' не найдено.")

def goto(event=None):
    line_num = simpledialog.askinteger("Перейти", "Введите номер строки:")
    if line_num is not None:
        max_index = text.index(END + "-1c").split(".")
        max_line = int(max_index[0])
        if 1 <= line_num <= max_line:
            text.mark_set("insert", f"{line_num}.0")
            text.see(f"{line_num}.0")
            text.focus()
            update_status()
        else:
            messagebox.showerror("Ошибка", "Номер строки вне диапазона")

def select_all(event=None):
    text.tag_add('sel', '1.0', END)
    update_status()

def insert_datetime(event=None):
    now = datetime.now().strftime("%H:%M %d.%m.%Y")
    text.insert("insert", now)
    update_status()

def choose_font(event=None):
    families = list(font.families())
    fam = simpledialog.askstring("Выбор шрифта", "Введите название шрифта (например Arial):", initialvalue="Arial")
    if fam not in families:
        messagebox.showwarning("Шрифт", "Шрифт не найден, будет использован шрифт по умолчанию")
        fam = "Arial"
    size = simpledialog.askinteger("Размер шрифта", "Введите размер шрифта:", initialvalue=12)
    if size is None:
        size = 12
    text.config(font=(fam, size))
    update_status()

def delete_all(event=None):
    text.delete("1.0", END)
    update_status()

# -----Функции для вкладки Просмотр-----
def zoom_in(event=None):
    global current_font_size
    current_font_size += 2
    text.config(font=(current_font_family, current_font_size))
    update_status()

def zoom_out(event=None):
    global current_font_size
    if current_font_size > 4:
        current_font_size -= 2
        text.config(font=(current_font_family, current_font_size))
        update_status()

def zoom_reset(event=None):
    global current_font_size, current_font_family
    current_font_size = default_font_size
    current_font_family = default_font_family
    text.config(font=(current_font_family, current_font_size))
    update_status()

def update_status(event=None):
    if status_enabled:
        try:
            index = text.index("insert")
            line, col = index.split('.')
            line_label.config(text=f"Строка: {line}")
            col_label.config(text=f"Столбец: {int(col)+1}")
            zoom_percent = int((current_font_size / default_font_size) * 100)
            zoom_label.config(text=f"{zoom_percent}%")
        except Exception as e:
            pass

def toggle_status_bar():
    global status_enabled
    status_enabled = not status_enabled
    
    if status_enabled:
        status_bar.pack(side=BOTTOM, fill=X, before=scrollH)
    else:
        status_bar.pack_forget()
    wrap1_var.set(1 if status_enabled else 0)
    update_status()

def toggle_word_wrap(event=None):
    global wrap_enabled
    if wrap_enabled:
        text.config(wrap=NONE)
        wrap_enabled = False
    else:
        text.config(wrap=WORD)
        wrap_enabled = True
    wrap_var.set(1 if wrap_enabled else 0)

# =====Бинды=====
# Файл
root.bind('<Control-n>', new_window)
root.bind('<Control-N>', new_window)
root.bind('<Control-o>', open_file)
root.bind('<Control-O>', open_file)
root.bind('<Control-s>', save_file)
root.bind('<Control-S>', save_file)
root.bind('<Control-Shift-S>', save_as)
root.bind('<Control-Shift-s>', save_as)
# Правка
root.bind('<Control-z>', undo)
root.bind('<Control-Z>', undo)
root.bind('<Control-x>', cut)
root.bind('<Control-X>', cut)
root.bind('<Control-c>', copy)
root.bind('<Control-C>', copy)
root.bind('<Control-b>', paste)
root.bind('<Control-B>', paste)
root.bind('<Delete>', delete)
root.bind('<Control-f>', find)
root.bind('<Control-F>', find)
root.bind('<F3>', find_next)
root.bind('<Shift-F3>', find_previous)
root.bind('<Control-h>', replace)
root.bind('<Control-H>', replace)
root.bind('<Control-g>', goto)
root.bind('<Control-G>', goto)
root.bind('<Control-a>', select_all)
root.bind('<Control-A>', select_all)
root.bind('<F5>', insert_datetime)
root.bind_all('<Control-equal>', zoom_in)
root.bind_all('<Control-plus>', zoom_in)
root.bind_all('<Control-minus>', zoom_out)
root.bind_all('<Control-0>', zoom_reset)
root.bind_all('<Escape>',exit_app)
# Привязка событий для обновления статуса
text.bind('<KeyRelease>', update_status)
text.bind('<ButtonRelease-1>', update_status)
text.bind('<Motion>', update_status)

#=====Меню=====
mainmenu = Menu(root)
root.config(menu=mainmenu)
#-----Файл-----
filemenu = Menu(mainmenu, tearoff=0)
filemenu.add_command(label='Новое окно', command=new_window, accelerator="Ctrl+N")
filemenu.add_command(label='Открыть', command=open_file, accelerator="Ctrl+O")
filemenu.add_command(label='Сохранить', command=save_file, accelerator="Ctrl+S")
filemenu.add_command(label='Сохранить как', command=save_as, accelerator="Ctrl+Shift+S")
filemenu.add_separator()
filemenu.add_command(label='Выйти', command=exit_app)
mainmenu.add_cascade(label='Файл', menu=filemenu)
#-----Изменить-----
editmenu = Menu(mainmenu, tearoff=0)
editmenu.add_command(label='Отменить', command=undo, accelerator="Ctrl+Z")
editmenu.add_separator()
editmenu.add_command(label='Вырезать', command=cut, accelerator="Ctrl+X")
editmenu.add_command(label='Копировать', command=copy, accelerator="Ctrl+C")
editmenu.add_command(label='Вставить', command=paste, accelerator="Ctrl+B")
editmenu.add_command(label='Удалить', command=delete, accelerator="Del")
editmenu.add_separator()
editmenu.add_command(label='Найти', command=find, accelerator="Ctrl+F")
editmenu.add_command(label='Найти далее', command=find_next, accelerator="F3")
editmenu.add_command(label='Найти ранее', command=find_previous, accelerator="Shift+F3")
editmenu.add_command(label='Заменить', command=replace, accelerator="Ctrl+H")
editmenu.add_command(label='Перейти', command=goto, accelerator="Ctrl+G")
editmenu.add_separator()
editmenu.add_command(label='Выбрать все', command=select_all, accelerator="Ctrl+A")
editmenu.add_command(label='Время и дата', command=insert_datetime, accelerator="F5")
editmenu.add_separator()
editmenu.add_command(label='Шрифт', command=choose_font)
mainmenu.add_cascade(label='Изменить', menu=editmenu)
#-----Просмотр-----
viewmenu = Menu(mainmenu, tearoff=0)
zoommenu = Menu(viewmenu, tearoff=0)
zoommenu.add_command(label='Увеличить', command=zoom_in, accelerator="Ctrl+Плюс")
zoommenu.add_command(label='Уменьшить', command=zoom_out, accelerator="Ctrl+Минус")
zoommenu.add_command(label='Восстановить масштаб по умолчанию', command=zoom_reset, accelerator="Ctrl+0")
viewmenu.add_cascade(label='Масштаб', menu=zoommenu)
viewmenu.add_separator()
wrap1_var = IntVar(value=1)
wrap_var = IntVar(value=0)
viewmenu.add_checkbutton(label='Строка состояния', variable=wrap1_var, 
                        command=toggle_status_bar, onvalue=1, offvalue=0)
viewmenu.add_checkbutton(label='Перенос по словам', variable=wrap_var, 
                        command=toggle_word_wrap, onvalue=1, offvalue=0)
mainmenu.add_cascade(label='Просмотр', menu=viewmenu)
status_bar.pack(side=BOTTOM, fill=X, before=scrollH)
update_status()

root.mainloop()
