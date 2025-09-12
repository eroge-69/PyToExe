import telebot
import pyautogui
import os
import time
from telebot import types

# Токен бота - получите у @BotFather
BOT_TOKEN = "8244082306:AAH5CxodklCzECwFU4pHiUs18Fq1CnZNOpc"  # Замените на ваш токен!
bot = telebot.TeleBot(BOT_TOKEN)

# Настройки
CURSOR_SPEED = 50
SCROLL_SPEED = 100
admin_id = None  # ID первого пользователя будет администратором

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором"""
    return user_id == admin_id

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global admin_id
    if admin_id is None:
        admin_id = message.from_user.id
        bot.send_message(message.chat.id, "🔐 Вы установлены как администратор!")
    
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Доступ запрещен. Обратитесь к администратору.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('🖱 Управление курсором')
    btn2 = types.KeyboardButton('⌨️ Клавиатура')
    btn3 = types.KeyboardButton('📊 Система')
    btn4 = types.KeyboardButton('❓ Помощь')
    markup.add(btn1, btn2, btn3, btn4)
    
    welcome_text = """
👋 Привет! Я бот для управления компьютером

🖱 - Управление курсором и мышью
⌨️ - Эмуляция клавиатуры
📊 - Системные команды
❓ - Справка и помощь

⚠️ Бот запущен на целевом компьютере
    """
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    if not is_admin(message.from_user.id):
        return
    
    help_text = """
🤖 **Команды бота:**

/start - Запустить бота
/help - Показать справку
/cursor - Управление курсором
/keyboard - Эмуляция клавиатура
/system - Системные команды

🖱 **Управление курсором:**
⬆️⬇️⬅️➡️ - Движение курсора
🖱 ЛКМ - Левый клик мыши
🖱 ПКМ - Правый клик мыши
📸 - Сделать скриншот
🔄 - Двойной клик
🖱 Скролл - Прокрутка колесиком

⌨️ **Эмуляция клавиатуры:**
⏎ Enter - Клавиша Enter
⎋ Esc - Клавиша Escape
␣ Space - Пробел
⌨️ Tab - Клавиша Tab
📋 Вставить - Ctrl+V
✂️ Копировать - Ctrl+C
🔍 Поиск - Ctrl+F

📊 **Системные команды:**
🔒 Блокировка - Заблокировать компьютер
🔅 Яркость - Управление яркостью
🔊 Громкость - Управление звуком
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['cursor'])
def show_cursor_command(message):
    if not is_admin(message.from_user.id):
        return
    show_cursor_controls(message.chat.id)

@bot.message_handler(commands=['keyboard'])
def keyboard_command(message):
    if not is_admin(message.from_user.id):
        return
    show_keyboard_controls(message.chat.id)

