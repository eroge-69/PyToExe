from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import tkinter as tk
import threading
import asyncio

# Токен вашего Telegram-бота
TOKEN = '8248630719:AAFA5Nwr8n59KffQVFY-oD7KLP62J1W4SpI'

# Переменная для хранения сообщений
messages = []

# Обработчик сообщений
async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user = update.message.from_user.first_name
    messages.append(f"📩 Получено сообщение от {user}: {message}")

# Обработчик отправки сообщений
async def send_message(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

# Окно Tkinter
class TelegramGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Telegram Chat Interface")
        self.geometry("600x400")

        # Тексты и элемент scrollbar
        self.scroll_y = tk.Scrollbar(self)
        self.messages_text = tk.Text(self, wrap=tk.WORD, yscrollcommand=self.scroll_y.set)
        self.scroll_y.config(command=self.messages_text.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_text.pack(expand=True, fill=tk.BOTH)

        # Поле ввода и кнопка отправки
        self.entry_field = tk.Entry(self, width=50)
        self.entry_field.pack(pady=10)
        button = tk.Button(self, text="Отправить", command=self.on_send)
        button.pack(pady=10)

        # Периодическое обновление содержимого Text
        self.update_ui()

    def update_ui(self):
        # Обновляем UI каждые 1 секунду
        self.messages_text.delete("1.0", tk.END)
        for msg in messages:
            self.messages_text.insert(tk.END, msg + "\n")
        self.after(1000, self.update_ui)

    def on_send(self):
        message = self.entry_field.get()
        if message.strip():  # Проверка на пустое сообщение
            asyncio.run(send_message(ApplicationBuilder().token(TOKEN).build().bot, 6726797826, message))
            messages.append(f"💬 Отправлено сообщение: {message}")
            self.entry_field.delete(0, tk.END)

# Вспомогательная функция для запуска Telegram бота
def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_message))
    application.run_polling()

# Запуск приложения
if __name__ == '__main__':
    gui = TelegramGUI()
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    gui.mainloop()