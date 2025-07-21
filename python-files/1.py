import sys
import re
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

# --- CONFIGURATION ---
# ❗️توکن ربات تلگرام خود را اینجا قرار دهید
TELEGRAM_BOT_TOKEN = "8187022583:AAE5Z726jIlSRjieCBUaMt5MfRdnzYje6aA"

# ❗️❗️ اطلاعات کانال خود را در اینجا جایگزین کنید
CHANNEL_ID = -1002445792791  # <--- شناسه عددی کانال خصوصی شما
CHANNEL_LINK = "https://t.me/+UwdAUMoJO0g3ZjVk"  # <--- لینک دعوت کانال شما

# --- RSA KEY AND FUNCTIONS (بدون تغییر) ---
PRIVATE_KEY_PEM = b"""
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2i0/yERQ/5+ax4i0Bnc03cQJpkq/dHsvf4I+Dd2HTX5wzPO8
zeqQo7EKzg0DJ09nozB7WU4qpg9cvY30P3wLCT1RZ/A1pyGju6TLzsRweTepXVGy
Hk7P+BwiAuLKFXh1Tr1UbiLwAJHO2uwGOaKZYWEMBkHVYTU3eL7q9kveJzAE4ZoS
vRV8rXEhvH6Z5Di3PFMx5Oa6cKIZTMSjM8kdZfOiQUHbGJ5b/lcy0Yok8wFne8mk
OdzF4nt4czOt7GMUeso0OFhRPUOAlcwO3GWbeOsqhvR/5f28KDHVbbxzM0I5Nm9U
qEzYvdwrHmQIhMn6R9HqHMnuLVNoUHihErBRDwIDAQABAoIBAE3/+1uXwPWClA1d
/C6Lk6TtHx4KfyQfnj2RzKmcV3EHEUDUqt1bTNaYxuofkM8O/lhDTvYAkhLITzmd
dIL1z+Q/vcjRAf18c1L0ecC0ThmoIq6wNGPNfWCQfkBV4DWI2TeLTJILf45UkoWF
+DvGu9sqnOfnxWd5ZRmP9+SR/xw2z34WHH9bBZX0hhehX8j8goWw3PFxJTC7ThkA
AbB2t0DDNL/cufhTSsVNPrnh+cGrFSu9KLMKaxVVZ5buZcK2BiHzNv8rlXiWAKVJ
IIIqCVdBR70UQWw0KOcvnuuixZzO0myKpSXax4fQU3QHU2KLEBpXRHvvbLKSa60U
ZAXVH6ECgYEA93ebNvy6Rb/RNIBYBMa2N2iw6P9112KAZmKw8qH2ilZ9Fa8xlYJE
8N8d8nsuz45HY7vEVeh6c3kK/lJkGmuFstxVrj+bLoF6wVp7s6Uj7Pu4oP2XwkiJ
WZOD14ZIUWP8W+1UCTfnzCXnr+PIhgwmCrexwgtViiEVlRaszWNf+2kCgYEA4bMY
jORlYzC7ZQGBQRE5vIe/XP8/Ym8Kke+VIqfNM65CSJ64xuXbKmOOQa4K4JMnVSmx
6aRd8znRXDVq8ExP8aBGqrOBGa9P7xL/s53Ch0ABDX+0H2Yx1SjgXDoUpUcgz62z
+vOTNUEX9KiPUozvsNTbqY1K867l431GhAJAsbcCgYBZcCry1qhj6Q2tUe193Gui
3v2BWEK402rgli6poou+N8ABhE4BYRGVlK34Izkp3pxCmWw+OEV5Unf8rr5rJg0u
NZ/p2Cc3yagaFZ+7r6WqUtfJp52fpCOv8jamQGwGroJYnw/OPRxTlieEVGj2uZFO
MlHWdc42m/p25bkSiiX4cQKBgQDMRoDN5FovcIfrX3VRIvoSvPpifVMtEDuM4j8k
4qNDR1EO0TmEK741m23B3HhT0lwjJF22jeHKpmXrAx4K58bjdqD/FwCd8qJyS8vL
Edpi93b8dLzePmyT9S87ygWtobb8wMbJN3PhG01HTtiJaq32anF2AD/6Vi4Tu+r6
x98t+QKBgQCZfQ1Ru5NgM4RgQ3oyJEkSoXi3/1ICvsuadPrEIjpM5/zK75ZKumY8
AgbMhhHcmiigYY4nEwz4DxgRHWHaBfgi7YvQqz2hfeLaLSg1YdMZZbfLrL0BCS01
Oc+m4aJQXKNzYO8uXqBwJK8koabbt+3VOYGKFgw/Yf2FdK5IKdhkdA==
-----END RSA PRIVATE KEY-----
"""

