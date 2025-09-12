#Напиши программу где 0-18 лет - 5% скидка 
#
#19-40 скидка 15%
#
#Более 40 - 27% скидка 
#
#И ещё можно запросить сумму покупки и считать со всеми скидками скока выходит

import time
bread = 45
Water = 60
Petr = 100
print('Привет! Ты попал в магазин Uchiha! У нас есть три продукта:')
print('Хлеб - 45р, Водяра - 60р, Петрушка(1кг) - 100р действуют скидки!')
old = int(input('Скидки действуют по возрасту, сколько тебе лет?: '))
time.sleep(2)
kor = str(input('Отлично! Теперь напиши, что ты покупаешь через запятую если товар не один, соблюдая орфографию!: '))
if kor == 'Хлеб' and old <= 18:
    itog = bread * (1 - 5/100)
    print('Итого: ', itog)
if kor == 'Хлеб' and old in range(19,41):
    itog = bread * (1 - 15/100)
    print('Итого: ', itog)
if kor == 'Хлеб' and old >= 41:
    itog = bread * (1 - 27/100)
    print('Итого: ', itog)
if kor == 'Водяра' and old <= 18:
    itog = Water * (1 - 5/100)
    print('Итого: ', itog)
if kor == 'Водяра' and old in range(19,41):
    itog = Water * (1 - 15/100)
    print('Итого: ', itog)
if kor == 'Водяра' and old >= 41:
    itog = Water * (1 - 27/100)
    print('Итого: ', itog)
if kor == 'Петрушка' and old <= 18:
    itog = Petr * (1 - 5/100)
    print('Итого: ', itog)
if kor == 'Петрушка' and old in range(19,41):
    itog = Petr * (1 - 15/100)
    print('Итого: ', itog)
if kor == 'Петрушка' and old >= 41:
    itog = Petr * (1 - 27/100)
    print('Итого: ', itog)
if kor == 'Хлеб, водяра' and old <= 18:
    itog = bread+Water * (1 - 5/100)
    print('Итого: ', itog)
if kor == 'Хлеб, водяра' and old in range(19,41):
    itog = bread+Water * (1 - 15/100)
    print('Итого: ', itog)
if kor == 'Хлеб, водяра' and old >= 41:
    itog = bread+Water * (1 - 27/100)
    print('Итого: ', itog)
if kor == 'Водяра, Петрушка' and old <= 18:
    itog = Water+Petr * (1 - 5/100)
    print('Итого: ', itog)
if kor == 'Водяра, Петрушка' and old in range(19,41):
    itog = Water+Petr * (1 - 15/100)
    print('Итого: ', itog)
if kor == 'Водяра, Петрушка' and old >= 41:
    itog = Water+Petr * (1 - 27/100)
    print('Итого: ', itog)
if kor == 'Хлеб, петрушка' and old <= 18:
    itog = bread+Petr * (1 - 5/100)
    print('Итого: ', itog)
if kor == 'Хлеб, петрушка' and old in range(19,41):
    itog = bread+Petr * (1 - 15/100)
    print('Итого: ', itog)
if kor == 'Хлеб, петрушка' and old >= 41:
    itog = bread+Petr * (1 - 27/100)
    print('Итого: ', itog)
if kor == 'Хлеб, Водяра, Петрушка' and old >= 41:
    itog = bread+Water+Petr * (1 - 27/100)
    print('Итого: ', itog)
print('Спасибо за покупку! Приходите ещё!')
