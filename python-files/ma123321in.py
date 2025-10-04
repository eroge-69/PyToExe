print("Вас приветствует программа крутого!")
true_running3 = True
while true_running3:
    print("Введите 'exit' если хотите закрыть программу.")
    login = input("Введите логин: ")
    parol = input("Введите пароль: ")
    if parol == "sanek228":
        print("Вы успешно зашли в систему!")
        true_running2 = True
        while true_running2:
            print("  Вы зашли как пользователь: ",login)
            print("  Выберите функцию программы:")
            print("    1. Калькулятор - calc")
            print("    2. Возраст - age")
            print("    3. Выйти - exit")
            chose = input("Введите код программы: ")
            if chose == ("calc") or chose == ("1"):
                true_running = True
                while true_running:
                    f_num = float(input("Введите число 1: "))
                    operacia = input("введите операцию: +,-,/,*, ** >> ")
                    s_num = float(input("Введите число 2: "))
                    if operacia == ("+"):
                        rez = print("Результат равен: ", f_num + s_num)
                    elif operacia == ("/"):
                        rez = ("Результат равен: ", f_num / s_num)
                    elif operacia == ("*"):
                        rez = print("Результат равен: ", f_num * s_num)
                    elif operacia == ("-"):
                        rez = print("Результат равен: ", f_num - s_num)
                    elif operacia == ("**"):
                        rez = print("Результат равен: ", f_num ** s_num)
                    else:
                        print("ты конченый долбаеб!")
                    end = input("Напишите y/n чтобы продолжить. ")
                    if end == "n":
                        break
            elif chose == ("age") or chose == ("2"):
                age2 = int(input("Введите ваш возраст: (число) >> "))
                if age2 <= 0:
                    print("Возраст не может быть отрицательным и равным нулю!")
                elif age2 <= 12 and age2 > 0:
                    print("Вы ребенок!")
                    print(f"До совершеннолетия вам:", 18-age2, "лет!")
                elif age2 >= 13 and age2 <= 17:
                    print("Вы подросток!")
                    print(f"До совершеннолетия вам:", 18-age2, "лет!")
                elif age2 >= 18 and age2 < 44:
                    print("Вы взрослый и молодой!")
                    print(f"До рекорда Жанны Кальман вам осталось:", 123 - age2, "лет!")
                elif age2 >= 45 and age2 < 59:
                    print("Вы среднего возраста!")
                    print(f"До рекорда Жанны Кальман вам осталось:", 123 - age2, "лет!")
                elif age2 >= 60 and age2 < 74:
                    print("Вы пожилые!")
                    print(f"До рекорда Жанны Кальман вам осталось:", 123 - age2, "лет!")
                elif age2 >= 75 and age2 < 89:
                    print("Вы старые!")
                    print(f"До рекорда Жанны Кальман вам осталось:", 123 - age2, "лет!")
                elif age2 >= 90 and age2 < 123:
                    print("Вы долгожители!")
                    print(f"До рекорда Жанны Кальман вам осталось:", 123 - age2, "лет!")
                else:
                    print("Вы долбаеб!")
            elif chose == ("exit") or chose == ("3"):
                quit()
    if parol == ("exit"):
        break
    else:
        print("Данные неверны.")

