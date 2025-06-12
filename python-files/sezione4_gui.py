
import tkinter as tk
from tkinter import ttk, messagebox

# Dati della Sezione 4
physical_forms = [
    "granules", "powder", "flakes", "fiber", "liquid", "chopped / grinded", "paste"
]

pre_mix_options = [
    "Pre-MIX Powders", "Pre-MIX Pow + Gran", "Pre-MIX Pow + Liq", "Pre-MIX Pow + Gran + Liq"
]

properties = ["MFI (g/10 min)", "Density (Kg/dm3)", "Bulk Density (Kg/dm3)",
              "Viscosity (mPas)", "Length(mm)"]

# Funzione per mostrare i risultati
def show_results():
    result = "=== Selected Material Characteristics ===\n"
    result += f"Physical Form: {form_var.get()}\n"
    result += f"Pre-MIX: {premix_var.get()}\n"
    for prop in properties:
        val = prop_vars[prop].get()
        if val:
            result += f"{prop}: {val}\n"
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

# Finestra principale
root = tk.Tk()
root.title("Material Characteristics - Sezione 4")
root.geometry("450x500")

# Physical Form
ttk.Label(root, text="Select Physical Form:").pack(anchor="w", padx=10, pady=5)
form_var = tk.StringVar()
form_menu = ttk.Combobox(root, textvariable=form_var, values=physical_forms)
form_menu.pack(fill="x", padx=10)

# Pre-MIX
ttk.Label(root, text="Select Pre-MIX Type:").pack(anchor="w", padx=10, pady=5)
premix_var = tk.StringVar()
premix_menu = ttk.Combobox(root, textvariable=premix_var, values=pre_mix_options)
premix_menu.pack(fill="x", padx=10)

# Proprietà fisiche
ttk.Label(root, text="Insert Physical Properties:").pack(anchor="w", padx=10, pady=10)
prop_vars = {}
for prop in properties:
    frame = ttk.Frame(root)
    frame.pack(fill="x", padx=10)
    ttk.Label(frame, text=prop + ":").pack(side="left")
    entry = ttk.Entry(frame)
    entry.pack(fill="x", expand=True)
    prop_vars[prop] = entry

# Bottone
ttk.Button(root, text="Show Results", command=show_results).pack(pady=10)

# Risultato
result_text = tk.Text(root, height=10)
result_text.pack(fill="both", padx=10, pady=10)

root.mainloop()
