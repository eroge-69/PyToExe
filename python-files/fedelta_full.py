#!/usr/bin/env python3
# fedelta_full.py
# Versione completa: GUI Tkinter, SQLite DB, backup automatico, report mensile, admin auth
# Requisiti: Python 3.8+ (librerie standard)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime, date
import csv
import os
import shutil
import hashlib
import sys
import threading

# ---------------- CONFIG ----------------
DB_FILE = "fedelta.db"
BACKUP_FOLDER = "backups"
PUNTO_PER_CENT = 2000        # 20€ = 2000 centesimi -> 1 punto
PUNTI_PER_SCONTO = 10
SCONTO_CENT = 1000           # 10€ = 1000 centesimi
MINIMO_SCONTO_CENT = 2000    # 20€ = 2000 centesimi
AUTO_BACKUP_DAILY = True     # backup automatico giornaliero all'avvio (se non già presente oggi)
ADMIN_DEFAULT_PASSWORD = "admin"  # verrà hashata e salvata, cambiarla al primo avvio
# ----------------------------------------

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

# ---------- Utility ----------
def euro_to_cents(euro_str):
    s = str(euro_str).strip().replace(",", ".")
    if s == "":
        raise ValueError("Importo vuoto")
    if s.count(".") > 1:
        raise ValueError("Formato importo non valido")
    try:
        if "." in s:
            euros, cents = s.split(".")
            euros = int(euros) if euros != "" else 0
            cents = (cents + "00")[:2]
            cents = int(cents)
        else:
            euros = int(s)
            cents = 0
        total = euros * 100 + cents
        return total
    except Exception:
        raise ValueError("Formato importo non valido. Usa 12.34 o 12,34 o 12")

