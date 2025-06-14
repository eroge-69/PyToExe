# Запрашиваем имя файла у пользователя
file_name = input("Введите имя текстового файла: ")

# Инициализируем счетчик
count = 0

try:
    # Открываем файл в режиме чтения
    with open(file_name, 'r') as file:
        # Читаем файл построчно
        for line in file:
            # Удаляем пробельные символы в конце строки (включая \n) и проверяем последний символ
            cleaned_line = line.rstrip()
            if cleaned_line.endswith(('z')):
                count += 1
except FileNotFoundError:
    print(f"Ошибка: Файл '{file_name}' не найден")
    exit()

# Выводим результат
print(f"Количество строк, заканчивающихся на 'z': {count}")
