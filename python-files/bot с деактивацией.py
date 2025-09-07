import asyncio
import random
import base64
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# --- Конфигурация ---
BOT_TOKEN = "8057199872:AAETD-t8t4HGNQ0SHFA0snftDSxkqyYbQAM"
TICKET_PRICE = 48
TIMEZONE_OFFSET = timedelta(hours=7)  # UTC+7
BUS_REGION = "124"  # Регион для номера автобуса по умолчанию
MINI_APP_URL = "https://busticket-three.vercel.app/"  # URL Mini App

# --- Данные о маршрутах и перевозчиках ---
routes_data = {   
    "1": {
        "name": "мкрн. Северный - мкрн. Тихие зори",
        "carriers": {
            "МП Городской транспорт": "МП Городской транспорт"
        }
    },
    "2": {
        "name": "Дом ученых - А/В Восточный",
        "carriers": {
            "ИП Галченкова Е. А.": "ИП Галченкова Е. А.",
            "ИП Багаев Д.Б.": "ИП Багаев Д.Б."
        }
    },
    "3": {
        "name": "Академгородок - А/В Восточный",
        "carriers": {
            "ООО \"СКАД\"": "ООО \"СКАД\"",
            "ООО Перевозчик": "ООО Перевозчик" #Не факт мб убрать
        }
    },
    "5": {
        "name": "Спорткомплекс Радуга - ОАО Красфарма",
        "carriers": {
            "ИП Долгушина Г.И.": "ИП Долгушина Г.И."#Не факт мб изменить
        } 
    },        
    "21": {
        "name": "Парк \"Прищеpка\" - Спортзал",
        "carriers": {
            "ООО \"СТК\"": "ООО \"СТК\"",
            "ИП Патрин Н. Н.": "ИП Патрин Н. Н."
        }
    },
    "23": {
        "name": "ЛДК - Солнечный (60-летия СССР)",
        "carriers": {
            "ООО Ветеран": "ООО Ветеран"
        }
    },
    "31": {
        "name": "ЛДК - Академия биатлона",
        "carriers": {
            "КПАТП-7": "КПАТП-7"
        }
    },        
    "52": {
        "name": "ЛДК - Озеро-парк",
        "carriers": {
            "КПАТП-5": "КПАТП-5"
        }
    },       
    "65": {
        "name": "ДК Кировский - Агротерминал",
        "carriers": {
            "ИП Ялтонский А. М.": "ИП Ялтонский А. М."
        }
    }, 
    "85": {
        "name": "Даурская - Сельхозкомплекс",
        "carriers": {
            "ООО \"СТК\"": "ООО \"СТК\"",
            "ООО \"СКАД\"": "ООО \"СКАД\""
        } 
    }, 
    "88": {
        "name": "Спортзал - Академия биатлона",
        "carriers": {
            "ИП Тагачаков В. Г.": "ИП Тагачаков В. Г."
        } 
    },            
    "90": {
        "name": "Ак. биатлона-Верхн. Базаиха",
        "carriers": {
            "ИП Патрин Н. Н.": "ИП Патрин Н. Н.",
            "ООО \"СКАД\"": "ООО \"СКАД\""
        } 
    }, 
    "94": {
        "name": "ЛДК - ТЭЦ-3",
        "carriers": {
            "ООО Практик": "ООО Практик",
            "ООО МаршрутАвто": "ООО МаршрутАвто",
            "ИП Карасева Н. Н.": "ИП Карасева Н. Н."
        }
    },       
    "95": {
        "name": "Верхние Черемушки-ЛДК", 
        "carriers": {
            "КПАТП-7": "КПАТП-7"
        }
    },
    "98": {
        "name": "ЛДК - ОАО \"РУСАЛ\"",  
        "carriers": {
            "ИП Гнетов Ю. Н.": "ИП Гнетов Ю. Н."
        }
    }    
}

# --- Машина состояний (FSM) ---
class TicketPurchase(StatesGroup):
    waiting_route = State()
    waiting_carrier = State()
    waiting_bus = State()
    waiting_quantity = State()

# --- Инициализация бота и диспетчера ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения информации о билетах
active_tickets = {}

