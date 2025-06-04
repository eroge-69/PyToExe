import tkinter as tk
from tkinter import ttk, messagebox
import math

# Прототип модуля экранирования с возможностью ввода толщины материала
# Рассчитывает коэффициент ослабления и переводит результат в децибелы

MATERIAL_PROPERTIES = {
    'Сталь': {'permittivity': 1e-6, 'conductivity': 1e7},
    'Медь': {'permittivity': 1e-6, 'conductivity': 5.8e7},
    'Алюминий': {'permittivity': 1e-6, 'conductivity': 3.5e7}
}

class ShieldingCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Прототип модуля экранирования')
        self.geometry('500x400')

        frame_geometry = ttk.LabelFrame(self, text='Геометрия помещения')
        frame_geometry.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_geometry, text='Длина (м):').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_length = ttk.Entry(frame_geometry)
        self.entry_length.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_geometry, text='Ширина (м):').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_width = ttk.Entry(frame_geometry)
        self.entry_width.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame_geometry, text='Высота (м):').grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.entry_height = ttk.Entry(frame_geometry)
        self.entry_height.grid(row=2, column=1, padx=5, pady=2)

        frame_material = ttk.LabelFrame(self, text='Материал и толщина экрана')
        frame_material.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_material, text='Материал:').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.material_var = tk.StringVar()
        material_combo = ttk.Combobox(frame_material, textvariable=self.material_var, state='readonly')
        material_combo['values'] = list(MATERIAL_PROPERTIES.keys())
        material_combo.current(0)
        material_combo.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_material, text='Толщина (мм):').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_thickness = ttk.Entry(frame_material)
        self.entry_thickness.grid(row=1, column=1, padx=5, pady=2)

        btn_calc = ttk.Button(self, text='Рассчитать ослабление', command=self.calculate)
        btn_calc.pack(pady=15)

        self.result_frame = ttk.LabelFrame(self, text='Результаты расчёта')
        self.result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.result_text = tk.Text(self.result_frame, height=8, wrap='word', state='disabled')
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

    def calculate(self):
        try:
            length = float(self.entry_length.get())
            width = float(self.entry_width.get())
            height = float(self.entry_height.get())
            thickness_mm = float(self.entry_thickness.get())
        except ValueError:
            messagebox.showerror('Ошибка ввода', 'Введите корректные числовые значения')
            return

        material = self.material_var.get()
        props = MATERIAL_PROPERTIES.get(material)
        if not props:
            messagebox.showerror('Ошибка материала', 'Свойства для выбранного материала не найдены')
            return

        thickness = thickness_mm / 1000.0
        area = 2 * (length * height + width * height + length * width)
        perm = props['permittivity']
        cond = props['conductivity']
        attenuation = cond * area / (perm * thickness)
        attenuation_db = 10 * math.log10(attenuation) if attenuation > 0 else 0

        description = f"Размеры помещения: {length:.2f}×{width:.2f}×{height:.2f} м.\n"
        description += f"Материал экрана: {material}, толщина {thickness_mm:.1f} мм.\n"
        description += f"Общая площадь экрана: {area:.2f} м².\n"
        description += f"Коэффициент ослабления A: {attenuation:.2e}.\n"
        description += f"Эквивалентное ослабление: {attenuation_db:.1f} дБ."

        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, description)
        self.result_text.config(state='disabled')

if __name__ == '__main__':
    app = ShieldingCalculator()
    app.mainloop()
