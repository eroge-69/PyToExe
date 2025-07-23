import discord
import asyncio
import random

# ==== CẤU HÌNH ====
TOKEN = "YOUR_BOT_TOKEN"  # Thay bằng bot token thật của bạn
CHANNEL_ID = 123456789012345678  # Thay bằng ID kênh muốn gửi tin
messages = [
    "Xin chào!",
    "Bot này đang hoạt động.",
    "Đây là một tin nhắn tự động.",
    "Gửi ngẫu nhiên với độ trễ.",
    "Hy vọng bạn có một ngày tốt lành!",
]

min_delay = 1   # 👈 thời gian chờ tối thiểu 1 giây
max_delay = 10  # 👈 thời gian chờ tối đa 10 giây
# ===================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 Bot đã đăng nhập: {client.user}")
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Không tìm thấy kênh. Kiểm tra lại CHANNEL_ID.")
        return

    while True:
        msg = random.choice(messages)
        delay = random.uniform(min_delay, max_delay)
        try:
            await channel.send(msg)
            print(f"✅ Đã gửi: '{msg}' | ⏱ Chờ {round(delay, 2)} giây")
        except discord.errors.HTTPException as e:
            print(f"⚠️ HTTP Exception: {e}")
        except Exception as e:
            print(f"⚠️ Lỗi khác: {e}")
        await asyncio.sleep(delay)

client.run(TOKEN)
