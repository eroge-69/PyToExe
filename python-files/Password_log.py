import os
import time
import random
random_integer = random.randint(0, 16)
a = str(input('Введите название сети Wi-Fi: '))
l = "Keylogger..."  
for string in l:  
    print(l)
    time.sleep(1)
l = "Buffering..."  
for string in l:  
    print(l)
    time.sleep(1)
b = str(input('Введите Ваш Регион: '))
t = int(5000)
r = int(0)
while r < t:
    print(r,'бит')
    r =(r+random_integer)*2
    time.sleep(1)
if (a == 'MTSRouter_4D0F3C')and(b == 'Tatarstan'):
    print('Proxy: http://proxy.school.tatar.ru/wpad.dat')
    print('Password: hb5akg7t')
else:
    print('Error, try again...')
os.system("pause")
