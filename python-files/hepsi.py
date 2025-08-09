import tkinter as tk
from tkinter import ttk, messagebox

ARKA_PLAN = "#ADD8E6"
YAZI_RENK = "black"
FREKANS_RENK = "PURPLE"

def format_frekans(frekans):
    if frekans >= 1e6:
        return f"{frekans / 1e6:.3f} MHz"
    elif frekans >= 1e3:
        return f"{frekans / 1e3:.3f} kHz"
    else:
        return f"{frekans:.1f} Hz"

def hesapla():
    try:
        entegr = combo_entegre.get()
        Rt_text = entry_rt.get().strip()
        Ct_text = entry_ct.get().strip()
        Rd_kullan = False
        Rd = 0

        if Rt_text == "":
            tk.messagebox.showerror("Hata", "Lütfen Zamanlama Direnci Rt (kΩ) giriniz!")
            return
        if Ct_text == "":
            tk.messagebox.showerror("Hata", "Lütfen Zamanlama Kondansatörü Ct (nF) giriniz!")
            return

        Rt = float(Rt_text) * 1e3  # kΩ -> Ω dönüşümü
        Ct = float(Ct_text) * 1e-9  # nF -> F

        if entegr in ["SG3525", "TL494"]:
            Rd_kullan = rd_var.get()
            if Rd_kullan:
                Rd_text = entry_rd.get().strip()
                if Rd_text == "":
                    tk.messagebox.showerror("Hata", "Lütfen Ölü Zaman Direnci Rd (Ω) giriniz!")
                    return
                Rd = float(Rd_text)
            else:
                Rd = 0

        if entegr == "SG3525":
            if not (2000 <= Rt <= 150_000):
                tk.messagebox.showerror("Hata", "SG3525 için Rt 2 kΩ ile 150 kΩ arasında olmalıdır!")
                return
            if not (1e-9 <= Ct <= 200e-9):
                tk.messagebox.showerror("Hata", "SG3525 için Ct 0.001 µF (1 nF) ile 0.2 µF (200 nF) arasında olmalıdır!")
                return
            if Rd_kullan and not (0 <= Rd <= 500):
                tk.messagebox.showerror("Hata", "SG3525 için Rd 0 ile 500 Ω arasında olmalıdır!")
                return

            if Rd_kullan:
                f = 1 / ((0.7 * Rt + 3 * Rd) * Ct)
            else:
                f = 1 / ((0.7 * Rt) * Ct)

            if not (100 <= f <= 400_000):
                tk.messagebox.showerror("Hata", "SG3525 için frekans 0.1 kHz ile 400 kHz arasında olmalıdır!")
                return

        elif entegr == "UC384x":
            if not (5e3 <= Rt <= 100e3):
                tk.messagebox.showerror("Hata", "UC384x için Rt 5 kΩ ile 100 kΩ arasında olmalıdır!")
                return
            if not (0.47e-9 <= Ct <= 4.7e-9):
                tk.messagebox.showerror("Hata", "UC384x için Ct 0.47 nF ile 4.7 nF arasında olmalıdır!")
                return

            f = 1 / (0.693 * Rt * Ct)

        elif entegr == "TL494":
            f = 1 / (Rt * Ct)

        else:
            f = 0

        f_pwm = f / 2  # PWM çıkış frekansı

        sonuc_label_osc.config(
            text=f"Osilatör Frekansı: {format_frekans(f)}",
            foreground=FREKANS_RENK
        )
        sonuc_label_pwm.config(
            text=f"PWM Çıkış Frekansı: {format_frekans(f_pwm)}",
            foreground=FREKANS_RENK
        )

        # E12 öneri hesaplama
        e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
        Rt_list = []
        Ct_list = []
        for mult in [1e2, 1e3, 1e4, 1e5, 1e6]:
            for val in e12:
                val_real = val * mult
                if 100 <= val_real <= 1e6:
                    Rt_list.append(val_real)
        for mult in [1e-10, 1e-9, 1e-8, 1e-7, 1e-6]:
            for val in e12:
                val_real = val * mult
                if 100e-12 <= val_real <= 1e-6:
                    Ct_list.append(val_real)

        hedef_f = f_pwm  # PWM frekansına göre öneri

        en_yakin = None
        min_fark = float("inf")
        for rt_val in Rt_list:
            for ct_val in Ct_list:
                if entegr == "SG3525":
                    if Rd_kullan:
                        freq = 1 / ((0.7 * rt_val + 3 * Rd) * ct_val)
                    else:
                        freq = 1 / ((0.7 * rt_val) * ct_val)
                elif entegr == "UC384x":
                    freq = 1 / (0.693 * rt_val * ct_val)
                elif entegr == "TL494":
                    freq = 1 / (rt_val * ct_val)
                else:
                    freq = 0
                freq_pwm = freq / 2
                fark = abs(freq_pwm - hedef_f)
                if fark < min_fark:
                    min_fark = fark
                    en_yakin = (rt_val, ct_val, freq)

        if en_yakin:
            öneri_rt, öneri_ct, öneri_f = en_yakin
            öneri_rt_kohm = öneri_rt / 1e3
            ayni_mi = (abs(öneri_rt - Rt) < 1) and (abs(öneri_ct - Ct) < 1e-10)

            if ayni_mi:
                öneri_label.config(text="PWM Frekans Önerisi: Mevcut değerleriniz uygundur.", foreground=YAZI_RENK)
            else:
                öneri_label.config(
                    text=f"PWM Frekans Önerisi: Rt={öneri_rt_kohm:.2f} kΩ, Ct={öneri_ct*1e9:.2f} nF → {format_frekans(öneri_f / 2)}",
                    foreground=YAZI_RENK
                )

    except ValueError:
        tk.messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler giriniz!")

