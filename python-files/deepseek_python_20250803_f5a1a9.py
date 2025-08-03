import tkinter as tk
from tkinter import messagebox, simpledialog
import os

class Win95DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("База данных номеров v1.0")
        self.root.geometry("500x400")
        self.root.configure(bg="#c0c0c0")  # Характерный серый цвет Windows 95
        self.root.resizable(False, False)
        
        # Установка иконки в стиле Windows 95
        try:
            self.root.iconbitmap("win95.ico")
        except:
            pass
        
        self.password = "2014"
        self.database = []
        self.db_file = "database.txt"
        
        # Загрузка базы данных
        self.load_database()
        
        # Создание интерфейса в стиле Windows 95
        self.create_widgets()
        
        # Центрирование окна
        self.center_window()
        
    def create_widgets(self):
        # Основной фрейм с рельефом
        main_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN, bg="#c0c0c0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Заголовок в стиле Windows 95
        header_frame = tk.Frame(main_frame, bd=1, relief=tk.RAISED, bg="#c0c0c0")
        header_frame.pack(fill=tk.X, padx=4, pady=4)
        
        header = tk.Label(
            header_frame, 
            text="База данных номеров", 
            bg="#c0c0c0",
            fg="black",
            font=("MS Sans Serif", 14, "bold"),
            padx=10,
            pady=5
        )
        header.pack()
        
        subtitle = tk.Label(
            header_frame, 
            text="Введите номер для поиска в базе данных", 
            bg="#c0c0c0",
            fg="black",
            font=("MS Sans Serif", 9),
            padx=10,
            pady=(0, 5)
        )
        subtitle.pack()
        
        # Поле поиска
        search_frame = tk.Frame(main_frame, bg="#c0c0c0")
        search_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(
            search_frame, 
            text="Номер:", 
            bg="#c0c0c0",
            font=("MS Sans Serif", 10),
            anchor="w"
        ).pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("MS Sans Serif", 12),
            relief=tk.SUNKEN,
            bd=2,
            width=30
        )
        self.search_entry.pack(fill=tk.X, pady=(5, 0))
        self.search_entry.bind("<Return>", lambda e: self.search_number())
        
        # Кнопка поиска
        search_btn = tk.Button(
            search_frame, 
            text="Поиск",
            command=self.search_number,
            font=("MS Sans Serif", 10),
            bg="#c0c0c0",
            relief=tk.RAISED,
            bd=2,
            width=10,
            padx=5,
            pady=2
        )
        search_btn.pack(pady=(10, 0), anchor="e")
        
        # Индикатор статуса (скрытый по умолчанию)
        self.status_frame = tk.Frame(main_frame, height=5, bg="#c0c0c0")
        self.status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.status_indicator = tk.Frame(self.status_frame, height=5, bg="#c0c0c0")
        self.status_indicator.pack(fill=tk.X)
        
        # Кнопка базы данных в стиле Windows 95
        self.db_btn = tk.Button(
            main_frame, 
            text="База данных",
            command=self.password_prompt,
            font=("MS Sans Serif", 10, "bold"),
            bg="#c0c0c0",
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=4
        )
        self.db_btn.pack(side=tk.BOTTOM, anchor=tk.SE, padx=20, pady=20)
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_database(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    self.database = [line.strip() for line in f.readlines() if line.strip()]
            except:
                self.database = []
        else:
            self.database = []
    
    def save_database(self):
        with open(self.db_file, "w") as f:
            for number in self.database:
                f.write(number + "\n")
    
    def search_number(self):
        number = self.search_var.get().strip()
        if not number:
            return
            
        # Сброс статуса
        self.status_indicator.configure(bg="#c0c0c0")
        
        if number in self.database:
            self.search_entry.configure(bg="#d4edda", fg="#155724")
            self.search_var.set(f"Найден: {number}")
            self.status_indicator.configure(bg="#28a745")  # Зеленый индикатор
        else:
            self.search_entry.configure(bg="#f8d7da", fg="#721c24")
            self.search_var.set(f"Не найден: {number}")
            self.status_indicator.configure(bg="#dc3545")  # Красный индикатор
        
        # Сброс через 3 секунды
        self.root.after(3000, self.reset_search)
    
    def reset_search(self):
        self.search_var.set("")
        self.search_entry.configure(bg="white", fg="black")
        self.status_indicator.configure(bg="#c0c0c0")
    
    def password_prompt(self):
        password = simpledialog.askstring(
            "Пароль", 
            "Введите пароль для доступа:",
            parent=self.root,
            show="*"
        )
        if password == self.password:
            self.open_database_window()
        elif password is not None:
            messagebox.showerror("Ошибка", "Неверный пароль!", parent=self.root)
    
    def open_database_window(self):
        # Скрыть главное окно
        self.root.withdraw()
        
        # Создать окно базы данных в стиле Windows 95
        self.db_window = tk.Toplevel(self.root)
        self.db_window.title("Управление базой данных")
        self.db_window.geometry("500x500")
        self.db_window.configure(bg="#c0c0c0")
        self.db_window.protocol("WM_DELETE_WINDOW", self.restart_system)
        self.db_window.resizable(False, False)
        
        # Центрирование окна
        self.center_database_window()
        
        # Заголовок
        header_frame = tk.Frame(self.db_window, bd=1, relief=tk.RAISED, bg="#c0c0c0")
        header_frame.pack(fill=tk.X, padx=4, pady=4)
        
        header = tk.Label(
            header_frame, 
            text="Управление базой данных", 
            bg="#c0c0c0",
            fg="black",
            font=("MS Sans Serif", 14, "bold"),
            padx=10,
            pady=5
        )
        header.pack()
        
        # Список номеров с рамкой
        list_frame = tk.LabelFrame(
            self.db_window, 
            text=" Номера в базе ",
            font=("MS Sans Serif", 9),
            bg="#c0c0c0",
            bd=2,
            relief=tk.GROOVE
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Полоса прокрутки
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame, 
            font=("MS Sans Serif", 11),
            bg="white",
            relief=tk.SUNKEN,
            bd=1,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.config(command=self.listbox.yview)
        
        self.update_listbox()
        
        # Кнопки действий
        btn_frame = tk.Frame(self.db_window, bg="#c0c0c0")
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        add_btn = tk.Button(
            btn_frame, 
            text="Добавить номер", 
            command=self.add_number,
            font=("MS Sans Serif", 9),
            bg="#c0c0c0",
            relief=tk.RAISED,
            bd=2,
            width=15,
            padx=5,
            pady=2
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_btn = tk.Button(
            btn_frame, 
            text="Удалить номер", 
            command=self.remove_number,
            font=("MS Sans Serif", 9),
            bg="#c0c0c0",
            relief=tk.RAISED,
            bd=2,
            width=15,
            padx=5,
            pady=2
        )
        remove_btn.pack(side=tk.LEFT)
        
        # Кнопка перезапуска
        restart_btn = tk.Button(
            self.db_window, 
            text="Перезапустить систему", 
            command=self.restart_system,
            font=("MS Sans Serif", 10, "bold"),
            bg="#c0c0c0",
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=4
        )
        restart_btn.pack(pady=20)
    
    def center_database_window(self):
        self.db_window.update_idletasks()
        width = self.db_window.winfo_width()
        height = self.db_window.winfo_height()
        x = (self.db_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.db_window.winfo_screenheight() // 2) - (height // 2)
        self.db_window.geometry(f'+{x}+{y}')
    
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        if not self.database:
            self.listbox.insert(tk.END, "База данных пуста")
            self.listbox.itemconfig(0, {'fg': 'gray'})
            return
            
        for number in self.database:
            self.listbox.insert(tk.END, number)
    
    def add_number(self):
        new_number = simpledialog.askstring(
            "Добавление", 
            "Введите номер для добавления:", 
            parent=self.db_window
        )
        if new_number:
            new_number = new_number.strip()
            if not new_number:
                return
                
            if new_number in self.database:
                messagebox.showinfo(
                    "Ошибка", 
                    "Номер уже существует в базе!", 
                    parent=self.db_window
                )
            else:
                self.database.append(new_number)
                self.save_database()
                self.update_listbox()
                messagebox.showinfo(
                    "Успех", 
                    f"Номер {new_number} добавлен!", 
                    parent=self.db_window
                )
    
    def remove_number(self):
        if not self.database:
            messagebox.showinfo(
                "Информация", 
                "База данных пуста!", 
                parent=self.db_window
            )
            return
            
        number_to_remove = simpledialog.askstring(
            "Удаление", 
            "Введите номер для удаления:", 
            parent=self.db_window
        )
        if number_to_remove:
            number_to_remove = number_to_remove.strip()
            if not number_to_remove:
                return
                
            if number_to_remove in self.database:
                self.database.remove(number_to_remove)
                self.save_database()
                self.update_listbox()
                messagebox.showinfo(
                    "Успех", 
                    f"Номер {number_to_remove} удален!", 
                    parent=self.db_window
                )
            else:
                messagebox.showinfo(
                    "Ошибка", 
                    "Номер не найден в базе!", 
                    parent=self.db_window
                )
    
    def restart_system(self):
        if hasattr(self, 'db_window'):
            self.db_window.destroy()
        self.root.deiconify()
        self.reset_search()

if __name__ == "__main__":
    root = tk.Tk()
    app = Win95DatabaseApp(root)
    root.mainloop()