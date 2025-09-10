import json
import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
import sys


class PensionCalculatorWithLargeTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("⏰ Калькулятор пенсии РФ - Таймер")
        self.root.geometry("900x800")
        self.root.configure(bg='#2c3e50')

        # Центрирование окна
        self.center_window()

        self.config_file = 'pension_config.json'
        self.config = self.load_config()
        self.timer_running = False
        self.timer_thread = None
        self.pension_date = None

        # Создаем кастомные шрифты
        self.create_fonts()

        self.setup_ui()
        self.load_saved_data()

    def create_fonts(self):
        """Создание кастомных шрифтов"""
        self.large_font = font.Font(family="Arial", size=48, weight="bold")
        self.medium_font = font.Font(family="Arial", size=24, weight="bold")
        self.normal_font = font.Font(family="Arial", size=14)
        self.small_font = font.Font(family="Arial", size=12)

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 900
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def load_config(self):
        """Загрузка конфигурации из файла - создает файл если не существует"""
        config_data = {
            'birth_date': '',
            'gender': 'м',
            'special_conditions': False
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем файл если он не существует
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                return config_data
        except:
            return config_data

    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def calculate_detailed_age(self, birth_date, current_date):
        """Расчет точного возраста"""
        years = current_date.year - birth_date.year
        months = current_date.month - birth_date.month
        days = current_date.day - birth_date.day

        if days < 0:
            months -= 1
            if current_date.month == 1:
                prev_month = current_date.replace(year=current_date.year - 1, month=12, day=31)
            else:
                prev_month = current_date.replace(month=current_date.month - 1, day=1) - datetime.timedelta(days=1)
            days += prev_month.day

        if months < 0:
            years -= 1
            months += 12

        return years, months, days

    def calculate_time_until(self, target_date):
        """Расчет времени до целевой даты"""
        now = datetime.datetime.now()
        target_datetime = datetime.datetime.combine(target_date, datetime.time(0, 0))

        if now >= target_datetime:
            return 0, 0, 0, 0

        delta = target_datetime - now
        total_seconds = int(delta.total_seconds())

        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return days, hours, minutes, seconds

    def setup_ui(self):
        """Настройка графического интерфейса с крупным таймером"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Заголовок
        title_label = tk.Label(main_frame, text="⏰ ТАЙМЕР ДО ПЕНСИИ РФ",
                               font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Фрейм ввода данных
        input_frame = tk.Frame(main_frame, bg="#34495e", padx=15, pady=15)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)

        tk.Label(input_frame, text="Дата рождения (ГГГГ-ММ-ДД):",
                 font=("Arial", 12), fg="white", bg="#34495e").grid(row=0, column=0, sticky=tk.W, pady=5)

        self.birth_date_entry = tk.Entry(input_frame, width=20, font=("Arial", 12))
        self.birth_date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        tk.Label(input_frame, text="Пол:",
                 font=("Arial", 12), fg="white", bg="#34495e").grid(row=1, column=0, sticky=tk.W, pady=5)

        self.gender_var = tk.StringVar(value="м")
        gender_frame = tk.Frame(input_frame, bg="#34495e")
        gender_frame.grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Radiobutton(gender_frame, text="Мужской", variable=self.gender_var, value="м",
                       font=("Arial", 11), fg="white", bg="#34495e", selectcolor="#2c3e50").pack(side=tk.LEFT)
        tk.Radiobutton(gender_frame, text="Женский", variable=self.gender_var, value="ж",
                       font=("Arial", 11), fg="white", bg="#34495e", selectcolor="#2c3e50").pack(side=tk.LEFT,
                                                                                                 padx=(10, 0))

        self.special_var = tk.BooleanVar(value=False)
        tk.Checkbutton(input_frame, text="Особые условия (Северный стаж)", variable=self.special_var,
                       font=("Arial", 11), fg="white", bg="#34495e", selectcolor="#2c3e50").grid(row=2, column=1,
                                                                                                 sticky=tk.W, pady=5)

        # Кнопки
        button_frame = tk.Frame(main_frame, bg="#2c3e50", padx=10, pady=10)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        buttons = [
            ("Рассчитать", self.calculate),
            ("Запустить таймер", self.start_timer),
            ("Остановить", self.stop_timer),
            ("Сброс", self.clear_data)
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command,
                            font=("Arial", 11), bg="#3498db", fg="white",
                            relief=tk.FLAT, padx=15, pady=8)
            btn.pack(side=tk.LEFT, padx=5)

        # Таймер - КРУПНЫЙ
        timer_frame = tk.Frame(main_frame, bg="#34495e", padx=20, pady=20)
        timer_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20, padx=10)

        # Основной таймер
        self.timer_var = tk.StringVar(value="00:00:00:00")
        timer_label = tk.Label(timer_frame, textvariable=self.timer_var,
                               font=("Arial", 72, "bold"),
                               fg="#e74c3c", bg="#34495e",
                               padx=20, pady=20)
        timer_label.pack(pady=20)

        # Детали таймера
        detail_frame = tk.Frame(timer_frame, bg="#34495e")
        detail_frame.pack(pady=10)

        labels = ["ДНЕЙ:", "ЧАСОВ:", "МИНУТ:", "СЕКУНД:"]
        vars = [self.days_var, self.hours_var, self.minutes_var, self.seconds_var] = [
            tk.StringVar(value="00") for _ in range(4)
        ]

        for i, (label_text, var) in enumerate(zip(labels, vars)):
            frame = tk.Frame(detail_frame, bg="#34495e")
            frame.pack(side=tk.LEFT, padx=15)

            tk.Label(frame, text=label_text, font=("Arial", 16), fg="#bdc3c7", bg="#34495e").pack()
            tk.Label(frame, textvariable=var, font=("Arial", 24, "bold"), fg="#3498db", bg="#34495e").pack()

        # Результаты
        results_frame = tk.Frame(main_frame, bg="#ecf0f1", padx=15, pady=15)
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)

        self.result_text = tk.Text(results_frame, height=8, width=70,
                                   font=("Arial", 12), bg="white", fg="#2c3e50",
                                   relief=tk.FLAT, bd=2, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              font=("Arial", 10), fg="#7f8c8d", bg="#34495e",
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E))

        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def load_saved_data(self):
        """Загрузка сохраненных данных"""
        if self.config:
            self.birth_date_entry.delete(0, tk.END)
            self.birth_date_entry.insert(0, self.config.get('birth_date', ''))
            self.gender_var.set(self.config.get('gender', 'м'))
            self.special_var.set(self.config.get('special_conditions', False))
            self.status_var.set("Загружены сохраненные данные")

    def validate_date(self, date_str):
        """Проверка корректности даты"""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def calculate_pension_date(self):
        """Расчет даты выхода на пенсию"""
        birth_date_str = self.birth_date_entry.get()
        if not self.validate_date(birth_date_str):
            return None

        birth_date = datetime.datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        gender = self.gender_var.get()
        special_conditions = self.special_var.get()

        # Расчет пенсионного возраста
        if gender == "м":
            base_age = 65
        else:
            base_age = 60

        # Учет особых условий
        if special_conditions:
            base_age -= 5

        # Расчет даты пенсии
        try:
            pension_date = datetime.date(
                birth_date.year + base_age,
                birth_date.month,
                birth_date.day
            )
            return pension_date
        except ValueError:
            # Обработка 29 февраля
            return datetime.date(birth_date.year + base_age, 3, 1)

    def calculate(self):
        """Основной расчет"""
        try:
            self.pension_date = self.calculate_pension_date()
            if not self.pension_date:
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return

            birth_date = datetime.datetime.strptime(self.birth_date_entry.get(), '%Y-%m-%d').date()
            today = datetime.date.today()

            # Сохранение данных
            self.config = {
                'birth_date': self.birth_date_entry.get(),
                'gender': self.gender_var.get(),
                'special_conditions': self.special_var.get()
            }
            self.save_config()

            # Расчет возраста
            age_years, age_months, age_days = self.calculate_detailed_age(birth_date, today)

            # Формирование результата
            result_text = f"📅 ДАТА РОЖДЕНИЯ: {birth_date.strftime('%d.%m.%Y')}\n"
            result_text += f"🎂 ВОЗРАСТ: {age_years} лет, {age_months} мес., {age_days} дней\n"
            result_text += f"👵 ПЕНСИОННЫЙ ВОЗРАСТ: {65 if self.gender_var.get() == 'м' else 60} лет\n"
            if self.special_var.get():
                result_text += f"🔧 С УЧЕТОМ ОСОБЫХ УСЛОВИЙ: -5 лет\n"
            result_text += f"📆 ДАТА ПЕНСИИ: {self.pension_date.strftime('%d.%m.%Y')}\n\n"

            if today >= self.pension_date:
                days_passed = (today - self.pension_date).days
                result_text += f"✅ ВЫ УЖЕ НА ПЕНСИИ!\n"
                result_text += f"🎉 Прошло дней: {days_passed}\n"
                result_text += f"🥳 Наслаждайтесь отдыхом!"
            else:
                days_remaining = (self.pension_date - today).days
                result_text += f"⏳ ДО ПЕНСИИ ОСТАЛОСЬ:\n"
                result_text += f"📅 Дней: {days_remaining}\n"
                result_text += f"🗓️ Это примерно {days_remaining // 365} лет и {(days_remaining % 365) // 30} месяцев\n"
                result_text += f"💡 Нажмите 'Запустить таймер' для отсчета!"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result_text)
            self.status_var.set("Расчет завершен")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")

    def start_timer(self):
        """Запуск таймерa"""
        if self.timer_running:
            return

        if not self.pension_date:
            self.calculate()
            if not self.pension_date:
                return

        today = datetime.date.today()
        if today >= self.pension_date:
            messagebox.showinfo("Информация", "Вы уже на пенсии! 🎉")
            return

        self.timer_running = True
        self.status_var.set("Таймер запущен ✅")

        def timer_loop():
            while self.timer_running:
                try:
                    days, hours, minutes, seconds = self.calculate_time_until(self.pension_date)
                    self.root.after(0, lambda: self.update_timer(days, hours, minutes, seconds))
                    time.sleep(1)
                except:
                    break

        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        """Остановка таймера"""
        self.timer_running = False
        self.status_var.set("Таймер остановлен ⏹️")

    def update_timer(self, days, hours, minutes, seconds):
        """Обновление отображения таймера"""
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            self.timer_var.set("🎉 ПЕНСИЯ! 🎉")
            self.days_var.set("00")
            self.hours_var.set("00")
            self.minutes_var.set("00")
            self.seconds_var.set("00")
            self.timer_running = False
            self.status_var.set("Вы на пенсии! 🥳")
        else:
            self.timer_var.set(f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.days_var.set(f"{days:02d}")
            self.hours_var.set(f"{hours:02d}")
            self.minutes_var.set(f"{minutes:02d}")
            self.seconds_var.set(f"{seconds:02d}")

    def clear_data(self):
        """Очистка данных"""
        self.stop_timer()
        self.birth_date_entry.delete(0, tk.END)
        self.gender_var.set("м")
        self.special_var.set(False)
        self.result_text.delete(1.0, tk.END)
        self.timer_var.set("00:00:00:00")
        for var in [self.days_var, self.hours_var, self.minutes_var, self.seconds_var]:
            var.set("00")
        self.config = {
            'birth_date': '',
            'gender': 'м',
            'special_conditions': False
        }
        self.save_config()
        self.status_var.set("Данные очищены 🗑️")


def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = PensionCalculatorWithLargeTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()