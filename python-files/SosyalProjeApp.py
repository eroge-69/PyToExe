#!/usr/bin/env python3
"""
Sosyal Proje Takip - Masaüstü Uygulama
- SQLite veritabanı kullanır (sosyal_proje.db)
- TC ile arama, yeni kayıt ekleme, güncelleme, silme
- Yardım türü dropdown, otomatik tarih
- Kayıtları listeleme ve Excel'e aktarma
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os

try:
    import openpyxl
    from openpyxl import Workbook
except Exception:
    openpyxl = None

APP_DB = os.path.join(os.path.dirname(__file__), "sosyal_proje.db")

HELP_TYPES = ["Gıda kolisi", "Giysi", "Yakacak", "Bebek bezi", "Hasta Bezi", "Diğer"]
STATUS_TYPES = ["İhtiyaç Sahibi", "Evde bakım", "Traş hizmeti", "Banyo hizmeti"]

def init_db():
    conn = sqlite3.connect(APP_DB)
    cur = conn.cursor()
    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tc TEXT UNIQUE,
        name TEXT,
        status TEXT,
        visited_date TEXT,
        help_given TEXT,
        notes TEXT
    )
    """
    )
    conn.commit()
    conn.close()

def add_sample_data():
    conn = sqlite3.connect(APP_DB)
    cur = conn.cursor()
    samples = [
        
    ]
    for s in samples:
        try:
            cur.execute("INSERT INTO records (tc,name,status,visited_date,help_given,notes) VALUES (?,?,?,?,?,?)", s)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sosyal Proje Takip Sistemi")
        self.geometry("1024x768")
        self.resizable(False, False)
        self.create_widgets()
        init_db()
        add_sample_data()
        self.load_records()

    def create_widgets(self):
        # Frames
        left = ttk.Frame(self, padding=(10,10))
        left.place(x=10, y=10, width=380, height=540)
        right = ttk.Frame(self, padding=(10,10))
        right.place(x=400, y=10, width=625, height=640)

        # Left - Form
        ttk.Label(left, text="TC Kimlik No:").pack(anchor="w")
        self.tc_var = tk.StringVar()
        self.tc_entry = ttk.Entry(left, textvariable=self.tc_var)
        self.tc_entry.pack(fill="x")

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=(6,8))
        ttk.Button(btn_frame, text="TC İle Ara", command=self.search_by_tc).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(btn_frame, text="Yeni Kişi Ekle", command=self.clear_form).pack(side="left", expand=True, fill="x", padx=2)

        ttk.Label(left, text="Ad Soyad:").pack(anchor="w")
        self.name_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.name_var).pack(fill="x")

        ttk.Label(left, text="Durum:").pack(anchor="w")
        self.status_cb = ttk.Combobox(left, values=STATUS_TYPES, state="readonly")
        self.status_cb.pack(fill="x")
        self.status_cb.set(STATUS_TYPES[0])

        ttk.Label(left, text="Gidilen Tarih:").pack(anchor="w")
        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        ttk.Entry(left, textvariable=self.date_var).pack(fill="x")

        ttk.Label(left, text="Yapılan Yardım:").pack(anchor="w")
        self.help_cb = ttk.Combobox(left, values=HELP_TYPES)
        self.help_cb.pack(fill="x")

        ttk.Label(left, text="Notlar:").pack(anchor="w")
        self.notes_txt = tk.Text(left, height=6)
        self.notes_txt.pack(fill="both")

        action_frame = ttk.Frame(left)
        action_frame.pack(fill="x", pady=(8,0))
        ttk.Button(action_frame, text="Kaydet", command=self.save_record).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(action_frame, text="Güncelle", command=self.update_record).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(action_frame, text="Sil", command=self.delete_record).pack(side="left", expand=True, fill="x", padx=2)

        # Right - Record list and controls
        top_controls = ttk.Frame(right)
        top_controls.pack(fill="x")
        ttk.Label(top_controls, text="Ara (isim veya TC):").pack(side="left")
        self.search_var = tk.StringVar()
        s_entry = ttk.Entry(top_controls, textvariable=self.search_var)
        s_entry.pack(side="left", expand=True, fill="x", padx=6)
        ttk.Button(top_controls, text="Ara", command=self.search_list).pack(side="left")
        ttk.Button(top_controls, text="Hepsini Göster", command=self.load_records).pack(side="left", padx=4)

        columns = ("id","tc","name","status","date","help","notes")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=30, anchor="center")
        self.tree.heading("tc", text="TC")
        self.tree.column("tc", width=110)
        self.tree.heading("name", text="Ad Soyad")
        self.tree.column("name", width=120)
        self.tree.heading("status", text="Durum")
        self.tree.column("status", width=80)
        self.tree.heading("date", text="Gidilen Tarih")
        self.tree.column("date", width=90)
        self.tree.heading("help", text="Yapılan Yardım")
        self.tree.column("help", width=110)
        self.tree.heading("notes", text="Notlar")
        self.tree.column("notes", width=140)

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both")

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        bottom_controls = ttk.Frame(right)
        bottom_controls.pack(fill="x", pady=(6,0))
        ttk.Button(bottom_controls, text="Excel'e Aktar", command=self.export_excel).pack(side="left")
        ttk.Button(bottom_controls, text="Seçiliyi Yükle", command=self.load_selected_into_form).pack(side="left", padx=6)

    def db(self):
        return sqlite3.connect(APP_DB)

    def save_record(self):
        tc = self.tc_var.get().strip()
        name = self.name_var.get().strip()
        status = self.status_cb.get().strip()
        date = self.date_var.get().strip()
        help_given = self.help_cb.get().strip()
        notes = self.notes_txt.get("1.0","end").strip()
        if not (tc and name):
            messagebox.showwarning("Eksik Bilgi", "Lütfen TC ve Ad Soyad girin.")
            return
        if not tc.isdigit() or len(tc)!=11:
            if not messagebox.askyesno("Uyarı", "TC 11 haneli değil. Yine de kaydetmek istiyor musunuz?"):
                return
        conn = self.db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO records (tc,name,status,visited_date,help_given,notes) VALUES (?,?,?,?,?,?)", (tc,name,status,date,help_given,notes))
            conn.commit()
            messagebox.showinfo("Başarılı","Kayıt eklendi.")
            self.clear_form()
            self.load_records()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu TC zaten kayıtlı. Güncellemek istiyorsanız 'Güncelle' butonunu kullanın.")
        finally:
            conn.close()

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Lütfen güncellemek için bir kayıt seçin (listeden).")
            return
        item = self.tree.item(selected)
        record_id = item["values"][0]
        tc = self.tc_var.get().strip()
        name = self.name_var.get().strip()
        status = self.status_cb.get().strip()
        date = self.date_var.get().strip()
        help_given = self.help_cb.get().strip()
        notes = self.notes_txt.get("1.0","end").strip()
        if not (tc and name):
            messagebox.showwarning("Eksik Bilgi", "Lütfen TC ve Ad Soyad girin.")
            return
        conn = self.db()
        cur = conn.cursor()
        cur.execute("UPDATE records SET tc=?,name=?,status=?,visited_date=?,help_given=?,notes=? WHERE id=?", (tc,name,status,date,help_given,notes,record_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Güncellendi", "Kayıt güncellendi.")
        self.load_records()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Lütfen silmek için bir kayıt seçin (listeden).")
            return
        if not messagebox.askyesno("Onay", "Seçili kaydı silmek istediğinize emin misiniz?"):
            return
        item = self.tree.item(selected)
        record_id = item["values"][0]
        conn = self.db()
        cur = conn.cursor()
        cur.execute("DELETE FROM records WHERE id=?", (record_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Silindi", "Kayıt silindi.")
        self.load_records()
        self.clear_form()

    def load_records(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = self.db()
        cur = conn.cursor()
        cur.execute("SELECT id,tc,name,status,visited_date,help_given,notes FROM records ORDER BY id DESC")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def search_by_tc(self):
        tc = self.tc_var.get().strip()
        if not tc:
            messagebox.showwarning("Eksik", "Lütfen aramak için TC girin.")
            return
        conn = self.db()
        cur = conn.cursor()
        cur.execute("SELECT id,tc,name,status,visited_date,help_given,notes FROM records WHERE tc=?", (tc,))
        row = cur.fetchone()
        conn.close()
        if not row:
            messagebox.showinfo("Bulunamadı", "Kayıt bulunamadı.")
            return
        # Yükle
        self.load_row_into_form(row)

    def search_list(self):
        q = self.search_var.get().strip().lower()
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = self.db()
        cur = conn.cursor()
        cur.execute("SELECT id,tc,name,status,visited_date,help_given,notes FROM records WHERE lower(tc) LIKE ? OR lower(name) LIKE ? ORDER BY id DESC", (f"%{q}%",f"%{q}%"))
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def load_row_into_form(self, row):
        # row: (id,tc,name,status,date,help,notes)
        self.tc_var.set(row[1])
        self.name_var.set(row[2])
        self.status_cb.set(row[3] if row[3] else STATUS_TYPES[0])
        self.date_var.set(row[4] if row[4] else datetime.today().strftime("%Y-%m-%d"))
        self.help_cb.set(row[5] if row[5] else "")
        self.notes_txt.delete("1.0","end")
        self.notes_txt.insert("1.0", row[6] if row[6] else "")

    def on_tree_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected)
        row = item["values"]
        self.load_row_into_form(row)

    def load_selected_into_form(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Listeden bir kayıt seçin.")
            return
        item = self.tree.item(selected)
        self.load_row_into_form(item["values"])

    def clear_form(self):
        self.tc_var.set("")
        self.name_var.set("")
        self.status_cb.set(STATUS_TYPES[0])
        self.date_var.set(datetime.today().strftime("%Y-%m-%d"))
        self.help_cb.set("")
        self.notes_txt.delete("1.0","end")

    def export_excel(self):
        if openpyxl is None:
            messagebox.showerror("Kütüphane Eksik", "Excel aktarımı için 'openpyxl' yüklü olmalı. (pip install openpyxl)")
            return
        conn = self.db()
        cur = conn.cursor()
        cur.execute("SELECT tc,name,status,visited_date,help_given,notes FROM records ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("Boş", "Export edilecek kayıt yok.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[("Excel files","*.xlsx")], initialfile="Sosyal_Proje_Kayitlari.xlsx")
        if not filepath:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "Kayıtlar"
        ws.append(["TC","Ad Soyad","Durum","Gidilen Tarih","Yapılan Yardım","Notlar"])
        for r in rows:
            ws.append(list(r))
        wb.save(filepath)
        messagebox.showinfo("Başarılı", f"Veriler {filepath} olarak kaydedildi.")

if __name__ == "__main__":
    init_db()
    add_sample_data()
    app = App()
    app.mainloop()