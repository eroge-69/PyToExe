# z.py - Telegram Support Bot (Professional/Styled Version)

import logging
from uuid import uuid4
from typing import Dict, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ----------------- CONFIG -----------------
BOT_TOKEN = "8026041396:AAFsTUhg6BSfis-XPo8Px9k-6c905ZWMNys"  # Twój token
ADMIN_CHAT_ID = 6438519831  # Twój chat id

(REASON, INVOICE, EMAIL, PROOFS) = range(4)

tickets: Dict[str, Dict[str, Any]] = {}
open_ticket_for_admin: Dict[int, str] = {}
open_ticket_for_user: Dict[int, str] = {}

SAMPLE_TEMPLATE = (
    "📝 <b>Sample (fill this format exactly):</b>\n\n"
    "• <b>Reason:</b>\n"
    "• <b>Invoice ID:</b>\n"
    "• <b>Email:</b>\n"
    "• <b>Proofs/record in Imgur:</b>\n"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# -------------- Helpers -----------------
def ticket_message_text(ticket_id: str, data: Dict[str, Any]) -> str:
    return (
        f"🎫 <b>New Support Ticket</b> — <code>{ticket_id}</code>\n\n"
        f"👤 <b>From:</b> {data['user_name']} (id: <code>{data['user_id']}</code>)\n"
        f"💡 <b>Reason:</b> {data['reason']}\n"
        f"🧾 <b>Invoice ID:</b> {data['invoice']}\n"
        f"📧 <b>Email:</b> {data['email']}\n"
        f"📎 <b>Proofs:</b> {data['proofs']}\n\n"
        "⚡ Use the buttons below to <b>Open</b> or <b>Ignore</b> this ticket."
    )


def admin_controls_markup(ticket_id: str, status: str = "new") -> InlineKeyboardMarkup:
    if status == "new":
        buttons = [
            [InlineKeyboardButton("🟢 Open Ticket", callback_data=f"open::{ticket_id}")],
            [InlineKeyboardButton("⚪ Ignore Ticket", callback_data=f"ignore::{ticket_id}")],
        ]
    elif status == "open":
        buttons = [
            [InlineKeyboardButton("🔒 Close Ticket", callback_data=f"close::{ticket_id}")],
        ]
    else:
        buttons = []
    return InlineKeyboardMarkup(buttons)


# -------------- Handlers -----------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Welcome to WolnyBooks Gateway Support!</b>\n\n"
        "To open a support ticket, please follow the short form below:\n\n"
        f"{SAMPLE_TEMPLATE}\n"
        "✏️ <b>Step 1:</b> Briefly state the reason for your ticket.",
        parse_mode="HTML",
    )
    return REASON


async def reason_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reason"] = update.message.text.strip()
    await update.message.reply_text("🧾 <b>Step 2:</b> Invoice ID (please paste invoice/order id):", parse_mode="HTML")
    return INVOICE


async def invoice_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["invoice"] = update.message.text.strip()
    await update.message.reply_text("📧 <b>Step 3:</b> Email used for purchase or contact email:", parse_mode="HTML")
    return EMAIL


async def email_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text.strip()
    await update.message.reply_text(
        "📎 <b>Step 4:</b> Proofs / record link (Imgur or other). "
        "You can also attach images after ticket creation.",
        parse_mode="HTML",
    )
    return PROOFS


