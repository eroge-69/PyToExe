# calculator.py
import tkinter as tk
from tkinter import ttk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Dyy")
        self.geometry("320x420")
        self.resizable(False, False)

        self.expression = ""
        self.result_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Display
        entry = ttk.Entry(self, textvariable=self.result_var, font=("Arial", 20), justify="right")
        entry.pack(fill="x", padx=10, pady=10, ipady=10)

        # Buttons
        buttons = [
            ("7",), ("8",), ("9",), ("/",),
            ("4",), ("5",), ("6",), ("*",),
            ("1",), ("2",), ("3",), ("-",),
            ("0",), (".",), ("=",), ("+",),
            ("C",)
        ]

        frame = ttk.Frame(self)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        row, col = 0, 0
        for btn in buttons:
            text = btn[0]
            b = ttk.Button(frame, text=text, command=lambda t=text: self.on_button_click(t))
            b.grid(row=row, column=col, ipadx=10, ipady=10, sticky="nsew", padx=5, pady=5)

            col += 1
            if col > 3:
                col = 0
                row += 1

        # Grid expand
        for i in range(5):
            frame.rowconfigure(i, weight=1)
        for i in range(4):
            frame.columnconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == "C":
            self.expression = ""
            self.result_var.set("")
        elif char == "=":
            try:
                result = str(eval(self.expression))
                self.result_var.set(result)
                self.expression = result
            except Exception:
                self.result_var.set("Error")
                self.expression = ""
        else:
            self.expression += str(char)
            self.result_var.set(self.expression)


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()