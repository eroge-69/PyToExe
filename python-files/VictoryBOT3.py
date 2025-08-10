import telebot
from telebot import types
import logging
import sqlite3
from datetime import datetime
import pickle
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = '8470801392:AAGqSAGR_o5yMNWSfOHSe7WOt83-DMBoS98'
bot = telebot.TeleBot(BOT_TOKEN)

# ID врачей и их специальности
DOCTORS = {
    980272270: {'name': 'Терапевт'},
    1259421542: {'name': 'Хирург'},
    1234567890: {'name': 'ЛОР'}
}

# Состояния для FSM
(
    STATE_REGISTRATION,
    STATE_ENTERING_FIRST_NAME,
    STATE_ENTERING_LAST_NAME,
    STATE_ENTERING_PATRONYMIC,
    STATE_ENTERING_BIRTH_DATE,
    STATE_ENTERING_PHONE,
    STATE_CHOOSING_DOCTOR,
    STATE_ENTERING_PET_NAME,
    STATE_WRITING_TO_DOCTOR,
    STATE_DOCTOR_RESPONSE,
    STATE_EDITING_PROFILE,
    STATE_EDITING_FIELD
) = range(12)

# Словарь для хранения состояний
user_states = {}
STATE_FILE = 'user_states.pkl'

def load_states():
    """Загружает состояния пользователей из файла"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки состояний: {e}")
    return {}

def save_states():
    """Сохраняет состояния пользователей в файл"""
    try:
        with open(STATE_FILE, 'wb') as f:
            pickle.dump(user_states, f)
    except Exception as e:
        logger.error(f"Ошибка сохранения состояний: {e}")

def reset_user_state(chat_id):
    """Сбрасывает состояние пользователя"""
    if chat_id in user_states:
        del user_states[chat_id]
        logger.info(f"Сброшено состояние для чата {chat_id}")

def is_valid_date(date_str):
    """Проверяет корректность даты в формате дд.мм.гггг"""
    try:
        day, month, year = map(int, date_str.split('.'))
        if year < 1900 or year > datetime.now().year:
            return False
        datetime(year=year, month=month, day=day)
        return True
    except (ValueError, AttributeError):
        return False

def init_db():
    """Инициализация базы данных"""
    try:
        conn = sqlite3.connect('clinic.db')
        cursor = conn.cursor()

        # Таблица для сообщений
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_type TEXT CHECK(message_type IN (
                'patient_to_doctor', 'doctor_to_patient', 'system', 
                'patient_action', 'doctor_action', 'registration',
                'system_error'
            )),
            patient_id INTEGER,
            patient_name TEXT,
            doctor_id INTEGER,
            doctor_specialty TEXT,
            pet_name TEXT,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        # Таблица для пациентов
        cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            patronymic TEXT,
            birth_date TEXT,
            phone TEXT,
            username TEXT,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        conn.commit()
        logger.info("База данных успешно инициализирована")
    except sqlite3.Error as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        raise
    finally:
        conn.close()

def save_patient(user_id, first_name, last_name, patronymic, birth_date, phone, username):
    """Сохраняет данные пациента в базу"""
    try:
        conn = sqlite3.connect('clinic.db')
        cursor = conn.cursor()

        cursor.execute('''INSERT OR REPLACE INTO patients 
                         (user_id, first_name, last_name, patronymic, birth_date, phone, username) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, first_name, last_name, patronymic, birth_date, phone, username))

        cursor.execute('''INSERT INTO messages 
                         (message_type, patient_id, patient_name, message_text) 
                         VALUES (?, ?, ?, ?)''',
                       ('registration',
                        user_id,
                        f"{last_name} {first_name}",
                        f"Новый пациент: {last_name} {first_name} {patronymic or ''}"))

        conn.commit()
        logger.info(f"Сохранен пациент {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка сохранения пациента {user_id}: {e}")
        raise
    finally:
        conn.close()

def get_patient(user_id):
    """Получает данные пациента из базы"""
    try:
        conn = sqlite3.connect('clinic.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM patients WHERE user_id = ?''', (user_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Ошибка получения пациента {user_id}: {e}")
        return None
    finally:
        conn.close()

def save_message(message_type):
    # Разрешенные типы для старой базы
    allowed_types = {'patient_to_doctor', 'doctor_to_patient'}
    if message_type not in allowed_types:
        logger.warning(f"Попытка сохранить сообщение с недопустимым типом: {message_type}")
        return

def save_message(message_type, patient_id=None, patient_name=None,
                 doctor_id=None, doctor_specialty=None, pet_name=None, message_text=None):
    """Сохраняет сообщение в базу данных"""
    try:
        conn = sqlite3.connect('clinic.db')
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO messages 
                         (message_type, patient_id, patient_name, 
                          doctor_id, doctor_specialty, pet_name, message_text) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (message_type, patient_id, patient_name,
                        doctor_id, doctor_specialty, pet_name, message_text))
        conn.commit()
        logger.info(f"Сохранено сообщение типа {message_type}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка сохранения сообщения: {e}")
        raise
    finally:
        conn.close()

def is_doctor(user_id):
    """Проверяет, является ли пользователь врачом"""
    return user_id in DOCTORS

def is_registered(user_id):
    """Проверяет, зарегистрирован ли пациент"""
    return get_patient(user_id) is not None

def create_main_menu(user_id):
    """Создает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if not is_doctor(user_id):
        buttons = [
            types.KeyboardButton('Оплатить'),
            types.KeyboardButton('Проверка оплаты'),
            types.KeyboardButton('Написать Врачу'),
            types.KeyboardButton('Редактировать профиль')
        ]
        markup.add(*buttons)
    return markup

