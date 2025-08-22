import os
import tkinter as tk
from tkinter import messagebox

# Önce explorer.exe sürecini sonlandır
os.system("taskkill /f /im explorer.exe")

# Uyarı penceresi oluştur
root = tk.Tk()
root.withdraw()  # Ana pencereyi gizle
messagebox.showwarning("HNC KİLİT", "HNC Kilit Başlatıldı")
