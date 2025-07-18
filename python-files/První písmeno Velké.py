# Promt: napiš kod v pythonu. Grafické rozhraní, kam se vloží text a tlačítko, které první písmeno v textu převede na velké písmeno


import tkinter as tk
from tkinter import messagebox

def capitalize_first_letter():
    text = entry.get()
    if text:
        new_text = text[0].upper() + text[1:]
        entry.delete(0, tk.END)
        entry.insert(0, new_text)
    else:
        messagebox.showwarning("Varování", "Zadejte prosím text.")

# Vytvoření hlavního okna
root = tk.Tk()
root.title("Velké první písmeno")

# Vytvoření vstupního pole
entry = tk.Entry(root, width=40)
entry.pack(pady=10)

# Tlačítko pro změnu prvního písmena na velké
button = tk.Button(root, text="Změň první písmeno na velké", command=capitalize_first_letter)
button.pack(pady=5)

# Spuštění aplikace
root.mainloop()

