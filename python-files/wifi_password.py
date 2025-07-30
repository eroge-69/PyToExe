import subprocess
import tkinter as tk
from tkinter import messagebox

def find_wifi_passwords():
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="backslashreplace").split('\n')
        profiles = []
        for line in data:
            if "All User Profile" in line:
                profile_name = line.split(":")[1].strip()
                profiles.append(profile_name)

        results = ""
        for profile in profiles:
            try:
                results_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8', errors="backslashreplace").split('\n')
                password = None
                for line in results_data:
                    if "Key Content" in line:
                        password = line.split(":")[1].strip()
                        break
                results += f"{profile:<30} | {password if password else 'Şifre Bulunamadı'}\n"
            except subprocess.CalledProcessError:
                results += f"{profile:<30} | HATA OLDU\n"

        messagebox.showinfo("Sonuçlar", results)
    except Exception as e:
        messagebox.showerror("Hata", str(e))

# Arayüz oluşturma
root = tk.Tk()
root.title("WiFi Bulucu")

# Pencere boyutunu ayarlama
root.geometry("350x350")  # Pencere boyutunu ayarlayın

# Butonu ortalamak için bir çerçeve ekleyin
frame = tk.Frame(root)
frame.pack(expand=True)  # Çerçeveyi ortalamak için genişletin

button = tk.Button(frame, text="WiFi Bul", command=find_wifi_passwords)
button.pack(pady=20)  # Butonu çerçeve içinde ortalayın

root.mainloop()