def cents_to_euro_str(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(int(cents))
    e = cents // 100
    c = cents % 100
    return f"{sign}{e}.{c:02d} €"

def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS clienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice_tessera TEXT UNIQUE,
        nome TEXT,
        punti INTEGER DEFAULT 0
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS transazioni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice_tessera TEXT,
        importo_cent INTEGER,
        punti_accreditati INTEGER,
        sconto_usato INTEGER DEFAULT 0,
        data TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS config (
        chiave TEXT PRIMARY KEY,
        valore TEXT
    )""")
    conn.commit()
    # inizializza password admin se non presente
    c.execute("SELECT valore FROM config WHERE chiave = 'admin_hash'")
    r = c.fetchone()
    if not r:
        c.execute("INSERT INTO config (chiave, valore) VALUES (?, ?)", ("admin_hash", hash_password(ADMIN_DEFAULT_PASSWORD)))
        conn.commit()
    return conn

class FedeltaDB:
    def __init__(self, conn):
        self.conn = conn
        self.lock = threading.Lock()
    def find_cliente(self, codice):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id, nome, punti FROM clienti WHERE codice_tessera = ?", (codice,))
            return cur.fetchone()
    def search_clienti(self, term, limit=100):
        term_like = f"%{term}%"
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT codice_tessera, nome, punti FROM clienti WHERE codice_tessera LIKE ? OR nome LIKE ? LIMIT ?", (term_like, term_like, limit))
            return cur.fetchall()
    def add_cliente(self, codice, nome=""):
        with self.lock:
            cur = self.conn.cursor()
            try:
                cur.execute("INSERT INTO clienti (codice_tessera, nome, punti) VALUES (?, ?, ?)", (codice, nome, 0))
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    def update_punti(self, codice, delta):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("UPDATE clienti SET punti = punti + ? WHERE codice_tessera = ?", (delta, codice))
            self.conn.commit()
    def set_punti(self, codice, punti):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("UPDATE clienti SET punti = ? WHERE codice_tessera = ?", (punti, codice))
            self.conn.commit()
    def get_punti(self, codice):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT punti FROM clienti WHERE codice_tessera = ?", (codice,))
            r = cur.fetchone()
            return r[0] if r else None
    def add_transazione(self, codice, importo_cent, punti_accreditati, sconto_usato):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO transazioni (codice_tessera, importo_cent, punti_accreditati, sconto_usato, data) VALUES (?, ?, ?, ?, ?)",
                        (codice, importo_cent, punti_accreditati, int(bool(sconto_usato)), datetime.now().isoformat()))
            self.conn.commit()
    def list_transazioni(self, limit=1000):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id, codice_tessera, importo_cent, punti_accreditati, sconto_usato, data FROM transazioni ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()
    def get_config(self, key):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT valore FROM config WHERE chiave = ?", (key,))
            r = cur.fetchone()
            return r[0] if r else None
    def set_config(self, key, value):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("INSERT OR REPLACE INTO config (chiave, valore) VALUES (?, ?)", (key, value))
            self.conn.commit()
    def transazioni_mese(self, year, month):
        with self.lock:
            cur = self.conn.cursor()
            start = f"{year:04d}-{month:02d}-01T00:00:00"
            if month == 12:
                end = f"{year+1:04d}-01-01T00:00:00"
            else:
                end = f"{year:04d}-{month+1:02d}-01T00:00:00"
            cur.execute("SELECT id, codice_tessera, importo_cent, punti_accreditati, sconto_usato, data FROM transazioni WHERE data >= ? AND data < ? ORDER BY data ASC", (start, end))
            return cur.fetchall()

# ---------- Business logic ----------
def calcola_punti_da_cent(importo_cent):
    return int(importo_cent // PUNTO_PER_CENT)

# ---------- Backup ----------
def backup_db_manual():
    ensure_folder(BACKUP_FOLDER)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_FOLDER, f"fedelta_backup_{timestamp}.db")
    shutil.copy2(DB_FILE, dest)
    return dest

def backup_db_daily_if_needed():
    ensure_folder(BACKUP_FOLDER)
    today = date.today().isoformat()
    marker = os.path.join(BACKUP_FOLDER, f".last_{today}")
    if os.path.exists(marker):
        return None
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUP_FOLDER, f"fedelta_backup_{timestamp}.db")
        shutil.copy2(DB_FILE, dest)
        open(marker, "w").close()
        return dest
    except Exception:
        return None

# ---------- GUI ----------
class FedeltaApp:
    def __init__(self, root, db: FedeltaDB):
        self.root = root
        self.db = db
        root.title("Gestione Tessere Fedeltà - FULL")
        root.geometry("1000x600")
        self.admin_logged = False
        self.current_codice = None
        self.create_widgets()
        self.refresh_transazioni()
        # backup automatico giornaliero (thread)
        if AUTO_BACKUP_DAILY:
            threading.Thread(target=self._auto_backup_thread, daemon=True).start()
        # check admin default password and force change if still default
        stored_hash = self.db.get_config("admin_hash")
        if stored_hash is None:
            self.db.set_config("admin_hash", hash_password(ADMIN_DEFAULT_PASSWORD))
            stored_hash = hash_password(ADMIN_DEFAULT_PASSWORD)
        if stored_hash == hash_password(ADMIN_DEFAULT_PASSWORD):
            self.force_change_admin_pw()

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)

        # Top: Operazioni e login admin
        top = ttk.Frame(frm)
        top.pack(fill=tk.X)

        left_ops = ttk.LabelFrame(top, text="Operazioni Tessera", padding=8)
        left_ops.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        ttk.Label(left_ops, text="Codice Tessera:").grid(column=0, row=0, sticky=tk.W)
        self.codice_var = tk.StringVar()
        self.codice_entry = ttk.Entry(left_ops, textvariable=self.codice_var, width=25)
        self.codice_entry.grid(column=1, row=0, sticky=tk.W)
        self.codice_entry.bind("<Return>", lambda e: self.trova_cliente())

        ttk.Button(left_ops, text="Trova / Crea", command=self.trova_cliente).grid(column=2, row=0, padx=6)

        ttk.Label(left_ops, text="Nome (per nuovo cliente):").grid(column=0, row=1, sticky=tk.W, pady=(6,0))
        self.nome_var = tk.StringVar()
        ttk.Entry(left_ops, textvariable=self.nome_var, width=22).grid(column=1, row=1, sticky=tk.W, columnspan=2)

        ttk.Separator(left_ops, orient=tk.HORIZONTAL).grid(column=0, row=2, columnspan=3, sticky="ew", pady=6)

        ttk.Label(left_ops, text="Importo (€):").grid(column=0, row=3, sticky=tk.W)
        self.importo_var = tk.StringVar()
        ttk.Entry(left_ops, textvariable=self.importo_var, width=12).grid(column=1, row=3, sticky=tk.W)

        ttk.Button(left_ops, text="Aggiungi Punti", command=self.azione_aggiungi_punti).grid(column=0, row=4, pady=6)
        ttk.Button(left_ops, text="Riscatta 10 punti = 10€", command=self.azione_riscatta).grid(column=1, row=4, pady=6)
        ttk.Button(left_ops, text="Aggiungi manualmente punti", command=self.dialog_aggiungi_manual).grid(column=2, row=4, pady=6)

        ttk.Separator(left_ops, orient=tk.HORIZONTAL).grid(column=0, row=5, columnspan=3, sticky="ew", pady=6)

        ttk.Button(left_ops, text="Backup manuale", command=self.backup_manual).grid(column=0, row=6, pady=6)
        ttk.Button(left_ops, text="Report mensile (CSV)", command=self.dialog_report_mese).grid(column=1, row=6, pady=6)
        ttk.Button(left_ops, text="Esporta transazioni (CSV)", command=self.esporta_csv).grid(column=2, row=6, pady=6)

        # Middle: Info cliente e ricerca
        mid = ttk.LabelFrame(top, text="Info Cliente / Ricerca", padding=8)
        mid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        ttk.Label(mid, text="Cerca per codice o nome:").grid(column=0, row=0, sticky=tk.W)
        self.search_var = tk.StringVar()
        ttk.Entry(mid, textvariable=self.search_var, width=30).grid(column=1, row=0, sticky=tk.W)
        ttk.Button(mid, text="Cerca", command=self.ricerca_clienti).grid(column=2, row=0, padx=6)

        self.search_tree = ttk.Treeview(mid, columns=("codice", "nome", "punti"), show="headings", height=6)
        self.search_tree.heading("codice", text="Codice")
        self.search_tree.heading("nome", text="Nome")
        self.search_tree.heading("punti", text="Punti")
        self.search_tree.grid(column=0, row=1, columnspan=3, sticky="nsew", pady=6)
        self.search_tree.bind("<Double-1>", self.on_search_select)

        ttk.Label(mid, text="Dettaglio cliente:").grid(column=0, row=2, sticky=tk.W)
        self.info_txt = tk.Text(mid, height=4, state=tk.DISABLED)
        self.info_txt.grid(column=0, row=3, columnspan=3, sticky="ew", pady=6)

        # Right: Admin
        admin = ttk.LabelFrame(top, text="Admin", padding=8)
        admin.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=6)
        self.admin_user_lbl = ttk.Label(admin, text="Non autenticato")
        self.admin_user_lbl.pack(anchor=tk.W)
        ttk.Button(admin, text="Login Admin", command=self.login_admin).pack(fill=tk.X, pady=4)
        ttk.Button(admin, text="Cambia password admin", command=self.change_admin_pw).pack(fill=tk.X, pady=4)
        ttk.Button(admin, text="Forza backup ora", command=self.backup_manual).pack(fill=tk.X, pady=4)

        # Bottom: Registro transazioni
        bot = ttk.LabelFrame(frm, text="Registro Transazioni (ultime)", padding=8)
        bot.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        columns = ("id","codice","importo","punti","sconto","data")
        self.tree = ttk.Treeview(bot, columns=columns, show="headings")
        for col, title in zip(columns, ["ID", "Codice Tessera", "Importo", "Punti", "Sconto", "Data"]):
            self.tree.heading(col, text=title)
        self.tree.pack(fill=tk.BOTH, expand=True)

        bt_frame = ttk.Frame(frm)
        bt_frame.pack(fill=tk.X, pady=6)
        ttk.Button(bt_frame, text="Aggiorna Lista", command=self.refresh_transazioni).pack(side=tk.LEFT)
        ttk.Button(bt_frame, text="Chiudi", command=self.root.quit).pack(side=tk.RIGHT)

    # ---------- admin ----------
    def login_admin(self):
        pw = simpledialog.askstring("Login Admin", "Inserisci password admin:", show="*", parent=self.root)
        if pw is None:
            return
        stored = self.db.get_config("admin_hash")
        if stored and stored == hash_password(pw):
            self.admin_logged = True
            self.admin_user_lbl.config(text="Admin autenticato")
            messagebox.showinfo("Login", "Accesso admin eseguito.")
        else:
            messagebox.showerror("Login fallito", "Password errata.")

    def change_admin_pw(self):
        if not self.admin_logged:
            if not messagebox.askyesno("Autenticazione richiesta", "Per cambiare la password devi autenticarti. Vuoi effettuare il login ora?"):
                return
            self.login_admin()
            if not self.admin_logged:
                return
        newpw = simpledialog.askstring("Nuova password", "Inserisci la nuova password admin:", show="*", parent=self.root)
        if not newpw:
            messagebox.showwarning("Vuoto", "Password non modificata.")
            return
        self.db.set_config("admin_hash", hash_password(newpw))
        messagebox.showinfo("Fatto", "Password admin modificata.")

    def force_change_admin_pw(self):
        messagebox.showinfo("Cambia password", "La password admin è ancora quella di default. Devi cambiarla ora.")
        self.login_admin()
        # se login con default (sa la default), allora permette cambiamento
        if self.admin_logged:
            self.change_admin_pw()

    # ---------- funzioni principali ----------
    def trova_cliente(self):
        codice = self.codice_var.get().strip()
        if not codice:
            messagebox.showwarning("Attenzione", "Inserisci il codice tessera.")
            return
        r = self.db.find_cliente(codice)
        if r:
            self.current_codice = codice
            self.mostra_info_cliente(codice)
        else:
            nome = self.nome_var.get().strip()
            if nome == "":
                nome = simpledialog.askstring("Nuovo cliente", "Inserisci il nome per il nuovo cliente (opzionale):", parent=self.root) or ""
            ok = self.db.add_cliente(codice, nome)
            if ok:
                messagebox.showinfo("Fatto", f"Cliente creato con codice {codice}")
                self.current_codice = codice
                self.mostra_info_cliente(codice)
            else:
                messagebox.showerror("Errore", "Impossibile creare cliente (codice duplicato?).")

    def mostra_info_cliente(self, codice):
        r = self.db.find_cliente(codice)
        self.info_txt.config(state=tk.NORMAL)
        self.info_txt.delete("1.0", tk.END)
        if r:
            _, nome, punti = r
            self.info_txt.insert(tk.END, f"Codice: {codice}\nNome: {nome}\nPunti: {punti}\n")
        else:
            self.info_txt.insert(tk.END, f"Codice: {codice}\nCliente non trovato.\n")
        self.info_txt.config(state=tk.DISABLED)

    def azione_aggiungi_punti(self):
        codice = self.codice_var.get().strip()
        if not codice:
            messagebox.showwarning("Attenzione", "Inserisci il codice tessera.")
            return
        try:
            importo_cent = euro_to_cents(self.importo_var.get().strip())
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            return
        if not self.db.find_cliente(codice):
            if not messagebox.askyesno("Cliente non trovato", "Cliente non trovato. Vuoi crearlo?"):
                return
            self.db.add_cliente(codice, "")
        punti = calcola_punti_da_cent(importo_cent)
        if punti > 0:
            self.db.update_punti(codice, punti)
        self.db.add_transazione(codice, importo_cent, punti, sconto_usato=0)
        messagebox.showinfo("Punti aggiunti", f"Aggiunti {punti} punti a {codice}.")
        self.mostra_info_cliente(codice)
        self.refresh_transazioni()

    def azione_riscatta(self):
        codice = self.codice_var.get().strip()
        if not codice:
            messagebox.showwarning("Attenzione", "Inserisci il codice tessera.")
            return
        try:
            importo_cent = euro_to_cents(self.importo_var.get().strip())
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            return
        if importo_cent < MINIMO_SCONTO_CENT:
            messagebox.showwarning("Minimo non raggiunto", f"Per usare lo sconto minimo {cents_to_euro_str(MINIMO_SCONTO_CENT)} richiesto.")
            return
        punti = self.db.get_punti(codice)
        if punti is None:
            messagebox.showerror("Errore", "Cliente non trovato.")
            return
        if punti < PUNTI_PER_SCONTO:
            messagebox.showwarning("Punti insufficienti", f"Hai {punti} punti. Ne servono {PUNTI_PER_SCONTO} per lo sconto.")
            return
        if not messagebox.askyesno("Conferma riscatto", f"Vuoi riscattare {PUNTI_PER_SCONTO} punti per {cents_to_euro_str(SCONTO_CENT)} di sconto?"):
            return
        # scala punti
        self.db.update_punti(codice, -PUNTI_PER_SCONTO)
        nuovo_importo = importo_cent - SCONTO_CENT
        # calcola eventuali punti sul valore originale (scelta: punti vengono comunque calcolati sull'importo originario)
        punti_acc = calcola_punti_da_cent(importo_cent)
        self.db.add_transazione(codice, nuovo_importo, punti_acc, sconto_usato=1)
        messagebox.showinfo("Sconto applicato", f"Sconto applicato. Totale da pagare: {cents_to_euro_str(nuovo_importo)}")
        self.mostra_info_cliente(codice)
        self.refresh_transazioni()

    def dialog_aggiungi_manual(self):
        codice = self.codice_var.get().strip()
        if not codice:
            messagebox.showwarning("Attenzione", "Inserisci il codice tessera per aggiungere punti manualmente.")
            return
        try:
            n = simpledialog.askinteger("Aggiungi punti manuali", "Numero di punti da aggiungere (valore positivo o negativo):", parent=self.root)
            if n is None:
                return
            self.db.update_punti(codice, n)
            messagebox.showinfo("Fatto", f"Aggiornati punti per {codice}.")
            self.mostra_info_cliente(codice)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def ricerca_clienti(self):
        term = self.search_var.get().strip()
        if term == "":
            messagebox.showwarning("Attenzione", "Inserisci un termine di ricerca.")
            return
        rows = self.db.search_clienti(term)
        for i in self.search_tree.get_children():
            self.search_tree.delete(i)
        for codice, nome, punti in rows:
            self.search_tree.insert("", tk.END, values=(codice, nome, punti))

    def on_search_select(self, event):
        sel = self.search_tree.selection()
        if not sel:
            return
        item = self.search_tree.item(sel[0])["values"]
        codice = item[0]
        self.codice_var.set(codice)
        self.trova_cliente()

    def refresh_transazioni(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.db.list_transazioni(500)
        for r in rows:
            id_, codice, importo_cent, punti, sconto, data = r
            self.tree.insert("", tk.END, values=(id_, codice, cents_to_euro_str(importo_cent), punti, "Sì" if sconto else "No", data))

    # ---------- export & report ----------
    def esporta_csv(self):
        rows = self.db.list_transazioni(10000)
        if not rows:
            messagebox.showinfo("Vuoto", "Nessuna transazione da esportare.")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Salva CSV transazioni")
        if not fpath:
            return
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id","codice_tessera","importo_cent","importo_euro","punti_accreditati","sconto_usato","data"])
            for r in rows[::-1]:
                id_, codice, importo_cent, punti, sconto, data = r
                w.writerow([id_, codice, importo_cent, f"{cents_to_euro_str(importo_cent)}", punti, sconto, data])
        messagebox.showinfo("Esportato", f"Transazioni esportate in {fpath}")

    def dialog_report_mese(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Report mensile CSV")
        dlg.geometry("320x160")
        ttk.Label(dlg, text="Anno (YYYY):").pack(pady=4)
        year_var = tk.IntVar(value=datetime.now().year)
        ttk.Entry(dlg, textvariable=year_var).pack()
        ttk.Label(dlg, text="Mese (1-12):").pack(pady=4)
        month_var = tk.IntVar(value=datetime.now().month)
        ttk.Entry(dlg, textvariable=month_var).pack()
        def gen():
            y = year_var.get()
            m = month_var.get()
            if not (1 <= m <= 12):
                messagebox.showerror("Errore", "Mese non valido")
                return
            rows = self.db.transazioni_mese(y, m)
            if not rows:
                messagebox.showinfo("Vuoto", "Nessuna transazione per il mese selezionato.")
                return
            fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Salva Report mensile")
            if not fpath:
                return
            with open(fpath, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id","codice_tessera","importo_cent","importo_euro","punti_accreditati","sconto_usato","data"])
                for r in rows:
                    id_, codice, importo_cent, punti, sconto, data = r
                    w.writerow([id_, codice, importo_cent, f"{cents_to_euro_str(importo_cent)}", punti, sconto, data])
                    ...messagebox.showinfo("Report creato", f"Report mensile creato in {fpath}")
...             dlg.destroy()
...         ttk.Button(dlg, text="Genera Report", command=gen).pack(pady=8)
... 
...     # ---------- backup ----------
...     def backup_manual(self):
...         try:
...             dest = backup_db_manual()
...             messagebox.showinfo("Backup", f"Backup creato: {dest}")
...         except Exception as e:
...             messagebox.showerror("Errore backup", str(e))
... 
...     def _auto_backup_thread(self):
...         try:
...             dest = backup_db_daily_if_needed()
...             if dest:
...                 # opzionale: notifica minimale (non bloccante)
...                 print(f"Backup automatico creato: {dest}")
...         except Exception:
...             pass
... 
... # ---------- Main ----------
... def main():
...     # assicurati cartelle
...     ensure_folder(BACKUP_FOLDER)
...     # inizializza DB
...     conn = init_db()
...     db = FedeltaDB(conn)
...     root = tk.Tk()
...     app = FedeltaApp(root, db)
...     root.mainloop()
...     conn.close()
... 
... if __name__ == "__main__":
...     main()
>>> [DEBUG ON]
>>> [DEBUG OFF]
