
import tkinter as tk
from tkinter import ttk, messagebox
import math

def calculer_diametre():
    try:
        Q = float(entry_q.get())
        L = float(entry_l.get())
        delta_H = float(entry_dh.get())
        materiau = combo_materiau.get()

        m = 5
        beta = 2
        k_values = {
            "PEHD": 0.00141,
            "acier": 0.00165,
            "fonte neuve": 0.00123,
            "fonte ancienne": 0.00288
        }

        if materiau not in k_values:
            messagebox.showerror("Erreur", "Matériau non reconnu.")
            return

        K = k_values[materiau]
        D = ((K * L * Q**beta) / delta_H) ** (1 / m)
        result_var.set(f"Diamètre calculé : {D:.3f} m")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

root = tk.Tk()
root.title("Calcul du diamètre de conduite (gravitaire)")

tk.Label(root, text="Débit Q (m³/s):").grid(row=0, column=0, sticky="e")
entry_q = tk.Entry(root)
entry_q.grid(row=0, column=1)

tk.Label(root, text="Longueur L (m):").grid(row=1, column=0, sticky="e")
entry_l = tk.Entry(root)
entry_l.grid(row=1, column=1)

tk.Label(root, text="Charge disponible ΔH (m):").grid(row=2, column=0, sticky="e")
entry_dh = tk.Entry(root)
entry_dh.grid(row=2, column=1)

tk.Label(root, text="Matériau:").grid(row=3, column=0, sticky="e")
combo_materiau = ttk.Combobox(root, values=["PEHD", "acier", "fonte neuve", "fonte ancienne"])
combo_materiau.grid(row=3, column=1)
combo_materiau.set("PEHD")

tk.Button(root, text="Calculer", command=calculer_diametre).grid(row=4, columnspan=2, pady=10)

result_var = tk.StringVar()
tk.Label(root, textvariable=result_var, font=("Arial", 12, "bold")).grid(row=5, columnspan=2)

root.mainloop()
