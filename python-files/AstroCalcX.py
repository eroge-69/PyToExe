import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Entry, Button, Label, Frame
import math, csv
import matplotlib.pyplot as plt
from datetime import datetime

# Sabitler
G = 6.67430e-11
sigma = 5.670374419e-8
c = 3e8
H0 = 70 * 1000 / (3.086e22)  # s^-1

# Tema: darkly / vapor / cyborg / solar / morph / journal / flatly
style = Style(theme="vapor")
root = style.master
root.title("AstroCalcX")
root.geometry("800x600")

frame = Frame(root, padding=20)
frame.pack(fill="both", expand=True)

def temizle():
    for widget in frame.winfo_children():
        widget.destroy()

def geri_butonu():
    Button(frame, text="← Geri", bootstyle="danger-outline", command=ana_menu).place(x=10, y=10)

def ana_menu():
    temizle()
    Label(frame, text="AstroCalcX - Astrofizik Hesaplayıcı", font=("Helvetica", 24)).pack(pady=30)

    menu_frame = Frame(frame)
    menu_frame.pack()

    for isim, fonksiyon in [
        ("Newton", newton),
        ("Stefan-Boltzmann", stefan),
        ("Hubble", hubble),
        ("Doppler", doppler),
        ("Kayıtlar", kayitlar)
    ]:
        Button(menu_frame, text=isim, bootstyle="info", width=20, command=fonksiyon).pack(pady=10, padx=10)

def kaydet(isim, sonuc):
    with open("veriler.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([isim, sonuc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def newton():
    temizle()
    geri_butonu()
    Label(frame, text="Newton Evrensel Çekim Kuvveti", font=("Helvetica", 18)).pack(pady=20)

    m1 = input_field("Kütle 1 (kg)")
    m2 = input_field("Kütle 2 (kg)")
    r = input_field("Mesafe (m)")

    def hesapla():
        try:
            F = G * float(m1.get()) * float(m2.get()) / float(r.get())**2
            kaydet("Newton", f"{F:.2e} N")
            popup("Çekim Kuvveti", f"{F:.2e} N")
        except:
            popup("Hata", "Lütfen geçerli değerler girin")

    Button(frame, text="Hesapla", bootstyle="success", command=hesapla).pack(pady=10)

def stefan():
    temizle()
    geri_butonu()
    Label(frame, text="Stefan-Boltzmann Yasası", font=("Helvetica", 18)).pack(pady=20)

    r = input_field("Yarıçap (m)")
    t = input_field("Sıcaklık (K)")

    def hesapla():
        try:
            L = 4 * math.pi * float(r.get())**2 * sigma * float(t.get())**4
            kaydet("Stefan-Boltzmann", f"{L:.2e} W")
            popup("Işıma Gücü", f"{L:.2e} W")
        except:
            popup("Hata", "Lütfen geçerli değerler girin")

    def grafik():
        try:
            T_vals = list(range(1000, 10001, 500))
            R_val = float(r.get())
            L_vals = [4 * math.pi * R_val**2 * sigma * T**4 for T in T_vals]
            plt.plot(T_vals, L_vals, color="orange")
            plt.title("Sıcaklık vs Işıma Gücü")
            plt.xlabel("Sıcaklık (K)")
            plt.ylabel("Işıma Gücü (W)")
            plt.grid(True)
            plt.show()
        except:
            popup("Hata", "Geçerli yarıçap giriniz")

    Button(frame, text="Hesapla", bootstyle="success", command=hesapla).pack(pady=5)
    Button(frame, text="📈 Grafik Göster", bootstyle="warning", command=grafik).pack(pady=5)

def hubble():
    temizle()
    geri_butonu()
    Label(frame, text="Hubble Yasası", font=("Helvetica", 18)).pack(pady=20)

    d = input_field("Uzaklık (Mpc)")

    def hesapla():
        try:
            v = H0 * float(d.get()) * 3.086e22
            kaydet("Hubble", f"{v:.2e} m/s")
            popup("Uzaklaşma Hızı", f"{v:.2e} m/s")
        except:
            popup("Hata", "Geçerli giriş yap")

    Button(frame, text="Hesapla", bootstyle="success", command=hesapla).pack(pady=10)

def doppler():
    temizle()
    geri_butonu()
    Label(frame, text="Doppler Kayması", font=("Helvetica", 18)).pack(pady=20)

    obs = input_field("Gözlenen λ (nm)")
    rest = input_field("Gerçek λ (nm)")

    def hesapla():
        try:
            z = (float(obs.get()) - float(rest.get())) / float(rest.get())
            v = z * c
            kaydet("Doppler", f"z={z:.4f}, v={v:.2e} m/s")
            popup("Doppler Sonucu", f"z: {z:.4f}\nHız: {v:.2e} m/s")
        except:
            popup("Hata", "Geçerli sayılar girin")

    Button(frame, text="Hesapla", bootstyle="success", command=hesapla).pack(pady=10)

def kayitlar():
    temizle()
    geri_butonu()
    Label(frame, text="Geçmiş Hesaplamalar", font=("Helvetica", 18)).pack(pady=20)
    try:
        with open("veriler.csv", "r", encoding="utf-8") as f:
            data = f.read()
        box = tk.Text(frame, height=20, width=80, bg="#222", fg="#0f0")
        box.insert("1.0", data)
        box.pack()
    except:
        Label(frame, text="Henüz veri kaydı yok.").pack()

def input_field(label):
    Label(frame, text=label, font=("Helvetica", 12)).pack(pady=5)
    entry = Entry(frame, width=25, font=("Helvetica", 12))
    entry.pack(pady=2)
    return entry

def popup(baslik, mesaj):
    p = tk.Toplevel(root)
    p.title(baslik)
    Label(p, text=mesaj, font=("Helvetica", 14)).pack(padx=20, pady=20)
    Button(p, text="Tamam", bootstyle="success", command=p.destroy).pack(pady=10)

ana_menu()
root.mainloop()