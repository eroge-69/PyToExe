import logging
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
API_TOKEN = '8090412206:AAF5B4liHCFt_V99zXz4a8YSZwKJDLpiPkA'
ADMIN_IDS = [1245323483]

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Контекстный менеджер для работы с БД
@contextmanager
def db_connection():
    conn = sqlite3.connect('media_center.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Инициализация базы данных
def init_db():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS applications
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           username TEXT,
                           date TEXT,
                           location TEXT,
                           time TEXT,
                           event_type TEXT,
                           specialist TEXT,
                           equipment TEXT,
                           status TEXT DEFAULT 'new',
                           is_admin BOOLEAN DEFAULT FALSE,
                           admin_id INTEGER,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS admins
                          (user_id INTEGER PRIMARY KEY,
                           notifications_enabled INTEGER DEFAULT 1)''')

        for admin_id in ADMIN_IDS:
            cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (admin_id,))
        conn.commit()


init_db()


# Определение состояний
class ApplicationStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_location = State()
    waiting_for_time = State()
    waiting_for_event_type = State()
    waiting_for_specialist = State()
    waiting_for_equipment = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast = State()


# Валидация даты
def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False


# Команда /cancel
@dp.message(Command('cancel'))
@dp.message(F.text.casefold() == 'cancel')
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        return

    await state.clear()
    await message.answer(
        "❌ Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

    if message.from_user.id in ADMIN_IDS:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Создать заявку"), KeyboardButton(text="Список заявок")],
                [KeyboardButton(text="Настройки уведомлений"), KeyboardButton(text="Статистика")]
            ],
            resize_keyboard=True
        )
        await message.answer("Админ-меню:", reply_markup=keyboard)


# Команда /start
@dp.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    if message.from_user.id in ADMIN_IDS:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Создать заявку"), KeyboardButton(text="Список заявок")],
                [KeyboardButton(text="Настройки уведомлений"), KeyboardButton(text="Статистика")]
            ],
            resize_keyboard=True
        )
        await message.answer("Привет, админ! Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer(
            "Привет! Это бот для подачи заявок на мероприятия. Давай начнем оформление заявки.\n\n"
            "Когда состоится мероприятие? (укажите дату в формате ДД.ММ.ГГГГ)\n"
            "Для отмены введите /cancel"
        )
        await state.set_state(ApplicationStates.waiting_for_date)


# Обработчик кнопки "Создать заявку" для админа
@dp.message(F.text == "Создать заявку", F.from_user.id.in_(ADMIN_IDS))
async def admin_create_application(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f"Админ {message.from_user.id} начал создание заявки")

    await message.answer(
        "Вы начали создание новой заявки от имени администратора.\n\n"
        "Когда состоится мероприятие? (укажите дату в формате ДД.ММ.ГГГГ)\n"
        "Для отмены введите /cancel",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(ApplicationStates.waiting_for_date)
    await state.update_data(is_admin=True, admin_id=message.from_user.id)


# Обработка даты мероприятия
@dp.message(ApplicationStates.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ\nПопробуйте еще раз:")
        return

    await state.update_data(
        date=message.text,
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    await message.answer("✅ Дата принята!\nГде будет проходить мероприятие? (укажите адрес или название места)")
    await state.set_state(ApplicationStates.waiting_for_location)


# Обработка локации
@dp.message(ApplicationStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("✅ Локация принята!\nВ какое время будет мероприятие? (укажите время начала и окончания)")
    await state.set_state(ApplicationStates.waiting_for_time)


# Обработка времени
@dp.message(ApplicationStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("✅ Время принято!\nЧто это за мероприятие? (кратко опишите)")
    await state.set_state(ApplicationStates.waiting_for_event_type)


# Обработка типа мероприятия
@dp.message(ApplicationStates.waiting_for_event_type)
async def process_event_type(message: Message, state: FSMContext):
    await state.update_data(event_type=message.text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Фотограф"), KeyboardButton(text="Видеограф"), KeyboardButton(text="Клипмейкер")],
            [KeyboardButton(text="Фотограф + Видеограф"), KeyboardButton(text="Другое")]
        ],
        resize_keyboard=True
    )

    await message.answer("✅ Тип мероприятия принят!\nКакой специалист нужен?", reply_markup=keyboard)
    await state.set_state(ApplicationStates.waiting_for_specialist)


# Обработка специалиста
@dp.message(ApplicationStates.waiting_for_specialist)
async def process_specialist(message: Message, state: FSMContext):
    await state.update_data(specialist=message.text)
    await message.answer(
        "✅ Специалист выбран!\nКакая аппаратура нужна? (опишите подробно)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ApplicationStates.waiting_for_equipment)


# Обработка аппаратуры и сохранение в БД
@dp.message(ApplicationStates.waiting_for_equipment)
async def process_equipment(message: Message, state: FSMContext):
    data = await state.get_data()
    data['equipment'] = message.text

    try:
        with db_connection() as conn:
            cursor = conn.cursor()

            # Проверяем существование колонок
            cursor.execute("PRAGMA table_info(applications)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'is_admin' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            if 'admin_id' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN admin_id INTEGER")

            # Сохраняем заявку
            cursor.execute('''INSERT INTO applications 
                            (user_id, username, date, location, time, event_type, 
                             specialist, equipment, is_admin, admin_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (data['user_id'], data['username'], data['date'],
                            data['location'], data['time'], data['event_type'],
                            data['specialist'], data['equipment'],
                            data.get('is_admin', False),
                            data.get('admin_id')))
            conn.commit()
            application_id = cursor.lastrowid

            application_text = (
                "📋 Новая заявка на мероприятие:\n\n"
                f"🆔 ID: #{application_id}\n"
                f"📅 Дата: {data['date']}\n"
                f"📍 Локация: {data['location']}\n"
                f"⏰ Время: {data['time']}\n"
                f"🎉 Мероприятие: {data['event_type']}\n"
                f"👨‍💻 Нужен: {data['specialist']}\n"
                f"📷 Аппаратура: {data['equipment']}\n\n"
                f"От: @{data['username']} (#id{data['user_id']})"
            )

            if data.get('is_admin'):
                application_text += "\n\n⚠️ Заявка создана администратором"

            # Отправка уведомления админам
            for admin_id in ADMIN_IDS:
                try:
                    cursor.execute("SELECT notifications_enabled FROM admins WHERE user_id=?", (admin_id,))
                    result = cursor.fetchone()
                    notification_enabled = result['notifications_enabled'] if result else True

                    if notification_enabled:
                        await bot.send_message(
                            chat_id=admin_id,
                            text=f"🚀 Новая заявка #{application_id}:\n\n{application_text}",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="Ответить",
                                        callback_data=f"reply_{data['user_id']}"
                                    ),
                                    InlineKeyboardButton(
                                        text="В работу",
                                        callback_data=f"status_working_{application_id}"
                                    )
                                ]
                            ])
                        )
                except Exception as e:
                    logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")

        await message.answer("✅ Спасибо! Ваша заявка принята:\n\n" + application_text)

        # Если это админ - возвращаем в админ-меню
        if data.get('is_admin'):
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Создать заявку"), KeyboardButton(text="Список заявок")],
                    [KeyboardButton(text="Настройки уведомлений"), KeyboardButton(text="Статистика")]
                ],
                resize_keyboard=True
            )
            await message.answer("Возврат в админ-меню:", reply_markup=keyboard)

        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при сохранении заявки: {e}")
        await message.answer("❌ Произошла ошибка при сохранении заявки. Попробуйте позже.")
        await state.clear()


