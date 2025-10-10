import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
import os
from datetime import datetime

class RecipeCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шифратор")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Настройка шрифта для CustomTkinter
        self.custom_font = ("Consolas", 12)

        self.history = []
        self.load_history()
        self.current_file = None

        self.method_var = ctk.StringVar(value="Цезарь")
        self.key_var = ctk.StringVar(value="3")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель управления
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 10))

        # Кнопки файлов
        self.open_btn = ctk.CTkButton(
            control_frame, text="📂 Открыть файл",
            command=self.open_file,
            fg_color="#607D8B", hover_color="#455A64"
        )
        self.open_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ctk.CTkButton(
            control_frame, text="💾 Сохранить результат",
            command=self.save_result,
            fg_color="#009688", hover_color="#00796B"
        )
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Метод шифрования
        ctk.CTkLabel(control_frame, text="Метод:").pack(side=tk.LEFT, padx=(0, 5))
        self.method_menu = ctk.CTkOptionMenu(
            control_frame,
            variable=self.method_var,
            values=["Цезарь", "Перестановка", "XOR", "Base64", "AES"],
            command=self.on_method_change
        )
        self.method_menu.pack(side=tk.LEFT, padx=(0, 10))

        # Ключ/Сдвиг
        ctk.CTkLabel(control_frame, text="Ключ/Сдвиг:").pack(side=tk.LEFT, padx=(0, 5))
        self.key_entry = ctk.CTkEntry(control_frame, textvariable=self.key_var, width=100)
        self.key_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Кнопка генерации ключа
        self.gen_key_btn = ctk.CTkButton(
            control_frame,
            text="🔑",
            width=40,
            command=self.generate_random_key
        )
        self.gen_key_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Кнопки шифрования
        self.encrypt_btn = ctk.CTkButton(
            control_frame, text="🔒 Зашифровать",
            command=self.encrypt,
            fg_color="#4CAF50", hover_color="#45a049"
        )
        self.encrypt_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.decrypt_btn = ctk.CTkButton(
            control_frame, text="🔓 Расшифровать",
            command=self.decrypt,
            fg_color="#F44336", hover_color="#d32f2f"
        )
        self.decrypt_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Поля ввода/вывода
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

        # Панель для кнопок копирования/вставки (исходный текст)
        input_control_frame = ctk.CTkFrame(input_frame)
        input_control_frame.pack(fill=tk.X, pady=(0, 5))

        ctk.CTkLabel(input_control_frame, text="Исходный текст:").pack(side=tk.LEFT)
        self.file_label = ctk.CTkLabel(input_control_frame, text="Файл не открыт", text_color="gray")
        self.file_label.pack(side=tk.RIGHT)

        copy_input_btn = ctk.CTkButton(
            input_control_frame, text="📋 Копировать",
            command=lambda: self.copy_text(self.input_text),
            width=100
        )
        copy_input_btn.pack(side=tk.RIGHT, padx=(0, 5))

        paste_input_btn = ctk.CTkButton(
            input_control_frame, text="🖌️ Вставить",
            command=lambda: self.paste_text(self.input_text),
            width=100
        )
        paste_input_btn.pack(side=tk.RIGHT)

        # Поле ввода с красивым шрифтом
        self.input_text = tk.Text(
            input_frame,
            wrap=tk.WORD,
            bg="#2b2b2b",
            fg="white",
            insertbackground="white",
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            font=("Consolas", 12)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.input_text.bind("<Control-c>", lambda e: self.copy_text(self.input_text))
        self.input_text.bind("<Control-v>", lambda e: self.paste_text(self.input_text))

        # Панель для кнопок копирования (результат)
        output_control_frame = ctk.CTkFrame(input_frame)
        output_control_frame.pack(fill=tk.X, pady=(0, 5))

        ctk.CTkLabel(output_control_frame, text="Результат:").pack(side=tk.LEFT)

        copy_output_btn = ctk.CTkButton(
            output_control_frame, text="📋 Копировать",
            command=lambda: self.copy_text(self.output_text),
            width=100
        )
        copy_output_btn.pack(side=tk.RIGHT)

        # Поле вывода с тем же шрифтом
        self.output_text = ctk.CTkTextbox(
            input_frame,
            wrap=tk.WORD,
            font=self.custom_font
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Подсказка
        self.tooltip = ctk.CTkLabel(
            main_frame,
            text="Откройте .txt файл или введите текст. Для XOR/AES можно сгенерировать ключ.\n",
            text_color="#AAAAAA"
        )
        self.tooltip.pack(fill=tk.X, pady=(10, 0))

        # Настройка поля ключа
        self.update_key_field()

    def on_method_change(self, method):
        self.update_key_field()
        if method in ["XOR", "AES"]:
            messagebox.showwarning(
                "Внимание!",
                f"⚠️ При использовании метода {method} ОБЯЗАТЕЛЬНО сохраните ключ!\n"
                "Без ключа расшифровать текст будет НЕВОЗМОЖНО!"
            )

    def update_key_field(self, event=None):
        method = self.method_var.get()
        if method in ["XOR", "AES"]:
            self.key_entry.configure(placeholder_text="Введите ключ или сгенерируйте")
            self.gen_key_btn.pack(side=tk.LEFT, padx=(0, 10))
        elif method == "Цезарь":
            self.key_entry.configure(placeholder_text="Сдвиг (число)")
            self.gen_key_btn.pack_forget()
        else:
            self.key_entry.configure(placeholder_text="")
            self.gen_key_btn.pack_forget()

    def generate_random_key(self):
        method = self.method_var.get()
        if method == "XOR":
            key = base64.b64encode(get_random_bytes(8)).decode()[:8]
        elif method == "AES":
            key = base64.b64encode(get_random_bytes(16)).decode()[:16]
        else:
            return
        self.key_var.set(key)
        messagebox.showinfo(
            "Сгенерирован ключ",
            f"Сгенерирован ключ: {key}\n\n"
            "⚠️ ОБЯЗАТЕЛЬНО сохраните его в надёжном месте!\n"
            "Без этого ключа расшифровать текст будет невозможно."
        )

    def copy_text(self, widget):
        try:
            if isinstance(widget, ctk.CTkTextbox):
                text = widget.get("1.0", tk.END).strip()
            else:  # Для стандартного Text
                text = widget.get("1.0", tk.END).strip()
            if text:
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                messagebox.showinfo("Успех", "Текст скопирован в буфер обмена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать: {e}")

    def paste_text(self, widget):
        try:
            text = self.root.clipboard_get()
            if text:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить: {e}")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.current_file = file_path
                self.file_label.configure(text=f"Файл: {os.path.basename(file_path)}")
                self.output_text.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def save_result(self):
        result = self.output_text.get("1.0", tk.END).strip()
        if not result:
            messagebox.showerror("Ошибка", "Нет результата для сохранения!")
            return

        if self.current_file:
            save_path = self.current_file
        else:
            save_path = filedialog.asksaveasfilename(
                title="Сохранить результат",
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
            )

        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(result)
                messagebox.showinfo("Успех", f"Результат сохранён в:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def encrypt(self):
        method = self.method_var.get()
        key = self.key_var.get()
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите текст для шифрования!")
            return
        if method in ["XOR", "AES"] and not key:
            messagebox.showerror("Ошибка", "Для этого метода требуется ключ!")
            return
        try:
            result = self.apply_cipher(text, method, key, encrypt=True)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", result)
            self.add_to_history(method, key, text, result, "Зашифровано")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось зашифровать: {e}")

    def decrypt(self):
        method = self.method_var.get()
        key = self.key_var.get()
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите текст для расшифрования!")
            return
        if method in ["XOR", "AES"] and not key:
            messagebox.showerror("Ошибка", "Для этого метода требуется ключ!")
            return
        try:
            result = self.apply_cipher(text, method, key, encrypt=False)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", result)
            self.add_to_history(method, key, text, result, "Расшифровано")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось расшифровать: {e}")

    def apply_cipher(self, text, method, key, encrypt):
        if method == "Цезарь":
            return self.caesar_cipher(text, int(key), encrypt)
        elif method == "Перестановка":
            return self.transposition_cipher(text, encrypt)
        elif method == "XOR":
            return self.xor_cipher(text, key, encrypt)
        elif method == "Base64":
            return self.base64_cipher(text, encrypt)
        elif method == "AES":
            return self.aes_cipher(text, key.ljust(16)[:16], encrypt)
        else:
            raise ValueError("Неизвестный метод")

    def caesar_cipher(self, text, shift, encrypt):
        result = []
        shift_amount = shift if encrypt else -shift
        for char in text:
            if 'а' <= char.lower() <= 'я':
                base = ord('а') if char.islower() else ord('А')
                new_char = chr((ord(char) - base + shift_amount) % 32 + base)
                result.append(new_char)
            elif 'a' <= char.lower() <= 'z':
                base = ord('a') if char.islower() else ord('A')
                new_char = chr((ord(char) - base + shift_amount) % 26 + base)
                result.append(new_char)
            else:
                result.append(char)
        return ''.join(result)

    def transposition_cipher(self, text, encrypt):
        return text[::-1] if encrypt else text[::-1]

    def xor_cipher(self, text, key, encrypt):
        return ''.join([chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text)])

    def base64_cipher(self, text, encrypt):
        if encrypt:
            return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        else:
            return base64.b64decode(text.encode('utf-8')).decode('utf-8')

    def aes_cipher(self, text, key, encrypt):
        cipher = AES.new(key.encode('utf-8'), AES.MODE_EAX)
        if encrypt:
            ciphertext, tag = cipher.encrypt_and_digest(text.encode('utf-8'))
            return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')
        else:
            data = base64.b64decode(text.encode('utf-8'))
            nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
            cipher = AES.new(key.encode('utf-8'), AES.MODE_EAX, nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

    def add_to_history(self, method, key, input_text, output_text, action):
        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": method,
            "key": key,
            "input": input_text,
            "output": output_text,
            "action": action
        })
        self.save_history()

    def save_history(self):
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_history(self):
        if os.path.exists("history.json"):
            with open("history.json", "r", encoding="utf-8") as f:
                self.history = json.load(f)

if __name__ == "__main__":
    root = ctk.CTk()
    app = RecipeCipherApp(root)
    root.mainloop()