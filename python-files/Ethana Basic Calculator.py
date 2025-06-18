import tkinter as tk

class EthanaBasicCalculator:
    def __init__(self, root):
        self.root = root
        root.title("Ethana Basic Calculator")

        self.entry = tk.Entry(root, font=("Arial", 18), borderwidth=2, relief="groove", justify="right")
        self.entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('C', 5, 0)
        ]

        for (text, row, col) in buttons:
            btn = tk.Button(root, text=text, font=("Arial", 16), command=lambda t=text: self.on_click(t))
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        for i in range(6):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)

    def on_click(self, char):
        if char == "=":
            try:
                result = eval(self.entry.get())
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, result)
            except Exception:
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, "Error")
        elif char == "C":
            self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, char)

if __name__ == "__main__":
    root = tk.Tk()
    app = EthanaBasicCalculator(root)
    root.geometry("300x400")
    root.minsize(200, 300)
    root.mainloop()