private_key = serialization.load_pem_private_key(
    PRIVATE_KEY_PEM,
    password=None,
)

def rsa_private_encrypt(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    key_size = private_key.key_size // 8
    if len(message) > key_size - 11:
        raise ValueError("Message too long for RSA key size")
    padding_size = key_size - len(message) - 3
    padding = b'\xff' * padding_size
    padded_message = b'\x00\x01' + padding + b'\x00' + message
    m_int = int.from_bytes(padded_message, 'big')
    private_numbers = private_key.private_numbers()
    d = private_numbers.d
    n = private_key.public_key().public_numbers().n
    c_int = pow(m_int, d, n)
    encrypted_data = c_int.to_bytes(key_size, 'big')
    return encrypted_data

# --- Telegram Bot Code ---

async def is_user_member(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """بررسی می‌کند که آیا کاربر عضو کانال است یا خیر."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except BadRequest as e:
        print(f"Error checking chat member: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error in is_user_member: {e}")
        return False

async def send_join_channel_message(update: Update) -> None:
    """پیام عضویت در کانال را به همراه دکمه تایید ارسال می‌کند."""
    keyboard = [
        [InlineKeyboardButton("Ranomware", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Confirm", callback_data="check_membership")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💡 Join first to get started.",
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پیام خوشامدگویی را در صورت عضو بودن کاربر ارسال می‌کند."""
    user = update.effective_user
    if not await is_user_member(context, user.id):
        await send_join_channel_message(update)
        return
    
    await update.message.reply_text("Enter NLBrute ID:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Join our channel, then tap “Joined"""
    user = update.effective_user
    if not await is_user_member(context, user.id):
        await send_join_channel_message(update)
        return

    user_id = update.message.text.strip()
    id_pattern = r'^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]+$'
    if user_id and re.fullmatch(id_pattern, user_id):
        try:
            msg_bytes = user_id.encode('utf-8')
            encrypted = rsa_private_encrypt(msg_bytes, private_key)
            
            await update.message.reply_text(
                f"NLBrute KEY:\n```{encrypted.hex()}```",
                parse_mode="MarkdownV2"
            )
        except ValueError as e:
            await update.message.reply_text(f"Error: {e}")
        except Exception as e:
            await update.message.reply_text(f"An unexpected error occurred: {e}")
    else:
        error_message = (
            "⚠️\n"
            "Invalid input\\.\n"
            "Enter a valid NLBrute ID\\.\n"
            "Example: `568B8FA5CD5F83AAE05A0AA6718346`"
        )
        await update.message.reply_text(error_message, parse_mode="MarkdownV2")

# --- تابع جدید برای مدیریت دکمه تایید عضویت ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت کلیک روی دکمه‌های اینلاین."""
    query = update.callback_query
    # ❗️ فراخوانی اولیه از اینجا حذف شد

    if query.data == "check_membership":
        user_id = query.from_user.id
        if await is_user_member(context, user_id):
            # ابتدا به کلیک پاسخ می‌دهیم تا لودینگ تمام شود
            await query.answer() 
            # سپس پیام را ویرایش می‌کنیم
            await query.edit_message_text(text="✅ successfully\n\nEnter NLBrute ID:")
        else:
            # اینجا اولین و تنها فراخوانی برای کاربر غیرعضو است و به درستی اجرا می‌شود
            await query.answer(text="❌ You have not joined the channel yet!", show_alert=True)

def main() -> None:
    """ربات را اجرا می‌کند."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- ثبت کردن هندلرها ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # --- ثبت هندلر جدید برای دکمه‌ها ---
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
