# Telegram Search Bot - Developed by @sinnerconfigs
# https://t.me/sinnerconfigs

import sqlite3, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, CallbackContext
import json

# Get user info from the database
def get_user_info(user_id: int):
    directory = 'clients'
    if not os.path.exists(directory):
        os.mkdir(directory)

    try:
        conn = sqlite3.connect('clients/database.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            name TEXT,
            coins FLOAT,
            id NUMERIC UNIQUE
        )
        ''')
        cursor.execute(f'SELECT * from user WHERE id == {user_id};')
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(e)
        conn.close()
        return str(e)

# Register a new user with starting coins
def register_user(name, user_id) -> bool:
    directory = 'clients'
    if not os.path.exists(directory):
        os.mkdir(directory)

    try:
        conn = sqlite3.connect('clients/database.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            name TEXT,
            coins FLOAT,
            id NUMERIC UNIQUE
        )
        ''')
        cursor.execute('''
        INSERT INTO user (name, coins, id)
        VALUES (?, ?, ?)
        ''', (name, 5, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if 'UNIQUE constraint failed' not in str(e):
            print('Register Error:', e)
        return False

# Admin command to add coins to a user
async def add_coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    sender_id = message.from_user.id

    if message.chat_id != admin_id and sender_id != admin_id:
        return

    keyboard = [
        [InlineKeyboardButton("Delete 🚮", callback_data='delete')],
        [InlineKeyboardButton("Search Anonymously", url='https://t.me/TUDOF_bot')]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        _, user_id, coins_to_add = message.text.split()[:3]
        chat = await context.bot.get_chat(user_id)
        name = chat.first_name
        username = chat.username
    except:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='<b>Incorrect Format</b>', parse_mode='HTML')
        return

    try:
        user_info = get_user_info(user_id)
        if not user_info:
            if register_user(name, user_id):
                user_info = get_user_info(user_id)
    except:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='<b>Error Connecting to DB</b>', parse_mode='HTML')
        return

    try:
        conn = sqlite3.connect('clients/database.db')
    except Exception as e:
        print('Database Connection Error:', e)
        return

    cursor = conn.cursor()
    try:
        cursor.execute(f'''UPDATE user SET coins = {float(user_info[1]) + float(coins_to_add)} WHERE id = {user_id};''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'<b>User Already Exists ❌\nID: <code>{user_id}</code></b>', parse_mode='HTML')
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'<b>Coins Added ✅\n\nName: {name}\nUsername: @{username}\nID: <code>{user_id}</code>\n\nCoins Added: <code>{float(coins_to_add)}</code>\nNew Balance: <code>{float(user_info[1]) + float(coins_to_add)}</code></b>', reply_markup=markup, parse_mode='HTML')

    if username == 'Channel_Bot':
        return

    await context.bot.send_message(chat_id=user_id, text=f'<b>Coins Added ✅\n\nName: {name}\nUsername: @{username}\n\nCoins: <code>{float(coins_to_add)}</code>\nNew Balance: <code>{float(user_info[1]) + float(coins_to_add)}</code></b>', parse_mode='HTML')
