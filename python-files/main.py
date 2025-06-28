import telebot
import pyautogui
import keyboard
import threading
from telebot import types

# Настройки
TOKEN = '8148077665:AAEOBjwAMJRvfegVUv_3TwnKaFTNFWB_OvQ'  # Замените на ваш токен
AUTHORIZED_USERS = []  # Добавьте сюда ID пользователей, которым разрешено управление

bot = telebot.TeleBot(TOKEN)

class ControlState:
    def __init__(self):
        self.mouse_locked = False
        self.keyboard_locked = False
        self.block_active = False
        self.block_thread = None

state = ControlState()

def is_authorized(user_id):
    """Проверяет, авторизован ли пользователь"""
    return not AUTHORIZED_USERS or user_id in AUTHORIZED_USERS

def create_keyboard():
    """Создает клавиатуру управления"""
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    
    btn_up = types.KeyboardButton('⬆️')
    btn_left = types.KeyboardButton('⬅️')
    btn_right = types.KeyboardButton('➡️')
    btn_down = types.KeyboardButton('⬇️')
    btn_lmb = types.KeyboardButton('ЛКМ')
    btn_rmb = types.KeyboardButton('ПКМ')
    btn_lock_mouse = types.KeyboardButton('🔒 Мышь' if not state.mouse_locked else '🔓 Мышь')
    btn_lock_keyboard = types.KeyboardButton('🔒 Клавиатура' if not state.keyboard_locked else '🔓 Клавиатура')
    
    markup.add(btn_up)
    markup.add(btn_left, btn_right)
    markup.add(btn_down)
    markup.add(btn_lmb, btn_rmb)
    markup.add(btn_lock_mouse, btn_lock_keyboard)
    
    return markup

def block_inputs():
    """Блокирует ввод мыши и клавиатуры"""
    while state.block_active:
        if state.mouse_locked:
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(pyautogui.size().width // 2, pyautogui.size().height // 2)
        
        if state.keyboard_locked:
            # Блокируем все клавиши (более эффективный способ)
            for key in ['ctrl', 'alt', 'shift', 'win', 'tab', 'esc', 'enter', 'space']:
                keyboard.block_key(key)

@bot.message_handler(commands=['start'])
def handle_start(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "🚫 У вас нет доступа к этому боту.")
        return
    
    bot.send_message(
        message.chat.id,
        "🖥️ Управление компьютером:\n"
        "⬆️⬅️⬇️➡️ - Движение мыши\n"
        "ЛКМ/ПКМ - Клики мыши\n"
        "🔒 Мышь/Клавиатура - Блокировка ввода",
        reply_markup=create_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_authorized(message.from_user.id):
        return
    
    step = 20  # Шаг движения мыши
    
    try:
        if message.text == '⬆️':
            pyautogui.move(0, -step)
        elif message.text == '⬇️':
            pyautogui.move(0, step)
        elif message.text == '⬅️':
            pyautogui.move(-step, 0)
        elif message.text == '➡️':
            pyautogui.move(step, 0)
        elif message.text == 'ЛКМ':
            pyautogui.click()
        elif message.text == 'ПКМ':
            pyautogui.click(button='right')
        elif message.text in ['🔒 Мышь', '🔓 Мышь']:
            state.mouse_locked = not state.mouse_locked
            bot.send_message(message.chat.id, f"Мышь {'заблокирована' if state.mouse_locked else 'разблокирована'}", 
                           reply_markup=create_keyboard())
        elif message.text in ['🔒 Клавиатура', '🔓 Клавиатура']:
            state.keyboard_locked = not state.keyboard_locked
            bot.send_message(message.chat.id, f"Клавиатура {'заблокирована' if state.keyboard_locked else 'разблокирована'}", 
                           reply_markup=create_keyboard())
        
        # Управление блокировкой
        if (state.mouse_locked or state.keyboard_locked) and not state.block_active:
            state.block_active = True
            state.block_thread = threading.Thread(target=block_inputs, daemon=True)
            state.block_thread.start()
        elif not state.mouse_locked and not state.keyboard_locked and state.block_active:
            state.block_active = False
            if state.block_thread:
                state.block_thread.join(timeout=1)
            keyboard.unhook_all()  # Разблокируем клавиатуру
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    print("Бот запущен...")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Бот остановлен")
        if state.block_thread:
            state.block_active = False
            state.block_thread.join(timeout=1)
        keyboard.unhook_all()
