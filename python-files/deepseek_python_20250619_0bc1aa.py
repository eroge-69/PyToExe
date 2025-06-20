import tkinter as tk
from datetime import datetime
from tkinter import messagebox

def calculate_hours():
    """Вычисляет разницу между двумя датами"""
    try:
        # Получаем даты из полей ввода
        date1_str = entry1.get()
        date2_str = entry2.get()
        
        # Парсим даты
        dt1 = parse_datetime(date1_str)
        dt2 = parse_datetime(date2_str)
        
        # Рассчитываем разницу в часах
        time_diff = dt2 - dt1
        total_hours = time_diff.total_seconds() / 3600
        
        # Определяем направление времени
        if total_hours >= 0:
            direction = "прошло"
        else:
            direction = "осталось"
            total_hours = abs(total_hours)
        
        # Форматируем результат
        result_text = f"Между датами {direction}:\n"
        result_text += f"• {total_hours:.2f} часов\n"
        result_text += f"• {total_hours/24:.2f} дней\n"
        result_text += f"• {total_hours*60:.0f} минут"
        
        # Обновляем поле результата
        result_label.config(text=result_text)
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Неправильный формат даты!\n\nИспользуйте форматы:\nГГГГ-ММ-ДД ЧЧ:ММ:СС\nДД.ММ.ГГГГ ЧЧ:ММ\n2025-03-15\n15.03.2025 14:30")

def parse_datetime(input_str):
    """Парсит строку с датой в различных форматах"""
    formats = [
        "%Y-%m-%d %H:%M:%S",   # Полный формат ISO
        "%Y-%m-%d",             # Только дата ISO
        "%Y-%m-%d %H:%M",       # ISO без секунд
        "%d.%m.%Y %H:%M:%S",    # Европейский формат
        "%d.%m.%Y",             # Только дата (европ.)
        "%d.%m.%Y %H:%M",       # Европейский без секунд
        "%H:%M %d.%m.%Y",       # Время сначала
        "%d/%m/%Y %H:%M:%S",    # Слэш-разделитель
        "%d/%m/%Y"              # Слэш-разделитель (дата)
    ]
    
    input_str = input_str.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(input_str, fmt)
        except ValueError:
            continue
    
    raise ValueError("Неверный формат даты")

# Создаем главное окно
root = tk.Tk()
root.title("🕒 Калькулятор временных интервалов 🕒")
root.geometry("500x400")
root.resizable(False, False)

# Настраиваем цвета
bg_color = "#f0f8ff"
button_color = "#e6e6fa"
root.configure(bg=bg_color)

# Создаем элементы интерфейса
header = tk.Label(
    root, 
    text="Расчет времени между датами",
    font=("Arial", 16, "bold"),
    bg=bg_color,
    pady=10
)
header.pack()

# Фрейм для первой даты
frame1 = tk.Frame(root, bg=bg_color)
frame1.pack(pady=5, fill="x", padx=20)
tk.Label(frame1, text="Первая дата:", bg=bg_color, font=("Arial", 10)).pack(side="left")
entry1 = tk.Entry(frame1, width=25, font=("Arial", 10))
entry1.pack(side="right", padx=10)
entry1.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

# Фрейм для второй даты
frame2 = tk.Frame(root, bg=bg_color)
frame2.pack(pady=5, fill="x", padx=20)
tk.Label(frame2, text="Вторая дата:", bg=bg_color, font=("Arial", 10)).pack(side="left")
entry2 = tk.Entry(frame2, width=25, font=("Arial", 10))
entry2.pack(side="right", padx=10)
entry2.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

# Кнопка расчета
calculate_btn = tk.Button(
    root,
    text="Рассчитать разницу",
    command=calculate_hours,
    bg=button_color,
    font=("Arial", 12, "bold"),
    padx=10,
    pady=5
)
calculate_btn.pack(pady=20)

# Поле для результата
result_frame = tk.LabelFrame(root, text="Результат", bg=bg_color, font=("Arial", 11))
result_frame.pack(fill="both", expand=True, padx=20, pady=10)
result_label = tk.Label(
    result_frame, 
    text="Введите даты и нажмите 'Рассчитать'",
    bg="#fffaf0",
    font=("Arial", 11),
    justify="left",
    pady=20
)
result_label.pack(fill="both", expand=True, padx=10, pady=10)

# Подсказки по форматам
formats_label = tk.Label(
    root,
    text="Поддерживаемые форматы:\nГГГГ-ММ-ДД ЧЧ:ММ  |  15.03.2025 14:30  |  ДД/ММ/ГГГГ",
    font=("Arial", 9),
    bg=bg_color,
    fg="#555555"
)
formats_label.pack(side="bottom", pady=5)

# Запускаем главный цикл
root.mainloop()