import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import os
import configparser
import time
import subprocess

# Функция для извлечения номера из email
def extract_number(email):
    try:
        parts = email.split('_')
        if len(parts) < 2:
            return None
        num_part = parts[1].split('@')[0]
        return int(num_part)
    except:
        return None

# Функция для создания splash screen
def show_splash(callback):
    splash = tk.Toplevel()
    splash.title("Splash")
    splash.overrideredirect(True)
    splash.geometry("700x300+250+200")  # Увеличена ширина
    
    # Создаем Canvas для градиента
    canvas = tk.Canvas(splash, width=800, height=60, highlightthickness=0)
    canvas.pack()
    
    # Рисуем градиент от синего к красному
    for i in range(800):
        # Вычисляем цвет для каждой позиции
        r = int(255 * i / 800)
        b = int(255 * (1 - i / 800))
        color = f'#{r:02x}00{b:02x}'
        canvas.create_line(i, 0, i, 60, fill=color)
    
    # Добавляем текст на градиент
    canvas.create_text(350, 30, text="Created by Fedorov Anton", 
                      font=("Comic Sans MS", 22, "bold italic"), fill="white")
    
    # Вторая строка текста
    label2 = tk.Label(
        splash, 
        text="Fedoroff Consulting Group", 
        font=("Arial", 20, "bold")
    )
    label2.pack(pady=20)
    
    # Закрываем splash через 2 секунды и вызываем callback
    splash.after(2000, lambda: [splash.destroy(), callback()])

# Функция для открытия справки
def open_help():
    help_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "help.chm")
    
    if not os.path.exists(help_file):
        messagebox.showerror("Ошибка", "Файл справки help.chm не найден в папке программы")
        return
    
    try:
        if is_help_open():
            return
        
        if os.name == 'nt':
            os.startfile(help_file)
        else:
            subprocess.Popen(['hh', help_file])
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл справки: {str(e)}")

# Функция для проверки, открыт ли файл справки
def is_help_open():
    try:
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq hh.exe', '/FO', 'CSV'], 
                                  capture_output=True, text=True)
            return 'hh.exe' in result.stdout
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            return 'xchm' in result.stdout or 'chm' in result.stdout
    except:
        return False

# Создание главного окна (сначала скрываем)
root = tk.Tk()
root.withdraw()
root.title("Email Manager 1.4a")  # Изменена версия
root.geometry("400x580")
root.resizable(False, False)

# Проверка и создание необходимых файлов при первом запуске
def initialize_files():
    if not os.path.exists("email.log"):
        with open("email.log", "w") as f:
            f.write("")
    
    if not os.path.exists("config.ini"):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'start_email': 'ms_license281@pvm.ooo',
            'end_email': 'ms_license552@pvm.ooo',
            'domain': 'pvm.ooo',
            'passwd': 'Mentos123!'
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)

initialize_files()

# Чтение настроек из config.ini
config = configparser.ConfigParser()
config.read("config.ini")

try:
    start_email = config['Settings']['start_email']
    end_email = config['Settings']['end_email']
    
    start_num = extract_number(start_email)
    end_num = extract_number(end_email)
    
    if start_num is None or end_num is None:
        start_num = 281
        end_num = 552
        config['Settings']['start_email'] = f'ms_license{start_num}@pvm.ooo'
        config['Settings']['end_email'] = f'ms_license{end_num}@pvm.ooo'
        with open("config.ini", "w") as configfile:
            config.write(configfile)
    
    domain = config['Settings']['domain']
    password = config['Settings']['passwd']
except:
    start_num = 281
    end_num = 552
    domain = "pvm.ooo"
    password = "Mentos123!"

# Генерация списка email-адресов
emails = [f"ms_license{num}@{domain}" for num in range(start_num, end_num + 1)]

# Функция для копирования выделенного email
def copy_email():
    selected_indices = listbox.curselection()
    if selected_indices:
        index = selected_indices[0]
        selected_email = listbox.get(index)
        
        # Копируем в буфер обмена
        pyperclip.copy(selected_email)
        
        # Сохраняем в файл
        with open("email.log", "w") as f:
            f.write(selected_email)
        
        # Обновляем интерфейс
        status_label.config(text=f"Скопирован: {selected_email}", fg="green")
        last_copied_label.config(text=f"Последний скопированный:   {selected_email}")
        
        # Выделяем следующую строку
        if index < listbox.size() - 1:
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index + 1)
            listbox.see(index + 1)
            listbox.focus_set()  # Устанавливаем фокус на список
    else:
        status_label.config(text="Выберите email для копирования", fg="red")

