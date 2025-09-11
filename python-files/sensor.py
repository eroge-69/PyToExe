import tkinter as tk
from tkinter import messagebox
def berechnen():
    try:
        c1 = float(entry_c1.get())
        V2 = float(entry_V2.get())
        c2_werte = entry_c2.get().split(",")
        ergebnisse = []
        for c2_str in c2_werte:
            c2 = float(c2_str.strip())
            V1 = (c2 * V2) / c1
            ergebnisse.append(f"{c2} ppm → {V1:.2f} mL Stammlösung + {V2 - V1:.2f} mL Lösungsmittel")
        messagebox.showinfo("Berechnung", "\n".join(ergebnisse))
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gültige Zahlen eingeben! (Konzentrationen mit Komma trennen)")
root = tk.Tk()
root.title("Labor Standardlösungen Rechner (ppm)")
label_c1 = tk.Label(root, text="Konzentration der Stammlösung (ppm):")
label_c1.pack()
entry_c1 = tk.Entry(root, width=20)
entry_c1.pack(pady=5)
label_V2 = tk.Label(root, text="Auffüllmenge Standerts (mL):")
label_V2.pack()
entry_V2 = tk.Entry(root, width=20)
entry_V2.pack(pady=5)
label_c2 = tk.Label(root, text="Konzentrationen der Standards (ppm, Mit Komma Trennen):")
label_c2.pack()
entry_c2 = tk.Entry(root, width=40)
entry_c2.pack(pady=5)
button = tk.Button(root, text="Berechnen", command=berechnen)
button.pack(pady=15)
root.mainloop()
