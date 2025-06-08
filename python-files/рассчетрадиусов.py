import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import json

signature = 'OBJ'

class Obj:
    def __init__(self):
        self.r1 = 1.0
        self.r2 = 1.0
        self.r3 = 1.0
        self.r4 = 1.0
        self.w1 = 1.0
        self.w2 = 1.0
        self.w3 = 1.0
        self.w4 = 1.0
        self.l = 60.0
        self.t = 0

    def save(self, filename):
        try:
            data = {
                'signature': signature,
                'r1': self.r1,
                'r2': self.r2,
                'r3': self.r3,
                'r4': self.r4,
                't': self.t,
                'w1': self.w1,
                'w2': self.w2,
                'w3': self.w3,
                'w4': self.w4,
                'l': self.l
            }
            with open(filename, 'w') as f:
                json.dump(data, f)
            return 0
        except Exception as e:
            print("Save error:", e)
            return 1

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            if data.get('signature') != signature:
                return 2
            self.r1 = float(data['r1'])
            self.r2 = float(data['r2'])
            self.r3 = float(data['r3'])
            self.r4 = float(data['r4'])
            self.t = int(data['t'])
            self.w1 = float(data['w1'])
            self.w2 = float(data['w2'])
            self.w3 = float(data['w3'])
            self.w4 = float(data['w4'])
            self.l = float(data['l'])
            return 0
        except Exception as e:
            print("Load error:", e)
            return 1

    def init(self):
        self.t = 0
        self.r1 = 1.0
        self.r2 = 1.0
        self.r3 = 1.0
        self.r4 = 1.0
        self.w1 = 1.0
        self.w2 = 1.0
        self.w3 = 1.0
        self.w4 = 1.0
        self.l = 60.0

    def calculate(self):
        # В зависимости от t вычисляем неизвестные параметры
        try:
            if self.t == 1:
                # Ищем R3, R4, W1, W2
                r4 = (self.w3 * self.l - self.w3 * self.r1 - self.w3 * 2 * self.r2) / (2 * self.w4 + self.w3)
                r3 = (self.l - self.r1 - 2 * self.r2 - r4) / 2
                r4 = abs(r4)
                r3 = abs(r3)
                w1 = r3 * self.w3 / self.r1 if self.r1 != 0 else 0
                w2 = self.r1 * w1 / self.r2 if self.r2 != 0 else 0
                self.r3 = r3
                self.r4 = r4
                self.w1 = w1
                self.w2 = w2

            elif self.t == 2:
                # Ищем R1, R2, W3, W4
                r1 = (self.w2 * self.l - self.w2 * self.r4 - self.w2 * 2 * self.r3) / (2 * self.w1 + self.w2)
                r2 = (self.l - r1 - 2 * self.r3 - self.r4) / 2
                r1 = abs(r1)
                r2 = abs(r2)
                w3 = r2 * self.w2 / self.r3 if self.r3 != 0 else 0
                w4 = self.r3 * w3 / self.r4 if self.r4 != 0 else 0
                self.r1 = r1
                self.r2 = r2
                self.w3 = w3
                self.w4 = w4

            elif self.t == 3:
                # Ищем R3, R1, W2, W4
                r1 = (self.w3 * self.l - self.w3 * self.r4 - self.w3 * 2 * self.r2) / (2 * self.w1 + self.w3)
                r3 = (self.l - r1 - 2 * self.r2 - self.r4) / 2
                r1 = abs(r1)
                r3 = abs(r3)
                w2 = r3 * self.w3 / self.r2 if self.r2 != 0 else 0
                w4 = r3 * self.w3 / self.r4 if self.r4 != 0 else 0
                self.r1 = r1
                self.r3 = r3
                self.w2 = w2
                self.w4 = w4

            elif self.t == 4:
                # Ищем R1, R4, W2, W3
                r4 = (self.w1 * self.l - 2 * self.w1 * self.r3 - self.w1 * 2 * self.r2) / (self.w1 + self.w4)
                r1 = (self.l - 2 * self.r3 - 2 * self.r2 - r4)
                r4 = abs(r4)
                r1 = abs(r1)
                w2 = r1 * self.w1 / self.r2 if self.r2 != 0 else 0
                w3 = self.r2 * w2 / self.r3 if self.r3 != 0 else 0
                self.r4 = r4
                self.r1 = r1
                self.w2 = w2
                self.w3 = w3

            elif self.t == 5:
                # Ищем R3, R2, W1, W4
                r3 = (self.w2 * self.l - self.w2 * self.r1 - self.w2 * self.r4) / (2 * self.w2 + 2 * self.w3)
                r2 = (self.l - 2 * r3 - self.r1 - self.r4) / 2
                r2 = abs(r2)
                r3 = abs(r3)
                w1 = r2 * self.w2 / self.r1 if self.r1 != 0 else 0
                w4 = r3 * self.w3 / self.r4 if self.r4 != 0 else 0
                self.r3 = r3
                self.r2 = r2
                self.w1 = w1
                self.w4 = w4

            elif self.t == 6:
                # Ищем R2, R4, W1, W3
                r4 = (self.w2 * self.l - 2 * self.w2 * self.r3 - self.w2 * self.r1) / (self.w2 + 2 * self.w4)
                r2 = (self.l - 2 * self.r3 - self.r1 - r4) / 2
                r4 = abs(r4)
                r2 = abs(r2)
                w1 = r2 * self.w2 / self.r1 if self.r1 != 0 else 0
                w3 = r2 * self.w2 / self.r3 if self.r3 != 0 else 0
                self.r4 = r4
                self.r2 = r2
                self.w1 = w1
                self.w3 = w3

            else:
                # t=0 or unknown variant - no calculation
                pass
        except Exception as e:
            messagebox.showerror("Ошибка вычисления", str(e))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gear Calculation")
        self.geometry("700x500")
        self.obj = Obj()

        self.create_widgets()
        self.load_data('obj.json')
        self.update_fields()
        self.draw_circles()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Вариант t
        ttk.Label(frm, text="Вариант (t):").grid(row=0, column=0, sticky=tk.W)
        self.t_var = tk.IntVar(value=0)
        self.t_combo = ttk.Combobox(frm, values=[0,1,2,3,4,5,6], textvariable=self.t_var, state="readonly", width=5)
        self.t_combo.grid(row=0, column=1)
        self.t_combo.bind("<<ComboboxSelected>>", lambda e: self.on_field_change())

        # Радиусы
        self.entries = {}
        labels = ['r1', 'r2', 'r3', 'r4', 'w1', 'w2', 'w3', 'w4', 'l']
        for i, label in enumerate(labels, start=1):
            ttk.Label(frm, text=label.upper() + ":").grid(row=i, column=0, sticky=tk.W)
            ent = ttk.Entry(frm, width=10)
            ent.grid(row=i, column=1)
            ent.bind("<FocusOut>", lambda e: self.on_field_change())
            self.entries[label] = ent

        # Кнопки
        btn_calc = ttk.Button(frm, text="Вычислить", command=self.calculate)
        btn_calc.grid(row=11, column=0, columnspan=2, pady=10)

        btn_save = ttk.Button(frm, text="Сохранить", command=self.save_data)
        btn_save.grid(row=12, column=0, columnspan=2, pady=5)

        btn_load = ttk.Button(frm, text="Загрузить", command=self.load_data_dialog)
        btn_load.grid(row=13, column=0, columnspan=2, pady=5)

        btn_new = ttk.Button(frm, text="Новый", command=self.new_data)
        btn_new.grid(row=14, column=0, columnspan=2, pady=5)

        # Результаты
        self.result_text = tk.Text(self, width=40, height=15)
        self.result_text.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Холст для рисования
        self.canvas = tk.Canvas(self, width=400, height=300, bg='white')
        self.canvas.pack(side=tk.BOTTOM, padx=10, pady=10)

    def on_field_change(self):
        try:
            self.obj.t = self.t_var.get()
            for key, ent in self.entries.items():
                val = ent.get()
                if val.strip() == '':
                    continue
                setattr(self.obj, key, float(val))
            self.draw_circles()
        except Exception as e:
            # Игнорируем ошибки ввода пока пользователь вводит данные
            pass

    def update_fields(self):
        self.t_var.set(self.obj.t)
        for key, ent in self.entries.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(round(getattr(self.obj, key), 2)))

    def calculate(self):
        self.on_field_change()
        self.obj.calculate()
        self.update_fields()
        self.show_results()
        self.draw_circles()

    def show_results(self):
        self.result_text.delete(1.0, tk.END)
        if self.obj.t == 0:
            text = (
                "Программа ищет необходимые радиусы и угловые скорости при вводе необходимых данных\n"
                "Для выбора редактируемой переменной нужно выбрать вариант (t)\n"
                "Для работы с программой введите имеющиеся данные, оставив неизвестные данные равными 1\n"
                "Список вариантов (с неизвестными данными):\n"
                "1) R3, R4, W1, W2\n"
                "2) R1, R2, W3, W4\n"
                "3) R3, R1, W2, W4\n"
                "4) R1, R4, W2, W3\n"
                "5) R3, R2, W1, W4\n"
                "6) R2, R4, W1, W3\n"
            )
        else:
            text = f"Вариант {self.obj.t} - результаты вычислений:\n"
            text += f"R1 = {self.obj.r1:.2f}\n"
            text += f"R2 = {self.obj.r2:.2f}\n"
            text += f"R3 = {self.obj.r3:.2f}\n"
            text += f"R4 = {self.obj.r4:.2f}\n"
            text += f"W1 = {self.obj.w1:.2f}\n"
            text += f"W2 = {self.obj.w2:.2f}\n"
            text += f"W3 = {self.obj.w3:.2f}\n"
            text += f"W4 = {self.obj.w4:.2f}\n"
            text += f"L = {self.obj.l:.2f}\n"
        self.result_text.insert(tk.END, text)

    def draw_circles(self):
        self.canvas.delete("all")
        x1 = 50
        y1 = 150

        # Масштаб для отображения радиусов
        scale = 2

        # Позиции кругов по X
        positions = [
            x1,
            x1 + scale * (self.obj.r1 + self.obj.r2),
            x1 + scale * (self.obj.r1 + 2 * self.obj.r2 + self.obj.r3),
            x1 + scale * (self.obj.r1 + 2 * self.obj.r2 + 2 * self.obj.r3 + self.obj.r4)
        ]

        radii = [self.obj.r1, self.obj.r2, self.obj.r3, self.obj.r4]

        for pos, r in zip(positions, radii):
            r_scaled = max(r * scale, 5)  # минимальный радиус для видимости
            self.canvas.create_oval(pos - r_scaled, y1 - r_scaled, pos + r_scaled, y1 + r_scaled, outline="black", width=2)

    def save_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if filename:
            self.on_field_change()
            res = self.obj.save(filename)
            if res == 0:
                messagebox.showinfo("Сохранение", "Данные успешно сохранены")
            else:
                messagebox.showerror("Ошибка", "Ошибка при сохранении")

    def load_data_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if filename:
            res = self.obj.load(filename)
            if res == 0:
                self.update_fields()
                self.show_results()
                self.draw_circles()
                messagebox.showinfo("Загрузка", "Данные успешно загружены")
            else:
                messagebox.showerror("Ошибка", "Ошибка при загрузке файла")

    def load_data(self, filename):
        res = self.obj.load(filename)
        if res == 0:
            self.update_fields()
            self.show_results()
            self.draw_circles()

    def new_data(self):
        self.obj.init()
        self.update_fields()
        self.show_results()
        self.draw_circles()

if __name__ == "__main__":
    app = App()
    app.mainloop() 
