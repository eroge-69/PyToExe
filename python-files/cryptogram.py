import tkinter as tk
from tkinter import ttk, messagebox
import base64
import hashlib
import string
import random
from typing import List, Tuple
from translate import Translator

# --- Функции шифрования ---

def caesar_encrypt(text: str, shift: int, alphabet: str) -> str:
    result = ''
    for char in text:
        if char.lower() in alphabet:
            index = alphabet.index(char.lower())
            shifted_char = alphabet[(index + shift) % len(alphabet)] if char.islower() else alphabet[(index + shift) % len(alphabet)].upper()
        elif char.isdigit():
            shifted_char = str((int(char) + shift) % 10)
        else:
            shifted_char = char
        result += shifted_char
    return result

def caesar_decrypt(text: str, shift: int, alphabet: str) -> str:
    return caesar_encrypt(text, -shift, alphabet)

def base64_encrypt(text: str) -> str:
    text_bytes = text.encode('utf-8')
    encoded_bytes = base64.b64encode(text_bytes)
    return encoded_bytes.decode('utf-8')

def base64_decrypt(text: str) -> str:
    try:
        decoded_bytes = base64.b64decode(text.encode('utf-8'))
        return decoded_bytes.decode('utf-8')
    except Exception:
        return "Ошибка декодирования"

def md5_hash(text: str) -> str:
    hashed = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hashed


def voyager_encrypt(text: str, key: str, alphabet: str) -> str:
    key = key.lower()
    key_chars = sorted(list(set(key)))  # Уникальные символы ключа
    remaining_chars = [char for char in alphabet if char not in key_chars]
    mapping = key_chars + remaining_chars

    encrypted_text = ""
    for char in text.lower():
        if char in alphabet:
            index = alphabet.index(char)
            encrypted_text += mapping[index]
        else:
            encrypted_text += char  # Сохраняем пробелы и другие символы
    return encrypted_text

def voyager_decrypt(text: str, key: str, alphabet: str) -> str:
    key = key.lower()
    key_chars = sorted(list(set(key)))
    remaining_chars = [char for char in alphabet if char not in key_chars]
    mapping = key_chars + remaining_chars

    decrypted_text = ""
    for char in text.lower():
        if char in mapping:
            index = mapping.index(char)
            decrypted_text += alphabet[index]
        else:
            decrypted_text += char
    return decrypted_text


