import tkinter as tk
from tkinter import font, messagebox
import math

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcTon")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#2e2e2e')
        
        # Create custom fonts
        display_font = font.Font(family='Arial', size=24, weight='bold')
        button_font = font.Font(family='Arial', size=14)
        footer_font = font.Font(family='Arial', size=10)
        
        # Create display frame
        display_frame = tk.Frame(self.root, bg='#2e2e2e')
        display_frame.pack(pady=20, padx=20, fill=tk.X)
        
        # Create display with BLACK text on WHITE background
        self.display_var = tk.StringVar()
        self.display = tk.Entry(display_frame, textvariable=self.display_var, 
                               font=display_font, bd=1, relief=tk.SOLID,
                               bg='white', fg='black', justify=tk.RIGHT,
                               state='readonly', insertwidth=0)
        self.display.pack(fill=tk.X, ipady=15)
        
        # Create button frame
        button_frame = tk.Frame(self.root, bg='#2e2e2e')
        button_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Button configuration
        buttons = [
            ('7', '#4a4a4a'), ('8', '#4a4a4a'), ('9', '#4a4a4a'), ('/', '#ff9500'), ('C', '#ff3b30'),
            ('4', '#4a4a4a'), ('5', '#4a4a4a'), ('6', '#4a4a4a'), ('*', '#ff9500'), ('⌫', '#ff9500'),
            ('1', '#4a4a4a'), ('2', '#4a4a4a'), ('3', '#4a4a4a'), ('-', '#ff9500'), ('√', '#ff9500'),
            ('0', '#4a4a4a'), ('.', '#4a4a4a'), ('=', '#4a4a4a'), ('+', '#ff9500'), ('^', '#ff9500'),
            ('(', '#4a4a4a'), (')', '#4a4a4a'), ('%', '#ff9500'), ('π', '#ff9500'), ('sin', '#ff9500'),
            ('cos', '#ff9500'), ('tan', '#ff9500'), ('log', '#ff9500'), ('ln', '#ff9500'), ('±', '#ff9500')
        ]
        
        # Create buttons
        row, col = 0, 0
        for (text, bg_color) in buttons:
            if text == '=':
                btn = tk.Button(button_frame, text=text, font=button_font, bd=0, 
                               bg=bg_color, fg='white', command=lambda t=text: self.on_equal())
            else:
                btn = tk.Button(button_frame, text=text, font=button_font, bd=0, 
                               bg=bg_color, fg='white', command=lambda t=text: self.on_button_click(t))
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            btn.config(height=1, width=1, relief=tk.RAISED)
            
            col += 1
            if col > 4:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(5):
            button_frame.columnconfigure(i, weight=1)
        for i in range(6):
            button_frame.rowconfigure(i, weight=1)
        
        # Footer
        footer = tk.Label(self.root, text="Developed By Md Milton Babu", font=footer_font, 
                         bg='#2e2e2e', fg='#aaaaaa')
        footer.pack(side=tk.BOTTOM, pady=10)
        
        # Initialize calculation
        self.current_input = ""
        self.history = []

    def on_button_click(self, value):
        if value == 'C':
            self.current_input = ""
        elif value == '⌫':
            self.current_input = self.current_input[:-1]
        elif value == '√':
            self.current_input += 'math.sqrt('
        elif value == 'π':
            self.current_input += str(math.pi)
        elif value == '^':
            self.current_input += '**'
        elif value == 'sin':
            self.current_input += 'math.sin(math.radians('
        elif value == 'cos':
            self.current_input += 'math.cos(math.radians('
        elif value == 'tan':
            self.current_input += 'math.tan(math.radians('
        elif value == 'log':
            self.current_input += 'math.log10('
        elif value == 'ln':
            self.current_input += 'math.log('
        elif value == '±':
            if self.current_input and self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
        else:
            self.current_input += value
            
        self.display_var.set(self.current_input)

    def on_equal(self):
        try:
            # Replace visual symbols with Python operators
            expression = self.current_input
            expression = expression.replace('%', '/100')
            
            # Evaluate expression
            result = eval(expression)
            self.history.append(f"{self.current_input} = {result}")
            
            # Update display
            self.display_var.set(result)
            self.current_input = str(result)
        except Exception as e:
            messagebox.showerror("Error", "Invalid Expression")
            self.current_input = ""
            self.display_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()