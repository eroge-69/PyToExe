from tkinter import *
from tkinter import filedialog, messagebox

def main():
    root = Tk()
    root.title('Блокнот')
    root.geometry('600x400')

    current_file = None
    text_changed = False

    # Добавляем полосы прокрутки
    scrollV = Scrollbar(root, orient=VERTICAL)
    scrollV.pack(side=RIGHT, fill=Y)
    scrollH = Scrollbar(root, orient=HORIZONTAL)
    scrollH.pack(side=BOTTOM, fill=X)

    # Создаем текстовый виджет с поддержкой undo
    text = Text(root, width=500, height=350, wrap=NONE, undo=True)
    text.config(yscrollcommand=scrollV.set, xscrollcommand=scrollH.set)
    text.pack(fill=BOTH, expand=1)

    # Привязываем полосы прокрутки к виджету
    scrollV.config(command=text.yview)
    scrollH.config(command=text.xview)

    # Строка состояния
    status_bar = Label(root, text="Строка: 1 | Столбец: 0 | Символов: 0", anchor=E)
    status_bar.pack(side=BOTTOM, fill=X)

    def ask_save_changes():
        answer = messagebox.askyesnocancel("Сохранить изменения", "Сохранить изменения перед выходом?")
        if answer is None:  # Отмена
            return False
        if answer:  # Да
            return save_file()
        return True  # Нет

    def new_file():
        nonlocal current_file, text_changed
        if text_changed and not ask_save_changes():
            return
        text.delete(1.0, END)
        current_file = None
        text_changed = False
        root.title("Блокнот")
        update_status()

    def open_file():
        nonlocal current_file, text_changed
        if text_changed and not ask_save_changes():
            return
        file = filedialog.askopenfilename(defaultextension=".txt",
                                          filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if file:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    text.delete(1.0, END)
                    text.insert(END, f.read())
                current_file = file
                text_changed = False
                root.title(f"Блокнот - {file}")
                update_status()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_file():
        nonlocal current_file, text_changed
        try:
            if not current_file:
                return save_as_file()
            with open(current_file, "w", encoding="utf-8") as f:
                f.write(text.get(1.0, END))
            text_changed = False
            update_status()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
            return False

    def save_as_file():
        nonlocal current_file, text_changed
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if file:
            try:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(text.get(1.0, END))
                current_file = file
                text_changed = False
                root.title(f"Блокнот - {file}")
                update_status()
                return True
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
        return False

    def exit_app():
        if text_changed and not ask_save_changes():
            return
        root.destroy()

    def undo():
        try:
            text.edit_undo()
        except TclError:
            pass

    def cut():
        copy()
        delete()

    def copy():
        try:
            selection = text.get(SEL_FIRST, SEL_LAST)
            root.clipboard_clear()
            root.clipboard_append(selection)
        except TclError:
            pass

    def paste():
        try:
            clipboard = root.clipboard_get()
            text.insert(INSERT, clipboard)
        except TclError:
            pass

    def delete():
        try:
            text.delete(SEL_FIRST, SEL_LAST)
        except TclError:
            pass

    def select_all():
        text.tag_add(SEL, "1.0", END)
        text.mark_set(INSERT, "1.0")
        text.see(INSERT)

    def toggle_status_bar():
        if show_status.get():
            status_bar.pack(side=BOTTOM, fill=X)
        else:
            status_bar.pack_forget()

    def update_status(event=None):
        nonlocal text_changed
        if event and event.type == "2":  # KeyPress event type
            text_changed = True
        line, col = text.index(INSERT).split('.')
        chars = len(text.get(1.0, END)) - 1
        status_bar.config(text=f"Строка: {line} | Столбец: {int(col)+1} | Символов: {chars}")

    # Меню
    mainmenu = Menu(root)
    root.config(menu=mainmenu)

    file_menu = Menu(mainmenu, tearoff=0)
    mainmenu.add_cascade(label="Файл", menu=file_menu)
    file_menu.add_command(label="Создать", command=new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Открыть", command=open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Сохранить", command=save_file, accelerator="Ctrl+S")
    file_menu.add_command(label="Сохранить как", command=save_as_file)
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=exit_app)

    edit_menu = Menu(mainmenu, tearoff=0)
    mainmenu.add_cascade(label="Изменить", menu=edit_menu)
    edit_menu.add_command(label="Отменить", command=undo, accelerator="Ctrl+Z")
    edit_menu.add_separator()
    edit_menu.add_command(label="Вырезать", command=cut, accelerator="Ctrl+X")
    edit_menu.add_command(label="Копировать", command=copy, accelerator="Ctrl+C")
    edit_menu.add_command(label="Вставить", command=paste, accelerator="Ctrl+V")
    edit_menu.add_command(label="Удалить", command=delete, accelerator="Del")
    edit_menu.add_separator()
    edit_menu.add_command(label="Выделить всё", command=select_all, accelerator="Ctrl+A")

    view_menu = Menu(mainmenu, tearoff=0)
    mainmenu.add_cascade(label="Просмотр", menu=view_menu)
    show_status = BooleanVar(value=True)
    view_menu.add_checkbutton(label="Строка состояния", variable=show_status, command=toggle_status_bar)

    # Горячие клавиши
    root.bind("<Control-n>", lambda e: new_file())
    root.bind("<Control-o>", lambda e: open_file())
    root.bind("<Control-s>", lambda e: save_file())
    root.bind("<Control-z>", lambda e: undo())
    root.bind("<Control-x>", lambda e: cut())
    root.bind("<Control-c>", lambda e: copy())
    root.bind("<Control-v>", lambda e: paste())
    root.bind("<Delete>", lambda e: delete())
    root.bind("<Control-a>", lambda e: select_all())

    root.mainloop()

if __name__ == '__main__':
    main()