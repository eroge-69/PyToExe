import tkinter as tk
from tkinter import messagebox
import secrets
import string
import os
import pyperclip
import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Parola Oluşturucu")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Ana frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Başlık
        title_label = tk.Label(main_frame, text="Parola Oluşturucu", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Ad alanı
        tk.Label(main_frame, text="Ad (isteğe bağlı):", font=("Arial", 10)).pack(anchor="w")
        self.name_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.name_entry.pack(pady=(5, 10), fill="x")
        
        # Soyad alanı
        tk.Label(main_frame, text="Soyad (isteğe bağlı):", font=("Arial", 10)).pack(anchor="w")
        self.surname_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.surname_entry.pack(pady=(5, 20), fill="x")
        
        # Parola oluştur butonu
        generate_btn = tk.Button(main_frame, text="Parola Oluştur", 
                               command=self.generate_password,
                               bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                               height=2)
        generate_btn.pack(pady=10, fill="x")
        
        # Çıkış butonu
        exit_btn = tk.Button(main_frame, text="Çıkış", 
                           command=root.quit,
                           bg="#f44336", fg="white", font=("Arial", 10))
        exit_btn.pack(pady=10)
        
    def generate_password(self):
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        
        if name or surname:
            password = self.create_name_based_password(name, surname)
        else:
            password = self.create_random_password()
        
        self.show_password_window(password)
    
    def create_name_based_password(self, name, surname):
        # Ad ve soyadı birleştir
        all_letters = list((name + surname).lower())
        
        # Harfleri karıştır
        secrets.SystemRandom().shuffle(all_letters)
        
        # Rastgele sayılar ve özel karakterler ekle
        numbers = [secrets.choice(string.digits) for _ in range(4)]
        special_chars = [secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?") for _ in range(4)]
        
        # Tüm karakterleri birleştir
        password_chars = all_letters + numbers + special_chars
        secrets.SystemRandom().shuffle(password_chars)
        
        # İlk harfi büyük yap
        if password_chars and password_chars[0].isalpha():
            password_chars[0] = password_chars[0].upper()
        
        # Parola uzunluğunu 12-20 arasında rastgele seç
        length = secrets.randbelow(9) + 12
        while len(password_chars) < length:
            password_chars.append(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        return ''.join(password_chars[:length])
    
    def create_random_password(self):
        # Rastgele parola uzunluğu (12-20)
        length = secrets.randbelow(9) + 12
        
        # Karakter setleri
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        numbers = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Her türden en az bir karakter garanti et
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(numbers),
            secrets.choice(special)
        ]
        
        # Kalan karakterleri rastgele doldur
        all_chars = lowercase + uppercase + numbers + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Karıştır
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def show_password_window(self, password):
        # Yeni pencere oluştur
        password_window = tk.Toplevel(self.root)
        password_window.title("Oluşturulan Parola")
        password_window.geometry("400x250")
        password_window.resizable(False, False)
        password_window.grab_set()
        
        frame = tk.Frame(password_window, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        # Parola göster
        tk.Label(frame, text="Oluşturulan Parola:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        password_text = tk.Text(frame, height=3, width=40, font=("Arial", 11), 
                               wrap=tk.WORD, bg="#f0f0f0")
        password_text.insert(tk.END, password)
        password_text.config(state=tk.DISABLED)
        password_text.pack(pady=(0, 20))
        
        # Buton frame
        button_frame = tk.Frame(frame)
        button_frame.pack(fill="x")
        
        # Butonlar
        copy_btn = tk.Button(button_frame, text="Panoya Kopyala", 
                           command=lambda: self.copy_to_clipboard(password),
                           bg="#2196F3", fg="white", font=("Arial", 9))
        copy_btn.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        save_btn = tk.Button(button_frame, text="Masaüstüne Kaydet", 
                           command=lambda: self.save_to_desktop(password),
                           bg="#FF9800", fg="white", font=("Arial", 9))
        save_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # İkinci buton satırı
        button_frame2 = tk.Frame(frame)
        button_frame2.pack(fill="x", pady=(10, 0))
        
        complicate_btn = tk.Button(button_frame2, text="Parolayı Karmaşıklaştır", 
                                 command=lambda: self.complicate_password(password, password_window),
                                 bg="#9C27B0", fg="white", font=("Arial", 9))
        complicate_btn.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        close_btn = tk.Button(button_frame2, text="Kapat", 
                            command=password_window.destroy,
                            bg="#607D8B", fg="white", font=("Arial", 9))
        close_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    def copy_to_clipboard(self, password):
        try:
            pyperclip.copy(password)
            messagebox.showinfo("Başarılı", "Parola panoya kopyalandı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Parola panoya kopyalanamadı!\nHata: {str(e)}")
    
    def save_to_desktop(self, password):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop, "parola.txt")
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Oluşturulan Parola: {password}\n")
                f.write(f"Oluşturulma Tarihi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            messagebox.showinfo("Başarılı", f"Parola masaüstüne kaydedildi!\nDosya: parola.txt")
        except Exception as e:
            messagebox.showerror("Hata", f"Parola kaydedilemedi!\nHata: {str(e)}")
    
    def complicate_password(self, password, parent_window):
        # Parolayı karmaşıklaştır: ters çevir, ek karakterler ekle, harfleri değiştir
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        # Ters çevir
        password_list = password_list[::-1]
        
        # Rastgele pozisyonlara ek karakterler ekle
        for _ in range(4):
            pos = secrets.randbelow(len(password_list) + 1)
            password_list.insert(pos, secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        # Bazı harfleri büyük/küçük yap
        for i in range(len(password_list)):
            if secrets.randbelow(2) and password_list[i].isalpha():
                password_list[i] = password_list[i].upper() if password_list[i].islower() else password_list[i].lower()
        
        complicated_password = ''.join(password_list)
        
        parent_window.destroy()
        self.show_password_window(complicated_password)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()