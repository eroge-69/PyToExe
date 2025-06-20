def caesar_encrypt(text, shift):
    result = ""

    for char in text:
        # Шифруем только латинские буквы
        if char.isalpha():
            # Определяем базовый код (ASCII) в зависимости от регистра буквы
            base = ord('A') if char.isupper() else ord('a')
            # Сдвиг символа и преобразуем обратно в символ
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char  # Если не буква, оставляем символ без изменений

    return result

def caesar_decrypt(text, shift):
    # Дешифрование проводится с тем же сдвигом, но в обратном направлении
    return caesar_encrypt(text, -shift)

# Основная программа
if __name__ == "__main__":
    action = input("Выберите действие (шифровать/дешифровать): ").strip().lower()
    text = input("Введите текст: ")
    shift = int(input("Введите сдвиг (число): "))

    if action == 'шифровать':
        encrypted_text = caesar_encrypt(text, shift)
        print("Зашифрованный текст:", encrypted_text)
    elif action == 'дешифровать':
        decrypted_text = caesar_decrypt(text, shift)
        print("Расшифрованный текст:", decrypted_text)
    else:
        print("Неверное действие. Пожалуйста, выберите 'шифровать' или 'дешифровать'.")
