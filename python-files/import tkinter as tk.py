import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import pygame
import os

# Varsayılan API Key ve Voice ID
DEFAULT_API_KEY = "sk_268566a1d02a4a57f9c71f1fb60a31d46dbcf28adea9845d"
DEFAULT_VOICE_ID = "mJABRua3NNxiiWgsfM9j"

def metni_sese_cevir(dosya_yolu):
    api_key = api_key_entry.get().strip() or DEFAULT_API_KEY
    voice_id = voice_id_entry.get().strip() or DEFAULT_VOICE_ID
    metin = metin_kutusu.get("1.0", tk.END).strip()
    stability = stability_scale.get() / 100
    similarity_boost = similarity_scale.get() / 100

    if not metin:
        messagebox.showwarning("Uyarı", "Lütfen metin girin.")
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    data = {
        "text": metin,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(dosya_yolu, "wb") as f:
                f.write(response.content)
            return True
        else:
            messagebox.showerror("Hata", f"API Hatası: {response.status_code}\n{response.text}")
            return False
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
        return False

def dinle():
    temp_dosya = "temp_ses.mp3"
    if metni_sese_cevir(temp_dosya):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(temp_dosya)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Hata", f"Ses oynatılamadı: {str(e)}")

def kaydet():
    dosya_yolu = filedialog.asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("MP3 Dosyaları", "*.mp3")],
        title="MP3 dosyasını kaydet"
    )
    if dosya_yolu:
        if metni_sese_cevir(dosya_yolu):
            messagebox.showinfo("Başarılı", f"Ses dosyası '{dosya_yolu}' olarak kaydedildi.")

# Arayüz tasarımı
pencere = tk.Tk()
pencere.title("Metni MP3'e Çevir ve Dinle")
pencere.geometry("520x600")

tk.Label(pencere, text="API Key:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10,0))
api_key_entry = tk.Entry(pencere, width=60, show="*")
api_key_entry.insert(0, DEFAULT_API_KEY)
api_key_entry.pack(padx=10)

tk.Label(pencere, text="Voice ID:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10,0))
voice_id_entry = tk.Entry(pencere, width=60)
voice_id_entry.insert(0, DEFAULT_VOICE_ID)
voice_id_entry.pack(padx=10)

tk.Label(pencere, text="Metin:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(15,0))
metin_kutusu = tk.Text(pencere, height=12, width=60)
metin_kutusu.pack(padx=10, pady=5)

tk.Label(pencere, text="Stability (Sesin stabilitesi):", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10,0))
stability_scale = tk.Scale(pencere, from_=0, to=100, orient=tk.HORIZONTAL)
stability_scale.set(75)
stability_scale.pack(padx=10)

tk.Label(pencere, text="Similarity Boost (Ses benzerliği):", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10,0))
similarity_scale = tk.Scale(pencere, from_=0, to=100, orient=tk.HORIZONTAL)
similarity_scale.set(75)
similarity_scale.pack(padx=10)

# Butonlar
buton_frame = tk.Frame(pencere)
buton_frame.pack(pady=20)

dinle_buton = tk.Button(buton_frame, text="Dinle", command=dinle, bg="#2196F3", fg="white", font=("Arial", 12), width=15)
dinle_buton.pack(side="left", padx=10)

kaydet_buton = tk.Button(buton_frame, text="MP3 Olarak Kaydet", command=kaydet, bg="#4CAF50", fg="white", font=("Arial", 12), width=20)
kaydet_buton.pack(side="left", padx=10)

pencere.mainloop()

# Geçici dosyayı sil
try:
    if os.path.exists("temp_ses.mp3"):
        os.remove("temp_ses.mp3")
except:
    pass
