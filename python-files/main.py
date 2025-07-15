"""импорт необходимых библиотек"""
from aiogram import Bot, types, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.types import WebAppInfo
from aiogram.filters import CommandStart

import asyncio
"""иморт конфига"""

from config import *








"""инициализация бота"""

bot = Bot(token=TOKEN)
dp = Dispatcher()



"""логика"""
@dp.message(CommandStart())
async def start_bot(message: Message):
	kb = [[types.KeyboardButton(text  = "открыть сканер", web_app = WebAppInfo(url = URL))]]
	markup = types.ReplyKeyboardMarkup(keyboard=kb)
	await message.answer(HELLO, reply_markup=markup)




@dp.message(F.web_app_data)
async def decod_qr(message: Message):

	try:
		await message.answer_audio(audio=FSInputFile(path=soun[message.web_app_data.data]))		
	except Exception as e:
		await message.answer(error_qr)
"""старт"""

async def main() -> None:
	await dp.start_polling(bot)

if __name__ == '__main__':
	asyncio.run(main())