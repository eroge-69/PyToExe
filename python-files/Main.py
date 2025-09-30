import tkinter as tk
from tkinter import ttk
import sqlite3

#Таблица
#c.execute("""CREATE TABLE mem_cards (
#    full_name VARCHAR(1000),
#    birth_date DATE,
#    mobile INTEGER,
#    Adres VARCHAR(100),
#    Pass VARCHAR(100)); 
#""")

# Подключение к БД
db = sqlite3.connect("Mem_card.db")
c = db.cursor()

# Цветовая палитра
BG_COLOR = "#EAF6F6"          # Фоновый цвет (мягкий голубой)
FRAME_BG = "#FFFFFF"          # Цвет фреймов (белый)
BTN_COLOR = "#AEDFF7"         # Цвет кнопок (светло-синий)
BTN_HOVER = "#96D1F0"         # Цвет при наведении
FONT_COLOR = "#04395E"        # Цвет текста
FONT = ("Arial", 13)            # Шрифт

# Центрирование окна
def center_window(window, width, height):
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # Вычисляем координаты для центрирования окна
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    # Устанавливаем размеры и позицию окна
    window.geometry(f"{width}x{height}+{x}+{y}")

# Окно заполнения пациента
def open_window1():
    # Заполнение базы данных спомощью переменных
    def AddData():
        Fio = entry_FIO.get()
        Born = entry_BORN.get()
        M = entry_M.get()
        Ad = entry_Ad.get()
        Pass = entry_Pass.get()
        c.execute("INSERT INTO mem_cards (full_name, birth_date, mobile, Adres, Pass) VALUES(?, ?, ?, ?, ?)",
                  (Fio, Born, M, Ad, Pass))
        db.commit()

    main_window.withdraw() # Скрыть главное окно
    window1 = tk.Toplevel(main_window) 
    window1.title("Добавить пациента")
    center_window(window1, 600, 500) # Центрируем окно
    window1.configure(bg=BG_COLOR)
    window1.protocol("WM_DELETE_WINDOW", lambda: close_all(window1))

    entry_frame = tk.Frame(window1, bg=FRAME_BG, padx=20, pady=20, bd=2, relief="ridge")
    entry_frame.pack(expand=True, fill="both", padx=30, pady=30)

    def add_label_entry(text, y):
        label = tk.Label(entry_frame, text=text, font=FONT, bg=FRAME_BG, fg=FONT_COLOR)
        label.place(x=20, y=y)
        entry = tk.Entry(entry_frame, width=40, font=FONT)
        entry.place(x=200, y=y)
        return entry

    entry_FIO = add_label_entry("ФИО:", 20)
    entry_BORN = add_label_entry("Дата рождения:", 60)
    entry_M = add_label_entry("Номер телефона:", 100)
    entry_Ad = add_label_entry("Адрес:", 140)
    entry_Pass = add_label_entry("Паспортные данные:", 180)

    save_button = tk.Button(entry_frame, text="Сохранить", width=20, height=2, bg=BTN_COLOR, fg=FONT_COLOR,
                            font=FONT, command=AddData, activebackground=BTN_HOVER)
    save_button.place(x=200, y=230)

    back_button = tk.Button(entry_frame, text="Назад", width=10, bg=BTN_COLOR, fg=FONT_COLOR, font=FONT,
                            command=lambda: back_to_main(window1), activebackground=BTN_HOVER)
    back_button.place(x=400, y=230)

# таблица
def open_window2():
    main_window.withdraw()
    window2 = tk.Toplevel(main_window)
    window2.title("Просмотр данных")
    center_window(window2, 900, 500)
    window2.configure(bg=BG_COLOR)
    window2.protocol("WM_DELETE_WINDOW", lambda: close_all(window2))

    Output_frame = tk.Frame(window2, bg=FRAME_BG, padx=20, pady=20, bd=2, relief="ridge")
    Output_frame.pack(expand=True, fill="both", padx=30, pady=30)

    back_button = tk.Button(Output_frame, text="Назад", width=10, bg=BTN_COLOR, fg=FONT_COLOR, font=FONT,
                            command=lambda: back_to_main(window2), activebackground=BTN_HOVER)
    back_button.pack(anchor="ne", pady=(0, 10))

    # Treeview (таблица)
    tree = ttk.Treeview(Output_frame, columns=("ФИО", "Дата рождения", "Телефон", "Адрес", "Паспорт"), show="headings")
    tree.pack(expand=True, fill="both")

    # Настройка заголовков
    tree.heading("ФИО", text="ФИО")
    tree.heading("Дата рождения", text="Дата рождения")
    tree.heading("Телефон", text="Телефон")
    tree.heading("Адрес", text="Адрес")
    tree.heading("Паспорт", text="Паспорт")

    # Настройка ширины столбцов
    tree.column("ФИО", width=180)
    tree.column("Дата рождения", width=100)
    tree.column("Телефон", width=100)
    tree.column("Адрес", width=200)
    tree.column("Паспорт", width=120)

    # Получение данных из БД
    c.execute("SELECT * FROM mem_cards")
    rows = c.fetchall()

    # Заполнение таблицы
    for row in rows:
        tree.insert("", "end", values=row)

def back_to_main(window):
    window.destroy() # Закрыть текущее окно
    main_window.deiconify() # Показать главное окно снова

def close_all(window):
    window.destroy() # Закрыть текущее окно
    main_window.destroy()

# Главное окно
main_window = tk.Tk()
main_window.title("Главное меню")
main_window.configure(bg=BG_COLOR)
center_window(main_window, 600, 450)
main_window.protocol("WM_DELETE_WINDOW", lambda: close_all(main_window))

button_frame = tk.Frame(main_window, bg=BG_COLOR)
button_frame.pack(expand=True)

button1 = tk.Button(button_frame, text="Записать пациента", width=25, height=3, font=FONT,
                    bg=BTN_COLOR, fg=FONT_COLOR, command=open_window1, activebackground=BTN_HOVER)
button1.pack(pady=20)

button2 = tk.Button(button_frame, text="Просмотр данных", width=25, height=3, font=FONT,
                    bg=BTN_COLOR, fg=FONT_COLOR, command=open_window2, activebackground=BTN_HOVER)
button2.pack(pady=10)

main_window.mainloop()
db.close()