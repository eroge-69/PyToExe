import pandas as pd
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog, messagebox

def load_and_calculate():
    try:
        # Диалог выбора файла
        filename = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xls *.xlsx"),))
        if not filename:
            return
        
        # Чтение файла Excel
        df = pd.read_excel(filename, sheet_name='Лист1')
        
        # Расчёт рабочего времени
        results = calculate_work_hours(df)
        
        # Очистка текста вывода
        output_text.delete(1.0, tk.END)
        
        # Формирование и вывод итогового отчета
        output_text.insert(tk.END, "Общее количество отработанных часов:\n")
        for emp, hours in results.items():
            output_text.insert(tk.END, f"{emp}: {hours:.2f} часа\n")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def calculate_work_hours(df):
    # Ваша логика расчета рабочего времени (пример ниже)
    employees_data = {}
    
    for _, row in df.iterrows():
        employee = row['Фамилия']
        object_comment = row['Объект'], row['Комментарий']
        date_time = pd.to_datetime(row['Дата'].strftime('%Y-%m-%d') + ' ' + row['Время'])
        
        if employee not in employees_data:
            employees_data[employee] = {'start': [], 'stop': []}
        
        if ('УРВ вход' in object_comment or 'Служебный вход' in object_comment):
            employees_data[employee]['start'].append(date_time)
        elif ('УРВ выход' in object_comment or 'Служебный выход' in object_comment):
            employees_data[employee]['stop'].append(date_time)
    
    # Расчёт продолжительности работы
    results = {}
    for emp, data in employees_data.items():
        starts = sorted(data['start'])
        stops = sorted(data['stop'])
        
        total_duration = timedelta()
        i = j = 0
        while i < len(starts) and j < len(stops):
            current_start = starts[i]
            next_stop = stops[j]
            
            if current_start <= next_stop:
                total_duration += (next_stop - current_start)
                i += 1
                j += 1
            else:
                break
        
        results[emp] = total_duration.total_seconds() / 3600
    
    return results

# Интерфейс приложения
root = tk.Tk()
root.title("Расчет рабочего времени")

# Кнопка для открытия файла
load_button = tk.Button(root, text="Открыть файл Excel", command=load_and_calculate)
load_button.pack(pady=10)

# Поле для вывода результата
output_text = tk.Text(root, height=10, width=50)
output_text.pack()

# Запуск приложения
root.mainloop()