# caesar.py
def encrypt(text: str, shift: int) -> str:
    """Шифрует текст с помощью шифра Цезаря"""
    result = []
    for char in text:
        if char.isalpha():
            # Определяем базовый символ в зависимости от регистра
            base = ord('А') if char.isupper() else ord('а')
            # Выполняем циклический сдвиг
            shifted_char = chr((ord(char) - base + shift) % 32 + base)
            result.append(shifted_char)
        else:
            # Не-буквенные символы остаются без изменений
            result.append(char)
    return ''.join(result)


def decrypt(text: str, shift: int) -> str:
    """Дешифрует текст, зашифрованный шифром Цезаря"""
    return encrypt(text, -shift)


def main():
    print("Шифр Цезаря")
    while True:
        print("\nВыберите действие:")
        print("1 - Шифрование")
        print("2 - Дешифрование")
        print("3 - Выход")

        choice = input("Введите номер действия: ").strip()

        if choice == '1':
            text = input("Введите текст для шифрования: ")
            try:
                shift = int(input("Введите ключ (сдвиг): "))
                encrypted = encrypt(text, shift)
                print(f"Зашифрованный текст: {encrypted}")
            except ValueError:
                print("Ошибка: ключ должен быть целым числом")

        elif choice == '2':
            text = input("Введите текст для дешифрования: ")
            try:
                shift = int(input("Введите ключ (сдвиг): "))
                decrypted = decrypt(text, shift)
                print(f"Расшифрованный текст: {decrypted}")
            except ValueError:
                print("Ошибка: ключ должен быть целым числом")

        elif choice == '3':
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()