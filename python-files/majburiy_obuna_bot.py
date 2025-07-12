
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import logging

TOKEN = "7993952088:AAGJihhyREVMnNmRVBtfvpF23G0PZtaqJeo"
REQUIRED_CHANNELS = ["@coldven", "@lemony17"]
ADMIN_ID = 7687732149
SCHEMA_FILE = "schema.txt"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

def get_schema_text():
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Hozircha sxema yo'q."

def save_schema_text(text):
    with open(SCHEMA_FILE, "w", encoding="utf-8") as f:
        f.write(text)

async def check_subscribed(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "creator", "administrator"]:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if await check_subscribed(user_id):
        button = KeyboardButton("📄 Sxema olish")
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
        await message.answer("Botga xush kelibsiz!

📄 'Sxema olish' tugmasini bosing.", reply_markup=markup)
    else:
        text = "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:

"
        for ch in REQUIRED_CHANNELS:
            text += f"➡ {ch}
"
        text += "\n✅ Obuna bo‘lgach, /start buyrug‘ini yana yozing."
        await message.answer(text)

@dp.message_handler(lambda msg: msg.text == "📄 Sxema olish")
async def send_schema(msg: types.Message):
    if await check_subscribed(msg.from_user.id):
        schema_text = get_schema_text()
        await msg.answer(f"📄 Sxema:\n\n{schema_text}")
    else:
        await msg.answer("❗ Avval kerakli kanallarga obuna bo‘ling.")

@dp.message_handler(commands=['matn'])
async def change_schema(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("Siz admin emassiz.")
        return
    args = msg.get_args()
    if not args:
        await msg.answer("Yangi matnni quyidagicha yuboring:\n`/matn Bu yangi sxema`")
        return
    save_schema_text(args)
    await msg.answer("✅ Matn yangilandi.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
