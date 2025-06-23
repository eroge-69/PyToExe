import telebot
import requests
import threading
from mnemonic import Mnemonic
import bip32utils

BOT_TOKEN = "7601001839:AAGBN_ofzmNZUpRaZgTRazZNPgazdjoat-s"
ADMIN_USERNAME = "cryptologistadmin"  # alt çizgi yok!
DEFAULT_LANGUAGE = "en"

CHANNEL_LINK = "https://t.me/cryptologist_original"

bot = telebot.TeleBot(BOT_TOKEN)
WHITELIST = set()
USER_LANG = {}

MESSAGES = {
    "tr": {
        "welcome": "Hoş geldin! Dil seçmek için /lang_tr veya /lang_en tuşuna tıkla.",
        "lang_set": "Dil başarıyla kuruldu!",
        "join_channel": "Botu kullanabilmek için lütfen şu kanala katılın:\n👉 {channel}\nKatıldıktan sonra bu botu kullanabilirsiniz.",
        "commands_user": "Kullanabileceğin komutlar:\n"
                         "- /btcscan - BTC taramasını başlat\n"
                         "- /help - Yardım mesajı",
        "commands_admin": "- /adduser ve /removeuser - Whitelist yönetimi (sadece admin)",
        "scan_start": "🔁 BTC cüzdan taraması başlıyor... Sadece her 100. cüzdan ve bakiyeli çıkarsa gönderilecek. Bakiyeli bulunursa duracak.",
        "scan_balance_found": "🎉 <b>Bakiyeli cüzdan bulundu! Tarama durduruldu.</b> 🎉",
        "wallet_msg": "<b>{counter}. Taranan Cüzdan</b>\n"
                      "🪙 <b>Blockchain:</b> BTC\n"
                      "📬 <b>Adres:</b> <code>{addr}</code>\n"
                      "🔐 <b>Özel Anahtar (WIF):</b> <code>{priv}</code>\n"
                      "🧠 <b>Seed:</b> <code>{seed}</code>\n"
                      "💰 <b>Bakiye:</b> {balance:.8f} BTC",
        "not_allowed": "Bu özelliği kullanmak için lütfen admin ile iletişime geçin: @cryptologistadmin",
        "added": "✅ @{username} whitelist'e eklendi.",
        "removed": "❌ @{username} whitelist'ten çıkarıldı.",
        "usage_adduser": "Kullanım: /adduser <kullaniciadi>",
        "usage_removeuser": "Kullanım: /removeuser <kullaniciadi>",
        "help_user": "Botun özellikleri:\n"
                     "- /start: Dil seçimi\n"
                     "- /lang_tr ve /lang_en: Dil değiştir\n"
                     "- /btcscan: BTC taraması başlat (yetkililere özel)\n",
        "help_admin": "- /adduser ve /removeuser: Whitelist yönetimi (sadece admin)",
        "no_username": "Kullanıcı adınız yok! Lütfen Telegram ayarlarından bir kullanıcı adı oluşturun."
    },
    "en": {
        "welcome": "Welcome! Click /lang_tr or /lang_en to select language.",
        "lang_set": "Language set successfully!",
        "join_channel": "Please join this channel before using the bot:\n👉 {channel}\nYou can use the bot after joining.",
        "commands_user": "Available commands:\n"
                         "- /btcscan - Start BTC scan\n"
                         "- /help - Display help message",
        "commands_admin": "- /adduser and /removeuser - Whitelist management (admin only)",
        "scan_start": "🔁 BTC wallet scan started... Only every 100th and wallets with balance will be sent. If a wallet with balance is found, scan will stop.",
        "scan_balance_found": "🎉 <b>Wallet with balance found! Scan stopped.</b> 🎉",
        "wallet_msg": "<b>{counter}th Scanned Wallet</b>\n"
                      "🪙 <b>Blockchain:</b> BTC\n"
                      "📬 <b>Address:</b> <code>{addr}</code>\n"
                      "🔐 <b>Private Key (WIF):</b> <code>{priv}</code>\n"
                      "🧠 <b>Seed:</b> <code>{seed}</code>\n"
                      "💰 <b>Balance:</b> {balance:.8f} BTC",
        "not_allowed": "To use this feature, please contact the admin: @cryptologistadmin",
        "added": "✅ @{username} added to whitelist.",
        "removed": "❌ @{username} removed from whitelist.",
        "usage_adduser": "Usage: /adduser <username>",
        "usage_removeuser": "Usage: /removeuser <username>",
        "help_user": "Bot features:\n"
                     "- /start: Language selection\n"
                     "- /lang_tr and /lang_en: Change language\n"
                     "- /btcscan: Start BTC scan (for authorized users only)\n",
        "help_admin": "- /adduser and /removeuser: Whitelist management (admin only)",
        "no_username": "You don't have a username! Please set one in your Telegram settings."
    }
}

def get_lang(user_id):
    return USER_LANG.get(user_id, DEFAULT_LANGUAGE)

def m(user_id, key, **kwargs):
    lang = get_lang(user_id)
    return MESSAGES[lang][key].format(**kwargs)

def is_admin(message):
    uname = (message.from_user.username or "").lower()
    return uname == ADMIN_USERNAME.lower()

def get_username(message):
    return (message.from_user.username or "").lower()

