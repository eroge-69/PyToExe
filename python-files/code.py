def encrypt(message, shift):
    encrypted_message = ""
    for char in message:
        if char.isalpha():  # Проверяем, является ли символ буквой
            shift_base = ord('A') if char.isupper() else ord('a')
            encrypted_message += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_message += char  # Не изменяем символы, которые не являются буквами
    return encrypted_message

def decrypt(encrypted_message, shift):
    return encrypt(encrypted_message, -shift)  # Дешифрование — это просто шифрование с отрицательным сдвигом

def main():
    choice = input("Выберите действие (1: Шифровать, 2: Дешифровать): ")
    message = input("Введите сообщение: ")
    shift = int(input("Введите сдвиг (число): "))

    if choice == '1':
        encrypted = encrypt(message, shift)
        print(f"Зашифрованное сообщение: {encrypted}")
    elif choice == '2':
        decrypted = decrypt(message, shift)
        print(f"Расшифрованное сообщение: {decrypted}")
    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()
