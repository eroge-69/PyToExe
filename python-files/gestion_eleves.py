#!/usr/bin/env python3
"""
Gestion simple des élèves prêts pour examen bout du monde- Application Tkinter + SQLite
Fonctions :
- Ajouter / modifier / supprimer un élève (Nom, Prénom, Mois, Prêt yes/no, Remarque)
- Filtrer par mois
- Trier par Nom / Mois
- Export CSV de la liste affichée
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import csv
import os

DB_FILE = "eleves.db"

# --- Base de données --------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS eleves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT,
        mois TEXT,
        pret INTEGER DEFAULT 0,
        remarque TEXT
    )
    """)
    conn.commit()
    return conn

# --- Opérations BDD ---------------------------------------------------------
def ajouter_eleve(conn, nom, prenom, mois, pret, remarque):
    cur = conn.cursor()
    cur.execute("INSERT INTO eleves (nom, prenom, mois, pret, remarque) VALUES (?, ?, ?, ?, ?)",
                (nom.strip(), prenom.strip(), mois, int(bool(pret)), remarque.strip()))
    conn.commit()

def modifier_eleve(conn, eid, nom, prenom, mois, pret, remarque):
    cur = conn.cursor()
    cur.execute("UPDATE eleves SET nom=?, prenom=?, mois=?, pret=?, remarque=? WHERE id=?",
                (nom.strip(), prenom.strip(), mois, int(bool(pret)), remarque.strip(), eid))
    conn.commit()

def supprimer_eleve(conn, eid):
    cur = conn.cursor()
    cur.execute("DELETE FROM eleves WHERE id=?", (eid,))
    conn.commit()

def lire_eleves(conn, filtre_mois=None, ordre="nom"):
    cur = conn.cursor()
    q = "SELECT id, nom, prenom, mois, pret, remarque FROM eleves"
    params = ()
    if filtre_mois and filtre_mois != "Tous":
        q += " WHERE mois = ?"
        params = (filtre_mois,)
    if ordre == "nom":
        q += " ORDER BY nom COLLATE NOCASE"
    elif ordre == "mois":
        q += " ORDER BY mois"
    cur.execute(q, params)
    return cur.fetchall()

