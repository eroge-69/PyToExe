from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import subprocess

BOT_TOKEN = "8401695437:AAHk7Nkb49XKD2RxTk9rcZSgEDQpat6O4-0"




async def reply(update:Update , context) -> None:

    user_message = update.message.text


    result = subprocess.check_output(user_message, shell=True, text=True)

    await update.message.reply_text(f"you said:{result}")







def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT,reply))
    app.run_polling()


if __name__ =="__main__":
     main()