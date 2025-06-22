
import time
import requests
from binance.client import Client
from datetime import datetime

# Telegram Bot Settings
TELEGRAM_TOKEN = "7016796408:AAGuUne0pdEyzfgXuI0pGll-5kFkM251bko"
CHAT_ID = "1777406294"

client = Client()

symbols = [
    "BOBUSDT", "ORDIUSDT", "ARMKUSDT", "BANANAUSDT",
    "XVGUSDT", "AIXBTUSDT", "JAGERUSDT", "RXPUSDT",
    "PEPEUSDT", "DOGEUSDT", "MEMEUSDT", "FETUSDT"
]

ALERT_THRESHOLD = 400000  # تنبيه إذا تجاوز الحجم هذا الرقم

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def report_liquidity():
    message = f"📊 تقرير السيولة (كل نصف ساعة)\n"
    alerts = []
    for symbol in symbols:
        try:
            klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_30MINUTE, limit=1)
            if klines:
                volume = float(klines[0][7])
                message += f"• {symbol}: ${volume:,.0f}\n"
                if volume >= ALERT_THRESHOLD:
                    alerts.append(f"🚨 سيولة مرتفعة!
{symbol} تجاوز {ALERT_THRESHOLD:,} → ${volume:,.0f}")
        except Exception as e:
            message += f"• {symbol}: خطأ\n"
    message += f"\n🕒 آخر تحديث: {datetime.now().strftime('%H:%M')}"
    send_telegram_message(message)
    for alert in alerts:
        send_telegram_message(alert)

while True:
    print(f"⏱️ إرسال تقرير وتنبيه - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_liquidity()
    time.sleep(1800)  # كل نصف ساعة
