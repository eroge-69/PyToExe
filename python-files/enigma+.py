import string
import tkinter as tk
from tkinter import ttk, messagebox
import itertools

# ======== АЛФАВИТЫ ======== #
SLAV_ALPHABET = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЁ"
ENG_ALPHABET = string.ascii_uppercase

# ======== ЦЕЗАРЬ ======== #
def caesar_cipher(text, shift, alphabet):
    result = ""
    text = text.upper()
    for c in text:
        if c in alphabet:
            idx = (alphabet.index(c) + shift) % len(alphabet)
            result += alphabet[idx]
        else:
            result += c
    return result

def caesar_decipher(text, shift, alphabet):
    return caesar_cipher(text, -shift, alphabet)

# ======== ПОЛІБІЙ ======== #
def polybius_cipher(text, alphabet):
    text = text.upper()
    size = 6
    table = [alphabet[i:i+size] for i in range(0, len(alphabet), size)]
    result = ""
    for c in text:
        found = False
        for i, row in enumerate(table):
            if c in row:
                result += f"{i+1}{row.index(c)+1} "
                found = True
                break
        if not found:
            result += c
    return result.strip()

def polybius_decipher(text, alphabet):
    size = 6
    table = [alphabet[i:i+size] for i in range(0, len(alphabet), size)]
    parts = text.split()
    result = ""
    for p in parts:
        if len(p) == 2 and p.isdigit():
            row, col = int(p[0]) - 1, int(p[1]) - 1
            if 0 <= row < len(table) and 0 <= col < len(table[row]):
                result += table[row][col]
            else:
                result += "?"
        else:
            result += p
    return result

# ======== ВИЖЕНЕР ======== #
def vigenere_cipher(text, key, alphabet):
    result = ""
    text = text.upper()
    key = key.upper()
    key_indices = [alphabet.index(k) for k in key if k in alphabet]
    ki = 0
    for c in text:
        if c in alphabet:
            shift = key_indices[ki % len(key_indices)]
            idx = (alphabet.index(c) + shift) % len(alphabet)
            result += alphabet[idx]
            ki += 1
        else:
            result += c
    return result

def vigenere_decipher(text, key, alphabet):
    result = ""
    text = text.upper()
    key = key.upper()
    key_indices = [alphabet.index(k) for k in key if k in alphabet]
    ki = 0
    for c in text:
        if c in alphabet:
            shift = key_indices[ki % len(key_indices)]
            idx = (alphabet.index(c) - shift) % len(alphabet)
            result += alphabet[idx]
            ki += 1
        else:
            result += c
    return result

# ======== АТБАШ ======== #
def atbash_cipher(text, alphabet):
    return "".join(alphabet[::-1][alphabet.index(c)] if c in alphabet else c for c in text.upper())

# ======== ЭНИГМА ======== #
class Rotor:
    def __init__(self, wiring, notch, position=0):
        self.wiring = wiring
        self.notch = notch
        self.position = position

    def encode_forward(self, c):
        idx = (ENG_ALPHABET.index(c) + self.position) % 26
        encoded = self.wiring[idx]
        return ENG_ALPHABET[(ENG_ALPHABET.index(encoded) - self.position) % 26]

    def encode_backward(self, c):
        idx = (ENG_ALPHABET.index(c) + self.position) % 26
        encoded = ENG_ALPHABET[self.wiring.index(ENG_ALPHABET[idx])]
        return ENG_ALPHABET[(ENG_ALPHABET.index(encoded) - self.position) % 26]

    def step(self):
        self.position = (self.position + 1) % 26
        return self.position == self.notch

class Reflector:
    def __init__(self, wiring):
        self.wiring = wiring

    def reflect(self, c):
        return self.wiring[ENG_ALPHABET.index(c)]

class EnigmaMachine:
    def __init__(self, rotors, reflector, anim_callback=None):
        self.rotors = rotors
        self.reflector = reflector
        self.anim_callback = anim_callback

    def encode_letter(self, c):
        if c not in ENG_ALPHABET:
            return c

        rotate_next = self.rotors[0].step()
        if self.anim_callback:
            self.anim_callback(self.rotors)
        if rotate_next:
            rotate_next = self.rotors[1].step()
            if self.anim_callback:
                self.anim_callback(self.rotors)
            if rotate_next:
                self.rotors[2].step()
                if self.anim_callback:
                    self.anim_callback(self.rotors)

        for rotor in self.rotors:
            c = rotor.encode_forward(c)
        c = self.reflector.reflect(c)
        for rotor in reversed(self.rotors):
            c = rotor.encode_backward(c)
        return c

    def encode_message(self, message):
        message = message.upper().replace(" ", "")
        return "".join(self.encode_letter(c) for c in message)

# ======== РОТОРЫ ======== #
ROTOR_CONFIGS = {
    "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", 17),
    "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", 5),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", 22),
    "IV": ("ESOVPZJAYQUIRHXLNFTGKDCMWB", 10),
    "V": ("VZBRGITYUPSDNHLXAWMJQOFECK", 25),
}
REFLECTOR_B = Reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT")

