import random, string
from googletrans import Translator
from pprint import pprint
import pyttsx3
import platform, socket, uuid, psutil, re, cpuinfo, datetime


while True:
    main = input("1. Калькулятор\n2. Угадай число\n3. Генератор чисел\n4. Переводчик\n5. Озвучка текста (НЕ РАБОТАЕТ)\n6. Информация о системе\n7. Генератор паорлей\n8. Генератор паролей (УСЛОЖНЕННЫЙ)\nВведите номер пункта: ")
    if not main.isdigit():
        print("\nОшибка! Пожалуйста напишите корректное значение!\n")
        continue
    elif int(main) == 1:
        calc = eval(input("Введите выражение (без пробелов): "))
        print(f"Ответ: {calc}\n")
        continue
    elif int(main) == 2:
        value = random.randint(1, 100)
        guess = 0
        attempts = 0
        print('Привет! Ты в игре "Угадай число". Тебе нужно отгадать число, которое я загадал! (от 1 до 100)')
        while guess != value:
            guess = int(input('Введи свое число: '))
            if guess > value:
                print("Мое число меньше")
                attempts += 1
            elif guess < value:
                print("Мое число больше")
                attempts += 1
            else:
                print(f"Выигрыш!\nУ тебя ушло {attempts} попыток\n")
                break
    elif int(main) == 3:
        border_1, border_2 = map(int, input("Введите 2 числа (Границы. Через пробел): ").split())
        print(f"Случайное число: {random.randint(border_1, border_2)}\n")      
        continue
    elif int(main) == 4:
        translator = Translator()
        print("\n1. С любого языка на английский\n2. С любого языка на русский")
        while True:
            text = int(input("Введи номер перевода: "))
            if text == 1:
                translation = translator.translate(text=input("Введи текст для перевода: "), dest="en")
                print(f"Перевод: {translation.text}\n")
                break
            elif text == 2:
                translation = translator.translate(text=input("Введи текст для перевода: "), dest="ru")
                print(f"Перевод: {translation.text}\n")
                break
    elif int(main) == 5:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        russian_voice = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0'
        engine.setProperty('voice', russian_voice)

        speach_text = input("Введите текст для озвучки: ")
        engine.say(speach_text)
        engine.runAndWait
        print("Озвучено!")
    elif int(main) == 6:
        print(f"\nПлатформа: {platform.platform()}")
        print(f"Имя хоста: {socket.gethostname()}")
        print(f"IP-адрес: {socket.gethostbyname(socket.gethostname())}")
        print(f"MAC-адрес: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}")
        print(f"Процессор: {cpuinfo.get_cpu_info()['brand_raw']}")
        print(f"Оперативная память: {str(round(psutil.virtual_memory().total / (1024.0 **3)))} GB\n")
    
        def get_size(bytes, suffix="B"):
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            print(f"=== Диск: {partition.device} ===")
            print(f"Общий объем: {get_size(partition_usage.total)}")
            print(f"Использовано: {get_size(partition_usage.used)}")
            print(f"Свободно: {get_size(partition_usage.free)}\n")
    elif int(main) == 7:
        def generation(length):
            symbols = string.ascii_letters + string.digits
            password = ''.join(random.choice(symbols) for _ in range(length))
            return password
        password_length = int(input("Введите длинну пароля: "))
        generated_password = generation(password_length)
        print(f"Ваш сгенерированный пароль: {generated_password}\n")
    elif int(main) == 8:
        def generation_hard(length):
            symbols = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(symbols) for _ in range(length))
            return password
        password_length = int(input("Введите длинну пароля: "))
        generated_password = generation_hard(password_length)
        print(f"Ваш сгенерированный пароль: {generated_password}\n")
