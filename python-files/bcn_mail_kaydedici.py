import os
import win32com.client
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

def kaydet():
    bcn_numara = bcn_entry.get().strip()
    if not bcn_numara:
        messagebox.showerror("Hata", "Lütfen BÇN numarasını girin!")
        return

    # Masaüstü yolu
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    numaralar_folder = os.path.join(desktop_path, "Numaralar")
    if not os.path.exists(numaralar_folder):
        os.makedirs(numaralar_folder)

    bcn_folder = os.path.join(numaralar_folder, bcn_numara)
    if not os.path.exists(bcn_folder):
        os.makedirs(bcn_folder)

    # Outlook ile bağlantı
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        sent_items = outlook.GetDefaultFolder(5)  # Gönderilenler klasörü
    except Exception as e:
        messagebox.showerror("Hata", f"Outlook'a bağlanılamadı: {e}")
        return

    kaydedilen_sayisi = 0
    for mail in sent_items.Items:
        try:
            if bcn_numara in str(mail.Subject) or bcn_numara in str(mail.Body):
                mail_date = mail.SentOn.strftime("%Y%m%d_%H%M%S")
                mail_subject = "".join(x for x in mail.Subject if x.isalnum() or x in " _-")[:50]
                mail_file = os.path.join(bcn_folder, f"{mail_date}_{mail_subject}.msg")
                mail.SaveAs(mail_file)
                kaydedilen_sayisi += 1
        except:
            continue

    messagebox.showinfo("Tamamlandı", f"{kaydedilen_sayisi} mail {bcn_folder} klasörüne kaydedildi.")

# GUI oluşturma
root = tk.Tk()
root.title("BÇN Mail Kaydedici")
root.geometry("400x150")

tk.Label(root, text="BÇN Numarası:").pack(pady=10)
bcn_entry = tk.Entry(root, width=30)
bcn_entry.pack()

tk.Button(root, text="Mailleri Kaydet", command=kaydet).pack(pady=20)

root.mainloop()
