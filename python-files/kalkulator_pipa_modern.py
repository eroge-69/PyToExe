Python 3.13.6 (tags/v3.13.6:4e66535, Aug  6 2025, 14:36:00) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import messagebox
import math

def hitung_berat_pipa():
    try:
        diameter_luar_mm = float(entry_diameter.get())
        tebal_mm = float(entry_tebal.get())
        panjang_m = float(entry_panjang.get())
        densitas = float(entry_densitas.get())  # kg/m³

        diameter_luar_m = diameter_luar_mm / 1000
        tebal_m = tebal_mm / 1000
        diameter_dalam_m = diameter_luar_m - (2 * tebal_m)
... 
...         if diameter_dalam_m <= 0:
...             messagebox.showerror("Error", "Tebal pipa terlalu besar dibanding diameter!")
...             return
... 
...         volume = (math.pi / 4) * (diameter_luar_m**2 - diameter_dalam_m**2) * panjang_m
...         berat = volume * densitas
... 
...         messagebox.showinfo("Hasil", f"Berat pipa: {berat:.2f} kg")
...     except ValueError:
...         messagebox.showerror("Error", "Masukkan angka yang benar!")
... 
... # GUI
... root = tk.Tk()
... root.title("Kalkulator Berat Pipa")
... root.geometry("300x250")
... 
... tk.Label(root, text="Diameter Luar (mm):").pack()
... entry_diameter = tk.Entry(root)
... entry_diameter.pack()
... 
... tk.Label(root, text="Tebal Pipa (mm):").pack()
... entry_tebal = tk.Entry(root)
... entry_tebal.pack()
... 
... tk.Label(root, text="Panjang Pipa (m):").pack()
... entry_panjang = tk.Entry(root)
... entry_panjang.pack()
... 
... tk.Label(root, text="Densitas (kg/m³):").pack()
... entry_densitas = tk.Entry(root)
... entry_densitas.insert(0, "7850")  # default untuk baja
... entry_densitas.pack()
... 
... tk.Button(root, text="Hitung Berat", command=hitung_berat_pipa).pack(pady=10)
... 
... root.mainloop()
