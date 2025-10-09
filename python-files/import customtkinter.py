import customtkinter
from tkinter import messagebox, filedialog
import math
import os

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")

ALPHABET_FULL = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ALPHABET_LEN = len(ALPHABET_FULL)

PLAYFAIR_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" + "123"
PLAYFAIR_LEN = len(PLAYFAIR_ALPHABET)
PLAYFAIR_SIZE = int(math.sqrt(PLAYFAIR_LEN))


def caesar_encrypt_ru(text, shift):
    encrypted_text = ""
    for char in text:
        upper_char = char.upper()
        if upper_char in ALPHABET_FULL:
            idx = ALPHABET_FULL.find(upper_char)
            new_idx = (idx + shift) % ALPHABET_LEN
            new_char = ALPHABET_FULL[new_idx]
            if char.islower():
                new_char = new_char.lower()

            encrypted_text += new_char
        else:
            encrypted_text += char
    return encrypted_text


def caesar_decrypt_ru(text, shift):
    return caesar_encrypt_ru(text, -shift)


def vigenere_encrypt_ru(text, key):
    encrypted_text = ""
    key = key.upper()
    key_len = len(key)
    j = 0
    for char in text:
        upper_char = char.upper()
        if upper_char in ALPHABET_FULL:
            shift = ALPHABET_FULL.find(key[j % key_len])
            idx = ALPHABET_FULL.find(upper_char)
            new_idx = (idx + shift) % ALPHABET_LEN

            # Сохранение регистра
            new_char = ALPHABET_FULL[new_idx]
            if char.islower():
                new_char = new_char.lower()

            encrypted_text += new_char
            j += 1
        else:
            encrypted_text += char
    return encrypted_text


def vigenere_decrypt_ru(text, key):
    decrypted_text = ""
    key = key.upper()
    key_len = len(key)
    j = 0
    for char in text:
        upper_char = char.upper()
        if upper_char in ALPHABET_FULL:
            shift = ALPHABET_FULL.find(key[j % key_len])
            idx = ALPHABET_FULL.find(upper_char)
            new_idx = (idx - shift + ALPHABET_LEN) % ALPHABET_LEN

            # Сохранение регистра
            new_char = ALPHABET_FULL[new_idx]
            if char.islower():
                new_char = new_char.lower()

            decrypted_text += new_char
            j += 1
        else:
            decrypted_text += char
    return decrypted_text


def atbash_encrypt_decrypt_ru(text):
    encrypted_text = ""
    for char in text:
        upper_char = char.upper()
        if upper_char in ALPHABET_FULL:
            idx = ALPHABET_FULL.find(upper_char)
            new_idx = ALPHABET_LEN - 1 - idx
            new_char = ALPHABET_FULL[new_idx]
            if char.islower():
                new_char = new_char.lower()

            encrypted_text += new_char
        else:
            encrypted_text += char
    return encrypted_text


def vernam_encrypt_ru(text, key):
    text = "".join(c for c in text.upper() if c in ALPHABET_FULL)
    key = "".join(c for c in key.upper() if c in ALPHABET_FULL)

    if len(text) != len(key) or len(text) == 0:
        return "ERROR: Текст и ключ должны быть одинаковой длины и содержать русские буквы."

    encrypted_text = ""
    for i in range(len(text)):
        idx_text = ALPHABET_FULL.find(text[i])
        idx_key = ALPHABET_FULL.find(key[i])
        new_idx = (idx_text + idx_key) % ALPHABET_LEN
        encrypted_text += ALPHABET_FULL[new_idx]

    return encrypted_text


def vernam_decrypt_ru(text, key):
    text = "".join(c for c in text.upper() if c in ALPHABET_FULL)
    key = "".join(c for c in key.upper() if c in ALPHABET_FULL)

    if len(text) != len(key) or len(text) == 0:
        return "ERROR: Текст и ключ должны быть одинаковой длины и содержать русские буквы."

    decrypted_text = ""
    for i in range(len(text)):
        idx_text = ALPHABET_FULL.find(text[i])
        idx_key = ALPHABET_FULL.find(key[i])
        new_idx = (idx_text - idx_key + ALPHABET_LEN) % ALPHABET_LEN
        decrypted_text += ALPHABET_FULL[new_idx]

    return decrypted_text


