import tkinter as tk
from tkinter import filedialog, messagebox
import math

def temizle_srt():
    dosya_yolu = filedialog.askopenfilename(
        title="SRT Dosyası Seç",
        filetypes=(("SRT files", ".srt"), ("All files", ".*"))
    )
    if not dosya_yolu:
        return

    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            satirlar = f.readlines()

        temiz_satirlar = []
        zaman = None
        for satir in satirlar:
            satir = satir.strip()
            if satir.isdigit() or satir == "":
                continue
            if "-->" in satir:   # zaman satırı
                zaman = satir
            else:                # cümle satırı
                if zaman:
                    temiz_satirlar.append(f"{zaman} | {satir}")
                    zaman = None

        if bolme_var.get():  # Checkbox işaretli ise parçala
            toplam_satir = len(temiz_satirlar)
            parca_sayisi = math.ceil(toplam_satir / 400)

            for i in range(parca_sayisi):
                basla = i * 400
                bitir = basla + 400
                parca = temiz_satirlar[basla:bitir]
                yeni_dosya = dosya_yolu.replace(".srt", f"_temiz_part{i+1}.txt")
                with open(yeni_dosya, "w", encoding="utf-8") as f:
                    f.write("\n".join(parca))

            messagebox.showinfo("Başarılı", f"{parca_sayisi} dosya oluşturuldu (her biri max 400 satır).")

        else:  # Tek dosya çıkar
            yeni_dosya = dosya_yolu.replace(".srt", "_temiz.txt")
            with open(yeni_dosya, "w", encoding="utf-8") as f:
                f.write("\n".join(temiz_satirlar))

            messagebox.showinfo("Başarılı", f"Temizlenmiş dosya kaydedildi:\n{yeni_dosya}")

    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")

# GUI
root = tk.Tk()
root.title("SRT Temizleyici")

bolme_var = tk.BooleanVar()

btn = tk.Button(root, text="SRT Dosyası Seç ve Temizle", command=temizle_srt)
btn.pack(padx=20, pady=10)

chk = tk.Checkbutton(root, text="400 satırda böl", variable=bolme_var)
chk.pack(padx=20, pady=10)

root.mainloop()