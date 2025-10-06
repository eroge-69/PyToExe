import math

def random():    
    l = []
    k = int(input("Количество используемых значений : "))
    i = 0
    x = float(input("Значение : "))
    l.insert(i, x)
    summ = x
    SUMM = 0
    while i < (k-1):
        x = float(input("Значение : "))
        summ = summ + x
        l.insert(i, x)
        i += 1
    i = 0
    X = summ/k
    SUMM = (l[i] - X)**2
    while i < (k-1):
        SUMM = SUMM + (l[i+1] - X)**2
        i += 1
    Sx = math.sqrt((1/(k*(k-1)))*SUMM)
    L = []
    L.insert(0, X)
    L.insert(1, Sx)
    return L

def sigma_small_or_system():
    do1 = float(input("Приборная погрешность прямого измерения : "))
    do2 = float(input("Субъективная погрешность : "))
    do3 = float(input("Погрешность метода : "))
    do4 = float(input("Погрешность окргуления : "))
    sigma = math.sqrt(do1**2 + do2**2 + do3**2 + do4**2)
    return sigma

def mult_const():
    x = float(input("Значение : "))
    dx = float(input("Погрешность измерения : "))
    k = int(input("Количество используемых констант : "))
    const = float(input("Константа : "))
    i = 0
    x = x*const
    dx = dx*const
    while i != (k-1):
        const = float(input("Константа : "))
        x = x*const
        dx = dx*const
        i += 1
    return x, dx

def div_const():
    x = float(input("Значение : "))
    dx = float(input("Погрешность измерения : "))
    k = int(input("Количество используемых констант : "))
    const = float(input("Константа : "))
    i = 0
    x = x/const
    dx = dx/const
    while i != (k-1):
        const = float(input("Константа : "))
        x = x/const
        dx = dx/const
        i += 1
    return x, dx

def summ():
    k = int(input("Количество используемых значений : "))
    i = 0
    x = float(input("Значение : "))
    summ_of_mean = x
    while i != (k-1):
        x = float(input("Значение : "))
        summ_of_mean = summ_of_mean + x
        i += 1
    i = 0
    dx = float(input("Погрешность измерения : "))
    d_summ_of_mean = dx
    while i != (k-1):
        dx = float(input("Погрешность измерения : "))
        d_summ_of_mean = d_summ_of_mean + dx
        i += 1
    return summ_of_mean, d_summ_of_mean

def diff():
    k = int(input("Количество используемых значений : "))
    i = 0
    X = float(input("Значине, из которого будут вычитаться другие : "))
    x = float(input("Значение, которое будет вычитаться : "))
    summ_of_mean = x
    while i < (k-2):
        x = float(input("Значение, которое будет вычитаться : "))
        summ_of_mean = summ_of_mean + x
        i += 1
    diff_of_mean = X - summ_of_mean
    dx = float(input("Погрешность измерения : "))
    d_diff_of_mean = dx
    i = 0
    while i < (k-1):
        dx = float(input("Погрешность измерения : "))
        d_diff_of_mean = d_diff_of_mean + dx
        i += 1
    return diff_of_mean, d_diff_of_mean

def mult():
    k = int(input("Количество используемых значений : "))
    l = []
    i = 0
    x = float(input("Значение : "))
    l.insert(i, x)
    mult_of_mean = x
    while i < (k-1):
        x = float(input("Значение : "))
        mult_of_mean = mult_of_mean*x
        l.insert(i+1, x)
        i += 1
    dx = float(input("Погрешность измерения : "))
    i = 0
    summ_epsilon = dx/l[i]
    while i < (k-1):
        dx = float(input("Погрешность измерения : "))
        summ_epsilon = summ_epsilon + dx/l[i+1]
        i += 1
    d_mult_of_mean = mult_of_mean*summ_epsilon
    return mult_of_mean, d_mult_of_mean

def div():
    k = int(input("Количество используемых значений : "))
    l = []
    i = 0
    X = float(input("Значение, которое будет делиться на остальные : "))
    l.insert(i, X)
    mult_of_mean = 1
    while i < (k-1):
        x = float(input("Значение : "))
        mult_of_mean = mult_of_mean*x
        l.insert(i+1, x)
        i += 1
    div_of_mean = X/mult_of_mean
    dx = float(input("Погрешность измерения : "))
    i = 0
    summ_epsilon = dx/l[i]
    while i < (k-1):
        dx = float(input("Погрешность измерения : "))
        summ_epsilon = summ_epsilon + dx/l[i+1]
        i += 1
    d_div_of_mean = div_of_mean*summ_epsilon
    return div_of_mean, d_div_of_mean

def full():
    n = random()
    a = n[1]
    b = sigma_small_or_system()
    c = math.sqrt(a**2 + b**2)
    d = n[0]
    return d, c

print("Выберите действие : случайная погрешность, систематическая погрешность, сумма величин, разность величин, " \
"произведение величин, деление величин, умножение на константу, деление на константу, полная величина и погрешность")
val = input()
a = 0
i = 0
while i != 1:
    if val == "случайная погрешность":
        a = random()
        i = 1
    elif val == "систематическая погрешность":
        a = sigma_small_or_system()
        i = 1
    elif val == "сумма величин":
        a = summ()
        i = 1
    elif val == "разность величин":
        a = diff()
        i = 1
    elif val == "произведение величин":
        a = mult()
        i = 1
    elif val == "деление величин":
        a = div()
        i = 1
    elif val == "умножение на константу":
        a = mult_const()
        i = 1
    elif val == "деление на константу":
        a = div_const()
        i = 1
    elif val == "полная величина и погрешность":
        a = full()
        i = 1
    else:
        print("Ошибка при вводе, повторите ещё раз")
        break
    print(a)