def create_playfair_matrix(key):
    key_chars = []
    for char in key.upper():
        if char in PLAYFAIR_ALPHABET and char not in key_chars:
            key_chars.append(char)

    for char in PLAYFAIR_ALPHABET:
        if char not in key_chars:
            key_chars.append(char)

    matrix = [key_chars[i:i + PLAYFAIR_SIZE] for i in range(0, PLAYFAIR_LEN, PLAYFAIR_SIZE)]
    return matrix


def find_char_coords(matrix, char):
    for row in range(PLAYFAIR_SIZE):
        if char in matrix[row]:
            col = matrix[row].index(char)
            return row, col
    return -1, -1


def playfair_encrypt_ru(text, key):
    matrix = create_playfair_matrix(key)
    processed_text = ""
    for char in text.upper():
        if char in PLAYFAIR_ALPHABET:
            processed_text += char

    if not processed_text: return ""

    digraphs = []
    i = 0
    substitute_char = '1'
    while i < len(processed_text):
        char1 = processed_text[i]

        if i + 1 >= len(processed_text):
            digraphs.append((char1, substitute_char))
            i += 1
            continue

        char2 = processed_text[i + 1]

        if char1 == char2:
            digraphs.append((char1, substitute_char))
            i += 1
        else:
            digraphs.append((char1, char2))
            i += 2

    encrypted_text = ""
    for char1, char2 in digraphs:
        r1, c1 = find_char_coords(matrix, char1)
        r2, c2 = find_char_coords(matrix, char2)

        if r1 == r2:
            new_c1 = (c1 + 1) % PLAYFAIR_SIZE
            new_c2 = (c2 + 1) % PLAYFAIR_SIZE
            encrypted_text += matrix[r1][new_c1] + matrix[r2][new_c2]
        elif c1 == c2:
            new_r1 = (r1 + 1) % PLAYFAIR_SIZE
            new_r2 = (r2 + 1) % PLAYFAIR_SIZE
            encrypted_text += matrix[new_r1][c1] + matrix[new_r2][c2]
        else:
            encrypted_text += matrix[r1][c2] + matrix[r2][c1]

    return encrypted_text


def playfair_decrypt_ru(text, key):
    matrix = create_playfair_matrix(key)

    processed_text = "".join(c for c in text.upper() if c in PLAYFAIR_ALPHABET)

    if len(processed_text) % 2 != 0:
        return "ERROR: Зашифрованный текст должен иметь четную длину."

    digraphs = [(processed_text[i], processed_text[i + 1]) for i in range(0, len(processed_text), 2)]

    decrypted_text = ""
    for char1, char2 in digraphs:
        r1, c1 = find_char_coords(matrix, char1)
        r2, c2 = find_char_coords(matrix, char2)

        if r1 == r2:
            new_c1 = (c1 - 1 + PLAYFAIR_SIZE) % PLAYFAIR_SIZE
            new_c2 = (c2 - 1 + PLAYFAIR_SIZE) % PLAYFAIR_SIZE
            decrypted_text += matrix[r1][new_c1] + matrix[r2][new_c2]
        elif c1 == c2:
            new_r1 = (r1 - 1 + PLAYFAIR_SIZE) % PLAYFAIR_SIZE
            new_r2 = (r2 - 1 + PLAYFAIR_SIZE) % PLAYFAIR_SIZE
            decrypted_text += matrix[new_r1][c1] + matrix[new_r2][c2]
        else:
            decrypted_text += matrix[r1][c2] + matrix[r2][c1]

    # Попытка удалить подстановочный символ '1' в конце, если он был добавлен при шифровании
    # В реальном Playfair это сложнее, но для простого демо-кода можно так
    # Проблема: '1' может быть частью оригинального текста. Это упрощение.
    if decrypted_text.endswith('1'):
        decrypted_text = decrypted_text[:-1]

    return decrypted_text


class CryptoApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Шифратор (русский алфавит)")
        self.geometry("650x750")

        self.new_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkScrollableFrame(self, label_text="Панель управления шифрованием")
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.main_frame.grid_columnconfigure(0, weight=1)

        # Frame for all top buttons (Info, Read File)
        self.top_buttons_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_buttons_frame.pack(pady=(10, 5), fill="x", padx=10)
        self.top_buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.open_window_button = customtkinter.CTkButton(self.top_buttons_frame, text="Дополнительная информация",
                                                          command=self.open_new_window)
        self.open_window_button.grid(row=0, column=0, padx=5, sticky="ew")

        # New button for file reading
        self.read_file_button = customtkinter.CTkButton(self.top_buttons_frame, text="Читать TXT файл",
                                                        command=self.read_txt_file)
        self.read_file_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.title_label = customtkinter.CTkLabel(self.main_frame, text="Шифратор",
                                                  font=customtkinter.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(10, 20))

        self.method_frame = customtkinter.CTkFrame(self.main_frame)
        self.method_frame.pack(pady=10, fill="x", padx=10)

        self.method_label = customtkinter.CTkLabel(self.method_frame, text="Выберите метод:")
        self.method_label.pack(side="left", padx=(10, 5))

        self.method_var = customtkinter.StringVar(value="Цезарь")
        self.method_optionmenu = customtkinter.CTkOptionMenu(self.method_frame,
                                                             values=["Цезарь", "Виженер", "Атбаш", "Плейфер", "Вернам"],
                                                             variable=self.method_var,
                                                             command=self.update_key_info)
        self.method_optionmenu.pack(side="left", padx=5)

        self.text_label = customtkinter.CTkLabel(self.main_frame,
                                                 text="Введите текст (для шифрования или дешифрования):")
        self.text_label.pack(pady=(10, 0))
        self.text_input = customtkinter.CTkTextbox(self.main_frame, height=100, width=550)
        self.text_input.pack(pady=(0, 10))

        self.key_label = customtkinter.CTkLabel(self.main_frame, text="Введите ключ (сдвиг или слово):")
        self.key_label.pack(pady=(10, 0))
        self.key_input = customtkinter.CTkEntry(self.main_frame, width=550)
        self.key_input.pack(pady=(0, 10))

        self.key_info_label = customtkinter.CTkLabel(self.main_frame, text="", wraplength=500, justify="left",
                                                     fg_color="gray20", corner_radius=5)
        self.key_info_label.pack(pady=(0, 10), fill="x", padx=10)
        self.update_key_info("Цезарь")

        self.button_frame = customtkinter.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=10, fill="x", padx=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)  # Add column for file save button

        # Set a fixed width for all main action buttons
        button_width = 180

        self.encrypt_button = customtkinter.CTkButton(self.button_frame, text="Зашифровать",
                                                      command=self.encrypt_text, width=button_width)
        self.encrypt_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.decrypt_button = customtkinter.CTkButton(self.button_frame, text="Расшифровать",
                                                      command=self.decrypt_text, width=button_width)
        self.decrypt_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # New button for saving the result to a file
        self.save_result_button = customtkinter.CTkButton(self.button_frame, text="Сохранить в TXT",
                                                          command=self.save_result_to_file, width=button_width)
        self.save_result_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.result_frame = customtkinter.CTkFrame(self.main_frame)
        self.result_frame.pack(pady=10, fill="x")

        self.output_label = customtkinter.CTkLabel(self.result_frame, text="Результат:",
                                                   font=customtkinter.CTkFont(weight="bold"))
        self.output_label.pack(pady=(5, 0))
        self.output_textbox = customtkinter.CTkTextbox(self.result_frame, height=100, width=550, state="disabled")
        self.output_textbox.pack(pady=(0, 5))

        # Ensure Copy button has the same width as the top and bottom buttons in the grid
        self.copy_result_button = customtkinter.CTkButton(self.result_frame, text="Скопировать результат в поле текста",
                                                          command=self.copy_result_to_text_input)
        self.copy_result_button.pack(pady=(5, 10), fill="x", padx=10)

    def read_txt_file(self):
        """Открывает диалог для выбора TXT файла и вставляет его содержимое в поле ввода текста."""
        filepath = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Clear current text and insert file content
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", content)
            messagebox.showinfo("Файл прочитан", f"Содержимое файла '{os.path.basename(filepath)}' загружено.")

        except UnicodeDecodeError:
            messagebox.showerror("Ошибка чтения", "Не удалось прочитать файл. Проверьте кодировку (должна быть UTF-8).")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при чтении файла: {e}")

    def save_result_to_file(self):
        """Сохраняет содержимое поля 'Результат' в TXT файл."""
        result_text = self.output_textbox.get("1.0", "end").strip()

        if not result_text:
            messagebox.showwarning("Предупреждение", "Нет результата для сохранения.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="encrypted_text.txt"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result_text)
            messagebox.showinfo("Сохранение", f"Результат успешно сохранен в файл:\n{os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл: {e}")

    def open_new_window(self):
        if self.new_window is None or not self.new_window.winfo_exists():
            self.new_window = ToplevelWindow(self)
        else:
            self.new_window.focus()

    def copy_result_to_text_input(self):
        result_text = self.output_textbox.get("1.0", "end").strip()

        if result_text:
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", result_text)

    def update_key_info(self, choice):
        info = ""
        if choice == "Цезарь":
            info = "Ключ: целое число (сдвиг)."
            self.key_input.configure(state="normal")
        elif choice == "Виженер":
            info = "Ключ: слово из русских букв. Если короче текста, будет повторяться."
            self.key_input.configure(state="normal")
        elif choice == "Атбаш":
            info = "Ключ не требуется, это шифр замещения (инверсия алфавита)."
            self.key_input.delete(0, "end")
            self.key_input.configure(state="disabled")
        elif choice == "Плейфер":
            info = f"Ключ: слово из русских букв. Используется алфавит {PLAYFAIR_LEN} символов."
            self.key_input.configure(state="normal")
        elif choice == "Вернам":
            info = "Ключ: слово из русских букв. КЛЮЧ ДОЛЖЕН БЫТЬ ТОЙ ЖЕ ДЛИНЫ, ЧТО И ТЕКСТ (без пробелов)."
            self.key_input.configure(state="normal")

        self.key_info_label.configure(text=info)

    def display_result(self, result, operation):
        self.output_label.configure(text=f"Результат ({operation}):")
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", result)
        self.output_textbox.configure(state="disabled")

    def encrypt_text(self):
        text = self.text_input.get("1.0", "end").strip()
        key = self.key_input.get().strip()
        method = self.method_var.get()

        if not text:
            messagebox.showwarning("Ошибка", "Введите текст для шифрования.")
            return

        encrypted = ""

        try:
            if method == "Цезарь":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите сдвиг (число) для шифра Цезаря.")
                    return
                shift = int(key)
                encrypted = caesar_encrypt_ru(text, shift)

            elif method == "Виженер":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите ключ-слово для шифра Виженера.")
                    return
                if not all(c.isalpha() and c.upper() in ALPHABET_FULL for c in key.upper()):
                    messagebox.showerror("Ошибка", "Для шифра Виженера ключ должен содержать только русские буквы.")
                    return
                encrypted = vigenere_encrypt_ru(text, key)

            elif method == "Атбаш":
                encrypted = atbash_encrypt_decrypt_ru(text)

            elif method == "Вернам":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите ключ-слово для шифра Вернама.")
                    return
                text_letters = "".join(c for c in text.upper() if c in ALPHABET_FULL)
                key_letters = "".join(c for c in key.upper() if c in ALPHABET_FULL)
                if len(text_letters) != len(key_letters) or len(text_letters) == 0:
                    messagebox.showerror("Ошибка",
                                         "Для шифра Вернама: Ключ должен быть той же длины, что и текст (только русские буквы).")
                    return
                encrypted = vernam_encrypt_ru(text, key)
                if encrypted.startswith("ERROR"): raise ValueError(encrypted[6:])

            elif method == "Плейфер":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите ключ-слово для шифра Плейфера.")
                    return
                if not all(c.upper() in PLAYFAIR_ALPHABET for c in key.upper()):
                    messagebox.showerror("Ошибка",
                                         f"Для шифра Плейфера ключ должен содержать только символы из алфавита: {PLAYFAIR_ALPHABET}")
                    return
                encrypted = playfair_encrypt_ru(text, key)
                if encrypted.startswith("ERROR"): raise ValueError(encrypted[6:])

            self.display_result(encrypted, "Зашифрованный текст")

        except ValueError as e:
            messagebox.showerror("Ошибка шифрования", str(e))
        except Exception as e:
            messagebox.showerror("Неизвестная ошибка", f"Произошла ошибка: {e}")

    def decrypt_text(self):
        text = self.text_input.get("1.0", "end").strip()
        key = self.key_input.get().strip()
        method = self.method_var.get()

        if not text:
            messagebox.showwarning("Ошибка", "Введите текст для дешифрования.")
            return

        decrypted = ""

        try:
            if method == "Цезарь":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите сдвиг (число) для шифра Цезаря.")
                    return
                shift = int(key)
                decrypted = caesar_decrypt_ru(text, shift)

            elif method == "Виженер":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите ключ-слово для шифра Виженера.")
                    return
                if not all(c.isalpha() and c.upper() in ALPHABET_FULL for c in key.upper()):
                    messagebox.showerror("Ошибка", "Для шифра Виженера ключ должен содержать только русские буквы.")
                    return
                decrypted = vigenere_decrypt_ru(text, key)

            elif method == "Атбаш":
                decrypted = atbash_encrypt_decrypt_ru(text)

            elif method == "Вернам":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите ключ-слово для шифра Вернама.")
                    return
                text_letters = "".join(c for c in text.upper() if c in ALPHABET_FULL)
                key_letters = "".join(c for c in key.upper() if c in ALPHABET_FULL)
                if len(text_letters) != len(key_letters) or len(text_letters) == 0:
                    messagebox.showerror("Ошибка",
                                         "Для шифра Вернама: Ключ должен быть той же длины, что и текст (только русские буквы).")
                    return
                decrypted = vernam_decrypt_ru(text, key)
                if decrypted.startswith("ERROR"): raise ValueError(decrypted[6:])

            elif method == "Плейфер":
                if not key:
                    messagebox.showwarning("Ошибка", "Введите ключ-слово для шифра Плейфера.")
                    return
                if not all(c.upper() in PLAYFAIR_ALPHABET for c in key.upper()):
                    messagebox.showerror("Ошибка",
                                         f"Для шифра Плейфера ключ должен содержать только символы из алфавита: {PLAYFAIR_ALPHABET}")
                    return
                decrypted = playfair_decrypt_ru(text, key)
                if decrypted.startswith("ERROR"): raise ValueError(decrypted[6:])

            self.display_result(decrypted, "Расшифрованный текст")

        except ValueError as e:
            messagebox.showerror("Ошибка дешифрования", str(e))
        except Exception as e:
            messagebox.showerror("Неизвестная ошибка", f"Произошла ошибка: {e}")


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x500")
        self.title("Дополнительная информация")
        self.resizable(False, False)

        info_text = ("Данный шифратор имеет несколько методов, такие как: шифр Цезаря,"
                     " Виженера, Атбаш, Плейфер, Вернам."
                     "\n Определенный метод можно выбрать через кнопку, ниже будет указана подсказка,"
                     " какой ключ нужен для шифрования."
                     "\n Имеются кнопки 'Зашифровать' и 'Расшифровать',"
                     " после нажатия которых в окне 'Результат' будет показываться определенный ответ."
                     "\n Добавлены кнопки 'Читать TXT файл' для загрузки текста и 'Сохранить в TXT' для сохранения результата."
                     "\n Выполнили программу Маташкин Даниил и Дубовкин Влад, группы: ИСП-323т ВКСиИТ ")

        self.label = customtkinter.CTkLabel(self, text=info_text,
                                            font=customtkinter.CTkFont(size=18, weight="bold"),
                                            wraplength=460, justify="left") 
        self.label.pack(padx=20, pady=10, fill="both", expand=True)

        self.close_button = customtkinter.CTkButton(self, text="Закрыть", command=self.destroy)
        self.close_button.pack(pady=10)

        self.grab_set()


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()