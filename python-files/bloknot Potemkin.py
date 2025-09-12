
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Блокнот")
        self.root.geometry("800x600")

        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True, font=("Helvetica", 12))
        self.text_area.pack(expand=True, fill='both')


        self.status_var = tk.StringVar()
        self.status_var.set("Строка 1, Столбец 1")

        self.status_bar = tk.Label(self.root, textvariable=self.status_var, anchor='w', relief=tk.SUNKEN, bd=1, font=("Helvetica", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.show_status_bar = tk.BooleanVar(value=True)

   
        self.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.text_area.bind("<ButtonRelease>", self.update_status_bar)


        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        Izmenit_menu = tk.Menu(menubar, tearoff=0)
        Prosmotr_menu = tk.Menu(menubar, tearoff=0)

        # Новая вкладка
        file_menu.add_command(label="Новая вкладка", accelerator="Ctrl+N", command=self.new_tab)
        # Новое окно
        file_menu.add_command(label="Новое окно", accelerator="Ctrl+Shift+N", command=self.new_window)
        # Открыть
        file_menu.add_command(label="Открыть", accelerator="Ctrl+O", command=self.open_file)
        # Что нового 
        new_features_menu = tk.Menu(file_menu, tearoff=0)
        new_features_menu.add_command(label="Версия 1.0 - базовый блокнот")
        new_features_menu.add_command(label="Версия 1.1 - добавлены вкладки")
        file_menu.add_cascade(label="Что нового", menu=new_features_menu)
        # Сохранить
        file_menu.add_command(label="Сохранить", accelerator="Ctrl+S", command=self.save_file)
        # Сохранить как
        file_menu.add_command(label="Сохранить как", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        # Сохранить все 
        file_menu.add_command(label="Сохранить все", accelerator="Ctrl+Alt+S", command=self.save_all)
        # Параметры страницы
        file_menu.add_command(label="Параметры страницы", command=self.page_setup)
        # Печать
        file_menu.add_command(label="Печать", accelerator="Ctrl+P", command=self.print_file)
        # Разделитель
        file_menu.add_separator()
        # Закрыть вкладку
        file_menu.add_command(label="Закрыть вкладку", accelerator="Ctrl+W", command=self.close_tab)
        # Закрыть окно
        file_menu.add_command(label="Закрыть окно", accelerator="Ctrl+Shift+W", command=self.close_window)
        # Выйти
        file_menu.add_command(label="Выйти", command=self.exit_app)  
        # Отменить
        Izmenit_menu.add_command(label="Отменить", accelerator="Ctrl+Z", command=self.Otmena)
        # Разделитель
        Izmenit_menu.add_separator()
        # Вырезать
        Izmenit_menu.add_command(label="Вырезать", accelerator="Ctrl+X", command=self.Virezat)
        # Копировать
        Izmenit_menu.add_command(label="Копировать", accelerator="Ctrl+C", command=self.Copyy)
        # Вставить
        Izmenit_menu.add_command(label="Вставить", accelerator="Ctrl+V", command=self.Vstavit)
        # Удалить
        Izmenit_menu.add_command(label="Удалить", accelerator="DEL", command=self.Deletee)
        # Разделитель
        Izmenit_menu.add_separator()
        # Поиск с помощью Bing
        Izmenit_menu.add_command(label="Поиск с помощью Bing", accelerator="Ctrl+E", command=self.Bingg)
        # Разделитель
        Izmenit_menu.add_separator()        
        # Найти
        Izmenit_menu.add_command(label="Найти", accelerator="Ctrl+F", command=self.Naiti)
        # Найти далее
        Izmenit_menu.add_command(label="Найти далее", accelerator="F3", command=self.NaitiDalee)        
        # Найти ранее
        Izmenit_menu.add_command(label="Найти ранее", accelerator="Shift+F3", command=self.NaitiRanee)
        # Заменить
        Izmenit_menu.add_command(label="Заменить", accelerator="Ctrl+H", command=self.Zamenit)
        # Перейти
        Izmenit_menu.add_command(label="Перейти", accelerator="Ctrl+G", command=self.Pereiti)
        # Разделитель
        Izmenit_menu.add_separator()  
        # Выбрать все
        Izmenit_menu.add_command(label="Выбрать все", accelerator="Ctrl+A", command=self.VibratVse)
        # Время и дата
        Izmenit_menu.add_command(label="Время и дата", accelerator="F5", command=self.Vremya_data)
        # Шрифт
        Izmenit_menu.add_command(label="Шрифт", command=self.Shrift)        

        # Масштаб
        Mashtab_menu = tk.Menu(Prosmotr_menu, tearoff=0)
        Mashtab_menu.add_command(label="Увеличить", command=self.increase_font_size)
        Mashtab_menu.add_command(label="Уменьшить", command=self.decrease_font_size)
        Prosmotr_menu.add_cascade(label="Масштаб", menu=Mashtab_menu)

        Prosmotr_menu.add_checkbutton(label="Строка состояния", onvalue=True, offvalue=False,
                                      variable=self.show_status_bar, command=self.toggle_status_bar)

        # Перенос по словам
        Prosmotr_menu.add_command(label="Перенос по словам", command=self.toggle_word_wrap)

        menubar.add_cascade(label="Файл", accelerator="Ctrl+плюс", menu=file_menu)
        menubar.add_cascade(label="Изменить", menu=Izmenit_menu)
        menubar.add_cascade(label="Просмотр", menu=Prosmotr_menu)

        self.root.config(menu=menubar)

        self.current_file = None
        self.font_size = 12

        self.root.bind_all("<Control-n>", lambda event: self.new_tab())
        self.root.bind_all("<Control-N>", lambda event: self.new_tab())
        self.root.bind_all("<Control-Shift-N>", lambda event: self.new_window())
        self.root.bind_all("<Control-o>", lambda event: self.open_file())
        self.root.bind_all("<Control-O>", lambda event: self.open_file())
        self.root.bind_all("<Control-s>", lambda event: self.save_file())
        self.root.bind_all("<Control-S>", lambda event: self.save_file())
        self.root.bind_all("<Control-Shift-S>", lambda event: self.save_file_as())
        self.root.bind_all("<Control-Alt-s>", lambda event: self.save_all())
        self.root.bind_all("<Control-p>", lambda event: self.print_file())
        self.root.bind_all("<Control-P>", lambda event: self.print_file())
        self.root.bind_all("<Control-w>", lambda event: self.close_tab())
        self.root.bind_all("<Control-W>", lambda event: self.close_tab())
        self.root.bind_all("<Control-Shift-W>", lambda event: self.close_window())
        
        self.root.bind_all("<Control-Z>", lambda event: self.Otmena())
        self.root.bind_all("<Control-X>", lambda event: self.Virezat())
        self.root.bind_all("<Control-C>", lambda event: self.Copyy())
        self.root.bind_all("<Control-V>", lambda event: self.Vstavit())
        self.root.bind_all("<Control-E>", lambda event: self.Bingg())
        self.root.bind_all("<Control-F>", lambda event: self.Naiti())
        self.root.bind_all("<F3>", lambda event: self.NaitiDalee())
        self.root.bind_all("<Shift-F3>", lambda event: self.NaitiRanee())
        self.root.bind_all("<Control-H>", lambda event: self.Zamenit())
        self.root.bind_all("<Control-G>", lambda event: self.Pereiti())
        self.root.bind_all("<Control-A>", lambda event: self.VibratVse())
        self.root.bind_all("<F5>", lambda event: self.Vremya_data())

    def new_tab(self):
        if messagebox.askyesno("Новая вкладка", "Сохранить текущие изменения перед созданием новой вкладки?"):
            self.save_file()
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Блокнот - Новая вкладка")

    def new_window(self):
        import subprocess
        import sys
        subprocess.Popen([sys.executable, __file__])

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
            self.current_file = file_path
            self.root.title(f"Блокнот - {os.path.basename(file_path)}")

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
            messagebox.showinfo("Сохранено", "Файл сохранён!")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.current_file = file_path
            self.root.title(f"Блокнот - {os.path.basename(file_path)}")

    def save_all(self):
        self.save_file()

    def page_setup(self):
        messagebox.showinfo("Параметры страницы", "Недоступно в вашем регионе.")

    def print_file(self):
        messagebox.showinfo("Печать", "Оформите подписку Блокнот+ чтобы пользоваться всеми функциями приложения.")

    def close_tab(self):
        if messagebox.askyesno("Закрыть вкладку", "Сохранить изменения перед закрытием вкладки?"):
            self.save_file()
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Блокнот")

    def close_window(self):
        if messagebox.askyesno("Закрыть окно", "Сохранить изменения перед закрытием окна?"):
            self.save_file()
        self.root.destroy()

    def exit_app(self):
        if messagebox.askyesno("Выход", "Сохранить изменения перед выходом?"):
            self.save_file()
        self.root.destroy()

    def Otmena(self, event=None):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def Virezat(self, event=None):
        self.text_area.event_generate("<<Cut>>")

    def Copyy(self, event=None):
        self.text_area.event_generate("<<Copy>>")

    def Vstavit(self, event=None):
        self.text_area.event_generate("<<Paste>>")

    def Deletee(self, event=None):
        try:
            sel = self.text_area.tag_ranges(tk.SEL)
            if sel:
                self.text_area.delete(*sel)
        except tk.TclError:
            pass


    def Bingg(self, event=None):
        import webbrowser
        try:
            selected_text = self.text_area.selection_get()
            query = selected_text.replace(' ', '+')
            url = f"https://www.bing.com/search?q={query}"
            webbrowser.open(url)
        except tk.TclError:
            messagebox.showerror("Ошибка", "Выделите текст для поиска.")

    def Naiti(self, event=None):
        from tkinter.simpledialog import askstring
        search_term = askstring("Найти", "Введите текст для поиска:")
        if search_term:
            start_pos = self.text_area.search(search_term, "1.0", tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text_area.tag_add(tk.SEL, start_pos, end_pos)
                self.text_area.mark_set(tk.INSERT, end_pos)
                self.text_area.see(start_pos)
            else:
                messagebox.showinfo("Не найдено", f"Текст '{search_term}' не найден.")

    def NaitiDalee(self, event=None):
        try:
            search_term = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            start_pos = self.text_area.index(tk.INSERT)
            pos = self.text_area.search(search_term, start_pos, tk.END)
            if pos:
                end_pos = f"{pos}+{len(search_term)}c"
                self.text_area.tag_add(tk.SEL, pos, end_pos)
                self.text_area.mark_set(tk.INSERT, end_pos)
                self.text_area.see(pos)
            else:
                messagebox.showinfo("Не найдено", f"Текст '{search_term}' не найден далее.")
        except tk.TclError:
            messagebox.showerror("Ошибка", "Сначала найдите текст.")

    def NaitiRanee(self, event=None):
        try:
            search_term = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            start_pos = self.text_area.index(tk.INSERT)
            pos = self.text_area.search(search_term, "1.0", start_pos, backwards=True)
            if pos:
                end_pos = f"{pos}+{len(search_term)}c"
                self.text_area.tag_add(tk.SEL, pos, end_pos)
                self.text_area.mark_set(tk.INSERT, end_pos)
                self.text_area.see(pos)
            else:
                messagebox.showinfo("Не найдено", f"Текст '{search_term}' не найден ранее.")
        except tk.TclError:
            messagebox.showerror("Ошибка", "Сначала найдите текст.")

    def Zamenit(self, event=None):
        from tkinter.simpledialog import askstring
        search_term = askstring("Заменить", "Введите текст для замены:")
        if search_term:
            replace_term = askstring("Заменить", "Введите новый текст:")
            if replace_term is not None:
                content = self.text_area.get(1.0, tk.END)
                new_content = content.replace(search_term, replace_term)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, new_content)

    def Pereiti(self, event=None):
        from tkinter.simpledialog import askinteger
        line_num = askinteger("Перейти", "Введите номер строки:")
        if line_num:
            self.text_area.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_area.see(f"{line_num}.0")

    def VibratVse(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, tk.END)

    def Vremya_data(self, event=None):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M %d/%m/%Y")
        self.text_area.insert(tk.INSERT, now)

    def Shrift(self, event=None):
        from tkinter import font
        font_window = tk.Toplevel(self.root)
        font_window.title("Шрифт")
        font_window.geometry("300x200")

        fonts = list(font.families())
        font_var = tk.StringVar(value=self.text_area.cget("font").split()[0])
        font_list = tk.Listbox(font_window, listvariable=tk.Variable(value=fonts))
        font_list.pack(fill=tk.BOTH, expand=True)

        def apply_font():
            selected_font = font_list.get(tk.ACTIVE)
            if selected_font:
                current_font = self.text_area.cget("font")
                new_font = (selected_font, self.font_size)
                self.text_area.config(font=new_font)
            font_window.destroy()

        apply_button = tk.Button(font_window, text="Применить", command=apply_font)
        apply_button.pack()

    def increase_font_size(self):
        self.font_size += 2
        current_font = self.text_area.cget("font")
        family = current_font.split()[0]
        self.text_area.config(font=(family, self.font_size))

    def decrease_font_size(self):
        if self.font_size > 2:
            self.font_size -= 2
            current_font = self.text_area.cget("font")
            family = current_font.split()[0]
            self.text_area.config(font=(family, self.font_size))

    def toggle_status_bar(self):
        if self.show_status_bar.get():
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.status_bar.pack_forget()
        self.update_status_bar()

    def update_status_bar(self, event=None):
        if self.show_status_bar.get():
            cursor_pos = self.text_area.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.status_var.set(f"Строка {line}, Столбец {int(col) + 1}")

    def toggle_word_wrap(self):
        current_wrap = self.text_area.cget("wrap")
        if current_wrap == tk.WORD:
            self.text_area.config(wrap=tk.NONE)
        else:
            self.text_area.config(wrap=tk.WORD)

if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadApp(root)
    root.mainloop()

