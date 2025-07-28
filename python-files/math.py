import random
import time
print("Привет.")
print("Добро пожаловать в математическую игру Матиматикс.")
count_a = 1
last_game = -1
while  count_a == 1:
    print("Желаете продолжить? (Да/Нет)")
    a=input()
    if a == 'да' or a == 'Да' or a == "ДА":
        print('Отлично! Начинаем игру.')
        count_a = 2
    elif a == 'нет' or a == 'Нет' or a == 'нЕт' or a == 'неТ' or a == 'НЕт' or a == 'нЕТ' or a == 'НеТ' or a == 'НЕТ':
        print('ОК! Закрываю игру через 3 секунды...')
        time.sleep(3)
        exit()
    else:
        print('Нераспознанная команда.')
if last_game == -1:
    print('Счёт предыдущей игры: игра не проводилась в данном сеансе')
else:
    print('Счёт предыдущей игры:', last_game)
#print('Уровень сложности повышается с каждыми 10 правильными ответами.')
print('Игра завершается при неправильном ответе.')
print('Введите любой символ для продолжения.')
abc=input()
count_b = 1
last_game = 0
while count_b == 1:
    num1 = (random.randint(0, 10))
    num2 = (random.randint(0, 10))
    znak = (random.randint(1, 3))
    if znak == 1:
        result = num1 * num2
        print('Чему равно равенство:', num1, '*', num2)
    elif znak == 2:
        result = num1 + num2
        print('Чему равно равенство:', num1, '+', num2)
    elif znak == 3:
        result = num1 - num2
        print('Чему равно равенство:', num1, '-', num2)
    if int(input()) == result:
       print('Верно!')
       last_game+=1
    else:
        print('Увы... Ответ неверен. Игра закончена')
        print('Ваш счёт:', last_game)
        count_a = 1
        while  count_a == 1:
            print("Желаете играть заново? (Да/Нет)")
            a=input()
            if a == 'да' or a == 'Да' or a == "ДА":
                print('Отлично! Начинаем игру.')
                count_a = 2
                last_game = 0   
            elif a == 'нет' or a == 'Нет' or a == 'нЕт' or a == 'неТ' or a == 'НЕт' or a == 'нЕТ' or a == 'НеТ' or a == 'НЕТ':
                print('ОК! Закрываю игру через 3 секунды...')
                time.sleep(3)
                exit()
            else:
                print('Нераспознанная команда.')
