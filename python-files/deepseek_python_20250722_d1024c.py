from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
import json
import os
import sys
import logging
import re

# Настройки
TOKEN = "7794593715:AAEZ_bGw50Thfk0Twr3DfVvMdiaQBISA1IU"
ADMIN_ID = 2031808258

# Определяем путь к файлу данных
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    DATA_FILE = os.path.join(base_dir, "bot_data.json")
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(base_dir, "bot_data.json")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
MAIN_MENU, ADD_USER, REMOVE_USER, SET_PRICE = range(4)

# Базовый текст с ценами
BASE_TEXT = """Цены:
МЕДНАЯ ГРУППА
Медь а1-1(блеск) : {медь_а1_1}Р
Медь а1-2(кусок) : {медь_а1_2}Р
Медь (разносорт.) : {медь_разносорт}Р
Газовая колонка : {газовая_колонка}Р
Медь (луж.) : {медь_луж}Р
ЛАТУННАЯ/БРОНЗОВАЯ ГРУППА
Бронза : {бронза}Р
Радиаторы : {радиаторы}Р
Латунь : {латунь}Р
АЛЮМИНИЙ:
Электротехнический : {алюминий_электро}Р
Пищевой : {алюминий_пищевой}Р
Профиль : {алюминий_профиль}Р
Моторный : {алюминий_моторный}Р
Микс : {алюминий_микс}Р
НЕРЖАВЕЙКА:
10% : {нержавейка_10}Р
8%: {нержавейка_8}Р
Свинец оболочка : {свинец_оболочка}Р
Свинец переплав : {свинец_переплав}Р
Цинк: {цинк}Р
АКБ сухие : {акб_сухие}Р"""

# Цены по умолчанию
DEFAULT_PRICES = {
    "медь_а1_1": 670,
    "медь_а1_2": 660,
    "медь_разносорт": 650,
    "газовая_колонка": 590,
    "медь_луж": 590,
    "бронза": 460,
    "радиаторы": 415,
    "латунь": 410,
    "алюминий_электро": 155,
    "алюминий_пищевой": 150,
    "алюминий_профиль": 140,
    "алюминий_моторный": 120,
    "алюминий_микс": 115,
    "нержавейка_10": 60,
    "нержавейка_8": 50,
    "свинец_оболочка": 120,
    "свинец_переплав": 110,
    "цинк": 120,
    "акб_сухие": 48
}

