
import random
import tkinter as tk
from tkinter import scrolledtext

class NumberGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pattern Number Generator")
        self.history = []
        self.high_value = 17.87

        self.text = scrolledtext.ScrolledText(root, width=40, height=20, font=("Courier", 12))
        self.text.pack(padx=10, pady=10)

        self.button = tk.Button(root, text="Generate Next", command=self.generate_next)
        self.button.pack(pady=5)

    def generate_next(self):
        step = len(self.history)
        value = self.generate_value(step)
        self.history.append(value)
        self.text.insert(tk.END, f"{value:.2f}\n")
        self.text.see(tk.END)

    def generate_value(self, step):
        if step % 15 == 0 and step != 0:
            self.high_value += random.uniform(0.3, 5.0)
            return self.high_value
        elif step > 5 and step % 15 < 10 and random.random() < 0.15:
            return random.uniform(8.0, 12.0)
        elif random.random() < 0.35:
            return random.uniform(2.0, 5.0)
        else:
            return random.uniform(1.00, 1.90)

if __name__ == "__main__":
    root = tk.Tk()
    app = NumberGeneratorApp(root)
    root.mainloop()
