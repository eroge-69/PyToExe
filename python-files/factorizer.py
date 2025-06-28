
import tkinter as tk
from tkinter import messagebox

def factorize(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i == 0:
            factors.append(i)
            n //= i
        else:
            i += 1
    if n > 1:
        factors.append(n)
    return factors

def on_factorize():
    try:
        num = int(entry.get())
        if num < 2:
            raise ValueError
        result = factorize(num)
        result_label.config(text=" x ".join(map(str, result)))
    except:
        messagebox.showerror("Invalid Input", "Please enter a valid integer greater than 1.")

# GUI
root = tk.Tk()
root.title("Prime Factorizer")
root.geometry("300x150")

tk.Label(root, text="Enter a number:").pack(pady=5)
entry = tk.Entry(root)
entry.pack()

tk.Button(root, text="Factorize", command=on_factorize).pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack()

root.mainloop()
