import tkinter as tk
from tkinter import ttk
import math
import re

class ModernCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modern Calculator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.current = "0"
        self.total = 0
        self.input_value = True
        self.result = False
        self.operator = ""
        self.memory = 0
        self.history = []
        
        # Configure style
        self.setup_styles()
        
        # Create widgets
        self.create_display()
        self.create_buttons()
        
        # Bind keyboard events
        self.root.bind('<Key>', self.key_press)
        self.root.focus_set()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Number.TButton', 
                       background='#2d2d2d', 
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 14))
        
        style.configure('Operator.TButton', 
                       background='#ff9500', 
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 14, 'bold'))
        
        style.configure('Function.TButton', 
                       background='#505050', 
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 12))
        
        style.configure('Equals.TButton', 
                       background='#ff9500', 
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 16, 'bold'))
        
        # Hover effects
        style.map('Number.TButton', background=[('active', '#3d3d3d')])
        style.map('Operator.TButton', background=[('active', '#ffb143')])
        style.map('Function.TButton', background=[('active', '#606060')])
        style.map('Equals.TButton', background=[('active', '#ffb143')])
    
    def create_display(self):
        # Main display frame
        display_frame = tk.Frame(self.root, bg='#1e1e1e', pady=20)
        display_frame.pack(fill=tk.X, padx=10)
        
        # History display
        self.history_var = tk.StringVar()
        history_label = tk.Label(display_frame, 
                               textvariable=self.history_var,
                               bg='#1e1e1e', 
                               fg='#888888',
                               font=('Arial', 12),
                               anchor='e')
        history_label.pack(fill=tk.X, pady=(0, 5))
        
        # Main display
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        display_label = tk.Label(display_frame, 
                               textvariable=self.display_var,
                               bg='#1e1e1e', 
                               fg='white',
                               font=('Arial', 36, 'bold'),
                               anchor='e')
        display_label.pack(fill=tk.X)
    
    def create_buttons(self):
        # Button frame
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights
        for i in range(6):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
        
        # Button layout
        buttons = [
            # Row 0 - Memory and Scientific functions
            [('MC', self.memory_clear, 'Function.TButton'), 
             ('MR', self.memory_recall, 'Function.TButton'), 
             ('M+', self.memory_add, 'Function.TButton'), 
             ('M-', self.memory_subtract, 'Function.TButton')],
            
            # Row 1 - Advanced functions
            [('√', lambda: self.scientific_operation('sqrt'), 'Function.TButton'), 
             ('x²', lambda: self.scientific_operation('square'), 'Function.TButton'), 
             ('1/x', lambda: self.scientific_operation('reciprocal'), 'Function.TButton'), 
             ('±', self.plus_minus, 'Function.TButton')],
            
            # Row 2 - Clear and basic functions
            [('C', self.clear, 'Function.TButton'), 
             ('CE', self.clear_entry, 'Function.TButton'), 
             ('⌫', self.backspace, 'Function.TButton'), 
             ('÷', lambda: self.operation('/'), 'Operator.TButton')],
            
            # Row 3 - Numbers and multiply
            [('7', lambda: self.number_press('7'), 'Number.TButton'), 
             ('8', lambda: self.number_press('8'), 'Number.TButton'), 
             ('9', lambda: self.number_press('9'), 'Number.TButton'), 
             ('×', lambda: self.operation('*'), 'Operator.TButton')],
            
            # Row 4 - Numbers and subtract
            [('4', lambda: self.number_press('4'), 'Number.TButton'), 
             ('5', lambda: self.number_press('5'), 'Number.TButton'), 
             ('6', lambda: self.number_press('6'), 'Number.TButton'), 
             ('-', lambda: self.operation('-'), 'Operator.TButton')],
            
            # Row 5 - Numbers and add
            [('1', lambda: self.number_press('1'), 'Number.TButton'), 
             ('2', lambda: self.number_press('2'), 'Number.TButton'), 
             ('3', lambda: self.number_press('3'), 'Number.TButton'), 
             ('+', lambda: self.operation('+'), 'Operator.TButton')],
        ]
        
        # Create buttons
        for row_idx, row in enumerate(buttons):
            for col_idx, (text, command, style) in enumerate(row):
                btn = ttk.Button(button_frame, 
                               text=text, 
                               command=command,
                               style=style)
                btn.grid(row=row_idx, column=col_idx, 
                        sticky='nsew', padx=2, pady=2)
        
        # Bottom row - 0, decimal, equals (special layout)
        zero_btn = ttk.Button(button_frame, 
                            text='0', 
                            command=lambda: self.number_press('0'),
                            style='Number.TButton')
        zero_btn.grid(row=6, column=0, columnspan=2, 
                     sticky='nsew', padx=2, pady=2)
        
        decimal_btn = ttk.Button(button_frame, 
                               text='.', 
                               command=self.decimal_press,
                               style='Number.TButton')
        decimal_btn.grid(row=6, column=2, 
                        sticky='nsew', padx=2, pady=2)
        
        equals_btn = ttk.Button(button_frame, 
                              text='=', 
                              command=self.equals_press,
                              style='Equals.TButton')
        equals_btn.grid(row=6, column=3, 
                       sticky='nsew', padx=2, pady=2)
    
    def number_press(self, num):
        if self.input_value is False:
            self.current = num
            self.input_value = True
        else:
            if self.current == "0":
                self.current = num
            else:
                self.current += num
        self.display_var.set(self.current)
    
    def decimal_press(self):
        if self.input_value is False:
            self.current = "0."
            self.input_value = True
        else:
            if "." not in self.current:
                self.current += "."
        self.display_var.set(self.current)
    
    def operation(self, op):
        if self.current == "":
            return
        
        if self.input_value:
            if self.result:
                self.total = float(self.current)
                self.result = False
            else:
                self.calculate()
        
        self.operator = op
        self.history_var.set(f"{self.format_number(self.total)} {op}")
        self.input_value = False
    
    def calculate(self):
        if self.operator == "" or not self.input_value:
            return
        
        try:
            current_num = float(self.current)
            if self.operator == "+":
                self.total += current_num
            elif self.operator == "-":
                self.total -= current_num
            elif self.operator == "*":
                self.total *= current_num
            elif self.operator == "/":
                if current_num != 0:
                    self.total /= current_num
                else:
                    self.display_var.set("Error")
                    return
        except:
            self.display_var.set("Error")
            return
        
        self.current = str(self.total)
        self.display_var.set(self.format_number(self.total))
    
    def equals_press(self):
        if self.operator != "" and self.input_value:
            self.calculate()
            self.history_var.set(f"{self.history_var.get()} {self.current} =")
            self.result = True
            self.input_value = False
            self.operator = ""
    
    def clear(self):
        self.current = "0"
        self.total = 0
        self.input_value = True
        self.result = False
        self.operator = ""
        self.display_var.set("0")
        self.history_var.set("")
    
    def clear_entry(self):
        self.current = "0"
        self.input_value = True
        self.display_var.set("0")
    
    def backspace(self):
        if len(self.current) > 1:
            self.current = self.current[:-1]
        else:
            self.current = "0"
        self.display_var.set(self.current)
    
    def plus_minus(self):
        if self.current != "0":
            if self.current.startswith("-"):
                self.current = self.current[1:]
            else:
                self.current = "-" + self.current
            self.display_var.set(self.current)
    
    def scientific_operation(self, op):
        try:
            num = float(self.current)
            if op == 'sqrt':
                if num >= 0:
                    result = math.sqrt(num)
                else:
                    self.display_var.set("Error")
                    return
            elif op == 'square':
                result = num ** 2
            elif op == 'reciprocal':
                if num != 0:
                    result = 1 / num
                else:
                    self.display_var.set("Error")
                    return
            
            self.current = str(result)
            self.display_var.set(self.format_number(result))
            self.input_value = False
            self.result = True
        except:
            self.display_var.set("Error")
    
    def memory_clear(self):
        self.memory = 0
    
    def memory_recall(self):
        self.current = str(self.memory)
        self.display_var.set(self.format_number(self.memory))
        self.input_value = False
    
    def memory_add(self):
        try:
            self.memory += float(self.current)
        except:
            pass
    
    def memory_subtract(self):
        try:
            self.memory -= float(self.current)
        except:
            pass
    
    def format_number(self, num):
        if isinstance(num, float) and num.is_integer():
            return str(int(num))
        elif isinstance(num, float):
            return f"{num:.10g}"
        return str(num)
    
    def key_press(self, event):
        key = event.char
        if key.isdigit():
            self.number_press(key)
        elif key == '.':
            self.decimal_press()
        elif key in ['+', '-', '*', '/']:
            op_map = {'*': '*', '/': '/'}
            self.operation(op_map.get(key, key))
        elif key in ['\r', '=']:  # Enter or equals
            self.equals_press()
        elif key == '\x08':  # Backspace
            self.backspace()
        elif key.lower() == 'c':
            self.clear()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    calculator = ModernCalculator()
    calculator.run()