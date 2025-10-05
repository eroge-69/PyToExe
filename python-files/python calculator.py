#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from math import sqrt

# --- Main Window ---
root = tk.Tk()
root.title("Python GUI Calculator")
root.geometry("320x520")
root.resizable(False, False)
root.configure(bg="#222")

# --- Display ---
display = tk.Entry(
    root, font=("Arial", 24), border=0, relief=tk.FLAT,
    justify="right", bg="#333", fg="white"
)
display.grid(row=0, column=0, columnspan=4, ipadx=8, ipady=20, pady=10, padx=10, sticky="nsew")

# --- Button Click Handler ---
def click(event):
    text = event.widget.cget("text")
    current = display.get()

    try:
        if text == "=":
            # Evaluate safely, allowing only sqrt and abs
            result = eval(current, {"_builtins_": None}, {"sqrt": sqrt, "abs": abs})
            display.delete(0, tk.END)
            display.insert(tk.END, str(result))
        elif text == "C":
            display.delete(0, tk.END)
        elif text == "√":
            if current:
                result = sqrt(float(current))
                display.delete(0, tk.END)
                display.insert(tk.END, str(result))
        elif text == "Abs":
            if current:
                result = abs(float(current))
                display.delete(0, tk.END)
                display.insert(tk.END, str(result))
        elif text == "⌫":
            display.delete(len(current) - 1, tk.END)
        else:
            display.insert(tk.END, text)
    except Exception:
        display.delete(0, tk.END)
        display.insert(tk.END, "Error")

# --- Buttons Layout ---
buttons = [
    ["C", "√", "Abs", "⌫"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

# --- Create Buttons ---
for r, row in enumerate(buttons, start=1):
    for c, text in enumerate(row):
        if text == "C":
            color = "#e74c3c"
        elif text == "=":
            color = "#2ecc71"
        elif text == "⌫":
            color = "#f39c12"
        elif text in ("Abs", "√"):
            color = "#9b59b6"
        else:
            color = "#444"

        btn = tk.Button(
            root, text=text, font=("Arial", 18, "bold"),
            bg=color, fg="white", activebackground="#555",
            activeforeground="white"
        )
        btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5, ipadx=5, ipady=10)
        btn.bind("<Button-1>", click)

# --- Responsive Layout ---
for i in range(6):
    root.rowconfigure(i, weight=1)
for i in range(4):
    root.columnconfigure(i, weight=1)

root.mainloop()


# In[ ]:





# In[ ]:




