from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import random
import requests
import json
from datetime import datetime
from telegram.error import TelegramError

TOKEN = '8010396487:AAEOL6JhGwjdxqFh7wq-8l-WflFh58id_30'
SOL_ADDRESS = "GcEM2e8ScJ1Fq1k7rNXCKnrTqhRHabNuHrkSNmcUngV8"

PENDING_FILE = "pending_payments.json"
PAID_FILE = "paid_users.json"

# Your Telegram group chat ID (replace this with your group's actual ID)
GROUP_CHAT_ID = -1002176594803

# Load JSON helper
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# Save JSON helper
def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Load data at startup
pending_payments = load_json(PENDING_FILE)
paid_users = load_json(PAID_FILE)

# --- Solana RPC helper functions ---
RPC_URL = "https://mainnet.helius-rpc.com/?api-key=434560ec-a871-4269-a277-781edbbb2e84"

def get_recent_transactions(wallet):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": 10}]
    }
    resp = requests.post(RPC_URL, json=payload).json()
    return [tx["signature"] for tx in resp.get("result", [])]

def get_transaction_details(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    resp = requests.post(RPC_URL, json=payload).json()
    return resp.get("result", {})

def check_sol_payment(expected_amount):
    """
    Check recent transactions to SOL_ADDRESS to see if any transaction exactly matches expected_amount.
    Return True if payment detected.
    """
    tx_sigs = get_recent_transactions(SOL_ADDRESS)
    for sig in tx_sigs:
        tx_data = get_transaction_details(sig)
        instructions = tx_data.get("transaction", {}).get("message", {}).get("instructions", [])

        for instr in instructions:
            if instr.get("program") == "system" and instr.get("parsed", {}).get("type") == "transfer":
                info = instr["parsed"]["info"]
                dest = info["destination"]
                lamports = int(info["lamports"])
                sol_received = lamports / 1e9
                if dest == SOL_ADDRESS and abs(sol_received - expected_amount) < 1e-9:  # Exact match
                    return True
    return False

# --- Fetch real-time SOL price in EUR from Coinbase ---
def get_sol_price_eur():
    try:
        url = "https://api.coinbase.com/v2/prices/SOL-EUR/spot"
        response = requests.get(url)
        data = response.json()
        price = float(data["data"]["amount"])
        return price
    except Exception as e:
        print("Error fetching SOL price:", e)
        return None

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Savaitė (7,00 €)", callback_data='sub_1')],
        [InlineKeyboardButton("1 Mėnuo (15,00 €)", callback_data='sub_2')],
        [InlineKeyboardButton("2 Mėnesiai (25,00 €)", callback_data='sub_3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption_text = (
        "🇱🇹 Sveikas atvykęs į vyrų bendruomenę, kur tikrumas susitinka su intymumu.\n"
        "Tai – ne eilinė grupė. Čia renkasi vyrai, kurie vertina autentišką lietuvišką turinį, "
        "diskretišką erdvę ir aukštą kokybę.\n\n"
        "🔍 Ką rasi viduje?\n"
        "• 🎞 Daugiau nei 53 000 unikalių nuotraukų ir vaizdo įrašų\n"
        "• 💃 Virš 200 tikrų lietuvaičių\n"
        "• 🔐 Uždara, saugi ir pasitikėjimu grįsta aplinka"
    )

    photo_message = await update.message.reply_photo(
        photo="https://i.postimg.cc/7YvQcj5Z/proof.jpg",
        caption=caption_text,
        reply_markup=reply_markup
    )

    context.user_data["start_photo_msg_id"] = photo_message.message_id

# --- Button Handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    photo_msg_id = context.user_data.get("start_photo_msg_id")
    if photo_msg_id:
        try:
            await context.bot.delete_message(chat_id=query.message.chat.id, message_id=photo_msg_id)
        except Exception as e:
            print("Couldn't delete image:", e)
        context.user_data.pop("start_photo_msg_id", None)

    if query.data.startswith('sub_'):
        duration = query.data.split('_')[1]
        context.user_data['duration'] = duration

        text = (
            "1️⃣ Pasirinkite patogiausią mokėjimo metodą:\n\n"
            "PayPal – Galite atsiskaityti naudojant PayPal balansą arba pasirinkti „Debit or Credit Card“ kortelę. "
            "Taip pat priimamos Google Pay, Apple Pay ir banko kortelės.\n\n"
            "Kriptovaliuta – Rinkitės šį metodą, jei pageidaujate greito, saugaus ir anonimiško atsiskaitymo.\n\n"
            "2️⃣ Sėkmingai atlikus mokėjimą:\n\n"
            "Spauskite /join mygtuką, kuris pasirodys žemiau.\n\n"
            "Pasirinkite „Prisijungti“.\n\n"
            "Ir viskas! Mėgaukitės neribota prieiga į mūsų bendruomenę."
        )

        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data='payment_paypal')],
            [InlineKeyboardButton("Kriptovaliuta", callback_data='payment_crypto')]
        ]

        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'payment_paypal':
        text = (
            "💳 Pasirinkote PayPal.\n\n"
            "Galite atsiskaityti naudojant PayPal balansą arba korteles (Debit, Credit, Google Pay, Apple Pay).\n\n"
            "Po sėkmingo mokėjimo spauskite /join mygtuką ir prisijunkite prie bendruomenės."
        )
        await query.message.reply_text(text)

    elif query.data == 'payment_crypto':
        duration = context.user_data.get('duration')

        base_price_eur = {"1": 7, "2": 15, "3": 25}.get(duration, 7)

        sol_price = get_sol_price_eur()
        if sol_price is None:
            await query.message.reply_text("Atsiprašome, šiuo metu nepavyko gauti SOL kainos. Bandykite vėliau.")
            return

        sol_amount = base_price_eur / sol_price

        offset = random.randint(1, 999) / 1_000_000
        unique_amount = sol_amount + offset
        unique_amount = round(unique_amount, 6)

        user_id_str = str(query.from_user.id)
        username = f"@{query.from_user.username}" if query.from_user.username else query.from_user.full_name

        pending_payments[user_id_str] = {
            "amount": unique_amount,
            "subscription": duration,
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        save_json(PENDING_FILE, pending_payments)

        await query.message.reply_text(
            f"💸 Mesk `{unique_amount}` SOL į adresą:\n\n"
            f"`{SOL_ADDRESS}`\n\n"
            "Palauk, bus patvirtinta automatiškai.",
            parse_mode="Markdown"
        )

# --- Join Command: Creates one-time invite link if user is paid, caches it ---
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_str = str(update.effective_user.id)
    if user_id_str not in paid_users:
        await update.message.reply_text(
            "🚫 Deja, jūs dar nesate prenumeratorius. Prašome sumokėti už prenumeratą, kad gautumėte prieigą."
        )
        return

    # Check if invite link already exists for this paid user
    if "invite_link" in paid_users[user_id_str]:
        invite_link = paid_users[user_id_str]["invite_link"]
        await update.message.reply_text(
            f"🎉 Jūsų unikalus prisijungimo kvietimo nuoroda:\n{invite_link}"
        )
        return

    # Otherwise, create a new one-time invite link
    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=GROUP_CHAT_ID,
            member_limit=1  # One-time use
        )
        invite_link = invite.invite_link

        # Save the invite link for this user in paid_users.json
        paid_users[user_id_str]["invite_link"] = invite_link
        save_json(PAID_FILE, paid_users)

        await update.message.reply_text(
            f"🎉 Jūsų unikalus prisijungimo kvietimo nuoroda:\n{invite_link}"
        )
    except TelegramError as e:
        print(f"Failed to create invite link: {e}")
        await update.message.reply_text(
            "Atsiprašome, nepavyko sukurti unikalios kvietimo nuorodos. Bandykite vėliau."
        )
        
