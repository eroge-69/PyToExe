import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os

# --------- Choisir Excel automatiquement dans le même dossier ----------
# Récupérer le dossier du script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chercher automatiquement le fichier .xlsx dans le dossier
excel_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".xlsx")]
if not excel_files:
    messagebox.showerror("Erreur", "Aucun fichier Excel trouvé dans le dossier!")
    exit()

EXCEL_PATH = os.path.join(BASE_DIR, excel_files[0])

SLOTS = ["8-9","9-10","10-11","11-12","14-15","15-16","16-17","17-18"]
DAYS = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]

# Fonction pour relire l'Excel et récupérer Lycées et Niveaux
def get_lycees_niveaux():
    xls = pd.ExcelFile(EXCEL_PATH)
    lycees = sorted(set(sheet.split("-")[0] for sheet in xls.sheet_names))
    niveaux = sorted(set(sheet.split("-")[1][:-1] for sheet in xls.sheet_names))
    return xls, lycees, niveaux

# Initialisation
xls, LYCEES, NIVEAUX = get_lycees_niveaux()

def find_free_classes(xls, selected_lycees, jour, niveaux, exclude_classes):
    result = {slot: [] for slot in SLOTS}
    day_to_row = { "Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3, "Vendredi": 4, "Samedi": 5 }

    for sheet in xls.sheet_names:
        if any(lycee in sheet for lycee in selected_lycees):
            sheet_niveau = sheet.split("-")[1][:-1]
            if sheet_niveau in niveaux:
                df = pd.read_excel(xls, sheet_name=sheet, header=4)
                row_idx = day_to_row[jour]
                if row_idx < len(df):
                    row = df.iloc[row_idx]
                    for idx, slot in enumerate(SLOTS):
                        val = str(row[idx+1]).strip()
                        if val.lower() == "libre":
                            lycee_abbr = ''.join([word[0] for word in sheet.split('-')[0].split()]).upper()
                            classe = f"{sheet.split('-')[1]} ({lycee_abbr})"
                            if classe not in exclude_classes:
                                result[slot].append(classe)
    return result

def rechercher():
    selected_indices = lst_lycees.curselection()
    selected_lycees = [lst_lycees.get(i) for i in selected_indices]
    jour = cb_jour.get()
    selected_niveaux = [niv for niv, var in niveaux_vars.items() if var.get() == 1]

    if not selected_lycees or not jour:
        messagebox.showwarning("Attention", "Choisir au moins un Lycée et un Jour")
        return
    if not selected_niveaux:
        messagebox.showwarning("Attention", "Choisir au moins un Niveau")
        return

    exclude_text = entry_exclude.get().strip()
    exclude_classes = [c.strip() for c in exclude_text.split(",")] if exclude_text else []

    for row in tree.get_children():
        tree.delete(row)

    free_map = find_free_classes(xls, selected_lycees, jour, selected_niveaux, exclude_classes)
    for slot in SLOTS:
        classes = ", ".join(free_map[slot]) if free_map[slot] else "-"
        tree.insert("", "end", values=(slot, classes))

def actualiser():
    global xls, LYCEES, NIVEAUX
    xls, LYCEES, NIVEAUX = get_lycees_niveaux()
    lst_lycees.delete(0, tk.END)
    for l in LYCEES:
        lst_lycees.insert(tk.END, l)
    for widget in frm_niveaux.winfo_children():
        widget.destroy()
    niveaux_vars.clear()
    for i, niv in enumerate(NIVEAUX):
        var = tk.IntVar()
        chk = tk.Checkbutton(frm_niveaux, text=niv, variable=var)
        chk.grid(row=i//5, column=i%5, sticky="w", padx=5, pady=2)
        niveaux_vars[niv] = var
    tk.Button(frm_niveaux, text="Tout", command=select_all).grid(row=2, column=0, pady=5)
    tk.Button(frm_niveaux, text="Aucun", command=unselect_all).grid(row=2, column=1, pady=5)

def select_all():
    for v in niveaux_vars.values():
        v.set(1)

def unselect_all():
    for v in niveaux_vars.values():
        v.set(0)

def copier_resultat():
    selected_rows = tree.selection()
    if not selected_rows:
        messagebox.showwarning("Copier", "Sélectionner au moins une ligne à copier !")
        return
    data = []
    for row_id in selected_rows:
        values = tree.item(row_id)["values"]
        data.append("\t".join(values))
    text = "\n".join(data)
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copier", "Les lignes sélectionnées ont été copiées dans le presse-papiers !")

# -------- GUI --------
root = tk.Tk()
root.title("Orientation - Heures creuses")
root.geometry("1000x750")

# Frame pour filtres
frm_top = tk.Frame(root)
frm_top.pack(pady=10)

lbl_lycee = tk.Label(frm_top, text="Lycée:")
lbl_lycee.grid(row=0, column=0, padx=5)
lst_lycees = tk.Listbox(frm_top, selectmode="multiple", height=5)
for l in LYCEES:
    lst_lycees.insert(tk.END, l)
lst_lycees.grid(row=0, column=1, padx=5)

lbl_jour = tk.Label(frm_top, text="Jour:")
lbl_jour.grid(row=0, column=2, padx=5)
cb_jour = ttk.Combobox(frm_top, values=DAYS, state="readonly")
cb_jour.grid(row=0, column=3, padx=5)

btn_actualiser = tk.Button(frm_top, text="Actualiser", command=actualiser)
btn_actualiser.grid(row=0, column=4, padx=5)

# Frame pour choisir niveaux
frm_niveaux = tk.LabelFrame(root, text="Choisir Niveaux")
frm_niveaux.pack(pady=10, fill="x")

niveaux_vars = {}
for i, niv in enumerate(NIVEAUX):
    var = tk.IntVar()
    chk = tk.Checkbutton(frm_niveaux, text=niv, variable=var)
    chk.grid(row=i//5, column=i%5, sticky="w", padx=5, pady=2)
    niveaux_vars[niv] = var

tk.Button(frm_niveaux, text="Tout", command=select_all).grid(row=2, column=0, pady=5)
tk.Button(frm_niveaux, text="Aucun", command=unselect_all).grid(row=2, column=1, pady=5)

# Frame pour exclure des classes
frm_exclude = tk.LabelFrame(root, text="Exclure des classes (séparer par des virgules)")
frm_exclude.pack(pady=10, fill="x")
entry_exclude = tk.Entry(frm_exclude, width=100)
entry_exclude.pack(padx=5, pady=5)

# Boutons rechercher et copier avec texte noir et gras
frm_buttons = tk.Frame(root)
frm_buttons.pack(pady=5)
btn_rechercher = tk.Button(frm_buttons, text="Rechercher", command=rechercher,
                           bg="white", fg="black", font=("Arial", 10, "bold"))
btn_rechercher.grid(row=0, column=0, padx=5)
btn_copier = tk.Button(frm_buttons, text="Copier Sélection", command=copier_resultat,
                       bg="white", fg="black", font=("Arial", 10, "bold"))
btn_copier.grid(row=0, column=1, padx=5)

# Frame pour tableau
frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True)

cols = ("Créneau", "Classes Libres")
tree = ttk.Treeview(frame_table, columns=cols, show="headings", selectmode="extended")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=200 if col=="Créneau" else 750)
tree.pack(fill="both", expand=True)

root.mainloop()
