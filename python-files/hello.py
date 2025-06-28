import time
from telethon.sync import TelegramClient

# User's Telegram API credentials
api_id = 21077474
api_hash = 'aefc0f9df7ee48aaa35a2e08d62ad204'

# Fixed message you want to send
message_text = (
    "express vpn only 180 tk 1 month\n"
    "এক্সপ্রেস ভিপিন মাত্র ১৮০ টাকা এক মাসের জন্য\n"
    "express vpn only 180 tk 1 month\n"
    "এক্সপ্রেস ভিপিন মাত্র ১৮০ টাকা এক মাসের জন্য\n"
    "express vpn only 180 tk 1 month\n"
    "এক্সপ্রেস ভিপিন মাত্র ১৮০ টাকা এক মাসের জন্য"
)

# Connect to Telegram and send the message to all groups with 30-second interval
with TelegramClient('pixelhut_auto_session', api_id, api_hash) as client:
    dialogs = client.get_dialogs()
    group_count = 0
    for dialog in dialogs:
        if dialog.is_group:
            try:
                client.send_message(dialog.id, message_text)
                print(f"✅ Sent to: {dialog.name}")
                group_count += 1
                time.sleep(30)  # Wait 30 seconds before sending to the next group
            except Exception as e:
                print(f"❌ Failed to send to: {dialog.name} | Reason: {e}")

    print(f"📢 মোট {group_count} টি গ্রুপে মেসেজ পাঠানো হয়েছে।")

input("\n⏹️ Enter চাপুন স্ক্রিপ্ট বন্ধ করতে...")