# Админ: список заявок
@dp.message(F.text == "Список заявок", F.from_user.id.in_(ADMIN_IDS))
async def admin_list_applications(message: Message):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, event_type, date, status FROM applications ORDER BY created_at DESC LIMIT 10")
        applications = cursor.fetchall()

    if not applications:
        await message.answer("Заявок пока нет.")
        return

    text = "📂 Последние заявки:\n\n"
    for app in applications:
        text += f"#{app['id']} - {app['event_type']} ({app['date']}) - {app['status']}\n"

    text += "\nИспользуйте /app <ID> для просмотра деталей (например /app 1)"
    await message.answer(text)


# Просмотр деталей заявки
@dp.message(Command('app'), F.from_user.id.in_(ADMIN_IDS))
async def admin_application_details(message: Message):
    try:
        app_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if not app_id:
            raise ValueError("Не указан ID заявки")

        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications WHERE id=?", (app_id,))
            app = cursor.fetchone()

        if not app:
            await message.answer("Заявка не найдена.")
            return

        text = (
            f"📋 Заявка #{app['id']}\n\n"
            f"👤 Пользователь: @{app['username']} (#id{app['user_id']})\n"
            f"📅 Дата: {app['date']}\n"
            f"📍 Локация: {app['location']}\n"
            f"⏰ Время: {app['time']}\n"
            f"🎉 Мероприятие: {app['event_type']}\n"
            f"👨‍💻 Специалист: {app['specialist']}\n"
            f"📷 Аппаратура: {app['equipment']}\n"
            f"🔄 Статус: {app['status']}\n"
            f"📅 Создана: {app['created_at']}"
        )

        if app['is_admin']:
            text += "\n\n⚠️ Заявка создана Руководством"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"reply_{app['user_id']}"
                ),
                InlineKeyboardButton(
                    text="В работу" if app['status'] == 'new' else "Завершить",
                    callback_data=f"status_{'working' if app['status'] == 'new' else 'completed'}_{app['id']}"
                )
            ]
        ])

        await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка просмотра заявки: {e}")
        await message.answer("❌ Ошибка: Используйте /app <ID заявки>")