def language_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add("/lang_tr", "/lang_en")
    return markup

def remove_keyboard():
    return telebot.types.ReplyKeyboardRemove()

def get_help_message(user_id, is_admin):
    msg = MESSAGES[get_lang(user_id)]["help_user"]
    if is_admin:
        msg += MESSAGES[get_lang(user_id)]["help_admin"]
    return msg

def send_commands(user_id, chat_id, is_admin):
    msg = MESSAGES[get_lang(user_id)]["commands_user"]
    if is_admin:
        msg += "\n" + MESSAGES[get_lang(user_id)]["commands_admin"]
    bot.send_message(chat_id, msg)

def generate_wallet():
    mnemo = Mnemonic("english")
    seed_words = mnemo.generate(strength=128)
    seed_bytes = mnemo.to_seed(seed_words, passphrase="")
    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed_bytes)
    bip32_child_key_obj = (
        bip32_root_key_obj
        .ChildKey(44 + bip32utils.BIP32_HARDEN)
        .ChildKey(0 + bip32utils.BIP32_HARDEN)
        .ChildKey(0 + bip32utils.BIP32_HARDEN)
        .ChildKey(0)
        .ChildKey(0)
    )
    address = bip32_child_key_obj.Address()
    privkey = bip32_child_key_obj.WalletImportFormat()
    return seed_words, address, privkey

def check_btc_balance(address):
    try:
        url = f"https://blockstream.info/api/address/{address}"
        # Timeout 10ms (0.01 saniye)
        res = requests.get(url, timeout=0.01)
        if res.status_code == 200:
            data = res.json()
            balance = int(data.get("chain_stats", {}).get("funded_txo_sum", 0))
            return balance / 1e8
    except:
        pass
    return 0.0

def btcscan_thread(chat_id, user_id):
    bot.send_message(chat_id, m(user_id, "scan_start"))
    counter = 1
    while True:
        seed, addr, priv = generate_wallet()
        balance = check_btc_balance(addr)
        if counter % 100 == 0 or balance > 0:
            msg = m(
                user_id, "wallet_msg",
                counter=counter, addr=addr, priv=priv, seed=seed, balance=balance
            )
            bot.send_message(chat_id, msg, parse_mode="HTML")
        if balance > 0:
            bot.send_message(chat_id, m(user_id, "scan_balance_found"), parse_mode="HTML")
            break
        counter += 1

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, m(user_id, "welcome"), reply_markup=language_keyboard())

@bot.message_handler(commands=['lang_tr'])
def lang_tr(message):
    user_id = message.from_user.id
    USER_LANG[user_id] = "tr"
    admin = is_admin(message)
    bot.send_message(message.chat.id, m(user_id, "lang_set"), reply_markup=remove_keyboard())
    bot.send_message(
        message.chat.id,
        MESSAGES["tr"]["join_channel"].format(channel=CHANNEL_LINK)
    )
    send_commands(user_id, message.chat.id, admin)

@bot.message_handler(commands=['lang_en'])
def lang_en(message):
    user_id = message.from_user.id
    USER_LANG[user_id] = "en"
    admin = is_admin(message)
    bot.send_message(message.chat.id, m(user_id, "lang_set"), reply_markup=remove_keyboard())
    bot.send_message(
        message.chat.id,
        MESSAGES["en"]["join_channel"].format(channel=CHANNEL_LINK)
    )
    send_commands(user_id, message.chat.id, admin)

@bot.message_handler(commands=['btcscan'])
def btcscan(message):
    user_id = message.from_user.id
    username = get_username(message)
    if not username:
        bot.send_message(message.chat.id, m(user_id, "no_username"))
        return
    if username in WHITELIST or is_admin(message):
        t = threading.Thread(target=btcscan_thread, args=(message.chat.id, user_id))
        t.start()
    else:
        bot.send_message(message.chat.id, m(user_id, "not_allowed"))

@bot.message_handler(commands=['adduser'])
def add_user(message):
    user_id = message.from_user.id
    if not is_admin(message):
        bot.send_message(message.chat.id, m(user_id, "not_allowed"))
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, m(user_id, "usage_adduser"))
        return
    username = parts[1].replace("@", "").lower()
    if not username:
        bot.send_message(message.chat.id, m(user_id, "usage_adduser"))
        return
    WHITELIST.add(username)
    bot.send_message(message.chat.id, m(user_id, "added", username=username))

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    user_id = message.from_user.id
    if not is_admin(message):
        bot.send_message(message.chat.id, m(user_id, "not_allowed"))
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, m(user_id, "usage_removeuser"))
        return
    username = parts[1].replace("@", "").lower()
    if not username:
        bot.send_message(message.chat.id, m(user_id, "usage_removeuser"))
        return
    WHITELIST.discard(username)
    bot.send_message(message.chat.id, m(user_id, "removed", username=username))

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    admin = is_admin(message)
    bot.send_message(message.chat.id, get_help_message(user_id, admin))

@bot.message_handler(func=lambda message: True)
def all(message):
    user_id = message.from_user.id
    username = get_username(message)
    if not username or (username not in WHITELIST and not is_admin(message)):
        bot.send_message(message.chat.id, m(user_id, "not_allowed"))

bot.polling(none_stop=True, interval=0, timeout=20)