
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from telegram import Bot
import schedule
import time

TELEGRAM_TOKEN = "7965743782:AAGKi9xNy2NZIIEBxUQyvSayNznttvQIBjg"
CHAT_ID = "6606597566"

def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

def analyze_and_send_signal():
    try:
        df = yf.download("USDTRY=X", interval="1h", period="5d")
        df['EMA9'] = ta.ema(df['Close'], length=9)
        df['EMA21'] = ta.ema(df['Close'], length=21)
        df['RSI'] = ta.rsi(df['Close'])
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']

        last = df.iloc[-1]
        message = f"📈 USD/TRY Analiz ({last.name.strftime('%Y-%m-%d %H:%M')}):\n"

        if last['ADX'] > 25:
            if last['EMA9'] > last['EMA21']:
                message += "🔹 Trend Güçlü → AL sinyali"
            else:
                message += "🔻 Trend Güçlü → SAT sinyali"
        else:
            if last['RSI'] < 30:
                message += "🟢 RSI düşük → AL sinyali (Aşırı satım)"
            elif last['RSI'] > 70:
                message += "🔴 RSI yüksek → SAT sinyali (Aşırı alım)"
            else:
                message += "⚪ Net bir sinyal yok, beklemede."

        send_telegram_message(message)

    except Exception as e:
        send_telegram_message(f"🚨 Hata oluştu: {e}")

schedule.every(1).hours.do(analyze_and_send_signal)
print("✅ Bot çalışıyor. Sinyal bekleniyor...")
while True:
    schedule.run_pending()
    time.sleep(1)
