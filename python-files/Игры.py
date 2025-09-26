import random
import colorama
ch = ["Камень","Ножницы","Бумага"]
w = [0.33,0.33,0.33]
colorama.init()

while True:
    print(colorama.Fore.CYAN+"Игра начиласью. Выбери"+colorama.Fore.RESET)
    print("1 - Камень")
    print("2 - Ножницы")
    print("3 - Бумага")
    print("99 - Выход")
    try:
        cmd = int(input())
    except ValueError:
        print(colorama.Fore.RED+"Введите значение из меню"+colorama.Fore.RESET)
        continue
    if(cmd == 99):
        break
    comp_ch = random.choices(ch,weights=w)[0]
    try:
        user_ch = ch[cmd-1]
    except IndexError:
        print(colorama.Fore.RED+"Введите значение из меню"+colorama.Fore.RESET)
        continue
    print(user_ch)
    print(comp_ch)
    if(comp_ch == user_ch):
        print(colorama.Fore.YELLOW+"Ничья"+colorama.Fore.RESET)
    if(user_ch == "Камень" and comp_ch == "Бумага"):
        print(colorama.Fore.RED+"Ты проиграл"+colorama.Fore.RESET)
    if(user_ch == "Камень" and comp_ch == "Ножницы"):
        print(colorama.Fore.GREEN+"Ты победил"+colorama.Fore.RESET)
    if(user_ch == "Ножницы" and comp_ch == "Камень"):
        print(colorama.Fore.RED+"Ты проиграл"+colorama.Fore.RESET)
    if(user_ch == "Ножницы" and comp_ch == "Бумага"):
        print(colorama.Fore.GREEN+"Ты победил"+colorama.Fore.RESET)
    if(user_ch == "Бумага" and comp_ch == "Камень"):
        print(colorama.Fore.GREEN+"Ты победил"+colorama.Fore.RESET)
    if(user_ch == "Бумага" and comp_ch == "Ножницы"):
        print(colorama.Fore.RED+"Ты проиграл"+colorama.Fore.RESET)
    
