import tkinter as tk
from telegram import Bot
import asyncio

BOT_TOKEN = "7378041484:AAHXaxlN_eH7HD_XRPEAKLmCpF8emXWwGLQ"
from tkinter import messagebox

CHAT_ID = "670786034"
film_eat = 0
day = 0
place = 0
place_spec = 0
another_location = 0
time = 0
addition = 0


async def send_file(bot_token, chat_id, file):
    bot = Bot(token=bot_token)
    await bot.send_document(chat_id=chat_id, document=file)
    with open(file, 'w') as file:
        file.write('')


def destroy(text, current_window):
    with open("add.txt", "a") as file:
        file.write(text)
    asyncio.run(send_file(BOT_TOKEN, CHAT_ID, "add.txt"))
    # Закрытие текущего окна
    current_window.destroy()


def add(text):
    with open("add.txt", "a") as file:
        file.write(text)
    asyncio.run(send_file(BOT_TOKEN, CHAT_ID, "add.txt"))


def on_button_click7(choice, current_window):
    global time
    global film_eat
    global day
    global place_spec
    global place
    global another_location
    global addition
    addition = choice
    current_window.destroy()
    new_window = tk.Tk()
    new_window.geometry("500x500")
    text = tk.Label(new_window,
                    text="Супер! Усі відповіді записані та відправлені!)")
    text.pack()
    with open("add.txt", "a") as file:
        file.write(str(place) + " " + str(place_spec) + " " + str(another_location) + " " + str(film_eat) + " " + str(day) + " " + str(time) + " " + str(addition))
    asyncio.run(send_file(BOT_TOKEN, CHAT_ID, "add.txt"))


def on_button_click6(choice, current_window):
    global time
    time = choice
    current_window.destroy()
    new_window = tk.Tk()
    new_window.geometry("500x500")
    text = tk.Label(new_window,
                    text="Усі відповіді збережені, якщо хочеш ще щось додати")
    text.pack()
    text2 = tk.Label(new_window,
                     text="(Наприклад улюблені квіти, попкорн, місце і т.д.)")
    text2.pack()
    text3 = tk.Label(new_window,
                     text="можешь це зробити зараз і відправити)")
    text3.pack()
    line = tk.Entry(new_window)
    line.pack()
    but_send = tk.Button(new_window, text="Відправити",
                         command=lambda: on_button_click7(line.get(), new_window))
    but_send.pack()


def on_button_click5(choice, current_window):
    current_window.destroy()
    global day
    day = choice
    new_window = tk.Tk()
    new_window.geometry("500x500")
    text = tk.Label(new_window,
                        text="І останнє - час)")
    text.pack()
    line = tk.Entry(new_window)
    line.pack()
    but_send = tk.Button(new_window, text="Відправити", command=lambda: on_button_click6(line.get(), new_window))
    but_send.pack()


def on_button_click3(choice, current_window):
    current_window.destroy()
    global film_eat
    film_eat = choice
    new_window = tk.Tk()
    new_window.geometry("500x500")
    text = tk.Label(new_window,
                        text="Ми вже на фінішній прямій! Давай оберемо день")
    text.pack()
    button1 = tk.Button(new_window, text="Понеділок", command=lambda: on_button_click5(1, new_window))
    button1.pack(pady=5)

    button2 = tk.Button(new_window, text="Вівторок", command=lambda: on_button_click5(2, new_window))
    button2.pack(pady=5)

    button3 = tk.Button(new_window, text="Середа", command=lambda: on_button_click5(3, new_window))
    button3.pack(pady=5)
    button4 = tk.Button(new_window, text="Четвер", command=lambda: on_button_click5(4, new_window))
    button4.pack(pady=5)
    button4 = tk.Button(new_window, text="П'ятниця", command=lambda: on_button_click5(5, new_window))
    button4.pack(pady=5)


