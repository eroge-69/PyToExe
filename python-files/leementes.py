
import tkinter as tk
from tkinter import messagebox

def adivinar_numero():
    numero = entry.get()
    if numero.strip() == "":
        messagebox.showwarning("Advertencia", "¡Debes escribir un número!")
    else:
        messagebox.showinfo("Leementes", f"¡Sabía que ibas a pensar en el número {numero}!")
        root.destroy()

root = tk.Tk()
root.title("Leementes - Adivino Mental")
root.geometry("300x150")
root.resizable(False, False)

label = tk.Label(root, text="Piensa en un número...\n¡Y escríbelo aquí abajo!")
label.pack(pady=10)

entry = tk.Entry(root, justify='center', font=("Arial", 14))
entry.pack(pady=5)

button = tk.Button(root, text="¡Revelar!", command=adivinar_numero)
button.pack(pady=10)

root.mainloop()
