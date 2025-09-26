import os
import time
import telebot
import pyautogui
import keyboard

BOT_TOKEN = "7924904605:AAGesbGMOTbGtyoD4JdBArrffGpHsubPq84"
YOUR_TELEGRAM_ID = 5622791576
SCREENSHOT_PATH = "screenshot.png"

bot = telebot.TeleBot(BOT_TOKEN)

def is_authorized(user_id):
    return user_id == YOUR_TELEGRAM_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "������! ������� /photo, ����� �������� �������� � �������� ��������.")
    else:
        bot.reply_to(message, "? � ���� ��� �������.")

@bot.message_handler(commands=['photo'])
def handle_photo(message):
    user_id = message.from_user.id

    if not is_authorized(user_id):
        bot.reply_to(message, "? ������ ��������.")
        return

    bot.reply_to(message, "?? �������� ������� /photo. ������� F5...")

    try:
        keyboard.press_and_release('f5')
        bot.send_message(user_id, "? F5 �����. ��� �������� ��������...")

        time.sleep(3)

        screenshot = pyautogui.screenshot()
        screenshot.save(SCREENSHOT_PATH)

        # ���������� ����
        with open(SCREENSHOT_PATH, 'rb') as photo:
            bot.send_photo(user_id, photo)

        bot.send_message(user_id, "?? �������� ���������!")

    except Exception as e:
        error_msg = f"? ������: {str(e)}"
        bot.send_message(user_id, error_msg)
        print(error_msg)
    finally:
        if os.path.exists(SCREENSHOT_PATH):
            os.remove(SCREENSHOT_PATH)

if __name__ == "__main__":
    print("? ��� �������. �������� ������� /photo...")
    print(f"���� Telegram ID: {YOUR_TELEGRAM_ID}")
    bot.infinity_polling()