import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import string
import os
import pyperclip

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
        title_label = tk.Label(main_frame, text="Parola Oluşturucu", 
                              font=("Arial", 16, "bold"))
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
                               bg="#4CAF50", fg="white", 
                               font=("Arial", 12, "bold"),
                               height=2)
        generate_btn.pack(pady=10, fill="x")
        
        # Çıkış butonu
        exit_btn = tk.Button(main_frame, text="Çıkış", 
                           command=root.quit,
                           bg="#f44336", fg="white", 
                           font=("Arial", 10))
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
        # Ad ve soyadın harflerini birleştir
        all_letters = list((name + surname).lower())
        
        # Harfleri karıştır
        random.shuffle(all_letters)
        
        # Rastgele sayılar ve özel karakterler ekle
        numbers = [str(random.randint(0, 9)) for _ in range(3)]
        special_chars = random.choices(['!', '@', '#', '$', '%', '&', '*'], k=2)
        
        # Tüm karakterleri birleştir
        password_chars = all_letters + numbers + special_chars
        random.shuffle(password_chars)
        
        # İlk harfi büyük yap
        if password_chars and password_chars[0].isalpha():
            password_chars[0] = password_chars[0].upper()
        
        return ''.join(password_chars)
    
    def create_random_password(self):
        # Karmaşık rastgele parola oluştur
        length = random.randint(12, 16)
        
        # Farklı karakter türlerinden seç
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        numbers = string.digits
        special = "!@#$%&*"
        
        # Her türden en az bir karakter garanti et
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(numbers),
            random.choice(special)
        ]
        
        # Kalan karakterleri rastgele doldur
        all_chars = lowercase + uppercase + numbers + special
        for _ in range(length - 4):
            password.append(random.choice(all_chars))
        
        # Karıştır
        random.shuffle(password)
        return ''.join(password)
    
    def show_password_window(self, password):
        # Yeni pencere oluştur
        password_window = tk.Toplevel(self.root)
        password_window.title("Oluşturulan Parola")
        password_window.geometry("400x250")
        password_window.resizable(False, False)
        password_window.grab_set()  # Modal yapı
        
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
        except:
            messagebox.showerror("Hata", "Parola panoya kopyalanamadı!")
    
    def save_to_desktop(self, password):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop, "parola.txt")
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Oluşturulan Parola: {password}\n")
                f.write(f"Oluşturulma Tarihi: {tk.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            messagebox.showinfo("Başarılı", f"Parola masaüstüne kaydedildi!\nDosya: parola.txt")
        except Exception as e:
            messagebox.showerror("Hata", f"Parola kaydedilemedi!\nHata: {str(e)}")
    
    def complicate_password(self, password, parent_window):
        # Karakterleri karıştır ve tersine çevir
        password_list = list(password)
        random.shuffle(password_list)
        complicated_password = ''.join(password_list)[::-1]
        
        parent_window.destroy()
        self.show_password_window(complicated_password)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()