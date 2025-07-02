import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LinearSegmentedColormap
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import sys

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("AnalytiXcel AK&IE")
        self.file_path = ""
        self.df_sheet1 = None
        self.df_sheet2 = None
        self.current_figure = None
        
        # Настройка цветовой схемы
        self.bg_color = "#5200CC"
        self.button_color = "#FFFFFF"
        self.text_color = "#000000"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Настройка главного окна
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width*0.7)}x{int(screen_height*0.7)}+"
                         f"{int((screen_width-screen_width*0.7)/2)}+"
                         f"{int((screen_height-screen_height*0.7)/2)}")
        self.root.configure(bg=self.bg_color)
        
        # Поле вывода
        self.output_field = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, bg=self.button_color, fg=self.text_color,
            font=('Arial', 10))
        self.output_field.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Создание кнопок
        self.create_buttons()
    
    def create_buttons(self):
        """Создание кнопок интерфейса"""
        buttons = [
            ("Выбрать файл", self.select_file),
            ("Корреляция", self.show_correlation_methods),
            ("Регрессия", self.perform_regression),
            ("Анализ во времени", self.show_time_series),
            ("Сохранить данные", self.save_results),
            ("Сохранить график", self.save_plot)
        ]
        
        # Создаем три ряда кнопок
        for i, row in enumerate([buttons[:1], buttons[1:4], buttons[4:]]):
            frame = tk.Frame(self.root, bg=self.bg_color)
            frame.pack(pady=5)
            for text, command in row:
                btn = tk.Button(
                    frame, text=text, command=command,
                    width=15, height=2, bg=self.button_color, fg=self.text_color,
                    font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=2)
                btn.pack(side=tk.LEFT, padx=5)
    
    def select_file(self):
        """Загрузка файла с данными"""
        self.file_path = filedialog.askopenfilename(
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")))
        
        if self.file_path:
            try:
                self.df_sheet1 = pd.read_excel(self.file_path, sheet_name="Лист1")
                self.df_sheet2 = pd.read_excel(self.file_path, sheet_name="Лист2")
                self.output_field.insert(tk.END, f"Файл успешно загружен\n")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def show_correlation_methods(self):
        """Показывает диалог выбора метода корреляции"""
        if self.df_sheet1 is None or self.df_sheet2 is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл!")
            return
        
        methods_window = tk.Toplevel(self.root)
        methods_window.title("Выберите метод корреляции")
        methods_window.geometry("300x200")
        methods_window.configure(bg=self.bg_color)
        
        tk.Label(methods_window, text="Выберите метод расчета корреляции:",
               bg=self.bg_color, fg=self.button_color).pack(pady=10)
        
        methods = [
            ("Пирсон", "pearson"),
            ("Кендалл", "kendall"),
            ("Спирмен", "spearman")
        ]
        
        for text, method in methods:
            btn = tk.Button(
                methods_window, text=text, 
                command=lambda m=method: self.calculate_correlation(m, methods_window),
                width=15, height=2, bg=self.button_color, fg=self.text_color)
            btn.pack(pady=5)
    
    def calculate_correlation(self, method, window=None):
        """Расчет корреляции выбранным методом"""
        if window:
            window.destroy()
        
        try:
            # Получаем числовые данные из обоих листов (исключая год)
            numeric_sheet1 = self.df_sheet1.select_dtypes(include=['number']).drop(columns=['Год'], errors='ignore')
            numeric_sheet2 = self.df_sheet2.select_dtypes(include=['number']).drop(columns=['Год'], errors='ignore')
            
            if numeric_sheet1.empty or numeric_sheet2.empty:
                messagebox.showwarning("Предупреждение", "Мало данных для анализа!")
                return
            
            # Объединяем данные для корреляции
            combined = pd.concat([
                numeric_sheet1.add_prefix('Лист1_'),
                numeric_sheet2.add_prefix('Лист2_')
            ], axis=1)
            
            # Вычисляем корреляцию и фильтруем только между листами
            corr_matrix = combined.corr(method=method)
            sheet1_cols = [col for col in corr_matrix.columns if col.startswith('Лист1_')]
            sheet2_cols = [col for col in corr_matrix.columns if col.startswith('Лист2_')]
            filtered_corr = corr_matrix.loc[sheet1_cols, sheet2_cols]
            
            # Сохраняем для последующего использования
            self.corr_matrix = filtered_corr
            
            # Создаем график корреляции
            self.create_correlation_plot(filtered_corr, method)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета корреляции:\n{str(e)}")
    
    def create_correlation_plot(self, corr_data, method):
        """Создание графика корреляции"""
        if hasattr(self, 'corr_window') and self.corr_window.winfo_exists():
            self.corr_window.destroy()
        
        self.corr_window = tk.Toplevel(self.root)
        self.corr_window.title(f"Корреляция ({method})")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        self.current_figure = fig
        
        # Создаем кастомную цветовую карту (красный-белый-зеленый)
        colors = [(0, '#FF0000'), (0.5, '#FFFFFF'), (1, '#00FF00')]
        cmap = LinearSegmentedColormap.from_list('custom_cmap', colors)
        
        # Создаем heatmap корреляции
        cax = ax.matshow(corr_data, cmap=cmap, vmin=-1, vmax=1)
        fig.colorbar(cax)
        
        # Добавляем значения корреляции
        for i in range(len(corr_data.index)):
            for j in range(len(corr_data.columns)):
                ax.text(j, i, f"{corr_data.iloc[i, j]:.2f}", 
                       ha="center", va="center", color="black", fontsize=8)
        
        # Настраиваем подписи
        ax.set_xticks(range(len(corr_data.columns)))
        ax.set_yticks(range(len(corr_data.index)))
        ax.set_xticklabels([col.replace('Лист2_', '') for col in corr_data.columns], 
                          rotation=45, ha='left', fontsize=8)
        ax.set_yticklabels([col.replace('Лист1_', '') for col in corr_data.index], 
                          fontsize=8)
        
        # Улучшаем отображение
        plt.tight_layout()
        
        # Создаем canvas с прокруткой
        self.create_scrollable_canvas(fig, self.corr_window)
    
    def create_scrollable_canvas(self, fig, window):
        """Создание листа с прокруткой"""
        frame = tk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        
        # Настройка прокрутки
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.get_tk_widget().xview)
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.get_tk_widget().yview)
        canvas.get_tk_widget().config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def perform_regression(self):
        """Регрессионный анализ с выбором типа регрессии"""
        if self.df_sheet1 is None or self.df_sheet2 is None:
            messagebox.showwarning("Предупреждение", "Загрузите файл!")
            return
        
        try:
            # Получаем числовые столбцы (исключая год)
            num_cols1 = [col for col in self.df_sheet1.select_dtypes(include=['number']).columns if col != "Год"]
            num_cols2 = [col for col in self.df_sheet2.select_dtypes(include=['number']).columns if col != "Год"]
            
            if not num_cols1 or not num_cols2:
                messagebox.showwarning("Предупреждение", "Мало данных для анализа!")
                return
            
            # Создаем диалог выбора регрессии
            regr_window = tk.Toplevel(self.root)
            regr_window.title("Регрессионный анализ")
            regr_window.configure(bg=self.bg_color)
            
            # Выбор типа регрессии
            tk.Label(regr_window, text="Выберите тип регрессии:", 
                   bg=self.bg_color, fg=self.button_color).pack(pady=5)
            
            regr_type = tk.IntVar(value=1)
            tk.Radiobutton(regr_window, text="Линейная регрессия", variable=regr_type, value=1,
                         bg=self.bg_color, fg=self.button_color, selectcolor=self.bg_color).pack(anchor=tk.W)
            tk.Radiobutton(regr_window, text="Множественная регрессия", variable=regr_type, value=2,
                         bg=self.bg_color, fg=self.button_color, selectcolor=self.bg_color).pack(anchor=tk.W)
            
            # Выбор переменных
            tk.Label(regr_window, text="Выберите независимую переменную (X):", 
                   bg=self.bg_color, fg=self.button_color).pack(pady=5)
            x_var = tk.StringVar(regr_window)
            x_var.set(num_cols1[0])
            tk.OptionMenu(regr_window, x_var, *num_cols1).pack()
            
            tk.Label(regr_window, text="Выберите зависимую переменную (Y):",
                   bg=self.bg_color, fg=self.button_color).pack(pady=5)
            y_var = tk.StringVar(regr_window)
            y_var.set(num_cols2[0])
            tk.OptionMenu(regr_window, y_var, *num_cols2).pack()
            
            def run_regression():
                x_col = x_var.get()
                y_col = y_var.get()
                regr_type_val = regr_type.get()
                regr_window.destroy()
                
                # Подготовка данных
                X = self.df_sheet1[[x_col]].values if regr_type_val == 1 else self.df_sheet1[num_cols1].values
                y = self.df_sheet2[y_col].values
                
                # Линейная регрессия
                if regr_type_val == 1:
                    model = LinearRegression()
                    model.fit(X, y)
                    y_pred = model.predict(X)
                    
                    # Вывод результатов
                    self.output_field.insert(tk.END, "\nРезультаты линейной регрессии:\n")
                    self.output_field.insert(tk.END, f"Зависимость: {y_col} ~ {x_col}\n")
                    self.output_field.insert(tk.END, f"Коэффициент (наклон): {model.coef_[0]:.4f}\n")
                    self.output_field.insert(tk.END, f"Пересечение: {model.intercept_:.4f}\n")
                    self.output_field.insert(tk.END, f"R²: {model.score(X, y):.4f}\n")
                    
                    # Визуализация
                    self.plot_regression(X, y, y_pred, x_col, y_col, "Линейная регрессия")
                
                # Множественная регрессия
                else:
                    model = LinearRegression()
                    model.fit(X, y)
                    y_pred = model.predict(X)
                    
                    # Вывод результатов
                    self.output_field.insert(tk.END, "\nРезультаты множественной регрессии:\n")
                    self.output_field.insert(tk.END, f"Зависимость: {y_col} ~ {' + '.join(num_cols1)}\n")
                    for i, col in enumerate(num_cols1):
                        self.output_field.insert(tk.END, f"Коэффициент для {col}: {model.coef_[i]:.4f}\n")
                    self.output_field.insert(tk.END, f"Пересечение: {model.intercept_:.4f}\n")
                    self.output_field.insert(tk.END, f"R²: {model.score(X, y):.4f}\n")
                    
                    # Визуализация для первой переменной (для простоты)
                    self.plot_regression(X[:,0].reshape(-1,1), y, model.predict(X), num_cols1[0], y_col, "Множественная регрессия")
            
            tk.Button(regr_window, text="Выполнить", command=run_regression,
                    bg=self.button_color, fg=self.text_color).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета регрессионного анализа:\n{str(e)}")
    
    def plot_regression(self, X, y, y_pred, x_name, y_name, title):
        """Визуализация регрессионной модели"""
        if hasattr(self, 'regr_window') and self.regr_window.winfo_exists():
            self.regr_window.destroy()
        
        self.regr_window = tk.Toplevel(self.root)
        self.regr_window.title(title)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        self.current_figure = fig
        
        # Точечный график исходных данных
        ax.scatter(X, y, color='blue', label='Данные')
        
        # Линия регрессии
        ax.plot(X, y_pred, color='red', linewidth=2, label='Регрессия')
        
        # Настройка графика
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.set_title(f"{title}: {y_name} ~ {x_name}")
        ax.legend()
        ax.grid(True)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.regr_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_time_series(self):
        """Анализ данных во времени"""
        if self.df_sheet1 is None or self.df_sheet2 is None:
            messagebox.showwarning("Предупреждение", "Загрузите файл!")
            return
        
        try:
            # Получаем числовые столбцы из обоих листов (исключая год)
            numeric_cols1 = [col for col in self.df_sheet1.select_dtypes(include=['number']).columns if col != "Год"]
            numeric_cols2 = [col for col in self.df_sheet2.select_dtypes(include=['number']).columns if col != "Год"]
            
            if not numeric_cols1 and not numeric_cols2:
                messagebox.showwarning("Предупреждение", "Нет числовых данных для анализа!")
                return
            
            # Создаем окно выбора показателей
            selection = tk.Toplevel(self.root)
            selection.title("Выберите показатели")
            selection.geometry("400x500")
            selection.configure(bg=self.bg_color)
            
            # Фрейм для листа 1
            frame1 = tk.Frame(selection, bg=self.bg_color)
            frame1.pack(pady=5, fill=tk.X)
            tk.Label(frame1, text="Показатели из Листа1:", 
                   bg=self.bg_color, fg=self.button_color).pack(anchor=tk.W)
            
            vars1 = []
            for col in numeric_cols1:
                var = tk.BooleanVar()
                vars1.append(var)
                tk.Checkbutton(frame1, text=col, variable=var,
                             bg=self.bg_color, fg=self.button_color, 
                             selectcolor=self.bg_color).pack(anchor=tk.W, padx=20)
            
            # Фрейм для листа 2
            frame2 = tk.Frame(selection, bg=self.bg_color)
            frame2.pack(pady=5, fill=tk.X)
            tk.Label(frame2, text="Показатели из Листа2:", 
                   bg=self.bg_color, fg=self.button_color).pack(anchor=tk.W)
            
            vars2 = []
            for col in numeric_cols2:
                var = tk.BooleanVar()
                vars2.append(var)
                tk.Checkbutton(frame2, text=col, variable=var,
                             bg=self.bg_color, fg=self.button_color,
                             selectcolor=self.bg_color).pack(anchor=tk.W, padx=20)
            
            selected = []
            
            def on_ok():
                nonlocal selected
                selected = []
                # Добавляем выбранные показатели из Листа1
                for col, var in zip(numeric_cols1, vars1):
                    if var.get():
                        selected.append(("Лист1", col))
                # Добавляем выбранные показатели из Листа2
                for col, var in zip(numeric_cols2, vars2):
                    if var.get():
                        selected.append(("Лист2", col))
                selection.destroy()
                
                if not selected:
                    messagebox.showwarning("Предупреждение", "Не выбрано ни одного показателя!")
                    return
                
                self.plot_time_series(selected)
            
            tk.Button(selection, text="OK", command=on_ok,
                     bg=self.button_color, fg=self.text_color).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка построения графика:\n{str(e)}")
    
    def plot_time_series(self, selected):
        """Построение графика для выбранных показателей"""
        if hasattr(self, 'ts_window') and self.ts_window.winfo_exists():
            self.ts_window.destroy()
        
        self.ts_window = tk.Toplevel(self.root)
        self.ts_window.title("Анализ во времени")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        self.current_figure = fig
        
        # Используем стандартную цветовую схему matplotlib
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        
        # Строим графики для выбранных показателей
        for i, (sheet, col) in enumerate(selected):
            if sheet == "Лист1":
                df = self.df_sheet1
            else:
                df = self.df_sheet2
            
            ax.plot(df["Год"], df[col], 
                   label=f"{sheet}: {col}", marker='o', color=colors[i % len(colors)])
        
        ax.set_xlabel("Год")
        ax.set_ylabel("Значение")
        ax.set_title("Динамика показателей")
        ax.legend()
        ax.grid(True)
        
        # Улучшаем отображение
        plt.tight_layout()
        
        # Отображаем график
        canvas = FigureCanvasTkAgg(fig, master=self.ts_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_plot(self):
        """Сохранение текущего графика"""
        if not self.current_figure:
            messagebox.showwarning("Предупреждение", "Нет графика для сохранения!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
            
            if file_path:
                # Увеличиваем DPI и добавляем дополнительные отступы
                self.current_figure.savefig(file_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
                messagebox.showinfo("Успех", f"График сохранен:\n{file_path}")
                self.output_field.insert(tk.END, f"\nГрафик сохранен: {file_path}\n")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения графика:\n{str(e)}")
    
    def save_results(self):
        """Сохранение результатов анализа"""
        if self.df_sheet1 is None or self.df_sheet2 is None:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")))
            
            if file_path:
                with pd.ExcelWriter(file_path) as writer:
                    self.df_sheet1.to_excel(writer, sheet_name="Лист1", index=False)
                    self.df_sheet2.to_excel(writer, sheet_name="Лист2", index=False)
                    
                    if hasattr(self, 'corr_matrix'):
                        self.corr_matrix.to_excel(writer, sheet_name="Корреляция")
                
                messagebox.showinfo("Успех", f"Данные сохранены:\n{file_path}")
                self.output_field.insert(tk.END, f"\nДанные сохранены: {file_path}\n")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения данных:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()