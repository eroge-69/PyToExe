# Генератор безопасных паролей
from random import choice

digits = '0123456789'
lowercase_letters = 'abcdefghijklmnopqrstuvwxyz'
uppercase_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
punctuation = '!#$%&*+-=?@^_.'

chars = ''

words = [
    'Сколько паролей сгенерировать (число/цифра больше 0)?',
    'Укажите длину одного пароля (число/цифра больше 0):',
    'Включать ли цифры "0123456789" (Да/Нет)?',
    'Включать ли прописные буквы "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (Да/Нет)?',
    'Включать ли строчные буквы "abcdefghijklmnopqrstuvwxyz" (Да/Нет)?',
    'Включать ли символы "!#$%&*+-=?@^_" (Да/Нет)?',
    'Исключать ли неоднозначные символы "il1Lo0O" (Да/Нет)?',
    'Упс! Ошибка🔧 Введите "Да" или "Нет" в любом регистре!',
    'Упс! Ошибка🔧 Введите любое число/цифру больше 0!'
]


def _0_():
    print(words[0])
    ans = input().strip()
    while True:
        if not (ans.isdigit() and ans != '0'):
            print(words[8])
            ans = input().strip()
        else:
            return int(ans)


def _1_():
    print(words[1])
    ans1 = input().strip()
    while True:
        if not (ans1.isdigit() and ans1 != '0'):
            print(words[8])
            ans1 = input().strip()
        else:
            return int(ans1)


def _2_():
    global chars
    print(words[2])
    ans2 = input().strip().lower()
    while True:
        if not ans2 in ('да', 'нет'):
            print(words[7])
            ans2 = input().strip().lower()
        elif ans2 == 'да':
            chars += digits
            return chars
        else:
            break


def _3_():
    global chars
    print(words[3])
    ans3 = input().strip().lower()
    while True:
        if not ans3 in ('да', 'нет'):
            print(words[7])
            ans3 = input().strip().lower()
        elif ans3 == 'да':
            chars += uppercase_letters
            return chars
        else:
            break


def _4_():
    global chars
    print(words[4])
    ans4 = input().strip().lower()
    while True:
        if not ans4 in ('да', 'нет'):
            print(words[7])
            ans4 = input().strip().lower()
        elif ans4 == 'да':
            chars += lowercase_letters
            return chars
        else:
            break


def _5_():
    global chars
    print(words[5])
    ans5 = input().strip().lower()
    while True:
        if not ans5 in ('да', 'нет'):
            print(words[7])
            ans5 = input().strip().lower()
        elif ans5 == 'да':
            chars += punctuation
            return chars
        else:
            break


def _6_():
    global chars
    print(words[6])
    ans6 = input().strip().lower()
    while True:
        if not ans6 in ('да', 'нет'):
            print(words[7])
            ans6 = input().strip().lower()
        elif ans6 == 'да':
            chars = chars.replace('i', '').replace('l', '').replace('1', '').replace('L', '') \
                         .replace('o', '').replace('0', '').replace('O', '')
            return chars
        else:
            break


result = _0_()
result1 = _1_()
result2 = _2_()
result3 = _3_()
result4 = _4_()
result5 = _5_()
result6 = _6_()


def generate_password():
    global chars
    length = result1

    passwords = []
    for _ in range(result):
        password = ''
        for _ in range(length):
             password += choice(chars)
        passwords.append(password)

    return passwords


print(*generate_password(), sep='\n')


print("\nГенерация завершена! Пароли выше ↑")
input("Нажмите Enter для выхода...")