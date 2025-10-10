import string
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
    def __init__(self, rotors, reflector):
        self.rotors = rotors
        self.reflector = reflector

    def encode_letter(self, c):
        if c not in ENG_ALPHABET:
            return c

        rotate_next = self.rotors[0].step()
        if rotate_next:
            rotate_next = self.rotors[1].step()
            if rotate_next:
                self.rotors[2].step()

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

# ======== CLI INTERFACE ======== #
def get_language():
    while True:
        print("\nВыберите язык алфавита:")
        print("1. Славянский (кириллица)")
        print("2. Английский (латиница)")
        choice = input("Введите номер (1 или 2): ").strip()
        if choice == "1":
            return "RUS", SLAV_ALPHABET
        elif choice == "2":
            return "ENG", ENG_ALPHABET
        else:
            print("Ошибка: выберите 1 или 2.")

def get_cipher(lang):
    if lang == "RUS":
        while True:
            print("\nВыберите шифр:")
            print("1. Цезарь")
            print("2. Полибий")
            print("3. Виженер")
            print("4. Атбаш")
            choice = input("Введите номер (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return ["Caesar", "Polybius", "Vigenere", "Atbash"][int(choice) - 1]
            else:
                print("Ошибка: выберите число от 1 до 4.")
    else:
        return "Enigma"

def get_operation():
    while True:
        print("\nВыберите действие:")
        print("1. Зашифровать")
        print("2. Расшифровать")
        choice = input("Введите номер (1 или 2): ").strip()
        if choice in ["1", "2"]:
            return "encrypt" if choice == "1" else "decrypt"
        else:
            print("Ошибка: выберите 1 или 2.")

def get_shift():
    while True:
        try:
            shift = int(input("Введите смещение (целое число): ").strip())
            return shift
        except ValueError:
            print("Ошибка: смещение должно быть целым числом.")

def get_key(alphabet):
    while True:
        key = input("Введите ключ: ").strip()
        if key:
            return key
        print("Ошибка: ключ не может быть пустым.")

def get_rotor_settings():
    rotors = []
    available_rotors = list(ROTOR_CONFIGS.keys())
    print("\nВыберите роторы (I, II, III, IV, V).")
    for i in range(3):
        while True:
            print(f"\nДоступные роторы: {', '.join(available_rotors)}")
            rotor = input(f"Выберите ротор {i+1} (введите I, II, III, IV или V): ").strip().upper()
            if rotor in available_rotors:
                available_rotors.remove(rotor)  # Prevent reusing the same rotor
                break
            print("Ошибка: выберите доступный ротор.")
        
        while True:
            pos = input(f"Введите начальную позицию для ротора {rotor} (A-Z): ").strip().upper()
            if pos in ENG_ALPHABET:
                wiring, notch = ROTOR_CONFIGS[rotor]
                rotors.append(Rotor(wiring, notch, ENG_ALPHABET.index(pos)))
                break
            print("Ошибка: позиция должна быть буквой от A до Z.")
    return rotors

def main():
    print("=== Многофункциональный шифратор ===")
    while True:
        # Get language and alphabet
        lang, alphabet = get_language()
        
        # Get cipher
        cipher = get_cipher(lang)
        
        # Get operation
        operation = get_operation()
        
        # Get cipher-specific parameters
        if lang == "RUS" and cipher == "Caesar" and operation == "encrypt":
            shift = get_shift()
        elif lang == "RUS" and cipher == "Vigenere":
            key = get_key(alphabet)
        elif lang == "ENG":
            rotors = get_rotor_settings()
        
        # Get input text
        text = input("\nВведите текст: ").strip()
        if not text:
            print("Ошибка: текст не может быть пустым.")
            continue
        
        # Process the text
        result = ""
        try:
            if lang == "RUS":
                if cipher == "Caesar":
                    result = caesar_cipher(text, shift, alphabet) if operation == "encrypt" else caesar_decipher(text, shift, alphabet)
                elif cipher == "Polybius":
                    result = polybius_cipher(text, alphabet) if operation == "encrypt" else polybius_decipher(text, alphabet)
                elif cipher == "Vigenere":
                    result = vigenere_cipher(text, key, alphabet) if operation == "encrypt" else vigenere_decipher(text, key, alphabet)
                elif cipher == "Atbash":
                    result = atbash_cipher(text, alphabet)  # Atbash is symmetric
            else:
                enigma = EnigmaMachine(rotors, REFLECTOR_B)
                result = enigma.encode_message(text)  # Enigma is symmetric
        except Exception as e:
            print(f"Ошибка обработки: {e}")
            continue
        
        # Display result
        print("\nРезультат:")
        print(result)
        
        # Ask to continue
        again = input("\nПродолжить? (да/нет): ").strip().lower()
        if again not in ["да", "y", "yes"]:
            break

if __name__ == "__main__":
    main()