
import tkinter as tk
from tkinter import messagebox
import math

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("400x600")
        self.expression = ""

        self.input_text = tk.StringVar()
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        input_field = tk.Entry(input_frame, textvariable=self.input_text, font=('arial', 20, 'bold'), bd=10, relief=tk.RIDGE, justify='right')
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=10)

        self.create_buttons()

    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+'),
            ('C', 'DEL', 'sqrt', '^'),
            ('sin', 'cos', 'tan', 'log'),
            ('ln', 'pi', 'e', 'exp')
        ]

        for row in buttons:
            row_frame = tk.Frame(button_frame)
            row_frame.pack(expand=True, fill='both')
            for btn in row:
                button = tk.Button(row_frame, text=btn, font=('arial', 18), relief=tk.GROOVE, border=0, command=lambda b=btn: self.on_button_click(b))
                button.pack(side='left', expand=True, fill='both')

    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
        elif char == 'DEL':
            self.expression = self.expression[:-1]
        elif char == '=':
            try:
                result = eval(self.parse_expression(self.expression))
                self.expression = str(result)
            except Exception as e:
                messagebox.showerror("Error", "Invalid Expression")
                self.expression = ""
        elif char == 'sqrt':
            self.expression += "math.sqrt("
        elif char == '^':
            self.expression += "**"
        elif char == 'sin':
            self.expression += "math.sin("
        elif char == 'cos':
            self.expression += "math.cos("
        elif char == 'tan':
            self.expression += "math.tan("
        elif char == 'log':
            self.expression += "math.log10("
        elif char == 'ln':
            self.expression += "math.log("
        elif char == 'pi':
            self.expression += "math.pi"
        elif char == 'e':
            self.expression += "math.e"
        elif char == 'exp':
            self.expression += "math.exp("
        else:
            self.expression += str(char)
        self.input_text.set(self.expression)

    def parse_expression(self, expr):
        return expr

if __name__ == "__main__":
    root = tk.Tk()
    calc = ScientificCalculator(root)
    root.mainloop()
