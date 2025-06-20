import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import hashlib

# Malkocx Şifreleme ve Çözme Algoritması
def malkocx_encrypt(data):
    encrypted_data = []
    shift_value = 5  # Şifreleme için kaydırma değeri

    for char in data:
        shifted_char = chr((ord(char) + shift_value) % 256)
        encrypted_data.append(shifted_char)
    
    return ''.join(encrypted_data)

def malkocx_decrypt(encrypted_data):
    decrypted_data = []
    shift_value = 5  # Şifre çözme için aynı kaydırma değeri

    for char in encrypted_data:
        shifted_char = chr((ord(char) - shift_value) % 256)
        decrypted_data.append(shifted_char)
    
    return ''.join(decrypted_data)

# Şifrelerin kaydedileceği dosya yolu (C: diskinde)
def get_file_path():
    base_dir = "C:\\Malkocx Authenticator Files"
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "passwords.txt")

# Ana şifre kaydetme
def set_master_password():
    global master_password
    master_password = simpledialog.askstring("Ana Şifre Belirle", "Ana şifrenizi belirleyin:", show="*")
    if master_password:
        hashed_master_password = hashlib.sha256(master_password.encode()).hexdigest()
        with open(get_file_path(), "a") as file:
            file.write(f"master,{hashed_master_password}\n")  # Ana şifreyi dosyaya kaydediyoruz
        messagebox.showinfo("Başarılı", "Ana şifreniz başarıyla belirlendi!")
        master_password_button.pack_forget()  # Butonu gizle

# Şifre ve platform bilgilerini kaydetme
def save_password():
    platform = platform_input.get()
    password = password_input.get()

    if not platform or not password:
        messagebox.showwarning("Eksik Bilgi", "Platform ve Şifre alanları doldurulmalıdır!")
        return
    
    encrypted_password = malkocx_encrypt(password)
    hashed_password = hashlib.sha256(encrypted_password.encode()).hexdigest()
    
    with open(get_file_path(), "a") as file:
        file.write(f"{platform},{encrypted_password},{hashed_password}\n")
    
    messagebox.showinfo("Başarılı", "Şifre kaydedildi!")
    platform_input.delete(0, tk.END)
    password_input.delete(0, tk.END)

# Şifreleri listeleme ve çözme
def retrieve_password():
    entered_password = simpledialog.askstring("Giriş", "Ana şifrenizi girin:", show="*")

    if entered_password and hashlib.sha256(entered_password.encode()).hexdigest() == get_stored_master_password():
        platform = simpledialog.askstring("Platform Seçimi", "Şifresini görüntülemek istediğiniz platformu girin:")
        if not platform:
            messagebox.showwarning("Eksik Bilgi", "Platform adı belirtilmelidir!")
            return
        
        with open(get_file_path(), "r") as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) < 3:
                    continue  # Eğer satırda yeterince parça yoksa devam et
                stored_platform, encrypted_password, _ = parts
                if stored_platform == platform:
                    decrypted_password = malkocx_decrypt(encrypted_password)
                    messagebox.showinfo("Şifre Çözüldü", f"{platform} için şifreniz: {decrypted_password}")
                    return
        
        messagebox.showwarning("Bulunamadı", f"{platform} platformu için şifre bulunamadı.")
    else:
        messagebox.showwarning("Hata", "Yanlış ana şifre!")

# Ana şifreyi dosyadan okuma
def get_stored_master_password():
    with open(get_file_path(), "r") as file:
        for line in file:
            if line.startswith("master"):
                return line.strip().split(",")[1]
    return None

# GUI Tasarımı
window = tk.Tk()
window.title("Malkocx Şifre Yöneticisi")

# Ana şifre belirleme butonu
master_password_button = tk.Button(window, text="Ana Şifre Belirle", command=set_master_password)
master_password_button.pack(pady=5)

# Platform ve Şifre giriş alanları
tk.Label(window, text="Platform:").pack()
platform_input = tk.Entry(window, width=30)
platform_input.pack()

tk.Label(window, text="Şifre:").pack()
password_input = tk.Entry(window, width=30, show="*")
password_input.pack()

# Kaydetme ve Şifre Çözme butonları
tk.Button(window, text="Şifre Kaydet", command=save_password).pack(pady=5)
tk.Button(window, text="Şifreleri Görüntüle", command=retrieve_password).pack(pady=5)

# GUI Başlat
window.mainloop()