# Функция для копирования пароля
def copy_password():
    pyperclip.copy(password)
    status_label.config(text=f"Скопирован пароль: {password}", fg="blue")

# Создание кастомного заголовка окна
def create_custom_titlebar():
    title_frame = tk.Frame(root, bg='#2c3e50', height=30)
    title_frame.pack(fill=tk.X)
    title_frame.pack_propagate(False)
    
    # Название программы с версией
    title_label = tk.Label(
        title_frame, 
        text="Email Manager 1.4a",  # Изменена версия
        bg='#2c3e50', 
        fg='white',
        font=('Arial', 10, 'bold')
    )
    title_label.pack(side=tk.LEFT, padx=10)
    
    # Кнопка справки
    help_btn = tk.Button(
        title_frame,
        text="?",
        bg='#2c3e50',
        fg='white',
        bd=0,
        font=('Arial', 12, 'bold'),
        command=open_help,
        width=3
    )
    help_btn.pack(side=tk.RIGHT, padx=5)
    
    # Кнопка закрытия
    close_btn = tk.Button(
        title_frame,
        text="✕",
        bg='#2c3e50',
        fg='white',
        bd=0,
        font=('Arial', 12, 'bold'),
        command=root.destroy,
        width=3
    )
    close_btn.pack(side=tk.RIGHT)
    
    # Функциональность перетаскивания окна
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def on_move(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    title_frame.bind('<ButtonPress-1>', start_move)
    title_frame.bind('<ButtonRelease-1>', stop_move)
    title_frame.bind('<B1-Motion>', on_move)

    return title_frame

# Создание кастомного заголовка
title_frame = create_custom_titlebar()

# Основной контейнер для виджетов
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Заголовок списка
title_label = ttk.Label(main_frame, text="Список email-адресов:", font=("Arial", 12, "bold"))
title_label.pack(pady=(0, 10))

# Список email-адресов
listbox_frame = ttk.Frame(main_frame)
listbox_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(listbox_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    listbox_frame,
    yscrollcommand=scrollbar.set,
    selectmode=tk.SINGLE,
    height=15,
    font=("Arial", 10)
)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Привязка двойного клика для копирования
listbox.bind('<Double-Button-1>', lambda e: copy_email())

scrollbar.config(command=listbox.yview)

# Заполнение списка email-адресами
for email in emails:
    listbox.insert(tk.END, email)

# Кнопки
button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=10, fill=tk.X)

copy_email_btn = ttk.Button(
    button_frame,
    text="Копировать email",
    command=copy_email
)
copy_email_btn.pack(side=tk.LEFT, expand=True, padx=5)

copy_password_btn = ttk.Button(
    button_frame,
    text="Копировать пароль",
    command=copy_password
)
copy_password_btn.pack(side=tk.LEFT, expand=True, padx=5)

# Статусная строка
status_label = ttk.Label(main_frame, text="", font=("Arial", 10))
status_label.pack(pady=5)

# Метка для последнего скопированного email (сдвинута левее)
last_copied_frame = ttk.Frame(main_frame)
last_copied_frame.pack(fill=tk.X, pady=5)

last_copied_label = ttk.Label(
    last_copied_frame, 
    text="Последний скопированный:   ", 
    font=("Arial", 10),
    anchor='w'  # Выравнивание по левому краю
)
last_copied_label.pack(anchor='w')  # Упаковка с выравниванием по левому краю

# Функция для восстановления последнего скопированного email
def restore_last_email():
    if os.path.exists("email.log"):
        try:
            with open("email.log", "r") as f:
                last_email = f.read().strip()
            
            if last_email:
                for i in range(listbox.size()):
                    if listbox.get(i) == last_email:
                        listbox.selection_clear(0, tk.END)
                        listbox.selection_set(i)
                        listbox.see(i)
                        last_copied_label.config(text=f"Последний скопированный:   {last_email}")
                        break
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")

# Функция, которая будет вызвана после splash screen
def after_splash():
    restore_last_email()
    root.deiconify()

# Показываем splash screen
show_splash(after_splash)

# Запуск приложения
root.mainloop()