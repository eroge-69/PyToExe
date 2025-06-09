import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

# Malzeme gereksinimleri
YELEK_GEREKSINIM = {"Karton": 40, "Kumaş": 50}
AGIR_PLAKA_GEREKSINIM = {
    "Metal hurda": 28,
    "Plastik": 20,
    "Alüminyum tozu": 60,
    "Çelik": 45
}

def hesapla():
    try:
        # Kullanıcı girdilerini al
        malzemeler = {
            "Karton": int(karton_entry.get() or 0),
            "Kumaş": int(kumas_entry.get() or 0),
            "Metal hurda": int(metal_entry.get() or 0),
            "Plastik": int(plastik_entry.get() or 0),
            "Alüminyum tozu": int(aluminyum_entry.get() or 0),
            "Çelik": int(celik_entry.get() or 0)
        }

        # Yelek hesapla
        yelek_sayisi = min(
            malzemeler["Karton"] // YELEK_GEREKSINIM["Karton"],
            malzemeler["Kumaş"] // YELEK_GEREKSINIM["Kumaş"]
        )

        # Ağır plaka hesapla
        agir_plaka_sayisi = min(
            malzemeler["Metal hurda"] // AGIR_PLAKA_GEREKSINIM["Metal hurda"],
            malzemeler["Plastik"] // AGIR_PLAKA_GEREKSINIM["Plastik"],
            malzemeler["Alüminyum tozu"] // AGIR_PLAKA_GEREKSINIM["Alüminyum tozu"],
            malzemeler["Çelik"] // AGIR_PLAKA_GEREKSINIM["Çelik"]
        )

        # Kalan malzemeler
        kalan_malzemeler = {
            "Karton": malzemeler["Karton"] - yelek_sayisi * YELEK_GEREKSINIM["Karton"],
            "Kumaş": malzemeler["Kumaş"] - yelek_sayisi * YELEK_GEREKSINIM["Kumaş"],
            "Metal hurda": malzemeler["Metal hurda"] - agir_plaka_sayisi * AGIR_PLAKA_GEREKSINIM["Metal hurda"],
            "Plastik": malzemeler["Plastik"] - agir_plaka_sayisi * AGIR_PLAKA_GEREKSINIM["Plastik"],
            "Alüminyum tozu": malzemeler["Alüminyum tozu"] - agir_plaka_sayisi * AGIR_PLAKA_GEREKSINIM["Alüminyum tozu"],
            "Çelik": malzemeler["Çelik"] - agir_plaka_sayisi * AGIR_PLAKA_GEREKSINIM["Çelik"]
        }

        # Sonuçları yazdır
        sonuc_text.config(state=tk.NORMAL)
        sonuc_text.delete(1.0, tk.END)

        sonuc_text.insert(tk.END, f"🔧 Üretim Sonuçları\n\n")

        sonuc_text.insert(tk.END, f"🦺 Yelek:\n")
        sonuc_text.insert(tk.END, f"• Üretilebilecek: {yelek_sayisi} adet\n")
        sonuc_text.insert(tk.END, f"• Kalan Karton: {kalan_malzemeler['Karton']}\n")
        sonuc_text.insert(tk.END, f"• Kalan Kumaş: {kalan_malzemeler['Kumaş']}\n\n")

        sonuc_text.insert(tk.END, f"🪖 Ağır Plaka:\n")
        sonuc_text.insert(tk.END, f"• Üretilebilecek: {agir_plaka_sayisi} adet\n")
        sonuc_text.insert(tk.END, f"• Kalan Metal hurda: {kalan_malzemeler['Metal hurda']}\n")
        sonuc_text.insert(tk.END, f"• Kalan Plastik: {kalan_malzemeler['Plastik']}\n")
        sonuc_text.insert(tk.END, f"• Kalan Alüminyum tozu: {kalan_malzemeler['Alüminyum tozu']}\n")
        sonuc_text.insert(tk.END, f"• Kalan Çelik: {kalan_malzemeler['Çelik']}\n")

        sonuc_text.config(state=tk.DISABLED)

    except ValueError:
        messagebox.showerror("Hata", "Lütfen tüm alanlara geçerli sayısal değerler giriniz.")

# Arayüz
root = tk.Tk()
root.title("ZIRHMATIK PRO - Malzeme Hesaplayıcı")
root.geometry("700x650")
root.configure(bg="#f5f6fa")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#f5f6fa", font=("Arial", 10))
style.configure("TButton", font=("Arial", 11, "bold"), background="#3498db", foreground="white")

baslik_font = Font(family="Arial", size=18, weight="bold")
ttk.Label(root, text="ZIRHMATIK PRO", font=baslik_font, foreground="#2c3e50").pack(pady=(15, 10))

ttk.Label(root, text="Malzeme miktarlarını girerek üretilebilecek eşyaları hesaplayın", 
          wraplength=500, justify="center", foreground="#7f8c8d").pack(pady=(0, 15))

# Giriş çerçevesi
giris_frame = ttk.LabelFrame(root, text=" MALZEME GİRİŞİ ", padding=(15, 10))
giris_frame.pack(pady=10, padx=20, fill="x")

def etiket_yerleştir(text, row):
    ttk.Label(giris_frame, text=text).grid(row=row, column=0, sticky="e", padx=5, pady=5)

def kutu_yerleştir(entry_var, row):
    entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

etiket_yerleştir("Karton:", 0)
karton_entry = ttk.Entry(giris_frame)
kutu_yerleştir(karton_entry, 0)

etiket_yerleştir("Kumaş:", 1)
kumas_entry = ttk.Entry(giris_frame)
kutu_yerleştir(kumas_entry, 1)

etiket_yerleştir("Metal hurda:", 2)
metal_entry = ttk.Entry(giris_frame)
kutu_yerleştir(metal_entry, 2)

etiket_yerleştir("Plastik:", 3)
plastik_entry = ttk.Entry(giris_frame)
kutu_yerleştir(plastik_entry, 3)

etiket_yerleştir("Alüminyum tozu:", 4)
aluminyum_entry = ttk.Entry(giris_frame)
kutu_yerleştir(aluminyum_entry, 4)

etiket_yerleştir("Çelik:", 5)
celik_entry = ttk.Entry(giris_frame)
kutu_yerleştir(celik_entry, 5)

giris_frame.grid_columnconfigure(1, weight=1)

# Buton
ttk.Button(root, text="HESAPLA", command=hesapla).pack(pady=15, ipadx=20, ipady=8)

# Sonuç kutusu
sonuc_frame = ttk.LabelFrame(root, text=" SONUÇLAR ", padding=(15, 10))
sonuc_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)
sonuc_text = tk.Text(sonuc_frame, height=18, font=("Arial", 11), wrap="word", background="#ecf0f1", state=tk.DISABLED)
sonuc_text.pack(fill="both", expand=True)

root.mainloop()
