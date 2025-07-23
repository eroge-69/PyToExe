import os
import tkinter as tk
from tkinter import messagebox

# Username dan Password yang sah
USERNAME = "navy"
PASSWORD = "amandaimut123"

# Fungsi untuk memeriksa login
def check_login():
    entered_user = username_entry.get()
    entered_pass = password_entry.get()

    if entered_user == USERNAME and entered_pass == PASSWORD:
        os.system("start explorer.exe")
        root.destroy()  # Menutup layar jika login benar
    else:
        messagebox.showerror("Login Gagal", "Username atau password salah!")
        password_entry.delete(0, tk.END)

# Membuat jendela utama
root = tk.Tk()
root.title("LOCKED")
root.attributes("-fullscreen", True)  # Fullscreen
root.protocol("WM_DELETE_WINDOW", lambda: None)  # Menonaktifkan tombol close
root.bind("<Alt-F4>", lambda e: "break")  # Mencegah Alt+F4
root.bind("<Escape>", lambda e: "break")  # Mencegah ESC
os.system("taskkill /F /IM explorer.exe")

# Warna latar belakang
root.configure(bg="black")

# Judul atau pesan di layar
label = tk.Label(root, text="🔒 Screen Locked 🔒", font=("Helvetica", 32), fg="white", bg="black")
label.pack(pady=40)

# Entry untuk username
username_label = tk.Label(root, text="Username:", fg="white", bg="black", font=("Arial", 16))
username_label.pack()
username_entry = tk.Entry(root, font=("Arial", 16), justify='center')
username_entry.pack(pady=10)

# Entry untuk password
password_label = tk.Label(root, text="Password:", fg="white", bg="black", font=("Arial", 16))
password_label.pack()
password_entry = tk.Entry(root, show="*", font=("Arial", 16), justify='center')
password_entry.pack(pady=10)

# Tombol login
login_button = tk.Button(root, text="Unlock", font=("Arial", 16), command=check_login)
login_button.pack(pady=30)

# Fokus ke entry pertama saat start
username_entry.focus_set()

# Jalankan loop aplikasi
root.mainloop()
