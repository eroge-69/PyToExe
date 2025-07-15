import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar

class VacationCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("Календарь отпусков 2025")
        
        # Переменные
        self.today = datetime(2025, 7, 15)  # По умолчанию 15.07.2025
        self.vacation_dates = []
        self.days_before_unavailable = 3
        self.selected_date = None  # Для хранения выбранной даты
        
        # Основные фреймы
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Календарь
        self.calendar_frame = ttk.LabelFrame(self.main_frame, text="Календарь 2025", padding="10")
        self.calendar_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
        
        self.create_calendar_widget()
        
        # Управление датами
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Управление", padding="10")
        self.control_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Сегодняшняя дата
        ttk.Label(self.control_frame, text="Сегодня:").grid(row=0, column=0, sticky=tk.W)
        self.today_var = tk.StringVar(value=self.today.strftime("%d.%m.%Y"))
        ttk.Label(self.control_frame, textvariable=self.today_var).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(self.control_frame, text="Предыдущий день", command=self.prev_day).grid(row=0, column=2, padx=5)
        ttk.Button(self.control_frame, text="Следующий день", command=self.next_day).grid(row=0, column=3, padx=5)
        
        # Параметры проверки
        ttk.Label(self.control_frame, text="Дней до недоступности:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.days_entry = ttk.Entry(self.control_frame, width=5)
        self.days_entry.grid(row=1, column=1, sticky=tk.W, pady=(10,0))
        self.days_entry.insert(0, str(self.days_before_unavailable))
        
        ttk.Button(self.control_frame, text="Обновить параметр", command=self.update_days).grid(row=1, column=2, columnspan=2, pady=(10,0))
        
        # Даты отпуска
        self.vacation_frame = ttk.LabelFrame(self.main_frame, text="Даты отпуска руководителя", padding="10")
        self.vacation_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.vacation_list = tk.Listbox(self.vacation_frame, width=30, height=5)
        self.vacation_list.grid(row=0, column=0, columnspan=2, pady=5)
        
        ttk.Button(self.vacation_frame, text="Добавить дату", command=self.add_vacation_date).grid(row=1, column=0, pady=5)
        ttk.Button(self.vacation_frame, text="Удалить дату", command=self.remove_vacation_date).grid(row=1, column=1, pady=5)
        
        # Результат проверки
        self.result_frame = ttk.LabelFrame(self.main_frame, text="Результат проверки", padding="10")
        self.result_frame.grid(row=3, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.result_var = tk.StringVar(value="Выберите даты отпуска и настройте параметры")
        ttk.Label(self.result_frame, textvariable=self.result_var).grid(row=0, column=0)
        
        ttk.Button(self.result_frame, text="Проверить доступность", command=self.check_availability).grid(row=1, column=0, pady=5)
        
        # Обновляем отображение календаря
        self.update_calendar()
    
    def create_calendar_widget(self):
        # Заголовок с месяцем и годом
        self.cal_header = ttk.Label(self.calendar_frame)
        self.cal_header.grid(row=0, column=0, columnspan=7)
        
        # Дни недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(weekdays):
            ttk.Label(self.calendar_frame, text=day).grid(row=1, column=i)
        
        # Ячейки календаря
        self.cal_cells = []
        for row in range(6):
            row_cells = []
            for col in range(7):
                cell = tk.Label(self.calendar_frame, text="", width=4, relief="ridge", 
                               anchor="center", bg="white")
                cell.grid(row=row+2, column=col, sticky="nsew")
                cell.bind("<Button-1>", lambda e, r=row, c=col: self.select_date(r, c))
                row_cells.append(cell)
            self.cal_cells.append(row_cells)
    
    def select_date(self, row, col):
        """Обработка выбора даты в календаре"""
        day_text = self.cal_cells[row][col].cget("text")
        if day_text:
            day = int(day_text)
            month = self.today.month
            year = 2025
            self.selected_date = datetime(year, month, day)
            
            # Сброс выделения всех дат
            for r in range(6):
                for c in range(7):
                    bg_color = "#ffcccc" if self.cal_cells[r][c].cget("text") and \
                        datetime(year, month, int(self.cal_cells[r][c].cget("text"))).strftime("%d.%m.%Y") in \
                        [d.strftime("%d.%m.%Y") for d in self.vacation_dates] else "white"
                    if day == self.today.day and month == self.today.month and r == row and c == col:
                        bg_color = "#ffffcc"
                    self.cal_cells[r][c].config(bg=bg_color)
            
            # Выделение выбранной даты
            self.cal_cells[row][col].config(bg="#ccffcc")
    
    def update_calendar(self):
        # Устанавливаем месяц и год
        year, month = 2025, self.today.month
        self.cal_header.config(text=f"{calendar.month_name[month]} {year}")
        
        # Получаем календарь на месяц
        cal = calendar.monthcalendar(year, month)
        
        # Очищаем ячейки
        for row in self.cal_cells:
            for cell in row:
                cell.config(text="", bg="white")
        
        # Заполняем ячейки датами
        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day != 0:
                    self.cal_cells[row][col].config(text=str(day))
                    
                    # Выделяем сегодняшнюю дату
                    if day == self.today.day and month == self.today.month:
                        self.cal_cells[row][col].config(bg="#ffffcc")
                    
                    # Выделяем даты отпуска
                    date_str = f"{day:02d}.{month:02d}.{year}"
                    if date_str in [d.strftime("%d.%m.%Y") for d in self.vacation_dates]:
                        self.cal_cells[row][col].config(bg="#ffcccc")
        
        # Сбрасываем выделенную дату при обновлении календаря
        self.selected_date = None
    
    def prev_day(self):
        self.today -= timedelta(days=1)
        self.today_var.set(self.today.strftime("%d.%m.%Y"))
        self.update_calendar()
    
    def next_day(self):
        self.today += timedelta(days=1)
        self.today_var.set(self.today.strftime("%d.%m.%Y"))
        self.update_calendar()
    
    def update_days(self):
        try:
            self.days_before_unavailable = int(self.days_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число дней")
    
    def add_vacation_date(self):
        if self.selected_date:
            date_str = self.selected_date.strftime("%d.%m.%Y")
            if date_str not in [d.strftime("%d.%m.%Y") for d in self.vacation_dates]:
                self.vacation_dates.append(self.selected_date)
                self.vacation_list.insert(tk.END, date_str)
                self.update_calendar()
        else:
            messagebox.showinfo("Информация", "Сначала выберите дату в календаре (кликните по ней)")
    
    def remove_vacation_date(self):
        selection = self.vacation_list.curselection()
        if selection:
            index = selection[0]
            date_str = self.vacation_list.get(index)
            
            # Удаляем дату из списка
            self.vacation_dates = [d for d in self.vacation_dates if d.strftime("%d.%m.%Y") != date_str]
            self.vacation_list.delete(index)
            self.update_calendar()
    
    def check_availability(self):
        if not self.vacation_dates:
            self.result_var.set("Не выбраны даты отпуска руководителя")
            return
        
        # Рассчитываем диапазон проверки
        start_date = self.today
        end_date = self.today + timedelta(days=self.days_before_unavailable)
        
        # Проверяем пересечение с датами отпуска
        unavailable = False
        conflict_date = None
        for vac_date in self.vacation_dates:
            if start_date <= vac_date <= end_date:
                unavailable = True
                conflict_date = vac_date
                break
        
        if unavailable:
            self.result_var.set(f"Делегирование вышестоящему\n(руководитель в отпуске {conflict_date.strftime('%d.%m.%Y')})")
        else:
            self.result_var.set("Согласует прямой руководитель")

if __name__ == "__main__":
    root = tk.Tk()
    app = VacationCalendar(root)
    root.mainloop()