# ================================================================
# ALSAN GÜVENLİK TEKNOLOJİLERİ - Satış ve Müşteri Takip Sistemi v3.0
# ================================================================
# Özellikler:
# - Türkçe arayüz (koyu tema)
# - Müşteri ve ürün yönetimi
# - Toptan / Perakende fiyat
# - Döviz destekli (₺, $, €)
# - Otomatik TCMB döviz kuru
# - Satış ekranı (müşteri zorunlu)
# - PDF satış raporu (TL bazlı toplam)
# - Otomatik günlük yedekleme
# ================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, os, datetime, requests, shutil, webbrowser
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DB_FILE = "alsan_pos.db"
BACKUP_DIR = "yedekler"
REPORT_DIR = "raporlar"

# ------------------------------------------------------------
# Veritabanı oluşturma
# ------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            type TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT,
            price_retail REAL,
            price_wholesale REAL,
            currency TEXT,
            stock INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            customer_id INTEGER,
            total REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sale_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            currency TEXT,
            FOREIGN KEY(sale_id) REFERENCES sales(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            id INTEGER PRIMARY KEY,
            usd_rate REAL,
            eur_rate REAL,
            last_update TEXT
        )
    """)
    conn.commit()
    conn.close()

# ------------------------------------------------------------
# Döviz Kuru Güncelleme
# ------------------------------------------------------------
def update_exchange_rates():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=TRY")
        data = r.json()
        usd = 1 / data["rates"]["USD"]
        eur = 1 / data["rates"]["EUR"]
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM settings")
        c.execute("INSERT INTO settings (usd_rate, eur_rate, last_update) VALUES (?,?,?)",
                  (usd, eur, datetime.date.today().isoformat()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Bilgi", f"Döviz kurları güncellendi:\nUSD: {usd:.2f} ₺\nEUR: {eur:.2f} ₺")
    except Exception as e:
        messagebox.showerror("Hata", f"Döviz kurları alınamadı:\n{e}")

def get_rates():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT usd_rate, eur_rate FROM settings LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return {"USD": row[0], "EUR": row[1], "TRY": 1}
    else:
        return {"USD": 35.0, "EUR": 37.0, "TRY": 1}

# ------------------------------------------------------------
# Yedekleme
# ------------------------------------------------------------
def backup_db():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    shutil.copy(DB_FILE, f"{BACKUP_DIR}/alsan_yedek_{now}.db")

# ------------------------------------------------------------
# PDF Rapor Oluşturma
# ------------------------------------------------------------
def create_pdf(sale_id, customer_name, items, total_tl):
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    file_name = f"{REPORT_DIR}/satis_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "ALSAN GÜVENLİK TEKNOLOJİLERİ - Satış Raporu")
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
    y -= 15
    c.drawString(50, y, f"Müşteri: {customer_name}")
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Ürün Adı")
    c.drawString(250, y, "Adet")
    c.drawString(300, y, "Fiyat")
    c.drawString(380, y, "Para")
    c.drawString(450, y, "TL Karşılığı")
    y -= 10
    c.line(50, y, 550, y)
    y -= 20
    c.setFont("Helvetica", 10)
    for i in items:
        c.drawString(50, y, i["name"])
        c.drawString(250, y, str(i["qty"]))
        c.drawString(300, y, str(i["price"]))
        c.drawString(380, y, i["currency"])
        c.drawString(450, y, f"{i['tl_value']:.2f} ₺")
        y -= 20
    y -= 10
    c.line(50, y, 550, y)
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y, f"TOPLAM: {total_tl:.2f} ₺")
    c.save()
    webbrowser.open(file_name)

# ------------------------------------------------------------
# Ana Arayüz
# ------------------------------------------------------------
class AlsanPOS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ALSAN GÜVENLİK TEKNOLOJİLERİ - Satış Takip Sistemi")
        self.geometry("950x600")
        self.configure(bg="#1e1e1e")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        self.style.configure("TButton", background="#cc0000", foreground="white")
        self.create_main_menu()

    def clear_frame(self):
        for w in self.winfo_children():
            w.destroy()

    def create_main_menu(self):
        self.clear_frame()
        tk.Label(self, text="ALSAN GÜVENLİK TEKNOLOJİLERİ", bg="#1e1e1e", fg="#cc0000", font=("Arial", 20, "bold")).pack(pady=30)
        buttons = [
            ("Müşteri Yönetimi", self.open_customers),
            ("Ürün Yönetimi", self.open_products),
            ("Satış Ekranı", self.open_sales),
            ("Kurları Güncelle", update_exchange_rates),
            ("Yedekleme", backup_db)
        ]
        for text, cmd in buttons:
            ttk.Button(self, text=text, command=cmd).pack(pady=10, ipadx=30, ipady=10)

    # --------------------------------------------------------
    # Müşteri Yönetimi
    # --------------------------------------------------------
    def open_customers(self):
        self.clear_frame()
        tk.Label(self, text="Müşteri Yönetimi", fg="white", bg="#1e1e1e", font=("Arial", 16)).pack(pady=10)
        frame = tk.Frame(self, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)
        cols = ("ID", "Ad", "Telefon", "Adres", "Tür")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)
        tree.pack(fill="both", expand=True, pady=10)
        def load_customers():
            for i in tree.get_children():
                tree.delete(i)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM customers")
            for r in c.fetchall():
                tree.insert("", "end", values=r)
            conn.close()
        def add_customer():
            win = tk.Toplevel(self)
            win.title("Müşteri Ekle")
            tk.Label(win, text="Ad Soyad").grid(row=0, column=0)
            name = tk.Entry(win)
            name.grid(row=0, column=1)
            tk.Label(win, text="Telefon").grid(row=1, column=0)
            phone = tk.Entry(win)
            phone.grid(row=1, column=1)
            tk.Label(win, text="Adres").grid(row=2, column=0)
            addr = tk.Entry(win)
            addr.grid(row=2, column=1)
            tk.Label(win, text="Tür").grid(row=3, column=0)
            ttype = ttk.Combobox(win, values=["Toptan", "Perakende"])
            ttype.grid(row=3, column=1)
            def save():
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO customers (name,phone,address,type) VALUES (?,?,?,?)",
                          (name.get(), phone.get(), addr.get(), ttype.get()))
                conn.commit()
                conn.close()
                load_customers()
                win.destroy()
            tk.Button(win, text="Kaydet", command=save).grid(row=4, column=0, columnspan=2)
        ttk.Button(self, text="Yeni Müşteri", command=add_customer).pack(pady=5)
        ttk.Button(self, text="Geri", command=self.create_main_menu).pack(pady=5)
        load_customers()

    # --------------------------------------------------------
    # Ürün Yönetimi
    # --------------------------------------------------------
    def open_products(self):
        self.clear_frame()
        tk.Label(self, text="Ürün Yönetimi", fg="white", bg="#1e1e1e", font=("Arial", 16)).pack(pady=10)
        frame = tk.Frame(self, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)
        cols = ("ID", "Barkod", "Ad", "Perakende", "Toptan", "Para", "Stok")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)
        tree.pack(fill="both", expand=True, pady=10)
        def load_products():
            for i in tree.get_children():
                tree.delete(i)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM products")
            for r in c.fetchall():
                tree.insert("", "end", values=r)
            conn.close()
        def add_product():
            win = tk.Toplevel(self)
            win.title("Ürün Ekle")
            labels = ["Barkod", "Ürün Adı", "Perakende Fiyat", "Toptan Fiyat", "Para Birimi (₺/$/€)", "Stok"]
            entries = []
            for i, lbl in enumerate(labels):
                tk.Label(win, text=lbl).grid(row=i, column=0)
                e = tk.Entry(win)
                e.grid(row=i, column=1)
                entries.append(e)
            def save():
                barkod, ad, per, top, para, stok = [e.get() for e in entries]
                if para not in ["₺", "$", "€"]:
                    messagebox.showerror("Hata", "Para birimi ₺, $, € olmalı!")
                    return
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO products (barcode,name,price_retail,price_wholesale,currency,stock) VALUES (?,?,?,?,?,?)",
                          (barkod, ad, per, top, para, stok))
                conn.commit()
                conn.close()
                load_products()
                win.destroy()
            tk.Button(win, text="Kaydet", command=save).grid(row=len(labels), column=0, columnspan=2)
        ttk.Button(self, text="Yeni Ürün", command=add_product).pack(pady=5)
        ttk.Button(self, text="Geri", command=self.create_main_menu).pack(pady=5)
        load_products()

    # --------------------------------------------------------
    # Satış Ekranı
    # --------------------------------------------------------
    def open_sales(self):
        self.clear_frame()
        tk.Label(self, text="Satış Ekranı", fg="white", bg="#1e1e1e", font=("Arial", 16)).pack(pady=10)
        frame = tk.Frame(self, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Müşteri Seç:", fg="white", bg="#1e1e1e").grid(row=0, column=0)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, type FROM customers")
        customers = c.fetchall()
        conn.close()
        cust_var = tk.StringVar()
        cust_cb = ttk.Combobox(frame, textvariable=cust_var, values=[f"{cid} - {name} ({ctype})" for cid, name, ctype in customers])
        cust_cb.grid(row=0, column=1)
        tk.Label(frame, text="Barkod:", fg="white", bg="#1e1e1e").grid(row=1, column=0)
        barcode_entry = tk.Entry(frame)
        barcode_entry.grid(row=1, column=1)
        cols = ("Ürün", "Adet", "Fiyat", "Para", "TL Değeri")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        for c in cols:
            tree.heading(c, text=c)
        tree.grid(row=2, column=0, columnspan=4, pady=10)
        total_label = tk.Label(frame, text="TOPLAM: 0 ₺", fg="#cc0000", bg="#1e1e1e", font=("Arial", 14, "bold"))
        total_label.grid(row=3, column=0, columnspan=2)
        rates = get_rates()
        cart = []
        def add_to_cart(event=None):
            code = barcode_entry.get().strip()
            if not code:
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id,name,price_retail,price_wholesale,currency FROM products WHERE barcode=?", (code,))
            p = c.fetchone()
            conn.close()
            if not p:
                messagebox.showerror("Hata", "Ürün bulunamadı!")
                return
            if not cust_cb.get():
                messagebox.showerror("Hata", "Önce müşteri seçiniz!")
                return
            cust_type = "Perakende" if "Perakende" in cust_cb.get() else "Toptan"
            price = p[2] if cust_type == "Perakende" else p[3]
            cur = p[4]
            tl_value = float(price) * rates["TRY"] if cur == "₺" else float(price) * rates["USD"] if cur == "$" else float(price) * rates["EUR"]
            cart.append({"id": p[0], "name": p[1], "price": price, "currency": cur, "tl_value": tl_value, "qty": 1})
            tree.insert("", "end", values=(p[1], 1, price, cur, f"{tl_value:.2f} ₺"))
            total_tl = sum(i["tl_value"] for i in cart)
            total_label.config(text=f"TOPLAM: {total_tl:.2f} ₺")
            barcode_entry.delete(0, tk.END)
        barcode_entry.bind("<Return>", add_to_cart)
        def complete_sale():
            if not cust_cb.get():
                messagebox.showerror("Hata", "Müşteri seçmeden satış yapılamaz!")
                return
            if not cart:
                messagebox.showerror("Hata", "Sepet boş!")
                return
            cust_id = int(cust_cb.get().split(" - ")[0])
            total_tl = sum(i["tl_value"] for i in cart)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO sales (date, customer_id, total) VALUES (?,?,?)",
                      (datetime.datetime.now().isoformat(), cust_id, total_tl))
            sale_id = c.lastrowid
            for i in cart:
                c.execute("INSERT INTO sale_items (sale_id, product_id, quantity, price, currency) VALUES (?,?,?,?,?)",
                          (sale_id, i["id"], i["qty"], i["price"], i["currency"]))
            conn.commit()
            conn.close()
            create_pdf(sale_id, cust_cb.get(), cart, total_tl)
            backup_db()
            messagebox.showinfo("Bilgi", "Satış tamamlandı ve rapor oluşturuldu.")
            self.create_main_menu()
        ttk.Button(frame, text="Satışı Tamamla", command=complete_sale).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Geri", command=self.create_main_menu).grid(row=4, column=1)
# ------------------------------------------------------------
if __name__ == "__
