import tkinter as tk
from tkinter import ttk, messagebox
from docx import Document
from datetime import datetime
import json
import os

# Константы для замены
FIO_MARKERS = ["111", "222", "333", "444", "555","666","777"]
POSITION_MARKERS = ["11", "22", "33", "44", "55","66","77"]

# Данные по сотрудникам (ФИО: должность)
EMPLOYEES = {
    "Перекин Д.А.": "Начальник",
    "Горбачев О.Н.": "Мастер",
    "Ласточкина Е.Н.": "Мастер",
    "Абрамов Д.М":"Слесарь",
    "Гринин С.М":"Слесарь",
    "Кабанов А.Н":"Слесарь"
}



class PermitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор наряда-допуска")
        self.root.geometry("900x800")

        self.brigade_members = []
        self.load_brigade()  # Загружаем сохраненную бригаду при запуске
        self.setup_ui()

    def setup_ui(self):
        # Основные поля
        main_frame = ttk.LabelFrame(self.root, text="Основные данные", padding=10)
        main_frame.pack(pady=10, padx=10, fill=tk.X)

        # Дата
        ttk.Label(main_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_date = ttk.Entry(main_frame, width=30)
        self.entry_date.grid(row=0, column=1, padx=5, sticky=tk.W)

        # Выдавший наряд
        ttk.Label(main_frame, text="Выдавший наряд:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.issuer_var = tk.StringVar()
        self.issuer_cb = ttk.Combobox(main_frame, textvariable=self.issuer_var,
                                      values=list(EMPLOYEES.keys()), width=30)
        self.issuer_cb.grid(row=1, column=1, padx=5, sticky=tk.W)

        # Ответственный руководитель
        ttk.Label(main_frame, text="Ответственный руководитель:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.manager_var = tk.StringVar()
        self.manager_cb = ttk.Combobox(main_frame, textvariable=self.manager_var,
                                       values=list(EMPLOYEES.keys()), width=30)
        self.manager_cb.grid(row=2, column=1, padx=5, sticky=tk.W)

        # Наблюдатель
        ttk.Label(main_frame, text="Наблюдатель:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.observer_var = tk.StringVar()
        self.observer_cb = ttk.Combobox(main_frame, textvariable=self.observer_var,
                                        values=list(EMPLOYEES.keys()), width=30)
        self.observer_cb.grid(row=3, column=1, padx=5, sticky=tk.W)

        # Исполнитель работ
        ttk.Label(main_frame, text="Исполнитель работ:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.performer_var = tk.StringVar()
        self.performer_cb = ttk.Combobox(main_frame, textvariable=self.performer_var,
                                         values=list(EMPLOYEES.keys()), width=30)
        self.performer_cb.grid(row=4, column=1, padx=5, sticky=tk.W)

        # Раздел для бригады
        brigade_frame = ttk.LabelFrame(self.root, text="Формирование бригады (макс. 5 человек)", padding=10)
        brigade_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Поля для добавления в бригаду
        ttk.Label(brigade_frame, text="ФИО:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.entry_fio = ttk.Entry(brigade_frame, width=30)
        self.entry_fio.grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(brigade_frame, text="Должность:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.entry_position = ttk.Entry(brigade_frame, width=30)
        self.entry_position.grid(row=0, column=3, padx=5, sticky=tk.W)

        ttk.Button(brigade_frame, text="Добавить", command=self.add_to_brigade).grid(row=0, column=4, padx=5)

        # Таблица бригады
        self.brigade_tree = ttk.Treeview(brigade_frame, columns=("fio", "position"),
                                         show="headings", height=8)
        self.brigade_tree.heading("fio", text="ФИО")
        self.brigade_tree.heading("position", text="Должность")
        self.brigade_tree.column("fio", width=300)
        self.brigade_tree.column("position", width=300)
        self.brigade_tree.grid(row=1, column=0, columnspan=5, pady=10, sticky=tk.EW)

        # Кнопки управления бригадой
        btn_frame = ttk.Frame(brigade_frame)
        btn_frame.grid(row=2, column=0, columnspan=5, pady=5)

        ttk.Button(btn_frame, text="Удалить выбранного", command=self.remove_from_brigade).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить бригаду", command=self.clear_brigade).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить бригаду", command=self.save_brigade).pack(side=tk.LEFT, padx=5)

        # Кнопка генерации документа
        ttk.Button(self.root, text="Создать документ", command=self.generate_document,
                   style="Accent.TButton").pack(pady=20)

        # Обновляем список бригады
        self.update_brigade_list()

    def add_to_brigade(self):
        fio = self.entry_fio.get().strip()
        position = self.entry_position.get().strip()

        if not fio or not position:
            messagebox.showwarning("Ошибка", "Заполните ФИО и должность!")
            return

        if len(self.brigade_members) >= 5:
            messagebox.showwarning("Ошибка", "Максимум 5 человек в бригаде!")
            return

        self.brigade_members.append({"fio": fio, "position": position})
        self.update_brigade_list()

        # Очищаем поля ввода
        self.entry_fio.delete(0, tk.END)
        self.entry_position.delete(0, tk.END)

    def remove_from_brigade(self):
        selected = self.brigade_tree.selection()
        if not selected:
            return

        for item in selected:
            index = self.brigade_tree.index(item)
            if 0 <= index < len(self.brigade_members):
                del self.brigade_members[index]

        self.update_brigade_list()

    def clear_brigade(self):
        self.brigade_members = []
        self.update_brigade_list()

    def update_brigade_list(self):
        self.brigade_tree.delete(*self.brigade_tree.get_children())
        for member in self.brigade_members:
            self.brigade_tree.insert("", tk.END, values=(member["fio"], member["position"]))

    def save_brigade(self):
        try:
            with open("dist/brigade.json", "w", encoding="utf-8") as f:
                json.dump(self.brigade_members, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", "Состав бригады сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

    def load_brigade(self):
        """Загружает состав бригады из файла"""
        if os.path.exists("dist/brigade.json"):
            try:
                with open("dist/brigade.json", "r", encoding="utf-8") as f:
                    self.brigade_members = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить бригаду: {str(e)}")
                self.brigade_members = []

    def generate_document(self):
        if not self.brigade_members:
            messagebox.showwarning("Ошибка", "Добавьте хотя бы одного члена бригады!")
            return

        date_input = self.entry_date.get().strip()
        if not date_input:
            messagebox.showwarning("Ошибка", "Введите дату!")
            return

        if not all([self.issuer_var.get(), self.manager_var.get(), self.observer_var.get(), self.performer_var.get()]):
            messagebox.showwarning("Ошибка", "Заполните все поля ответственных!")
            return

        try:
            datetime.strptime(date_input, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неправильный формат даты! Используйте ДД.ММ.ГГГГ")
            return

        try:
            doc = Document("template.docx")

            # Получаем данные для замены
            issuer_name = self.issuer_var.get()
            manager_name = self.manager_var.get()
            issuer_position = EMPLOYEES.get(issuer_name, "")
            manager_position = EMPLOYEES.get(manager_name, "")

            # Основные замены
            replacements = {
                "###": date_input,
                "$$$": issuer_name,
                "@@@": manager_name,
                "%%%": self.observer_var.get(),
                "&&&": self.performer_var.get(),
                "***": issuer_position,
                "!!!": manager_position,
                "???": EMPLOYEES.get(self.observer_var.get(), ""),
                "+++": EMPLOYEES.get(self.performer_var.get(), "")
            }

            # Обработка параграфов
            for paragraph in doc.paragraphs:
                self.process_paragraph(paragraph, replacements)

            # Обработка таблиц
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        # Обрабатываем текст в ячейках
                        for paragraph in cell.paragraphs:
                            self.process_paragraph(paragraph, replacements)

                        # Специальная обработка таблицы бригады
                        if "Фамилия, Имя, Отчество" in cell.text:
                            self.process_brigade_table(table)

            # Сохраняем документ
            output_filename = f"Наряд-допуск_{date_input.replace('.', '_')}.docx"
            doc.save(output_filename)
            messagebox.showinfo("Готово", f"Документ сохранен как:\n{output_filename}")

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл шаблона 'template.docx' не найден!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")

    def process_brigade_table(self, table):
        """Специальная обработка таблицы с бригадой"""
        # Находим строки после заголовка (пропускаем шапку)
        for row_idx, row in enumerate(table.rows[1:], start=1):
            # Останавливаемся, если закончились члены бригады
            if row_idx - 1 >= len(self.brigade_members):
                break

            member = self.brigade_members[row_idx - 1]

            # Заполняем ячейки в строке
            if len(row.cells) > 0:
                row.cells[0].text = member["fio"]
            if len(row.cells) > 1:
                row.cells[1].text = member["position"]
            # Можно добавить обработку других колонок при необходимости

    def process_paragraph(self, paragraph, replacements):
        """Обработка параграфа с заменой маркеров"""
        # Обрабатываем комбинированные маркеры
        if "*** $$$" in paragraph.text:
            paragraph.text = paragraph.text.replace(
                "*** $$$",
                f"{replacements['***']} {replacements['$$$']}"
            )
        if "!!! @@@" in paragraph.text:
            paragraph.text = paragraph.text.replace(
                "!!! @@@",
                f"{replacements['!!!']} {replacements['@@@']}"
            )

        # Обрабатываем одиночные маркеры
        for marker, value in replacements.items():
            if marker in paragraph.text:
                paragraph.text = paragraph.text.replace(marker, value)

        # Обрабатываем маркеры бригады
        for i, member in enumerate(self.brigade_members):
            if i < len(FIO_MARKERS) and FIO_MARKERS[i] in paragraph.text:
                paragraph.text = paragraph.text.replace(FIO_MARKERS[i], member["fio"])
            if i < len(POSITION_MARKERS) and POSITION_MARKERS[i] in paragraph.text:
                paragraph.text = paragraph.text.replace(POSITION_MARKERS[i], member["position"])

        # Удаляем лишние маркеры
        for i in range(len(self.brigade_members), len(FIO_MARKERS)):
            if FIO_MARKERS[i] in paragraph.text:
                paragraph.text = paragraph.text.replace(FIO_MARKERS[i], "")
            if POSITION_MARKERS[i] in paragraph.text:
                paragraph.text = paragraph.text.replace(POSITION_MARKERS[i], "")
    def replace_text_keeping_format(self, paragraph, old, new):
        """Заменяет текст с сохранением форматирования"""
        if old not in paragraph.text:
            return

        # Получаем все runs в параграфе
        runs = paragraph.runs
        text = ''.join([run.text for run in runs])

        if old not in text:
            return

        # Разбиваем текст на части до и после заменяемого фрагмента
        before, after = text.split(old, 1)

        # Очищаем все runs
        for run in runs:
            run.text = ""

        # Восстанавливаем текст с заменой
        if before:
            runs[0].text = before
        if new:
            runs[-1].text = new
        if after:
            if len(runs) > 1:
                runs[1].text = after
            else:
                run = paragraph.add_run()
                run.text = after


if __name__ == "__main__":
    root = tk.Tk()

    # Стиль для кнопок
    style = ttk.Style()
    style.configure("Accent.TButton", foreground="white", background="#0078d7")

    app = PermitApp(root)
    root.mainloop()