# ======== GUI ======== #
class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Многофункциональный шифратор")
        self.root.geometry("700x750")
        self.root.configure(bg="#20232a")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#20232a", foreground="white", font=("Segoe UI", 10))
        style.configure("TButton", background="#3a3f47", foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "#4e5969")])
        style.configure("TFrame", background="#20232a")

        ttk.Label(root, text="🔐 Универсальный шифратор", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Язык
        lang_frame = ttk.Frame(root)
        lang_frame.pack(pady=5)
        self.lang_var = tk.StringVar(value="RUS")
        ttk.Label(lang_frame, text="Язык:").pack(side="left", padx=5)
        ttk.Radiobutton(lang_frame, text="Славянский", variable=self.lang_var, value="RUS", command=self.update_ui).pack(side="left", padx=5)
        ttk.Radiobutton(lang_frame, text="Английский", variable=self.lang_var, value="ENG", command=self.update_ui).pack(side="left", padx=5)

        # Шифр
        self.cipher_frame = ttk.Frame(root)
        self.cipher_frame.pack(pady=5)
        ttk.Label(self.cipher_frame, text="Шифр:").pack(side="left")
        self.cipher_var = tk.StringVar(value="Caesar")
        self.cipher_box = ttk.Combobox(self.cipher_frame, textvariable=self.cipher_var,
                                       values=["Caesar", "Polybius", "Vigenere", "Atbash"], state="readonly", width=10)
        self.cipher_box.pack(side="left", padx=5)
        self.cipher_box.bind("<<ComboboxSelected>>", lambda e: self.update_ui())

        # Смещение для Цезаря
        self.shift_frame = ttk.Frame(root)
        ttk.Label(self.shift_frame, text="Смещение:").pack(side="left")
        self.shift_entry = ttk.Entry(self.shift_frame, width=5, justify="center")
        self.shift_entry.insert(0, "3")
        self.shift_entry.pack(side="left", padx=5)

        # Ключ для Виженера
        self.key_frame = ttk.Frame(root)
        ttk.Label(self.key_frame, text="Ключ:").pack(side="left")
        self.key_entry = ttk.Entry(self.key_frame, width=15, justify="center")
        self.key_entry.pack(side="left", padx=5)

        # Роторы для Энигмы
        self.rotor_frame = ttk.Frame(root)
        ttk.Label(self.rotor_frame, text="Роторы (слева направо):").pack()
        rotor_sel = ttk.Frame(self.rotor_frame)
        rotor_sel.pack(pady=5)
        self.rotor_vars = [tk.StringVar(value="I"), tk.StringVar(value="II"), tk.StringVar(value="III")]
        for var in self.rotor_vars:
            ttk.Combobox(rotor_sel, textvariable=var, values=list(ROTOR_CONFIGS.keys()), width=5, state="readonly").pack(side="left", padx=5)
        ttk.Label(self.rotor_frame, text="Начальные позиции (A-Z):").pack(pady=3)
        pos_frame = ttk.Frame(self.rotor_frame)
        pos_frame.pack(pady=5)
        self.pos_vars = [tk.StringVar(value="A"), tk.StringVar(value="A"), tk.StringVar(value="A")]
        for var in self.pos_vars:
            ttk.Entry(pos_frame, textvariable=var, width=5, justify="center").pack(side="left", padx=5)

        # Анимация роторов
        self.anim_labels = [ttk.Label(root, text="Ротор 1: A", font=("Consolas", 10), foreground="#00ffae"),
                            ttk.Label(root, text="Ротор 2: A", font=("Consolas", 10), foreground="#00ffae"),
                            ttk.Label(root, text="Ротор 3: A", font=("Consolas", 10), foreground="#00ffae")]

        # Ввод текста
        ttk.Label(root, text="Введите текст:").pack(pady=5)
        self.input_text = tk.Text(root, height=5, width=75, bg="#2a2f38", fg="white", insertbackground="white", relief="flat", font=("Consolas", 10))
        self.input_text.pack(pady=5)
        # Кнопки для ввода
        input_btn_frame = ttk.Frame(root)
        input_btn_frame.pack(pady=5)
        ttk.Button(input_btn_frame, text="📋 Копировать ввод", command=self.copy_input).pack(side="left", padx=5)
        ttk.Button(input_btn_frame, text="📋 Вставить в ввод", command=self.paste_input).pack(side="left", padx=5)

        # Кнопки шифрования/расшифрования
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🔒 Зашифровать", command=self.encrypt).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🔓 Расшифровать", command=self.decrypt).pack(side="left", padx=10)

        # Результат
        ttk.Label(root, text="Результат:").pack(pady=5)
        self.output_text = tk.Text(root, height=6, width=75, bg="#1e2229", fg="#00ffae", insertbackground="white", relief="flat", font=("Consolas", 10))
        self.output_text.pack(pady=5)
        # Кнопки для вывода
        output_btn_frame = ttk.Frame(root)
        output_btn_frame.pack(pady=5)
        ttk.Button(output_btn_frame, text="📋 Копировать результат", command=self.copy_output).pack(side="left", padx=5)
        ttk.Button(output_btn_frame, text="📋 Вставить в результат", command=self.paste_output).pack(side="left", padx=5)

        self.update_ui()

    def update_ui(self):
        self.cipher_frame.pack_forget()
        self.shift_frame.pack_forget()
        self.key_frame.pack_forget()
        self.rotor_frame.pack_forget()
        for lbl in self.anim_labels:
            lbl.pack_forget()

        if self.lang_var.get() == "RUS":
            self.cipher_frame.pack(pady=5)
            if self.cipher_var.get() == "Caesar":
                self.shift_frame.pack(pady=5)
            elif self.cipher_var.get() == "Vigenere":
                self.key_frame.pack(pady=5)
        else:
            self.rotor_frame.pack(pady=5)
            for lbl in self.anim_labels:
                lbl.pack()

    def copy_input(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if text:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.root.update()  # Ensure clipboard is updated
                messagebox.showinfo("Успех", "Текст ввода скопирован в буфер обмена!")
            except tk.TclError:
                messagebox.showerror("Ошибка", "Не удалось скопировать текст в буфер обмена!")
        else:
            messagebox.showwarning("Ошибка", "Поле ввода пустое!")

    def copy_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.root.update()  # Ensure clipboard is updated
                messagebox.showinfo("Успех", "Текст результата скопирован в буфер обмена!")
            except tk.TclError:
                messagebox.showerror("Ошибка", "Не удалось скопировать текст в буфер обмена!")
        else:
            messagebox.showwarning("Ошибка", "Поле результата пустое!")

    def paste_input(self):
        try:
            text = self.root.clipboard_get()
            if text:
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, text)
                messagebox.showinfo("Успех", "Текст вставлен в поле ввода!")
            else:
                messagebox.showwarning("Ошибка", "Буфер обмена пуст!")
        except tk.TclError:
            messagebox.showerror("Ошибка", "Не удалось получить текст из буфера обмена!")

    def paste_output(self):
        try:
            text = self.root.clipboard_get()
            if text:
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert(tk.END, text)
                messagebox.showinfo("Успех", "Текст вставлен в поле результата!")
            else:
                messagebox.showwarning("Ошибка", "Буфер обмена пуст!")
        except tk.TclError:
            messagebox.showerror("Ошибка", "Не удалось получить текст из буфера обмена!")

    def animate_rotors(self, rotors):
        for i, rotor in enumerate(rotors):
            self.anim_labels[i].config(text=f"Ротор {i+1}: {ENG_ALPHABET[rotor.position]}")
        self.root.update_idletasks()

    def encrypt(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Ошибка", "Введите текст!")
            return
        result = ""
        if self.lang_var.get() == "RUS":
            if self.cipher_var.get() == "Caesar":
                try:
                    shift = int(self.shift_entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Смещение должно быть числом")
                    return
                result = caesar_cipher(text, shift, SLAV_ALPHABET)
            elif self.cipher_var.get() == "Polybius":
                result = polybius_cipher(text, SLAV_ALPHABET)
            elif self.cipher_var.get() == "Vigenere":
                key = self.key_entry.get()
                if not key:
                    messagebox.showerror("Ошибка", "Введите ключ для Виженера")
                    return
                result = vigenere_cipher(text, key, SLAV_ALPHABET)
            elif self.cipher_var.get() == "Atbash":
                result = atbash_cipher(text, SLAV_ALPHABET)
        else:
            rotors = []
            for i in range(3):
                try:
                    wiring, notch = ROTOR_CONFIGS[self.rotor_vars[i].get()]
                    pos = ENG_ALPHABET.index(self.pos_vars[i].get().upper())
                    rotors.append(Rotor(wiring, notch, pos))
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверная начальная позиция ротора!")
                    return
            enigma = EnigmaMachine(rotors, REFLECTOR_B, anim_callback=self.animate_rotors)
            result = enigma.encode_message(text)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)

    def decrypt(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Ошибка", "Введите текст!")
            return

        if self.lang_var.get() == "RUS":
            cipher = self.cipher_var.get()
            if cipher == "Caesar":
                try:
                    shift = int(self.shift_entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Смещение должно быть числом")
                    return
                result = caesar_decipher(text, shift, SLAV_ALPHABET)
            elif cipher == "Polybius":
                result = polybius_decipher(text, SLAV_ALPHABET)
            elif cipher == "Vigenere":
                key = self.key_entry.get()
                if not key:
                    messagebox.showerror("Ошибка", "Введите ключ")
                    return
                result = vigenere_decipher(text, key, SLAV_ALPHABET)
            elif cipher == "Atbash":
                result = atbash_cipher(text, SLAV_ALPHABET)
        else:
            # Enigma симметрична: шифруем снова
            self.encrypt()
            return

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)


# ======== ЗАПУСК ======== #
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CipherApp(root)
        root.mainloop()
    except tk.TclError as e:
        print(f"Ошибка инициализации Tkinter: {e}")
        print("Убедитесь, что Tkinter установлен и работает корректно.")