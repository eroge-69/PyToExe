# Bu, Python'un yerel GUI (Grafik Kullanıcı Arayüzü) kütüphanesidir.
import tkinter as tk
from tkinter import messagebox

# Uygulamanın ana penceresini oluşturur.
root = tk.Tk()
root.title("Gyssagly Ýardam")
root.geometry("400x600")
root.configure(bg="#2E2E3A") # Arka plan rengini ayarlar.

# Ekranlar arasında geçiş yapmak için bir konteyner oluşturur.
main_frame = tk.Frame(root, bg="#2E2E3A")
main_frame.pack(fill="both", expand=True)

# Ekranları temsil eden Frame'leri oluşturur.
register_frame = tk.Frame(main_frame, bg="#2E2E3A")
emergency_frame = tk.Frame(main_frame, bg="#2E2E3A")

# Ekranları yöneten bir fonksiyon.
def show_frame(frame):
    for widget in main_frame.winfo_children():
        widget.pack_forget()
    frame.pack(fill="both", expand=True)

# Bilgileri kaydetme fonksiyonu.
def save_data():
    name = name_entry.get()
    phone = phone_entry.get()
    
    if not name or not phone:
        messagebox.showerror("Hata", "Hemme meýdanlary dolduryň!")
        return

    # Bilgileri yerel bir dosyaya kaydetmeyi simgeler.
    try:
        with open("ulanyjy_maglumaty.txt", "w") as file:
            file.write(f"Ady: {name}\n")
            file.write(f"Telefon Belgisi: {phone}\n")
        messagebox.showinfo("Üstünlik", "Maglumatlar üstünlikli ýazyldy.")
        
        # Ekranı değiştirir.
        welcome_label.config(text=f"Salam, {name}!")
        show_frame(emergency_frame)
    except Exception as e:
        messagebox.showerror("Hata", f"Ýazmakda ýalňyşlyk: {e}")

# Acil durum aramasını simüle eden fonksiyon.
def make_emergency_call():
    # Masaüstü uygulamaları telefon araması yapamaz.
    messagebox.showinfo("Jaň et", "112-nji belgä jaň etmek funksiýasy işjeňleşdirildi.")

# Kayıt Ekranı Arayüzü
title_label = tk.Label(register_frame, text="Maglumatlaryňyz", font=("Arial", 28, "bold"), fg="white", bg="#2E2E3A")
title_label.pack(pady=40)

name_entry = tk.Entry(register_frame, font=("Arial", 16), width=30, justify="center", bg="#42424E", fg="white", insertbackground="white")
name_entry.insert(0, "Adyňyz we Familiýaňyz")
name_entry.bind("<FocusIn>", lambda event: name_entry.delete(0, tk.END) if name_entry.get() == "Adyňyz we Familiýaňyz" else None)
name_entry.pack(pady=10, padx=20)

phone_entry = tk.Entry(register_frame, font=("Arial", 16), width=30, justify="center", bg="#42424E", fg="white", insertbackground="white")
phone_entry.insert(0, "Telefon belgiňiz")
phone_entry.bind("<FocusIn>", lambda event: phone_entry.delete(0, tk.END) if phone_entry.get() == "Telefon belgiňiz" else None)
phone_entry.pack(pady=10, padx=20)

save_button = tk.Button(register_frame, text="Maglumatlary Ýazdyr", font=("Arial", 18, "bold"), fg="white", bg="#007BFF", relief="flat", padx=20, pady=10, command=save_data)
save_button.pack(pady=30, padx=20)

# Acil Durum Ekranı Arayüzü
welcome_label = tk.Label(emergency_frame, text="Salam!", font=("Arial", 24, "bold"), fg="white", bg="#2E2E3A")
welcome_label.pack(pady=50)

call_button = tk.Button(emergency_frame, text="Jaň et", font=("Arial", 32, "bold"), fg="white", bg="#DC3545", relief="flat", width=12, height=6, command=make_emergency_call)
call_button.pack(pady=30, padx=20)

# Uygulamanın başlangıcında kayıt ekranını gösterir.
show_frame(register_frame)

# Ana döngüyü başlatır.
root.mainloop()
