import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# Название CSV-файла, в который будут сохраняться данные
CSV_FILENAME = "health_diary.csv"


def compute_baevsky_ap(age, weight, height, systolic, diastolic, pulse):
    """
    Расчёт адаптационного потенциала (АП) по формуле Р.М. Баевского:
    AP = 0.011 * Pulse
         + 0.014 * Systolic
         + 0.008 * Diastolic
         + 0.014 * Age
         + 0.009 * Weight
         - 0.009 * Height
         - 0.27
    """
    try:
        ap = (0.011 * pulse
              + 0.014 * systolic
              + 0.008 * diastolic
              + 0.014 * age
              + 0.009 * weight
              - 0.009 * height
              - 0.27)
        return round(ap, 2)
    except:
        return None


def classify_baevsky_ap(ap):
    """
    Классификация адаптационного потенциала:
    - <=2.1:  Удовлетворительная адаптация
    - 2.11..3.2: Напряжение механизмов адаптации
    - 3.21..4.3: Неудовлетворительная адаптация
    - >4.3:  Срыв адаптации
    """
    if ap is None:
        return "Нет данных"
    if ap <= 2.1:
        return "Удовлетворительная адаптация"
    elif ap <= 3.2:
        return "Напряжение механизмов адаптации"
    elif ap <= 4.3:
        return "Неудовлетворительная адаптация"
    else:
        return "Срыв адаптации"


def compute_ruffier_index(p1, p2, p3):
    """
    Индекс Руфье:
    IR = [4 * (P1 + P2 + P3) - 200] / 10
    """
    try:
        r_index = (4 * (p1 + p2 + p3) - 200) / 10
        return round(r_index, 2)
    except:
        return None


def classify_ruffier(age, r_index):
    """
    Классификация индекса Руфье с учётом возраста, 
    возвращает категории "Высокий", "Выше среднего", "Средний", 
    "Ниже среднего", "Низкий" или "Нет данных".
    """
    if r_index is None:
        return "Нет данных"

    # Границы по условию (если возраст > 18, используем последние значения)
    thresholds_map = {
        (0, 6):   {"Низкий": 22.5, "Ниже среднего": 17.5, "Средний": 15.5, "Выше среднего": 12.6},
        (7, 8):   {"Низкий": 21.0, "Ниже среднего": 16.0, "Средний": 14.0, "Выше среднего": 11.1},
        (9, 10):  {"Низкий": 19.5, "Ниже среднего": 14.5, "Средний": 12.5, "Выше среднего": 9.6},
        (11, 12): {"Низкий": 18.0, "Ниже среднего": 13.0, "Средний": 11.0, "Выше среднего": 8.1},
        (13, 14): {"Низкий": 16.5, "Ниже среднего": 11.5, "Средний": 9.5,  "Выше среднего": 6.6},
        (15, 18): {"Низкий": 15.0, "Ниже среднего": 10.0, "Средний": 8.0,  "Выше среднего": 5.1},
    }

    # Определяем, какая возрастная группа подходит
    group = None
    for (min_a, max_a), values in thresholds_map.items():
        if min_a <= age <= max_a:
            group = (min_a, max_a)
            break
    if group is None:
        # Если возраст > 18, берём группу (15, 18) как ближайшую
        group = (15, 18)

    thresholds = thresholds_map[group]

    # Логика сравнения (сверху вниз)
    if r_index >= thresholds["Низкий"]:
        return "Низкий"
    elif r_index >= thresholds["Ниже среднего"]:
        return "Ниже среднего"
    elif r_index >= thresholds["Средний"]:
        return "Средний"
    elif r_index >= thresholds["Выше среднего"]:
        return "Выше среднего"
    else:
        return "Высокий"


def classify_serkin(t1, t2, t3):
    """
    Классификация пробы Серкина:
      - "Здоров, тренирован": T1 >= ~50, T2 >= 50% T1, T3 >= 100% T1
      - "Здоров, нетренирован": 45 <= T1 < 50, T2 ~ 30..50% T1, T3 ~70..100% T1
      - "Скрытая недостаточность кровообращения": 30 <= T1 < 45, T2 <30% T1, T3 <70% T1
    Иначе "Нет данных".
    """
    if t1 <= 0:
        return "Нет данных (T1 <= 0)"

    ratio2 = t2 / t1
    ratio3 = t3 / t1

    # Здоров, тренирован
    if t1 >= 50 and ratio2 >= 0.5 and ratio3 >= 1.0:
        return "Здоров, тренирован"

    # Здоров, нетренирован
    if 45 <= t1 < 50 and 0.3 <= ratio2 < 0.5 and 0.7 <= ratio3 < 1.0:
        return "Здоров, нетренирован"

    # Скрытая недостаточность кровообращения
    if 30 <= t1 < 45 and ratio2 < 0.3 and ratio3 < 0.7:
        return "Скрытая недостаточность кровообращения"

    return "Нет данных"