def create_edit_profile_menu():
    """Создает меню для редактирования профиля"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton('Имя'),
        types.KeyboardButton('Фамилия'),
        types.KeyboardButton('Отчество'),
        types.KeyboardButton('Дата рождения'),
        types.KeyboardButton('Телефон'),
        types.KeyboardButton('Назад')
    ]
    markup.add(*buttons)
    return markup

def safe_send_message(chat_id, text, reply_markup=None):
    """Безопасная отправка сообщения с обработкой ошибок"""
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
        return None

@bot.message_handler(commands=['start', 'reset'])
def start(message):
    """Обработчик команды /start и /reset"""
    reset_user_state(message.chat.id)
    user_id = message.from_user.id
    username = message.from_user.username

    save_message('system', message_text=f"Пользователь {user_id} запустил бота")

    if is_doctor(user_id):
        safe_send_message(
            message.chat.id,
            f'Добро пожаловать, доктор {DOCTORS[user_id]["name"]}!',
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    if is_registered(user_id):
        patient = get_patient(user_id)
        if not patient:
            safe_send_message(message.chat.id, "Ошибка: данные пациента не найдены")
            return

        full_name = f"{patient[2]} {patient[1]}"
        if patient[3]:
            full_name += f" {patient[3]}"

        welcome_message = (
            f'Здравствуйте, {full_name}!\n'
            f'Ваш Telegram (@{patient[6] if patient[6] else "без username"}) есть в базе клиники "Лес".\n'
            'При необходимости изменить данные в главном меню нажмите кнопку "Редактировать профиль".'
        )

        safe_send_message(
            message.chat.id,
            welcome_message,
            reply_markup=create_main_menu(user_id)
        )
    else:
        user_states[message.chat.id] = {
            'state': STATE_ENTERING_FIRST_NAME,
            'username': username
        }
        safe_send_message(
            message.chat.id,
            'Добро пожаловать! Для регистрации введите ваше имя:',
            reply_markup=types.ReplyKeyboardRemove()
        )

@bot.message_handler(func=lambda m: m.text == 'Редактировать профиль' and not is_doctor(m.from_user.id))
def edit_profile(message):
    if not is_registered(message.from_user.id):
        safe_send_message(message.chat.id, 'Пожалуйста, сначала завершите регистрацию через команду /start')
        return

    save_message('patient_action',
                 message.from_user.id,
                 None,
                 None,
                 None,
                 None,
                 'Начато редактирование профиля')

    user_states[message.chat.id] = {'state': STATE_EDITING_PROFILE}
    safe_send_message(
        message.chat.id,
        'Выберите поле для редактирования:',
        reply_markup=create_edit_profile_menu()
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_EDITING_PROFILE)
def process_edit_choice(message):
    if message.text == 'Назад':
        user_states[message.chat.id] = {}
        safe_send_message(
            message.chat.id,
            'Главное меню:',
            reply_markup=create_main_menu(message.from_user.id)
        )
        return

    field_map = {
        'Имя': 'first_name',
        'Фамилия': 'last_name',
        'Отчество': 'patronymic',
        'Дата рождения': 'birth_date',
        'Телефон': 'phone'
    }

    if message.text not in field_map:
        safe_send_message(
            message.chat.id,
            'Пожалуйста, выберите поле из предложенных вариантов.',
            reply_markup=create_edit_profile_menu()
        )
        return

    user_states[message.chat.id] = {
        'state': STATE_EDITING_FIELD,
        'editing_field': field_map[message.text]
    }

    if message.text == 'Отчество':
        safe_send_message(
            message.chat.id,
            'Введите новое отчество (или "нет", если отчества нет):',
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text == 'Дата рождения':
        safe_send_message(
            message.chat.id,
            'Введите новую дату рождения в формате дд.мм.гггг:',
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        safe_send_message(
            message.chat.id,
            f'Введите новое значение для {message.text.lower()}:',
            reply_markup=types.ReplyKeyboardRemove()
        )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_EDITING_FIELD)
def process_field_edit(message):
    user_id = message.from_user.id
    field = user_states[message.chat.id]['editing_field']
    patient = get_patient(user_id)

    patient_data = {
        'first_name': patient[1],
        'last_name': patient[2],
        'patronymic': patient[3],
        'birth_date': patient[4],
        'phone': patient[5],
        'username': patient[6]
    }

    if field == 'birth_date':
        if not is_valid_date(message.text):
            safe_send_message(message.chat.id, 'Пожалуйста, введите корректную дату в формате дд.мм.гггг:')
            return
        patient_data[field] = message.text
    elif field == 'phone':
        phone = ''.join(filter(str.isdigit, message.text))
        if len(phone) < 10:
            safe_send_message(message.chat.id, 'Пожалуйста, введите корректный номер телефона:')
            return
        patient_data[field] = phone
    elif field == 'patronymic':
        patient_data[field] = message.text if message.text.lower() != 'нет' else None
    else:
        patient_data[field] = message.text

    save_message('patient_action',
                 user_id,
                 f"{patient_data['last_name']} {patient_data['first_name']}",
                 None,
                 None,
                 None,
                 f'Изменено поле {field}: {message.text}')

    save_patient(
        user_id,
        patient_data['first_name'],
        patient_data['last_name'],
        patient_data['patronymic'],
        patient_data['birth_date'],
        patient_data['phone'],
        patient_data['username']
    )

    full_name = f"{patient_data['last_name']} {patient_data['first_name']}"
    if patient_data['patronymic']:
        full_name += f" {patient_data['patronymic']}"

    del user_states[message.chat.id]

    safe_send_message(
        message.chat.id,
        f'Данные успешно обновлены, {full_name}!',
        reply_markup=create_main_menu(user_id)
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_FIRST_NAME)
def process_first_name(message):
    user_states[message.chat.id].update({
        'state': STATE_ENTERING_LAST_NAME,
        'first_name': message.text
    })
    safe_send_message(message.chat.id, 'Отлично! Теперь введите вашу фамилию:')

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_LAST_NAME)
def process_last_name(message):
    user_states[message.chat.id].update({
        'state': STATE_ENTERING_PATRONYMIC,
        'last_name': message.text
    })
    safe_send_message(message.chat.id, 'Введите ваше отчество (или напишите "нет", если его нет):')

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_PATRONYMIC)
def process_patronymic(message):
    patronymic = None if message.text.lower() == 'нет' else message.text
    user_states[message.chat.id].update({
        'state': STATE_ENTERING_BIRTH_DATE,
        'patronymic': patronymic
    })
    safe_send_message(message.chat.id, 'Введите вашу дату рождения в формате дд.мм.гггг (например, 15.05.1990):')

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_BIRTH_DATE)
def process_birth_date(message):
    if not is_valid_date(message.text):
        safe_send_message(message.chat.id,
                          'Пожалуйста, введите корректную дату в формате дд.мм.гггг (например, 15.05.1990):')
        return

    user_states[message.chat.id].update({
        'state': STATE_ENTERING_PHONE,
        'birth_date': message.text
    })
    safe_send_message(message.chat.id, 'Введите ваш номер телефона:')

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_PHONE)
def process_phone(message):
    phone = ''.join(filter(str.isdigit, message.text))
    if len(phone) < 10:
        safe_send_message(message.chat.id, 'Пожалуйста, введите корректный номер телефона:')
        return

    user_data = user_states[message.chat.id]

    save_patient(
        message.from_user.id,
        user_data['first_name'],
        user_data['last_name'],
        user_data['patronymic'],
        user_data['birth_date'],
        phone,
        user_data.get('username')
    )

    full_name = f"{user_data['last_name']} {user_data['first_name']}"
    if user_data['patronymic']:
        full_name += f" {user_data['patronymic']}"

    del user_states[message.chat.id]

    safe_send_message(
        message.chat.id,
        f'Регистрация завершена, {full_name}! Ваш Telegram (@{user_data.get("username", "без username")}) сохранен в базе клиники "Лес".',
        reply_markup=create_main_menu(message.from_user.id)
    )

@bot.message_handler(func=lambda m: m.text == 'Написать Врачу' and not is_doctor(m.from_user.id))
def write_to_doctor(message):
    if not is_registered(message.from_user.id):
        safe_send_message(message.chat.id, 'Пожалуйста, сначала завершите регистрацию через команду /start')
        return

    save_message('patient_action',
                 message.from_user.id,
                 None,
                 None,
                 None,
                 None,
                 'Начало диалога с врачом')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [types.KeyboardButton(spec['name']) for spec in DOCTORS.values()]
    buttons.append(types.KeyboardButton('Назад'))
    markup.add(*buttons)

    user_states[message.chat.id] = {'state': STATE_CHOOSING_DOCTOR}
    safe_send_message(
        message.chat.id,
        'Выберите специалиста, которому хотите написать:',
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_CHOOSING_DOCTOR)
def process_doctor_choice(message):
    if message.text == 'Назад':
        user_states[message.chat.id] = {}
        safe_send_message(
            message.chat.id,
            'Главное меню:',
            reply_markup=create_main_menu(message.from_user.id)
        )
        return

    doctor_specialty = None
    for spec in DOCTORS.values():
        if message.text == spec['name']:
            doctor_specialty = message.text
            break

    if not doctor_specialty:
        safe_send_message(message.chat.id, 'Пожалуйста, выберите специалиста из предложенных вариантов.')
        return

    user_states[message.chat.id] = {
        'state': STATE_ENTERING_PET_NAME,
        'doctor_specialty': doctor_specialty
    }
    safe_send_message(
        message.chat.id,
        'Введите имя вашего питомца:',
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена❌')
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_PET_NAME and m.text == 'Отмена❌')
def cancel_pet_name_input(message):
    save_message('patient_action',
                 message.from_user.id,
                 None,
                 None,
                 None,
                 None,
                 'Отмена ввода имени питомца')
    user_states[message.chat.id] = {}
    safe_send_message(
        message.chat.id,
        'Главное меню:',
        reply_markup=create_main_menu(message.from_user.id)
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_ENTERING_PET_NAME)
def process_pet_name(message):
    user_states[message.chat.id].update({
        'state': STATE_WRITING_TO_DOCTOR,
        'pet_name': message.text
    })
    safe_send_message(
        message.chat.id,
        'Напишите ваше сообщение врачу:',
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена❌')
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_WRITING_TO_DOCTOR)
def process_message_to_doctor(message):
    if message.text == 'Отмена❌':
        save_message('patient_action',
                     message.from_user.id,
                     None,
                     None,
                     None,
                     None,
                     'Отмена сообщения врачу')
        user_states[message.chat.id] = {}
        safe_send_message(
            message.chat.id,
            'Главное меню:',
            reply_markup=create_main_menu(message.from_user.id)
        )
        return

    user_data = user_states[message.chat.id]
    patient = get_patient(message.from_user.id)

    full_name = f"{patient[2]} {patient[1]}"
    if patient[3]:
        full_name += f" {patient[3]}"

    doctor_id = None
    for doc_id, doc_data in DOCTORS.items():
        if doc_data['name'] == user_data['doctor_specialty']:
            doctor_id = doc_id
            break

    if not doctor_id:
        save_message('system_error',
                     message.from_user.id,
                     full_name,
                     None,
                     user_data['doctor_specialty'],
                     user_data['pet_name'],
                     'Врач не найден')
        safe_send_message(message.chat.id, 'Ошибка: врач не найден')
        return

    save_message(
        'patient_to_doctor',
        message.from_user.id,
        full_name,
        doctor_id,
        user_data['doctor_specialty'],
        user_data['pet_name'],
        message.text
    )

    reply_markup = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton(
        text="Ответить",
        callback_data=f"reply_{message.from_user.id}"
    )
    reply_markup.add(reply_button)

    safe_send_message(
        message.chat.id,
        f'Ваше сообщение для {user_data["doctor_specialty"]} отправлено!',
        reply_markup=create_main_menu(message.from_user.id)
    )

    try:
        bot.send_message(
            doctor_id,
            f'Новое сообщение от пациента:\n'
            f'👤 Пациент: {full_name}\n'
            f'🐾 Питомец: {user_data["pet_name"]}\n'
            f'✉️ Сообщение: {message.text}',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f'Не удалось отправить сообщение врачу {doctor_id}: {e}')

    del user_states[message.chat.id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_doctor_reply(call):
    doctor_id = call.from_user.id
    if not is_doctor(doctor_id):
        save_message('system_error',
                     None,
                     None,
                     doctor_id,
                     None,
                     None,
                     'Не врач пытался ответить пациенту')
        bot.answer_callback_query(call.id, "Только врачи могут отвечать пациентам")
        return

    patient_id = int(call.data.split('_')[1])
    patient = get_patient(patient_id)
    if not patient:
        save_message('system_error',
                     patient_id,
                     None,
                     doctor_id,
                     None,
                     None,
                     'Пациент не найден при попытке ответа')
        bot.answer_callback_query(call.id, "Пациент не найден")
        return

    save_message('doctor_action',
                 patient_id,
                 f"{patient[2]} {patient[1]}",
                 doctor_id,
                 DOCTORS.get(doctor_id, {}).get('name'),
                 None,
                 'Врач начал ответ пациенту')

    user_states[call.message.chat.id] = {
        'state': STATE_DOCTOR_RESPONSE,
        'patient_id': patient_id,
        'patient_name': f"{patient[2]} {patient[1]}",
        'message_id': call.message.message_id
    }

    safe_send_message(
        doctor_id,
        f'Введите ваш ответ пациенту {patient[2]} {patient[1]}:',
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена❌')
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == STATE_DOCTOR_RESPONSE)
def process_doctor_reply(message):
    if message.text == 'Отмена❌':
        save_message('doctor_action',
                     user_states[message.chat.id]['patient_id'],
                     user_states[message.chat.id]['patient_name'],
                     message.from_user.id,
                     DOCTORS.get(message.from_user.id, {}).get('name'),
                     None,
                     'Врач отменил ответ')
        del user_states[message.chat.id]
        safe_send_message(
            message.chat.id,
            'Ответ отменен',
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    user_data = user_states[message.chat.id]
    doctor = DOCTORS.get(message.from_user.id, {}).get('name', 'Доктор')

    save_message(
        'doctor_to_patient',
        user_data['patient_id'],
        user_data['patient_name'],
        message.from_user.id,
        doctor,
        None,
        message.text
    )

    try:
        bot.send_message(
            user_data['patient_id'],
            f'✉️ Ответ от врача {doctor}:\n\n{message.text}',
            reply_markup=create_main_menu(user_data['patient_id'])
        )

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_data['message_id'],
            text=f"✅ Вы ответили пациенту:\n{message.text}"
        )
    except Exception as e:
        logger.error(f'Ошибка отправки ответа пациенту: {e}')

    del user_states[message.chat.id]

@bot.message_handler(func=lambda m: True)
def handle_unexpected_messages(message):
    """Обработчик непредвиденных сообщений"""
    reset_user_state(message.chat.id)
    save_message('system',
                 message.from_user.id,
                 None,
                 None,
                 None,
                 None,
                 f'Неожиданное сообщение: {message.text}')
    safe_send_message(
        message.chat.id,
        "Извините, я не понял ваше сообщение. Пожалуйста, используйте кнопки меню.",
        reply_markup=create_main_menu(message.from_user.id)
    )

if __name__ == '__main__':
    # Инициализация
    init_db()
    user_states = load_states()

    # Сохраняем факт запуска бота
    save_message('system', message_text='Бот запущен')

    logger.info("Бот запущен...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
    finally:
        # Сохраняем состояния и факт остановки
        save_states()
        save_message('system', message_text='Бот остановлен')
        logger.info("Бот остановлен")