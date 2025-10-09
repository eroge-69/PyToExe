import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread

# ------------------------------------------------------------
# 1️⃣  MERGE FONKSİYONU
# ------------------------------------------------------------
def merge_fivem_vehicles(folder_path):
    data_path = os.path.join(folder_path, "data")
    stream_path = os.path.join(folder_path, "stream")

    if not os.path.exists(data_path) or not os.path.exists(stream_path):
        messagebox.showerror("Hata", "Bu klasörde 'data' ve 'stream' klasörleri bulunamadı!")
        return

    merged_path = os.path.join(folder_path, "merged_resource")
    merged_data_path = os.path.join(merged_path, "data")
    merged_stream_path = os.path.join(merged_path, "stream")

    os.makedirs(merged_data_path, exist_ok=True)
    os.makedirs(merged_stream_path, exist_ok=True)

    # 🔥 Birleştirilecek META dosyaları (tam liste)
    meta_files = [
        "carcols.meta",
        "carvariations.meta",
        "dlctext.meta",
        "handling.meta",
        "shop_vehicle.meta",
        "vehiclelayouts.meta",  # ✅ doğru isim
        "vehicles.meta"
    ]

    # ------------------------------------------------------------
    # 2️⃣  META DOSYALARINI BİRLEŞTİR
    # ------------------------------------------------------------
    for meta in meta_files:
        merged_file_path = os.path.join(merged_data_path, meta)
        with open(merged_file_path, "w", encoding="utf-8") as outfile:
            for subfolder in os.listdir(data_path):
                subfolder_path = os.path.join(data_path, subfolder)
                meta_file_path = os.path.join(subfolder_path, meta)
                if os.path.exists(meta_file_path):
                    with open(meta_file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read().strip() + "\n\n")
        print(f"{meta} birleştirildi.")

    # ------------------------------------------------------------
    # 3️⃣  STREAM DOSYALARINI KOPYALA
    # ------------------------------------------------------------
    for subfolder in os.listdir(stream_path):
        src = os.path.join(stream_path, subfolder)
        if os.path.isdir(src):
            for file in os.listdir(src):
                shutil.copy(os.path.join(src, file), merged_stream_path)
        else:
            shutil.copy(src, merged_stream_path)
    print("Tüm stream dosyaları kopyalandı.")

    # ------------------------------------------------------------
    # 4️⃣  FXMANIFEST OLUŞTUR
    # ------------------------------------------------------------
    fxmanifest_path = os.path.join(merged_path, "fxmanifest.lua")
    with open(fxmanifest_path, "w", encoding="utf-8") as f:
        f.write(f"""fx_version 'cerulean'
game 'gta5'

files {{
    'data/**/*.meta'
}}

data_file 'HANDLING_FILE' 'data/handling.meta'
data_file 'VEHICLE_METADATA_FILE' 'data/vehicles.meta'
data_file 'CARCOLS_FILE' 'data/carcols.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/carvariations.meta'
data_file 'VEHICLE_LAYOUTS_FILE' 'data/vehiclelayouts.meta'
data_file 'DLC_TEXT_FILE' 'data/dlctext.meta'

client_script 'client.lua'
""")

    messagebox.showinfo("Tamamlandı", "✅ Araçlar başarıyla birleştirildi!\n\nKlasör: merged_resource")

# ------------------------------------------------------------
# 5️⃣  GUI (Görsel Arayüz)
# ------------------------------------------------------------
def start_merge():
    folder_path = filedialog.askdirectory(title="Resource klasörünü seç (data + stream içeren)")
    if not folder_path:
        return
    status_label.config(text="Birleştiriliyor, lütfen bekleyin...")
    merge_button.config(state="disabled")

    def run():
        merge_fivem_vehicles(folder_path)
        status_label.config(text="✅ Birleştirme tamamlandı!")
        merge_button.config(state="normal")

    Thread(target=run).start()

# ------------------------------------------------------------
# 6️⃣  ARAYÜZ TASARIMI
# ------------------------------------------------------------
root = tk.Tk()
root.title("🚗 FiveM Vehicle Merger")
root.geometry("420x260")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

title_label = tk.Label(root, text="FiveM Vehicle Merger", fg="white", bg="#1e1e1e", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=20)

desc_label = tk.Label(root, text="Araç resource'larını tek klasörde birleştir!", fg="#bbbbbb", bg="#1e1e1e", font=("Segoe UI", 10))
desc_label.pack()

merge_button = tk.Button(
    root, text="Klasör Seç ve Birleştir", command=start_merge,
    bg="#0078d7", fg="white", font=("Segoe UI", 11, "bold"),
    relief="flat", width=25, height=2
)
merge_button.pack(pady=25)

status_label = tk.Label(root, text="", fg="#00ff88", bg="#1e1e1e", font=("Segoe UI", 10))
status_label.pack()

root.mainloop()
