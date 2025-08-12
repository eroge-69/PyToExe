import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    messagebox.showerror("Error", "Module reportlab belum terinstall.\nJalankan: pip install reportlab")
    raise

try:
    import pandas as pd
except ImportError:
    messagebox.showerror("Error", "Module pandas belum terinstall.\nJalankan: pip install pandas openpyxl")
    raise

try:
    import tabula
except ImportError:
    messagebox.showerror("Error", "Module tabula-py belum terinstall.\nJalankan: pip install tabula-py")
    raise

DB_FILE = "data_pemilih.db"

KECAMATAN_LIST = [
    "Candisari", "Gajahmungkur", "Gayamsari", "Genuk", "Gunungpati",
    "Mijen", "Ngaliyan", "Pedurungan", "Semarang Barat", "Semarang Selatan",
    "Semarang Tengah", "Semarang Timur", "Semarang Utara", "Tembalang",
    "Tugu", "Banyumanik"
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pemilih (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor TEXT,
            nama TEXT NOT NULL,
            nik TEXT UNIQUE NOT NULL,
            alamat TEXT,
            kelurahan TEXT,
            kecamatan TEXT,
            no_tps TEXT,
            koordinator TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_next_nomor():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT nomor FROM pemilih ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        try:
            next_num = int(row[0]) + 1
        except ValueError:
            next_num = 1
    else:
        next_num = 1
    return str(next_num)

def insert_pemilih(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pemilih (nomor, nama, nik, alamat, kelurahan, kecamatan, no_tps, koordinator)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def update_pemilih(id_, data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE pemilih SET nomor=?, nama=?, nik=?, alamat=?, kelurahan=?, kecamatan=?, no_tps=?, koordinator=?
            WHERE id=?
        """, (*data, id_))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def delete_pemilih(id_):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM pemilih WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def fetch_pemilih(filters=None):
    filters = filters or {}
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    query = "SELECT id, nomor, nama, nik, alamat, kelurahan, kecamatan, no_tps, koordinator FROM pemilih WHERE 1=1"
    params = []
    for key, val in filters.items():
        if val:
            query += f" AND {key} LIKE ?"
            params.append(f"%{val}%")
    query += " ORDER BY id"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def export_pdf(rows):
    if not rows:
        messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport.")
        return

    path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Simpan Laporan PDF")
    if not path:
        return

    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    elems = []

    elems.append(Paragraph("LAPORAN DATA PEMILIH DPRD KOTA SEMARANG", styles['Title']))
    elems.append(Spacer(1, 12))
    elems.append(Paragraph(f"Di-export: {datetime.now().strftime('%d %B %Y %H:%M:%S')}", styles['Normal']))
    elems.append(Spacer(1, 12))

    # Header tanpa kolom ID
    data = [["Nomor","Nama","NIK","Alamat","Kelurahan","Kecamatan","No TPS","Koordinator"]]
    for row in rows:
        # row = (id, nomor, nama, nik, alamat, kelurahan, kecamatan, no_tps, koordinator)
        # Buang kolom id (index 0)
        data.append(list(map(str, row[1:])))

    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))

    elems.append(t)
    doc.build(elems)
    messagebox.showinfo("Sukses", f"Laporan PDF berhasil disimpan:\n{path}")

def export_excel(rows):
    if not rows:
        messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport.")
        return

    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Simpan Laporan Excel")
    if not path:
        return

    data = [list(row[1:]) for row in rows]  # tanpa id
    columns = ["Nomor","Nama","NIK","Alamat","Kelurahan","Kecamatan","No TPS","Koordinator"]

    df = pd.DataFrame(data, columns=columns)
    try:
        df.to_excel(path, index=False)
        messagebox.showinfo("Sukses", f"Laporan Excel berhasil disimpan:\n{path}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan Excel:\n{str(e)}")

def import_excel(app):
    path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")], title="Pilih File Excel untuk Import")
    if not path:
        return

    try:
        df = pd.read_excel(path)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuka file Excel:\n{str(e)}")
        return

    required_cols = {"Nomor","Nama","NIK","Alamat","Kelurahan","Kecamatan","No TPS","Koordinator"}
    if not required_cols.issubset(set(df.columns)):
        messagebox.showerror("Error", f"File Excel harus berisi kolom: {', '.join(required_cols)}")
        return

    count_inserted = 0
    count_failed = 0
    for _, row in df.iterrows():
        data = (
            str(row["Nomor"]),
            str(row["Nama"]),
            str(row["NIK"]),
            str(row["Alamat"]) if not pd.isna(row["Alamat"]) else "",
            str(row["Kelurahan"]),
            str(row["Kecamatan"]),
            str(row["No TPS"]) if not pd.isna(row["No TPS"]) else "",
            str(row["Koordinator"]) if not pd.isna(row["Koordinator"]) else "",
        )
        success, err = insert_pemilih(data)
        if success:
            count_inserted += 1
        else:
            count_failed += 1
    messagebox.showinfo("Import Selesai", f"Berhasil impor {count_inserted} data.\nGagal: {count_failed} data (mungkin duplikat).")
    app.load_view()

def import_pdf(app):
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], title="Pilih File PDF untuk Import")
    if not path:
        return

    try:
        # ekstrak semua tabel dalam pdf
        dfs = tabula.read_pdf(path, pages='all', multiple_tables=True)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membaca file PDF:\n{str(e)}")
        return

    count_inserted = 0
    count_failed = 0
    # Coba tiap tabel
    for df in dfs:
        # Pastikan kolom sudah sesuai (case-insensitive)
        df.columns = [c.strip().lower() for c in df.columns]
        # Kolom yg dicari:
        needed_cols = {"nomor","nama","nik","alamat","kelurahan","kecamatan","no tps","koordinator"}
        if not needed_cols.issubset(set(df.columns)):
            continue  # skip tabel yg gak cocok

        # Normalisasi kolom nama agar pas ke insert
        df = df.rename(columns={
            "no tps": "no_tps"
        })
        for _, row in df.iterrows():
            data = (
                str(row["nomor"]),
                str(row["nama"]),
                str(row["nik"]),
                str(row["alamat"]) if not pd.isna(row["alamat"]) else "",
                str(row["kelurahan"]),
                str(row["kecamatan"]),
                str(row["no_tps"]) if not pd.isna(row["no_tps"]) else "",
                str(row["koordinator"]) if not pd.isna(row["koordinator"]) else "",
            )
            success, err = insert_pemilih(data)
            if success:
                count_inserted += 1
            else:
                count_failed += 1

    messagebox.showinfo("Import Selesai", f"Berhasil impor {count_inserted} data dari PDF.\nGagal: {count_failed} data (mungkin duplikat).")
    app.load_view()

class PemilihApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Input Data Pemilih - DPRD Kota Semarang")
        self.root.geometry("900x650")

        # --- Input Frame ---
        frm_input = tk.LabelFrame(root, text="Form Input Data Pemilih", padx=10, pady=10)
        frm_input.pack(fill="x", padx=10, pady=5)

        # Nomor (otomatis)
        tk.Label(frm_input, text="Nomor:").grid(row=0, column=0, sticky="e")
        self.var_nomor = tk.StringVar(value=get_next_nomor())
        self.entry_nomor = tk.Entry(frm_input, textvariable=self.var_nomor, width=10, state='readonly')
        self.entry_nomor.grid(row=0, column=1, padx=5, pady=5)

        # Nama Lengkap
        tk.Label(frm_input, text="Nama Lengkap:").grid(row=0, column=2, sticky="e")
        self.entry_nama = tk.Entry(frm_input, width=30)
        self.entry_nama.grid(row=0, column=3, padx=5, pady=5)

        # NIK
        tk.Label(frm_input, text="NIK (16 digit):").grid(row=1, column=0, sticky="e")
        self.entry_nik = tk.Entry(frm_input, width=30)
        self.entry_nik.grid(row=1, column=1, padx=5, pady=5)

        # Alamat
        tk.Label(frm_input, text="Alamat:").grid(row=1, column=2, sticky="e")
        self.entry_alamat = tk.Entry(frm_input, width=30)
        self.entry_alamat.grid(row=1, column=3, padx=5, pady=5)

        # Kelurahan (teks)
        tk.Label(frm_input, text="Kelurahan:").grid(row=2, column=0, sticky="e")
        self.entry_kelurahan = tk.Entry(frm_input, width=30)
        self.entry_kelurahan.grid(row=2, column=1, padx=5, pady=5)

        # Kecamatan (Combobox)
        tk.Label(frm_input, text="Kecamatan:").grid(row=2, column=2, sticky="e")
        self.cmb_kecamatan = ttk.Combobox(frm_input, values=KECAMATAN_LIST, state='readonly', width=28)
        self.cmb_kecamatan.grid(row=2, column=3, padx=5, pady=5)

        # No TPS
        tk.Label(frm_input, text="No TPS:").grid(row=3, column=0, sticky="e")
        self.entry_no_tps = tk.Entry(frm_input, width=30)
        self.entry_no_tps.grid(row=3, column=1, padx=5, pady=5)

        # Koordinator
        tk.Label(frm_input, text="Koordinator:").grid(row=3, column=2, sticky="e")
        self.entry_koordinator = tk.Entry(frm_input, width=30)
        self.entry_koordinator.grid(row=3, column=3, padx=5, pady=5)

        # Buttons
        frm_buttons = tk.Frame(frm_input)
        frm_buttons.grid(row=4, column=0, columnspan=4, pady=10)
        self.btn_save = tk.Button(frm_buttons, text="Simpan Data", width=15, command=self.save_data)
        self.btn_save.pack(side="left", padx=5)
        self.btn_clear = tk.Button(frm_buttons, text="Bersihkan Form", width=15, command=self.clear_form)
        self.btn_clear.pack(side="left", padx=5)
        self.btn_delete = tk.Button(frm_buttons, text="Hapus Data Terpilih", width=18, command=self.delete_data)
        self.btn_delete.pack(side="left", padx=5)
        self.btn_find = tk.Button(frm_buttons, text="Cari Data", width=15, command=self.open_find_window)
        self.btn_find.pack(side="left", padx=5)

        # --- Filter Frame ---
        frm_filter = tk.LabelFrame(root, text="Filter Data", padx=10, pady=10)
        frm_filter.pack(fill="x", padx=10, pady=5)

        tk.Label(frm_filter, text="Nama:").grid(row=0, column=0, sticky="e")
        self.filter_nama = tk.Entry(frm_filter, width=20)
        self.filter_nama.grid(row=0, column=1, padx=5)

        tk.Label(frm_filter, text="Kelurahan:").grid(row=0, column=2, sticky="e")
        self.filter_kelurahan = tk.Entry(frm_filter, width=20)
        self.filter_kelurahan.grid(row=0, column=3, padx=5)

        tk.Label(frm_filter, text="No TPS:").grid(row=0, column=4, sticky="e")
        self.filter_no_tps = tk.Entry(frm_filter, width=10)
        self.filter_no_tps.grid(row=0, column=5, padx=5)

        tk.Label(frm_filter, text="Koordinator:").grid(row=0, column=6, sticky="e")
        self.filter_koordinator = tk.Entry(frm_filter, width=20)
        self.filter_koordinator.grid(row=0, column=7, padx=5)

        tk.Button(frm_filter, text="Terapkan Filter", command=self.load_view).grid(row=0, column=8, padx=10)

        # --- Treeview ---
        columns = ("id", "nomor", "nama", "nik", "alamat", "kelurahan", "kecamatan", "no_tps", "koordinator")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor="w")
        self.tree.column("nama", width=200)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Export/Import Buttons ---
        frm_export_import = tk.Frame(root)
        frm_export_import.pack(fill="x", padx=10, pady=5)
        tk.Button(frm_export_import, text="Export Laporan PDF", command=self.export_report).pack(side="left", padx=5)
        tk.Button(frm_export_import, text="Export Excel", command=self.export_excel).pack(side="left", padx=5)
        tk.Button(frm_export_import, text="Import Excel", command=lambda: import_excel(self)).pack(side="left", padx=5)
        tk.Button(frm_export_import, text="Import PDF", command=lambda: import_pdf(self)).pack(side="left", padx=5)

        self.selected_id = None
        self.load_view()

    def clear_form(self):
        self.selected_id = None
        self.var_nomor.set(get_next_nomor())
        self.entry_nama.delete(0, tk.END)
        self.entry_nik.delete(0, tk.END)
        self.entry_alamat.delete(0, tk.END)
        self.entry_kelurahan.delete(0, tk.END)
        self.cmb_kecamatan.set("")
        self.entry_no_tps.delete(0, tk.END)
        self.entry_koordinator.delete(0, tk.END)
        self.btn_save.config(text="Simpan Data")

    def save_data(self):
        nama = self.entry_nama.get().strip()
        nik = self.entry_nik.get().strip()
        alamat = self.entry_alamat.get().strip()
        kelurahan = self.entry_kelurahan.get().strip()
        kecamatan = self.cmb_kecamatan.get()
        no_tps = self.entry_no_tps.get().strip()
        koordinator = self.entry_koordinator.get().strip()
        nomor = self.var_nomor.get()

        if not (nama and nik and kelurahan and kecamatan):
            messagebox.showwarning("Peringatan", "Nama, NIK, Kelurahan, dan Kecamatan harus diisi.")
            return
        if len(nik) != 16 or not nik.isdigit():
            messagebox.showwarning("Peringatan", "NIK harus 16 digit angka.")
            return

        data = (nomor, nama, nik, alamat, kelurahan, kecamatan, no_tps, koordinator)

        if self.selected_id is None:
            success, err = insert_pemilih(data)
            if not success:
                messagebox.showerror("Error", f"Gagal menyimpan data:\n{err}")
                return
            messagebox.showinfo("Sukses", "Data berhasil disimpan.")
        else:
            success, err = update_pemilih(self.selected_id, data)
            if not success:
                messagebox.showerror("Error", f"Gagal memperbarui data:\n{err}")
                return
            messagebox.showinfo("Sukses", "Data berhasil diperbarui.")

        self.clear_form()
        self.load_view()

    def load_view(self):
        filters = {
            "nama": self.filter_nama.get().strip(),
            "kelurahan": self.filter_kelurahan.get().strip(),
            "no_tps": self.filter_no_tps.get().strip(),
            "koordinator": self.filter_koordinator.get().strip()
        }
        rows = fetch_pemilih(filters)
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            data = item['values']
            self.selected_id = data[0]
            self.var_nomor.set(data[1])
            self.entry_nama.delete(0, tk.END)
            self.entry_nama.insert(0, data[2])
            self.entry_nik.delete(0, tk.END)
            self.entry_nik.insert(0, data[3])
            self.entry_alamat.delete(0, tk.END)
            self.entry_alamat.insert(0, data[4])
            self.entry_kelurahan.delete(0, tk.END)
            self.entry_kelurahan.insert(0, data[5])
            self.cmb_kecamatan.set(data[6])
            self.entry_no_tps.delete(0, tk.END)
            self.entry_no_tps.insert(0, data[7])
            self.entry_koordinator.delete(0, tk.END)
            self.entry_koordinator.insert(0, data[8])
            self.btn_save.config(text="Perbarui Data")

    def delete_data(self):
        if self.selected_id is None:
            messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu untuk dihapus.")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
            delete_pemilih(self.selected_id)
            messagebox.showinfo("Sukses", "Data berhasil dihapus.")
            self.clear_form()
            self.load_view()

    def open_find_window(self):
        def cari():
            keyword = ent_keyword.get().strip()
            if not keyword:
                messagebox.showwarning("Peringatan", "Masukkan kata kunci pencarian.")
                return
            filters = {
                "nama": keyword,
                "kelurahan": keyword,
                "no_tps": keyword,
                "koordinator": keyword
            }
            rows = fetch_pemilih(filters)
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            find_win.destroy()

        find_win = tk.Toplevel(self.root)
        find_win.title("Cari Data Pemilih")
        find_win.geometry("400x120")
        tk.Label(find_win, text="Masukkan kata kunci (Nama/Kelurahan/No TPS/Koordinator):").pack(padx=10, pady=10)
        ent_keyword = tk.Entry(find_win, width=40)
        ent_keyword.pack(padx=10, pady=5)
        tk.Button(find_win, text="Cari", command=cari).pack(pady=10)

    def export_report(self):
        filters = {
            "nama": self.filter_nama.get().strip(),
            "kelurahan": self.filter_kelurahan.get().strip(),
            "no_tps": self.filter_no_tps.get().strip(),
            "koordinator": self.filter_koordinator.get().strip()
        }
        rows = fetch_pemilih(filters)
        export_pdf(rows)

    def export_excel(self):
        filters = {
            "nama": self.filter_nama.get().strip(),
            "kelurahan": self.filter_kelurahan.get().strip(),
            "no_tps": self.filter_no_tps.get().strip(),
            "koordinator": self.filter_koordinator.get().strip()
        }
        rows = fetch_pemilih(filters)
        export_excel(rows)


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = PemilihApp(root)
    root.mainloop()
