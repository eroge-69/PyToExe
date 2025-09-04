while True:
    password = input ("Введите пароль:") # запрос на ввод пароля
    new_password = "" # строка где будет записан преобразованный пароль
    for code in password: # преобразование символов
        code = ord(code) # перевод буквы в код
        new_code = code + 6 # прибавка к каждой букве 7
        new_code = chr(new_code) # берем код и возвращаем символ
        new_password = new_password + new_code # добавляем символ к результату
    if new_password == "primer": # проверка, равен ли преобразованный пароль
        print ("верно")
        input ("Нажмите любую клавишу для выхода")
        break
    else:
        print("неверно")
