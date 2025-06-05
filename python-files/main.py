import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import importlib.util
import sys
import os
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

COLOR = '#F0F0F0'
plt.rcParams['axes.facecolor'] = COLOR

class LabApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Численные методы")
        self.geometry("1200x800")
        self.configure(bg=COLOR)
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        
        # Интерфейс
        self._create_widgets()
        self.current_lab = None
        self.canvas = None

    def _setup_styles(self):
        self.bg_color = '#F5F5F5'
        self.primary_color = '#3F51B5'
        self.secondary_color = '#FF5722'
        self.text_color = '#212121'
        
        self.style.theme_use('clam')
        
        # Общие настройки
        self.style.configure('.', 
                            background=self.bg_color,
                            foreground=self.text_color,
                            font=('Helvetica', 10))
                            
        # Панели
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Input.TFrame', background='#FFFFFF', borderwidth=1, relief='solid')
        
        # Кнопки
        self.style.configure('TButton', 
                            background=self.primary_color,
                            foreground='white',
                            padding=8,
                            font=('Helvetica', 10, 'bold'),
                            borderwidth=0)
                            
                # Для кнопок
        self.style.map('TButton',
                      background=[
                          ('active', '#3949AB'),
                          ('pressed', '#283593')
                      ],
                      relief=[('pressed', 'sunken'), ('!pressed', 'groove')])
        
        # Метки
        self.style.configure('Param.TLabel', 
                            font=('Helvetica', 9),
                            foreground='#666666',
                            padding=5)
        
        # Поля ввода
        self.style.configure('TEntry',
                            fieldbackground='white',
                            foreground='#333333',
                            borderwidth=1,
                            relief='solid')
        
        # Текстовые области
        self.style.configure('Help.TScrolledText', 
                            background='#FFFDE7',
                            font=('Georgia', 10),
                            relief='flat')
                            
        self.style.configure('Output.TScrolledText', 
                            background='white',
                            font=('Consolas', 9),
                            relief='solid')
        

        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#3F51B5', '#FF5722', '#4CAF50', '#9C27B0'])
        
    def _create_widgets(self):
        # Панель выбора лабораторных
        self.header = ttk.Frame(self)
        self.header.pack(fill=tk.X, pady=5)
        
        labs = [
            ("1. Табулирование", 1),
            ("2. Дифференцирование", 2),
            ("3. Интегрирование", 3),
            ("4. Нелинейные ур-я", 4),
            ("5. Дифф. ур-я", 5)
        ]
        
        for text, num in labs:
            btn = ttk.Button(self.header, text=text, 
                            command=lambda n=num: self.show_lab(n))
            btn.pack(side=tk.LEFT, padx=5, ipadx=10)
            
        main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, 
                                       sashwidth=5, bg=self.bg_color)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Левая панель (параметры)
        self.input_frame = ttk.Frame(main_paned, style='TFrame')
        main_paned.add(self.input_frame, minsize=250, stretch='never')
            
            # Правая панель (результаты)
        right_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, 
                                        sashwidth=5, bg=self.bg_color)
            
            # Верхняя часть (справка + вывод)
        top_paned = tk.PanedWindow(right_paned, orient=tk.HORIZONTAL, 
                                      sashwidth=5, bg=self.bg_color)
        
        # Справочная информация
        help_frame = ttk.Frame(top_paned)
        self.help_panel = scrolledtext.ScrolledText(
            help_frame,
            wrap=tk.WORD,
            font=('Verdana', 9),
            bg='#f2ffe7',
            height=10
        )
        self.help_panel.pack(fill=tk.BOTH, expand=True)
        top_paned.add(help_frame, minsize=300)
        
        # Вывод результатов
        output_frame = ttk.Frame(top_paned)
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            height=15
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        top_paned.add(output_frame)
        
        right_paned.add(top_paned, height=300)
        
        # График
        self.graph_frame = ttk.Frame(right_paned)
        right_paned.add(self.graph_frame)
        
        main_paned.add(right_paned)
        
    def show_lab(self, lab_num):
        self._clear_previous()
        try:
            module = self._load_module(lab_num)
            self._setup_inputs(module.INPUT_FIELDS)
            self._show_help(getattr(module, 'HELP_TEXT', 'Справка отсутствует'))
            self.current_lab = module
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            
    def _show_help(self, text):
        self.help_panel.config(state=tk.NORMAL)
        self.help_panel.delete('1.0', tk.END)
        self.help_panel.insert(tk.END, text)
        self.help_panel.config(state=tk.DISABLED)
            
    def _load_module(self, lab_num):
        lab_file = f"lab{lab_num}.py"
        if not os.path.exists(lab_file):
            raise FileNotFoundError(f"Файл {lab_file} не найден!")
            
        spec = importlib.util.spec_from_file_location(f"lab{lab_num}", lab_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"lab{lab_num}"] = module
        spec.loader.exec_module(module)
        return module
            
    def _setup_inputs(self, fields):
        # Очистка предыдущих полей
        for widget in self.input_frame.winfo_children():
            widget.destroy()
            
        self.entries = {}
        
        # Создание полей ввода
        ttk.Label(self.input_frame, text="Параметры:", style='Param.TLabel').pack(anchor='w')
        
        for field in fields:
            frame = ttk.Frame(self.input_frame)
            frame.pack(fill=tk.X, pady=2)
            
            label = ttk.Label(frame, text=field['label'], width=15, style='Param.TLabel')
            label.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.insert(0, field['default'])
            entry.pack(side=tk.RIGHT, expand=True)
            self.entries[field['name']] = entry
            
        # Кнопка расчета
        btn = ttk.Button(self.input_frame, text="Рассчитать", command=self.run_calculation)
        btn.pack(pady=10)
            
    def run_calculation(self):
        if not self.current_lab:
            return
            
        try:
            params = {name: entry.get() for name, entry in self.entries.items()}
            output, fig = self.current_lab.run(params)
            
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, output)
            
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                
            if fig:
                self.canvas = FigureCanvasTkAgg(fig, self.graph_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
        except Exception as e:
            messagebox.showerror("Ошибка вычислений", str(e))
            
    def _clear_previous(self):
        self.output_text.delete('1.0', tk.END)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.current_lab = None

if __name__ == "__main__":
    app = LabApp()
    app.mainloop()