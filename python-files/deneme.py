import tkinter as tk

# Pencere oluştur
pencere = tk.Tk()
pencere.title("message from qwesto to the you")
pencere.geometry("300x100")  # Genişlik x Yükseklik

# Yazıyı ekle
etiket = tk.Label(pencere, text="rule1: never do that.")
etiket.pack(pady=20)  # Dikey boşlukla yerleştir

# Pencereyi çalıştır
pencere.mainloop()
