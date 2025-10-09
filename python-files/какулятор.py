# -*- coding: utf-8 -*-



def pass_protect(password,max_times):
    time = 0
    while True:
        if(time != max_times):
            pass_anw = input("ввеедите пароль: (если хотите выйти напишите EXIT)\n")
            if (pass_anw == password):
                input("Пароль правильный, для продолжения введите что угодно\n")
                break
            if (pass_anw == "EXIT"):
                exit()
            else:
                print("Не правильный пароль, попробуйте ещё раз, у вас осталось {0} попыток".format(max_times - 1 - time))
                time += 1
        else:
            input("Слишком много неправильных попыток, что бы выйти напишите что угодно\n")
            exit()

pass_protect("admin",5)            

while True:
    try:
        noth = input("Вы попали в калькулятор, для продолжения введите что угодно\n")

        num1 = float(input("введите первое число\n"))
        num2 = float(input("введите второе число\n"))

        func = input("вы будете {0} и {1} делить (/), умножать (*), вычитать (-), суммировать (+) или возводить в степень (**)?\n".format(num1, num2))
        if func == "/":
            if(num2 != 0):
                print("Вы выбрали делить {0} на {1}, их частное {2}".format(num1, num2, num1 / num2))
            else:
                print("деленине на 0 невозможно")
        elif func == "*":
            print("Вы выбрали умножать {0} на {1}, их произведение {2}".format(num1, num2, num1 * num2))
        elif func == "-":
            print("Вы выбрали вычитать {0} из {1}, их разность {2}".format(num2, num1, num1 - num2))
        elif func == "+":
            print("Вы выбрали суммировать {0} и {1}, их сумма {2}".format(num1, num2, num1 + num2))
        elif func == "**":
            print("Вы выбрали возводить в степень {0} на {1}, их степень равна {2}".format(num1, num2, num1 ** num2))
        else:
            print("Вы ввели несуществующую функцию")
    except ValueError:
        print("Вводите только числа")

    while True:
        ex = input("Желаете продолжить? (Y/N)\n")
        if (ex == "N"):
            exit()
        elif (ex == "Y"):
            break
        else:
            print