# Работа с данными
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Добавляем недостающие ключи цен
                for key, value in DEFAULT_PRICES.items():
                    if key not in data["prices"]:
                        data["prices"][key] = value
                return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
    
    return {
        "allowed_users": [],
        "prices": DEFAULT_PRICES.copy()
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

# Форматирование текста с ценами
def format_message(prices):
    return BASE_TEXT.format(**prices)

# Создание главного меню
def create_main_menu():
    keyboard = [
        [InlineKeyboardButton("👥 Добавить получателя", callback_data='add_user')],
        [InlineKeyboardButton("👥 Удалить получателя", callback_data='remove_user')],
        [InlineKeyboardButton("📋 Список получателей", callback_data='list_users')],
        [InlineKeyboardButton("💰 Изменить цену", callback_data='set_price_menu')],
        [InlineKeyboardButton("📤 Запустить рассылку", callback_data='broadcast')],
        [InlineKeyboardButton("ℹ️ Текущие цены", callback_data='show_prices')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Создание меню для выбора цены
def create_price_menu():
    keyboard = [
        [
            InlineKeyboardButton("Медь а1-1", callback_data='медь_а1_1'),
            InlineKeyboardButton("Медь а1-2", callback_data='медь_а1_2'),
            InlineKeyboardButton("Медь разносорт", callback_data='медь_разносорт')
        ],
        [
            InlineKeyboardButton("Газовая колонка", callback_data='газовая_колонка'),
            InlineKeyboardButton("Медь луж", callback_data='медь_луж'),
            InlineKeyboardButton("Бронза", callback_data='бронза')
        ],
        [
            InlineKeyboardButton("Радиаторы", callback_data='радиаторы'),
            InlineKeyboardButton("Латунь", callback_data='латунь'),
            InlineKeyboardButton("Алюминий электро", callback_data='алюминий_электро')
        ],
        [
            InlineKeyboardButton("Алюминий пищевой", callback_data='алюминий_пищевой'),
            InlineKeyboardButton("Алюминий профиль", callback_data='алюминий_профиль'),
            InlineKeyboardButton("Алюминий моторный", callback_data='алюминий_моторный')
        ],
        [
            InlineKeyboardButton("Алюминий микс", callback_data='алюминий_микс'),
            InlineKeyboardButton("Нержавейка 10%", callback_data='нержавейка_10'),
            InlineKeyboardButton("Нержавейка 8%", callback_data='нержавейка_8')
        ],
        [
            InlineKeyboardButton("Свинец оболочка", callback_data='свинец_оболочка'),
            InlineKeyboardButton("Свинец переплав", callback_data='свинец_переплав'),
            InlineKeyboardButton("Цинк", callback_data='цинк')
        ],
        [
            InlineKeyboardButton("АКБ сухие", callback_data='акб_сухие'),
            InlineKeyboardButton("🔙 Назад", callback_data='back')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    else:
        await update.message.reply_text(
            "👋 Привет! Этот бот предназначен для администратора."
        )
        return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.message.reply_text("❌ У вас нет прав доступа!")
        return ConversationHandler.END
    
    data = load_data()
    
    if query.data == 'add_user':
        await query.edit_message_text(
            "👤 Введите ID пользователя или номер телефона в формате +79123456789:"
        )
        return ADD_USER
    
    elif query.data == 'remove_user':
        if not data["allowed_users"]:
            await query.edit_message_text("📃 Список получателей пуст!")
            await query.message.reply_text(
                "⚡ Панель управления рассылкой",
                reply_markup=create_main_menu()
            )
            return MAIN_MENU
        
        users_list = "\n".join([f"• {uid}" for uid in data["allowed_users"]])
        await query.edit_message_text(
            f"📃 Текущие получатели:\n{users_list}\n\n"
            "➖ Введите ID или номер для удаления:"
        )
        return REMOVE_USER
    
    elif query.data == 'list_users':
        if not data["allowed_users"]:
            await query.edit_message_text("📃 Список получателей пуст!")
        else:
            users_list = "\n".join([f"• {uid}" for uid in data["allowed_users"]])
            await query.edit_message_text(f"📃 Получатели ({len(data['allowed_users']}):\n{users_list}")
        
        await query.message.reply_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    
    elif query.data == 'show_prices':
        formatted_text = format_message(data["prices"])
        await query.edit_message_text(f"📝 Текущие цены:\n\n{formatted_text}")
        await query.message.reply_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    
    elif query.data == 'set_price_menu':
        await query.edit_message_text(
            "💰 Выберите цену для изменения:",
            reply_markup=create_price_menu()
        )
        return MAIN_MENU
    
    elif query.data in DEFAULT_PRICES:
        context.user_data['selected_price'] = query.data
        current_price = data["prices"][query.data]
        await query.edit_message_text(
            f"✏️ Вы выбрали: {query.data.replace('_', ' ').title()}\n"
            f"Текущая цена: {current_price}Р\n\n"
            "Введите новую цену (только число):"
        )
        return SET_PRICE
    
    elif query.data == 'broadcast':
        if not data["allowed_users"]:
            await query.edit_message_text("⚠️ Нет получателей! Добавьте пользователей.")
            await query.message.reply_text(
                "⚡ Панель управления рассылкой",
                reply_markup=create_main_menu()
            )
            return MAIN_MENU
        
        await query.edit_message_text("📤 Начинаю рассылку...")
        # Получаем username бота для отправки ссылки
        bot_username = (await context.bot.get_me()).username
        bot_link = f"https://t.me/{bot_username}"

        message_text = format_message(data["prices"])
        success = 0
        failed = []
        not_started = []

        for user_id in data["allowed_users"]:
            try:
                # Для числовых ID отправляем напрямую
                if isinstance(user_id, int):
                    await context.bot.send_message(chat_id=user_id, text=message_text)
                    success += 1
                # Для номеров телефонов используем формат "phone:79123456789"
                elif isinstance(user_id, str) and user_id.startswith("phone:"):
                    phone = user_id.replace("phone:", "")
                    # Пытаемся отправить как контакт (но это работает только если пользователь добавил бота)
                    try:
                        await context.bot.send_message(chat_id=int(phone), text=message_text)
                        success += 1
                    except Exception as e:
                        # Если не получилось, сообщаем админу
                        error_msg = str(e)
                        if "Forbidden: user haven't started a chat with the bot" in error_msg:
                            not_started.append(phone)
                            await context.bot.send_message(
                                chat_id=ADMIN_ID,
                                text=f"ℹ️ Пользователь +{phone} не начал диалог с ботом. Отправьте ему ссылку:\n{bot_link}"
                            )
                        else:
                            failed.append(phone)
                else:
                    failed.append(str(user_id))
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Ошибка отправки {user_id}: {error_msg}")
                failed.append(str(user_id))

        report = f"📤 Рассылка завершена!\n• Успешно: {success}\n• Не удалось: {len(failed) + len(not_started)}"
        
        if not_started:
            report += f"\n• Не начинали диалог: {len(not_started)}"
        
        if failed:
            report += f"\n• Ошибки отправки: {len(failed)}"

        await query.message.reply_text(report)
        await query.message.reply_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    
    elif query.data == 'back':
        await query.edit_message_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    
    return MAIN_MENU

async def add_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    identifier = update.message.text.strip()
    data = load_data()
    
    # Проверяем формат (ID или номер)
    if re.match(r'^(\+7|8)\d{10}$', identifier.replace(" ", "")):
        # Нормализуем номер телефона
        phone = re.sub(r'\D', '', identifier)
        if phone.startswith('8'):
            phone = '7' + phone[1:]
        elif phone.startswith('+7'):
            phone = phone[1:]
        
        # Сохраняем как строку
        user_id = f"phone:{phone}"
    else:
        try:
            # Пробуем сохранить как числовой ID
            user_id = int(identifier)
        except ValueError:
            await update.message.reply_text("❌ Неверный формат! Используйте ID или номер телефона (+79123456789)")
            await update.message.reply_text(
                "⚡ Панель управления рассылкой",
                reply_markup=create_main_menu()
            )
            return MAIN_MENU

    # Проверка на дубликаты
    if user_id in data["allowed_users"]:
        await update.message.reply_text(f"⚠️ Пользователь уже в списке: {identifier}")
    else:
        data["allowed_users"].append(user_id)
        save_data(data)
        await update.message.reply_text(f"✅ Добавлен: {identifier}")
    
    await update.message.reply_text(
        "⚡ Панель управления рассылкой",
        reply_markup=create_main_menu()
    )
    return MAIN_MENU

async def remove_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    identifier = update.message.text.strip()
    data = load_data()
    removed = False
    
    # Нормализуем введенный идентификатор
    normalized_id = None
    if re.match(r'^(\+7|8)\d{10}$', identifier.replace(" ", "")):
        # Нормализуем номер телефона
        phone = re.sub(r'\D', '', identifier)
        if phone.startswith('8'):
            phone = '7' + phone[1:]
        elif phone.startswith('+7'):
            phone = phone[1:]
        normalized_id = f"phone:{phone}"
    else:
        try:
            normalized_id = int(identifier)
        except ValueError:
            normalized_id = identifier

    # Ищем в списке
    if normalized_id in data["allowed_users"]:
        data["allowed_users"].remove(normalized_id)
        save_data(data)
        removed = True
    
    if removed:
        await update.message.reply_text(f"✅ Удален: {identifier}")
    else:
        await update.message.reply_text(f"⚠️ Пользователь не найден: {identifier}")
    
    await update.message.reply_text(
        "⚡ Панель управления рассылкой",
        reply_markup=create_main_menu()
    )
    return MAIN_MENU

async def set_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_price = update.message.text.strip()
    price_key = context.user_data.get('selected_price')
    
    if not price_key:
        await update.message.reply_text("❌ Ошибка! Пожалуйста, начните заново.")
        await update.message.reply_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    
    try:
        new_price_value = int(new_price)
    except ValueError:
        await update.message.reply_text("❌ Цена должна быть числом! Попробуйте еще раз.")
        return SET_PRICE
    
    data = load_data()
    old_price = data["prices"][price_key]
    data["prices"][price_key] = new_price_value
    save_data(data)
    
    # Преобразуем ключ в читаемое название
    price_name = price_key.replace('_', ' ').title()
    
    await update.message.reply_text(f"✅ Цена изменена!\n{price_name}: {old_price}Р → {new_price_value}Р")
    await update.message.reply_text(
        "⚡ Панель управления рассылкой",
        reply_markup=create_main_menu()
    )
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_ID:
        await update.message.reply_text(
            "⚡ Панель управления рассылкой",
            reply_markup=create_main_menu()
        )
        return MAIN_MENU
    return ConversationHandler.END

# Основная функция
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button_handler)
            ],
            ADD_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_handler)
            ],
            REMOVE_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, remove_user_handler)
            ],
            SET_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_price_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    
    # Запуск бота
    logger.info("Бот запущен. Ожидание команд...")
    application.run_polling()

if __name__ == "__main__":
    main()