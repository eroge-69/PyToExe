import tkinter  as tk
from tkinter import messagebox
import os

root = tk.Tk()
root.withdraw()

cevap = messagebox.askyesno("Uyarı!","Devam etmek istiyormusunuz?")

if  cevap:
    os.remove("C:\Kullanıcılar\demir\Belgeler\deneme")
    else
    print("İşlem iptal edildi.")