# --- Background task: Solana payment detection ---
async def monitor_solana_payments(bot):
    while True:
        try:
            for user_id_str, info in list(pending_payments.items()):
                expected_amount = info["amount"]
                if check_sol_payment(expected_amount):
                    username = info.get("username", "N/A")
                    subscription = info.get("subscription", "N/A")
                    timestamp_paid = datetime.utcnow().isoformat()

                    try:
                        await bot.send_message(int(user_id_str), f"✅ Gauta {expected_amount} SOL! Sveikiname, {username}.\n"
                                                                 f"Prenumerata: {subscription} mėnesiai.\n\n"
                                                                 "Dabar galite naudoti komandą /join, kad gautumėte unikalų prisijungimo kvietimą.")
                    except Exception as e:
                        print(f"Failed to send message to {user_id_str}: {e}")

                    paid_users[user_id_str] = {
                        "username": username,
                        "subscription": subscription,
                        "paid_amount": expected_amount,
                        "paid_timestamp": timestamp_paid
                    }
                    save_json(PAID_FILE, paid_users)

                    del pending_payments[user_id_str]
                    save_json(PENDING_FILE, pending_payments)

        except Exception as e:
            print("Error checking payments:", e)

        await asyncio.sleep(30)

# --- Main ---
def main():
    async def on_startup(app_):
        asyncio.create_task(monitor_solana_payments(app_.bot))

    app = Application.builder().token(TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("join", join_command))

    app.run_polling()

if __name__ == '__main__':
    main()
