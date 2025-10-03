import requests

# Replace with your actual webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1423554829829148776/pHaZSGYPl3XXhNQQzICwZA_KiIh5S2m0hEKwzD6oGyJqzBZvph_6sQDuVA70oLz2ydrW"

# The message content (with @everyone)
data = {
    "content": "@everyone Hello from Python!"
}

# Send the POST request to the webhook
response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("Message sent successfully!")
else:
    print(f"Failed to send message: {response.status_code}, {response.text}")
