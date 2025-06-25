
from telethon import TelegramClient, events
import MetaTrader5 as mt5
import re
import time
from datetime import datetime
import pytz
import winsound

api_id = 22021158
api_hash = '55491c802739cd4cec3a4d7de7a765bc'
channel_username = 'mekoalerts'
user_phone = '+98944309867'

def connect_mt5():
    if not mt5.initialize():
        print("❌ فشل الاتصال بـ MetaTrader 5")
        quit()
    print("✅ تم الاتصال بـ MetaTrader 5")

def place_order(symbol, order_type, volume, price, sl, tp):
    order_type_code = mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_code,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "AutoTrade by Telegram",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ فشل تنفيذ الصفقة: {result.retcode}")
        play_sound(success=False)
        send_notification(f"❌ فشل تنفيذ صفقة {symbol.upper()} | السبب: {result.retcode}")
    else:
        print("✅ صفقة تم تنفيذها بنجاح")
        play_sound(success=True)
        send_notification(f"✅ صفقة نُفذت: {symbol.upper()} - {order_type.upper()} @ {price}")

def play_sound(success=True):
    if success:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    else:
        winsound.MessageBeep(winsound.MB_ICONHAND)

def send_notification(message):
    try:
        client.send_message(user_phone, message)
    except Exception as e:
        print(f"⚠️ فشل إرسال إشعار: {e}")

def parse_signal(message):
    try:
        pair = re.search(r'Pair\s*:\s*(\w+)', message).group(1)
        type_ = re.search(r'Type\s*:\s*(Buy|Sell)', message, re.IGNORECASE).group(1).lower()
        entry = float(re.search(r'En\s*[-:]?\s*(\d+\.?\d*)', message).group(1))
        sl = float(re.search(r'SL\s*[-:]?\s*(\d+\.?\d*)', message).group(1))
        tp1 = float(re.search(r'TP1\s*[-:]?\s*(\d+\.?\d*)', message).group(1))
        return {
            "pair": pair,
            "type": type_,
            "entry": entry,
            "sl": sl,
            "tp": tp1
        }
    except Exception as e:
        print("⚠️ فشل في تحليل الرسالة:", e)
        return None

client = TelegramClient('session_meko', api_id, api_hash)

@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    msg = event.message.message
    print(f"\n📩 رسالة جديدة:\n{msg}")
    signal = parse_signal(msg)
    if signal:
        print("✅ إشارة مكتشفة، جاري التنفيذ...")
        place_order(
            symbol=signal['pair'],
            order_type=signal['type'],
            volume=0.1,
            price=signal['entry'],
            sl=signal['sl'],
            tp=signal['tp']
        )
    else:
        print("🚫 ليست إشارة صالحة")

if __name__ == '__main__':
    connect_mt5()
    print("🚀 البوت قيد التشغيل... في انتظار الإشارات من تليجرام")
    client.start()
    client.run_until_disconnected()
