import requests
import pyfiglet

def send_webhook_messages(webhook_url, message_name, amount):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "content": message_name
    }

    for i in range(amount):
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code == 204:
            print(f"Message {i+1} sent successfully!")
        else:
            print(f"Failed to send message {i+1}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Print ASCII art banner
    ascii_banner = pyfiglet.figlet_format("FISHSTICKAS")
    print(ascii_banner)

    webhook = input("Enter the webhook URL: ")
    name = input("Enter the message content: ")
    try:
        count = int(input("Enter the number of messages to send: "))
        if count <= 0:
            print("Amount must be a positive number.")
        else:
            send_webhook_messages(webhook, name, count)
    except ValueError:
        print("Please enter a valid number for amount.")
