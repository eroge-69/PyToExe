import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        ct = float(entry_ct.get())
        hdl = float(entry_hdl.get())
        ldl = float(entry_ldl.get())
        tg = float(entry_tg.get())
        apo_a1 = float(entry_apoa1.get())
        apo_b = float(entry_apob.get())

        ct_hdl = ct / hdl
        ldl_hdl = ldl / hdl
        tg_hdl = tg / hdl
        apo_ratio = apo_b / apo_a1

        interpretacao = []

        if ct_hdl < 4.5:
            i1 = "CT/HDL: Bom"
        else:
            i1 = "CT/HDL: Risco aumentado"
        interpretacao.append(f"CT/HDL: {ct_hdl:.2f} → {i1}")

        if ldl_hdl < 3.5:
            i2 = "LDL/HDL: Ideal"
        else:
            i2 = "LDL/HDL: Risco aumentado"
        interpretacao.append(f"LDL/HDL: {ldl_hdl:.2f} → {i2}")

        if tg_hdl < 2:
            i3 = "TG/HDL: Excelente"
        elif tg_hdl <= 3:
            i3 = "TG/HDL: Moderado"
        else:
            i3 = "TG/HDL: Alto risco"
        interpretacao.append(f"TG/HDL: {tg_hdl:.2f} → {i3}")

        if apo_ratio < 0.7:
            i4 = "ApoB/ApoA1: Risco muito baixo"
        elif apo_ratio <= 0.9:
            i4 = "ApoB/ApoA1: Risco moderado"
        else:
            i4 = "ApoB/ApoA1: Alto risco"
        interpretacao.append(f"ApoB/ApoA1: {apo_ratio:.2f} → {i4}")

        messagebox.showinfo("Resultados", "\n".join(interpretacao))

    except ValueError:
        messagebox.showerror("Erro", "Insira valores válidos em todos os campos.")

root = tk.Tk()
root.title("Analisador Lipídico")

labels = ["Colesterol Total (mg/dL):", "HDL (mg/dL):", "LDL (mg/dL):",
          "Triglicerídeos (mg/dL):", "ApoA1 (mg/dL):", "ApoB (mg/dL):"]
entries = []

for i, text in enumerate(labels):
    tk.Label(root, text=text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

entry_ct, entry_hdl, entry_ldl, entry_tg, entry_apoa1, entry_apob = entries

tk.Button(root, text="Calcular", command=calcular).grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()