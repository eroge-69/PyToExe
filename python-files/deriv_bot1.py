import asyncio
import websockets
import json
import random
import time
import requests

# إعدادات التداول
DERIV_TOKEN = "4UeUtycRJYzRZB1"  # التوكن الخاص بحسابك التجريبي
SYMBOL = "R_100"               # الزوج الذي تريد التداول عليه
STAKE = 1                      # قيمة الصفقة بالدولار
DURATION = 60                  # مدة الصفقة بالثواني

# إعدادات تيليجرام
TELEGRAM_TOKEN = "7951384068:AAFXbaZIMOo6PeAuyC5jLBMsCm-G4M-dtZs"
TELEGRAM_CHAT_ID = "7951384068"

total_profit = 0

# إرسال رسالة إلى تيليجرام
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

# الاتصال بمنصة ديريف
async def authorize(ws):
    await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
    response = await ws.recv()
    data = json.loads(response)
    if 'error' in data:
        send_telegram(f"❌ Authorization Error: {data['error']['message']}")
        raise Exception(data['error']['message'])

# تنفيذ الصفقة
async def execute_trade(ws):
    proposal = {
        "buy": 1,
        "price": STAKE,
        "parameters": {
            "amount": STAKE,
            "basis": "stake",
            "contract_type": "CALL",
            "currency": "USD",
            "duration": 1,
            "duration_unit": "m",
            "symbol": SYMBOL
        }
    }
    await ws.send(json.dumps(proposal))
    response = await ws.recv()
    return json.loads(response)

# محاكاة نتيجة الصفقة التجريبية
async def simulate_result():
    await asyncio.sleep(DURATION)
    win = random.choice([True, False])
    payout = STAKE * 2 if win else 0
    return ("ربح" if win else "خسارة"), payout

# الحلقة الرئيسية
async def main():
    global total_profit
    uri = "wss://ws.deriv.com/websockets/v3"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                await authorize(ws)
                result = await execute_trade(ws)

                if "error" in result:
                    send_telegram(f"❌ خطأ في تنفيذ الصفقة: {result['error']['message']}")
                    continue

                msg = f"📥 دخول صفقة على {SYMBOL}\n💵 القيمة: {STAKE}$\n⏳ المدة: {DURATION} ثانية"
                send_telegram(msg)

                outcome, payout = await simulate_result()
                profit = payout - STAKE
                total_profit += profit

                summary = f"📊 نتيجة الصفقة:\n- الزوج: {SYMBOL}\n- النتيجة: {outcome}\n- العائد: {payout}$\n- الربح/الخسارة: {profit}$\n💰 الإجمالي: {round(total_profit, 2)}$"
                print(summary)
                send_telegram(summary)

                await asyncio.sleep(5)
        except Exception as e:
            print("🔴 Error:", e)
            send_telegram(f"🔴 توقف البوت بسبب خطأ: {str(e)}")
            await asyncio.sleep(10)

# بدء التشغيل التلقائي
asyncio.run(main())
