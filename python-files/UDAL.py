import json
import threading
import keyboard
import time
import random
from docx import Document
from tkinter import *
from tkinter import filedialog, ttk
import pyautogui  # Библиотека для работы с мышью

CONFIG_FILE = "settings.json"

# Настроим начальные параметры
DEFAULT_SETTINGS = {
    "base_delay": 0.05,              # Базовая задержка между символами
    "variance": 0.03,                # Колебания временной задержки
    "error_rate": 0.005,             # Вероятность случайных опечаток (0.5%)
    "micro_pause_chance": 0.05,      # Вероятность микро-паузы
    "min_micro_pause": 0.1,          # Минимальная длительность паузы
    "max_micro_pause": 0.3,          # Максимальная длительность паузы
    "mouse_jitter_interval": 10      # Интервал дергания мыши в секундах
}

global_stop_flag = False  # Глобальный флаг остановки процесса
global_pause_flag = False  # Глобальный флаг паузы
processing_thread = None  # Поток для ввода текста
jitter_thread = None  # Поток для дергания мыши
mouse_jitter_enabled = False  # Флаг включения дергания мыши

try:
    with open(CONFIG_FILE, "r") as f:
        current_settings = json.load(f)
except FileNotFoundError:
    current_settings = DEFAULT_SETTINGS.copy()

# Дополнительная проверка наличия новых ключей в настройках
for key, value in DEFAULT_SETTINGS.items():
    if key not in current_settings:
        current_settings[key] = value


# Вспомогательные функции

def apply_settings():
    """Применяет текущие настройки из формы"""
    global current_settings
    current_settings.update({
        "base_delay": float(base_delay_value.get()),
        "variance": float(variance_value.get()),
        "error_rate": float(error_rate_value.get()),
        "micro_pause_chance": float(micro_pause_chance_value.get()),
        "min_micro_pause": float(min_micro_pause_value.get()),
        "max_micro_pause": float(max_micro_pause_value.get()),
        "mouse_jitter_interval": int(mouse_jitter_interval_value.get())
    })
    save_settings()

def reset_settings():
    """Восстанавливает стандартные настройки"""
    global current_settings
    current_settings = DEFAULT_SETTINGS.copy()
    update_gui_values()
    save_settings()

