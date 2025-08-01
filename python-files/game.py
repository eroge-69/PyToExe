from telethon import TelegramClient, events
import pyautogui
import asyncio
import time

# 👤 User Configuration
api_id = 22024481
api_hash = '9f94f025630f38277122da64e8c09d2a'
user_name = "amitgamexv"
group_username = 'footballstudio_ingles'

# 🎯 Button Coordinates
coordinates = {
    'red': (718, 622),    # 🔴 RED
    'blue': (944, 622),   # 🔵 BLUE
    'tie': (832, 617)     # 🟤 TIE
}

# 💰 Betting Plan (3 Rounds)
bets = [
    {'color': 2, 'tie': 1},   # Round 1: 3 total clicks (2+1)
    {'color': 5, 'tie': 1},   # 1ª GALE: 6 clicks (5+1)
    {'color': 13, 'tie': 2}   # 2ª GALE: 15 clicks (13+2)
]

current_round = 0
last_prediction = None

# 🖱️ Ultra-Fast Click Function (7-second completion)
def rapid_betting(x, y, clicks, max_time=7):
    start_time = time.time()
    try:
        pyautogui.moveTo(x, y, duration=0.1)
        for i in range(clicks):
            pyautogui.click()
            # Calculate remaining time per click
            elapsed = time.time() - start_time
            remaining = max(0.05, (max_time - elapsed) / (clicks - i))
            time.sleep(min(0.2, remaining))
        print(f"⚡ {clicks} clicks at ({x},{y}) in {time.time()-start_time:.2f}s")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# 📩 Message Parser
def parse_message(message):
    msg = message.lower()
    
    # RED Signals
    if 'apostar no: 🔴' in msg or 'apostar no:🔴' in msg:
        return 'red', None
        
    # BLUE Signals
    elif 'apostar no: 🔵' in msg or 'apostar no:🔵' in msg:
        return 'blue', None
        
    # GALE Signals
    elif 'vamos para o 1ª gale' in msg:
        return None, 1
    elif 'vamos para o 2ª gale' in msg:
        return None, 2
        
    return None, None

# 💸 Betting Logic (7-second completion)
def place_bets(prediction):
    global current_round, last_prediction
    
    if current_round >= len(bets):
        current_round = 0
        
    plan = bets[current_round]
    total_clicks = plan['color'] + plan['tie']
    print(f"\n🎲 Round {current_round+1}: {prediction.upper()} ({total_clicks} clicks)")
    
    start_time = time.time()
    
    # Place color bet (dynamic timing)
    if prediction in coordinates:
        x, y = coordinates[prediction]
        rapid_betting(x, y, plan['color'])
    
    # Place tie bet (dynamic timing)
    tx, ty = coordinates['tie']
    rapid_betting(tx, ty, plan['tie'])
    
    last_prediction = prediction
    current_round += 1
    print(f"✅ All bets placed in {time.time()-start_time:.2f} seconds")

# 🤖 Telegram Client
client = TelegramClient('amit_session', api_id, api_hash)

@client.on(events.NewMessage(chats=group_username))
async def handler(event):
    global current_round, last_prediction
    
    message = event.message.text
    print(f"\n📩 Message: {message.strip()}")
    
    prediction, gale = parse_message(message)
    
    if prediction:
        print(f"🔍 Detected {prediction.upper()} signal")
        print("⏳ Waiting 4 seconds...")
        await asyncio.sleep(4)
        place_bets(prediction)
    elif gale and last_prediction:
        current_round = gale
        print(f"⚠️ GALE {gale} detected")
        print("⏳ Waiting 4 seconds...")
        await asyncio.sleep(4)
        place_bets(last_prediction)

# 🚀 Start Bot
print(f"\n🚀 ULTRA-FAST BETTING BOT ACTIVATED")
print(f"👤 User: {user_name}")
print(f"🔴 RED: {coordinates['red']}")
print(f"🔵 BLUE: {coordinates['blue']}")
print(f"🟤 TIE: {coordinates['tie']}")
print("\n⚡ Key Features:")
print("- 4s initial delay after signal")
print("- ALL clicks complete within next 3s (Total 7s)")
print("- Dynamic click timing for perfect speed")

client.start()
client.run_until_disconnected()