def place3(choice, current_window):
    global another_location
    global place_spec
    another_location = choice
    current_window.destroy()
    new_window = tk.Tk()
    new_window.geometry("500x500")
    if place_spec == 1 or place_spec == 2:
        text = tk.Label(new_window,
                        text="Супер, ми майже в кінці. Скажи, будь ласка - на який фільм тобі цікаво піти?)")
        text.pack()
        button1 = tk.Button(new_window, text="Фантастична 4", command=lambda: on_button_click6(1, new_window))
        button1.pack(pady=5)
        button2 = tk.Button(new_window, text="Как приручить дракона", command=lambda: on_button_click6(2, new_window))
        button2.pack(pady=5)
        button2 = tk.Button(new_window, text="Ліло і стіч", command=lambda: on_button_click6(3, new_window))
        button2.pack(pady=5)
    elif place_spec == 3 or place_spec == 4 or place_spec == 5 or place_spec == 6:
        text = tk.Label(new_window,
                        text="Супер, ми майже в кінці. Скажи, будь ласка, що ти більше любиш?")
        text.pack()
        button1 = tk.Button(new_window, text="М'ясо", command=lambda: on_button_click6(4, new_window))
        button1.pack(pady=5)
        button2 = tk.Button(new_window, text="Кава/чай", command=lambda: on_button_click6(5, new_window))
        button2.pack(pady=5)
        button2 = tk.Button(new_window, text="Щось інше (Наприклад, просто посидіти)", command=lambda: on_button_click6(6, new_window))
        button2.pack(pady=5)
    else:
        on_button_click6(0, new_window)



def on_button_click2(choice, current_window):
    current_window.destroy()
    global place_spec
    place_spec = choice
    new_window = tk.Tk()
    new_window.geometry("500x500")
    if choice == 6:
        text = tk.Label(new_window,
                        text="Чудово!) Напиши куди саме тобі цікавить піти?)")
        text.pack()
        line = tk.Entry(new_window)
        line.pack()
        but_send = tk.Button(new_window, text="Відправити", command=lambda: place3(line.get(), new_window))
        but_send.pack()
    else:
        place3(0, new_window)


def on_button_click(choice):
    global place
    place = choice
    root.destroy()
    new_window = tk.Tk()
    new_window.geometry("500x500")
    if choice == 1:

        text = tk.Label(new_window,
                        text="Чудово!) Давай тоді оберемо, в який кінотеатр ти би хотіла піти - звичайний чи IMAX/4DX?")
        text.pack()
        button1 = tk.Button(new_window, text="Звичайний", command=lambda: on_button_click2(1, new_window))
        button1.pack(pady=5)
        button2 = tk.Button(new_window, text="IMAX/4DX", command=lambda: on_button_click2(2, new_window))
        button2.pack(pady=5)

    if choice == 2:

        text = tk.Label(new_window,
                        text="Чудово!) Давай тоді оберемо, що ти більше любиш")
        text.pack()
        button1 = tk.Button(new_window, text="Ліс", command=lambda: on_button_click2(7, new_window))
        button1.pack(pady=5)
        button2 = tk.Button(new_window, text="Пляж", command=lambda: on_button_click2(8, new_window))
        button2.pack(pady=5)
        button3 = tk.Button(new_window, text="Мости", command=lambda: on_button_click2(9, new_window))
        button3.pack(pady=5)
        button4 = tk.Button(new_window, text="Будь-які красиві місця", command=lambda: on_button_click2(10, new_window))
        button4.pack(pady=5)

    if choice == 3:
        text = tk.Label(new_window,
                        text="Чудово!) Давай тоді оберемо, в яке кафе ти б хотіла піти?")
        text.pack()
        button1 = tk.Button(new_window, text="Азіатське", command=lambda: on_button_click2(3, new_window))
        button1.pack(pady=5)
        button2 = tk.Button(new_window, text="Європейське", command=lambda: on_button_click2(4, new_window))
        button2.pack(pady=5)
        button3 = tk.Button(new_window, text="Красиве, щоб пофоткатись", command=lambda: on_button_click2(5, new_window))
        button3.pack(pady=5)
        button4 = tk.Button(new_window, text="Свій варіант", command=lambda: on_button_click2(6, new_window))
        button4.pack(pady=5)

    if choice == 4:
        text = tk.Label(new_window,
                        text="Чудово!) Напиши куди саме тобі цікавить піти?)")
        text.pack()
        line = tk.Entry(new_window)
        line.pack()
        but_send = tk.Button(new_window, text="Відправити", command=lambda: on_button_click2(line.get(), new_window))
        but_send.pack()


# Создание главного окна
root = tk.Tk()
root.geometry("500x500")
root.title("Walk")
theme = tk.Label(text="Куди хочеш сходити?)")
theme.pack()

# Добавление кнопок для выбора
button1 = tk.Button(root, text="Кіно", command=lambda: on_button_click(1))
button1.pack(pady=5)

button2 = tk.Button(root, text="Природа", command=lambda: on_button_click(2))
button2.pack(pady=5)

button3 = tk.Button(root, text="Кафе/Ресторан", command=lambda: on_button_click(3))
button3.pack(pady=5)

button4 = tk.Button(root, text="Свій варіант", command=lambda: on_button_click(4))
button4.pack(pady=5)

# Запуск главного цикла приложения
root.mainloop()
