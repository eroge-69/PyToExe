import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from datetime import datetime
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas

DB_NAME = "kasowy.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    datetime TEXT,
                    amount REAL,
                    description TEXT
                )''')
    conn.commit()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [("user1","123"), ("user2","123"), ("user3","123")]
        c.executemany("INSERT INTO users (username,password) VALUES (?,?)", users)
        conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_transaction(user_id, amount, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO transactions (user_id, datetime, amount, description) VALUES (?, ?, ?, ?)",
              (user_id, dt, amount, description))
    conn.commit()
    conn.close()

def get_transactions(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT datetime, amount, description FROM transactions WHERE user_id=? ORDER BY datetime DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_report_rows(user_id, period='daily'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now()

    if period == 'daily':
        date_str = now.strftime('%Y-%m-%d') + '%'
        c.execute("""SELECT datetime, amount, description FROM transactions
                     WHERE user_id=? AND datetime LIKE ?
                     ORDER BY datetime DESC""",
                  (user_id, date_str))
    elif period == 'monthly':
        date_str = now.strftime('%Y-%m') + '%'
        c.execute("""SELECT datetime, amount, description FROM transactions
                     WHERE user_id=? AND datetime LIKE ?
                     ORDER BY datetime DESC""",
                  (user_id, date_str))
    elif period == 'yearly':
        date_str = now.strftime('%Y') + '%'
        c.execute("""SELECT datetime, amount, description FROM transactions
                     WHERE user_id=? AND datetime LIKE ?
                     ORDER BY datetime DESC""",
                  (user_id, date_str))
    elif period == 'cash':
        c.execute("""SELECT datetime, amount, description FROM transactions
                     WHERE user_id=? AND amount>0 AND
                           description NOT LIKE '%Karta%' AND description NOT LIKE '%Przelew%'
                     ORDER BY datetime DESC""",
                  (user_id,))
    else:
        conn.close()
        return []

    rows = c.fetchall()
    conn.close()
    return rows

class ReportWindow(tk.Toplevel):
    def __init__(self, master, user_id, period):
        super().__init__(master)
        self.user_id = user_id
        self.period = period
        self.title(f"Raport {period}")
        self.geometry("700x400")
        self.create_widgets()
        self.populate_report()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("datetime", "type", "amount", "description"), show="headings")
        self.tree.heading("datetime", text="Data i godzina")
        self.tree.heading("type", text="Typ")
        self.tree.heading("amount", text="Kwota")
        self.tree.heading("description", text="Opis")

        self.tree.column("datetime", width=150, anchor='center')
        self.tree.column("type", width=80, anchor='center')
        self.tree.column("amount", width=100, anchor='center')
        self.tree.column("description", width=350, anchor='center')

        self.tree.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)

        self.export_btn = tk.Button(self, text="Eksportuj do CSV", command=self.export_csv)
        self.export_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.export_pdf_btn = tk.Button(self, text="Eksportuj do PDF", command=self.export_pdf)
        self.export_pdf_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.sum_label = tk.Label(self, text="")
        self.sum_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def populate_report(self):
        self.tree.delete(*self.tree.get_children())
        rows = get_report_rows(self.user_id, self.period)
        total_in = 0
        total_out = 0
        for dt, amount, desc in rows:
            typ = "Wpłata" if amount > 0 else "Wypłata"
            self.tree.insert("", tk.END, values=(dt, typ, f"{amount:.2f}", desc))
            if amount > 0:
                total_in += amount
            else:
                total_out += abs(amount)
        self.sum_label.config(text=f"Suma wpłat: {total_in:.2f}   Suma wypłat: {total_out:.2f}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="Zapisz raport jako")
        if not file_path:
            return
        rows = get_report_rows(self.user_id, self.period)
        try:
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Data i godzina", "Typ", "Kwota", "Opis"])
                for dt, amount, desc in rows:
                    typ = "Wpłata" if amount > 0 else "Wypłata"
                    writer.writerow([dt, typ, f"{amount:.2f}", desc])
            messagebox.showinfo("Eksport", f"Raport został zapisany do:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać pliku:\n{e}")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                                                 title="Zapisz raport jako")
        if not file_path:
            return
        rows = get_report_rows(self.user_id, self.period)
        try:
            c = pdf_canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica", 12)
            c.drawString(30, height - 30, f"Raport: {self.period} - użytkownik ID: {self.user_id}")
            c.drawString(30, height - 50, f"Data wygenerowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            y = height - 80
            c.setFont("Helvetica-Bold", 10)
            c.drawString(30, y, "Data i godzina")
            c.drawString(150, y, "Typ")
            c.drawString(220, y, "Kwota")
            c.drawString(280, y, "Opis")
            c.setFont("Helvetica", 10)
            y -= 20

            total_in = 0
            total_out = 0
            for dt, amount, desc in rows:
                if y < 50:
                    c.showPage()
                    y = height - 50
                typ = "Wpłata" if amount > 0 else "Wypłata"
                c.drawString(30, y, dt)
                c.drawString(150, y, typ)
                c.drawRightString(260, y, f"{amount:.2f}")
                c.drawString(280, y, desc)
                y -= 20
                if amount > 0:
                    total_in += amount
                else:
                    total_out += abs(amount)

            if y < 100:
                c.showPage()
                y = height - 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y - 10, f"Suma wpłat: {total_in:.2f}")
            c.drawString(150, y - 10, f"Suma wypłat: {total_out:.2f}")

            c.save()
            messagebox.showinfo("Eksport PDF", f"Raport PDF został zapisany do:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać PDF:\n{e}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Kasowy - logowanie")
        self.user_id = None
        self.create_login()

    def create_login(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text="Login:").pack()
        self.login_entry = tk.Entry(self.root)
        self.login_entry.pack()
        tk.Label(self.root, text="Hasło:").pack()
        self.pw_entry = tk.Entry(self.root, show="*")
        self.pw_entry.pack()
        tk.Button(self.root, text="Zaloguj", command=self.login).pack(pady=5)

    def login(self):
        username = self.login_entry.get()
        password = self.pw_entry.get()
        user = get_user(username)
        if user and user[1] == password:
            self.user_id = user[0]
            self.create_main()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło")

    def create_main(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text=f"Zalogowano jako ID: {self.user_id}").pack(anchor='nw', padx=5, pady=5)

        # FRAME PRZESZUKIWANIA
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_transactions())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_label = tk.Label(search_frame, text="Szukaj:")
        search_label.pack(side=tk.LEFT, padx=(0,5))

        # LEWY PANEL Z PRZYCISKAMI
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Button(left_frame, text="Dodaj wpłatę", command=self.deposit, width=20).pack(pady=3)
        tk.Button(left_frame, text="Dodaj wypłatę", command=self.withdraw, width=20).pack(pady=3)
        tk.Button(left_frame, text="Wpłata kartą", command=self.deposit_card, width=20).pack(pady=3)
        tk.Button(left_frame, text="Wpłata przelewem", command=self.deposit_transfer, width=20).pack(pady=3)
        tk.Button(left_frame, text="Raport dzienny", command=self.open_daily_report, width=20).pack(pady=3)
        tk.Button(left_frame, text="Raport miesięczny", command=self.open_monthly_report, width=20).pack(pady=3)
        tk.Button(left_frame, text="Raport roczny", command=self.open_yearly_report, width=20).pack(pady=3)
        tk.Button(left_frame, text="Raport wpłat gotówkowych", command=self.open_cash_report, width=20).pack(pady=3)
        tk.Button(left_frame, text="Sprawdź saldo", command=self.check_balance, width=20).pack(pady=3)
        tk.Button(left_frame, text="Kopia bazy danych", command=self.backup_db, width=20).pack(pady=10)
        tk.Button(left_frame, text="Wyloguj", command=self.create_login, width=20).pack(pady=3)

        # PRAWY PANEL Z TABELĄ
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("datetime", "type", "amount", "description")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.tree.heading("datetime", text="Data i godzina", command=lambda: self.sort_by("datetime", False))
        self.tree.heading("type", text="Typ", command=lambda: self.sort_by("type", False))
        self.tree.heading("amount", text="Kwota", command=lambda: self.sort_by("amount", False))
        self.tree.heading("description", text="Opis", command=lambda: self.sort_by("description", False))

        self.tree.column("datetime", width=150, anchor='center')
        self.tree.column("type", width=80, anchor='center')
        self.tree.column("amount", width=100, anchor='center')
        self.tree.column("description", width=350, anchor='center')

        self.tree.pack(expand=True, fill=tk.BOTH)

        self.status_label = tk.Label(right_frame, text="", anchor='e')
        self.status_label.pack(fill=tk.X, pady=5)

        self.refresh_list()

    def refresh_list(self):
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        self.tree.delete(*self.tree.get_children())
        transactions = get_transactions(self.user_id)
        total_in = 0
        total_out = 0
        for dt, amount, desc in transactions:
            typ = "Wpłata" if amount > 0 else "Wypłata"
            line = f"{dt} | {typ} | {amount:.2f} | {desc}"
            if search_text in line.lower():
                self.tree.insert("", tk.END, values=(dt, typ, f"{amount:.2f}", desc))
                if amount > 0:
                    total_in += amount
                else:
                    total_out += abs(amount)
        saldo = total_in - total_out
        self.status_label.config(text=f"Suma wpłat: {total_in:.2f}   Suma wypłat: {total_out:.2f}   Saldo: {saldo:.2f}")

    def filter_transactions(self):
        self.refresh_list()

    def deposit(self):
        amount = simpledialog.askfloat("Wpłata gotówkowa", "Kwota wpłaty:")
        if amount is None or amount <= 0:
            messagebox.showwarning("Niepoprawne dane", "Kwota musi być dodatnia")
            return
        desc = simpledialog.askstring("Opis", "Opis wpłaty:")
        if desc is None:
            desc = ""
        add_transaction(self.user_id, amount, desc)
        self.refresh_list()

    def deposit_card(self):
        amount = simpledialog.askfloat("Wpłata kartą", "Kwota wpłaty kartą:")
        if amount is None or amount <= 0:
            messagebox.showwarning("Niepoprawne dane", "Kwota musi być dodatnia")
            return
        desc = simpledialog.askstring("Opis", "Opis wpłaty kartą:")
        if desc is None:
            desc = ""
        desc += " [Karta]"
        add_transaction(self.user_id, amount, desc)
        self.refresh_list()

    def deposit_transfer(self):
        amount = simpledialog.askfloat("Wpłata przelewem", "Kwota wpłaty przelewem:")
        if amount is None or amount <= 0:
            messagebox.showwarning("Niepoprawne dane", "Kwota musi być dodatnia")
            return
        desc = simpledialog.askstring("Opis", "Opis wpłaty przelewem:")
        if desc is None:
            desc = ""
        desc += " [Przelew]"
        add_transaction(self.user_id, amount, desc)
        self.refresh_list()

    def withdraw(self):
        amount = simpledialog.askfloat("Wypłata", "Kwota wypłaty:")
        if amount is None or amount <= 0:
            messagebox.showwarning("Niepoprawne dane", "Kwota musi być dodatnia")
            return
        desc = simpledialog.askstring("Opis", "Opis wypłaty:")
        if desc is None:
            desc = ""
        add_transaction(self.user_id, -amount, desc)
        self.refresh_list()

    def open_daily_report(self):
        ReportWindow(self.root, self.user_id, 'daily')

    def open_monthly_report(self):
        ReportWindow(self.root, self.user_id, 'monthly')

    def open_yearly_report(self):
        ReportWindow(self.root, self.user_id, 'yearly')

    def open_cash_report(self):
        ReportWindow(self.root, self.user_id, 'cash')

    def check_balance(self):
        transactions = get_transactions(self.user_id)
        saldo = sum(amount for _, amount, _ in transactions)
        messagebox.showinfo("Saldo", f"Twoje saldo wynosi: {saldo:.2f}")

    def backup_db(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db",
                                                 filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                                                 title="Zapisz kopię bazy danych jako")
        if not file_path:
            return
        try:
            with open(DB_NAME, "rb") as src, open(file_path, "wb") as dst:
                dst.write(src.read())
            messagebox.showinfo("Kopia bazy", f"Kopia bazy została zapisana do:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zrobić kopii bazy:\n{e}")

    def sort_by(self, col, descending):
        # Pobierz dane z drzewa i posortuj
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        if col == "amount":
            data.sort(key=lambda t: float(t[0]), reverse=descending)
        elif col == "datetime":
            data.sort(key=lambda t: datetime.strptime(t[0], "%Y-%m-%d %H:%M:%S"), reverse=descending)
        else:
            data.sort(reverse=descending)
        # Przełóż posortowane elementy z powrotem do drzewa
        for index, (val, iid) in enumerate(data):
            self.tree.move(iid, '', index)
        # Odwróć kolejność sortowania przy następnym kliknięciu
        self.tree.heading(col, command=lambda: self.sort_by(col, not descending))


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.geometry("900x600")
    app = App(root)
    root.mainloop()