# --- Вспомогательные функции ---
def get_carrier_keyboard(route_number: str) -> ReplyKeyboardMarkup:
    """Создает клавиатуру с перевозчиками для выбранного маршрута"""
    builder = ReplyKeyboardBuilder()
    carriers = routes_data[route_number]["carriers"]
    
    for carrier in carriers.values():
        builder.add(KeyboardButton(text=carrier))
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def format_ticket_number(number: int) -> str:
    """Форматирует номер билета с пробелами"""
    return f"{number:,}".replace(",", " ")

async def delete_messages(chat_id: int, message_ids: list):
    """Удаляет список сообщений"""
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            # Игнорируем ошибки удаления (сообщение уже удалено или нет прав)
            pass

async def check_ticket_expiry():
    """Периодически проверяет истекшие билеты и обновляет сообщения"""
    while True:
        await asyncio.sleep(30)  # Проверяем каждые 30 секунд
        
        current_time = datetime.utcnow() + TIMEZONE_OFFSET
        expired_tickets = []
        
        for ticket_id, ticket_info in active_tickets.items():
            if current_time >= ticket_info["valid_until"]:
                chat_id, message_id = ticket_id
                
                # Создаем неактивную кнопку
                keyboard = InlineKeyboardBuilder()
                keyboard.row(InlineKeyboardButton(
                    text="Срок действия билета закончился", 
                    callback_data="expired_ticket"
                ))
                
                try:
                    # Редактируем только кнопку, сохраняя текст сообщения
                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=keyboard.as_markup()
                    )
                    expired_tickets.append(ticket_id)
                except Exception as e:
                    print(f"Ошибка при обновлении кнопки: {e}")
        
        # Удаляем обработанные билеты из активных
        for ticket_id in expired_tickets:
            active_tickets.pop(ticket_id, None)

# Обработчик для неактивной кнопки
@dp.callback_query(F.data == "expired_ticket")
async def handle_expired_ticket(callback: types.CallbackQuery):
    # Просто отвечаем на callback, но ничего не делаем
    await callback.answer()

# --- Хэндлеры ---

# Start command - сразу начинаем процесс покупки
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Пытаемся удалить сообщение с командой /start
    try:
        await message.delete()
    except:
        pass
    
    # Очищаем состояние и инициализируем список сообщений для удаления
    await state.clear()
    await state.set_data({"messages_to_delete": []})
    
    # Сразу переходим к запросу номера маршрута
    await ask_for_route(message, state)

