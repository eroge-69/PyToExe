Python 3.12.5 (tags/v3.12.5:ff3bc82, Aug  6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import random

# Транслитерация
def transliterate(text):
    map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'e', 'ж': 'zh','з': 'z', 'и': 'i',
        'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh','ц': 'ts','ч': 'ch',
        'ш': 'sh','щ': 'shch','ы': 'y','э': 'e', 'ю': 'yu',
        'я': 'ya', 'ь': '', 'ъ': ''
    }
    return ''.join(map.get(c.lower(), c) for c in text)

# Генерация пароля вида Буква+Цифра 4 раза
def generate_password():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
...     digits = '0123456789'
...     return ''.join(random.choice(letters) + random.choice(digits) for _ in range(4))
... 
... # Генерация логина и пароля
... def generate_credentials(full_name):
...     parts = full_name.strip().split()
...     if len(parts) != 3:
...         return None
...     last, first, middle = parts
...     last_tr = transliterate(last)
...     first_tr = transliterate(first)
...     middle_tr = transliterate(middle)
...     login = (first_tr[0] + middle_tr[0] + last_tr).lower()
...     password = generate_password()
...     return f"{full_name}\n{login}\n{password}\n"
... 
... # Основная программа
... def main():
...     print("Введите ФИО через разрыв строки. Для завершения — пустая строка:")
...     lines = []
...     while True:
...         line = input()
...         if line.strip() == '':
...             break
...         lines.append(line)
... 
...     result = ''
...     for line in lines:
...         credentials = generate_credentials(line)
...         if credentials:
...             result += credentials + '\n'
... 
...     with open("Логины и пароли.txt", "w", encoding="utf-8") as f:
...         f.write(result.strip())
... 
...     print("Файл 'Логины и пароли.txt' создан.")
... 
... if name == "main":