async def proofs_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        context.user_data["proofs"] = update.message.text.strip()
    elif update.message.photo or update.message.document:
        context.user_data["proofs"] = "User provided attachment(s)."
    else:
        context.user_data["proofs"] = "No proof provided."

    ticket_id = uuid4().hex[:8]
    ticket_data = {
        "ticket_id": ticket_id,
        "user_id": update.effective_user.id,
        "user_name": update.effective_user.full_name,
        "reason": context.user_data.get("reason", ""),
        "invoice": context.user_data.get("invoice", ""),
        "email": context.user_data.get("email", ""),
        "proofs": context.user_data.get("proofs", ""),
        "status": "new",
    }
    tickets[ticket_id] = ticket_data

    await update.message.reply_text(
        f"✅ <b>Ticket Created!</b>\n\n"
        f"🆔 <b>Ticket ID:</b> {ticket_id}\n"
        f"💡 <b>Reason:</b> {ticket_data['reason']}\n"
        f"🧾 <b>Invoice ID:</b> {ticket_data['invoice']}\n"
        f"📧 <b>Email:</b> {ticket_data['email']}\n"
        f"📎 <b>Proofs:</b> {ticket_data['proofs']}\n\n"
        "Support will contact you soon. Reply here to add images if needed.",
        parse_mode="HTML",
    )

    # Send ticket to admin
    msg_text = ticket_message_text(ticket_id, ticket_data)
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg_text,
        parse_mode="HTML",
        reply_markup=admin_controls_markup(ticket_id, status="new"),
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ <b>Ticket creation cancelled.</b>", parse_mode="HTML")
    return ConversationHandler.END


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, ticket_id = query.data.split("::", 1)
    ticket = tickets.get(ticket_id)
    if not ticket:
        await query.edit_message_text("⚠️ Ticket not found.")
        return

    if action == "ignore":
        ticket["status"] = "ignored"
        await query.edit_message_text(f"⚪ <b>Ticket {ticket_id} ignored.</b>", parse_mode="HTML")
        await context.bot.send_message(chat_id=ticket["user_id"], text=f"⚠️ Your ticket {ticket_id} was ignored.")

    elif action == "open":
        ticket["status"] = "open"
        open_ticket_for_admin[ADMIN_CHAT_ID] = ticket_id
        open_ticket_for_user[ticket["user_id"]] = ticket_id
        await query.edit_message_text(
            f"🟢 <b>Ticket {ticket_id} is now OPEN.</b>\nYou can reply directly here.",
            parse_mode="HTML",
            reply_markup=admin_controls_markup(ticket_id, status="open"),
        )
        await context.bot.send_message(chat_id=ticket["user_id"], text=f"🟢 Your ticket {ticket_id} has been opened.")

    elif action == "close":
        ticket["status"] = "closed"
        open_ticket_for_admin.pop(ADMIN_CHAT_ID, None)
        open_ticket_for_user.pop(ticket["user_id"], None)
        await query.edit_message_text(f"🔒 <b>Ticket {ticket_id} closed.</b>", parse_mode="HTML")
        await context.bot.send_message(chat_id=ticket["user_id"], text=f"🔒 Your ticket {ticket_id} has been closed.")


async def admin_message_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    ticket_id = open_ticket_for_admin.get(ADMIN_CHAT_ID)
    if not ticket_id:
        return
    ticket = tickets.get(ticket_id)
    if ticket and ticket["status"] == "open":
        user_id = ticket["user_id"]
        if update.message.text:
            await context.bot.send_message(chat_id=user_id, text="💬 <b>Support:</b>\n" + update.message.text, parse_mode="HTML")
        elif update.message.photo:
            await update.message.reply_chat_action(action=ChatAction.UPLOAD_PHOTO)
            await context.bot.send_photo(chat_id=user_id, photo=update.message.photo[-1].file_id)


async def user_message_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ticket_id = open_ticket_for_user.get(user_id)
    if not ticket_id:
        return
    ticket = tickets.get(ticket_id)
    if ticket and ticket["status"] == "open" and update.message.text:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔁 Message from <b>{update.effective_user.full_name}</b> (ticket <code>{ticket_id}</code>):\n{update.message.text}",
            parse_mode="HTML",
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, reason_step)],
            INVOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, invoice_step)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_step)],
            PROOFS: [MessageHandler((filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, proofs_step)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(admin_callback_handler))
    application.add_handler(MessageHandler(filters.Chat(ADMIN_CHAT_ID) & ~filters.COMMAND, admin_message_relay))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.User(ADMIN_CHAT_ID), user_message_relay))

    logger.info("🚀 WolnyBooks Gateway Support Bot starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
