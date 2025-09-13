table = {
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15
}
reverse_table = {
    '10': 'A','11': 'B', '12': 'C','13': 'D','14': 'E','15': 'F'
}

def sixteenthtonumber(obj):
    obj = obj.upper()
    if obj in table:
        return table[obj]
    else:
        return obj

def other_to_ten(object, number):
    result = 0 
    number = int(number)
    x = len(str(object))
    for symbol in str(object):
        x -= 1 
        newsymbol = symbol
        if number == 16:
            newsymbol = sixteenthtonumber(symbol)
        result += int(newsymbol) * (number**x)
    return result

def ten_to_other(object, number):
    all = str()
    object = int(object)
    number = int(number)
    while object >= number:
        ost = object % number
        if number == 16 and ost >= 10:
            ost = reverse_table[str(ost)]
        all += str(ost)
        object //= number
    if object > 0:
        if number == 16 and object >= 10:
            object = reverse_table[str(object)]
        all += str(object)
    result = all[::-1]
    return result
def zapros():
    print("Введите операцию которую хотите исполнить:")
    print("1.Перевести из любой в десятичную")
    print("2.Перевести из десятичной в любую")
    print("3.Перевести из любой в любую")
    num = input("Какую операцию исполнить?:")
    if num == "1":
        obj = input("Введите цифру в любой системе счисления:")
        numb = input("Введите систему счисления числа введенного ранее:")
        print("Ответ:",other_to_ten(obj,numb))
    elif num == "2":
        obj = input("Введите цифру в десятичной системе счисления:")
        numb = input("Введите систему счисления в которую надо перевести:")
        print("Ответ:",ten_to_other(obj,numb))
    elif num == "3":
        obj = input("Введите цифру в любой системе счисления:")
        numbe = input("Введите систему счисления числа введенного ранее:")
        numb = input("Введите систему счисления в которую надо перевести:")
        obj2 = other_to_ten(obj,numbe)
        print("Ответ:",ten_to_other(obj2,numb))
    else:
        print("Перезапуск программы...")
        print("_______________________")
        return zapros()
    print("Перезапуск программы...")
    print("_______________________")
    return zapros()
zapros()
