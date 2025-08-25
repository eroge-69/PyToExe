import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Токен бота
TOKEN = "8269841855:AAGGdIx8Y22sHlxX-iYW3nvLoeu-xW_LsHY"

WAITING_FOR_FIO, WAITING_FOR_FILE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте! Пожалуйста, введите ваше ФИО:")
    context.user_data['state'] = WAITING_FOR_FIO

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == WAITING_FOR_FIO:
        context.user_data['fio'] = update.message.text
        keyboard = [
            [InlineKeyboardButton("Справка", callback_data='справка')],
            [InlineKeyboardButton("Кредит", callback_data='кредит')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Спасибо, {context.user_data['fio']}! Выберите тип документа:",
            reply_markup=reply_markup
        )
        context.user_data['state'] = WAITING_FOR_FILE

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['document_type'] = query.data
    await query.message.reply_text("Пожалуйста, отправьте документ (нажмите прикрепить --> документ, НЕ ФОТО ИЛИ ВИДЕО)")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == WAITING_FOR_FILE:
        fio = context.user_data.get('fio', 'Unknown')
        document_type = context.user_data.get('document_type', 'unknown')
        
        folder_path = f"documents/{fio.replace(' ', '_')}"
        os.makedirs(folder_path, exist_ok=True)
        
        file = await update.message.document.get_file()
        file_extension = os.path.splitext(update.message.document.file_name)[1]
         
        current_date = datetime.now().strftime("%d.%m.%Y")

        new_file_name = f"{fio.replace(' ', '_')}_{document_type}_{current_date}{file_extension}"
        file_path = os.path.join(folder_path, new_file_name)
        

        await file.download_to_drive(file_path)
        
        await update.message.reply_text(
            f"Файл успешно сохранен в папке {fio} как {new_file_name}!"
        )
        # Сбрасываем состояние
        context.user_data.clear()

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    
    application.run_polling()

if __name__ == '__main__':
    main()