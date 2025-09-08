# # # # # # # # # #-Z
# RELEASE 0.0.1a # #Z от 15.11.2024
# # # # # # # # # #-Z
import logging # для записи
import asyncio # общая библиотека
import aiosqlite # для базы данных
import Settings # настройки бота
import Homework # отдельный файл для подбота ДЗ
import Union # отдельный файл для подбота Профсоюза
import Club # отдельный файл для подбота Клуба Станкина
from telebot import types # основная библиотека бота
import AdvertisementFile # файл рекламы
logging.basicConfig(level=logging.INFO) # Настройка логирования


@Settings.bot.message_handler(commands=['start'])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    _item1_ = types.KeyboardButton('Д/З')
    _item2_ = types.KeyboardButton('Профком')
    _item3_ = types.KeyboardButton('Клуб')
    _item4_ = types.KeyboardButton('Подписаться/отписаться от рекламы💜')  # Обновленная кнопка
    _item5_ = types.KeyboardButton('Инструкция по использованию🤓')

    markup.add(_item1_, _item2_, _item3_, _item4_, _item5_)
    await Settings.bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Выбери интересующий тебя раздел бота!',reply_markup=markup)

@Settings.bot.message_handler(content_types=['text'])
async def bot_message(message: types.Message):
    user_id = str(message.from_user.id)  # Убедитесь, что user_id - строка

    if user_id not in Settings.user_states:
        Settings.user_states[user_id] = None  # Инициализируем состояние при первом взаимодействии

    if message.text == 'Д/З':
        await Homework._homework_(message)

    if message.text == 'Профком':
        await Union._union_(message)

    if message.text == 'Клуб':
        await Club._club_(message)

    if message.text == 'Подписаться/отписаться от рекламы💜':
        await AdvertisementFile.toggle_subscription(user_id, message)  # Переключение подписки
    if message.text == 'Проверить свою роль✅':
        await check_role(message)
    if message.text == 'Инструкция по использованию🤓':
        await Settings.bot.reply_to(message,"Хочешь научится пользоваться нашим ботом-помощником? "
                                   "Тогда мы с радостью расскажем как именно его нужно использовать\n\n")
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_role = await cursor.fetchone()
                user_role = ''.join(user_role)
                if user_role == 'elder' or user_role == 'admin':
                    await Settings.bot.reply_to(message, "Up")
                else:
                    await Settings.bot.reply_to(message, "Down")
                await db.commit()
    if message.text == 'Назад':
        await start(message)


    if message.text == 'Изменить дз':
        await Settings.bot.reply_to(message, 'Д/З изменено')
        await Homework.refactor_homework(message, 'Изменить Д/З')

    if message.text == 'Не менять дз':
        await Settings.bot.reply_to(message, 'Изменений нет')
        await Homework.refactor_homework(message, 'Не изменять Д/З')
    
    if message.text == 'Удалить дз':
        await Settings.bot.reply_to(message, 'Д/З удалено')
        await Homework.refactor_homework(message, 'Удалить Д/З')

    
   
    if message.text == 'Вывести ДЗ🚀':
        Settings.user_states[user_id] = 'получить_Д/З_группа'  # Устанавливаем состояние ожидания ввода группы
        await Settings.bot.reply_to(message, "Введите группу для вывода домашнего задания:")

    elif message.text == 'Добавить дз📝':
        Settings.user_states[user_id] = 'добавить_Д/З_группа' # Устанавливаем состояние ожидания ввода группы
        await Settings.bot.reply_to(message, 'Введите свою группу для добавления дз:')

    elif message.text == 'Редактировать дз':
        Settings.user_states[user_id] = 'редактировать_Д/З_группа'
        Settings.user_states[f'group_{user_id}'] = message.text  # Сохраняем введённую группу
        await Settings.bot.reply_to(message, 'Введите свою группу для редактирования дз:')


    elif Settings.user_states[user_id] == 'получить_Д/З_группа':
        Settings.user_states[user_id] = 'получить_Д/З_дата'  # Переходим на этап ввода даты
        Settings.user_states[f'group_{user_id}'] = message.text  # Сохраняем введённую группу
        await Settings.bot.reply_to(message, "Теперь введите дату, на которую вам нужно узнать дз:")

    elif Settings.user_states[user_id] == 'получить_Д/З_дата':
        group = Settings.user_states[f'group_{user_id}']  # Получаем группу
        date = message.text  # Сохраняем введённую дату
        results = await Homework.search_in_database(group, date)
        if results:
            response = f"Список домашнего задания на дату {date}:\n\n" + "\n".join(f"{i + 1}) {row[1]} - {row[2]}" for i, row in enumerate(results))
        else:
            response = "Ничего не найдено."
        await Settings.bot.reply_to(message, response)
        Settings.user_states[user_id] = None # Сбрасываем состояния
        del Settings.user_states[f'group_{user_id}']

    elif Settings.user_states[user_id] == 'добавить_Д/З_группа':
        async with aiosqlite.connect('database/datausers.db') as db:
            async with db.execute("SELECT group_of, role FROM users WHERE id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
                if user_data[0] != message.text and user_data[1] == 'elder':
                    await Settings.bot.reply_to(message, "Вы не можете добавлять задания для этой группы.")
                elif (user_data[0] == message.text and user_data[1] == 'elder') or user_data[1]=='admin':
                    Settings.user_states[user_id] = 'добавить_Д/З_дата'
                    Settings.user_states[f'group_{user_id}'] = message.text  # Сохраняем введённую группу
                    await Settings.bot.reply_to(message, "Теперь введите дату домашнего задания:")
            await db.commit()

    elif Settings.user_states[user_id] in ('добавить_Д/З_дата'):
        Settings.user_states[user_id] = 'добавить_Д/З_предмет'  # Переходим на этап ввода домашнего задания
        Settings.user_states[f'date_{user_id}'] = message.text  # Сохраняем введённую дату
        await Settings.bot.reply_to(message, "Теперь введите название предмета:")


    elif Settings.user_states[user_id] == 'добавить_Д/З_предмет':
        Settings.user_states[user_id] = 'добавить_Д/З_описание'  # Переходим на этап ввода предмета
        Settings.user_states[f'subject_{user_id}'] = message.text  # Сохраняем введённое домашнее задание
        await Settings.bot.reply_to(message, "Теперь введите описание домашнего задания:")


    elif Settings.user_states[user_id] == 'добавить_Д/З_описание':
        group = Settings.user_states[f'group_{user_id}']
        date = Settings.user_states[f'date_{user_id}']
        subject = Settings.user_states[f'subject_{user_id}']
        homework = message.text
        async with aiosqlite.connect('database/datahomework.db') as db: # Вызываем функцию добавления с передачей message
            async with db.execute("SELECT description FROM homework WHERE group_of =  ? AND date_of = ? AND subject = ?", (group,date,subject)) as cursor:
                if await cursor.fetchone() == None:
                    await db.commit()
                    await Homework.insert_into_database(group, date, homework, subject, user_id,message)  # user_id как идентификатор чата
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(types.KeyboardButton('Изменить дз'), types.KeyboardButton('Не менять дз'), types.KeyboardButton('Удалить дз'))
                    await Settings.bot.reply_to(message, 'Домашнее задание уже существует, вы хотите его изменить на вписанное?', reply_markup = markup)
                    Settings.user_refactor_states[message.from_user.id] = group,date,subject,homework
        Settings.user_states[user_id] = None # Сбрасываем состояния
        for key in ['group', 'date', 'subject']:
            Settings.user_states.pop(f'{key}_{user_id}', None)

async def check_role(message):
    user_id = str(message.from_user.id)
    print(user_id)
    async with aiosqlite.connect('database/datausers.db') as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            id = await cursor.fetchall()
    if id:
        match id[0][2]:
            case 'admin':
                text = f"ВАША РОЛЬ - АДМИНИСТРАТОР\nВАША ГРУППА - {id[0][1]}"
            case 'elder':
                text = f"ВАША РОЛЬ - СТАРОСТА\nВАША ГРУППА - {id[0][1]}"
            case _:
                text = 'ВЫ ОБЫЧНЫЙ СТУДЕНТ'
    else:
        text = 'ВЫ ОБЫЧНЫЙ СТУДЕНТ'

    await Settings.bot.reply_to(message, text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(AdvertisementFile.send_advertisements())  # Запуск задачи отправки рекламы
    loop.run_until_complete(Settings.bot.polling())
