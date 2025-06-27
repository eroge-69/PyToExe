
import tkinter as tk
from tkinter import messagebox
import math

def calculate_das28():
    try:
        tjc = float(entry_tjc.get())
        sjc = float(entry_sjc.get())
        crp = float(entry_crp.get())
        gh = float(entry_gh.get())

        das28 = 0.56 * math.sqrt(tjc) + 0.28 * math.sqrt(sjc) + 0.36 * math.log(crp + 1) + 0.014 * gh + 0.96
        result = f"VAS: {int(gh)} (škála 0-100) DAS28-CRP: {das28:.2f}"

        root.clipboard_clear()
        root.clipboard_append(result)
        root.update()

        messagebox.showinfo("Výsledek DAS28-CRP(4)", f"{result}\n\n(bylo zkopírováno do schránky)")
    except ValueError:
        messagebox.showerror("Chyba", "Zadejte platné číselné hodnoty.")

root = tk.Tk()
root.title("DAS28-CRP(4) Kalkulačka")

tk.Label(root, text="Počet citlivých kloubů (TJC28):").grid(row=0, column=0, sticky="e")
entry_tjc = tk.Entry(root)
entry_tjc.grid(row=0, column=1)

tk.Label(root, text="Počet oteklých kloubů (SJC28):").grid(row=1, column=0, sticky="e")
entry_sjc = tk.Entry(root)
entry_sjc.grid(row=1, column=1)

tk.Label(root, text="CRP (mg/l):").grid(row=2, column=0, sticky="e")
entry_crp = tk.Entry(root)
entry_crp.grid(row=2, column=1)

tk.Label(root, text="GH (VAS 0-100):").grid(row=3, column=0, sticky="e")
entry_gh = tk.Entry(root)
entry_gh.grid(row=3, column=1)

tk.Button(root, text="Spočítat DAS28", command=calculate_das28).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
