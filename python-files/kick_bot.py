import asyncio
import json
import websockets
import time
import requests

token_sor = input("Kick Token Girin : ")
channel_sor = input("Kanal ID'sini Girin :")

# Kick API token ve channel ID (yayın kanalının kimliği)
KICK_TOKEN = token_sor
CHANNEL_ID = channel_sor   # Hangi kanal için çalışacaksa ID’sini gir

# Basit spam kuralları
MESSAGE_LIMIT = 5       # Kaç mesajdan sonra spam sayılacak
TIME_WINDOW = 10        # 10 saniye içinde
BANNED_WORDS = ["reklam", "link", "twitch", "http"]

# Kullanıcı mesaj geçmişini tutmak için
user_messages = {}

async def kick_ban(username):
    """Kick API üzerinden kullanıcıyı banla"""
    url = f"https://kick.com/api/v2/channels/{CHANNEL_ID}/bans"
    headers = {
        "Authorization": f"Bearer {KICK_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"username": username, "reason": "Spam tespit edildi"}
    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 200:
            print(f"{username} banlandı (spam).")
        else:
            print(f"Ban başarısız: {r.text}")
    except Exception as e:
        print(f"Ban isteği başarısız: {e}")

async def handle_message(username, message):
    """Mesajı analiz et, spam kontrolü yap"""
    now = time.time()
    
    # Kullanıcının mesaj geçmişini güncelle
    if username not in user_messages:
        user_messages[username] = []
    user_messages[username].append(now)
    
    # Eski mesajları temizle
    user_messages[username] = [t for t in user_messages[username] if now - t < TIME_WINDOW]
    
    # Yasaklı kelime kontrolü
    if any(word in message.lower() for word in BANNED_WORDS):
        await kick_ban(username)
        return
    
    # Spam mesaj limiti kontrolü
    if len(user_messages[username]) >= MESSAGE_LIMIT:
        await kick_ban(username)

async def listen_chat():
    url = f"wss://ws-api.kick.com/v2/chat/{CHANNEL_ID}"
    async with websockets.connect(url) as ws:
        print("Chat bağlantısı kuruldu!")
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                
                if data.get("type") == "message":
                    username = data["sender"]["username"]
                    message = data["content"]
                    print(f"{username}: {message}")
                    await handle_message(username, message)
            except Exception as e:
                print(f"Hata: {e}")
                break

asyncio.run(listen_chat())