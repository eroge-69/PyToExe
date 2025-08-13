import os
import sys
import asyncio
from gtts import gTTS
import pygame
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import ctypes
import tempfile

# Скрываем окно (Windows)
if sys.platform == 'win32':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Конфиг
BOT_TOKEN = "ВАШ_ТОКЕН"
ADMIN_ID = 123456789  # Ваш ID в Telegram

class SilentBot:
    def __init__(self):
        pygame.mixer.init()
        self.volume = 0.7
        
    async def speak(self, text: str):
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tts = gTTS(text=text, lang='ru')
                tts.save(tmp.name)
                pygame.mixer.music.load(tmp.name)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
        except:
            pass
        finally:
            try: os.unlink(tmp.name)
            except: pass

bot = SilentBot()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    text = update.message.text
    if text.startswith('/vol '):
        try:
            vol = int(text.split()[1]) / 100
            bot.volume = max(0.0, min(1.0, vol))
        except:
            pass
    else:
        await bot.speak(text)

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Механизм скрытого перезапуска при ошибках
    async def restart():
        while True:
            try:
                await app.initialize()
                await app.start()
                await app.updater.start_polling()
                await app.stop()
            except:
                await asyncio.sleep(60)
    
    asyncio.run(restart())

if __name__ == "__main__":
    # Двойной форк для полного отсоединения (Unix/Windows)
    if sys.platform != 'win32':
        if os.fork(): os._exit(0)
    
    run_bot()