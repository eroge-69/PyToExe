import random

# это типа масив только простой сюда юз тг вставлять(парни)
a = ("q")
s = ("4")
d = ("3")
f = ("2")
g = ("1")
#рандом выбор
Parni = [a, s, d, f, g,]
Parni = random.choice(Parni)

# это типа масив только простой сюда юз тг вставлять(девушки)
z =("222")
x =("333")
c =("444")
v =("555")
b =("666")
#рандом выбор
devushki =[z,x,c,b,v]
devushki = random.choice(devushki)


P = input("Привет, Кого тебе найти Девушку/Парня")
#кароч это отвечает за поиск
if P == ("Парня"):
    print(Parni)
else:
    print(devushki)
    