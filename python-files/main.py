# main.py
import tkinter as tk
from tkinter import ttk
import json

class BallValveCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор шаровых кранов v1.0")
        
        # Загрузка данных из JSON
        with open('valve_data.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0)
        
        # Параметры ввода
        ttk.Label(main_frame, text="DN (мм):").grid(row=0, column=0, sticky=tk.W)
        self.dn_entry = ttk.Combobox(main_frame, values=list(self.data['effective_diameters'].keys()))
        self.dn_entry.grid(row=0, column=1)
        
        ttk.Label(main_frame, text="PN (бар):").grid(row=1, column=0, sticky=tk.W)
        self.pn_entry = ttk.Combobox(main_frame, values=["10", "16", "25", "40", "63", "100", "160", "250"])
        self.pn_entry.grid(row=1, column=1)
        
        ttk.Label(main_frame, text="Тип крана:").grid(row=2, column=0, sticky=tk.W)
        self.valve_type = ttk.Combobox(main_frame, values=["Полнопроходной", "Неполнопроходной"])
        self.valve_type.grid(row=2, column=1)
        
        ttk.Label(main_frame, text="Давление (МПа):").grid(row=3, column=0, sticky=tk.W)
        self.pressure_entry = ttk.Entry(main_frame)
        self.pressure_entry.grid(row=3, column=1)
        
        # Кнопка расчёта
        ttk.Button(main_frame, text="Рассчитать", command=self.calculate).grid(row=4, columnspan=2)
        
        # Результаты
        self.result_text = tk.Text(main_frame, height=10, width=50)
        self.result_text.grid(row=5, columnspan=2)
    
    def calculate(self):
        try:
            dn = self.dn_entry.get()
            pn = int(self.pn_entry.get())
            valve_type = self.valve_type.get()
            pressure = float(self.pressure_entry.get())
            
            # Расчёт эффективного диаметра
            eff_diameter = self.data['effective_diameters'][dn][valve_type][pn]
            
            # Расчёт крутящего момента (упрощённая формула)
            torque = (pressure * 10) * eff_diameter**2 * 0.001
            
            # Форматирование результатов
            result = f"""Результаты расчёта:
Номинальный диаметр (DN): {dn} мм
Эффективный диаметр: {eff_diameter} мм
Рабочее давление: {pressure} МПа
Расчётный крутящий момент: {torque:.2f} Н·м
Рекомендуемый класс герметичности: {self.data['leakage_classes'][pn]}"""
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Ошибка: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BallValveCalculator(root)
    root.mainloop()
