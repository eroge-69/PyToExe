from math import cos, sin, tan, radians

while True:
    command = input(f'введите команду >> ')
    
    if command == 'команды':
        print(f'чет, кос, син, тан, радиан, калькулятор, стоп')

    elif command == 'чет':
        a = input(f'>> ')
        try:
            a = int(a)
            if a % 2 == 0:
                print(f'чет >> {a} <<')
            else:
                print(f'нечет >> {a} <<')
        except ValueError:
            print(f'>> {a} << не число!')

    elif command == 'кос':
        try:
            coss = int(input(f'>> '))
            print(cos(coss))
        except ValueError:
            print(f'>> {coss} << не число!')

    elif command == 'син':
        try:
            sinn = int(input('>> '))
            print(sin(sinn))
        except ValueError:
            print(f'>> {sinn} << не число!')

    elif command == 'тан':
        try:
            tann = int(input(f'>> '))
            print(tan(tann))
        except ValueError:
            print(f'>> {tann} << не число!')

    elif command == 'радиан':
        try:
            radian = int(input(f'>> '))
            print(radians(radian))
        except ValueError:
            print(f'>> {radian} << не число!')

    elif command == 'калькулятор':
        znak = input(f'какой знак использовать?\n 1) +\n 2) -\n 3) *\n 4) /\n>> ')
        if znak not in ['1', '2', '3', '4']:
            print(f'>> {znak} << не является цифрой из заданных! выберите цифру 1, 2, 3 или 4!')
        elif znak == '1':
            chislo = float(input(f'>> '))
            chislo1 = float(input(f'>> '))
            print(f'>> {chislo + chislo1} <<')

        elif znak == '2':
            chislo2 = float(input(f'>> '))
            chislo3 = float(input(f'>> '))
            print(f'>> {chislo2 - chislo3} <<')

        elif znak == '3':
            chislo4 = float(input(f'>> '))
            chislo5 = float(input(f'>> '))
            print(f'>> {chislo4 * chislo5} <<')

        elif znak == '4':
            chislo6 = float(input(f'>> '))
            chislo7 = float(input(f'>> '))
            print(f'>> {chislo6 / chislo7} <<')

    elif command == 'стоп':
        print(f'>> {command} << выход!')
        break
    else:
        print(f'нет такой команды!')