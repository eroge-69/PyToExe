import os
import gspread
from datetime import datetime
from dotenv import load_dotenv
import requests

# โหลด ENV
load_dotenv(".env_timeexit")
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

# ตรวจค่า ENV
if not all([TOKEN, CHAT_ID, SPREADSHEET_ID, SHEET_NAME]):
    print("❌ Environment variables ไม่ครบ")
    exit()

# เชื่อมต่อ Google Sheets
gc = gspread.service_account(filename="credentials.json")
ws = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
data = ws.get_all_records()

today = datetime.today().strftime("%d/%m/%Y")
msg_lines = []
context_updated = False

for i, row in enumerate(data):
    symbol = row.get("Symbol", "")
    unreal_raw = str(row.get("%Unrealized P/L", "")).replace("%", "").replace(",", "")
    entry_date = row.get("Entry Date", "")
    score_col = list(row.keys()).index("S Score") + 1
    time_col = list(row.keys()).index("Time Exit") + 1

    try:
        val = float(unreal_raw)
    except:
        continue

    try:
        entry = datetime.strptime(entry_date.strip(), "%d/%m/%Y")
        today_dt = datetime.today()
        days_held = (today_dt - entry).days
        ws.update_cell(i + 2, time_col, days_held)
    except:
        days_held = "?"

    # คำนวณ Score
    if val > 5:
        score = "A"
    elif val > 3:
        score = "B"
    elif val > 0:
        score = "C"
    else:
        score = "D"
    ws.update_cell(i + 2, score_col, score)

    # Time Exit เงื่อนไข
    if isinstance(days_held, int) and days_held > 5:
        if days_held > 15:
            rec = "ถือเกิน 15 วัน → ขายทั้งหมด"
        elif days_held > 10:
            rec = "ถือเกิน 10 วัน → ขาย 50%"
        else:
            rec = "ถือเกิน 5 วัน → ขาย 25%"

        line = f"{symbol} : ถือมา {days_held} วัน • {rec} • กำไร {val:.2f}% • Score {score}"
        msg_lines.append(line)
        context_updated = True

# สร้างข้อความ
if context_updated:
    full_msg = "🔔 แจ้งเตือน Time-Based Exit:\n\n"
    full_msg += "\n".join(msg_lines)
    full_msg += "\n\n"
    full_msg += f"\n📆 วันที่: {today}"
else:
    full_msg = f"📄 ไม่มีรายการเข้าเงื่อนไขวันนี้\n📆 วันที่: {today}"

print(full_msg)

# ส่ง Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": full_msg})