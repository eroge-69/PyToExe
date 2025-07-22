# Novatek Su Sayaç Takip Sistemi

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# ------------------------------
# Veritabanı ve Ayarlar
# ------------------------------
DB_FILE = "su_abone.db"
SETTINGS_FILE = "ayarlar.json"

def create_tables():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS aboneler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT,
                adres TEXT,
                sayac_no TEXT UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS okumalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sayac_no TEXT,
                tarih TEXT,
                onceki_endeks INTEGER,
                son_endeks INTEGER,
                birim_fiyat REAL,
                FOREIGN KEY(sayac_no) REFERENCES aboneler(sayac_no)
            )
        ''')


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"birim_fiyat": 1.96}, f)
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(birim_fiyat):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"birim_fiyat": birim_fiyat}, f)

# ------------------------------
# Ana Uygulama
# ------------------------------
class SuTakipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novatek Su Sayaç Takip Sistemi")
        self.settings = load_settings()
        create_tables()
        self.init_gui()

    def init_gui(self):
        tab_control = ttk.Notebook(self.root)

        # Sekmeler
        self.abone_tab = ttk.Frame(tab_control)
        self.okuma_tab = ttk.Frame(tab_control)
        self.ayar_tab = ttk.Frame(tab_control)

        tab_control.add(self.abone_tab, text='Abone Bilgileri')
        tab_control.add(self.okuma_tab, text='Sayaç Okuma')
        tab_control.add(self.ayar_tab, text='Ayarlar')
        tab_control.pack(expand=1, fill='both')

        self.abone_gui()
        self.okuma_gui()
        self.ayar_gui()

    # -------------------------
    # Abone Arayüzü
    # -------------------------
    def abone_gui(self):
        tk.Label(self.abone_tab, text="Ad Soyad").pack()
        self.ad_entry = tk.Entry(self.abone_tab)
        self.ad_entry.pack()

        tk.Label(self.abone_tab, text="Adres").pack()
        self.adres_entry = tk.Entry(self.abone_tab)
        self.adres_entry.pack()

        tk.Label(self.abone_tab, text="Sayaç No").pack()
        self.sayac_entry = tk.Entry(self.abone_tab)
        self.sayac_entry.pack()

        tk.Button(self.abone_tab, text="Abone Ekle", command=self.abone_ekle).pack(pady=10)

    def abone_ekle(self):
        ad = self.ad_entry.get()
        adres = self.adres_entry.get()
        sayac = self.sayac_entry.get()

        if not (ad and adres and sayac):
            messagebox.showerror("Hata", "Tüm alanlar doldurulmalı")
            return

        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO aboneler (ad_soyad, adres, sayac_no) VALUES (?, ?, ?)", (ad, adres, sayac))
                conn.commit()
            messagebox.showinfo("Başarı", "Abone eklendi.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Sayaç No zaten mevcut.")

    # -------------------------
    # Sayaç Okuma Arayüzü
    # -------------------------
    def okuma_gui(self):
        tk.Label(self.okuma_tab, text="Sayaç No").pack()
        self.okuma_sayac_entry = tk.Entry(self.okuma_tab)
        self.okuma_sayac_entry.pack()

        tk.Label(self.okuma_tab, text="Tarih (GG.AA.YYYY)").pack()
        self.tarih_entry = tk.Entry(self.okuma_tab)
        self.tarih_entry.pack()

        tk.Label(self.okuma_tab, text="Önceki Endeks").pack()
        self.onceki_entry = tk.Entry(self.okuma_tab)
        self.onceki_entry.pack()

        tk.Label(self.okuma_tab, text="Son Endeks").pack()
        self.son_entry = tk.Entry(self.okuma_tab)
        self.son_entry.pack()

        tk.Button(self.okuma_tab, text="Okuma Kaydet", command=self.okuma_kaydet).pack(pady=10)

    def okuma_kaydet(self):
        sayac = self.okuma_sayac_entry.get()
        tarih = self.tarih_entry.get()
        try:
            onceki = int(self.onceki_entry.get())
            son = int(self.son_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Endeksler sayı olmalı")
            return

        if son < onceki:
            messagebox.showerror("Hata", "Son endeks öncekinden küçük olamaz")
            return

        birim_fiyat = self.settings.get("birim_fiyat", 1.96)

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO okumalar (sayac_no, tarih, onceki_endeks, son_endeks, birim_fiyat) VALUES (?, ?, ?, ?, ?)",
                      (sayac, tarih, onceki, son, birim_fiyat))
            conn.commit()
        messagebox.showinfo("Başarı", "Okuma kaydedildi.")

    # -------------------------
    # Ayarlar Arayüzü
    # -------------------------
    def ayar_gui(self):
        tk.Label(self.ayar_tab, text="Birim Fiyat (TL/m3)").pack()
        self.birim_entry = tk.Entry(self.ayar_tab)
        self.birim_entry.insert(0, str(self.settings.get("birim_fiyat", 1.96)))
        self.birim_entry.pack()

        tk.Button(self.ayar_tab, text="Kaydet", command=self.birim_guncelle).pack(pady=10)

    def birim_guncelle(self):
        try:
            yeni_fiyat = float(self.birim_entry.get())
            save_settings(yeni_fiyat)
            self.settings["birim_fiyat"] = yeni_fiyat
            messagebox.showinfo("Kaydedildi", "Birim fiyat güncellendi.")
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir fiyat giriniz.")

# ------------------------------
# Uygulamayı Çalıştır
# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SuTakipApp(root)
    root.mainloop()
