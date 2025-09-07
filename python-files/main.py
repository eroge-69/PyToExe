import tkinter as tk
from tkinter import ttk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("DesktopCalculator")
        self.root.iconbitmap('Calculator.ico')
        self.root.geometry("360x500")
        self.root.resizable(True, True)
        
        self.expression = ""
        
        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 14), padding=10)

        # Entry display
        self.display = tk.Entry(root, font=("Segoe UI", 20), borderwidth=2, relief="solid", justify="right")
        self.display.pack(fill="both", ipadx=8, ipady=15, pady=10, padx=10)

        # Buttons layout
        buttons_frame = tk.Frame(root)
        buttons_frame.pack()

        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("=", 3, 2), ("+", 3, 3),
        ]

        for (text, row, col) in buttons:
            button = ttk.Button(buttons_frame, text=text, command=lambda t=text: self.on_button_click(t))
            button.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        # Adjust grid scaling
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)
            buttons_frame.rowconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == "=":
            try:
                result = str(eval(self.expression))
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, result)
                self.expression = result
            except:
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, "Error")
                self.expression = ""
        else:
            self.expression += str(char)
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, self.expression)


if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
