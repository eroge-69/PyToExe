import tkinter as tk
from tkinter import messagebox

def tamam_butonu_tiklandi():
    messagebox.showinfo("Bilgi", "Tamam butonuna tıkladınız!")

# Pencereyi oluştur
pencere = tk.Tk()
pencere.title("Basit Pencere")
pencere.geometry("300x150")  # Genişlik x Yükseklik

# Buton oluştur ve pencereye ekle
tamam_butonu = tk.Button(pencere, text="Tamam", command=tamam_butonu_tiklandi)
tamam_butonu.pack(pady=50)

# Ana döngüyü başlat
pencere.mainloop()
