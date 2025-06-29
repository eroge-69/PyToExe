import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
import tkinter as tkmane.py
from tkinter import messagebox


class CryptoApp:
    def __init__(self, master):
        self.master = master
        master.title("Шифрование/Дешифрование")

        # Настройка интерфейса
        self.label = tk.Label(master, text="Введите текст:")
        self.label.pack()

        self.text_entry = tk.Text(master, height=5, width=50)
        self.text_entry.pack()

        self.password_label = tk.Label(master, text="Введите пароль:")
        self.password_label.pack()

        self.password_entry = tk.Entry(master, show="*", width=50)
        self.password_entry.pack()

        self.encrypt_button = tk.Button(master, text="Зашифровать", command=self.encrypt)
        self.encrypt_button.pack()

        self.decrypt_button = tk.Button(master, text="Расшифровать", command=self.decrypt)
        self.decrypt_button.pack()

        self.clear_button = tk.Button(master, text="Очистить", command=self.clear)
        self.clear_button.pack()

        self.result_label = tk.Label(master, text="Результат:")
        self.result_label.pack()

        self.result_text = tk.Text(master, height=5, width=50)
        self.result_text.pack()

    def pad(self, s):
        """Дополнение строки до размера, кратного 16 байтам"""
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

    def unpad(self, s):
        """Удаление дополнения из строки"""
        return s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        """Шифрование текста"""
        text = self.text_entry.get("1.0", tk.END).strip()
        password = self.password_entry.get()

        if not text or not password:
            messagebox.showerror("Ошибка", "Введите текст и пароль!")
            return

        try:
            # Генерация ключа из пароля
            key = hashlib.sha256(password.encode()).digest()

            # Дополнение текста и генерация вектора инициализации
            padded_text = self.pad(text)
            iv = Random.new().read(AES.block_size)

            # Создание шифра и шифрование текста
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_bytes = iv + cipher.encrypt(padded_text.encode('utf-8'))

            # Кодирование результата в base64
            encrypted_text = base64.b64encode(encrypted_bytes).decode('utf-8')

            # Вывод результата
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", encrypted_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании: {str(e)}")

    def decrypt(self):
        """Дешифрование текста"""
        encrypted_text = self.text_entry.get("1.0", tk.END).strip()
        password = self.password_entry.get()

        if not encrypted_text or not password:
            messagebox.showerror("Ошибка", "Введите зашифрованный текст и пароль!")
            return

        try:
            # Генерация ключа из пароля
            key = hashlib.sha256(password.encode()).digest()

            # Декодирование из base64
            encrypted_bytes = base64.b64decode(encrypted_text)

            # Извлечение вектора инициализации
            iv = encrypted_bytes[:AES.block_size]

            # Создание шифра и дешифрование текста
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_text = self.unpad(cipher.decrypt(encrypted_bytes[AES.block_size:])).decode('utf-8')

            # Вывод результата
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", decrypted_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при дешифровании: {str(e)}\nВозможно, неверный пароль.")

    def clear(self):
        """Очистка полей ввода и вывода"""
        self.text_entry.delete("1.0", tk.END)
        self.password_entry.delete(0, tk.END)
        self.result_text.delete("1.0", tk.END)


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()