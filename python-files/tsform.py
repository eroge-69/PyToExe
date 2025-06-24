import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import json
import shutil
import datetime

# === SABİT YOLLAR ===
RESIM_KLASORU = "yuklenen_resimler"
VERI_DOSYASI = "form_kayitlari.json"
form_kayitlari = []

os.makedirs(RESIM_KLASORU, exist_ok=True)

# --- JSON Veri Okuma ---
def verileri_jsondan_oku():
    if not os.path.exists(VERI_DOSYASI):
        return []
    with open(VERI_DOSYASI, "r", encoding="utf-8") as dosya:
        kayitlar = json.load(dosya)
        for kayit in kayitlar:
            kayit["tarih"] = datetime.datetime.fromisoformat(kayit["tarih"])
        return kayitlar

# --- JSON Veri Yazma ---
def verileri_jsona_yaz():
    with open(VERI_DOSYASI, "w", encoding="utf-8") as dosya:
        json.dump(form_kayitlari, dosya, ensure_ascii=False, indent=4, default=str)

# --- Resmi Kopyala ve Kaydet ---
def resmi_kopyala_kaydet(orijinal_yol):
    if not os.path.exists(orijinal_yol):
        return None
    uzanti = os.path.splitext(orijinal_yol)[1]
    yeni_ad = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}{uzanti}"
    hedef_yol = os.path.join(RESIM_KLASORU, yeni_ad)
    shutil.copy(orijinal_yol, hedef_yol)
    return hedef_yol

# --- Ana Pencere ---
def ana_pencere_olustur():
    global form_kayitlari
    form_kayitlari = verileri_jsondan_oku()

    pencere = tk.Tk()
    pencere.title("Form Yükleme Uygulaması ~Refo")
    pencere.geometry("800x500")
    pencere.configure(bg='lightblue')
    imza = tk.Label(pencere, text="Made by REFO", font=("arial", 10), fg="white", bg="red",)
    imza.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    buton_frame = tk.Frame(pencere)
    buton_frame.pack(pady=50)

    tk.Button(buton_frame, text="Yeni Form Yükle", font=("Arial", 14), width=20, height=2,
              command=form_yukle_penceresi).pack(side="left", padx=20)

    tk.Button(buton_frame, text="Yüklenen Formlar", font=("Arial", 14), width=20, height=2,
              command=yuklenen_formlari_goster).pack(side="left", padx=20)

    pencere.mainloop()

# --- Form Yükleme Penceresi ---
def form_yukle_penceresi():
    pencere = tk.Toplevel()
    pencere.title("Form Yükle")
    pencere.geometry("400x400")
    imza = tk.Label(pencere, text="Made by REFO", font=("arial", 10), fg="white", bg="red",)
    imza.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    tk.Label(pencere, text="Açıklama:").pack(pady=5)
    aciklama_entry = tk.Text(pencere, height=4, width=40)
    aciklama_entry.pack()

    tk.Label(pencere, text="Kategori:").pack(pady=5)
    kategori_entry = tk.Entry(pencere, width=40)
    kategori_entry.pack()

    def resmi_sec_ve_kaydet():
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg")])
        if dosya_yolu:
            yeni_yol = resmi_kopyala_kaydet(dosya_yolu)
            aciklama = aciklama_entry.get("1.0", tk.END).strip()
            kategori = kategori_entry.get().strip()
            tarih = datetime.datetime.now()

            form = {
                "resim_yolu": yeni_yol,
                "aciklama": aciklama,
                "kategori": kategori,
                "tarih": tarih
            }

            form_kayitlari.append(form)
            verileri_jsona_yaz()
            messagebox.showinfo("Başarılı", "Form yüklendi.")
            pencere.destroy()

    tk.Button(pencere, text="Resim Seç ve Yükle", command=resmi_sec_ve_kaydet,
              font=("Arial", 12), width=20).pack(pady=20)

