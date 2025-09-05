import hashlib

# Функция для хэширования информации методом sha1


def crypt_to_sha1(role=0):
    print("\nВведите сообщения для создание хэша SHA1:")
    ext_message = input(">>> ")
    if (len(ext_message) >= 4) or (role == 1):
        out_message = hashlib.sha1(ext_message.encode()).hexdigest()
        print(f"Ваше сообщение: {ext_message}\nХэш SHA1: {out_message}\n")
    else:
        print("Не соблюдены условия использования функции. Выход из подпрограммы.\n")


def two_digit():
    print("\nError: 360 line string in .hex\n")


def settings():
    mode = "true"
    hash = "sha1"
    sdk = "1.0"
    ver = "1.0"
    compile = False
    parse_test = True
    size = "1920x1080"
    print(f"mode:{mode}\n"
          f"hash:{hash}\n"
          f"sdk:{sdk}\n"
          f"ver:{ver}\n"
          f"compile:{compile}\n"
          f"parse:{parse_test}\n"
          f"size:{size}\n"
    )
    check_settings()

    hash_result = input('>>> ')
    if hash_result == "dc76e9f0c0006e8f919e0c515c66dbba3982f785":
        print("тут ссылку на флаг")
    else:
        print("fssps:jowbmje_ibti")

def check_settings():
    if __name__ == "__main__":
        print("Настройки применены успешно.\n Введите хэш для использования конфига или сброса к стандартным настрйокам")


if __name__ == "__main__":
    print("Программа запущена успешно. Введите \"help\" для вывода подсказки.")
    exit = False
    while not exit:
        cmd = input(">>> ")
        if cmd == "hash_sha1":
            crypt_to_sha1()
        elif cmd == "help":
            print("Название команды\t\tОписание\n")
            print("hash_sha1\t\t\tПозволяет использовать алгоритм SHA1\n")
            print("task1\t\t\t\tЗапуск проверки выполнения задания\n")
            print("2digit\t\t\t\tВозвести двойку в степень???\n")
            print("help\t\t\t\tВыводит сообщение с подсказкой\n")
            print("exit\t\t\t\tЗакрыть программу\n")
            print("Подсказка: Где-то в задаче использовался шифр Цезаря со сдвигом 1 :)\n")
        elif cmd == "2digit":
            two_digit()
            quit()
        elif cmd == "task1":
            settings()
        elif cmd == "exit":
            quit()
        else:
            print(f"Комманды {cmd} не существует\n")