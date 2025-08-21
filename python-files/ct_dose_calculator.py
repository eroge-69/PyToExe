import tkinter as tk
from tkinter import ttk, messagebox

class CTDoseCalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Калькулятор лучевой нагрузки КТ")
        self.geometry("480x320")
        self.resizable(False, False)

        # Тема оформления
        self.theme = tk.StringVar(value="light")
        self.init_theme_switcher()

        # Коэффициенты
        self.coefficients_data = {
            'age_groups': [
                'взрослые',
                'от 12 до 17',
                'от 7 до 12',
                'от 0.5 до 2',
                'от 2 до 7 ',
                'от 0 до 0.5',
            ],
            'areas': {
                'Голова': {'от 0 до 0.5': 0.0059, 'от 0.5 до 2': 0.0048, 'от 2 до 7 ': 0.0035, 'от 7 до 12': 0.0027, 'от 12 до 17': 0.0018, 'взрослые': 0.0014},
                'Шея': {'от 0 до 0.5': 0.022, 'от 0.5 до 2': 0.018, 'от 2 до 7 ': 0.013, 'от 7 до 12': 0.011, 'от 12 до 17': 0.0073, 'взрослые': 0.006},
                'Голова/шея': {'от 0 до 0.5': 0.0078, 'от 0.5 до 2': 0.0066, 'от 2 до 7 ': 0.0051, 'от 7 до 12': 0.0043, 'от 12 до 17': 0.003, 'взрослые': 0.0025},
                'Грудная клетка': {'от 0 до 0.5': 0.026, 'от 0.5 до 2': 0.02, 'от 2 до 7 ': 0.014, 'от 7 до 12': 0.026, 'от 12 до 17': 0.016, 'взрослые': 0.012},
                'Брюшная полость': {'от 0 до 0.5': 0.031, 'от 0.5 до 2': 0.024, 'от 2 до 7 ': 0.017, 'от 7 до 12': 0.03, 'от 12 до 17': 0.018, 'взрослые': 0.014},
                'Малый таз': {'от 0 до 0.5': 0.034, 'от 0.5 до 2': 0.027, 'от 2 до 7 ': 0.019, 'от 7 до 12': 0.033, 'от 12 до 17': 0.02, 'взрослые': 0.015},
                'Нижние конечности': {'от 0 до 0.5': 0.0015, 'от 0.5 до 2': 0.00099, 'от 2 до 7 ': 0.00055, 'от 7 до 12': 0.00068, 'от 12 до 17': 0.0003, 'взрослые': 0.0002},
                'Грудная клетка/брюшная полость': {'от 0 до 0.5': 0.028, 'от 0.5 до 2': 0.022, 'от 2 до 7 ': 0.016, 'от 7 до 12': 0.028, 'от 12 до 17': 0.017, 'взрослые': 0.013},
                'Брюшная полость/малый таз': {'от 0 до 0.5': 0.032, 'от 0.5 до 2': 0.026, 'от 2 до 7 ': 0.018, 'от 7 до 12': 0.031, 'от 12 до 17': 0.019, 'взрослые': 0.015},
                'Грудная клетка/брюшная полость/малый таз': {'от 0 до 0.5': 0.03, 'от 0.5 до 2': 0.024, 'от 2 до 7 ': 0.017, 'от 7 до 12': 0.029, 'от 12 до 17': 0.018, 'взрослые': 0.014}
            }
        }

        # Основной интерфейс
        self.create_main_interface()

    def init_theme_switcher(self):
        style_frame = ttk.Frame(self)
        style_frame.pack(pady=10)
        ttk.Label(style_frame, text="Выберите тему:").grid(row=0, column=0, padx=(0, 10))
        tk.Radiobutton(style_frame, text="Светлая", variable=self.theme, value="light", command=self.change_theme).grid(row=0, column=1)
        tk.Radiobutton(style_frame, text="Темная", variable=self.theme, value="dark", command=self.change_theme).grid(row=0, column=2)
        self.change_theme()

    def change_theme(self):
        style = ttk.Style()
        if self.theme.get() == 'light':
            self.configure(bg="#F8F8FF")
            style.configure('.', background="#F8F8FF", foreground="#333", font=("Helvetica Neue", 12))
            style.configure('TButton', background='#F8F8FF')
            style.map('TButton',
                      foreground=[('pressed', '#007AFF'), ('active', '#007AFF')],
                      background=[('pressed', '!disabled', '#DCDCDC'), ('active', '#EDEDED')])
        else:
            self.configure(bg="#4D4D4D")
            style.configure('.', background="#1A1A1A", foreground="#FFF", font=("Helvetica Neue", 12))
            style.configure('TButton', background='#333333')
            style.map('TButton',
                      foreground=[('pressed', '#FFFFFF'), ('active', '#FFFFFF')],
                      background=[('pressed', '!disabled', '#4C4C4C'), ('active', '#5A5A5A')])

    def create_main_interface(self):
        frame = ttk.Frame(self, padding="18")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="DLP (мГр·см):").grid(row=0, column=0, sticky="w", pady=6)
        self.dlp_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dlp_var, width=18).grid(row=0, column=1, pady=6, sticky="w")

        ttk.Label(frame, text="Возрастная группа:").grid(row=1, column=0, sticky="w", pady=6)
        self.age_group_var = tk.StringVar()
        self.age_combo = ttk.Combobox(frame, textvariable=self.age_group_var,
                                      values=self.coefficients_data['age_groups'], width=20, state="readonly")
        self.age_combo.grid(row=1, column=1, pady=6, sticky="w")

        ttk.Label(frame, text="Область исследования:").grid(row=2, column=0, sticky="w", pady=6)
        self.area_var = tk.StringVar()
        self.area_combo = ttk.Combobox(frame, textvariable=self.area_var,
                                       values=list(self.coefficients_data['areas'].keys()), width=36, state="readonly")
        self.area_combo.grid(row=2, column=1, pady=6, sticky="w")

        calc_btn = ttk.Button(frame, text="Рассчитать дозу", command=self.calculate_dose)
        calc_btn.grid(row=3, column=0, columnspan=2, pady=18)

        self.result_text = tk.Text(frame, height=10, width=67, font=("Arial", 10))
        self.result_text.grid(row=4, column=0, columnspan=2, pady=5)
        self.result_text.configure(state="disabled")

        clear_btn = ttk.Button(frame, text="Очистить", command=self.clear_fields)
        clear_btn.grid(row=5, column=0, columnspan=2, pady=10)

    def calculate_dose(self):
        try:
            dlp = float(self.dlp_var.get().replace(',', '.'))
            age_group = self.age_group_var.get().strip()
            area = self.area_var.get()
            if dlp <= 0:
                messagebox.showerror("Ошибка", "DLP должно быть положительным числом")
                return
            if not area:
                messagebox.showerror("Ошибка", "Выберите область исследования")
                return
            if not age_group:
                messagebox.showerror("Ошибка", "Выберите возрастную группу")
                return
            coefficient = self.coefficients_data['areas'][area][age_group]
            effective_dose = dlp * coefficient
            result = f"""
{effective_dose:.4f} мЗв

"""
            self.result_text.configure(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            self.result_text.configure(state="disabled")
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введенных данных.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def clear_fields(self):
        self.dlp_var.set("")
        self.age_group_var.set("")
        self.area_var.set("")
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.configure(state="disabled")

if __name__ == "__main__":
    app = CTDoseCalculator()
    app.mainloop()
