import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your real bot token
BOT_TOKEN = "7421905331:AAHKgXnadZvOofsoCyeW2zTjwZ7C9yE3VeQ"


# Replace with your Telegram user ID for security
# You can find your Telegram user ID using @userinfobot
ALLOWED_USER_ID = 1492462402

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text("Hello! Send me a command to run.")

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return

    command = update.message.text
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10)
        output = result.decode(errors='ignore')
    except Exception as e:
        output = str(e)

    # Telegram messages have a size limit; truncate if needed
    if len(output) > 4000:
        output = output[:4000] + "\n[Output truncated]"

    await update.message.reply_text(f"Output:\n{output}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), run_command))

    print("Bot is running...")
    app.run_polling()



