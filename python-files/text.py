import tkinter as tk
from tkinter import messagebox
import secrets
import string
import os
import datetime

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parola Oluşturucu")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # Ana frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Başlık
        tk.Label(main_frame, text="Parola Oluşturucu", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        # Ad girişi
        tk.Label(main_frame, text="Ad (isteğe bağlı):", font=("Arial", 10)).pack(anchor="w")
        self.name_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.name_entry.pack(pady=(5, 10), fill="x")

        # Soyad girişi
        tk.Label(main_frame, text="Soyad (isteğe bağlı):", font=("Arial", 10)).pack(anchor="w")
        self.surname_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.surname_entry.pack(pady=(5, 10), fill="x")

        # Parola uzunluğu seçimi
        tk.Label(main_frame, text="Parola Uzunluğu (12-20):", font=("Arial", 10)).pack(anchor="w")
        self.length_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.length_entry.insert(0, "16")  # Varsayılan uzunluk
        self.length_entry.pack(pady=(5, 20), fill="x")

        # Parola oluştur butonu
        tk.Button(main_frame, text="Parola Oluştur", command=self.generate_password,
                  bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2).pack(pady=10, fill="x")

        # Çıkış butonu
        tk.Button(main_frame, text="Çıkış", command=root.quit,
                  bg="#f44336", fg="white", font=("Arial", 10)).pack(pady=10)

    def generate_password(self):
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        try:
            length = int(self.length_entry.get())
            if not 12 <= length <= 20:
                messagebox.showerror("Hata", "Parola uzunluğu 12 ile 20 arasında olmalı!")
                return
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı girin (12-20)!")
            return

        if name or surname:
            password = self.create_name_based_password(name, surname, length)
        else:
            password = self.create_random_password(length)

        self.show_password_window(password)

    def create_name_based_password(self, name, surname, length):
        base = ''.join(c for c in (name + surname).lower() if c.isalpha())
        if not base:
            base = string.ascii_lowercase

        numbers = [secrets.choice(string.digits) for _ in range(4)]
        special = [secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?") for _ in range(4)]
        chars = list(base) + numbers + special

        secrets.SystemRandom().shuffle(chars)

        while len(chars) < length:
            chars.append(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"))
        if len(chars) > length:
            chars = chars[:length]

        for i, char in enumerate(chars):
            if char.isalpha():
                chars[i] = char.upper()
                break

        return ''.join(chars)

    def create_random_password(self, length):
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        numbers = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(numbers),
            secrets.choice(special)
        ]

        all_chars = lowercase + uppercase + numbers + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

    def show_password_window(self, password):
        window = tk.Toplevel(self.root)
        window.title("Oluşturulan Parola")
        window.geometry("400x250")
        window.resizable(False, False)
        window.grab_set()

        frame = tk.Frame(window, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Oluşturulan Parola:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        password_text = tk.Text(frame, height=3, width=40, font=("Arial", 11), wrap="word", bg="#f0f0f0")
        password_text.insert("1.0", password)
        password_text.config(state="disabled")
        password_text.pack(pady=(0, 20))

        button_frame = tk.Frame(frame)
        button_frame.pack(fill="x")

        # Panoya kopyala butonu kaldırıldı

        tk.Button(button_frame, text="Masaüstüne Kaydet", command=lambda: self.save_to_desktop(password),
                  bg="#FF9800", fg="white", font=("Arial", 9)).pack(side="left", padx=5, fill="x", expand=True)

        button_frame2 = tk.Frame(frame)
        button_frame2.pack(fill="x", pady=(10, 0))

        tk.Button(button_frame2, text="Parolayı Karmaşıklaştır",
                  command=lambda: self.complicate_password(password, window),
                  bg="#9C27B0", fg="white", font=("Arial", 9)).pack(side="left", padx=(0, 5), fill="x", expand=True)

        tk.Button(button_frame2, text="Kapat", command=window.destroy,
                  bg="#607D8B", fg="white", font=("Arial", 9)).pack(side="left", padx=5, fill="x", expand=True)

    def save_to_desktop(self, password):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop, f"parola_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Oluşturulan Parola: {password}\n")
                f.write(f"Oluşturulma Tarihi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            messagebox.showinfo("Başarılı", f"Parola masaüstüne kaydedildi!\nDosya: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Parola kaydedilemedi!\nHata: {str(e)}")

    def complicate_password(self, password, parent_window):
        chars = list(password)
        secrets.SystemRandom().shuffle(chars)

        chars = chars[::-1]
        for _ in range(3):
            pos = secrets.randbelow(len(chars) + 1)
            chars.insert(pos, secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

        for i in range(len(chars)):
            if secrets.randbelow(2) and chars[i].isalpha():
                chars[i] = chars[i].upper() if chars[i].islower() else chars[i].lower()

        new_password = ''.join(chars[:20])
        parent_window.destroy()
        self.show_password_window(new_password)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()