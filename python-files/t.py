import json import os import tkinter as tk from tkinter import ttk, messagebox import ttkbootstrap as tb from datetime import datetime

Dosya yolları

HASTA_DOSYASI = "hastalar.json" DOKTOR_DOSYASI = "doktorlar.json" RANDEVU_DOSYASI = "randevular.json" POLIKLINIK_DOSYASI = "poliklinikler.json" RECETE_DOSYASI = "receteler.json"

JSON Kontrol

for dosya in [HASTA_DOSYASI, DOKTOR_DOSYASI, RANDEVU_DOSYASI, POLIKLINIK_DOSYASI, RECETE_DOSYASI]: if not os.path.exists(dosya): with open(dosya, "w") as f: json.dump([], f)

def json_oku(dosya): with open(dosya, "r") as f: return json.load(f)

def json_yaz(dosya, veri): with open(dosya, "w") as f: json.dump(veri, f, indent=4)

Ekleme Fonksiyonları

def hasta_ekle(entryler, liste): ad = entryler["Ad"].get() soyad = entryler["Soyad"].get() tc = entryler["TC"].get() yas = entryler["Yaş"].get() tel = entryler["Telefon"].get()

if not ad or not tc: messagebox.showerror("Hata", "Ad ve TC zorunludur!") return hastalar = json_oku(HASTA_DOSYASI) hastalar.append({"ad": ad, "soyad": soyad, "tc": tc, "yas": yas, "tel": tel}) json_yaz(HASTA_DOSYASI, hastalar) messagebox.showinfo("Başarılı", "Hasta kaydedildi.") liste_guncelle(liste, HASTA_DOSYASI) 

def doktor_ekle(entryler, liste): ad = entryler["Ad"].get() soyad = entryler["Soyad"].get() uzmanlik = entryler["Uzmanlık"].get()

if not ad or not uzmanlik: messagebox.showerror("Hata", "Ad ve Uzmanlık zorunludur!") return doktorlar = json_oku(DOKTOR_DOSYASI) doktorlar.append({"ad": ad, "soyad": soyad, "uzmanlik": uzmanlik}) json_yaz(DOKTOR_DOSYASI, doktorlar) messagebox.showinfo("Başarılı", "Doktor kaydedildi.") liste_guncelle(liste, DOKTOR_DOSYASI) 

def randevu_ekle(entryler, liste): tc = entryler["Hasta TC"].get() doktor = entryler["Doktor Adı"].get() tarih = entryler["Tarih"].get() saat = entryler["Saat"].get()

randevular = json_oku(RANDEVU_DOSYASI) randevular.append({"tc": tc, "doktor": doktor, "tarih": tarih, "saat": saat}) json_yaz(RANDEVU_DOSYASI, randevular) messagebox.showinfo("Başarılı", "Randevu eklendi.") liste_guncelle(liste, RANDEVU_DOSYASI) 

def poliklinik_ekle(entryler, liste): ad = entryler["Ad"].get() kat = entryler["Kat"].get() poliklinikler = json_oku(POLIKLINIK_DOSYASI) poliklinikler.append({"ad": ad, "kat": kat}) json_yaz(POLIKLINIK_DOSYASI, poliklinikler) messagebox.showinfo("Başarılı", "Poliklinik eklendi.") liste_guncelle(liste, POLIKLINIK_DOSYASI)

def recete_ekle(entryler, liste): tc = entryler["Hasta TC"].get() doktor = entryler["Doktor Adı"].get() ilaclar = entryler["İlaçlar"].get() tarih = datetime.now().strftime("%d.%m.%Y %H:%M") receteler = json_oku(RECETE_DOSYASI) receteler.append({"tc": tc, "doktor": doktor, "ilaclar": ilaclar.split(","), "tarih": tarih}) json_yaz(RECETE_DOSYASI, receteler) messagebox.showinfo("Başarılı", "Reçete kaydedildi.") liste_guncelle(liste, RECETE_DOSYASI)

def liste_guncelle(tree, dosya): tree.delete(*tree.get_children()) veriler = json_oku(dosya) for v in veriler: tree.insert("", "end", values=list(v.values()))

Arayüz

app = tb.Window(themename="darkly") app.title("🏥 Hastane Otomasyon Sistemi") app.geometry("1000x600")

notebook = ttk.Notebook(app) notebook.pack(fill="both", expand=True)

def sekme_olustur(baslik, alanlar, ekle_func, dosya): frame = ttk.Frame(notebook) notebook.add(frame, text=baslik) entryler = {}

for i, alan in enumerate(alanlar): ttk.Label(frame, text=alan).grid(row=i, column=0, padx=5, pady=5, sticky="e") entry = ttk.Entry(frame, width=30) entry.grid(row=i, column=1, padx=5, pady=5) entryler[alan] = entry liste = ttk.Treeview(frame, columns=alanlar, show="headings") for col in alanlar: liste.heading(col, text=col) liste.column(col, width=150) liste.grid(row=0, column=3, rowspan=len(alanlar)+1, padx=20, pady=5) btn = tb.Button(frame, text="Ekle", bootstyle="success", command=lambda: ekle_func(entryler, liste)) btn.grid(row=len(alanlar), column=0, columnspan=2, pady=10) liste_guncelle(liste, dosya) 

Sekmeler

sekme_olustur("👤 Hastalar", ["Ad", "Soyad", "TC", "Yaş", "Telefon"], hasta_ekle, HASTA_DOSYASI) sekme_olustur("🩺 Doktorlar", ["Ad", "Soyad", "Uzmanlık"], doktor_ekle, DOKTOR_DOSYASI) sekme_olustur("📅 Randevular", ["Hasta TC", "Doktor Adı", "Tarih", "Saat"], randevu_ekle, RANDEVU_DOSYASI) sekme_olustur("🏢 Poliklinikler", ["Ad", "Kat"], poliklinik_ekle, POLIKLINIK_DOSYASI) sekme_olustur("💊 Reçeteler", ["Hasta TC", "Doktor Adı", "İlaçlar"], recete_ekle, RECETE_DOSYASI)

app.mainloop()