# Админ: настройки уведомлений
@dp.message(F.text == "Настройки уведомлений", F.from_user.id.in_(ADMIN_IDS))
async def admin_notification_settings(message: Message):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT notifications_enabled FROM admins WHERE user_id=?", (message.from_user.id,))
        result = cursor.fetchone()
        current_status = result['notifications_enabled'] if result else True

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Уведомления: {'ВКЛ' if current_status else 'ВЫКЛ'}",
                callback_data="toggle_notifications"
            )
        ]
    ])

    await message.answer("Настройки уведомлений:", reply_markup=keyboard)


# Админ: статистика
@dp.message(F.text == "Статистика", F.from_user.id.in_(ADMIN_IDS))
async def admin_stats(message: Message):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM applications")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM applications WHERE status='new'")
        new = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM applications WHERE status='working'")
        working = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM applications WHERE status='completed'")
        completed = cursor.fetchone()[0]

    text = (
        "📊 Статистика заявок:\n\n"
        f"Всего заявок: {total}\n"
        f"🆕 Новые: {new}\n"
        f"🔄 В работе: {working}\n"
        f"✅ Завершенные: {completed}"
    )

    await message.answer(text)


# Обработка callback-запросов
@dp.callback_query(F.data.startswith('reply_'))
async def process_callback_reply(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[1])
    await callback.answer()
    await callback.message.answer(f"✏️ Введите сообщение для пользователя #{user_id}:")
    await state.set_state(AdminStates.waiting_for_broadcast)
    await state.update_data(reply_to=user_id)


@dp.callback_query(F.data.startswith('status_'))
async def process_callback_status(callback: CallbackQuery):
    parts = callback.data.split('_')
    if len(parts) < 3:
        await callback.answer("❌ Ошибка в данных")
        return

    action = parts[1]
    app_id = parts[2]
    new_status = 'working' if action == 'working' else 'completed'

    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE applications SET status=? WHERE id=?", (new_status, app_id))
        conn.commit()

    await callback.answer(f"✅ Статус изменен на {new_status}")
    await callback.message.delete()
    await callback.message.answer(f"Статус заявки #{app_id} изменен на {new_status}")


@dp.callback_query(F.data == 'toggle_notifications')
async def process_callback_toggle_notifications(callback: CallbackQuery):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT notifications_enabled FROM admins WHERE user_id=?", (callback.from_user.id,))
        result = cursor.fetchone()
        current_status = result['notifications_enabled'] if result else True

        new_status = 0 if current_status else 1

        cursor.execute("UPDATE admins SET notifications_enabled=? WHERE user_id=?",
                       (new_status, callback.from_user.id))
        conn.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Уведомления: {'ВКЛ' if new_status else 'ВЫКЛ'}",
                callback_data="toggle_notifications"
            )
        ]
    ])

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer(f"Уведомления {'включены ✅' if new_status else 'выключены ⚠️'}")


# Обработка сообщений админа для пересылки
@dp.message(AdminStates.waiting_for_broadcast)
async def process_admin_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('reply_to')
    if not user_id:
        await message.answer("❌ Ошибка: не найден получатель")
        await state.clear()
        return

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✉️ Сообщение от администратора:\n\n{message.text}"
        )
        await message.answer("✅ Сообщение отправлено!")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        await message.answer(f"❌ Не удалось отправить сообщение: {e}")
    finally:
        await state.clear()


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.info("Бот запущен")
    import asyncio

    asyncio.run(main())