# --- Interface --------------------------------------------------------------
class App:
    MONTHS = ["Tous","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

    def __init__(self, root):
        self.root = root
        self.root.title("Gestion élèves - Prêts examen")
        self.conn = init_db()
        self.sort_order = "nom"

        # Top frame - form
        frm = ttk.Frame(root, padding=10)
        frm.pack(fill="x")


        ttk.Label(frm, text="Nom").grid(row=0, column=0, sticky="w")
        self.entry_nom = ttk.Entry(frm, width=20)
        self.entry_nom.grid(row=0, column=1, padx=5)

        ttk.Label(frm, text="Prénom").grid(row=0, column=2, sticky="w")
        self.entry_prenom = ttk.Entry(frm, width=20)
        self.entry_prenom.grid(row=0, column=3, padx=5)

        ttk.Label(frm, text="Mois prévu").grid(row=1, column=0, sticky="w", pady=6)
        self.combo_mois = ttk.Combobox(frm, values=self.MONTHS[1:], state="readonly", width=18)
        self.combo_mois.grid(row=1, column=1, padx=5)
        self.combo_mois.set(self.MONTHS[1])

        self.pret_var = tk.IntVar()
        ttk.Checkbutton(frm, text="Prêt", variable=self.pret_var).grid(row=1, column=2, sticky="w")


        ttk.Label(frm, text="Remarque").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_remarque = ttk.Entry(frm, width=60)
        self.entry_remarque.grid(row=2, column=1, columnspan=3, padx=5)

        ttk.Button(frm, text="Ajouter", command=self.ajouter).grid(row=0, column=4, rowspan=2, padx=8)
        ttk.Button(frm, text="Modifier sélection", command=self.modifier_selection).grid(row=2, column=4, padx=8)
        ttk.Button(frm, text="Supprimer sélection", command=self.supprimer_selection).grid(row=3, column=4, padx=8)

        # Middle frame - filters and export
        mid = ttk.Frame(root, padding=10)
        mid.pack(fill="x")
        ttk.Label(mid, text="Filtrer par mois").pack(side="left")
        self.filter_var = tk.StringVar(value="Tous")
        self.filter_combo = ttk.Combobox(mid, values=self.MONTHS, textvariable=self.filter_var, state="readonly", width=15)
        self.filter_combo.pack(side="left", padx=6)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.rafraichir())

        ttk.Label(mid, text="Trier par").pack(side="left", padx=(20,4))
        self.sort_combo = ttk.Combobox(mid, values=["nom","mois"], state="readonly", width=8)
        self.sort_combo.pack(side="left")
        self.sort_combo.set("nom")
        self.sort_combo.bind("<<ComboboxSelected>>", self.change_sort)

        ttk.Button(mid, text="Exporter CSV", command=self.export_csv).pack(side="right", padx=6)
        ttk.Button(mid, text="Importer CSV", command=self.import_csv).pack(side="right")


        # Treeview - liste
        cols = ("id","nom","prenom","mois","pret","remarque")
        self.tree = ttk.Treeview(root, columns=cols, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("prenom", text="Prénom")
        self.tree.heading("mois", text="Mois")
        self.tree.heading("pret", text="Prêt")
        self.tree.heading("remarque", text="Remarque")
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nom", width=140)
        self.tree.column("prenom", width=120)
        self.tree.column("mois", width=90, anchor="center")
        self.tree.column("pret", width=60, anchor="center")
        self.tree.column("remarque", width=240)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

        self.rafraichir()

    # --- actions
    def ajouter(self):
        nom = self.entry_nom.get().strip()
        if not nom:
            messagebox.showwarning("Attention", "Veuillez saisir le nom.")
            return
        prenom = self.entry_prenom.get().strip()
        mois = self.combo_mois.get() or ""
        remark = self.entry_remarque.get().strip()
        pret = self.pret_var.get()
        ajouter_eleve(self.conn, nom, prenom, mois, pret, remark)
        self.entry_nom.delete(0, "end")
        self.entry_prenom.delete(0, "end")
        self.entry_remarque.delete(0, "end")
        self.pret_var.set(0)
        self.rafraichir()

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0])["values"]
        return item  # id, nom, prenom, mois, pret, remarque

    def modifier_selection(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez une ligne à modifier.")
            return
        eid = sel[0]
        nom = simpledialog.askstring("Modifier", "Nom :", initialvalue=sel[1])
        if nom is None: return
        prenom = simpledialog.askstring("Modifier", "Prénom :", initialvalue=sel[2]) or ""
        mois = simpledialog.askstring("Modifier", "Mois :", initialvalue=sel[3]) or ""
        pret = messagebox.askyesno("Prêt", "L'élève est-il prêt ?")
        remarque = simpledialog.askstring("Modifier", "Remarque :", initialvalue=sel[5]) or ""
        modifier_eleve(self.conn, eid, nom, prenom, mois, pret, remarque)
        self.rafraichir()

    def supprimer_selection(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez une ligne à supprimer.")
            return
        eid = sel[0]
        if messagebox.askyesno("Confirmer", "Supprimer l'élève sélectionné ?"):
            supprimer_eleve(self.conn, eid)
            self.rafraichir()

    def rafraichir(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        mois = self.filter_var.get()
        rows = lire_eleves(self.conn, filtre_mois=mois if mois else None, ordre=self.sort_order)
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3] or "", "Oui" if r[4] else "Non", r[5] or ""))

    def change_sort(self, event=None):
        self.sort_order = self.sort_combo.get()
        self.rafraichir()

    def export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Exporter CSV")
        if not f:
            return
        rows = [self.tree.item(i)["values"] for i in self.tree.get_children()]
        with open(f, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["ID","Nom","Prénom","Mois","Prêt","Remarque"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("Export", f"Exporté {len(rows)} lignes vers {os.path.basename(f)}")


    def import_csv(self):
        f = filedialog.askopenfilename(filetypes=[("CSV","*.csv")], title="Importer CSV")
        if not f: return
        if not messagebox.askyesno("Importer", "Les données du fichier seront ajoutées à la base. Continuer ?"):
            return
        with open(f, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            cnt = 0
            for row in reader:
                nom = row.get("Nom") or row.get("nom") or ""
                prenom = row.get("Prénom") or row.get("prenom") or ""
                mois = row.get("Mois") or row.get("mois") or ""
                pret = row.get("Prêt") or row.get("pret") or ""
                pret_flag = 1 if str(pret).strip().lower() in ("1","oui","yes","true") else 0
                remarque = row.get("Remarque") or row.get("remarque") or ""
                if nom:
                    ajouter_eleve(self.conn, nom, prenom, mois, pret_flag, remarque)
                    cnt += 1
        messagebox.showinfo("Import", f"{cnt} lignes ajoutées.")
        self.rafraichir()

# --- Lancement ---------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.geometry("920x560")
    root.mainloop()
