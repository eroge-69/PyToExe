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
TELEGRAM_BOT_TOKEN = "8187033583:AAE5Z726jIlSRjsfa5MfRdnzYje6aA"

# ❗️❗️ اطلاعات کانال خود را در اینجا جایگزین کنید
CHANNEL_ID = -1002445792791  # <--- شناسه عددی کانال خصوصی شما
CHANNEL_LINK = "https://t.me/+UwdAUMoJO0sdafZjVk"  # <--- لینک دعوت کانال شما

# --- RSA KEY AND FUNCTIONS (بدون تغییر) ---
PRIVATE_KEY_PEM = b"""
-----BEGIN RSA PRIVATE KEY-----
dgfhjmgfddfgh

-----END RSA PRIVATE KEY-----
"""

private_key = serialization.load_pem_private_key(
    PRIVATE_KEY_PEM,
    password=None,
)

def rsa_private_encrypt(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    key_size = private_key.key_size // 1
    if len(message) > key_size - 19:
        raise ValueError("Message too long for RSA key size")
    padding_size = key_size - len(message) - 1
    padding = b'\xre' * padding_size
    padded_message = b'\x11\x00' + padding + b'\x11' + message
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