def rd_secildi():
    if rd_var.get():
        entry_rd.config(state="normal")
    else:
        entry_rd.config(state="disabled")
        entry_rd.delete(0, tk.END)

def entegre_degisti(event=None):
    secilen = combo_entegre.get()
    if secilen == "UC384x":
        chk_rd.grid_remove()
        label_rd.grid_remove()
        entry_rd.grid_remove()
    else:
        chk_rd.grid()
        label_rd.grid()
        entry_rd.grid()
    rd_secildi()
    sonuc_label_osc.config(text="Osilatör Frekansı: ")
    sonuc_label_pwm.config(text="PWM Çıkış Frekansı: ")
    öneri_label.config(text="PWM Frekans Önerisi:")  # Burada açılışta yazacak

root = tk.Tk()
root.iconbitmap(r"DEF.ico")
root.title("PWM Frekans Hesaplayıcı")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg=ARKA_PLAN)


tk.Label(root, text="Entegre Seçin:", bg=ARKA_PLAN, fg=YAZI_RENK).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
combo_entegre = ttk.Combobox(root, values=["SG3525", "UC384x", "TL494"], width=15)
combo_entegre.current(0)
combo_entegre.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")
combo_entegre.bind("<<ComboboxSelected>>", entegre_degisti)

tk.Label(root, text="Zamanlama Direnci Rt (kΩ):", bg=ARKA_PLAN, fg=YAZI_RENK).grid(row=2, column=0, sticky="w", padx=10, pady=2)
entry_rt = ttk.Entry(root, width=20)
entry_rt.grid(row=3, column=0, padx=10, pady=(0,10), sticky="w")

tk.Label(root, text="Zamanlama Kondansatörü Ct (nF):", bg=ARKA_PLAN, fg=YAZI_RENK).grid(row=4, column=0, sticky="w", padx=10, pady=2)
entry_ct = ttk.Entry(root, width=20)
entry_ct.grid(row=5, column=0, padx=10, pady=(0,10), sticky="w")

rd_var = tk.BooleanVar(value=False)
chk_rd = tk.Checkbutton(root, text="Ölü Zaman Direnci Rd kullan", variable=rd_var, bg=ARKA_PLAN, fg=YAZI_RENK, command=rd_secildi)
chk_rd.grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))

label_rd = tk.Label(root, text="Ölü Zaman Direnci Rd (Ω):", bg=ARKA_PLAN, fg=YAZI_RENK)
label_rd.grid(row=7, column=0, sticky="w", padx=10, pady=2)
entry_rd = ttk.Entry(root, width=20, state="disabled")
entry_rd.grid(row=8, column=0, padx=10, pady=(0,10), sticky="w")

btn_hesapla = ttk.Button(root, text="Frekansı Hesapla", command=hesapla)
btn_hesapla.grid(row=9, column=0, pady=10, padx=10, sticky="w")

sonuc_label_osc = tk.Label(root, text="Osilatör Frekansı: ", bg=ARKA_PLAN, fg=FREKANS_RENK, font=("Arial", 14, "bold"))
sonuc_label_osc.grid(row=10, column=0, pady=5, padx=10, sticky="w")

sonuc_label_pwm = tk.Label(root, text="PWM Çıkış Frekansı: ", bg=ARKA_PLAN, fg=FREKANS_RENK, font=("Arial", 14, "bold"))
sonuc_label_pwm.grid(row=11, column=0, pady=5, padx=10, sticky="w")

öneri_label = tk.Label(root, text="PWM Frekans Önerisi:", bg=ARKA_PLAN, fg=YAZI_RENK, font=("Arial", 12))
öneri_label.grid(row=12, column=0, pady=(5, 5), padx=10, sticky="w")

tk.Label(root, text="HSE OTOMASYON AR-GE TEKNİK", bg=ARKA_PLAN, fg="blue").place(x=155, y=450)
tk.Label(root, text="*HÜSEYİN SİNAN EMİN tarafından yapılmıştır.*", bg=ARKA_PLAN, fg="blue").place(x=120, y=480)

entegre_degisti()
root.mainloop()
