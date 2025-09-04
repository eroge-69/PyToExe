import asyncio
import logging
import os
import pyautogui
from aiogram.types import FSInputFile
from aiogram import Bot,Dispatcher,types
from aiogram.filters.command import Command

API_TOKEN = '7760110652:AAEGx9nKO-b0jc_03fP3WYvKTNUJua9hei4'

SCREENSHOT_PATH = 'screenshot.png'

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    @dp.message(Command('start'))
    async def cmd_start(message: types.Message):
        await message.answer('Привет!😑\nОтправь /screenshot, чтобы сделать снимок экрана.')

    @dp.message(Command('screenshot'))
    async def cmd_screenshot(message: types.Message):
        await message.answer('Секунду...')

        screenshot = pyautogui.screenshot()
        screenshot.save(SCREENSHOT_PATH)

        photo = FSInputFile(SCREENSHOT_PATH)
        await message.answer_photo(photo)
        os.remove(SCREENSHOT_PATH)
        print('OK')

    await dp.start_polling(bot)

asyncio.run(main())
