
import tkinter as tk
import pyttsx3

engine = pyttsx3.init()

def panggil_nomor():
    format_str = entry_format.get()
    kode = entry_kode.get().strip().upper()
    nomor = entry_nomor.get().strip().zfill(3)
    loket = entry_loket.get().strip()

    if not nomor or not loket:
        label_status.config(text="❌ Isi semua kolom!", fg="red")
        return

    teks_antrian = format_str.replace("{kode}", kode).replace("{nomor}", nomor)
    teks_panggilan = f"{teks_antrian}, silakan ke loket {loket}"
    engine.say(teks_panggilan)
    engine.runAndWait()
    label_status.config(text=f"✅ {teks_panggilan}", fg="green")

root = tk.Tk()
root.title("Panggilan Antrian Puskesmas")
root.geometry("500x300")

tk.Label(root, text="Format Antrian (misal: Poli-{kode}-{nomor}):").pack()
entry_format = tk.Entry(root, font=("Arial", 12))
entry_format.insert(0, "Poli-{kode}-{nomor}")
entry_format.pack(fill="x", padx=20)

tk.Label(root, text="Kode (misal: G):").pack()
entry_kode = tk.Entry(root, font=("Arial", 12))
entry_kode.pack(fill="x", padx=20)

tk.Label(root, text="Nomor Antrian (angka):").pack()
entry_nomor = tk.Entry(root, font=("Arial", 12))
entry_nomor.pack(fill="x", padx=20)

tk.Label(root, text="Loket:").pack()
entry_loket = tk.Entry(root, font=("Arial", 12))
entry_loket.pack(fill="x", padx=20)

tk.Button(root, text="🔊 Panggil", font=("Arial", 14), command=panggil_nomor).pack(pady=10)

label_status = tk.Label(root, text="", font=("Arial", 12))
label_status.pack()

root.mainloop()
