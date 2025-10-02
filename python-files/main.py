import tkinter as tk
from tkinter import messagebox, ttk
import pyrebase
import subprocess
import serial.tools.list_ports

# Firebase config
firebaseConfig = {
  "apiKey": "AIzaSyAKmKfv3NLJvrQ6CqhGRB-S4OkJ5-LrqhA",
  "authDomain": "vionos-92152.firebaseapp.com",
  "databaseURL": "https://vionos-92152-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "vionos-92152",
  "storageBucket": "vionos-92152.firebasestorage.app",
  "messagingSenderId": "43451201247",
  "appId": "1:43451201247:web:54f9b2941e72ca9cb21b6a",
  "measurementId": "G-V0X57FFZE6"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Ana pencere
root = tk.Tk()
root.title("🚴 VionOS BIKE Sürüm Yükle")
root.geometry("550x650")
root.configure(bg="#f8f9fa")

# Başlık
title = tk.Label(root, text="VionOS BIKE Sürüm Yükle",
                 font=("Google Sans", 20, "bold"),
                 bg="#f8f9fa", fg="#202124")
title.pack(pady=20)

subtitle = tk.Label(root, text="Firebase üzerindeki sürümlerden birini seçin ve Arduino Nano’ya yükleyin.",
                    font=("Google Sans", 11),
                    bg="#f8f9fa", fg="#5f6368", wraplength=480, justify="center")
subtitle.pack(pady=10)


# --- Hover efekti fonksiyonları ---
def on_enter(e):
    e.widget.config(bg="#185abc", fg="white")

def on_leave(e):
    e.widget.config(bg="#1a73e8", fg="white")


def upload_code(code):
    # COM portları bul
    ports = [port.device for port in serial.tools.list_ports.comports()]
    if not ports:
        messagebox.showerror("Hata", "Herhangi bir COM port bulunamadı!")
        return

    # Port seçim penceresi
    top = tk.Toplevel(root)
    top.title("COM Port Seç")
    top.geometry("350x200")
    top.configure(bg="#f8f9fa")

    tk.Label(top, text="Bir COM port seçin:", 
             font=("Google Sans", 12), bg="#f8f9fa").pack(pady=15)

    selected_com = tk.StringVar()
    combo = ttk.Combobox(top, textvariable=selected_com, values=ports, font=("Google Sans", 11))
    combo.pack(pady=10)

    def confirm():
        com = selected_com.get()
        if com not in ports:
            messagebox.showerror("Hata", "Geçersiz COM port seçildi!")
            return

        # Kod .ino dosyasına yaz
        import os
        os.makedirs("temp_code", exist_ok=True)
        with open("temp_code/temp_code.ino", "w", encoding="utf-8") as f:
            f.write(code)

        try:
            subprocess.run([
                "arduino-cli", "compile", "--fqbn", "arduino:avr:nano", "temp_code"
            ], check=True)

            subprocess.run([
                "arduino-cli", "upload", "-p", com, "--fqbn", "arduino:avr:nano", "temp_code"
            ], check=True)

            messagebox.showinfo("Başarılı", f"Sürüm {com} portuna yüklendi!")
            top.destroy()

        except Exception as e:
            messagebox.showerror("Hata", str(e))

    btn = tk.Button(top, text="Yükle", font=("Google Sans", 12, "bold"),
                    bg="#1a73e8", fg="white", relief="flat", padx=20, pady=8,
                    activebackground="#185abc", activeforeground="white",
                    command=confirm)
    btn.pack(pady=20)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


# Firebase'den sürümleri çek
versions = db.child("versions").get()

container = tk.Frame(root, bg="#f8f9fa")
container.pack(pady=30, fill="both", expand=True)

if versions.each():
    for v in versions.each():
        code = v.val()

        # Kart benzeri Frame
        card = tk.Frame(container, bg="white", bd=0, relief="flat")
        card.pack(pady=10, padx=40, fill="x")

        # Gölge efekti simülasyonu
        card.config(highlightbackground="#dadce0", highlightthickness=1)

        lbl = tk.Label(card, text=f"Sürüm {v.key()}",
                       font=("Google Sans", 13, "bold"),
                       bg="white", fg="#202124", anchor="w")
        lbl.pack(pady=10, padx=15, anchor="w")

        btn = tk.Button(card, text="Yükle",
                        font=("Google Sans", 11, "bold"),
                        bg="#1a73e8", fg="white",
                        relief="flat", padx=15, pady=5,
                        activebackground="#185abc", activeforeground="white",
                        command=lambda c=code: upload_code(c))
        btn.pack(pady=10, padx=15, anchor="e")

        # Hover efekti
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

else:
    tk.Label(root, text="⚠️ Hiç sürüm bulunamadı!",
             font=("Google Sans", 12, "bold"),
             bg="#f8f9fa", fg="red").pack(pady=40)

root.mainloop()
