
import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
import os
from datetime import datetime

# Kayıtları tutmak için liste
kayitlar = []

# PDF oluşturma fonksiyonu
def pdf_olustur(kayit):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="UYSAL SERVİS FORMU", ln=True, align="C")
    pdf.ln(10)

    for key, value in kayit.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    # PDF dosya adı
    filename = f"ServisFormu_{kayit['Ad Soyad']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    messagebox.showinfo("Başarılı", f"PDF oluşturuldu: {filename}")

# Kayıt işlemi
def kaydet():
    kayit = {
        "Ad Soyad": ad_entry.get(),
        "Firma": firma_entry.get(),
        "Telefon": telefon_entry.get(),
        "Adres": adres_entry.get(),
        "Arıza": ariza_entry.get("1.0", tk.END).strip()
    }

    if not kayit["Ad Soyad"] or not kayit["Telefon"]:
        messagebox.showerror("Hata", "Ad Soyad ve Telefon zorunludur.")
        return

    kayitlar.append(kayit)
    liste.insert(tk.END, f"{kayit['Ad Soyad']} - {kayit['Telefon']}")
    pdf_olustur(kayit)

# GUI oluştur
pencere = tk.Tk()
pencere.title("UysalServis")
pencere.geometry("500x600")

# Logo ekleme (opsiyonel)
if os.path.exists("logo.png"):
    logo = tk.PhotoImage(file="logo.png")
    tk.Label(pencere, image=logo).pack()

tk.Label(pencere, text="Ad Soyad").pack()
ad_entry = tk.Entry(pencere, width=50)
ad_entry.pack()

tk.Label(pencere, text="Firma").pack()
firma_entry = tk.Entry(pencere, width=50)
firma_entry.pack()

tk.Label(pencere, text="Telefon").pack()
telefon_entry = tk.Entry(pencere, width=50)
telefon_entry.pack()

tk.Label(pencere, text="Adres").pack()
adres_entry = tk.Entry(pencere, width=50)
adres_entry.pack()

tk.Label(pencere, text="Arıza Açıklaması").pack()
ariza_entry = tk.Text(pencere, width=50, height=5)
ariza_entry.pack()

tk.Button(pencere, text="Kaydet ve PDF Oluştur", command=kaydet, bg="#4CAF50", fg="white").pack(pady=10)

tk.Label(pencere, text="Kayıtlar").pack()
liste = tk.Listbox(pencere, width=60)
liste.pack(pady=10)

pencere.mainloop()
