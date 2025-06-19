import cv2
from pyzbar.pyzbar import decode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
import asyncio
from telegram import Bot
import os
import smtplib
from email.message import EmailMessage

# === CONFIGURATION ===
BOT_TOKEN = "8144152240:AAFaFiNVHFNPgqvfPcOoRzn65rNjXv50JFw"
CHAT_ID = "7694955169"
EMAIL_ADDRESS = "molsonlaorden0830@gmail.com"
EMAIL_PASSWORD = "_Laorden10897moL_"
RECEIVER = "molsonlaorden12719@gmail.com"

# Ensure log directory exists
LOG_DIR = "C:\\Users\\Minero$\\Downloads\\Coded System\\Logs & Backups"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "Attendance_System_Log.txt")
BACKUP_TRACK_FILE = os.path.join(LOG_DIR, "Backup.txt")

# === GOOGLE SHEETS SETUP ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("AttendanceSheet").sheet1

# === TELEGRAM SETUP ===
bot = Bot(token=BOT_TOKEN)

# === LOGGING ===
def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        write_log(f"[❌] Telegram error: {e}")

# === DAILY RESET ===
def reset_sheet_daily():
    today = date.today().strftime("%Y-%m-%d")
    try:
        meta_cell = sheet.cell(1, 4).value  # D1 stores last reset date
    except:
        sheet.update_cell(1, 4, "")
        meta_cell = ""

    if meta_cell != today:
        sheet.clear()
        sheet.update('A1:C1', [['ID', 'Time In', 'Time Out']])
        sheet.update_cell(1, 4, today)
        write_log(f"📅 Sheet reset for {today}")
    else:
        write_log(f"📝 Sheet already reset today ({today})")

# === WEEKLY BACKUP ===
def backup_sheet_weekly():
    today = date.today()
    week_key = today.strftime("%Y-W%U")

    if os.path.exists(BACKUP_TRACK_FILE):
        with open(BACKUP_TRACK_FILE, "r") as f:
            last = f.read().strip()
            if last == week_key:
                write_log("🔁 Weekly backup already done.")
                return

    try:
        backup_title = f"Attendance Backup - Week {today.strftime('%U')}"
        client.copy(sheet.spreadsheet.id, title=backup_title)
        write_log(f"🗂 Backup created: {backup_title}")
        with open(BACKUP_TRACK_FILE, "w") as f:
            f.write(week_key)
    except Exception as e:
        write_log(f"[❌] Backup failed: {e}")

# === EMAIL LOG FILE ===
def send_log_email():
    if not os.path.exists(LOG_FILE): return

    try:
        msg = EmailMessage()
        msg['Subject'] = '📄 Weekly Attendance Log'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECEIVER
        msg.set_content("Attached is the attendance log file.")

        with open(LOG_FILE, "rb") as f:
            msg.add_attachment(f.read(), maintype='text', subtype='plain', filename="qr_attendance_log.txt")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        write_log("📧 Log file emailed successfully.")
    except Exception as e:
        write_log(f"[❌] Failed to send email: {e}")

# === ATTENDANCE FUNCTION ===
async def mark_attendance(id_):
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    all_records = sheet.get_all_records()

    for i, row in enumerate(all_records, start=2):
        if row['ID'] == id_:
            if row['Time Out'] != '':
                msg = f"⚠️ {id_} already logged out."
                await send_telegram_message(msg)
                write_log(msg)
                return

            time_in = datetime.strptime(row['Time In'], "%Y-%m-%d %H:%M:%S")
            time_since_in = (now - time_in).total_seconds()
            timeout_seconds = 10

            if time_since_in < timeout_seconds:
                remaining = timeout_seconds - int(time_since_in)
                msg = f"⏳ {id_}, wait {remaining}s before logging out."
                await send_telegram_message(msg)
                write_log(msg)
                return

            sheet.update_cell(i, 3, now_str)
            msg = f"📤 {id_} logged out at {now_str}"
            await send_telegram_message(msg)
            write_log(msg)
            return

    sheet.append_row([id_, now_str, ''])
    msg = f"✅ {id_} logged in at {now_str}"
    await send_telegram_message(msg)
    write_log(msg)

# === INIT ===
reset_sheet_daily()
backup_sheet_weekly()
if date.today().weekday() == 6:
    send_log_email()

# === START QR SCANNER ===
cap = cv2.VideoCapture(0)
print("📷 QR scanner started. Press Q to quit.")

last_id = None
cooldown = 2
last_scan_time = datetime.now()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    decoded_objs = decode(frame)
    for obj in decoded_objs:
        id_text = obj.data.decode('utf-8')
        now = datetime.now()

        if id_text != last_id or (now - last_scan_time).total_seconds() > cooldown:
            asyncio.run(mark_attendance(id_text))
            last_id = id_text
            last_scan_time = now

        cv2.rectangle(frame, (obj.rect.left, obj.rect.top),
                             (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                             (0, 255, 0), 2)

    cv2.imshow("QR Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()