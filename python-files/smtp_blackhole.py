import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
from datetime import datetime
import os

LOG_DIR = "logs"

class BlackholeHandler(AsyncMessage):
    async def handle_message(self, message):
        now = datetime.now()
        log_filename = now.strftime("smtp_blackhole_%Y%m%d_%H.log")
        log_path = os.path.join(LOG_DIR, log_filename)

        os.makedirs(LOG_DIR, exist_ok=True)

        log_entry = (
            f"--- {now.isoformat()} ---\n"
            f"From: {message['from']}\n"
            f"To: {message['to']}\n"
            f"Subject: {message['subject']}\n"
            f"Date: {message['date']}\n\n"
        )

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        return

if __name__ == "__main__":
    # Vérifie si on a les droits administrateur pour utiliser le port 25
    if os.name == "nt":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Ce script doit être exécuté avec les droits administrateur pour écouter sur le port 25.")
            exit(1)

    handler = BlackholeHandler()
    controller = Controller(handler, hostname="0.0.0.0", port=25)
    controller.start()
    print("SMTP Blackhole actif sur le port 25. Ctrl+C pour arrêter.")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()