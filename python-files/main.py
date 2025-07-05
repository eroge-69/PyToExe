import tkinter as tk
from tkinter import messagebox

class CS2FermaLukai:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("CS2 Ферма Lukai")
        self.window.configure(background="#f0f0f0")

        # Заголовок
        self.title_label = tk.Label(self.window, text="CS2 Ферма Lukai", font=("Arial", 24), bg="#f0f0f0", fg="#00698f")
        self.title_label.pack(pady=20)

        # Панель ввода
        self.input_panel = tk.Frame(self.window, bg="#ffffff", highlightbackground="#dddddd", highlightthickness=1)
        self.input_panel.pack(padx=20, pady=20)

        # Количество аккаунтов
        self.accounts_label = tk.Label(self.input_panel, text="Количество аккаунтов:", font=("Arial", 14), bg="#ffffff", fg="#333333")
        self.accounts_label.grid(row=0, column=0, padx=10, pady=10)
        self.accounts_entry = tk.Entry(self.input_panel, width=20, font=("Arial", 14), bg="#f0f0f0", fg="#333333")
        self.accounts_entry.grid(row=0, column=1, padx=10, pady=10)

        # Кнопка создания полей ввода доходов
        self.create_incomes_button = tk.Button(self.input_panel, text="Создать поля ввода доходов", command=self.create_incomes_entries, font=("Arial", 14), bg="#4CAF50", fg="#ffffff")
        self.create_incomes_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Создание прокручиваемой области для полей ввода доходов
        self.canvas = tk.Canvas(self.input_panel, bg="#ffffff")
        self.scrollbar = tk.Scrollbar(self.input_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ffffff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollbar.grid(row=2, column=1, sticky="ns")

        # Поля ввода доходов
        self.incomes_entries = []

        # Кнопка расчета
        self.calculate_button = tk.Button(self.input_panel, text="Рассчитать", command=self.calculate_profit, font=("Arial", 14), bg="#4CAF50", fg="#ffffff")
        self.calculate_button.grid(row=3, column=0, padx=10, pady=10)

        # Кнопка очистки
        self.clear_button = tk.Button(self.input_panel, text="Очистить", command=self.clear_fields, font=("Arial", 14), bg="#f44336", fg="#ffffff")
        self.clear_button.grid(row=3, column=1, padx=10, pady=10)

        # Результаты
        self.results_frame = tk.Frame(self.window)
        self.results_frame.pack(pady=10)

        self.results_text = tk.Text(self.results_frame, width=40, height=15, font=("Arial", 14), bg="#ffffff", fg="#333333", yscrollcommand='yview')
        self.results_text.pack(side=tk.LEFT)

        self.scrollbar_results = tk.Scrollbar(self.results_frame)
        self.scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_results.config(command=self.results_text.yview)

    def create_incomes_entries(self):
        # Удаляем старые поля ввода, если они существуют
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.incomes_entries = []  # Список для хранения полей ввода доходов
        try:
            accounts = int(self.accounts_entry.get())  # Получаем количество аккаунтов
            if accounts <= 0:
                raise ValueError("Количество аккаунтов должно быть положительным")

            # Создаем поля ввода для каждого аккаунта
            for i in range(accounts):
                income_label = tk.Label(self.scrollable_frame, text=f"Аккаунт {i+1}:", font=("Arial", 14), bg="#ffffff", fg="#333333")
                income_label.grid(row=i, column=0, padx=10, pady=10)  # Метка для аккаунта
                income_entry = tk.Entry(self.scrollable_frame, width=20, font=("Arial", 14), bg="#f0f0f0", fg="#333333")
                income_entry.grid(row=i, column=1, padx=10, pady=10)  # Поле ввода дохода
                self.incomes_entries.append(income_entry)  # Добавляем поле ввода в список
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный ввод количества аккаунтов")
        
    def calculate_profit(self):
        try:
            # Сбор доходов из полей ввода
            incomes = [float(entry.get()) for entry in self.incomes_entries]

            # Проверка на неотрицательные значения
            if any(income < 0 for income in incomes):
                raise ValueError("Все доходы должны быть неотрицательными")

            steam_fee = 0.05  # Комиссия Steam 5%
            total_income = sum(incomes)  # Общий доход
            steam_commission = total_income * steam_fee  # Комиссия Steam
            net_profit = total_income - steam_commission  # Чистая прибыль

            # Формирование результатов
            results = f"Общий доход: {total_income:.2f} руб.\n"
            results += f"Комиссия Steam: {steam_commission:.2f} руб. ({steam_fee * 100}%)\n"
            results += f"Чистая прибыль: {net_profit:.2f} руб.\n\n"

            for i, income in enumerate(incomes, start=1):
                results += f"Аккаунт {i}: {income:.2f} руб.\n"

            # Вывод результатов в текстовое поле
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, results)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    def clear_fields(self):
            # Очищаем поле ввода количества аккаунтов
            self.accounts_entry.delete(0, tk.END)
        
        # Очищаем все поля ввода доходов
            for entry in self.incomes_entries:
                entry.delete(0, tk.END)
        
        # Очищаем текстовое поле с результатами
            self.results_text.delete('1.0', tk.END)
        
        # Сбрасываем список полей ввода доходов
            self.incomes_entries.clear()
    def run(self):
            self.window.mainloop()  # Запуск основного цикла приложения

if __name__ == "__main__":
    calculator = CS2FermaLukai()  # Создание экземпляра класса
    calculator.run()  # Запуск приложения