# --- Графический интерфейс ---
class CryptoApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Crypto App")
        master.geometry("600x500")  # Увеличиваем высоту
        master.resizable(False, False)
        self.font = ("Arial", 10)
        self.translator = Translator(to_lang="ru")

        # Инициализация алфавитов
        self.alphabets = {
            "english": string.ascii_lowercase,
            "russian": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
        }
        self.current_alphabet = self.alphabets["english"]  # По умолчанию английский
        self.language_var = tk.StringVar(value="english") # Определяем language_var здесь


        self.create_widgets()

    def create_widgets(self):
        # --- Вкладки ---
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- Вкладка "Шифрование/Дешифрование" ---
        self.crypto_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crypto_frame, text="Шифрование/Дешифрование")
        self.create_crypto_widgets()

        # --- Вкладка "Информация" ---
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Информация")
        self.create_info_widgets()

        # --- Вкладка "О приложении" ---
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="О приложении")
        self.create_about_widgets()

    def create_crypto_widgets(self):
        # --- Выбор языка ---
        ttk.Label(self.crypto_frame, text="Выберите язык:", font=self.font).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.language_combobox = ttk.Combobox(self.crypto_frame, textvariable=self.language_var, values=["english", "russian"], state="readonly")
        self.language_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.language_combobox.bind("<<ComboboxSelected>>", self.update_alphabets) # Binding здесь, а функция ниже


        # --- Ввод текста ---
        ttk.Label(self.crypto_frame, text="Введите текст:", font=self.font).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_text = tk.Text(self.crypto_frame, height=5, width=40, font=self.font)
        self.input_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # --- Выбор метода ---
        ttk.Label(self.crypto_frame, text="Выберите метод:", font=self.font).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.method_var = tk.StringVar(value="caesar")
        self.method_combobox = ttk.Combobox(self.crypto_frame, textvariable=self.method_var, values=["caesar", "base64", "md5", "voyager"])
        self.method_combobox.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.method_combobox.bind("<<ComboboxSelected>>", self.update_method_options)

        # --- Параметры метода (сдвиг для Caesar, ключ для Voyager) ---
        self.option_frame = ttk.Frame(self.crypto_frame)
        self.option_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.option_label = ttk.Label(self.option_frame, text="Сдвиг (для Caesar):", font=self.font)
        self.option_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.option_entry = ttk.Entry(self.option_frame, width=5, font=self.font)
        self.option_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.update_method_options()

        # --- Кнопки ---
        self.encrypt_button = ttk.Button(self.crypto_frame, text="Зашифровать", command=self.encrypt, width=15, style="TButton")
        self.encrypt_button.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        self.decrypt_button = ttk.Button(self.crypto_frame, text="Расшифровать", command=self.decrypt, width=15, style="TButton")
        self.decrypt_button.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

        # --- Вывод текста ---
        ttk.Label(self.crypto_frame, text="Результат:", font=self.font).grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_text = tk.Text(self.crypto_frame, height=5, width=40, font=self.font)
        self.output_text.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        # --- Настройка стилей ---
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white", font=self.font)
        style.map("TButton", background=[("active", "#388E3C")])


    def create_info_widgets(self):
        # --- Выбор метода для информации ---
        ttk.Label(self.info_frame, text="Выберите метод:", font=self.font).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.info_method_var = tk.StringVar(value="caesar")
        self.info_method_combobox = ttk.Combobox(self.info_frame, textvariable=self.info_method_var, values=["caesar", "base64", "md5", "voyager"], state="readonly")
        self.info_method_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # --- Кнопка для отображения информации ---
        self.show_info_button = ttk.Button(self.info_frame, text="Показать информацию", command=self.show_method_info, width=20, style="TButton")
        self.show_info_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # --- Текстовое поле для отображения информации ---
        self.info_text = tk.Text(self.info_frame, height=10, width=50, font=self.font)
        self.info_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.info_text.config(state=tk.DISABLED)  # Заблокировано для редактирования

    def show_method_info(self):
        """Отображает информацию о выбранном методе шифрования."""
        method = self.info_method_var.get()
        info = ""

        if method == "caesar":
            info = (
                "Шифр Цезаря (или шифр сдвига) — один из самых простых и известных методов шифрования.\n"
                "Это вид шифра подстановки, в котором каждый символ в открытом тексте заменяется символом,\n"
                "находящимся на некотором постоянном числе позиций дальше в алфавите.\n"
                "Шифр Цезаря часто используется как часть более сложных схем."
            )
        elif method == "base64":
            info = (
                "Base64 — это общее обозначение для нескольких подобных схем кодирования, которые кодируют двоичные данные,\n"
                "преобразуя их в строковое представление ASCII. Термин Base64 происходит от конкретной кодировки MIME,\n"
                "в которой для представления данных используются символы ASCII A-Z, a-z, 0-9 и + /."
            )
        elif method == "md5":
            info = (
                "MD5 (Message Digest Algorithm 5) — это широко используемая криптографическая хеш-функция,\n"
                "которая производит 128-битное хеш-значение. MD5 использовался в самых разных приложениях безопасности,\n"
                "а также обычно использовался для проверки целостности данных. Однако MD5 больше не считается\n"
                "криптографически безопасным для использования в дальнейшем."
            )
        elif method == "voyager":
            info = (
                "Шифр Voyager — это простой демонстрационный шифр подстановки, который в этом приложении\n"
                "использует ключ для перестановки алфавита. Важно отметить, что этот шифр не является\n"
                "криптографически безопасным и не должен использоваться для каких-либо целей, требующих реальной безопасности."
            )
        else:
            info = "Информация недоступна."

        self.info_text.config(state=tk.NORMAL)  # Разблокируем
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", info)
        self.info_text.config(state=tk.DISABLED)  # Снова блокируем

    def create_about_widgets(self):
        about_text = (
            "Это приложение для шифрования и дешифрования.\n"
            "Поддерживаемые методы:\n"
            "- Caesar (сдвиг)\n"
            "- Base64\n"
            "- MD5 (хеширование)\n"
            "- Voyager (простой метод, не является криптографически безопасным)\n"
            "\n"
            "Поддержка языков: Русский, Английский\n"
            "\n"
            "Автор: [Ваше имя]\n"
            "Версия: 1.3"
        )
        ttk.Label(self.about_frame, text=about_text, wraplength=500, justify="left", font=self.font).pack(padx=10, pady=10)


    def update_method_options(self, event=None):
        method = self.method_var.get()
        if method == "caesar":
            self.option_label.config(text="Сдвиг:")
            self.option_entry.delete(0, tk.END)
            self.option_entry.insert(0, "3")
            self.option_entry.config(state="normal")
        elif method == "voyager":
            self.option_label.config(text="Ключ:")
            self.option_entry.delete(0, tk.END)
            self.option_entry.insert(0, "voyager")
            self.option_entry.config(state="normal")
        else:
            self.option_label.config(text="")
            self.option_entry.delete(0, tk.END)
            self.option_entry.config(state="disabled")

    def update_alphabets(self, event=None):
        """Обновляет текущий алфавит в зависимости от выбранного языка."""
        selected_language = self.language_var.get()
        if selected_language in self.alphabets:
            self.current_alphabet = self.alphabets[selected_language]
        else:
            self.current_alphabet = string.ascii_lowercase  # Fallback

    def get_input_text(self) -> str:
        return self.input_text.get("1.0", tk.END).strip()

    def set_output_text(self, text: str):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def translate_text(self, text: str, target_language: str) -> str:
        try:
            translator = Translator(to_lang=target_language)
            translation = translator.translate(text)
            return translation
        except Exception as e:
            messagebox.showerror("Ошибка перевода", f"Ошибка перевода: {e}")
            return text

    def encrypt(self):
        text = self.get_input_text()
        method = self.method_var.get()
        output = ""
        selected_language = self.language_var.get()

        try:
            if selected_language == "russian" and method != "base64" and method != "md5":
                translated_text = self.translate_text(text, 'ru')
                text = translated_text

            if method == "caesar":
                shift = int(self.option_entry.get())
                if selected_language == "russian":
                    alphabet = self.alphabets["russian"]
                else:
                    alphabet = self.alphabets["english"]

                output = caesar_encrypt(text, shift, alphabet)
            elif method == "base64":
                output = base64_encrypt(text)
            elif method == "md5":
                output = md5_hash(text)
            elif method == "voyager":
                key = self.option_entry.get()
                if selected_language == "russian":
                    alphabet = self.alphabets["russian"]
                else:
                    alphabet = self.alphabets["english"]
                output = voyager_encrypt(text, key, alphabet)
            else:
                output = "Неизвестный метод"

            if selected_language == "russian" and method != "base64" and method != "md5":
                output = self.translate_text(output, 'en')

        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат ввода для параметров.")
            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при шифровании: {e}")
            return

        self.set_output_text(output)


    def decrypt(self):
        text = self.get_input_text()
        method = self.method_var.get()
        output = ""
        selected_language = self.language_var.get()

        try:
            if selected_language == "russian" and method != "base64" and method != "md5":
                translated_text = self.translate_text(text, 'en')
                text = translated_text

            if method == "caesar":
                shift = int(self.option_entry.get())
                if selected_language == "russian":
                    alphabet = self.alphabets["russian"]
                else:
                    alphabet = self.alphabets["english"]
                output = caesar_decrypt(text, shift, alphabet)
            elif method == "base64":
                output = base64_decrypt(text)
            elif method == "md5":
                output = "MD5 - это хеш-функция, дешифрование невозможно."
            elif method == "voyager":
                key = self.option_entry.get()
                if selected_language == "russian":
                    alphabet = self.alphabets["russian"]
                else:
                    alphabet = self.alphabets["english"]
                output = voyager_decrypt(text, key, alphabet)
            else:
                output = "Неизвестный метод"

            if selected_language == "russian" and method != "base64" and method != "md5":
                output = self.translate_text(output, 'ru')
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат ввода для параметров.")
            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при дешифровании: {e}")
            return

        self.set_output_text(output)

# --- Запуск приложения ---
root = tk.Tk()
app = CryptoApp(root)
root.mainloop()
