import tkinter as tk
from tkinter import ttk

# --- Fonctions conversions ---
def euro_to_dollar(euro):
    return euro * 1.07  # taux fictif
def dollar_to_euro(dollar):
    return dollar / 1.07
def c_to_f(c):
    return (c * 9/5) + 32
def c_to_k(c):
    return c + 273.15

# --- Logique ---
def add_digit(digit):
    display_var.set(display_var.get() + str(digit))

def clear_display():
    display_var.set("")

def backspace():
    display_var.set(display_var.get()[:-1])

def convert_currency():
    try:
        val = float(display_var.get())
        if mode_var.get() == "EUR -> USD":
            res = f"{val} € = {euro_to_dollar(val):.2f} $"
        else:
            res = f"{val} $ = {dollar_to_euro(val):.2f} €"
        display_var.set(res)
    except:
        display_var.set("Erreur")

def convert_temp():
    try:
        c = float(display_var.get())
        f = c_to_f(c)
        k = c_to_k(c)
        res = f"{c}°C → {f:.2f}°F | {k:.2f}K"
        display_var.set(res)
    except:
        display_var.set("Erreur")

# --- Interface ---
root = tk.Tk()
root.title("Convertisseur Style Calculatrice")
root.geometry("320x420")
root.resizable(False, False)

# Affichage
display_var = tk.StringVar()
display = tk.Entry(root, textvariable=display_var, font=("Segoe UI", 18), justify="right", bd=5, relief="sunken")
display.pack(fill="x", padx=10, pady=10, ipady=10)

# Sélecteur de mode
mode_var = tk.StringVar(value="EUR -> USD")
mode_frame = tk.Frame(root)
mode_frame.pack(pady=5)
ttk.Radiobutton(mode_frame, text="EUR -> USD", variable=mode_var, value="EUR -> USD").grid(row=0, column=0, padx=5)
ttk.Radiobutton(mode_frame, text="USD -> EUR", variable=mode_var, value="USD -> EUR").grid(row=0, column=1, padx=5)

# Grille de boutons (style calculatrice)
btns_frame = tk.Frame(root)
btns_frame.pack(padx=10, pady=10)

buttons = [
    ("7", lambda: add_digit(7)), ("8", lambda: add_digit(8)), ("9", lambda: add_digit(9)), ("⌫", backspace),
    ("4", lambda: add_digit(4)), ("5", lambda: add_digit(5)), ("6", lambda: add_digit(6)), ("C", clear_display),
    ("1", lambda: add_digit(1)), ("2", lambda: add_digit(2)), ("3", lambda: add_digit(3)), ("Temp", convert_temp),
    ("0", lambda: add_digit(0)), (".", lambda: add_digit(".")), ("€/$", convert_currency), ("Exit", root.quit),
]

r, c = 0, 0
for (text, cmd) in buttons:
    b = tk.Button(btns_frame, text=text, command=cmd, font=("Segoe UI", 14), width=5, height=2, relief="raised")
    b.grid(row=r, column=c, padx=5, pady=5)
    c += 1
    if c > 3:
        c = 0
        r += 1

root.mainloop()
