import imaplib
import email
import os
import csv
import zipfile
from email.header import decode_header
from datetime import datetime

# === Настройки ===
IMAP_SERVER = "imap.mail.ru"
EMAIL_ACCOUNT = "your_email@mail.ru"   # твой email
PASSWORD = "your_app_password"         # пароль приложения
SAVE_DIR = "mail_export"

# === Вспомогательные функции ===
def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return "".join(
        part.decode(charset or "utf-8") if isinstance(part, bytes) else part
        for part, charset in decoded
    )

# Подключение к почте
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_ACCOUNT, PASSWORD)
mail.select("INBOX")

status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()

os.makedirs(SAVE_DIR, exist_ok=True)
csv_path = os.path.join(SAVE_DIR, "emails.csv")

with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Дата", "Отправитель", "Тема", "Текст (первые 200 символов)", "Вложения"])

    for i, eid in enumerate(email_ids, start=1):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                date_str = msg.get("Date", "")
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    date_fmt = date_obj.strftime("%Y-%m-%d_%H-%M-%S")
                except:
                    date_fmt = "unknown_date"

                sender = decode_mime_words(msg.get("From", ""))
                subject = decode_mime_words(msg.get("Subject", ""))

                # Извлечение текста письма
                body = ""
                attachments_list = []
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            charset = part.get_content_charset() or "utf-8"
                            try:
                                body = part.get_payload(decode=True).decode(charset, errors="ignore")
                            except:
                                pass
                        elif part.get("Content-Disposition"):
                            filename = decode_mime_words(part.get_filename())
                            if filename:
                                attach_dir = os.path.join(SAVE_DIR, "attachments", date_fmt)
                                os.makedirs(attach_dir, exist_ok=True)
                                filepath = os.path.join(attach_dir, filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                attachments_list.append(filepath)
                else:
                    charset = msg.get_content_charset() or "utf-8"
                    body = msg.get_payload(decode=True).decode(charset, errors="ignore")

                writer.writerow([date_str, sender, subject, body[:200], "; ".join(attachments_list)])

        print(f"[{i}/{len(email_ids)}] Загружено")

mail.logout()

# Упаковка в ZIP
zip_path = SAVE_DIR + ".zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(SAVE_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.relpath(filepath, SAVE_DIR))

print(f"\n✅ Готово! Архив: {zip_path}")
