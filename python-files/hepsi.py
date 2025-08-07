import tkinter as tk
from tkinter import ttk, messagebox

def hesapla():
    try:
        rt = float(entry_rt.get())        # ohm
        ct = float(entry_ct.get()) * 1e-9 # nF -> F

        secilen = entegre_secim.get()

        if secilen == "SG3525":
            frekans = 1 / (rt * ct)
        elif secilen == "UC384x":
            frekans = 1.72 / (rt * ct)
        elif secilen == "TL494":
            frekans = 1.1 / (rt * ct)
        else:
            messagebox.showerror("Hata", "Entegre seçilmedi.")
            return

        label_sonuc.config(text=f"Frekans: {frekans:.1f} Hz")

    except ValueError:
        messagebox.showerror("Hata", "Geçerli sayısal değerler giriniz.")

# Ana pencere
pencere = tk.Tk()
pencere.title("PWM Frekans Hesaplayıcı")
pencere.geometry("320x260")

# Entegre seçimi
tk.Label(pencere, text="Entegre Seçin:").pack(pady=5)
entegre_secim = ttk.Combobox(pencere, values=["SG3525", "UC384x", "TL494"])
entegre_secim.current(0)
entegre_secim.pack()

# Rt girişi
tk.Label(pencere, text="Rt (ohm):").pack()
entry_rt = tk.Entry(pencere)
entry_rt.pack()

# Ct girişi
tk.Label(pencere, text="Ct (nF):").pack()
entry_ct = tk.Entry(pencere)
entry_ct.pack()

# Hesapla butonu
tk.Button(pencere, text="Frekansı Hesapla", command=hesapla).pack(pady=10)

# Sonuç etiketi
label_sonuc = tk.Label(pencere, text="Frekans: ")
label_sonuc.pack()

# Çalıştır
pencere.mainloop()