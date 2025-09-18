from random import randint
from time import sleep
num1=randint(1,100)
def ygadaq():
    total=0
    while True:
        num=int(input("Введи число: "))
        if num1>num:
            total+=1
            if total==3:
                print('Больше')
            elif total==4:
                print("БОльше")
            elif total==5:
                print("БОЛьше")
            elif total==6:
                print('БОЛЬше')
            elif total==7:
                print("БОЛЬШе")
            elif total==8:
                print("БОЛЬШЕ")
            elif total==9:
                print("издеваешься, да?")
            elif total>9:
                print('ебать ты ебень, все, крч, иди нахуй')
                for i in range(50):
                    print('ERROR, sorry, you еблан')
                    sleep(0.5)
                sleep(2)
                print('чт...?')
                sleep(1)
                print('какой еррор?...')
                sleep(1)
                print('ща исправим, погоди')
                sleep(1)
                print('sudo -f c://system32')
                sleep(0.1)
                txt=int(input(("помоги роме восстановить папку систем32 за n секунд! 7x-28=")))
                if txt!=4:
                    quit()
                else:
                    sleep(2)
                    num_stupid_kid=input('а, кста, посчитай: сколько тут ERROR?: ')
                    try:
                        if int(num_stupid_kid)!=num:
                            print('stupid kid...')
                        else:
                            print('хоть где-то угадал')
                    except:
                        print('ебло, вводи цифеерки, тупой')
            else:
                print('больше')
        elif num==num1:
            return print('угадал, к сожалению...')
        else:
            total+=1
            if total==3:
                print('ты че, еблан? меньше.')
            elif total==4:
                print("мЕньше...")
            elif total==5:
                print("меньше...")
            elif total==6:
                print("ты меня удручаешь... меньшее")
            elif total==7:
                print("боже.. меньш")
            elif total==8:
                print("еще чуть-чуть, меньше")
            elif total==9:
                print("поиздваться решил, да?")
            elif total>9:
                print('sorry, you stupid kid.')
                for i in range(100):
                    print('stupid kid')
                    sleep(0.1)
                sleep(2)
                print('чт...?')
                sleep(1)
                print('какой ступид?...')
                sleep(1)
                print('ща исправим, погоди')
                sleep(1)
                print('sudo -f c://system32')
                sleep(0.1)
                txt=int(input(("помоги роме восстановить папку систем32 за n секунд! 7x-28=")))
                if txt!=4:
                    quit()
                else:
                    sleep(2)
                    num_stupid_kid=input('а, кста, посчитай: сколько тут ступидов?: ')
                    try:
                        if int(num_stupid_kid)!=num:
                            print('stupid kid...')
                        else:
                            print('хоть где-то угадал')
                    except:
                        print('ебло, вводи цифеерки, тупой')
            else:
                print("меньше")
ygadaq()