@bot.message_handler(commands=['system'])
def system_command(message):
    if not is_admin(message.from_user.id):
        return
    show_system_controls(message.chat.id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_admin(message.from_user.id):
        return
    
    # Основное меню
    if message.text == '🖱 Управление курсором':
        show_cursor_controls(message.chat.id)
    elif message.text == '⌨️ Клавиатура':
        show_keyboard_controls(message.chat.id)
    elif message.text == '📊 Система':
        show_system_controls(message.chat.id)
    elif message.text == '❓ Помощь':
        send_help(message)
    
    # Управление курсором
    elif message.text in ['⬆️', '⬇️', '⬅️', '➡️']:
        handle_cursor_movement(message.chat.id, message.text)
    elif message.text == '🖱 ЛКМ':
        pyautogui.click()
        bot.send_message(message.chat.id, "✅ Левый клик мыши")
    elif message.text == '🖱 ПКМ':
        pyautogui.rightClick()
        bot.send_message(message.chat.id, "✅ Правый клик мыши")
    elif message.text == '🔄 Двойной':
        pyautogui.doubleClick()
        bot.send_message(message.chat.id, "✅ Двойной клик")
    elif message.text == '📸 Скриншот':
        take_screenshot(message.chat.id)
    elif message.text == '🖱 Скролл ▲':
        pyautogui.scroll(SCROLL_SPEED)
        bot.send_message(message.chat.id, "⬆️ Прокрутка вверх")
    elif message.text == '🖱 Скролл ▼':
        pyautogui.scroll(-SCROLL_SPEED)
        bot.send_message(message.chat.id, "⬇️ Прокрутка вниз")
    
    # Клавиатура
    elif message.text == '⏎ Enter':
        pyautogui.press('enter')
        bot.send_message(message.chat.id, "✅ Нажат Enter")
    elif message.text == '⎋ Esc':
        pyautogui.press('escape')
        bot.send_message(message.chat.id, "✅ Нажат Escape")
    elif message.text == '␣ Space':
        pyautogui.press('space')
        bot.send_message(message.chat.id, "✅ Нажат Пробел")
    elif message.text == '⌨️ Tab':
        pyautogui.press('tab')
        bot.send_message(message.chat.id, "✅ Нажат Tab")
    elif message.text == '📋 Вставить':
        pyautogui.hotkey('ctrl', 'v')
        bot.send_message(message.chat.id, "✅ Вставлено из буфера")
    elif message.text == '✂️ Копировать':
        pyautogui.hotkey('ctrl', 'c')
        bot.send_message(message.chat.id, "✅ Скопировано в буфер")
    elif message.text == '🔍 Поиск':
        pyautogui.hotkey('ctrl', 'f')
        bot.send_message(message.chat.id, "✅ Поиск активирован")
    
    # Системные команды
    elif message.text == '🔒 Блокировка':
        os.system("rundll32.exe user32.dll,LockWorkStation")
        bot.send_message(message.chat.id, "🔒 Компьютер заблокирован")
    elif message.text == '🔅 Яркость +':
        bot.send_message(message.chat.id, "🔅 Яркость увеличена")
    elif message.text == '🔅 Яркость -':
        bot.send_message(message.chat.id, "🔅 Яркость уменьшена")
    elif message.text == '🔊 Громкость +':
        pyautogui.press('volumeup')
        bot.send_message(message.chat.id, "🔊 Громкость увеличена")
    elif message.text == '🔊 Громкость -':
        pyautogui.press('volumedown')
        bot.send_message(message.chat.id, "🔊 Громкость уменьшена")
    elif message.text == '🔇 Mute':
        pyautogui.press('volumemute')
        bot.send_message(message.chat.id, "🔇 Звук отключен")
    
    # Навигация
    elif message.text == '🔙 Назад':
        send_welcome(message)

def show_cursor_controls(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    btn_up = types.KeyboardButton('⬆️')
    btn_down = types.KeyboardButton('⬇️')
    btn_left = types.KeyboardButton('⬅️')
    btn_right = types.KeyboardButton('➡️')
    
    btn_left_click = types.KeyboardButton('🖱 ЛКМ')
    btn_right_click = types.KeyboardButton('🖱 ПКМ')
    btn_double_click = types.KeyboardButton('🔄 Двойной')
    
    btn_screenshot = types.KeyboardButton('📸 Скриншот')
    btn_scroll_up = types.KeyboardButton('🖱 Скролл ▲')
    btn_scroll_down = types.KeyboardButton('🖱 Скролл ▼')
    
    btn_back = types.KeyboardButton('🔙 Назад')
    
    markup.add(btn_up, btn_left_click, btn_screenshot)
    markup.add(btn_left, btn_down, btn_right)
    markup.add(btn_right_click, btn_double_click, btn_scroll_up)
    markup.add(btn_scroll_down, btn_back)
    
    bot.send_message(chat_id, 
                    "🖱 **Управление курсором:**\n\n"
                    "⬆️⬇️⬅️➡️ - Движение курсора\n"
                    "🖱 ЛКМ - Левый клик\n"
                    "🖱 ПКМ - Правый клик\n"
                    "🔄 - Двойной клик\n"
                    "📸 - Скриншот экрана\n"
                    "🖱 Скролл - Прокрутка колесиком\n"
                    "🔙 - Назад в меню", 
                    reply_markup=markup,
                    parse_mode='Markdown')

def show_keyboard_controls(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    btn_enter = types.KeyboardButton('⏎ Enter')
    btn_escape = types.KeyboardButton('⎋ Esc')
    btn_space = types.KeyboardButton('␣ Space')
    btn_tab = types.KeyboardButton('⌨️ Tab')
    
    btn_paste = types.KeyboardButton('📋 Вставить')
    btn_copy = types.KeyboardButton('✂️ Копировать')
    btn_search = types.KeyboardButton('🔍 Поиск')
    
    btn_back = types.KeyboardButton('🔙 Назад')
    
    markup.add(btn_enter, btn_escape, btn_space)
    markup.add(btn_tab, btn_paste, btn_copy)
    markup.add(btn_search, btn_back)
    
    bot.send_message(chat_id,
                    "⌨️ **Эмуляция клавиатуры:**\n\n"
                    "⏎ Enter - Клавиша Enter\n"
                    "⎋ Esc - Клавиша Escape\n"
                    "␣ Space - Клавиша Пробел\n"
                    "⌨️ Tab - Клавиша Tab\n"
                    "📋 - Вставить (Ctrl+V)\n"
                    "✂️ - Копировать (Ctrl+C)\n"
                    "🔍 - Поиск (Ctrl+F)\n"
                    "🔙 - Назад в меню",
                    reply_markup=markup,
                    parse_mode='Markdown')

def show_system_controls(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    btn_lock = types.KeyboardButton('🔒 Блокировка')
    btn_brightness_up = types.KeyboardButton('🔅 Яркость +')
    btn_brightness_down = types.KeyboardButton('🔅 Яркость -')
    
    btn_volume_up = types.KeyboardButton('🔊 Громкость +')
    btn_volume_down = types.KeyboardButton('🔊 Громкость -')
    btn_mute = types.KeyboardButton('🔇 Mute')
    
    btn_back = types.KeyboardButton('🔙 Назад')
    
    markup.add(btn_lock, btn_brightness_up, btn_brightness_down)
    markup.add(btn_volume_up, btn_volume_down, btn_mute)
    markup.add(btn_back)
    
    bot.send_message(chat_id,
                    "📊 **Системные команды:**\n\n"
                    "🔒 - Заблокировать компьютер\n"
                    "🔅 - Управление яркостью\n"
                    "🔊 - Управление громкостью\n"
                    "🔇 - Отключить звук\n"
                    "🔙 - Назад в меню",
                    reply_markup=markup,
                    parse_mode='Markdown')

def handle_cursor_movement(chat_id, direction):
    try:
        if direction == '⬆️':
            pyautogui.move(0, -CURSOR_SPEED)
        elif direction == '⬇️':
            pyautogui.move(0, CURSOR_SPEED)
        elif direction == '⬅️':
            pyautogui.move(-CURSOR_SPEED, 0)
        elif direction == '➡️':
            pyautogui.move(CURSOR_SPEED, 0)
        
        x, y = pyautogui.position()
        bot.send_message(chat_id, f"✅ Курсор перемещен {direction}\n📍 Позиция: X={x}, Y={y}")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка перемещения: {str(e)}")

def take_screenshot(chat_id):
    try:
        # Создаем папку для скриншотов если нет
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        screenshot = pyautogui.screenshot()
        screenshot_path = f"screenshots/screenshot_{int(time.time())}.png"
        screenshot.save(screenshot_path)
        
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption="📸 Текущий экран")
        
        bot.send_message(chat_id, f"✅ Скриншот сохранен")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка создания скриншота: {str(e)}")

if __name__ == "__main__":
    print("🤖 Бот для управления компьютером запускается...")
    print("📍 Токен бота:", BOT_TOKEN)
    print("📋 Доступные функции:")
    print("   - Управление курсором мыши")
    print("   - Клики и скроллинг")
    print("   - Эмуляция клавиатуры")
    print("   - Системные команды")
    print("   - Скриншоты экрана")
    print("\n✅ Бот готов к работе!")
    print("📞 Ищите бота в Telegram и отправьте /start")
    
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("Проверьте токен бота и интернет соединение")
