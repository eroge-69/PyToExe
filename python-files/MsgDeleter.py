from typing import Final

import telegram, time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = "YOUR-TELEGRAM-BOT-TOKEN"
BOT_USERNAME: Final = "YOUR-TELEGRAM-BOT-NAME"
STATUS: bool = False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ACK")
    STATUS = True

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Paused")
    STATUS = False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if "http" in text.lower() and STATUS:
        try:
            time.sleep(5)
            await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
            print("Message deleted!")
        except telegram.error.TelegramError as e:
            print(f"Failed to delete message: {e}")
        return
    return

if __name__ == "__main__":
    print('Starting Bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print('Polling...')
    app.run_polling(poll_interval=3)