def load_data():
    """
    Считываем все записи из CSV, если файл уже существует.
    """
    records = []
    if os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    return records


def save_data(record):
    """
    Добавляем новую запись в CSV.
    Включаем кодировку 'utf-8-sig', чтобы Excel корректно читал кириллицу.
    """
    file_exists = os.path.exists(CSV_FILENAME)
    fieldnames = [
        "ФИО", "Возраст", "Вес", "Рост",
        "Систолическое", "Диастолическое", "Пульс",
        "АП_Баевский", "Оценка_Баевского",
        "P1", "P2", "P3", "Индекс_Руфье", "Оценка_Руфье",
        "T1", "T2", "T3", "Оценка_Серкина",
        "Дата/Время"
    ]

    # Важно: 'utf-8-sig' – добавляет BOM, Excel обычно корректно открывает
    # Если нужно, можно использовать "cp1251", но тогда иногда UTF-системы покажут кракозябры.
    with open(CSV_FILENAME, mode="a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


class HealthDiaryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Дневник самоконтроля (Баевский, Руфье, Серкин)")

        # Установим примерный стартовый размер окна, 
        # чтобы было место для горизонтальной прокрутки
        self.geometry("1000x600")

        # Переменные для полей ввода
        self.var_name = tk.StringVar()
        self.var_age = tk.StringVar()
        self.var_weight = tk.StringVar()
        self.var_height = tk.StringVar()
        self.var_systolic = tk.StringVar()
        self.var_diastolic = tk.StringVar()
        self.var_pulse = tk.StringVar()

        self.var_p1 = tk.StringVar()
        self.var_p2 = tk.StringVar()
        self.var_p3 = tk.StringVar()

        self.var_t1 = tk.StringVar()
        self.var_t2 = tk.StringVar()
        self.var_t3 = tk.StringVar()

        # Notebook (две вкладки)
        notebook = ttk.Notebook(self)
        notebook.pack(padx=5, pady=5, fill="both", expand=True)

        frame_input = ttk.Frame(notebook)
        frame_diary = ttk.Frame(notebook)

        notebook.add(frame_input, text="Ввод данных")
        notebook.add(frame_diary, text="Дневник самоконтроля")

        # ------------------ ФОРМА ВВОДА ------------------
        row_ = 0
        ttk.Label(frame_input, text="ФИО ученика:").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_name).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="Возраст (лет):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_age).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="Вес (кг):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_weight).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="Рост (см):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_height).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="Систолическое (мм рт. ст.):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_systolic).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="Диастолическое (мм рт. ст.):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_diastolic).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="Пульс (уд/мин):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_pulse).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="--- Проба Руфье ---").grid(row=row_, column=0, columnspan=2, pady=5)

        row_ += 1
        ttk.Label(frame_input, text="P1 (уд/15с в покое):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_p1).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="P2 (первые 15с восстановления):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_p2).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="P3 (последние 15с 1-й минуты):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_p3).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="--- Проба Серкина (задержка дыхания, с) ---").grid(row=row_, column=0, columnspan=2, pady=5)

        row_ += 1
        ttk.Label(frame_input, text="T1 (до нагрузки):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_t1).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="T2 (после 20 приседаний):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_t2).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        ttk.Label(frame_input, text="T3 (через 1 мин отдыха):").grid(row=row_, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_input, textvariable=self.var_t3).grid(row=row_, column=1, padx=5, pady=2)

        row_ += 1
        save_button = ttk.Button(frame_input, text="Сохранить результаты", command=self.save_results)
        save_button.grid(row=row_, column=0, columnspan=2, pady=10)

        # ------------------ ТАБЛИЦА "Дневник самоконтроля" ------------------
        # Создаём фрейм, в котором таблица будет занимать всё свободное пространство
        # и вертикальный скроллбар будет справа.
        # Горизонтальный скроллбар разместим отдельно снизу (для наглядности).
        columns = [
            "ФИО", "Возраст", "Вес", "Рост",
            "Систолическое", "Диастолическое", "Пульс",
            "АП_Баевский", "Оценка_Баевского",
            "P1", "P2", "P3", "Индекс_Руфье", "Оценка_Руфье",
            "T1", "T2", "T3", "Оценка_Серкина",
            "Дата/Время"
        ]
        self.tree = ttk.Treeview(frame_diary, columns=columns, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        # Вертикальная прокрутка
        scroll_y = ttk.Scrollbar(frame_diary, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)

        # Горизонтальная прокрутка (добавим её в главное окно снизу)
        scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scroll_x.set)

        # Устанавливаем заголовки и ширину столбцов
        for col in columns:
            self.tree.heading(col, text=col)
            # Можно указать фиксированную ширину. stretch=True позволяет растягивать вручную
            self.tree.column(col, width=120, stretch=True)

        # Загрузка уже имеющихся данных в таблицу
        self.refresh_diary()


    def refresh_diary(self):
        """Очистить и перезаполнить таблицу Treeview из CSV."""
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        records = load_data()
        for rec in records:
            self.tree.insert("", tk.END, values=(
                rec["ФИО"],
                rec["Возраст"],
                rec["Вес"],
                rec["Рост"],
                rec["Систолическое"],
                rec["Диастолическое"],
                rec["Пульс"],
                rec["АП_Баевский"],
                rec["Оценка_Баевского"],
                rec["P1"], rec["P2"], rec["P3"],
                rec["Индекс_Руфье"], rec["Оценка_Руфье"],
                rec["T1"], rec["T2"], rec["T3"],
                rec["Оценка_Серкина"],
                rec["Дата/Время"]
            ))

    def save_results(self):
        """
        Считать поля ввода, вычислить результаты (Баевский, Руфье, Серкин),
        сохранить в CSV и обновить таблицу.
        """
        try:
            name = self.var_name.get().strip()
            age = float(self.var_age.get())
            weight = float(self.var_weight.get())
            height = float(self.var_height.get())
            systolic = float(self.var_systolic.get())
            diastolic = float(self.var_diastolic.get())
            pulse = float(self.var_pulse.get())
            p1 = float(self.var_p1.get())
            p2 = float(self.var_p2.get())
            p3 = float(self.var_p3.get())
            t1 = float(self.var_t1.get())
            t2 = float(self.var_t2.get())
            t3 = float(self.var_t3.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введённых числовых данных!")
            return

        # Вычисления
        ap_value = compute_baevsky_ap(age, weight, height, systolic, diastolic, pulse)
        ap_class = classify_baevsky_ap(ap_value)

        ruffier_value = compute_ruffier_index(p1, p2, p3)
        ruffier_class = classify_ruffier(age, ruffier_value)

        serkin_class = classify_serkin(t1, t2, t3)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "ФИО": name,
            "Возраст": age,
            "Вес": weight,
            "Рост": height,
            "Систолическое": systolic,
            "Диастолическое": diastolic,
            "Пульс": pulse,
            "АП_Баевский": ap_value if ap_value is not None else "",
            "Оценка_Баевского": ap_class,
            "P1": p1, "P2": p2, "P3": p3,
            "Индекс_Руфье": ruffier_value if ruffier_value is not None else "",
            "Оценка_Руфье": ruffier_class,
            "T1": t1, "T2": t2, "T3": t3,
            "Оценка_Серкина": serkin_class,
            "Дата/Время": now_str
        }

        # Сохраняем в CSV (с поддержкой кириллицы, utf-8-sig)
        save_data(record)
        self.refresh_diary()

        # Очищаем поля
        self.var_name.set("")
        self.var_age.set("")
        self.var_weight.set("")
        self.var_height.set("")
        self.var_systolic.set("")
        self.var_diastolic.set("")
        self.var_pulse.set("")
        self.var_p1.set("")
        self.var_p2.set("")
        self.var_p3.set("")
        self.var_t1.set("")
        self.var_t2.set("")
        self.var_t3.set("")

        messagebox.showinfo("Готово", "Результаты успешно сохранены.")


if __name__ == "__main__":
    app = HealthDiaryApp()
    app.mainloop()
