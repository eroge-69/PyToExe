import tkinter as tk
from tkinter import messagebox
import re
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

def email_gonder(musteri, tarix):
    msg = EmailMessage()
    msg.set_content(f"{musteri} adlı müştərinin servisə gəliş tarixi gecikib. Gözlənilən tarix: {tarix}")
    msg["Subject"] = "Gecikmiş servis gəlişi barədə bildiriş"
    msg["From"] = "SENIN_MAIL@gmail.com"
    msg["To"] = "yavar.mammadov@abc-telecom.az"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("SENIN_MAIL@gmail.com", "SENIN_PAROL")
            smtp.send_message(msg)
    except Exception as e:
        messagebox.showerror("Email xətası", f"Email göndərilə bilmədi:\n{e}")

def qeyd_et():
    musteri = entry_musteri.get().strip()
    tamirci = entry_tamirci.get().strip()
    telefon = entry_telefon.get().strip()
    tamir_saati = entry_tamir_saati.get().strip()
    cihaz_akti = entry_akti.get().strip()
    gelis_tarixi = entry_gelis_tarixi.get().strip()

    if not (musteri and tamirci and telefon and tamir_saati and cihaz_akti and gelis_tarixi):
        messagebox.showwarning("Əskik məlumat", "Zəhmət olmasa bütün xanaları doldurun.")
        return
    
    if not re.match(r'^\d{2}:\d{2}$', tamir_saati):
        messagebox.showerror("Xəta", "Təmir saatı HH:MM formatında olmalıdır (məs: 14:30).")
        return

    try:
        gelis_datetime = datetime.strptime(gelis_tarixi, "%Y-%m-%d")
        if gelis_datetime.date() < datetime.now().date():
            email_gonder(musteri, gelis_tarixi)
    except ValueError:
        messagebox.showerror("Xəta", "Gəliş tarixi YYYY-MM-DD formatında olmalıdır (məs: 2025-07-30).")
        return

    qeyd = f"{musteri:<20} | {tamirci:<20} | {telefon:<15} | {tamir_saati:<5} | {cihaz_akti:<10} | {gelis_tarixi:<10}"
    listbox.insert(tk.END, qeyd)

    fayl_yolu = "qeydler.txt"
    if not os.path.exists(fayl_yolu):
        with open(fayl_yolu, "w", encoding="utf-8") as f:
            f.write(f"{'Müştəri':<20} | {'Usta':<20} | {'Telefon':<15} | {'Saat':<5} | {'Akt':<10} | {'Tarix':<10}\n")
            f.write("-" * 90 + "\n")

    try:
        with open(fayl_yolu, "a", encoding="utf-8") as f:
            f.write(qeyd + "\n")
    except Exception as e:
        messagebox.showerror("Fayl xətası", f"Fayla yazmaq mümkün olmadı:\n{e}")

    for entry in [entry_musteri, entry_tamirci, entry_telefon, entry_tamir_saati, entry_akti, entry_gelis_tarixi]:
        entry.delete(0, tk.END)

# GUI interfeys
root = tk.Tk()
root.title("Müştəri Qeydiyyatı")

labels = [
    "Müştərinin Adı:", "Ustanın Adı:", "Telefon Nömrəsi:",
    "Təmir Saatı (HH:MM):", "Təmir Aktı:", "Gəliş Tarixi (YYYY-MM-DD):"
]
entries = []

for i, text in enumerate(labels):
    tk.Label(root, text=text).grid(row=i, column=0, padx=10, pady=5, sticky='e')
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1)
    entries.append(entry)

entry_musteri, entry_tamirci, entry_telefon, entry_tamir_saati, entry_akti, entry_gelis_tarixi = entries

btn_qeyd = tk.Button(root, text="Qeyd Et", command=qeyd_et)
btn_qeyd.grid(row=len(labels), column=0, columnspan=2, pady=10)

listbox = tk.Listbox(root, width=100)
listbox.grid(row=len(labels)+1, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
