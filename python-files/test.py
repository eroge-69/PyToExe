import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1387115264700710924/Du2z5_59SLP6Qk6pFxI5D28QkPE86lt6je1Qih428kw2U5R9kBAmsbovegsclaB6Hm8S"

data = {
    "content": "hello"
}

response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("Message sent successfully.")
else:
    print(f"Failed to send message: {response.status_code} - {response.text}")