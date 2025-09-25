import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar

class DateCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Калькулятор временных интервалов")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Данные о праздниках
        self.holidays_rf = [
            {"date": "2025-01-01", "name": "Новый год", "period": "2025-01-01 to 2025-01-08"},
            {"date": "2025-02-23", "name": "День защитника Отечества"},
            {"date": "2025-03-08", "name": "Международный женский день"},
            {"date": "2025-05-01", "name": "Праздник Весны и Труда"},
            {"date": "2025-05-09", "name": "День Победы"},
            {"date": "2025-06-12", "name": "День России"},
            {"date": "2025-11-04", "name": "День народного единства"}
        ]
        
        self.holidays_china = [
            {"date": "2025-01-01", "name": "Новый год"},
            {"date": "2025-01-28", "name": "Праздник Весны", "period": "2025-01-28 to 2025-02-03"},
            {"date": "2025-04-05", "name": "День поминовения предков"},
            {"date": "2025-05-01", "name": "День труда", "period": "2025-05-01 to 2025-05-03"},
            {"date": "2025-05-31", "name": "Праздник лодок-драконов", "period": "2025-05-31 to 2025-06-02"},
            {"date": "2025-09-06", "name": "Праздник середины осени", "period": "2025-09-06 to 2025-09-08"},
            {"date": "2025-10-01", "name": "Национальный день КНР", "period": "2025-10-01 to 2025-10-07"}
        ]
        
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10)
        
        title_label = ttk.Label(title_frame, text="📅 Калькулятор временных интервалов", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Расчет периодов с учетом праздников 🇷🇺 РФ и 🇨🇳 Китая", 
                                  font=("Arial", 10))
        subtitle_label.pack()
        
        # Основная рамка
        main_frame = ttk.LabelFrame(self.root, text="Параметры расчета", padding=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Выбор режима
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(mode_frame, text="Способ расчета:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.calc_mode = tk.StringVar(value="dates")
        ttk.Radiobutton(mode_frame, text="По датам (начальная → конечная)", 
                       variable=self.calc_mode, value="dates", 
                       command=self.toggle_mode).pack(anchor="w", padx=20)
        ttk.Radiobutton(mode_frame, text="По количеству дней (начальная + дни)", 
                       variable=self.calc_mode, value="days", 
                       command=self.toggle_mode).pack(anchor="w", padx=20)
        
        # Поля ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=(0, 15))
        
        # Начальная дата
        ttk.Label(input_frame, text="📅 Начальная дата:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.start_date = ttk.Entry(input_frame, width=15, font=("Arial", 10))
        self.start_date.grid(row=0, column=1, sticky="w")
        ttk.Label(input_frame, text="(формат: ДД.ММ.ГГГГ)", 
                 font=("Arial", 8)).grid(row=0, column=2, sticky="w", padx=(5, 0))
        
        # Конечная дата
        self.end_date_label = ttk.Label(input_frame, text="📅 Конечная дата:")
        self.end_date_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.end_date = ttk.Entry(input_frame, width=15, font=("Arial", 10))
        self.end_date.grid(row=1, column=1, sticky="w", pady=(10, 0))
        
        # Количество дней
        self.days_label = ttk.Label(input_frame, text="🔢 Количество дней:")
        self.days_count = ttk.Entry(input_frame, width=15, font=("Arial", 10))
        
        # Кнопка расчета
        calc_frame = ttk.Frame(main_frame)
        calc_frame.pack(pady=15)
        
        self.calc_button = ttk.Button(calc_frame, text="🔄 Рассчитать", 
                                     command=self.calculate, style="Accent.TButton")
        self.calc_button.pack()
        
        # Результаты
        self.results_frame = ttk.LabelFrame(main_frame, text="Результаты расчета", padding=15)
        self.results_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        # Текстовое поле для результатов
        self.results_text = tk.Text(self.results_frame, height=15, wrap=tk.WORD, 
                                   font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Изначально скрыть поля для дней
        self.toggle_mode()
        
    def toggle_mode(self):
        if self.calc_mode.get() == "dates":
            self.end_date_label.grid()
            self.end_date.grid()
            self.days_label.grid_remove()
            self.days_count.grid_remove()
        else:
            self.end_date_label.grid_remove()
            self.end_date.grid_remove()
            self.days_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
            self.days_count.grid(row=1, column=1, sticky="w", pady=(10, 0))
            
    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str.strip(), "%d.%m.%Y")
        except:
            try:
                return datetime.strptime(date_str.strip(), "%Y-%m-%d")
            except:
                raise ValueError("Неверный формат даты")
                
    def get_week_number(self, date):
        return date.isocalendar()[1]
        
    def check_holidays(self, start_date, end_date):
        rf_holidays = []
        china_holidays = []
        
        for holiday in self.holidays_rf:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d")
            if start_date <= holiday_date <= end_date:
                rf_holidays.append(holiday)
                
        for holiday in self.holidays_china:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d")
            if start_date <= holiday_date <= end_date:
                china_holidays.append(holiday)
                
        return rf_holidays, china_holidays
        
    def calculate(self):
        try:
            # Очистка результатов
            self.results_text.delete(1.0, tk.END)
            
            # Получение начальной даты
            start_date_str = self.start_date.get()
            if not start_date_str:
                raise ValueError("Введите начальную дату")
                
            start_date = self.parse_date(start_date_str)
            
            # Получение конечной даты
            if self.calc_mode.get() == "dates":
                end_date_str = self.end_date.get()
                if not end_date_str:
                    raise ValueError("Введите конечную дату")
                end_date = self.parse_date(end_date_str)
            else:
                days_str = self.days_count.get()
                if not days_str:
                    raise ValueError("Введите количество дней")
                days = int(days_str)
                end_date = start_date + timedelta(days=days-1)
                
            # Расчеты
            days_diff = (end_date - start_date).days + 1
            weeks_count = (days_diff + 6) // 7  # Округление вверх
            week_number = self.get_week_number(end_date)
            
            # Проверка праздников
            rf_holidays, china_holidays = self.check_holidays(start_date, end_date)
            
            # Формирование результата
            result = f"📊 РЕЗУЛЬТАТЫ РАСЧЕТА\n"
            result += f"{'='*50}\n\n"
            result += f"📅 Период: с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}\n"
            result += f"📆 Количество дней: {days_diff} дней\n"
            result += f"📝 Количество календарных недель: {weeks_count} недель\n"
            result += f"🗓️ Номер календарной недели: неделя №{week_number} {end_date.year} года\n\n"
            
            # Праздники
            if rf_holidays or china_holidays:
                result += f"🚨 ВНИМАНИЕ! Обнаружены праздники:\n"
                result += f"{'='*50}\n"
                
                if rf_holidays:
                    result += f"🇷🇺 ПРАЗДНИКИ РФ:\n"
                    for holiday in rf_holidays:
                        date_obj = datetime.strptime(holiday["date"], "%Y-%m-%d")
                        result += f"   • {date_obj.strftime('%d.%m.%Y')} — {holiday['name']}\n"
                        if "period" in holiday:
                            result += f"     (период: {holiday['period']})\n"
                    result += f"\n"
                    
                if china_holidays:
                    result += f"🇨🇳 ПРАЗДНИКИ КИТАЯ:\n"
                    for holiday in china_holidays:
                        date_obj = datetime.strptime(holiday["date"], "%Y-%m-%d")
                        result += f"   • {date_obj.strftime('%d.%m.%Y')} — {holiday['name']}\n"
                        if "period" in holiday:
                            result += f"     (период: {holiday['period']})\n"
                    result += f"\n"
                    
                # Рекомендации
                total_holidays = len(rf_holidays) + len(china_holidays)
                additional_days = total_holidays * 1.5  # Примерный расчет
                
                result += f"⚠️ КОРРЕКТИРОВКА СРОКОВ:\n"
                result += f"{'='*50}\n"
                result += f"Рекомендуется добавить +{int(additional_days)} дня к планируемой\n"
                result += f"дате завершения в связи с государственными праздниками\n\n"
                result += f"💡 РЕКОМЕНДАЦИИ:\n"
                result += f"• Учесть возможные задержки в работе государственных органов\n"
                result += f"• Уведомить партнеров о праздничных периодах\n"
                result += f"• Скорректировать планы поставок и платежей\n"
                result += f"• Предусмотреть дополнительное время на таможенное оформление\n"
            else:
                result += f"✅ В указанном периоде государственных праздников не обнаружено\n"
                
            self.results_text.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете: {str(e)}")

def main():
    root = tk.Tk()
    app = DateCalculatorApp(root)
    
    # Настройка стилей
    style = ttk.Style()
    if "Accent.TButton" not in style.theme_names():
        style.configure("Accent.TButton", foreground="white", background="blue")
    
    root.mainloop()

if __name__ == "__main__":
    main()
