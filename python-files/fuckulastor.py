import math
from colorama import Fore, Back, Style
from colorama import init

#int
n = 5
age = 21
#float
m = 5.7
#str
na = "a"
#bool
status = True#\False

#print('он \'плохо\'делает!')
#print("hello \nworld")
#print("lox  baka"'\n' + na + "!")
#print("me " + str(age) + " penis") 

#name = input("whats ur name?:")
#age = input("how old are you?:")
#print("hello " + name + " !!!")
#print("wow you are " + age + " years old")

#math:

#a = 10
#a = -a       #-10
#print(a)

#a = 5.2981821892891891280 # 5 или print(round/math.floor(a)) 
                        #или ceil в большую сторону 6
#print(math.ceil(a))

#калькулятор
print(Fore.GREEN)
print(Style.DIM)

what = input("чо делaть?: ")
print(Fore.RED)
print(Style.DIM)
a =  float (input("введи число: "))
b =  float (input("введи другое число: "))
if what == "+":
    c = a + b
    print(Fore.CYAN)
    print(Style.DIM)
    print("результат: " + str(c))
elif what == "-":
    c = a - b
    print(Fore.CYAN)
    print(Style.DIM)
    print("результат: " + str(c))
elif what == "/":
    c = a / b
    print(Fore.CYAN)
    print(Style.DIM)
    print("результат: " + str(c))
elif what == "*":
    c = a * b
    print(Fore.CYAN)
    print(Style.DIM)
    print("результат: " + str(c))
else:
    print('даун нето')
input("бб")    
    