def save_settings():
    """Сохраняет текущие настройки в файл"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(current_settings, f, indent=4)

def update_gui_values():
    """Обновляет интерфейс значениями из текущих настроек"""
    base_delay_value.set(current_settings["base_delay"])
    variance_value.set(current_settings["variance"])
    error_rate_value.set(current_settings["error_rate"])
    micro_pause_chance_value.set(current_settings["micro_pause_chance"])
    min_micro_pause_value.set(current_settings["min_micro_pause"])
    max_micro_pause_value.set(current_settings["max_micro_pause"])
    mouse_jitter_interval_value.set(current_settings["mouse_jitter_interval"])

def jitter_mouse(interval):
    """Поток для периодического дергания мыши"""
    global mouse_jitter_enabled
    while not global_stop_flag and mouse_jitter_enabled:
        x_offset = random.uniform(-2, 2)  # Небольшое смещение ~2 мм
        y_offset = random.uniform(-2, 2)
        pyautogui.moveRel(x_offset, y_offset, duration=0.1)
        time.sleep(interval)

def toggle_mouse_jitter():
    """Включение/отключение дергания мыши"""
    global mouse_jitter_enabled, jitter_thread
    if mouse_jitter_enabled:
        mouse_jitter_enabled = False
        if jitter_thread is not None:
            jitter_thread.join()
            jitter_thread = None
    else:
        interval = current_settings["mouse_jitter_interval"]
        mouse_jitter_enabled = True
        jitter_thread = threading.Thread(target=jitter_mouse, args=(interval,))
        jitter_thread.daemon = True
        jitter_thread.start()

# Основной ввод текста

def extract_text_from_word(file_path):
    """Извлекает текст из файла Word"""
    doc = Document(file_path)
    text_list = []
    for para in doc.paragraphs:
        text_list.extend(para.text.splitlines())
    return text_list

def write_char(char):
    """Печатаем символ с учётом русской раскладки"""
    keyboard.write(char, exact=True)

def generate_delay(settings):
    """Генерирует случайную задержку, ограничивая минимум"""
    delay = settings["base_delay"] + random.uniform(-settings["variance"], settings["variance"])
    return max(delay, 0.01)  # Минимальное ограничение задержки

def add_micro_pause(settings):
    """Добавляем микро-паузу для реалистичного эффекта набора текста"""
    pause_time = random.uniform(settings["min_micro_pause"], settings["max_micro_pause"])
    time.sleep(pause_time)

def stop_process():
    """Останавливает весь процесс ввода текста и снимает ограничения с интерфейса"""
    global global_stop_flag, processing_thread
    global_stop_flag = True  # Устанавливаем флаг остановки
    
    # Ждем завершения существующего потока ввода текста
    if processing_thread is not None:
        processing_thread.join()
        processing_thread = None
    
    # Возврат кнопки "Старт" в доступное состояние
    process_button.config(state='normal')
    
    # Не отменяем дергание мыши, если оно активно
    # Только снимаем признак паузы
    global_pause_flag = False
    
    # Скрываем индикатор активности
    activity_indicator.pack_forget()

def pause_process():
    """Поставить процесс на паузу"""
    global global_pause_flag
    global_pause_flag = True

def resume_process():
    """Возобновить приостановленный процесс"""
    global global_pause_flag
    global_pause_flag = False

def type_text_with_mistakes(text_lines, settings):
    """Осуществляет ввод текста с редкими ошибками и временными задержками"""
    for line in text_lines:
        if global_stop_flag or global_pause_flag:
            while global_pause_flag:
                time.sleep(0.1)
            continue
        typed_line = ""
        for char in line:
            if global_stop_flag or global_pause_flag:
                while global_pause_flag:
                    time.sleep(0.1)
                continue
            if random.random() < settings["micro_pause_chance"]:
                add_micro_pause(settings)
            if random.random() < settings["error_rate"]:
                if random.choice([True, False]):
                    pass  # Пропуск символа
                else:
                    # Генерация русского символа
                    mistyped_char = chr(random.randint(ord('А'), ord('я')))
                    write_char(mistyped_char)
                    time.sleep(generate_delay(settings))
                    keyboard.press_and_release('backspace')
                    time.sleep(generate_delay(settings))
            write_char(char)
            time.sleep(generate_delay(settings))
        keyboard.press_and_release('enter')
        time.sleep(settings["base_delay"] * 2)

def start_processing():
    """Начинает обработку текста из указанного файла Word"""
    global processing_thread, FILE_INPUT, global_stop_flag, global_pause_flag
    global_stop_flag = False
    global_pause_flag = False
    FILE_INPUT = filedialog.askopenfilename(title="Выберите файл Word", filetypes=[("Word documents", "*.docx")])
    if FILE_INPUT:
        process_button.config(state='disabled')
        settings = current_settings.copy()  # Используем текущие настройки
        lines_to_type = extract_text_from_word(FILE_INPUT)
        print("Начало через 5 секунд...")
        time.sleep(5)
        processing_thread = threading.Thread(target=lambda: type_text_with_mistakes(lines_to_type, settings))
        processing_thread.start()
        
        # Показываем индикатор активности
        activity_indicator.pack()

# Графический интерфейс

root = Tk()
root.title("Программа типографа")

# Основные кнопки
process_button = Button(root, text="Старт", width=20, height=2, font=("Arial", 14), bg="#3498db", fg="white", command=start_processing)
process_button.pack(pady=20)

stop_button = Button(root, text="Стоп", width=20, height=2, font=("Arial", 14), bg="#e74c3c", fg="white", command=stop_process)
stop_button.pack(pady=10)

pause_button = Button(root, text="Пауза", width=20, height=2, font=("Arial", 14), bg="#ffbb33", fg="black", command=pause_process)
pause_button.pack(pady=10)

resume_button = Button(root, text="Продолжить", width=20, height=2, font=("Arial", 14), bg="#27ae60", fg="white", command=resume_process)
resume_button.pack(pady=10)

# Индикатор активности программы
activity_indicator = Label(root, text="Processing...", font=("Arial", 14), fg="red")
activity_indicator.pack(pady=10)
activity_indicator.pack_forget()  # Изначально скрыт

# Настройки программы
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

frame_settings = Frame(notebook)
notebook.add(frame_settings, text="Настройки")

# Параметры настройки
Label(frame_settings, text="Задержка между символами:").grid(row=0, column=0, sticky=E)
base_delay_value = StringVar(value=str(current_settings["base_delay"]))
Entry(frame_settings, textvariable=base_delay_value).grid(row=0, column=1)

Label(frame_settings, text="Колебания задержки:").grid(row=1, column=0, sticky=E)
variance_value = StringVar(value=str(current_settings["variance"]))
Entry(frame_settings, textvariable=variance_value).grid(row=1, column=1)

Label(frame_settings, text="Частота опечаток:").grid(row=2, column=0, sticky=E)
error_rate_value = StringVar(value=str(current_settings["error_rate"]))
Entry(frame_settings, textvariable=error_rate_value).grid(row=2, column=1)

Label(frame_settings, text="Вероятность микро-пауз:").grid(row=3, column=0, sticky=E)
micro_pause_chance_value = StringVar(value=str(current_settings["micro_pause_chance"]))
Entry(frame_settings, textvariable=micro_pause_chance_value).grid(row=3, column=1)

Label(frame_settings, text="Минимальная пауза:").grid(row=4, column=0, sticky=E)
min_micro_pause_value = StringVar(value=str(current_settings["min_micro_pause"]))
Entry(frame_settings, textvariable=min_micro_pause_value).grid(row=4, column=1)

Label(frame_settings, text="Максимальная пауза:").grid(row=5, column=0, sticky=E)
max_micro_pause_value = StringVar(value=str(current_settings["max_micro_pause"]))
Entry(frame_settings, textvariable=max_micro_pause_value).grid(row=5, column=1)

# Интервал дергания мыши
Label(frame_settings, text="Интервал дергания мыши (секунды):").grid(row=6, column=0, sticky=E)
mouse_jitter_interval_value = StringVar(value=str(current_settings["mouse_jitter_interval"]))
Entry(frame_settings, textvariable=mouse_jitter_interval_value).grid(row=6, column=1)

# Чекбокс для включения/отключения дергания мыши
toggle_jitter_checkbox = Checkbutton(frame_settings, text="Дергать мышь", variable=BooleanVar(), command=toggle_mouse_jitter)
toggle_jitter_checkbox.grid(row=7, columnspan=2)

# Кнопки для применения и сброса настроек
apply_button = Button(frame_settings, text="Применить настройки", command=apply_settings)
apply_button.grid(row=8, column=0, pady=10)

reset_button = Button(frame_settings, text="Сбросить настройки", command=reset_settings)
reset_button.grid(row=8, column=1, pady=10)

# Обновляем интерфейс текущими значениями
update_gui_values()

# Запускаем основную петлю Tkinter
root.mainloop()