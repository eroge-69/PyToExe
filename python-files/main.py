import asyncio, os, base64
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputFile
from .keyboards import main_menu, plans_menu, pay_kb, help_menu
from .texts import WELCOME, HELP_ROOT, HELP_IPHONE, HELP_ANDROID, HELP_DESKTOP, PRIVACY_MD
from . import services
from backend.utils import make_qr_data_url
from tempfile import NamedTemporaryFile

bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher()
r = Router()

@r.message(CommandStart())
async def start(m: Message):
    ref_code = None
    if m.text and ' ' in m.text: ref_code = m.text.split(' ',1)[1].strip()
    await services.ensure_user(m.from_user.id, m.from_user.username, ref_code=ref_code)
    await m.answer(WELCOME, reply_markup=main_menu())

@r.callback_query(F.data == 'buy')
async def buy(call: CallbackQuery):
    await call.message.edit_text('Выберите тариф:', reply_markup=plans_menu(services.PRICES))

@r.callback_query(F.data.startswith('plan:'))
async def plan(call: CallbackQuery):
    plan = call.data.split(':',1)[1]
    pid, url = await services.start_payment(call.from_user.id, plan)
    await call.message.edit_text('Сформирован счёт. Перейдите к оплате:', reply_markup=pay_kb(url))

@r.callback_query(F.data == 'check_payment')
async def check_payment(call: CallbackQuery):
    order = await services.last_pending_order(call.from_user.id)
    if not order:
        await call.answer('Нет ожидающих платежей.', show_alert=True); return
    res = await services.provision_after_payment(order.payment_id)
    if not res:
        await call.answer('Оплата пока не найдена. Попробуйте через минуту.', show_alert=True); return
    sublink = res['sublink']
    data_url = make_qr_data_url(sublink)
    b64 = data_url.split(',',1)[1]; img_bytes = base64.b64decode(b64)
    with NamedTemporaryFile(delete=False, suffix='.png') as f:
        f.write(img_bytes); temp_path = f.name
    await call.message.answer('Готово! Ваша подписка:')
    await call.message.answer(sublink)
    await call.message.answer_photo(InputFile(temp_path), caption='QR для быстрой настройки')

@r.callback_query(F.data == 'status')
async def status(call: CallbackQuery):
    st = await services.get_status(call.from_user.id)
    if not st:
        await call.message.answer('Пока нет активной подписки. Нажмите «Купить VPN».'); return
    msg = '📊 *Статус VPN*\n'
    if st['expires_at']: msg += f"Срок: до {st['expires_at']}\n"
    if st['traffic_gb']: msg += f"Тариф: {st['traffic_gb']} ГБ\n"
    if st['sublink']: msg += f"Ссылка: {st['sublink']}\n"
    if st.get('balance') is not None: msg += f"Баланс: {st['balance']}₽ (баллы)\n"
    await call.message.answer(msg, parse_mode='Markdown')

@r.callback_query(F.data == 'help')
async def help_root(call: CallbackQuery):
    await call.message.edit_text(HELP_ROOT, reply_markup=help_menu())

@r.callback_query(F.data.startswith('help:'))
async def help_device(call: CallbackQuery):
    kind = call.data.split(':',1)[1]
    md = HELP_DESKTOP if kind=='desktop' else (HELP_ANDROID if kind=='android' else HELP_IPHONE)
    await call.message.answer(md, parse_mode='Markdown')

@r.callback_query(F.data == 'privacy')
async def privacy(call: CallbackQuery):
    await call.message.answer(PRIVACY_MD, parse_mode='Markdown')

@r.callback_query(F.data == 'refer')
async def ref(call: CallbackQuery):
    me = await bot.get_me(); code = str(call.from_user.id)
    link = f"https://t.me/{me.username}?start={code}"
    await call.message.answer(
        "Приведи друга и получай баллы!\n"
        f"Твоя ссылка: {link}\n"
        f"Начисление: {os.getenv('REFERRAL_PCT', '50')}% от оплаты в баллах.\n"
        f"Бонус за первую покупку: {os.getenv('FIRST_PURCHASE_BONUS','0')}₽"
    )

async def main():
    dp.include_router(r)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