# --- Yüklenen Formları Gösterme Penceresi ---
def yuklenen_formlari_goster():
    pencere = tk.Toplevel()
    pencere.title("Yüklenen Formlar")
    pencere.geometry("700x700")
    imza = tk.Label(pencere, text="Made by REFO", font=("arial", 10), fg="white", bg="red",)
    imza.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    # --- Silme fonksiyonu ---
    def formu_sil(form, frame):
        if messagebox.askyesno("Onay", "Bu formu silmek istediğinize emin misiniz?"):
            try:
                if os.path.exists(form["resim_yolu"]):
                    os.remove(form["resim_yolu"])
            except Exception as e:
                print("Resim silinemedi:", e)

            form_kayitlari.remove(form)
            verileri_jsona_yaz()
            frame.destroy()
            filtre_ve_goster()

    # --- Küçük resim göster ---
    def resmi_kucuk_goster(frame_icerik, form):
        try:
            img = Image.open(form["resim_yolu"])
            img.thumbnail((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            btn = tk.Button(frame_icerik, image=img_tk, command=lambda yol=form["resim_yolu"]: resmi_goster(yol))
            btn.image = img_tk
            btn.pack(side="left", padx=5)
        except:
            tk.Label(frame_icerik, text="Resim Yüklenemedi").pack(side="left", padx=5)

    # --- Filtreleme ve listeyi güncelle ---
    def filtre_ve_goster(*args):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        secilen_kategori = kategori_var.get()
        arama_kelimesi = arama_var.get().lower()

        # Filtrelenmiş listeyi oluştur
        for form in sorted(form_kayitlari, key=lambda x: x["tarih"], reverse=True):
            if (secilen_kategori == "Tümü" or form["kategori"] == secilen_kategori) and \
               (arama_kelimesi in form["aciklama"].lower()):
                frame = tk.Frame(scrollable_frame, bd=1, relief="solid", pady=5, padx=5)
                frame.pack(padx=10, pady=5, fill="x")

                # Küçük resmi göster
                resmi_kucuk_goster(frame, form)

                info = f"Açıklama: {form['aciklama']}\nKategori: {form['kategori']}\nTarih: {form['tarih'].strftime('%Y-%m-%d %H:%M:%S')}"
                tk.Label(frame, text=info, justify="left").pack(side="left", padx=10)

                # Sil butonu
                tk.Button(frame, text="Sil", fg="red", font=("Arial", 10, "bold"),
                          command=lambda f=form, fr=frame: formu_sil(f, fr)).pack(side="right", padx=5)

    # --- Üst filtre ve arama çubuğu ---
    ust_cerceve = tk.Frame(pencere)
    ust_cerceve.pack(fill="x", padx=10, pady=5)

    kategori_var = tk.StringVar(value="Tümü")
    kategoriler = sorted(set(f["kategori"] for f in form_kayitlari if f["kategori"]))
    kategori_secenekler = ["Tümü"] + kategoriler
    kategori_combo = ttk.Combobox(ust_cerceve, textvariable=kategori_var, values=kategori_secenekler, width=20)
    kategori_combo.pack(side="left", padx=5)

    arama_var = tk.StringVar()
    arama_entry = tk.Entry(ust_cerceve, textvariable=arama_var, width=30)
    arama_entry.pack(side="left", padx=5)

    tk.Label(ust_cerceve, text="(Kategori seçin / Açıklama arayın)").pack(side="left", padx=5)

    kategori_var.trace_add("write", filtre_ve_goster)
    arama_var.trace_add("write", filtre_ve_goster)

    # --- Scrollable Frame için ---
    canvas = tk.Canvas(pencere)
    scrollbar = tk.Scrollbar(pencere, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    filtre_ve_goster()

# --- Resim Görüntüleme ve Zoom ---
def resmi_goster(dosya_yolu):
    pencere = tk.Toplevel()
    pencere.title("Resim Görüntüle")
    pencere.geometry("800x600")

    canvas = tk.Canvas(pencere, bg="black")
    canvas.pack(fill="both", expand=True)

    orijinal_resim = Image.open(dosya_yolu)
    zoom_factor = 1.0
    resim_tk = None

    def resmi_guncelle():
        nonlocal zoom_factor, orijinal_resim, resim_tk
        yeni_boyut = (
            int(orijinal_resim.width * zoom_factor),
            int(orijinal_resim.height * zoom_factor)
        )
        guncellenmis = orijinal_resim.resize(yeni_boyut, Image.LANCZOS)
        resim_tk = ImageTk.PhotoImage(guncellenmis)
        canvas.delete("all")
        # Resmi canvas ortasında gösteriyoruz
        canvas.create_image(canvas.winfo_width()//2, canvas.winfo_height()//2, image=resim_tk, anchor="center")

    def mouse_scroll(event):
        nonlocal zoom_factor
        # Windows ve Mac için event.delta farklı olabilir
        if event.delta > 0 or event.num == 4:
            zoom_factor *= 1.1
        elif event.delta < 0 or event.num == 5:
            zoom_factor /= 1.1
        zoom_factor = max(0.1, min(zoom_factor, 5.0))
        resmi_guncelle()

    pencere.bind("<MouseWheel>", mouse_scroll)  # Windows, MacOS
    pencere.bind("<Button-4>", mouse_scroll)    # Linux scroll up
    pencere.bind("<Button-5>", mouse_scroll)    # Linux scroll down

    # Canvas boyutu değişince resmi güncelle
    def canvas_boyut_degisti(event):
        resmi_guncelle()
    canvas.bind("<Configure>", canvas_boyut_degisti)

    resmi_guncelle()
    pencere.mainloop()

# --- Programı Başlat ---
if __name__ == "__main__":
    ana_pencere_olustur()
