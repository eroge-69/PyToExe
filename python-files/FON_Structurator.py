import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

def create_structure():
    client = entry_nume.get().strip()
    tip_eveniment = combo_tip.get()
    data = entry_data.get().strip()
    locatie = entry_locatie.get().strip()

    if not client or not tip_eveniment or not data or not locatie:
        messagebox.showwarning("Eroare", "Completează toate câmpurile!")
        return

    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Dată invalidă", "Formatul trebuie să fie YYYY-MM-DD.")
        return

    folder_principal = f"{tip_eveniment.upper()} - {client} - {data}"
    cale_completa = os.path.join(locatie, folder_principal)

    structura = [
        "FOTO/RAW",
        "FOTO/EDITATE",
        "VIDEO/BRUT",
        "VIDEO/MONTAT",
        "DOCUMENTE",
        "EXPORT/pentru client",
        "EXPORT/pentru backup"
    ]

    try:
        for folder in structura:
            os.makedirs(os.path.join(cale_completa, folder), exist_ok=True)
        messagebox.showinfo("Succes", f"Structura a fost creată în:\n{cale_completa}")
    except Exception as e:
        messagebox.showerror("Eroare", str(e))

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_locatie.delete(0, tk.END)
        entry_locatie.insert(0, folder)

# UI
root = tk.Tk()
root.title("FON Structurator - Fulaș Nicolae")
root.geometry("400x300")
root.resizable(False, False)

tk.Label(root, text="Nume client:").pack()
entry_nume = tk.Entry(root, width=50)
entry_nume.pack()

tk.Label(root, text="Tip eveniment:").pack()
combo_tip = ttk.Combobox(root, values=["Nuntă", "Botez", "Majorat", "Cununie"])
combo_tip.pack()

tk.Label(root, text="Data (YYYY-MM-DD):").pack()
entry_data = tk.Entry(root)
entry_data.pack()

tk.Label(root, text="Locație salvare:").pack()
frame = tk.Frame(root)
frame.pack()
entry_locatie = tk.Entry(frame, width=35)
entry_locatie.pack(side=tk.LEFT)
tk.Button(frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)

tk.Button(root, text="Creează Structura", command=create_structure, bg="#4CAF50", fg="white").pack(pady=20)

root.mainloop()
