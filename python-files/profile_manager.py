import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Listbox, Scrollbar, Frame
from tkinter import ttk
import pickle
import os

# Цветовая схема
DARK_BG = "#121212"
DARK_FG = "#e0e0e0"
ACCENT_COLOR = "#4e9a06"
BUTTON_BG = "#333333"
BUTTON_ACTIVE = "#555555"
ENTRY_BG = "#252525"
LISTBOX_BG = "#252525"
LISTBOX_FG = "#ffffff"
SCROLLBAR_BG = "#454545"
TAB_BG = "#1e1e1e"

class Profile:
    def __init__(self, profile_id, nickname):
        self.profile_id = profile_id
        self.nickname = nickname
        self.history = {}

    def add_history_entry(self, tab_name, entry):
        if tab_name not in self.history:
            self.history[tab_name] = []
        self.history[tab_name].append(entry)

    def edit_history_entry(self, tab_name, index, new_entry):
        if tab_name in self.history and 0 <= index < len(self.history[tab_name]):
            self.history[tab_name][index] = new_entry
            
    def delete_history_entry(self, tab_name, index):
        if tab_name in self.history and 0 <= index < len(self.history[tab_name]):
            del self.history[tab_name][index]
            return True
        return False
            
    def delete_tab(self, tab_name):
        if tab_name in self.history:
            del self.history[tab_name]
            return True
        return False
            
    def rename_tab(self, old_name, new_name):
        if old_name in self.history and new_name not in self.history:
            self.history[new_name] = self.history.pop(old_name)
            return True
        return False

    def __str__(self):
        return f"{self.nickname} (ID: {self.profile_id})"

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=DARK_BG)
        
        self.result = None
        
        tk.Label(self, text=prompt, bg=DARK_BG, fg=DARK_FG).pack(pady=5)
        
        self.entry = ttk.Entry(
            self,
            style='TEntry',
            font=('Segoe UI', 10)
        )
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        self.entry.focus_set()
        
        button_frame = tk.Frame(self, bg=DARK_BG)
        button_frame.pack(pady=10)
        
        ok_button = self.create_rounded_button(button_frame, "OK", self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = self.create_rounded_button(button_frame, "Отмена", self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        self.geometry("300x150")
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def create_rounded_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=BUTTON_BG,
            fg=DARK_FG,
            activebackground=BUTTON_ACTIVE,
            activeforeground=DARK_FG,
            relief='flat',
            borderwidth=0,
            font=('Segoe UI', 10),
            padx=15,
            pady=5,
            highlightthickness=0
        )
        return btn
    
    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()
    
    def on_cancel(self):
        self.destroy()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("История персонала")
        self.profiles = {}
        self.selected_profile = None
        self.last_click_time = 0
        
        # Настройка стилей
        self.setup_styles()
        root.configure(bg=DARK_BG)
        
        # Создание интерфейса
        self.create_widgets()
        self.load_profiles()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Общие настройки
        style.configure('.', background=DARK_BG, foreground=DARK_FG)
        style.configure('TFrame', background=DARK_BG)
        style.configure('TNotebook', background=DARK_BG, borderwidth=0)
        style.configure('TNotebook.Tab', 
                      background=TAB_BG, 
                      foreground=DARK_FG,
                      padding=[10, 5], 
                      font=('Segoe UI', 9),
                      borderwidth=0)
        style.map('TNotebook.Tab', 
                background=[('selected', ACCENT_COLOR)],
                foreground=[('selected', '#ffffff')])
        
        # Настройка Entry
        style.configure('TEntry', 
                       fieldbackground=ENTRY_BG,
                       foreground=DARK_FG,
                       insertcolor=DARK_FG,
                       bordercolor=ACCENT_COLOR,
                       lightcolor=ACCENT_COLOR,
                       darkcolor=ACCENT_COLOR)

    def create_widgets(self):
        # Основные фреймы
        self.frame_left = Frame(self.root, bg=DARK_BG)
        self.frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.frame_right = Frame(self.root, bg=DARK_BG)
        self.frame_right.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Поле поиска
        self.search_entry = ttk.Entry(
            self.frame_left,
            style='TEntry',
            font=('Segoe UI', 10)
        )
        self.search_entry.pack(pady=5, fill=tk.X, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_profile_list)

        # Список профилей
        self.profile_listbox = Listbox(
            self.frame_left,
            bg=LISTBOX_BG,
            fg=LISTBOX_FG,
            selectbackground=ACCENT_COLOR,
            selectforeground='white',
            relief='flat',
            font=('Segoe UI', 10),
            highlightthickness=0,
            borderwidth=0
        )
        self.profile_listbox.pack(pady=5, fill=tk.BOTH, expand=True, padx=5)
        self.profile_listbox.bind('<Button-1>', self.on_profile_click)
        self.profile_listbox.bind('<Double-Button-1>', self.on_profile_double_click)

        # Скроллбар для списка
        self.scrollbar = Scrollbar(
            self.frame_left,
            bg=SCROLLBAR_BG,
            activebackground=BUTTON_ACTIVE,
            troughcolor=DARK_BG,
            borderwidth=0,
            relief='flat'
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.profile_listbox.yview)

        # Кнопки с закругленными краями
        self.button_add_profile = self.create_rounded_button(
            self.frame_right, "Добавить участника", self.add_profile)
        self.button_add_profile.pack(pady=10, fill=tk.X, padx=5)

        self.button_edit_profile = self.create_rounded_button(
            self.frame_right, "Редактировать профиль", self.edit_profile)
        self.button_edit_profile.pack(pady=10, fill=tk.X, padx=5)

        self.button_delete_profile = self.create_rounded_button(
            self.frame_right, "Удалить участника", self.delete_profile)
        self.button_delete_profile.pack(pady=10, fill=tk.X, padx=5)

    def create_rounded_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=BUTTON_BG,
            fg=DARK_FG,
            activebackground=BUTTON_ACTIVE,
            activeforeground=DARK_FG,
            relief='flat',
            borderwidth=0,
            font=('Segoe UI', 10, 'bold'),
            padx=15,
            pady=8,
            highlightthickness=0
        )
        btn.config(borderwidth=0, highlightbackground=ACCENT_COLOR, highlightcolor=ACCENT_COLOR)
        return btn

    def load_profiles(self):
        if os.path.exists("profiles.pkl"):
            with open("profiles.pkl", "rb") as f:
                self.profiles = pickle.load(f)
                self.update_profile_list()

    def save_profiles(self):
        with open("profiles.pkl", "wb") as f:
            pickle.dump(self.profiles, f)

    def update_profile_list(self, event=None):
        self.profile_listbox.delete(0, tk.END)
        search_term = self.search_entry.get().lower()
        for profile in self.profiles.values():
            if search_term in profile.nickname.lower() or search_term in profile.profile_id.lower():
                self.profile_listbox.insert(tk.END, profile)

    def on_profile_click(self, event):
        current_time = event.time
        if current_time - self.last_click_time < 300:  # 300ms для двойного клика
            return
        self.last_click_time = current_time
        
        # Выделение профиля при одинарном клике
        index = self.profile_listbox.nearest(event.y)
        if index >= 0:
            self.profile_listbox.selection_clear(0, tk.END)
            self.profile_listbox.selection_set(index)
            self.selected_profile = list(self.profiles.values())[index]

    def on_profile_double_click(self, event):
        index = self.profile_listbox.nearest(event.y)
        if index >= 0:
            self.selected_profile = list(self.profiles.values())[index]
            self.open_profile(self.selected_profile)

    def add_profile(self):
        # Создаем окно регистрации
        reg_window = Toplevel(self.root)
        reg_window.title("Регистрация")
        reg_window.geometry("400x200")
        reg_window.configure(bg=DARK_BG)
        
        # Поле для DISCORD ника
        tk.Label(reg_window, text="DISCORD ник:", bg=DARK_BG, fg=DARK_FG).pack(pady=5)
        nick_entry = ttk.Entry(reg_window, style='TEntry', font=('Segoe UI', 10))
        nick_entry.pack(pady=5, fill=tk.X, padx=20)
        nick_entry.focus_set()
        
        # Поле для ID
        tk.Label(reg_window, text="ID:", bg=DARK_BG, fg=DARK_FG).pack()
        id_entry = ttk.Entry(reg_window, style='TEntry', font=('Segoe UI', 10))
        id_entry.pack(pady=5, fill=tk.X, padx=20)
        
        # Функция обработки ввода
        def process_input():
            nickname = nick_entry.get()
            profile_id = id_entry.get()
            
            if not nickname:
                messagebox.showerror("Ошибка", "Ник не может быть пустым!", parent=reg_window)
                return
                
            if not profile_id:
                messagebox.showerror("Ошибка", "ID не может быть пустым!", parent=reg_window)
                return
                
            if profile_id in self.profiles:
                messagebox.showerror("Ошибка", "ID уже существует!", parent=reg_window)
                return
                
            self.profiles[profile_id] = Profile(profile_id, nickname)
            messagebox.showinfo("Успех", "Профиль успешно создан!", parent=reg_window)
            self.update_profile_list()
            self.save_profiles()
            reg_window.destroy()
        
        # Кнопка регистрации
        reg_button = self.create_rounded_button(reg_window, "Зарегистрировать", process_input)
        reg_button.pack(pady=10)
        
        # Центрируем окно
        reg_window.transient(self.root)
        reg_window.grab_set()
        reg_window.wait_window()

    def edit_profile(self):
        if self.selected_profile:
            # Создаем окно редактирования
            edit_window = Toplevel(self.root)
            edit_window.title("Редактирование профиля")
            edit_window.geometry("400x200")
            edit_window.configure(bg=DARK_BG)
            
            # Старый ID (не редактируемый)
            tk.Label(edit_window, text=f"Текущий ник: {self.selected_profile.nickname}", 
                   bg=DARK_BG, fg=DARK_FG).pack(pady=5)
            tk.Label(edit_window, text=f"Текущий ID: {self.selected_profile.profile_id}", 
                   bg=DARK_BG, fg=DARK_FG).pack(pady=5)
            
            # Новый ник
            tk.Label(edit_window, text="Новый ник:", bg=DARK_BG, fg=DARK_FG).pack()
            new_nick_entry = ttk.Entry(edit_window, style='TEntry', font=('Segoe UI', 10))
            new_nick_entry.insert(0, self.selected_profile.nickname)
            new_nick_entry.pack(pady=5, fill=tk.X, padx=20)

            # Новый ID
            tk.Label(edit_window, text="Новый ID:", bg=DARK_BG, fg=DARK_FG).pack()
            new_id_entry = ttk.Entry(edit_window, style='TEntry', font=('Segoe UI', 10))
            new_id_entry.pack(pady=5, fill=tk.X, padx=20)
            
            # Кнопка сохранения
            def save_changes():
                new_id = new_id_entry.get()
                new_nick = new_nick_entry.get()
                
                if not new_nick:
                    messagebox.showerror("Ошибка", "Ник не может быть пустым!", parent=edit_window)
                    return
                
                # Если ID изменился
                if new_id and new_id != self.selected_profile.profile_id:
                    if new_id in self.profiles:
                        messagebox.showerror("Ошибка", "Этот ID уже занят!", parent=edit_window)
                        return
                    
                    # Обновляем ID
                    profile = self.profiles.pop(self.selected_profile.profile_id)
                    profile.profile_id = new_id
                    profile.nickname = new_nick
                    self.profiles[new_id] = profile
                    self.selected_profile = profile
                else:
                    # Только меняем ник
                    self.selected_profile.nickname = new_nick
                
                self.update_profile_list()
                self.save_profiles()
                messagebox.showinfo("Успех", "Профиль обновлен!", parent=edit_window)
                edit_window.destroy()
            
            save_btn = self.create_rounded_button(edit_window, "Сохранить", save_changes)
            save_btn.pack(pady=10)
            
        else:
            messagebox.showerror("Ошибка", "Профиль не выбран!")

    def delete_profile(self):
        if self.selected_profile:
            confirm = messagebox.askyesno(
                "Подтверждение",
                f"Удалить профиль {self.selected_profile.nickname}?",
                parent=self.root
            )
            if confirm:
                del self.profiles[self.selected_profile.profile_id]
                self.selected_profile = None
                self.update_profile_list()
                self.save_profiles()
                messagebox.showinfo("Успех", "Профиль удален!")
        else:
            messagebox.showerror("Ошибка", "Профиль не выбран!")

    def open_profile(self, profile):
        profile_window = Toplevel(self.root)
        profile_window.title(f"Профиль: {profile.nickname}")
        profile_window.geometry("800x600")
        profile_window.configure(bg=DARK_BG)
        
        # Настройка растягивания
        profile_window.grid_rowconfigure(0, weight=1)
        profile_window.grid_columnconfigure(0, weight=1)

        # Создание вкладок
        notebook = ttk.Notebook(profile_window)
        notebook.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        for tab_name in profile.history.keys():
            self.create_history_tab(notebook, profile, tab_name)

        # Фрейм для кнопок управления вкладками
        tab_buttons_frame = Frame(profile_window, bg=DARK_BG)
        tab_buttons_frame.pack(pady=5, fill=tk.X, padx=10)

        button_add_tab = self.create_rounded_button(
            tab_buttons_frame, 
            "Создать вкладку", 
            lambda: self.add_tab(profile, notebook)
        )
        button_add_tab.pack(side=tk.LEFT, padx=5, expand=True)

        button_rename_tab = self.create_rounded_button(
            tab_buttons_frame,
            "Переименовать",
            lambda: self.rename_current_tab(notebook, profile)
        )
        button_rename_tab.pack(side=tk.LEFT, padx=5, expand=True)

        button_delete_tab = self.create_rounded_button(
            tab_buttons_frame,
            "Удалить",
            lambda: self.delete_current_tab(notebook, profile)
        )
        button_delete_tab.pack(side=tk.LEFT, padx=5, expand=True)

        profile_window.protocol("WM_DELETE_WINDOW", lambda: self.on_profile_close(profile_window, profile))

    def create_history_tab(self, notebook, profile, tab_name):
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text=tab_name)

        # Настройка grid
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        history_listbox = Listbox(
            history_frame,
            bg=LISTBOX_BG,
            fg=LISTBOX_FG,
            selectbackground=ACCENT_COLOR,
            selectforeground='white',
            relief='flat',
            font=('Segoe UI', 10),
            highlightthickness=0,
            borderwidth=0
        )
        history_listbox.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)

        for entry in profile.history.get(tab_name, []):
            history_listbox.insert(tk.END, entry)

        # Фрейм для кнопок
        button_frame = Frame(history_frame, bg=DARK_BG)
        button_frame.grid(row=1, column=0, sticky="ew", pady=5)

        button_add_history = self.create_rounded_button(
            button_frame, 
            "Добавить", 
            lambda: self.add_history_entry(profile, tab_name, history_listbox)
        )
        button_add_history.pack(side=tk.LEFT, padx=5, expand=True)

        button_edit_history = self.create_rounded_button(
            button_frame, 
            "Изменить", 
            lambda: self.edit_history_entry(profile, tab_name, history_listbox)
        )
        button_edit_history.pack(side=tk.LEFT, padx=5, expand=True)

        button_delete_history = self.create_rounded_button(
            button_frame,
            "Удалить",
            lambda: self.delete_history_entry(profile, tab_name, history_listbox)
        )
        button_delete_history.pack(side=tk.LEFT, padx=5, expand=True)

        # Скроллбар
        scrollbar = Scrollbar(
            history_frame,
            bg=SCROLLBAR_BG,
            troughcolor=DARK_BG,
            borderwidth=0
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=history_listbox.yview)

    def add_tab(self, profile, notebook):
        dialog = CustomDialog(self.root, "Новая вкладка", "Название вкладки:")
        tab_name = dialog.result
        
        if tab_name:
            if tab_name not in profile.history:
                profile.history[tab_name] = []
                self.create_history_tab(notebook, profile, tab_name)
                self.save_profiles()
            else:
                messagebox.showerror("Ошибка", "Вкладка уже существует!")

    def rename_current_tab(self, notebook, profile):
        current_tab = notebook.select()
        if current_tab:
            old_name = notebook.tab(current_tab, "text")
            
            dialog = CustomDialog(
                self.root, 
                "Переименование", 
                "Новое название вкладки:"
            )
            new_name = dialog.result
            
            if new_name and new_name != old_name:
                if profile.rename_tab(old_name, new_name):
                    notebook.tab(current_tab, text=new_name)
                    self.save_profiles()
                    messagebox.showinfo("Успех", "Вкладка переименована!")
                else:
                    messagebox.showerror("Ошибка", "Не удалось переименовать вкладку!")
        else:
            messagebox.showerror("Ошибка", "Вкладка не выбрана!")

    def delete_current_tab(self, notebook, profile):
        current_tab = notebook.select()
        if current_tab:
            tab_name = notebook.tab(current_tab, "text")
            confirm = messagebox.askyesno(
                "Подтверждение",
                f"Удалить вкладку '{tab_name}' и все её записи?",
                parent=self.root
            )
            if confirm:
                if profile.delete_tab(tab_name):
                    notebook.forget(current_tab)
                    self.save_profiles()
                    messagebox.showinfo("Успех", "Вкладка удалена!")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить вкладку!")
        else:
            messagebox.showerror("Ошибка", "Вкладка не выбрана!")

    def add_history_entry(self, profile, tab_name, history_listbox):
        dialog = CustomDialog(self.root, "Новая запись", "Текст записи:")
        history_entry = dialog.result
        
        if history_entry:
            profile.add_history_entry(tab_name, history_entry)
            history_listbox.insert(tk.END, history_entry)
            self.save_profiles()
        else:
            messagebox.showerror("Ошибка", "Запись не может быть пустой!")

    def edit_history_entry(self, profile, tab_name, history_listbox):
        selected_index = history_listbox.curselection()
        if selected_index:
            current_entry = history_listbox.get(selected_index)
            
            dialog = CustomDialog(
                self.root, 
                "Редактирование", 
                "Изменить запись:"
            )
            dialog.entry.insert(0, current_entry)
            new_entry = dialog.result
            
            if new_entry:
                profile.edit_history_entry(tab_name, selected_index[0], new_entry)
                history_listbox.delete(selected_index)
                history_listbox.insert(selected_index, new_entry)
                self.save_profiles()
        else:
            messagebox.showerror("Ошибка", "Запись не выбрана!")

    def delete_history_entry(self, profile, tab_name, history_listbox):
        selected_index = history_listbox.curselection()
        if selected_index:
            confirm = messagebox.askyesno(
                "Подтверждение",
                "Удалить выбранную запись?",
                parent=self.root
            )
            if confirm:
                if profile.delete_history_entry(tab_name, selected_index[0]):
                    history_listbox.delete(selected_index)
                    self.save_profiles()
                    messagebox.showinfo("Успех", "Запись удалена!")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить запись!")
        else:
            messagebox.showerror("Ошибка", "Запись не выбрана!")

    def on_profile_close(self, profile_window, profile):
        profile_window.destroy()
        self.save_profiles()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("История персонала")
    root.geometry("800x600")
    root.configure(bg=DARK_BG)
    
    # Установка иконки (если есть)
    try:
        root.iconbitmap('app.ico')
    except:
        pass
    
    app = App(root)
    root.mainloop()
