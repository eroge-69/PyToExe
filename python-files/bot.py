from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = '7731943156:AAEZEbci88lmuHKgK246m-vhp2NRvP2e1Xs'
OWNER_ID = 29095346  # ← Замени на свой Telegram ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Ты — один из немногих, кто попал в группу PROJECT_W.\n\n"
        "Пожалуйста, заполни анкету **одним сообщением**, вот шаблон:\n\n"
        "1. Как тебя зовут?\n"
        "2. Сколько тебе лет?\n"
        "3. Из какого ты города?\n"
        "4. Расскажи немного о себе.\n\n"
        "✍️ Просто скопируй и заполни!"
    )

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = update.message.text

    text = (
        f"📥 Новая анкета:\n\n"
        f"👤 Пользователь: @{user.username or 'без username'} (ID: {user.id})\n\n"
        f"{msg}"
    )

    await context.bot.send_message(chat_id=OWNER_ID, text=text)
    await update.message.reply_text("✅ Спасибо! Твоя анкета отправлена.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    app.run_polling()

if __name__ == "__main__":
    main()