async def ask_for_route(message: types.Message, state: FSMContext):
    """Запрос номера маршрута"""
    msg = await message.answer(
        "Введите номер маршрута (например: 94):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    # Сохраняем ID сообщения для последующего удаления
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    
    await state.set_state(TicketPurchase.waiting_route)

# Обработка ввода номера маршрута
@dp.message(TicketPurchase.waiting_route)
async def process_route(message: types.Message, state: FSMContext):
    # Сохраняем ID сообщения пользователя для удаления
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    
    route_number = message.text.strip()
    
    if route_number not in routes_data:
        msg = await message.answer("❌ Маршрут не найден. Введите корректный номер маршрута:")
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    await state.update_data(route_number=route_number)
    
    # Получаем клавиатуру с перевозчиками для этого маршрута
    keyboard = get_carrier_keyboard(route_number)
    
    msg = await message.answer(
        f"Маршрут {route_number} - {routes_data[route_number]['name']}\n"
        "Выберите перевозчика:",
        reply_markup=keyboard
    )
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(TicketPurchase.waiting_carrier)

# Обработка выбора перевозчика
@dp.message(TicketPurchase.waiting_carrier)
async def process_carrier(message: types.Message, state: FSMContext):
    # Сохраняем ID сообщения пользователя для удаления
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    
    carrier = message.text.strip()
    data = await state.get_data()
    route_number = data['route_number']
    
    # Проверяем, что выбранный перевозчик есть для этого маршрута
    if carrier not in routes_data[route_number]["carriers"].values():
        msg = await message.answer("❌ Пожалуйста, выберите перевозчика из предложенных вариантов:")
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    await state.update_data(carrier=carrier)
    msg = await message.answer(
        "Введите номер автобуса (первые 6 символов, например: x677ca).\n"
        "Или полный номер с регионом (например: x677ca777):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(TicketPurchase.waiting_bus)

# Обработка ввода номера автобуса
@dp.message(TicketPurchase.waiting_bus)
async def process_bus(message: types.Message, state: FSMContext):
    # Сохраняем ID сообщения пользователя для удаления
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    
    bus_input = message.text.strip()
    
    # Проверяем формат номера автобуса
    if len(bus_input) == 6 and bus_input.isalnum():
        # Пользователь ввел только первые 6 символов, добавляем регион по умолчанию
        full_bus_number = f"{bus_input}{BUS_REGION}"
    elif len(bus_input) >= 7 and bus_input.isalnum():
        # Пользователь ввел полный номер с регионом, используем как есть
        full_bus_number = bus_input
    else:
        msg = await message.answer("❌ Номер автобуса должен состоять из букв и цифр. Попробуйте еще раз:")
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    await state.update_data(bus_number=full_bus_number)
    msg = await message.answer("Введите количество билетов:")
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(TicketPurchase.waiting_quantity)

# Обработка ввода количества билетов
@dp.message(TicketPurchase.waiting_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    # Сохраняем ID сообщения пользователя для удаления
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        msg = await message.answer("❌ Пожалуйста, введите корректное число (больше 0):")
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    # Получаем все данные из состояния
    data = await state.get_data()
    route_number = data['route_number']
    route_name = routes_data[route_number]['name']
    carrier = data['carrier']
    bus_number = data['bus_number']
    messages_to_delete = data.get("messages_to_delete", [])
    
    total_price = TICKET_PRICE * quantity
    
    # Генерируем билет
    ticket_number = random.randint(1220000000, 1300000000)
    purchase_time = datetime.utcnow() + TIMEZONE_OFFSET
    valid_until = purchase_time + timedelta(hours=2)  # Действует 2 часа
    
    # Форматируем время
    valid_until_str = valid_until.strftime("%H:%M")
    purchase_time_str = purchase_time.strftime("%H:%M")
    months_ru = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    purchase_date_str = f"{purchase_time.day} {months_ru[purchase_time.month-1]} {purchase_time.year} г."
    
    # Форматируем номер билета с пробелами
    formatted_ticket_number = format_ticket_number(ticket_number)
    
    # Формируем сообщение с билетом
    ticket_message = (
        f"<b>Билет куплен успешно.</b>\n"
        f"{carrier}\n"
        f"🚏 {route_number} {route_name}\n"
        f"🚌 {bus_number}\n"
        f"🪙 Тариф: Полный {total_price},00 ₽\n"
        f"🎫 Билет № {formatted_ticket_number}\n"
        f"🕑 Действует до {valid_until_str}"
    )
    
    # Создаем кнопку "Предъявить билет" с Mini App
    ticket_data = {
        "number": ticket_number,
        "route_number": route_number,
        "route_name": route_name,
        "carrier": carrier,
        "bus_number": bus_number,
        "valid_until": valid_until_str,
        "price": TICKET_PRICE,
        "quantity": quantity,
        "total_price": total_price,
        "purchase_time": purchase_time_str,
        "purchase_date": purchase_date_str 
    }
    
    ticket_data_json = json.dumps(ticket_data)
    ticket_data_b64 = base64.urlsafe_b64encode(ticket_data_json.encode()).decode()
    
    # Формируем URL для Mini App с данными билета
    mini_app_url = f"{MINI_APP_URL}?data={ticket_data_b64}"
    
    # Создаем кнопку с WebApp
    web_app = WebAppInfo(url=mini_app_url)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="🎫 Предъявить билет", web_app=web_app))
    
    # Удаляем все предыдущие сообщения (и бота, и пользователя)
    await delete_messages(message.chat.id, messages_to_delete)
    
    # Отправляем финальное сообщение с билетом
    sent_message = await message.answer(
        ticket_message,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    
    # Сохраняем информацию о билете для отслеживания истечения срока
    ticket_id = (message.chat.id, sent_message.message_id)
    active_tickets[ticket_id] = {
        "ticket_number": ticket_number,
        "route_number": route_number,
        "route_name": route_name,
        "carrier": carrier,
        "bus_number": bus_number,
        "total_price": total_price,
        "valid_until": valid_until
    }
    
    await state.clear()

# --- Запуск бота и задачи проверки истечения билетов ---
async def main():
    # Запускаем задачу проверки истечения билетов в фоне
    asyncio.create_task(check_ticket_expiry())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())