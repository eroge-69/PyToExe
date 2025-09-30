import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv
import os
import shutil
from tkinter import PhotoImage

def acceul():
    # -----------------------
    # Configuration générale
    # -----------------------
    DB_FILE = "transactions.db"
    DATE_FORMAT = "%Y-%m-%d"

    # -----------------------
    # Base de données
    # -----------------------
    def init_db():
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                amount REAL,
                date TEXT,
                reason TEXT,
                created_at TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                amount REAL,
                date TEXT,
                reason TEXT,
                created_at TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type TEXT, -- "Matériel" ou "Financier"
                value REAL,
                acquisition_date TEXT,
                notes TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def db_execute(query, params=(), fetch=False):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            rows = cur.fetchall()
            conn.commit()
            conn.close()
            return rows
        conn.commit()
        conn.close()

    # -----------------------
    # Utilitaires
    # -----------------------
    def today_str():
        return datetime.now().strftime(DATE_FORMAT)

    def is_valid_date(s):
        try:
            datetime.strptime(s, DATE_FORMAT)
            return True
        except:
            return False

    def format_currency(v):
        try:
            return f"{float(v):.2f}"
        except:
            return v

    # -----------------------
    # Actions Transactions
    # -----------------------
    def add_transaction(kind):
        # kind = 'income' or 'expense'
        name = tx_name_var.get().strip()
        amount = tx_amount_var.get().strip()
        date = tx_date_var.get().strip()
        reason = tx_reason_var.get().strip()
        if not name or not amount or not date:
            messagebox.showwarning("Champs manquants", "Veuillez remplir au moins le nom, le montant et la date.")
            return
        try:
            amount_f = float(amount)
        except:
            messagebox.showerror("Montant invalide", "Le montant doit être un nombre (ex: 1200.50).")
            return
        if not is_valid_date(date):
            messagebox.showerror("Date invalide", f"La date doit être au format {DATE_FORMAT}.")
            return
        created = datetime.now().isoformat()
        table = 'incomes' if kind == 'income' else 'expenses'
        db_execute(f"INSERT INTO {table} (name, amount, date, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                   (name, amount_f, date, reason, created))
        clear_tx_form()
        refresh_tx_tables()
        update_dashboard()
        messagebox.showinfo("Ajouté", f"{'Entrée' if kind=='income' else 'Sortie'} enregistrée.")

    def update_transaction(kind):
        sel = incomes_tree.selection() if kind == 'income' else expenses_tree.selection()
        if not sel:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une transaction à modifier.")
            return
        item = sel[0]
        item_values = (incomes_tree.item(item)['values'] if kind == 'income' else expenses_tree.item(item)['values'])
        tx_id = item_values[0]
        name = tx_name_var.get().strip()
        amount = tx_amount_var.get().strip()
        date = tx_date_var.get().strip()
        reason = tx_reason_var.get().strip()
        if not name or not amount or not date:
            messagebox.showwarning("Champs manquants", "Veuillez remplir au moins le nom, le montant et la date.")
            return
        try:
            amount_f = float(amount)
        except:
            messagebox.showerror("Montant invalide", "Le montant doit être un nombre.")
            return
        if not is_valid_date(date):
            messagebox.showerror("Date invalide", f"La date doit être au format {DATE_FORMAT}.")
            return
        table = 'incomes' if kind == 'income' else 'expenses'
        db_execute(f"UPDATE {table} SET name=?, amount=?, date=?, reason=? WHERE id=?",
                   (name, amount_f, date, reason, tx_id))
        clear_tx_form()
        refresh_tx_tables()
        update_dashboard()
        messagebox.showinfo("Modifié", "Transaction mise à jour.")

    def delete_transaction(kind):
        sel = incomes_tree.selection() if kind == 'income' else expenses_tree.selection()
        if not sel:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une transaction à supprimer.")
            return
        item = sel[0]
        item_values = (incomes_tree.item(item)['values'] if kind == 'income' else expenses_tree.item(item)['values'])
        tx_id = item_values[0]
        if messagebox.askyesno("Confirmer suppression", "Voulez-vous vraiment supprimer cette transaction ?"):
            table = 'incomes' if kind == 'income' else 'expenses'
            db_execute(f"DELETE FROM {table} WHERE id=?", (tx_id,))
            refresh_tx_tables()
            update_dashboard()
            clear_tx_form()

    def load_selected_tx(kind):
        sel = incomes_tree.selection() if kind == 'income' else expenses_tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = (incomes_tree.item(item)['values'] if kind == 'income' else expenses_tree.item(item)['values'])
        # vals: [id, name, amount, date, reason, created_at]
        tx_name_var.set(vals[1])
        tx_amount_var.set(format_currency(vals[2]))
        tx_date_var.set(vals[3])
        tx_reason_var.set(vals[4])

    def clear_tx_form():
        tx_name_var.set("")
        tx_amount_var.set("")
        tx_date_var.set(today_str())
        tx_reason_var.set("")

    # -----------------------
    # Refresh affichage
    # -----------------------
    def refresh_tx_tables():
        # incomes
        for row in incomes_tree.get_children():
            incomes_tree.delete(row)
        rows = db_execute("SELECT id, name, amount, date, reason, created_at FROM incomes ORDER BY date DESC, id DESC", fetch=True)
        for r in rows:
            incomes_tree.insert("", "end", values=r)
        # expenses
        for row in expenses_tree.get_children():
            expenses_tree.delete(row)
        rows = db_execute("SELECT id, name, amount, date, reason, created_at FROM expenses ORDER BY date DESC, id DESC", fetch=True)
        for r in rows:
            expenses_tree.insert("", "end", values=r)
        update_totals_labels()

    def update_totals_labels():
        inc = db_execute("SELECT SUM(amount) FROM incomes", fetch=True)[0][0] or 0.0
        exp = db_execute("SELECT SUM(amount) FROM expenses", fetch=True)[0][0] or 0.0
        incomes_total_var.set(f"{inc:.2f}")
        expenses_total_var.set(f"{exp:.2f}")
        balance_var.set(f"{inc - exp:.2f}")

    # -----------------------
    # Export / Backup
    # -----------------------
    def export_table_csv(table):
        default_name = f"{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_name,
                                            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        rows = db_execute(f"SELECT * FROM {table}", fetch=True)
        if not rows:
            messagebox.showinfo("Vide", "La table est vide, rien à exporter.")
            return
        col_names = [d[0] for d in sqlite_table_columns(table)]
        try:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(col_names)
                writer.writerows(rows)
            messagebox.showinfo("Export réussi", f"Exporté {len(rows)} lignes vers :\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur export", str(e))

    def sqlite_table_columns(table):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        conn.close()
        # return list of tuples - we'll use names
        return [(c[1], c[2]) for c in cols]

    def backup_database():
        dest = filedialog.asksaveasfilename(defaultextension=".db", initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        if not dest:
            return
        try:
            shutil.copyfile(DB_FILE, dest)
            messagebox.showinfo("Sauvegarde", f"Base sauvegardée :\n{dest}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # -----------------------
    # Assets (Biens)
    # -----------------------
    def add_asset():
        name = asset_name_var.get().strip()
        typ = asset_type_var.get()
        value = asset_value_var.get().strip()
        date = asset_date_var.get().strip()
        notes = asset_notes_var.get().strip()
        if not name or not value:
            messagebox.showwarning("Champs manquants", "Veuillez remplir au moins le nom et la valeur.")
            return
        try:
            value_f = float(value)
        except:
            messagebox.showerror("Valeur invalide", "La valeur doit être un nombre.")
            return
        if date and not is_valid_date(date):
            messagebox.showerror("Date invalide", f"La date doit être au format {DATE_FORMAT}.")
            return
        created = datetime.now().isoformat()
        db_execute("INSERT INTO assets (name, type, value, acquisition_date, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, typ, value_f, date, notes, created))
        clear_asset_form()
        refresh_assets_table()
        update_dashboard()
        messagebox.showinfo("Ajouté", "Bien ajouté.")

    def refresh_assets_table():
        for row in assets_tree.get_children():
            assets_tree.delete(row)
        rows = db_execute("SELECT id, name, type, value, acquisition_date, notes, created_at FROM assets ORDER BY id DESC", fetch=True)
        for r in rows:
            assets_tree.insert("", "end", values=r)
        update_assets_total()

    def clear_asset_form():
        asset_name_var.set("")
        asset_type_var.set("Matériel")
        asset_value_var.set("")
        asset_date_var.set(today_str())
        asset_notes_var.set("")

    def load_selected_asset():
        sel = assets_tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = assets_tree.item(item)['values']
        asset_name_var.set(vals[1])
        asset_type_var.set(vals[2])
        asset_value_var.set(format_currency(vals[3]))
        asset_date_var.set(vals[4] or today_str())
        asset_notes_var.set(vals[5] or "")

    def update_asset():
        sel = assets_tree.selection()
        if not sel:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un bien à modifier.")
            return
        item = sel[0]
        vals = assets_tree.item(item)['values']
        asset_id = vals[0]
        name = asset_name_var.get().strip()
        typ = asset_type_var.get()
        value = asset_value_var.get().strip()
        date = asset_date_var.get().strip()
        notes = asset_notes_var.get().strip()
        if not name or not value:
            messagebox.showwarning("Champs manquants", "Veuillez remplir au moins le nom et la valeur.")
            return
        try:
            value_f = float(value)
        except:
            messagebox.showerror("Valeur invalide", "La valeur doit être un nombre.")
            return
        if date and not is_valid_date(date):
            messagebox.showerror("Date invalide", f"La date doit être au format {DATE_FORMAT}.")
            return
        db_execute("UPDATE assets SET name=?, type=?, value=?, acquisition_date=?, notes=? WHERE id=?",
                   (name, typ, value_f, date, notes, asset_id))
        refresh_assets_table()
        update_dashboard()
        clear_asset_form()
        messagebox.showinfo("Modifié", "Bien mis à jour.")

    def delete_asset():
        sel = assets_tree.selection()
        if assets_tree.selection() :
            print("selection")
        if not sel:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un bien à supprimer.")
            return
        item = sel[0]
        vals = assets_tree.item(item)['values']
        asset_id = vals[0]
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer ce bien ?"):
            db_execute("DELETE FROM assets WHERE id=?", (asset_id,))
            refresh_assets_table()
            update_dashboard()

    def update_assets_total():
        total = db_execute("SELECT SUM(value) FROM assets", fetch=True)[0][0] or 0.0
        assets_total_var.set(f"{total:.2f}")

    # -----------------------
    # Comptabilité / Dashboard
    # -----------------------
    def update_dashboard():
        update_totals_labels()
        update_assets_total()
        # remplir journal combiné
        for r in journal_tree.get_children():
            journal_tree.delete(r)
        rows_inc = db_execute("SELECT id, 'Entrée' as type, name, amount, date, reason FROM incomes", fetch=True)
        rows_exp = db_execute("SELECT id, 'Sortie' as type, name, amount, date, reason FROM expenses", fetch=True)
        combined = rows_inc + rows_exp
        # trier par date desc
        combined_sorted = sorted(combined, key=lambda x: (x[4] or ""), reverse=True)
        for r in combined_sorted:
            journal_tree.insert("", "end", values=r)

    # -----------------------
    # UI Construction
    # -----------------------
    root = tk.Tk()
    root.title("Gestion Transactions - TECHNIPRO-AFRIC")
    root.geometry("1100x700")
    root.minsize(900, 600)

    # Style épuré
    style = ttk.Style(root)
    # try to use 'clam' theme for clean look
    try:
        style.theme_use('clam')
    except:
        pass
    default_font = ("Segoe UI", 10)
    heading_font = ("Segoe UI", 12, "bold")
    style.configure(".", font=default_font, background="#ffffff")
    style.configure("TNotebook", padding=10)
    style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[10, 8])
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.configure("Accent.TButton", padding=6)
    # Colors (minimal)
    BG = "#f8f9fb"
    root.configure(bg=BG)

    # Notebook (pages)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=12, pady=12)

    # ---- Page Transactions ----
    page_tx = ttk.Frame(notebook)
    notebook.add(page_tx, text="Transactions")

    # Left: form
    form_frame = ttk.Frame(page_tx, padding=12)
    form_frame.pack(side="left", fill="y", padx=(0,12), pady=6)

    ttk.Label(form_frame, text="Formulaire transaction", font=heading_font).pack(anchor="w", pady=(0,8))
    tx_name_var = tk.StringVar()
    tx_amount_var = tk.StringVar()
    tx_date_var = tk.StringVar(value=today_str())
    tx_reason_var = tk.StringVar()

    ttk.Label(form_frame, text="Nom (personne)").pack(anchor="w")
    ttk.Entry(form_frame, textvariable=tx_name_var, width=30).pack(anchor="w", pady=4)

    ttk.Label(form_frame, text="Montant").pack(anchor="w")
    ttk.Entry(form_frame, textvariable=tx_amount_var, width=20).pack(anchor="w", pady=4)

    ttk.Label(form_frame, text=f"Date ({DATE_FORMAT})").pack(anchor="w")
    ttk.Entry(form_frame, textvariable=tx_date_var, width=20).pack(anchor="w", pady=4)

    ttk.Label(form_frame, text="Raison / Description").pack(anchor="w")
    ttk.Entry(form_frame, textvariable=tx_reason_var, width=40).pack(anchor="w", pady=4)

    btns_fr = ttk.Frame(form_frame)
    btns_fr.pack(anchor="w", pady=10, fill="x")
    ttk.Button(btns_fr, text="Ajouter Entrée", style="Accent.TButton", command=lambda: add_transaction('income')).pack(side="left", padx=2)
    ttk.Button(btns_fr, text="Ajouter Sortie", style="Accent.TButton", command=lambda: add_transaction('expense')).pack(side="left", padx=2)
    ttk.Button(btns_fr, text="Modifier sélection", command=lambda: update_transaction(current_tx_kind.get())).pack(side="left", padx=8)
    ttk.Button(btns_fr, text="Supprimer sélection", command=lambda: delete_transaction(current_tx_kind.get())).pack(side="left", padx=2)
    ttk.Button(btns_fr, text="Effacer formulaire", command=clear_tx_form).pack(side="left", padx=8)

    ttk.Separator(form_frame, orient="horizontal").pack(fill="x", pady=10)

    # Switch incomes/expenses selection for update/delete actions
    current_tx_kind = tk.StringVar(value="income")
    ttk.Label(form_frame, text="Opérations (modifier / supprimer):").pack(anchor="w")
    op_frame = ttk.Frame(form_frame)
    op_frame.pack(anchor="w", pady=4)
    ttk.Radiobutton(op_frame, text="Entrées", variable=current_tx_kind, value="income").pack(side="left", padx=6)
    ttk.Radiobutton(op_frame, text="Sorties", variable=current_tx_kind, value="expense").pack(side="left", padx=6)

    # Right: tables
    tables_frame = ttk.Frame(page_tx)
    tables_frame.pack(side="left", fill="both", expand=True)

    # Incomes panel
    incomes_panel = ttk.LabelFrame(tables_frame, text="Entrées", padding=8)
    incomes_panel.pack(fill="both", expand=True, side="top", padx=4, pady=(0,6))

    incomes_tree = ttk.Treeview(incomes_panel, columns=("id","name","amount","date","reason","created_at"), show="headings", selectmode="browse")
    for col, txt, w in [("id","ID",50), ("name","Nom",180), ("amount","Montant",100), ("date","Date",100), ("reason","Raison",240), ("created_at","Enregistré",150)]:
        incomes_tree.heading(col, text=txt)
        incomes_tree.column(col, width=w, anchor="center" if col in ("id","amount","date") else "w")
    incomes_tree.pack(fill="both", expand=True, side="left")
    incomes_tree.bind("<Double-1>", lambda e: (load_selected_tx('income')))

    incomes_scroll = ttk.Scrollbar(incomes_panel, orient="vertical", command=incomes_tree.yview)
    incomes_tree.configure(yscrollcommand=incomes_scroll.set)
    incomes_scroll.pack(side="right", fill="y")

    # Expenses panel
    expenses_panel = ttk.LabelFrame(tables_frame, text="Sorties", padding=8)
    expenses_panel.pack(fill="both", expand=True, side="top", padx=4, pady=(6,0))

    expenses_tree = ttk.Treeview(expenses_panel, columns=("id","name","amount","date","reason","created_at"), show="headings", selectmode="browse")
    for col, txt, w in [("id","ID",50), ("name","Nom",180), ("amount","Montant",100), ("date","Date",100), ("reason","Raison",240), ("created_at","Enregistré",150)]:
        expenses_tree.heading(col, text=txt)
        expenses_tree.column(col, width=w, anchor="center" if col in ("id","amount","date") else "w")
    expenses_tree.pack(fill="both", expand=True, side="left")
    expenses_tree.bind("<Double-1>", lambda e: (load_selected_tx('expense')))

    expenses_scroll = ttk.Scrollbar(expenses_panel, orient="vertical", command=expenses_tree.yview)
    expenses_tree.configure(yscrollcommand=expenses_scroll.set)
    expenses_scroll.pack(side="right", fill="y")

    # Totals area
    totals_frame = ttk.Frame(tables_frame, padding=8)
    totals_frame.pack(fill="x", pady=8)

    incomes_total_var = tk.StringVar(value="0.00")
    expenses_total_var = tk.StringVar(value="0.00")
    balance_var = tk.StringVar(value="0.00")

    ttk.Label(totals_frame, text="Total Entrées:", font=default_font).pack(side="left", padx=(6,3))
    ttk.Label(totals_frame, textvariable=incomes_total_var, font=heading_font).pack(side="left", padx=(0,12))
    ttk.Label(totals_frame, text="Total Sorties:").pack(side="left", padx=(6,3))
    ttk.Label(totals_frame, textvariable=expenses_total_var, font=heading_font).pack(side="left", padx=(0,12))
    ttk.Label(totals_frame, text="Solde:", foreground="#004d00").pack(side="left", padx=(6,3))
    ttk.Label(totals_frame, textvariable=balance_var, font=heading_font).pack(side="left", padx=(0,12))

    # ---- Page Biens (Assets) ----
    page_assets = ttk.Frame(notebook)
    notebook.add(page_assets, text="Biens & Actifs")

    left_assets = ttk.Frame(page_assets, padding=12)
    left_assets.pack(side="left", fill="y", padx=(0,12), pady=6)

    ttk.Label(left_assets, text="Formulaire bien", font=heading_font).pack(anchor="w", pady=(0,8))
    asset_name_var = tk.StringVar()
    asset_type_var = tk.StringVar(value="Matériel")
    asset_value_var = tk.StringVar()
    asset_date_var = tk.StringVar(value=today_str())
    asset_notes_var = tk.StringVar()

    ttk.Label(left_assets, text="Nom du bien").pack(anchor="w")
    ttk.Entry(left_assets, textvariable=asset_name_var, width=30).pack(anchor="w", pady=4)
    ttk.Label(left_assets, text="Type (Matériel / Financier)").pack(anchor="w")
    ttk.Combobox(left_assets, textvariable=asset_type_var, values=["Matériel", "Financier"], state="readonly", width=20).pack(anchor="w", pady=4)
    ttk.Label(left_assets, text="Valeur").pack(anchor="w")
    ttk.Entry(left_assets, textvariable=asset_value_var, width=20).pack(anchor="w", pady=4)
    ttk.Label(left_assets, text=f"Date acquisition ({DATE_FORMAT})").pack(anchor="w")
    ttk.Entry(left_assets, textvariable=asset_date_var, width=20).pack(anchor="w", pady=4)
    ttk.Label(left_assets, text="Notes").pack(anchor="w")
    ttk.Entry(left_assets, textvariable=asset_notes_var, width=40).pack(anchor="w", pady=4)

    asset_btns = ttk.Frame(left_assets)
    asset_btns.pack(anchor="w", pady=10)
    ttk.Button(asset_btns, text="Ajouter bien", command=add_asset).pack(side="left", padx=4)
    ttk.Button(asset_btns, text="Modifier bien", command=update_asset).pack(side="left", padx=4)
    ttk.Button(asset_btns, text="Supprimer bien", command=delete_asset).pack(side="left", padx=4)
    ttk.Button(asset_btns, text="Effacer formulaire", command=clear_asset_form).pack(side="left", padx=4)

    right_assets = ttk.Frame(page_assets)
    right_assets.pack(side="left", fill="both", expand=True)

    assets_panel = ttk.LabelFrame(right_assets, text="Liste des biens", padding=8)
    assets_panel.pack(fill="both", expand=True)

    assets_tree = ttk.Treeview(assets_panel, columns=("id","name","type","value","acq_date","notes","created_at"), show="headings", selectmode="browse")
    for col, txt, w in [("id","ID",50), ("name","Nom",220), ("type","Type",100), ("value","Valeur",120),
                        ("acq_date","Date acquis",110), ("notes","Notes",200), ("created_at","Enregistré",140)]:
        assets_tree.heading(col, text=txt)
        assets_tree.column(col, width=w, anchor="w")
    assets_tree.pack(fill="both", expand=True)
    assets_tree.bind("<Double-1>", lambda e: load_selected_asset())

    assets_scroll = ttk.Scrollbar(assets_panel, orient="vertical", command=assets_tree.yview)
    assets_tree.configure(yscrollcommand=assets_scroll.set)
    assets_scroll.pack(side="right", fill="y")

    assets_total_var = tk.StringVar(value="0.00")
    assets_footer = ttk.Frame(right_assets, padding=6)
    assets_footer.pack(fill="x")
    ttk.Label(assets_footer, text="Total des actifs:").pack(side="left")
    ttk.Label(assets_footer, textvariable=assets_total_var, font=heading_font).pack(side="left", padx=6)

    # ---- Page Comptabilité ----
    page_accounting = ttk.Frame(notebook)
    notebook.add(page_accounting, text="Comptabilité & Journal")

    upper_acc = ttk.Frame(page_accounting, padding=8)
    upper_acc.pack(fill="x")
    ttk.Label(upper_acc, text="Tableau de bord", font=heading_font).pack(anchor="w")
    # small dashboard area
    dash_frame = ttk.Frame(upper_acc, padding=8)
    dash_frame.pack(fill="x", pady=8)
    ttk.Label(dash_frame, text="Entrées totales :").grid(row=0, column=0, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, textvariable=incomes_total_var).grid(row=0, column=1, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, text="Sorties totales :").grid(row=0, column=2, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, textvariable=expenses_total_var).grid(row=0, column=3, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, text="Actifs totaux :").grid(row=0, column=4, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, textvariable=assets_total_var).grid(row=0, column=5, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, text="Solde:").grid(row=0, column=6, sticky="w", padx=6, pady=2)
    ttk.Label(dash_frame, textvariable=balance_var).grid(row=0, column=7, sticky="w", padx=6, pady=2)

    # Journal combiné
    journal_panel = ttk.LabelFrame(page_accounting, text="Journal combiné (Entrées & Sorties)", padding=8)
    journal_panel.pack(fill="both", expand=True, padx=8, pady=8)

    journal_tree = ttk.Treeview(journal_panel, columns=("id","type","name","amount","date","reason"), show="headings")
    for col, txt, w in [("id","ID",50), ("type","Type",80), ("name","Nom",220), ("amount","Montant",110), ("date","Date",110), ("reason","Raison",300)]:
        journal_tree.heading(col, text=txt)
        journal_tree.column(col, width=w, anchor="w")
    journal_tree.pack(fill="both", expand=True)

    # ---- Page Export & Utilitaires ----
    page_export = ttk.Frame(notebook)
    notebook.add(page_export, text="Export & Sauvegarde")

    exp_frame = ttk.Frame(page_export, padding=12)
    exp_frame.pack(fill="both", expand=True)

    ttk.Label(exp_frame, text="Export / Sauvegarde", font=heading_font).pack(anchor="w", pady=(0,8))
    ttk.Button(exp_frame, text="Exporter entrées (CSV)", command=lambda: export_table_csv('incomes')).pack(anchor="w", pady=6)
    ttk.Button(exp_frame, text="Exporter sorties (CSV)", command=lambda: export_table_csv('expenses')).pack(anchor="w", pady=6)
    ttk.Button(exp_frame, text="Exporter biens (CSV)", command=lambda: export_table_csv('assets')).pack(anchor="w", pady=6)
    ttk.Button(exp_frame, text="Sauvegarder la base (copie .db)", command=backup_database).pack(anchor="w", pady=12)

    # Short help and app info
    ttk.Separator(exp_frame, orient="horizontal").pack(fill="x", pady=12)
    ttk.Label(exp_frame, text="Aide rapide", font=heading_font).pack(anchor="w", pady=(6,2))
    help_text = (
        "• Double-clic sur une ligne pour charger la transaction / bien dans le formulaire.\n"
        "• Modifier depuis le formulaire puis cliquer sur 'Modifier sélection'.\n"
        "• Utiliser l'onglet 'Export' pour exporter CSV ou sauvegarder la base.\n"
        f"• Date au format {DATE_FORMAT} (ex: 2025-09-29)."
    )
    ttk.Label(exp_frame, text=help_text, wraplength=700, justify="left").pack(anchor="w", pady=6)

    # -----------------------
    # Initialisation
    # -----------------------
    init_db()
    refresh_tx_tables()
    refresh_assets_table()
    update_dashboard()

    # Start main loop
    root.mainloop()


# ======= Vérification des identifiants =======
def verifier_identifiants():
    nom = entry_nom.get().strip()
    code = entry_code.get().strip()

    noms_valides = ["EDOU Elolo Emmanuel", "Mohamed DIOP","Visiteur"]
    code_valide = "TECHNIPRO-AFRIC-#454#"

    if nom in noms_valides and code == code_valide:
        messagebox.showinfo("Succès", "Authentification réussie !")
        root.destroy()
        acceul()
        # Ici tu peux lancer ton logiciel principal
    else:
        messagebox.showerror("Erreur", "Nom ou code incorrect !")
        entry_code.delete(0, tk.END)


# ======= Interface graphique =======
root = tk.Tk()
root.title("Authentification - TECHNIPRO-AFRIC")
root.geometry("425x400")
root.resizable(False, False)
root.configure(bg="#f0f4f7")  # Couleur de fond douce
image=PhotoImage(file="ok (3).png")
ina=PhotoImage(file="ok.png")
root.iconphoto(ina,ina)
# Cadre principal
frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Titre avec logo simulé
label_logo = tk.Label(frame, image=image)
label_logo.pack(pady=15)

# Nom
label_nom = tk.Label(frame, text="Nom :", font=("Arial", 12), bg="#ffffff", anchor="w")
label_nom.pack(fill="x", padx=30, pady=(10, 0))
entry_nom = tk.Entry(frame, font=("Arial", 12))
entry_nom.pack(fill="x", padx=30, pady=5)

# Code
label_code = tk.Label(frame, text="Code :", font=("Arial", 12), bg="#ffffff", anchor="w")
label_code.pack(fill="x", padx=30, pady=(10, 0))
entry_code = tk.Entry(frame, font=("Arial", 12), show="*")
entry_code.pack(fill="x", padx=30, pady=5)

# Bouton Connexion
btn_connexion = tk.Button(frame, text="Se connecter", font=("Arial", 12, "bold"),
                          bg="#1e3d59", fg="#ffffff", activebackground="#3e5c7b",
                          command=verifier_identifiants)
btn_connexion.pack(pady=20, ipadx=10, ipady=5)

# Astuce : Entrée déclenche la connexion
root.bind('<Return>', lambda event: verifier_identifiants())

root.mainloop()