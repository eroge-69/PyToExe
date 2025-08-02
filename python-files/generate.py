import secrets
import string

print("Выберите тип пароля:")
print("1. Только буквы (прописные и строчные)")
print("2. Буквы и цифры")
print("3. Буквы, цифры и специальные символы")
while True:
    password_type = input("Ваш выбор (1-3): ")
    if password_type in ['1', '2', '3']:
        break
    else:
        print("Некорректный выбор. Пожалуйста, введите 1, 2 или 3.")

if password_type == '1':
    characters = string.ascii_letters
elif password_type == '2':
    characters = string.ascii_letters + string.digits
elif password_type == '3':
    characters = string.ascii_letters + string.digits + string.punctuation

while True:
    try:
        password_length = int(input("Введите длину пароля (от 1 до 100): "))
        if 1 <= password_length <= 100:
            break
        else:
            print("Длина должна быть от 1 до 100.")
    except ValueError:
        print("Пожалуйста, введите целое число.")

while True:
    password = ''.join(secrets.choice(characters) for _ in range(password_length))
    print(f"Сгенерированный пароль: {password}")
    while True:
        next_action = input("Что дальше? 1. Сгенерировать новый пароль 2. Выйти из программы: ")
        if next_action in ['1', '2']:
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1 или 2.")
    if next_action == '2':
        print(f"Пароль: {password}. Вы можете скопировать его вручную.")
        print("Программа завершена.")
        break