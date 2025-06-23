import time
import sys
password = "AIDS boogers"
starttext = "Запуск..."
for char in starttext:
    print(char, end='', flush=True)
    time.sleep(0.3)
print()
text1 = "Внимание! Неавторизованный пользователь! Для входа в приложение T-control требуется пароль"
for char in text1:
    print(char, end='', flush=True)
    time.sleep(0.02)
while True:
    try:
        passuser = input("Введите пароль:")
    except ValueError:
        print("введите корректный верный пароль")
        continue
    except TypeError:
        print("введите корректный верный пароль")
        continue
    if passuser == password:
        print("Пароль принят! Вход под пользователем root успешен!")
        break
    else:
        print("введите корректный верный пароль")
        continue
searchingtext = "Поиск доступных для подключения терминаторов..."
for char in searchingtext:
    print(char, end='', flush=True)
    time.sleep(0.03)
print("Для подключение доступно 5 моделей:")
print("1: I-950")
print("2: T-900(class:TOK715)")
print("3: T-850(num2357847model:101)")
print("4: T-H")
print("5: T-888")
termuser = int(input("выберите номер модели для подключения:"))
if termuser == 2:
    print("Подключение...")
    time.sleep(2)
    print("Подключение успешно. Пройдите к МУУНТ(машина удаленного управления не отключенными терминаторами)")
else:
    print("Подключение...")
    time.sleep(1)
    print("ОШИБКА: подключение разорвано")
time.sleep(20)
print("Подключение человека к МУУНТ выполнено, запуск передачи сигналов во времени завершен, начинаю синхронизацию с системами терминатора...")
time.sleep(5)
print("Синхронизация: Успешно. Сознание терминатора: отключено. МУУНТ успешно заместила сознание терминатора. Контроллеры активны!")
time.sleep(99999)